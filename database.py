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

        # Ensure existing databases also have the created_at column
        connection.execute("""
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS created_at TIMESTAMP
            DEFAULT CURRENT_TIMESTAMP
        """)

        # Global allergies table
        connection.execute("""
            CREATE TABLE IF NOT EXISTS allergies (
                allergy_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                allergy_name TEXT UNIQUE NOT NULL
            )
        """)

        # Ensure existing databases also have the is_active column
        connection.execute("""
            ALTER TABLE allergies
            ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE
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

        # Store inventory allergen verification results
        connection.execute("""
            CREATE TABLE IF NOT EXISTS inventory_verifications (
                inventory_id INTEGER PRIMARY KEY,
                

                verification_status VARCHAR(20) NOT NULL
                    CHECK (
                        verification_status IN (
                            'allergen_free',
                            'allergic'
                        )
                    ),

                allergy_id INTEGER,

                verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (inventory_id)
                    REFERENCES inventory(inventory_id)
                    ON DELETE CASCADE,

                FOREIGN KEY (allergy_id)
                    REFERENCES allergies(allergy_id),

                CONSTRAINT valid_verification_allergy
                    CHECK (
                        (
                            verification_status = 'allergen_free'
                            AND allergy_id IS NULL
                        )
                        OR verification_status = 'allergic'
                    )
            )
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

        # Store predefined food suggestions
        connection.execute("""
            CREATE TABLE IF NOT EXISTS food_suggestions (
                food_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                food_name VARCHAR(100) UNIQUE NOT NULL,
                category VARCHAR(30) NOT NULL
            )
        """)

        # Insert predefined food suggestions
        connection.execute("""
            WITH predefined_foods (food_name, category) AS (
                VALUES
                    ('Rice', 'Non-perishable'),
                    ('Wheat Flour', 'Non-perishable'),
                    ('Cooking Oil', 'Non-perishable'),
                    ('Salt', 'Non-perishable'),
                    ('Sugar', 'Non-perishable'),

                    ('Toor Dal', 'Non-perishable'),
                    ('Moong Dal', 'Non-perishable'),
                    ('Chana Dal', 'Non-perishable'),
                    ('Chickpeas', 'Non-perishable'),
                    ('Kidney Beans', 'Non-perishable'),

                    ('Milk', 'Perishable'),
                    ('Eggs', 'Perishable'),
                    ('Bread', 'Highly perishable'),
                    ('Butter', 'Perishable'),
                    ('Curd', 'Perishable'),

                    ('Onion', 'Semi-perishable'),
                    ('Tomato', 'Highly perishable'),
                    ('Potato', 'Semi-perishable'),
                    ('Garlic', 'Semi-perishable'),
                    ('Ginger', 'Semi-perishable'),
                    ('Green Chilli', 'Highly perishable'),

                    ('Turmeric Powder', 'Non-perishable'),
                    ('Red Chilli Powder', 'Non-perishable'),
                    ('Coriander Powder', 'Non-perishable'),
                    ('Cumin Seeds', 'Non-perishable'),

                    ('Apple', 'Highly perishable'),
                    ('Banana', 'Highly perishable'),
                    ('Canned Beans', 'Canned'),
                    ('Frozen Peas', 'Frozen'),
                    ('Raisins', 'Dehydrated'),
                    ('Bhujia Namkeen', 'Non-perishable'),
                    ('Butter Cookies', 'Non-perishable'),
                    ('Chocolate Biscuits', 'Non-perishable'),
                    ('Chocolate Wafer', 'Non-perishable'),
                    ('Cream Biscuits', 'Non-perishable'),
                    ('Masala Noodles', 'Non-perishable'),
                    ('Milk Rusk', 'Non-perishable'),
                    ('Peanut Cookies', 'Non-perishable'),
                    ('Sesame Crackers', 'Non-perishable'),
                    ('Spicy Mixture', 'Non-perishable')
            )

            INSERT INTO food_suggestions (food_name, category)
            SELECT
                predefined.food_name,
                predefined.category
            FROM predefined_foods AS predefined
            WHERE NOT EXISTS (
                SELECT 1
                FROM food_suggestions AS existing
                WHERE LOWER(TRIM(existing.food_name)) =
                    LOWER(TRIM(predefined.food_name))
            )
        """)

        # Map food items to their allergens
        connection.execute("""
            CREATE TABLE IF NOT EXISTS food_allergens (
                food_id INTEGER NOT NULL,
                allergy_id INTEGER NOT NULL,

                PRIMARY KEY (food_id, allergy_id),

                FOREIGN KEY (food_id)
                    REFERENCES food_suggestions(food_id)
                    ON DELETE CASCADE,

                FOREIGN KEY (allergy_id)
                    REFERENCES allergies(allergy_id)
                    ON DELETE CASCADE
            )
        """)

        # Predefined food allergen mappings
        connection.execute("""
            WITH predefined_mappings (food_name, allergy_name) AS (
                VALUES
                    ('Bhujia Namkeen', 'Peanuts'),
                    ('Bhujia Namkeen', 'Wheat'),

                    ('Butter Cookies', 'Eggs'),
                    ('Butter Cookies', 'Milk'),
                    ('Butter Cookies', 'Wheat'),

                    ('Chocolate Biscuits', 'Milk'),
                    ('Chocolate Biscuits', 'Soy'),
                    ('Chocolate Biscuits', 'Wheat'),

                    ('Chocolate Wafer', 'Milk'),
                    ('Chocolate Wafer', 'Soy'),
                    ('Chocolate Wafer', 'Wheat'),

                    ('Cream Biscuits', 'Milk'),
                    ('Cream Biscuits', 'Soy'),
                    ('Cream Biscuits', 'Wheat'),

                    ('Masala Noodles', 'Soy'),
                    ('Masala Noodles', 'Wheat'),

                    ('Milk', 'Milk'),

                    ('Milk Rusk', 'Milk'),
                    ('Milk Rusk', 'Wheat'),

                    ('Peanut Cookies', 'Milk'),
                    ('Peanut Cookies', 'Peanuts'),
                    ('Peanut Cookies', 'Wheat'),

                    ('Sesame Crackers', 'Sesame'),
                    ('Sesame Crackers', 'Wheat'),

                    ('Spicy Mixture', 'Peanuts'),
                    ('Spicy Mixture', 'Wheat')
            )
            INSERT INTO food_allergens (food_id, allergy_id)
            SELECT
                fs.food_id,
                a.allergy_id
            FROM predefined_mappings AS pm
            JOIN food_suggestions AS fs
                ON LOWER(TRIM(fs.food_name)) = LOWER(TRIM(pm.food_name))
            JOIN allergies AS a
                ON LOWER(TRIM(a.allergy_name)) = LOWER(TRIM(pm.allergy_name))
            ON CONFLICT (food_id, allergy_id) DO NOTHING
        """)

        # Store predefined essential food items
        connection.execute("""
            CREATE TABLE IF NOT EXISTS essential_foods (
                food_id INTEGER PRIMARY KEY
                    REFERENCES food_suggestions(food_id)
                    ON DELETE CASCADE,

                display_order INTEGER NOT NULL
            )
        """)

        # Link predefined foods to the essential foods list
        connection.execute("""
            WITH predefined_foods (food_name, display_order) AS (
                VALUES
                    ('Rice', 1),
                    ('Wheat Flour', 2),
                    ('Cooking Oil', 3),
                    ('Salt', 4),
                    ('Sugar', 5),
                    ('Toor Dal', 6),
                    ('Moong Dal', 7),
                    ('Chana Dal', 8),
                    ('Chickpeas', 9),
                    ('Kidney Beans', 10),
                    ('Milk', 11),
                    ('Eggs', 12),
                    ('Bread', 13),
                    ('Butter', 14),
                    ('Curd', 15),
                    ('Onion', 16),
                    ('Tomato', 17),
                    ('Potato', 18),
                    ('Garlic', 19),
                    ('Ginger', 20),
                    ('Green Chilli', 21),
                    ('Turmeric Powder', 22),
                    ('Red Chilli Powder', 23),
                    ('Coriander Powder', 24),
                    ('Cumin Seeds', 25)
            )

            INSERT INTO essential_foods (food_id, display_order)
            SELECT
                food.food_id,
                predefined.display_order
            FROM predefined_foods AS predefined
            JOIN food_suggestions AS food
                ON LOWER(TRIM(food.food_name)) =
                LOWER(TRIM(predefined.food_name))
            ON CONFLICT (food_id) DO NOTHING
        """)

        # Index essential foods by display order
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_essential_foods_display_order
            ON essential_foods (display_order)
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

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_allergies_allergy
            ON user_allergies(allergy_id)
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_recipe
            ON recipe_ingredients(recipe_id)
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_recipe_instructions_recipe
            ON recipe_instructions(recipe_id)
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_shopping_history_items_food
            ON shopping_history_items(food_id)
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_active_shopping_items_food
            ON active_shopping_items(food_id)
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_food_allergens_allergy
            ON food_allergens(allergy_id)
        """)
