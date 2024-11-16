from telegram import Update
from telegram.ext import ContextTypes
from database.db import get_all_reminders, get_active_reminders, get_reminders_statistics
from keyboards.inline_keyboards import get_reminder_type_keyboard, get_reminder_management_keyboard
from .utils import delete_message

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
    
    if not reminders:
        await update.message.reply_text("У вас нет активных напоминаний.")
        return

    for reminder in reminders:
        reminder_id, user_id, text, reminder_type, days_of_week, time, date, is_active, last_reminded = reminder
        reminder_text = format_reminder_text(reminder)
        
        await update.message.reply_text(
            reminder_text,
            reply_markup=get_reminder_management_keyboard(reminder_id, is_active)
        )
        
async def list_all_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Обработчик для вывода списка всех напоминаний'''
    reminders = get_all_reminders(update.effective_user.id)
    
    if not reminders:
        await update.message.reply_text("У вас нет напоминаний.")
        return

    for reminder in reminders:
        reminder_id, user_id, text, reminder_type, days_of_week, time, date, is_active, last_reminded = reminder
        reminder_text = format_reminder_text(reminder)
        
        await update.message.reply_text(
            reminder_text,
            reply_markup=get_reminder_management_keyboard(reminder_id, is_active)
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
    elif reminder_type in ['monthly', 'yearly', 'once'] and date:
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
            'once': '📌'
        }.get(r_type, '📝')
        text += f"{emoji} {r_type}: {count}\n"
    
    await update.message.reply_text(text, parse_mode='Markdown')