from telegram.ext import ContextTypes
from telegram.error import BadRequest
from datetime import datetime

async def delete_message(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int):
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except BadRequest:
        pass

def validate_date(date_str):
    try:
        date = datetime.strptime(date_str, '%d.%m.%Y')
        #current_date = datetime.now()
        
        #current_date = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
        #date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        #if date < current_date:
        #    return False, "Дата не может быть в прошлом!"
        return True, date.strftime('%Y-%m-%d')
    except ValueError:
        return False, "Неверный формат даты!" 