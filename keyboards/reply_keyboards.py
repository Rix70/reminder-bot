from telegram import ReplyKeyboardMarkup

def get_main_keyboard():
    keyboard = [
        ["📝 Новое напоминание", "📋 Мои напоминания"],
        ["ℹ️ Помощь"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True) 