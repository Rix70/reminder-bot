# 🤖 Telegram Reminder Bot

Многофункциональный Telegram бот для управления напоминаниями. Позволяет создавать и управлять различными типами напоминаний: ежедневными, еженедельными, ежемесячными, ежегодными и одноразовыми.

## ✨ Основные возможности

- 📝 **Создание напоминаний:**
  - Ежедневные напоминания
  - Еженедельные напоминания с выбором дней
  - Ежемесячные напоминания
  - Ежегодные напоминания
  - Одноразовые напоминания

- ⚙️ **Управление напоминаниями:**
  - ✏️ Редактирование текста, времени и даты
  - 🔕 Включение/отключение напоминаний
  - ❌ Удаление напоминаний
  - 📋 Просмотр списка всех напоминаний

## 🛠 Технологии

- Python 3.9+
- python-telegram-bot 21.0+
- SQLite3
- APScheduler
- logging

## 🚀 Установка и запуск

1. **Клонирование репозитория:**

    ```bash
    git clone https://github.com/Rix70/reminder-bot.git
    cd reminder-bot
    ```

2. **Создание виртуального окружения:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Для Unix или MacOS
    venv\Scripts\activate     # Для Windows
    ```

3. **Установка зависимостей:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Настройка конфигурации:**

    - Откройте файл `config.py` и введите ваш `TELEGRAM_TOKEN` и `OWNER_ID`.

    ```python
    # config.py

    TELEGRAM_TOKEN = 'ВАШ_TELEGRAM_TOKEN'
    OWNER_ID = 'ВАШ_OWNER_ID'
    ```

5. **Инициализация базы данных:**

    База данных будет автоматически создана при первом запуске бота. Убедитесь, что у вас есть права на запись в директорию проекта.

6. **Запуск бота:**

    ```bash
    python main.py
    ```

    После запуска бот начнет работать и будет доступен в Telegram по вашему токену.

### Автоматическая установка (одной командой)
Скопируйте и вставьте следующую команду в терминал, находясь в директории проекта:

```bash
sudo bash -c 'cat > /etc/systemd/system/reminder-bot.service << EOL
[Unit]
Description=Telegram Reminder Bot
After=network.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory='$(pwd)'
ExecStart='$(pwd)'/venv/bin/python '$(pwd)'/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 🎯 Использование

После успешного запуска бота, вы можете воспользоваться следующими командами:

- `/start` — Начать взаимодействие с ботом.
- `/new` — Создать новое напоминание.
- `/list` — Показать все ваши напоминания.
- `/help` — Показать справочную информацию.

## 🔧 Настройка

Вы можете изменить настройки бота, отредактировав файл `config.py`. Например, изменить ID владельца или настроить дополнительные параметры.
## Структура проекта

```bash
reminder_bot/
├── main.py
├── config.py
├── database/
│   ├── db.py
│   └── db_context.py
├── requirements.txt
└── README.md
```






