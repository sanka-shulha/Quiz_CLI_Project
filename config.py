from dotenv import load_dotenv
import os

load_dotenv()

DB_NAME = os.getenv("DB_NAME", "quiz_shulha")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")