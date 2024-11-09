from contextlib import contextmanager
import sqlite3
import logging

@contextmanager
def database_connection():
    conn = None
    try:
        conn = sqlite3.connect('reminders.db')
        yield conn
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        raise
    finally:
        if conn:
            conn.close() 