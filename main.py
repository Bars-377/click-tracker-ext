import json
from datetime import datetime, timezone
from typing import Optional
import os
import sys

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

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

@app.post("/click")
async def receive_click(event: ClickEvent, request: Request):
    if not event.url and not event.page_url:
        raise HTTPException(status_code=400, detail="No url/page_url provided")

    ts = None
    if event.timestamp:
        try:
            ts = datetime.fromisoformat(event.timestamp.replace("Z", "+00:00"))
            ts = ts.astimezone(timezone.utc).replace(tzinfo=None)
        except Exception:
            ts = datetime.utcnow()
    else:
        ts = datetime.utcnow()

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

    try:
        with open(SQL_FILE, "a", encoding="utf-8") as f:
            f.write(sql + "\n")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
