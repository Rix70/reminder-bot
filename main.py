import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram import BotCommand
from handlers import (
    start, help_command, new_reminder, list_active_reminders, list_all_reminders,
    button_callback, handle_text_input, check_owner
)
from database.db import init_db, get_active_reminders, update_last_reminded, cleanup_old_reminders
from config import TELEGRAM_TOKEN, validate_config
from datetime import datetime, time

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def setup_commands(application: Application):
    commands = [
        BotCommand("start", "Запустить бота"),
        BotCommand("new", "Создать новое напоминание"),
        BotCommand("list_active", "Показать активные напоминания"),
        BotCommand("list_all", "Показать все напоминания"),
        BotCommand("help", "Показать помощь")
    ]
    await application.bot.set_my_commands(commands)

async def check_reminders(context):
    """Проверяет и отправляет напоминания"""
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    current_date = now.strftime("%Y-%m-%d")
    weekday = str(now.isoweekday())
    
    logging.info(f"Checking reminders at {current_time}")
    
    try:
        reminders = get_active_reminders()
    except Exception as e:
        logging.error(f"Ошибка при получении напоминаний: {e}")
        return
        
    for reminder in reminders:
        reminder_id, user_id, text, reminder_type, days_of_week, time, date, is_active, last_reminded = reminder
        
        logging.info(f"Checking reminder {reminder_id}: time={time}, current_time={current_time}")
        
        if time != current_time:
            continue
            
        should_remind = False
        
        # Определяем необходимость отправки напоминания в зависимости от типа
        should_remind = {
            'daily': True,
            'weekly': bool(days_of_week and weekday in days_of_week.split(',')),
            'monthly': current_date[8:] == date[8:],
            'yearly': current_date[5:] == date[5:],
            'once': current_date == date
        }.get(reminder_type, False)
        
        logging.info(f"Should remind: {should_remind}, last_reminded: {last_reminded}")
        
        if should_remind and last_reminded != current_date:
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"🔔 Напоминание:\n{text}",
                    parse_mode='HTML'
                )
                update_last_reminded(reminder_id) # Обновляем дату последнего напоминания
                logging.info(f"Reminder {reminder_id} sent successfully")
            except Exception as e:
                logging.error(f"Failed to send reminder: {e}")

async def cleanup_job(context):
    """Задача для периодической очистки старых напоминаний"""
    try:
        cleanup_old_reminders()
    except Exception as e:
        logging.error(f"Ошибка при выполнении очистки: {e}")

def main():
    try:
        # Проверка конфигурации
        validate_config()
        
        # Инициализация базы данных
        init_db()
        
        # Создание приложения
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Установка команд бота
        application.job_queue.run_once(setup_commands, when=1, data=application)
        
        # Обработчики с проверкой владельца
        application.add_handler(CommandHandler("start", check_owner(start)))
        application.add_handler(CommandHandler("help", check_owner(help_command)))
        application.add_handler(CommandHandler("new", check_owner(new_reminder)))
        application.add_handler(CommandHandler("list_active", check_owner(list_active_reminders)))
        application.add_handler(CommandHandler("list_all", check_owner(list_all_reminders)))
        application.add_handler(CallbackQueryHandler(check_owner(button_callback)))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_owner(handle_text_input)))
        
        # Настройка проверки напоминаний через job_queue
        job_queue = application.job_queue
        job_queue.run_repeating(check_reminders, interval=60, first=1)
        job_queue.run_daily(cleanup_job, time=time(hour=0, minute=0))
        
        # Запуск бота
        application.run_polling()
        
    except ValueError as e:
        logging.error(f"Ошибка конфигурации: {e}")
        return

if __name__ == '__main__':
    main() 