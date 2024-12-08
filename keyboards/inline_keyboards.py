from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_reminder_type_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔄 Ежедневно", callback_data="type_daily")],
        [InlineKeyboardButton("📅 Еженедельно", callback_data="type_weekly")],
        [InlineKeyboardButton("📆 Ежемесячно", callback_data="type_monthly")],
        [InlineKeyboardButton("🗓 Ежегодно", callback_data="type_yearly")],
        [InlineKeyboardButton("🎂 День рождения", callback_data="type_birthday")],
        [InlineKeyboardButton("📌 Одноразово", callback_data="type_once")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_weekdays_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("Пн", callback_data="day_1"),
            InlineKeyboardButton("Вт", callback_data="day_2"),
            InlineKeyboardButton("Ср", callback_data="day_3")
        ],
        [
            InlineKeyboardButton("Чт", callback_data="day_4"),
            InlineKeyboardButton("Пт", callback_data="day_5"),
            InlineKeyboardButton("Сб", callback_data="day_6")
        ],
        [
            InlineKeyboardButton("Вс", callback_data="day_7")
        ],
        [InlineKeyboardButton("✅ Готово", callback_data="days_done")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_pagination_keyboard(current_page: int, total_pages: int, reminder_id: int, is_active: bool):
    """Создает клавиатуру с пагинацией и управлением напоминанием"""
    keyboard = [
        [
            InlineKeyboardButton("✏️ Изменить текст", callback_data=f"edit_text_{reminder_id}"),
            InlineKeyboardButton("⏰ Изменить время", callback_data=f"edit_time_{reminder_id}")
        ],
        [
            InlineKeyboardButton("📅 Изменить дату", callback_data=f"edit_date_{reminder_id}")
        ],
        [
            InlineKeyboardButton(
                "🔕 Выключить" if is_active else "🔔 Включить",
                callback_data=f"toggle_{reminder_id}"
            ),
            InlineKeyboardButton("🗑 Удалить", callback_data=f"delete_{reminder_id}")
        ]
    ]
    
    # Добавляем кнопки пагинации
    pagination_row = []
    if current_page > 1:
        pagination_row.append(InlineKeyboardButton("◀️", callback_data=f"page_{current_page-1}"))
    pagination_row.append(InlineKeyboardButton(f"{current_page}/{total_pages}", callback_data="ignore"))
    if current_page < total_pages:
        pagination_row.append(InlineKeyboardButton("▶️", callback_data=f"page_{current_page+1}"))
    
    keyboard.append(pagination_row)
    return InlineKeyboardMarkup(keyboard) 

def get_reminder_management_keyboard(reminder_id: int, is_active: bool):
    keyboard = [
        [
            InlineKeyboardButton("✏️ Изменить текст", callback_data=f"edit_text_{reminder_id}"),
            InlineKeyboardButton("⏰ Изменить время", callback_data=f"edit_time_{reminder_id}")
        ],
        [
            InlineKeyboardButton("📅 Изменить дату", callback_data=f"edit_date_{reminder_id}")
        ],
        [
            InlineKeyboardButton(
                "🔕 Выключить" if is_active else "🔔 Включить",
                callback_data=f"toggle_{reminder_id}"
            ),
            InlineKeyboardButton("🗑 Удалить", callback_data=f"delete_{reminder_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard) 

def get_create_reminder_keyboard():
    """Создает клавиатуру с подтверждением создания напоминания"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Да", callback_data="create_reminder_yes"),
            InlineKeyboardButton("❌ Нет", callback_data="create_reminder_no")
        ]
    ]
    return InlineKeyboardMarkup(keyboard) 