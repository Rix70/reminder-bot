from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db import get_reminder_by_id, toggle_reminder, delete_reminder
from keyboards.inline_keyboards import get_weekdays_keyboard, get_reminder_management_keyboard
import logging

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    handlers = {
        'type_': handle_type_callback,
        'edit_': handle_edit_callback,
        'toggle_': handle_toggle_callback,
        'day_': handle_day_callback,
        'days_done': handle_days_done_callback,
        'delete_': handle_delete_callback,
        'cancel_': handle_cancel_callback
    }
    
    for prefix, handler in handlers.items():
        if query.data.startswith(prefix):
            await handler(query, context)
            break

async def handle_type_callback(query, context):
    '''Обработчик для выбора типа напоминания'''
    reminder_type = query.data.split("_")[1]
    context.user_data['reminder_type'] = reminder_type
    await query.message.edit_text("Введите текст напоминания:")
    context.user_data['waiting_for'] = 'text'
    context.user_data['last_bot_message'] = query.message.message_id

async def handle_edit_callback(query, context):
    '''Обработчик для редактирования напоминания'''
    _, edit_type, reminder_id = query.data.split("_")
    reminder = get_reminder_by_id(int(reminder_id))

    if not reminder:
        await query.message.edit_text("❌ Напоминание не найдено!")
        return
    
    context.user_data.clear()  # Очищаем предыдущие данные
    context.user_data['editing_reminder'] = int(reminder_id)
    context.user_data['edit_type'] = edit_type
    
    messages = {
        'text': f"\nТекущий текст: _{reminder[2]}_ \n\nВведите новый текст:",
        'time': f"\nТекущее время: _{reminder[5]}_ \n\nВведите новое время в формате ЧЧ:ММ:",
        'date': f"\nТекущая дата: _{reminder[6]}_ \n\nВведите новую дату в формате ДД.ММ.ГГГГ:"
    }
    
    keyboard = [[InlineKeyboardButton("❌ Отмена", callback_data=f"cancel_{reminder_id}")]]
    
    await query.message.edit_text(
        messages.get(edit_type, "❌ Неизвестный тип редактирования"), 
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    context.user_data['last_bot_message'] = query.message.message_id

async def handle_toggle_callback(query, context):
    '''Обработчик для переключения статуса напоминания'''
    from .reminder_handlers import format_reminder_text

    try:
        reminder_id = int(query.data.split("_")[1])
        
        new_status = toggle_reminder(reminder_id)
        reminder = get_reminder_by_id(reminder_id)
        status_text = "включено ✅" if new_status else "отключено 🔕"
        text = f"*Напоминание {status_text}*\n\n{format_reminder_text(reminder)}"
        
        await query.message.edit_text(
            text,
            parse_mode='Markdown',
            reply_markup=get_reminder_management_keyboard(reminder_id, new_status)
        )
        
    except (ValueError, IndexError):
        logging.error(f"Ошибка при обработке callback данных: {query.data}")
        await query.message.edit_text("❌ Произошла ошибка при обработке запроса")
    except Exception as e:
        logging.error(f"Неожиданная ошибка в handle_toggle_callback: {e}")
        await query.message.edit_text("❌ Произошла непредвиденная ошибка")

async def handle_day_callback(query, context):
    '''Обработчик для выбора дней недели'''
    day = query.data.split("_")[1]
    
    if 'selected_days' not in context.user_data:
        context.user_data['selected_days'] = set()
    
    if day in context.user_data['selected_days']:
        context.user_data['selected_days'].remove(day)
    else:
        context.user_data['selected_days'].add(day)
    
    days_text = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    selected = [days_text[int(d)-1] for d in context.user_data['selected_days']]
    
    await query.message.edit_text(
        f"Выбранные дни: {', '.join(selected) if selected else 'нет'}\n"
        "Нажмите 'Готово' когда закончите выбор:",
        reply_markup=get_weekdays_keyboard()
    )

async def handle_days_done_callback(query, context):
    '''Обработчик завершения выбора дней недели'''
    if not context.user_data.get('selected_days'):
        await query.message.edit_text(
            "❌ Выберите хотя бы один день недели:",
            reply_markup=get_weekdays_keyboard()
        )
        return
    
    # Сортируем дни недели
    days = sorted(list(context.user_data['selected_days']))
    context.user_data['days_of_week'] = ','.join(days)
    
    await query.message.edit_text("Введите время в формате ЧЧ:ММ")
    context.user_data['waiting_for'] = 'time'

async def handle_delete_callback(query, context):
    reminder_id = int(query.data.split("_")[1])
    delete_reminder(reminder_id)
    await query.message.edit_text("Напоминание удалено!")

async def handle_cancel_callback(query, context):
    '''Обработчик для отмены редактирования'''
    reminder_id = int(query.data.split("_")[1])
    reminder = get_reminder_by_id(reminder_id)
    
    if reminder:
        from .reminder_handlers import format_reminder_text
        reminder_text = format_reminder_text(reminder)
        await query.message.edit_text(
            reminder_text,
            reply_markup=get_reminder_management_keyboard(reminder_id, reminder[7])
        )
    else:
        await query.message.edit_text("❌ Напоминание не найдено!")
    
    context.user_data.clear()