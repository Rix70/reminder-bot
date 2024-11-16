import sqlite3
from datetime import datetime
import logging
from .db_context import database_connection

def init_db():
    '''Инициализация базы данных'''
    try:
        with database_connection() as conn:
            c = conn.cursor()
            c.execute('''
        CREATE TABLE IF NOT EXISTS reminders
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         user_id INTEGER,
         text TEXT,
         reminder_type TEXT,
         days_of_week TEXT,
         time TEXT,
         date TEXT,
         is_active INTEGER,
         last_reminded TEXT)
    ''')
    
            conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Ошибка при инициализации базы данных: {e}")
        raise

def add_reminder(user_id, text, reminder_type, days_of_week=None, time=None, date=None):
    '''Добавление напоминания'''
    try:
        with database_connection() as conn:
            c = conn.cursor()
            logging.info(f"Adding reminder: user={user_id}, type={reminder_type}, "
                        f"text={text}, time={time}, date={date}, days={days_of_week}")
            
            c.execute('''
                INSERT INTO reminders 
                (user_id, text, reminder_type, days_of_week, time, date, is_active, last_reminded)
                VALUES (?, ?, ?, ?, ?, ?, 1, ?)
            ''', (user_id, text, reminder_type, days_of_week, time, date, 
                  datetime.now().strftime('%Y-%m-%d')))
            
            reminder_id = c.lastrowid
            conn.commit()
            logging.info(f"Successfully added reminder {reminder_id}")
            return reminder_id
    except sqlite3.Error as e:
        logging.error(f"Error adding reminder: {e}")
        raise

def get_all_reminders(user_id):
    '''Получение всех напоминаний пользователя'''
    try:
        with database_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM reminders WHERE user_id = ?', (user_id,))
            return c.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Ошибка при получении напоминаний: {e}")
        raise

def get_active_reminders():
    '''Получение активных напоминаний'''
    try:
        with database_connection() as conn:
            c = conn.cursor()
            c.execute('''
                SELECT * FROM reminders 
                WHERE is_active = 1 
                ORDER BY time ASC
            ''')
            return c.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Ошибка при получении активных напоминаний: {e}")
        raise

def get_reminder_by_id(reminder_id):
    '''Получение напоминания по ID'''
    try:
        with database_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM reminders WHERE id = ?', (reminder_id,))
            return c.fetchone()
    except sqlite3.Error as e:
        logging.error(f"Ошибка при получении напоминания по ID: {e}")
        raise

def update_reminder(reminder_id, **kwargs):
    '''Обновление напоминания'''
    try:
        with database_connection() as conn:
            c = conn.cursor()
            update_fields = [f'{key} = ?' for key in kwargs.keys()]
            params = list(kwargs.values()) + [reminder_id]
            
            query = f'UPDATE reminders SET {", ".join(update_fields)} WHERE id = ?'
            c.execute(query, params)
            conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Ошибка при обновлении напоминания: {e}")
        raise

def update_last_reminded(reminder_id):
    '''Обновление даты последнего напоминания'''
    try:
        with database_connection() as conn:
            c = conn.cursor()
            c.execute('UPDATE reminders SET last_reminded = ? WHERE id = ?', 
                    (datetime.now().strftime('%Y-%m-%d'), reminder_id))
            conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Ошибка при обновлении времени напоминания: {e}")
        raise

def delete_reminder(reminder_id):
    '''Удаление напоминания'''
    try:
        with database_connection() as conn:
            c = conn.cursor()
            c.execute('DELETE FROM reminders WHERE id = ?', (reminder_id,))
            conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Ошибка при удалении напоминания: {e}")
        raise

def toggle_reminder(reminder_id):
    '''Переключение статуса напоминания'''
    try:
        with database_connection() as conn:
            c = conn.cursor()
            # Начинаем транзакцию
            conn.execute('BEGIN TRANSACTION')
            try:
                c.execute('''
                    UPDATE reminders 
                    SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END 
                    WHERE id = ?
                ''', (reminder_id,))
                
                c.execute('SELECT is_active FROM reminders WHERE id = ?', (reminder_id,))
                new_status = c.fetchone()[0]
                
                conn.commit()
                return new_status
            except Exception as e:
                conn.rollback()
                raise
    except sqlite3.Error as e:
        logging.error(f"Ошибка при переключении статуса напоминания: {e}")
        raise

def cleanup_old_reminders():
    """Очищает старые неактивные напоминания из базы данных"""
    try:
        with database_connection() as conn:
            c = conn.cursor()
            # Начинаем транзакцию
            conn.execute('BEGIN TRANSACTION')
            try:
                # Деактивируем просроченные одноразовые напоминания
                c.execute('''
                    UPDATE reminders 
                    SET is_active = 0 
                    WHERE reminder_type = 'once' 
                    AND date < date('now')
                    AND is_active = 1
                ''')
                
                # Удаляем неактивные напоминания старше 30 дней
                c.execute('''
                    DELETE FROM reminders 
                    WHERE is_active = 0 
                    AND last_reminded < date('now', '-30 days')
                ''')
                
                deleted_count = c.rowcount
                conn.commit()
                logging.info(f"Удалено {deleted_count} старых напоминаний")
            except Exception as e:
                conn.rollback()
                raise
    except sqlite3.Error as e:
        logging.error(f"Ошибка при очистке старых напоминаний: {e}")
        raise