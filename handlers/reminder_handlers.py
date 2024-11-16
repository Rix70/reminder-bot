from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
from database.db import (
    add_reminder, get_user_reminders, delete_reminder, 
    get_reminder_by_id, update_reminder, toggle_reminder
)
from keyboards.inline_keyboards import get_reminder_type_keyboard, get_weekdays_keyboard, get_reminder_management_keyboard
from keyboards.reply_keyboards import get_main_keyboard
from telegram.error import BadRequest

async def delete_message(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int):
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except BadRequest:
        pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот для напоминаний.\n\n"
        "Я помогу вам не забыть о важных делах и событиях.\n"
        "Вы можете создавать:\n"
        "• Ежедневные напоминания\n"
        "• Еженедельные напоминания\n"
        "• Ежемесячные напоминания\n"
        "• Ежегодные напоминания\n"
        "• Одноразовые напоминания\n\n"
        "Используйте кнопки меню для управления:",
        reply_markup=get_main_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 *Основные команды:*\n"
        "/new или 📝 Новое напоминание - создать напоминание\n"
        "/list или 📋 Мои напоминания - список ваших напоминаний\n"
        "/help или ℹ️ Помощь - показать это сообщение\n\n"
        "*Типы напоминаний:*\n"
        "• Ежедневные - каждый день в указанное время\n"
        "• Еженедельные - в выбранные дни недели\n"
        "• Ежемесячные - каждый месяц в указанную дату\n"
        "• Ежегодные - каждый год в указанную дату\n"
        "• Одноразовые - только один раз в указанную дату\n\n"
        "Для удаления напоминания используйте кнопку 'Удалить' в списке напоминаний.",
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )

async def new_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
# Очищаем предыдущие данные
    context.user_data.clear()
    
    # Удаляем команду пользователя
    await update.message.delete()
    
    # Сохраняем новое сообщение
    message = await update.message.reply_text(
        "Выберите тип напоминания:",
        reply_markup=get_reminder_type_keyboard()
    )
    context.user_data['last_bot_message'] = message.message_id

def validate_date(date_str):
    try:
        date = datetime.strptime(date_str, '%d.%m.%Y')
        current_date = datetime.now()
        
        # Убираем время для корректного сравнения дат
        current_date = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
        date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        if date < current_date:
            return False, "Дата не может быть в прошлом!"
        return True, date.strftime('%Y-%m-%d')
    except ValueError:
        return False, "Неверный формат даты!"

async def list_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reminders = get_user_reminders(update.effective_user.id)
    
    if not reminders:
        await update.message.reply_text("У вас нет активных напоминаний.")
        return

    for reminder in reminders:
        reminder_id, user_id, text, reminder_type, days_of_week, time, date, is_active, last_reminded = reminder
        
        status = "🔔 Активно" if is_active else "🔕 Отключено"
        reminder_text = f"📝 {text}\n⏰ {time}\n{status}\n"
        
        if reminder_type == 'daily':
            reminder_text += "🔄 Ежедневно"
        elif reminder_type == 'weekly':
            days = days_of_week.split(',')
            days_text = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
            selected_days = [days_text[int(d)-1] for d in days]
            reminder_text += f"🔄 Еженедельно ({', '.join(selected_days)})"
        elif reminder_type == 'monthly':
            reminder_text += f"🔄 Ежемесячно ({date})"
        elif reminder_type == 'yearly':
            reminder_text += f"🔄 Ежегодно ({date})"
        else:
            reminder_text += f"📅 Одноразово ({date})"
        
        await update.message.reply_text(
            reminder_text,
            reply_markup=get_reminder_management_keyboard(reminder_id, is_active)
        )

async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # Обработка текстовых команд меню
    if text == "📝 Новое напоминание":
        await new_reminder(update, context)
        return
    elif text == "📋 Мои напоминания":
        await list_reminders(update, context)
        return
    elif text == "ℹ️ Помощь":
        await help_command(update, context)
        return
    
    # Удаляем предыдущее сообщение бота, если оно есть
    if 'last_bot_message' in context.user_data:
        await delete_message(context, update.effective_chat.id, context.user_data['last_bot_message'])

    if 'editing_reminder' in context.user_data:
        reminder_id = context.user_data['editing_reminder']
        edit_type = context.user_data['edit_type']
        
        if edit_type == 'text':
            update_reminder(reminder_id, text=update.message.text)
            message = await update.message.reply_text("✅ Текст напоминания обновлен!")
            context.user_data['last_bot_message'] = message.message_id
        
        context.user_data.clear()
        await update.message.delete()
        await list_reminders(update, context)
        return

    if 'waiting_for' not in context.user_data:
        return
# Удаляем сообщение пользователя
    await update.message.delete()

    if context.user_data['waiting_for'] == 'text':
        context.user_data['text'] = update.message.text
        
        if context.user_data['reminder_type'] == 'weekly':
            message = await update.message.reply_text(
                "Выберите дни недели:",
                reply_markup=get_weekdays_keyboard()
            )
        elif context.user_data['reminder_type'] in ['monthly', 'yearly', 'once']:
            message = await update.message.reply_text("Введите дату в формате ДД.ММ.ГГГГ:")
            context.user_data['waiting_for'] = 'date'
        else:  # daily
            message = await update.message.reply_text("Введите время в формате ЧЧ:ММ")
            context.user_data['waiting_for'] = 'time'
        context.user_data['last_bot_message'] = message.message_id
    
    elif context.user_data['waiting_for'] == 'date':
        is_valid, result = validate_date(update.message.text)
        if not is_valid:
            message = await update.message.reply_text(f"❌ {result}")
            context.user_data['last_bot_message'] = message.message_id
            return
        
        context.user_data['date'] = result
        message = await update.message.reply_text("Введите время в формате ЧЧ:ММ")
        context.user_data['last_bot_message'] = message.message_id
        context.user_data['waiting_for'] = 'time'
    
    elif context.user_data['waiting_for'] == 'time':
        try:
            time = datetime.strptime(update.message.text, '%H:%M')
            context.user_data['time'] = time.strftime('%H:%M')
            
            # Сохраняем напоминание
            reminder_id = add_reminder(
                user_id=update.effective_user.id,
                text=context.user_data['text'],
                reminder_type=context.user_data['reminder_type'],
                days_of_week=','.join(context.user_data.get('selected_days', [])),
                time=context.user_data['time'],
                date=context.user_data.get('date')
            )
            
            message = await update.message.reply_text("✅ Напоминание успешно создано!")
            context.user_data['last_bot_message'] = message.message_id
            # Удаляем сообщение о создании через 3 секунды
            context.job_queue.run_once(
                lambda ctx: delete_message(context, update.effective_chat.id, message.message_id),
                3
            )
            
            context.user_data.clear()
        except ValueError:
            message = await update.message.reply_text("❌ Неверный формат времени. Попробуйте снова (ЧЧ:ММ):")
            context.user_data['last_bot_message'] = message.message_id

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("type_"):
        reminder_type = query.data.split("_")[1]
        context.user_data['reminder_type'] = reminder_type
        await query.message.edit_text("Введите текст напоминания:")
        context.user_data['waiting_for'] = 'text'
        context.user_data['last_bot_message'] = query.message.message_id
    
    elif query.data.startswith("edit_"):
        _, edit_type, reminder_id = query.data.split("_")
        reminder = get_reminder_by_id(int(reminder_id))
        
        if not reminder:
            await query.message.edit_text("❌ Напоминание не найдено!")
            return
        
        context.user_data['editing_reminder'] = int(reminder_id)
        context.user_data['edit_type'] = edit_type
        
        if edit_type == 'text':
            await query.message.edit_text("Введите новый текст напоминания:")
        elif edit_type == 'time':
            await query.message.edit_text("Введите новое время в формате ЧЧ:ММ:")
        elif edit_type == 'date':
            await query.message.edit_text("Введите новую дату в формате ДД.ММ.ГГГГ:")
        context.user_data['last_bot_message'] = query.message.message_id
    elif query.data.startswith("toggle_"):
        reminder_id = int(query.data.split("_")[1])
        new_status = toggle_reminder(reminder_id)
        status_text = "включено" if new_status else "отключено"
        await query.message.edit_text(
            f"Напоминание {status_text}!",
            reply_markup=get_reminder_management_keyboard(reminder_id, new_status)
        )

    elif query.data.startswith("day_"):
        if 'selected_days' not in context.user_data:
            context.user_data['selected_days'] = []
        
        day = query.data.split("_")[1]
        if day in context.user_data['selected_days']:
            context.user_data['selected_days'].remove(day)
        else:
            context.user_data['selected_days'].append(day)
        
        # Обновляем сообщение с выбранными днями
        days_text = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
        selected = [days_text[int(d)-1] for d in context.user_data['selected_days']]
        await query.message.edit_text(
            f"Выбранные дни: {', '.join(selected) if selected else 'нет'}\n"
            "Выберите дни недели:",
            reply_markup=get_weekdays_keyboard()
        )
        context.user_data['last_bot_message'] = query.message.message_id
    
    elif query.data == "days_done":
        if not context.user_data.get('selected_days'):
            await query.message.edit_text("Выберите хотя бы один день недели:")
            return
        
        await query.message.edit_text("Введите время в формате ЧЧ:ММ")
        context.user_data['waiting_for'] = 'time'
    
    elif query.data.startswith("delete_"):
        reminder_id = int(query.data.split("_")[1])
        delete_reminder(reminder_id)
        await query.message.edit_text("Напоминание удалено!")