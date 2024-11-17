import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram import BotCommand
from handlers import (
    start, help_command, new_reminder, list_active_reminders, list_all_reminders,
    button_callback, handle_text_input, check_owner, get_statistics
)
from database.db import init_db, get_active_reminders, update_last_reminded, cleanup_old_reminders, get_weekly_reminders
from config import TELEGRAM_TOKEN, OWNER_ID, validate_config
from datetime import datetime, time, timedelta

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
# Отключаем логи от httpx
logging.getLogger('httpx').setLevel(logging.WARNING)

async def setup_commands(application: Application):
    commands = [
        BotCommand("start", "Запустить бота"),
        BotCommand("new", "Создать новое напоминание"),
        BotCommand("list_active", "Показать активные напоминания"),
        BotCommand("list_all", "Показать все напоминания"),
        BotCommand("stats", "Показать статистику напоминаний"),
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
            'weekly': bool(days_of_week is not None and weekday in (days_of_week.split(',') if days_of_week else [])),
            'monthly': bool(date is not None and current_date[8:] == date[8:]),
            'yearly': bool(date is not None and current_date[5:] == date[5:]), 
            'once': bool(date is not None and current_date == date)
        }.get(reminder_type, False)
        
        logging.info(f"Should remind: {should_remind}, last_reminded: {last_reminded}")
        
        if should_remind and last_reminded != current_date:
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"🔔 *Напоминание:*\n\n{text}",
                    parse_mode='Markdown'
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

async def send_weekly_summary(context):
    """Отправляет обзор напоминаний на следующую неделю"""
    now = datetime.now()
    print("Checking weekly summary")
    if now.weekday() != 6:  # Воскресенье
        return
        
    try:
        reminders = get_weekly_reminders()
        if not reminders:
            return
            
        # Определяем даты следующей недели
        next_week_start = (now + timedelta(days=1)).date()
        next_week_end = (now + timedelta(days=7)).date()
        
        # Группируем напоминания по типам
        summary = "📅 *События на следующую неделю:*\n"
        summary += f"*{next_week_start.strftime('%d.%m')} - {next_week_end.strftime('%d.%m')}*\n\n"
        
        type_headers = {
            'daily': '🔁 *Ежедневные:*',
            'weekly': '📅 *Еженедельные:*',
            'monthly': '📆 *Ежемесячные:*',
            'yearly': '🗓 *Ежегодные:*',
            'once': '📌 *Одноразовые:*'
        }
        
        grouped_reminders = {}
        for reminder in reminders:
            r_type = reminder[3]  # reminder_type
            r_date = reminder[6]  # date
            
            # Проверяем, подходит ли напоминание для следующей недели
            should_include = False
            
            if r_type == 'daily':
                should_include = True
            elif r_type == 'weekly':
                # Проверяем, есть ли дни недели в следующей неделе
                days = reminder[4].split(',')  # days_of_week
                should_include = bool(days)
            elif r_type == 'monthly':
                # Проверяем, попадает ли день месяца на следующую неделю
                if r_date:
                    r_day = int(r_date[8:10])
                    for d in range(8):
                        check_date = next_week_start + timedelta(days=d)
                        if check_date.day == r_day:
                            should_include = True
                            break
            elif r_type == 'yearly' and r_date:
                # Проверяем, попадает ли дата на следующую неделю
                r_date = datetime.strptime(r_date, '%Y-%m-%d').date()
                next_occurrence = r_date.replace(year=now.year)
                if next_occurrence < now.date():
                    next_occurrence = next_occurrence.replace(year=now.year + 1)
                should_include = next_week_start <= next_occurrence <= next_week_end
            elif r_type == 'once' and r_date:
                # Включаем только если дата в следующей неделе
                r_date = datetime.strptime(r_date, '%Y-%m-%d').date()
                should_include = next_week_start <= r_date <= next_week_end
            
            if should_include:
                if r_type not in grouped_reminders:
                    grouped_reminders[r_type] = []
                grouped_reminders[r_type].append(reminder)
        
        # Если нет напоминаний на следующую неделю, не отправляем сообщение
        if not grouped_reminders:
            return
        
        # Формируем текст для каждого типа напоминаний
        for r_type, reminders in grouped_reminders.items():
            if reminders:
                summary += f"\n{type_headers.get(r_type, '📝 *Другие:*')}\n"
                for reminder in reminders:
                    text = reminder[2]  # text
                    time = reminder[5]  # time
                    date = reminder[6]  # date
                    
                    if r_type == 'weekly':
                        days = reminder[4].split(',')  # days_of_week
                        days_text = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
                        days = [days_text[int(d)-1] for d in days]
                        summary += f"• {text} ⏰ {time} ({', '.join(days)})\n"
                    elif r_type in ['monthly', 'yearly', 'once'] and date:
                        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
                        date_str = date_obj.strftime('%d.%m')
                        summary += f"• {text} ⏰ {time} 📅 {date_str}\n"
                    else:
                        summary += f"• {text} ⏰ {time}\n"
        
        # Отправляем сообщение владельцу
        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=summary,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logging.error(f"Ошибка при отправке еженедельного обзора: {e}")

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
        application.add_handler(CommandHandler("statistics", check_owner(get_statistics)))
        application.add_handler(CallbackQueryHandler(check_owner(button_callback)))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_owner(handle_text_input)))
        
        # Настройка проверки напоминаний через job_queue
        job_queue = application.job_queue
        job_queue.run_repeating(check_reminders, interval=60, first=1) # проверка напоминаний каждые 60 секунд
        job_queue.run_daily(cleanup_job, time=time(hour=0, minute=0)) # очистка старых напоминаний ежедневный в 00:00
        job_queue.run_daily(send_weekly_summary, time=time(hour=6, minute=15),  days=(0,))    # еженедельный обзор Каждое воскресенье в 9:00
        # Запуск бота
        application.run_polling()
        
    except ValueError as e:
        logging.error(f"Ошибка конфигурации: {e}")
        return

if __name__ == '__main__':
    main() 