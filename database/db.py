import sqlite3
from datetime import datetime
import logging
from .db_context import database_connection

def init_db():
    conn = sqlite3.connect('reminders.db')
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
    conn.close()

def add_reminder(user_id, text, reminder_type, days_of_week=None, time=None, date=None):
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO reminders (user_id, text, reminder_type, days_of_week, time, date, is_active, last_reminded)
        VALUES (?, ?, ?, ?, ?, ?, 1, ?)
    ''', (user_id, text, reminder_type, days_of_week, time, date, datetime.now().strftime('%Y-%m-%d')))
    
    reminder_id = c.lastrowid
    conn.commit()
    conn.close()
    return reminder_id

def get_user_reminders(user_id):
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    
    c.execute('SELECT * FROM reminders WHERE user_id = ? AND is_active = 1', (user_id,))
    reminders = c.fetchall()
    
    conn.close()
    return reminders

def delete_reminder(reminder_id):
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    
    c.execute('UPDATE reminders SET is_active = 0 WHERE id = ?', (reminder_id,))
    
    conn.commit()
    conn.close()

def update_last_reminded(reminder_id):
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    
    c.execute('UPDATE reminders SET last_reminded = ? WHERE id = ?', 
              (datetime.now().strftime('%Y-%m-%d'), reminder_id))
    
    conn.commit()
    conn.close()

def get_active_reminders():
    with database_connection() as conn:
        c = conn.cursor()
        c.execute('''
            SELECT * FROM reminders 
            WHERE is_active = 1 
            ORDER BY time ASC
        ''')
        return c.fetchall()

def get_reminder_by_id(reminder_id):
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    
    c.execute('SELECT * FROM reminders WHERE id = ?', (reminder_id,))
    reminder = c.fetchone()
    
    conn.close()
    return reminder

def update_reminder(reminder_id, **kwargs):
    with database_connection() as conn:
        c = conn.cursor()
        
        update_fields = [f'{key} = ?' for key in kwargs.keys()]
        params = list(kwargs.values()) + [reminder_id]
        
        query = f'UPDATE reminders SET {", ".join(update_fields)} WHERE id = ?'
        c.execute(query, params)
        conn.commit()

def toggle_reminder(reminder_id):
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    
    c.execute('UPDATE reminders SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END WHERE id = ?', 
              (reminder_id,))
    
    c.execute('SELECT is_active FROM reminders WHERE id = ?', (reminder_id,))
    new_status = c.fetchone()[0]
    
    conn.commit()
    conn.close()
    
    return new_status