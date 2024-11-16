from contextlib import contextmanager
import sqlite3
import logging

@contextmanager
def database_connection():
    conn = None
    try:
        conn = sqlite3.connect('reminders.db')
        conn.row_factory = sqlite3.Row
        yield conn
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            try:
                conn.close()
            except sqlite3.Error as e:
                logging.error(f"Error closing database connection: {e}") 