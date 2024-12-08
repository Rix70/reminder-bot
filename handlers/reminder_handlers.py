from telegram import Update
from telegram.ext import ContextTypes
from database.db import get_all_reminders, get_active_reminders, get_reminders_statistics, get_weekly_reminders
from keyboards.inline_keyboards import get_reminder_type_keyboard, get_reminder_management_keyboard, get_pagination_keyboard
from .utils import delete_message
from datetime import datetime, timedelta
import logging

async def new_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Обработчик для создания нового напоминания'''
    context.user_data.clear()
    await update.message.delete()
    
    message = await update.message.reply_text(
        "Выберите тип напоминания:",
        reply_markup=get_reminder_type_keyboard()
    )
    context.user_data['last_bot_message'] = message.message_id

async def list_active_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Обработчик для вывода списка активных напоминаний'''
    reminders = get_active_reminders()
    await show_reminders_page(update, context, reminders, 1, "активных")

async def list_all_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Обработчик для вывода списка всех напоминаний'''
    reminders = get_all_reminders(update.effective_user.id)
    await show_reminders_page(update, context, reminders, 1, "всех")

async def show_reminders_page(update: Update, context: ContextTypes.DEFAULT_TYPE, reminders, page: int, reminder_type: str):
    '''Показывает страницу с напоминаниями'''
    if not reminders:
        await update.message.reply_text(f"У вас нет {reminder_type} напоминаний.")
        return
        
    # Сохраняем список напоминаний в контексте
    context.user_data['current_reminders'] = reminders
    total_pages = len(reminders)
    page = min(max(1, page), total_pages)
    
    # Получаем текущее напоминание
    reminder = reminders[page-1]
    reminder_text = format_reminder_text(reminder)
    
    # Определяем метод отправки сообщения
    if isinstance(update, Update):
        send_method = update.message.reply_text
    else:
        # Для callback query используем edit_message_text
        send_method = update.edit_message_text
    
    await send_method(
        reminder_text,
        reply_markup=get_pagination_keyboard(page, total_pages, reminder[0], reminder[7])
    )

def format_reminder_text(reminder):
    '''Форматирование текста напоминания для отображения пользователю'''
    reminder_id, user_id, text, reminder_type, days_of_week, time, date, is_active, last_reminded = reminder
    
    # Словарь для маппинга типов напоминаний на эмодзи и текст
    type_mapping = {
        'daily': ('🔁', 'Ежедневно'),
        'weekly': ('📅', 'Еженедельно'), 
        'monthly': ('📆', 'Ежемесячно'),
        'yearly': ('🗓', 'Ежегодно'),
        'birthday': ('🎂', 'День рождения'),
        'once': ('📌', 'Одноразово')
    }

    # Формируем базовую информацию
    status = "🔔 Активно" if is_active else "🔕 Отключено"
    reminder_text = f"ID: {reminder_id}\n 📝 {text}\n⏰ {time}\n{status}\n"
    
    # Получаем эмодзи и текст для типа напоминания
    emoji, type_text = type_mapping.get(reminder_type, ('📌', 'Одноразово'))
    
    # Добавляем специфичную для типа информацию
    if reminder_type == 'weekly' and days_of_week:
        days = days_of_week.split(',')
        days_text = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
        selected_days = [days_text[int(d)-1] for d in days]
        reminder_text += f"{emoji} {type_text} ({', '.join(selected_days)})"
    elif reminder_type == 'birthday' and date:
        birth_date = datetime.strptime(date, '%Y-%m-%d')
        today = datetime.now()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        next_birthday = birth_date.replace(year=today.year)
        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)
        reminder_text += f"{emoji} {type_text} ({date}) - {age} лет"
    elif reminder_type in ['monthly', 'yearly', 'once', 'birthday'] and date:
        reminder_text += f"{emoji} {type_text} ({date})"
    else:
        reminder_text += f"{emoji} {type_text}"
    
    return reminder_text

async def get_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Статистика напоминаний'''
    stats = get_reminders_statistics()
    
    text = "*📊 Статистика напоминаний:*\n\n"
    text += f"Всего напоминаний: {stats['total']}\n"
    text += f"Активных: {stats['active']}\n\n"
    
    text += "*По типам:*\n"
    for r_type, count in stats['by_type'].items():
        emoji = {
            'daily': '🔁',
            'weekly': '📅',
            'monthly': '📆',
            'yearly': '🗓',
            'once': '📌',
            'birthday': '🎂'
        }.get(r_type, '📝')
        text += f"{emoji} {r_type}: {count}\n"
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def send_weekly_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет обзор напоминаний на следующую неделю"""
    try:
        reminders = get_weekly_reminders()
        if not reminders:
            await update.message.reply_text("На следующую неделю напоминаний нет.")
            return
            
        # Определяем даты следующей недели
        now = datetime.now()
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
            'birthday': '🎂 *Дни рождения:*',
            'once': '📌 *Одноразовые:*'
        }
        
        grouped_reminders = {}
        for reminder in reminders:
            r_type = reminder[3]  # reminder_type
            if r_type not in grouped_reminders:
                grouped_reminders[r_type] = []
            
            # Проверяем, подходит ли напоминание для следующей недели
            should_include = False
            
            if r_type == 'daily':
                should_include = True
            elif r_type == 'weekly':
                days = reminder[4].split(',') if reminder[4] else []
                should_include = bool(days)
            elif r_type == 'birthday' and reminder[6]:  # date
                birth_date = datetime.strptime(reminder[6], '%Y-%m-%d').date()
                next_birthday = birth_date.replace(year=now.year)
                if next_birthday < now.date():
                    next_birthday = next_birthday.replace(year=now.year + 1)
                should_include = next_week_start <= next_birthday <= next_week_end
            elif reminder[6]:  # date для других типов
                event_date = datetime.strptime(reminder[6], '%Y-%m-%d').date()
                if r_type == 'monthly':
                    # Проверяем, попадает ли день месяца на следующую неделю
                    for d in range(8):
                        check_date = next_week_start + timedelta(days=d)
                        if check_date.day == event_date.day:
                            should_include = True
                            break
                elif r_type == 'yearly':
                    # Проверяем, попадает ли дата (без года) на следующую неделю
                    event_date = event_date.replace(year=now.year)
                    if event_date < now.date():
                        event_date = event_date.replace(year=now.year + 1)
                    should_include = next_week_start <= event_date <= next_week_end
                elif r_type == 'once':
                    should_include = next_week_start <= event_date <= next_week_end
            
            if should_include:
                grouped_reminders[r_type].append(reminder)
        
        # Формируем текст для каждого типа напоминаний
        for r_type, type_reminders in grouped_reminders.items():
            if type_reminders:
                summary += f"\n{type_headers.get(r_type, '📝 *Другие:*')}\n"
                for reminder in type_reminders:
                    text = reminder[2]  # text
                    time = reminder[5]  # time
                    date = reminder[6]  # date
                    days_of_week = reminder[4]  # days_of_week
                    
                    if r_type == 'birthday' and date:
                        birth_date = datetime.strptime(date, '%Y-%m-%d').date()
                        age = now.year - birth_date.year
                        if (now.month, now.day) < (birth_date.month, birth_date.day):
                            age -= 1
                        next_birthday = birth_date.replace(year=now.year)
                        if next_birthday < now.date():
                            next_birthday = next_birthday.replace(year=now.year + 1)
                            age += 1
                        date_str = next_birthday.strftime('%d.%m')
                        summary += f"• {text} ⏰ {time} 📅 {date_str} 🎂 {age} лет\n"
                    elif r_type == 'weekly' and days_of_week:
                        days = days_of_week.split(',')
                        days_text = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
                        days = [days_text[int(d)-1] for d in days]
                        summary += f"• {text} ⏰ {time} ({', '.join(days)})\n"
                    elif date:
                        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
                        date_str = date_obj.strftime('%d.%m')
                        summary += f"• {text} ⏰ {time} 📅 {date_str}\n"
                    else:
                        summary += f"• {text} ⏰ {time}\n"
        
        await update.message.reply_text(
            summary,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logging.error(f"Ошибка при отправке еженедельного обзора: {e}")
        await update.message.reply_text("Произошла ошибка при формировании обзора на неделю.")