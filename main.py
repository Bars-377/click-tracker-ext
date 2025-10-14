import json
from datetime import datetime, timezone
from typing import Optional

import asyncpg
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Загрузка конфигурации
with open("config.json", "r") as f:
    config = json.load(f)

DB_CONFIG = config["db"]
HOST = config["server"]["host"]
PORT = config["server"]["port"]

DB_DSN = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@" \
         f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

app = FastAPI(title="Click Receiver")

# Разрешаем запросы с локального фронта
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

# Модель события клика
class ClickEvent(BaseModel):
    url: Optional[str] = Field(None, description="URL перехода")
    text: Optional[str] = Field(None, description="Текст ссылки")
    page_url: Optional[str] = Field(None, description="URL страницы, где кликнули")
    page_title: Optional[str] = None
    timestamp: Optional[str] = None
    mechanism: Optional[str] = None

# Инициализация базы и создание таблицы
async def init_db():
    pool = await asyncpg.create_pool(dsn=DB_DSN, min_size=1, max_size=5)
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS clicks (
                id SERIAL PRIMARY KEY,
                url TEXT,
                text TEXT,
                page_url TEXT,
                page_title TEXT,
                mechanism TEXT,
                timestamp TIMESTAMP
            )
        """)
    return pool

@app.on_event("startup")
async def startup():
    try:
        app.state.db_pool = await init_db()
        print("Connected to DB")
    except Exception as e:
        print("Error connecting to DB:", e)
        raise

@app.on_event("shutdown")
async def shutdown():
    await app.state.db_pool.close()
    print("DB pool closed")

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

    try:
        async with app.state.db_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO clicks (url, text, page_url, page_title, mechanism, timestamp)
                VALUES ($1, $2, $3, $4, $5, $6)
                """,
                event.url, event.text, event.page_url, event.page_title, event.mechanism, ts
            )
    except Exception as e:
        import traceback
        print("Error inserting into DB:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("server:app", host=HOST, port=PORT, log_level="info")
