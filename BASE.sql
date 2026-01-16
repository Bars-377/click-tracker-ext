-- Создаём таблицу с уникальным ограничением сразу
CREATE TABLE clicks (
    id SERIAL PRIMARY KEY,
    url TEXT,
    text TEXT,
    page_url TEXT,
    page_title TEXT,
    mechanism TEXT,
    timestamp TIMESTAMP NOT NULL,
    client_id TEXT,
    user_login TEXT,
    timestamp_user TIMESTAMP,
    user_name TEXT,
    _hash VARCHAR(32),  -- добавляем колонку для MD5-хеша
    UNIQUE (_hash)
);