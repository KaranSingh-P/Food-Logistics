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

        # Store recipe information
        connection.execute("""
            CREATE TABLE IF NOT EXISTS recipes (
                recipe_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                recipe_name TEXT NOT NULL,
                description TEXT,

                meal_type VARCHAR(20) NOT NULL
                    CHECK (
                        meal_type IN (
                            'Breakfast',
                            'Lunch',
                            'Dinner',
                            'Brunch',
                            'Snack',
                            'Dessert'
                        )
                    ),

                dietary_preferences TEXT[] NOT NULL DEFAULT '{}',

                preparation_time INTEGER,
                servings INTEGER,

                calories NUMERIC(8, 2),
                protein NUMERIC(8, 2),
                carbohydrates NUMERIC(8, 2),
                fat NUMERIC(8, 2),

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Store ingredients belonging to each recipe
        connection.execute("""
            CREATE TABLE IF NOT EXISTS recipe_ingredients (
                recipe_ingredient_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                recipe_id INTEGER NOT NULL,
                ingredient_name TEXT NOT NULL,
                amount TEXT NOT NULL,

                FOREIGN KEY (recipe_id)
                    REFERENCES recipes(recipe_id)
                    ON DELETE CASCADE
            )
        """)

        # Store step-by-step cooking instructions
        connection.execute("""
            CREATE TABLE IF NOT EXISTS recipe_instructions (
                instruction_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                recipe_id INTEGER NOT NULL,
                step_number INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,

                FOREIGN KEY (recipe_id)
                    REFERENCES recipes(recipe_id)
                    ON DELETE CASCADE,

                UNIQUE (recipe_id, step_number)
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS user_recipe_history (
                history_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

                user_id INTEGER NOT NULL,
                recipe_id INTEGER NOT NULL,

                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE,

                FOREIGN KEY (recipe_id)
                    REFERENCES recipes(recipe_id)
                    ON DELETE CASCADE
            )
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_recipe_history_user_generated
            ON user_recipe_history(user_id, generated_at DESC)
        """)


        # Store each user's active shopping list
        connection.execute("""
            CREATE TABLE IF NOT EXISTS active_shopping_lists (
                list_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

                user_id INTEGER NOT NULL UNIQUE,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
            )
        """)

        # Store items belonging to active shopping lists
        connection.execute("""
            CREATE TABLE IF NOT EXISTS active_shopping_items (
                item_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

                list_id INTEGER NOT NULL,
                food_id INTEGER,

                item_name TEXT NOT NULL,
                quantity TEXT NOT NULL DEFAULT '',
                is_completed BOOLEAN NOT NULL DEFAULT FALSE,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (list_id)
                    REFERENCES active_shopping_lists(list_id)
                    ON DELETE CASCADE,

                FOREIGN KEY (food_id)
                    REFERENCES food_suggestions(food_id)
                    ON DELETE SET NULL
            )
        """)

        # Store saved shopping list history
        connection.execute("""
            CREATE TABLE IF NOT EXISTS shopping_history (
                history_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

                user_id INTEGER NOT NULL,
                saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
            )
        """)

        # Store items belonging to historical shopping lists
        connection.execute("""
            CREATE TABLE IF NOT EXISTS shopping_history_items (
                history_item_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

                history_id INTEGER NOT NULL,
                food_id INTEGER,

                item_name TEXT NOT NULL,
                quantity TEXT NOT NULL DEFAULT '',
                is_completed BOOLEAN NOT NULL DEFAULT FALSE,

                FOREIGN KEY (history_id)
                    REFERENCES shopping_history(history_id)
                    ON DELETE CASCADE,

                FOREIGN KEY (food_id)
                    REFERENCES food_suggestions(food_id)
                    ON DELETE SET NULL
            )
        """)

        # Indexes for shopping list queries
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_active_shopping_items_list
            ON active_shopping_items(list_id)
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_shopping_history_user_saved
            ON shopping_history(user_id, saved_at DESC)
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_shopping_history_items_history
            ON shopping_history_items(history_id)
        """)
