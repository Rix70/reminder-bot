from telegram import Update
from telegram.ext import ContextTypes
from keyboards.reply_keyboards import get_main_keyboard

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
        "/new или ✏️ Новое напоминание - создать напоминание\n"
        "/list_active или 📄 Активные напоминания - список ваших напоминаний\n"
        "/list_all или 📑 Все напоминания - список всех ваших напоминаний\n"
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