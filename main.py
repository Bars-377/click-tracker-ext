import json
from datetime import datetime
from typing import Optional
import os
import sys
import time
import logging
from logging.handlers import RotatingFileHandler
import getpass

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

import win32wnet
import win32netcon
import win32com.client

# ---------- BASE DIR ----------
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

config_path = os.path.join(base_dir, "config.json")

# ---------- CONFIG ----------
with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)

HOST = config["server"]["host"]
PORT = config["server"]["port"]
CLIENT_ID = config.get("client_id")

# ---------- LOGGING ----------
log_file = os.path.join(base_dir, "uvicorn.log")

sys.stdout = open(log_file, "a", encoding="utf-8")
sys.stderr = open(log_file, "a", encoding="utf-8")

logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

handler = RotatingFileHandler(
    log_file,
    maxBytes=5 * 1024 * 1024,
    backupCount=2,
    encoding="utf-8"
)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# ---------- FASTAPI ----------
app = FastAPI(
    title="Internal Event Service",
    description="Corporate internal service. Not intended for public use."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

# ---------- MODELS ----------
class ClickEvent(BaseModel):
    url: Optional[str] = None
    text: Optional[str] = None
    page_url: Optional[str] = None
    page_title: Optional[str] = None
    timestamp: Optional[str] = None
    mechanism: Optional[str] = None
    user_login: Optional[str] = None  # логин в веб-системе

# ---------- UTILS ----------
def sql_escape(value: Optional[str]) -> str:
    if value is None:
        return "NULL"
    return "'" + value.replace("'", "''") + "'"

def get_windows_user() -> str:
    return getpass.getuser()

def get_windows_login_time() -> datetime:
    """
    Возвращает время интерактивного входа пользователя в Windows
    """
    wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
    svc = wmi.ConnectServer(".", "root\\cimv2")

    sessions = svc.ExecQuery(
        "SELECT * FROM Win32_LogonSession WHERE LogonType = 2"
    )

    for session in sessions:
        start_time = session.StartTime
        if start_time:
            return datetime.strptime(start_time.split(".")[0], "%Y%m%d%H%M%S")

    return datetime.now()

WINDOWS_USER = get_windows_user()
WINDOWS_LOGIN_TIME = get_windows_login_time()

logger.info(f"Windows user: {WINDOWS_USER}")
logger.info(f"Windows login time: {WINDOWS_LOGIN_TIME}")

# ---------- UNC ----------
def connect_unc_with_retry(path: str, username: str, password: str, retry_delay: int = 5):
    net_resource = win32wnet.NETRESOURCE()
    net_resource.dwType = win32netcon.RESOURCETYPE_DISK
    net_resource.lpRemoteName = path

    while True:
        try:
            win32wnet.WNetAddConnection2(
                net_resource,
                password,
                username,
                0
            )
            logger.info(f"Подключение к UNC успешно: {path}")
            return
        except Exception as e:
            if "1219" in str(e):
                logger.info(f"UNC уже подключён: {path}")
                return

            logger.error(f"Ошибка подключения к UNC {path}: {e}")
            time.sleep(retry_delay)

# ---------- ENDPOINT ----------
@app.post("/click")
async def receive_click(event: ClickEvent, request: Request):
    if not event.url and not event.page_url:
        raise HTTPException(status_code=400, detail="No url/page_url provided")

    # --- event timestamp ---
    if event.timestamp:
        try:
            ts = datetime.fromisoformat(
                event.timestamp.replace("Z", "+00:00")
            ).astimezone()
        except Exception:
            ts = datetime.now()
    else:
        ts = datetime.now()

    sql = f"""
INSERT INTO clicks (
    url,
    text,
    page_url,
    page_title,
    mechanism,
    timestamp,
    client_id,
    user_login,
    timestamp_user,
    user_name
) VALUES (
    {sql_escape(event.url)},
    {sql_escape(event.text)},
    {sql_escape(event.page_url)},
    {sql_escape(event.page_title)},
    {sql_escape(event.mechanism)},
    '{ts.strftime("%Y-%m-%d %H:%M:%S")}',
    {sql_escape(CLIENT_ID)},
    {sql_escape(event.user_login)},
    '{WINDOWS_LOGIN_TIME.strftime("%Y-%m-%d %H:%M:%S")}',
    {sql_escape(WINDOWS_USER)}
);
"""

    UNC_SHARE = r"\\172.18.10.210\share-toma"
    USERNAME = r"share-toma"
    PASSWORD = r"zWS1JLp8R_u!Vl["

    connect_unc_with_retry(UNC_SHARE, USERNAME, PASSWORD)

    file_path = os.path.join(UNC_SHARE, f"clicks_{CLIENT_ID}.sql")

    try:
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(sql + "\n")
    except Exception as e:
        logger.error(f"Ошибка записи в UNC: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "status": "ok",
        "client_id": CLIENT_ID,
        "user_name": WINDOWS_USER,
        "timestamp_user": WINDOWS_LOGIN_TIME.isoformat()
    }

# ---------- MAIN ----------
if __name__ == "__main__":
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_level="info",
        access_log=True
    )
