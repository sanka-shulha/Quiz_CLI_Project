import os
import psycopg2
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

def connect():
    try:
        # чтобы клиент ожидал UTF-8
        os.environ["PGCLIENTENCODING"] = "UTF8"

        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            # ВАЖНО: сообщения сервера на английском (без кириллицы)
            options="-c lc_messages=C"
        )
        return conn
    except Exception as e:
        print(f"Помилка підключення: {e}")
        return None