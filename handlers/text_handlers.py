from telegram import Update
from telegram.ext import ContextTypes
from database.db import add_reminder, update_reminder, get_reminder_by_id
from .utils import delete_message, validate_date
from datetime import datetime
from keyboards.inline_keyboards import get_weekdays_keyboard, get_reminder_management_keyboard
from .base_handlers import help_command
from .reminder_handlers import new_reminder, list_active_reminders, list_all_reminders, format_reminder_text
import logging

async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    menu_commands = {
        "✏️ Новое напоминание": new_reminder,
        "📄 Активные напоминания": list_active_reminders, 
        "📑 Все напоминания": list_all_reminders,
        "ℹ️ Помощь": help_command
    }

    if text in menu_commands:
        await menu_commands[text](update, context)
        return

    await process_text_input(update, context)

async def process_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'waiting_for' not in context.user_data and 'edit_type' not in context.user_data:
        return

    text = update.message.text
    user_id = update.effective_user.id
    message = None
    
    try:
        # Обработка редактирования
        if 'edit_type' in context.user_data:
            edit_type = context.user_data['edit_type']
            reminder_id = context.user_data['editing_reminder']
            
            if edit_type == 'text':
                update_reminder(reminder_id, text=text)
                message = await update.message.reply_text("✅ Текст напоминания обновлен!")
                
            elif edit_type == 'time':
                try:
                    time = datetime.strptime(text, '%H:%M')
                    time_str = time.strftime('%H:%M')
                    update_reminder(reminder_id, time=time_str)
                    message = await update.message.reply_text("✅ Время напоминания обновлено!")
                except ValueError:
                    message = await update.message.reply_text(
                        "❌ Неверный формат времени. Используйте формат ЧЧ:ММ:"
                    )
                    return
                    
            elif edit_type == 'date':
                is_valid, result = validate_date(text)
                if is_valid:
                    update_reminder(reminder_id, date=result)
                    message = await update.message.reply_text("✅ Дата напоминания обновлена!")
                else:
                    message = await update.message.reply_text(
                        f"❌ {result}\nВведите дату в формате ДД.ММ.ГГГГ:"
                    )
                    return
            
            # Очищаем данные редактирования
            if message and message.text.startswith("✅"):
                reminder = get_reminder_by_id(reminder_id)
                reminder_text = format_reminder_text(reminder)
                await message.edit_text(
                    reminder_text,
                    reply_markup=get_reminder_management_keyboard(reminder_id, reminder[7])
                )
                context.user_data.clear()
                
        else:
            waiting_for=context.user_data['waiting_for']
            if waiting_for == 'text':
                context.user_data['text'] = text
                
                if context.user_data['reminder_type'] == 'weekly':
                    message = await update.message.reply_text(
                        "Выберите дни недели:",
                        reply_markup=get_weekdays_keyboard()
                    )
                else:
                    message = await update.message.reply_text("Введите время в формате ЧЧ:ММ")
                    context.user_data['waiting_for'] = 'time'
                    
            elif waiting_for == 'time':
                try:
                    time = datetime.strptime(text, '%H:%M')
                    time_str = time.strftime('%H:%M')
                    context.user_data['time'] = time_str
                    
                    if context.user_data['reminder_type'] in ['once', 'monthly', 'yearly']:
                        message = await update.message.reply_text(
                            "Введите дату в формате ДД.ММ.ГГГГ:"
                        )
                        context.user_data['waiting_for'] = 'date'
                    else:
                        # Сохраняем ежедневное или еженедельное напоминание
                        reminder_id = add_reminder(
                            user_id=user_id,
                            text=context.user_data['text'],
                            reminder_type=context.user_data['reminder_type'],
                            days_of_week=context.user_data.get('days_of_week'),
                            time=time_str
                        )
                        logging.info(f"Created reminder {reminder_id} for user {user_id}")
                        message = await update.message.reply_text("✅ Напоминание создано!")
                        context.user_data.clear()
                except ValueError:
                    message = await update.message.reply_text(
                        "❌ Неверный формат времени. Используйте формат ЧЧ:ММ:"
                    )
                    
            elif waiting_for == 'date':
                is_valid, result = validate_date(text)
                if is_valid:
                    reminder_id = add_reminder(
                        user_id=user_id,
                        text=context.user_data['text'],
                        reminder_type=context.user_data['reminder_type'],
                        time=context.user_data['time'],
                        date=result
                    )
                    message = await update.message.reply_text("✅ Напоминание создано!")
                    context.user_data.clear()
                else:
                    message = await update.message.reply_text(
                        f"❌ {result}\nВведите дату в формате ДД.ММ.ГГГГ:"
                    )
                        
    except Exception as e:
        logging.error(f"Error processing text input: {e}")
        message = await update.message.reply_text("❌ Произошла ошибка. Попробуйте еще раз.")
        context.user_data.clear()
    
    if message:
        context.user_data['last_bot_message'] = message.message_id
    await update.message.delete()