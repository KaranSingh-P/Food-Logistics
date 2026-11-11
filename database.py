
import sqlite3
import os

DATABASE = os.path.join(os.path.dirname(__file__), "users.db")


def get_db_connection():
    return sqlite3.connect(DATABASE)


def init_db():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()
