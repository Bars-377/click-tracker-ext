import json
from datetime import datetime, timezone
from typing import Optional
import os
import sys

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

import win32wnet
import win32netcon

# --- Определяем базовую директорию ---
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

config_path = os.path.join(base_dir, "config.json")

# --- Загружаем конфиг ---
with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)

HOST = config["server"]["host"]
PORT = config["server"]["port"]

# Берём client_id из конфига или генерируем новый
CLIENT_ID = config.get("client_id")

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

# Модель клика
class ClickEvent(BaseModel):
    url: Optional[str] = Field(None, description="URL перехода")
    text: Optional[str] = Field(None, description="Текст ссылки")
    page_url: Optional[str] = Field(None, description="URL страницы")
    page_title: Optional[str] = None
    timestamp: Optional[str] = None
    mechanism: Optional[str] = None
    user_login: Optional[str] = None


SQL_FILE = os.path.join(base_dir, f"clicks_{CLIENT_ID}.sql")


def sql_escape(value: Optional[str]) -> str:
    if value is None:
        return "NULL"
    # Экранируем одинарные кавычки для SQL
    return f"'{value.replace('\'', '\'\'')}'"

def connect_unc(path, username, password):
    net_resource = win32wnet.NETRESOURCE()
    net_resource.dwType = win32netcon.RESOURCETYPE_DISK
    net_resource.lpRemoteName = path

    try:
        win32wnet.WNetAddConnection2(
            net_resource,
            password,
            username,
            0
        )
    except Exception as e:
        if "1219" not in str(e):
            raise

@app.post("/click")
async def receive_click(event: ClickEvent, request: Request):
    if not event.url and not event.page_url:
        raise HTTPException(status_code=400, detail="No url/page_url provided")

    # --- Определяем реальное локальное время ---
    if event.timestamp:
        try:
            # Конвертируем ISO-время в datetime и приводим к локальному часовому поясу
            ts = datetime.fromisoformat(event.timestamp.replace("Z", "+00:00")).astimezone()
        except Exception:
            ts = datetime.now()
    else:
        ts = datetime.now()

    # --- Формируем SQL-запрос ---
    sql = f"""INSERT INTO clicks (url, text, page_url, page_title, mechanism, timestamp, client_id, user_login)
VALUES (
    {sql_escape(event.url)},
    {sql_escape(event.text)},
    {sql_escape(event.page_url)},
    {sql_escape(event.page_title)},
    {sql_escape(event.mechanism)},
    '{ts.strftime("%Y-%m-%d %H:%M:%S")}',
    {sql_escape(CLIENT_ID)},
    {sql_escape(event.user_login)}
);
"""

    # --- Сохраняем локально ---
    try:
        with open(SQL_FILE, "a", encoding="utf-8") as f:
            f.write(sql + "\n")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # --- Сохраняем на SMB-шару ---
    UNC_SHARE = r"\\172.18.10.210\mfcshare"
    SUBDIR = "share"

    USERNAME = r"share-toma"
    PASSWORD = r"zWS1JLp8R_u!Vl["

    connect_unc(UNC_SHARE, USERNAME, PASSWORD)

    target_dir = os.path.join(UNC_SHARE, SUBDIR)
    os.makedirs(target_dir, exist_ok=True)

    file_path = os.path.join(target_dir, f"clicks_{CLIENT_ID}.sql")

    with open(file_path, "a", encoding="utf-8") as f:
        f.write(sql + "\n")

    return {"status": "ok", "client_id": CLIENT_ID}


import logging
from logging.handlers import RotatingFileHandler

# --- Настройка логов ---
log_file = os.path.join(base_dir, "uvicorn.log")

# Перенаправляем stdout/stderr в файл, чтобы uvicorn не падал
sys.stdout = open(log_file, "a", encoding="utf-8")
sys.stderr = open(log_file, "a", encoding="utf-8")

logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)

file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=2)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT, log_level="info", access_log=True)
