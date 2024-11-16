import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram import BotCommand
from handlers.reminder_handlers import (
    start, help_command, new_reminder, list_reminders,
    button_callback, handle_text_input
)
from database.db import init_db, get_active_reminders, update_last_reminded
from config import TELEGRAM_TOKEN
from datetime import datetime

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def setup_commands(application: Application):
    commands = [
        BotCommand("start", "Запустить бота"),
        BotCommand("new", "Создать новое напоминание"),
        BotCommand("list", "Показать мои напоминания"),
        BotCommand("help", "Показать помощь")
    ]
    await application.bot.set_my_commands(commands)

async def check_reminders(context):
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    current_date = now.strftime("%Y-%m-%d")
    weekday = str(now.isoweekday())
    
    logging.info(f"Checking reminders at {current_time}")
    
    reminders = get_active_reminders()
    
    for reminder in reminders:
        reminder_id, user_id, text, reminder_type, days_of_week, time, date, is_active, last_reminded = reminder
        
        logging.info(f"Checking reminder {reminder_id}: time={time}, current_time={current_time}")
        
        if time != current_time:
            continue
            
        should_remind = False
        
        if reminder_type == 'daily':
            should_remind = True
        elif reminder_type == 'weekly':
            if days_of_week and weekday in days_of_week.split(','):
                should_remind = True
        elif reminder_type == 'monthly':
            if current_date[8:] == date[8:]:
                should_remind = True
        elif reminder_type == 'yearly':
            if current_date[5:] == date[5:]:
                should_remind = True
        elif reminder_type == 'once':
            if current_date == date:
                should_remind = True
        
        logging.info(f"Should remind: {should_remind}, last_reminded: {last_reminded}")
        
        if should_remind and last_reminded != current_date:
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"🔔 Напоминание:\n{text}"
                )
                update_last_reminded(reminder_id)
                logging.info(f"Reminder {reminder_id} sent successfully")
            except Exception as e:
                logging.error(f"Failed to send reminder: {e}")

def main():
    # Инициализация базы данных
    init_db()
    
    # Создание приложения
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Установка команд бота
    application.job_queue.run_once(setup_commands, when=1, data=application)
    
    # Обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("new", new_reminder))
    application.add_handler(CommandHandler("list", list_reminders))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))
    
    # Настройка проверки напоминаний через job_queue
    job_queue = application.job_queue
    job_queue.run_repeating(check_reminders, interval=60, first=1)
    
    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main() 