from telegram import ReplyKeyboardMarkup

def get_main_keyboard():
    keyboard = [
        ["✏️ Новое напоминание", "📅 На неделю"],
        ["📑 Все напоминания", "📄 Активные напоминания"],
        ["📊 Статистика", "ℹ️ Помощь"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True) 