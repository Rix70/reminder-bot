from telegram import Update
from telegram.ext import ContextTypes
from config import OWNER_ID

def check_owner(func):
    '''Проверка на владельца бота'''
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        
        if user_id != OWNER_ID:
            if update.callback_query:
                await update.callback_query.answer("У вас нет прав доступа к этому боту.", show_alert=True)
                return
            else:
                await update.message.reply_text("У вас нет прав доступа к этому боту.")
                return
        
        return await func(update, context)
    return wrapper 