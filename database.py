import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
POSTGRES_BIN = r"C:\Program Files\PostgreSQL\18\bin"
_DLL_DIRECTORY = os.add_dll_directory(POSTGRES_BIN)
os.environ["PATH"] = POSTGRES_BIN + os.pathsep + os.environ["PATH"]
os.environ["PSYCOPG_IMPL"] = "python"
import psycopg
from psycopg.rows import dict_row
DATABASE_URL = os.getenv("DATABASE_URL")


def get_db_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is missing from .env")
    return psycopg.connect(
        DATABASE_URL,
        row_factory=dict_row
    )


def init_db():
    with get_db_connection() as connection:
        # User Accounts DB table
        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Global allergies table
        connection.execute("""
            CREATE TABLE IF NOT EXISTS allergies (
                allergy_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                allergy_name TEXT UNIQUE NOT NULL
            )
        """)
        # Insert the 14 main food allergen categories.
        connection.cursor().executemany(
            """
            INSERT INTO allergies (allergy_name)
            VALUES (%s)
            ON CONFLICT (allergy_name) DO NOTHING
            """,
            [
                ("Peanuts",),
                ("Tree Nuts",),
                ("Milk",),
                ("Eggs",),
                ("Wheat",),
                ("Soy",),
                ("Fish",),
                ("Shellfish",),
                ("Sesame",),
                ("Mustard",),
                ("Celery",),
                ("Lupin",),
                ("Molluscs",),
                ("Sulphites",)
            ]
        )
        # This table in DB contains User_id and their allergies
        connection.execute("""
            CREATE TABLE IF NOT EXISTS user_allergies (
                user_id INTEGER NOT NULL,
                allergy_id INTEGER NOT NULL,

                PRIMARY KEY (user_id, allergy_id),

                FOREIGN KEY (user_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE,

                FOREIGN KEY (allergy_id)
                    REFERENCES allergies(allergy_id)
                    ON DELETE CASCADE
            )
        """)

        # User Settings table
        connection.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                user_id INTEGER PRIMARY KEY,
                username TEXT NOT NULL DEFAULT '',
                theme TEXT NOT NULL DEFAULT 'light'
                    CHECK (theme IN ('light', 'dark')),

                FOREIGN KEY (user_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
            )
        """)

        connection.execute("""
            INSERT INTO user_settings (user_id)
            SELECT user_id FROM users
            ON CONFLICT (user_id) DO NOTHING
        """)

        # Inventory table
        connection.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                inventory_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                user_id INTEGER NOT NULL,
                item_name TEXT NOT NULL,
                category VARCHAR(30) NOT NULL,
                purchase_date DATE NOT NULL,
                expiration_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                CONSTRAINT fk_inventory_user
                    FOREIGN KEY (user_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE,

                CONSTRAINT check_inventory_category
                    CHECK (
                        category IN (
                            'perishable',
                            'highly-perishable',
                            'semi-perishable',
                            'non-perishable',
                            'canned',
                            'frozen',
                            'dehydrated',
                            'fermented'
                        )
                    ),

                CONSTRAINT check_inventory_dates
                    CHECK (expiration_date >= purchase_date)
            );
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_inventory_user_expiration
            ON inventory(user_id, expiration_date);
        """)


