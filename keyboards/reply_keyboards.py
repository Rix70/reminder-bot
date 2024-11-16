from telegram import ReplyKeyboardMarkup

def get_main_keyboard():
    keyboard = [
        ["✏️ Новое напоминание", "📄 Активные напоминания"],
        ["📑 Все напоминания", "ℹ️ Помощь"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True) 