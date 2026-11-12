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
        # Code to inserts huge list of allergies into the above table
        connection.cursor().executemany(
            """
            INSERT INTO allergies (allergy_name)
            VALUES (%s)
            ON CONFLICT (allergy_name) DO NOTHING
            """,
            [
                    ("Peanuts",),
                    ("Tree Nuts",),
                    ("Almonds",),
                    ("Cashews",),
                    ("Walnuts",),
                    ("Pistachios",),
                    ("Pecans",),
                    ("Hazelnuts",),
                    ("Macadamia Nuts",),
                    ("Brazil Nuts",),
                    ("Pine Nuts",),
                    ("Coconuts",),

                    ("Milk",),
                    ("Dairy",),
                    ("Lactose",),
                    ("Casein",),
                    ("Whey",),
                    ("Milk Protein",),

                    ("Eggs",),
                    ("Egg Whites",),
                    ("Egg Yolks",),
                    ("Albumin",),

                    ("Wheat",),
                    ("Gluten",),
                    ("Barley",),
                    ("Rye",),
                    ("Oats",),
                    ("Spelt",),
                    ("Semolina",),
                    ("Durum",),

                    ("Soy",),
                    ("Soybeans",),
                    ("Soy Protein",),
                    ("Soy Lecithin",),
                    ("Tofu",),
                    ("Tempeh",),

                    ("Fish",),
                    ("Salmon",),
                    ("Tuna",),
                    ("Cod",),
                    ("Sardines",),
                    ("Anchovies",),
                    ("Mackerel",),
                    ("Trout",),

                    ("Shellfish",),
                    ("Shrimp",),
                    ("Prawns",),
                    ("Crab",),
                    ("Lobster",),
                    ("Crayfish",),
                    ("Prawns",),
                    ("Clams",),
                    ("Oysters",),
                    ("Mussels",),
                    ("Scallops",),
                    ("Squid",),
                    ("Octopus",),

                    ("Sesame",),
                    ("Sesame Seeds",),
                    ("Sesame Oil",),
                    ("Tahini",),

                    ("Mustard",),
                    ("Mustard Seeds",),
                    ("Mustard Oil",),

                    ("Corn",),
                    ("Corn Starch",),
                    ("Corn Flour",),
                    ("Corn Syrup",),
                    ("High Fructose Corn Syrup",),
                    ("Corn Oil",),
                    ("Maltodextrin",),

                    ("Strawberries",),
                    ("Strawberry Extract",),
                    ("Strawberry Flavoring",),

                    ("Chocolate",),
                    ("Cocoa",),
                    ("Cocoa Powder",),
                    ("Cocoa Butter",),
                    ("Dark Chocolate",),
                    ("Milk Chocolate",),
                    ("White Chocolate",),

                    ("Yeast",),
                    ("Garlic",),
                    ("Onion",),
                    ("Celery",),
                    ("Carrot",),
                    ("Tomatoes",),
                    ("Potatoes",),
                    ("Peas",),
                    ("Lentils",),
                    ("Chickpeas",),
                    ("Beans",),
                    ("Coconut",),
                    ("Avocado",),
                    ("Banana",),
                    ("Pineapple",),
                    ("Kiwi",),
                    ("Mango",),
                    ("Apple",),
                    ("Peach",),
                    ("Pear",),
                    ("Grapes",),
                    ("Citrus Fruits",),
                    ("Oranges",),
                    ("Lemons",),
                    ("Limes",),
                    ("Pineapple",),
                    ("Mushrooms",),
                    ("Cinnamon",),
                    ("Black Pepper",),
                    ("Chili Pepper",),
                    ("Turmeric",),
                    ("Coriander",),
                    ("Cumin",),
                    ("Fenugreek",),
                    ("Poppy Seeds",),
                    ("Sunflower Seeds",),
                    ("Pumpkin Seeds",),
                    ("Flax Seeds",),
                    ("Chia Seeds",),
                    ("Quinoa",),
                    ("Buckwheat",),
                    ("Rice",),
                    ("Gelatin",),
                    ("Food Coloring",),
                    ("Artificial Sweeteners",),
                    ("Preservatives",),
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


