import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PROXY_API_KEY = os.getenv("PROXY_API_KEY")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Не найден TELEGRAM_BOT_TOKEN в .env")

if not PROXY_API_KEY:
    raise ValueError("Не найден PROXY_API_KEY в .env")