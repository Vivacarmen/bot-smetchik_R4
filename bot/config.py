import os
from dotenv import load_dotenv

load_dotenv()

# API
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")  # ← НОВОЕ
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")

# Безопасность: 6 ролей
ACCESS_PASSWORD_CLIENT = os.getenv("ACCESS_PASSWORD_CLIENT", "")
ACCESS_PASSWORD_AGENT = os.getenv("ACCESS_PASSWORD_AGENT", "")
ACCESS_PASSWORD_MANAGER = os.getenv("ACCESS_PASSWORD_MANAGER", "")
ACCESS_PASSWORD_ADMIN = os.getenv("ACCESS_PASSWORD_ADMIN", "")
ACCESS_PASSWORD_CEO = os.getenv("ACCESS_PASSWORD_CEO", "")
ACCESS_PASSWORD_SUPERUSER = os.getenv("ACCESS_PASSWORD_SUPERUSER", "")

ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))
TELEGRAM_LOG_CHAT_ID = os.getenv("TELEGRAM_LOG_CHAT_ID", "")  # ← НОВОЕ

# Пути
DB_PATH = os.getenv("DB_PATH", "/root/projects/py/data/database.db")
TEMP_PATH = os.getenv("TEMP_PATH", "/root/projects/py/temp")
LOG_PATH = os.getenv("LOG_PATH", "/root/projects/py/logs")
ARCHIVE_PATH = os.getenv("ARCHIVE_PATH", "/root/projects/py/archives")  # ← НОВОЕ
CONFIG_PATH = os.getenv("CONFIG_PATH", "/root/projects/py/config")  # ← НОВОЕ

# Прокси
USE_PROXY = os.getenv("USE_PROXY", "false").lower() == "true"

# Проверки
if not TELEGRAM_TOKEN:
    raise ValueError("Не задан TELEGRAM_TOKEN в .env")
