from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_reminder_type_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔄 Ежедневно", callback_data="type_daily")],
        [InlineKeyboardButton("📅 Еженедельно", callback_data="type_weekly")],
        [InlineKeyboardButton("📆 Ежемесячно", callback_data="type_monthly")],
        [InlineKeyboardButton("🗓 Ежегодно", callback_data="type_yearly")],
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
