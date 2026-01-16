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
    CONSTRAINT unique_click UNIQUE (page_url, timestamp, client_id)
);

-- Дополнительно создаём индекс для ускорения проверок уникальности
CREATE UNIQUE INDEX IF NOT EXISTS unique_click_idx
ON clicks(page_url, timestamp, client_id);
