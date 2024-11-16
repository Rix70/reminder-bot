# config.py

TELEGRAM_TOKEN = ''
OWNER_ID = ''

def validate_config():
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN не установлен")
    if not OWNER_ID:
        raise ValueError("OWNER_ID не установлен")
