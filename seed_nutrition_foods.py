
from database import get_db_connection


# Nutritional values are approximate and are per 100 grams.
# Format: food_name, calories, protein, carbohydrates, fats

nutrition_foods = [

    # Existing predefined foods
    ("Chapati", 297, 9.6, 46.0, 7.5),
    ("Rice", 130, 2.7, 28.0, 0.3),
    ("Dal", 116, 9.0, 20.0, 0.4),
    ("Banana", 89, 1.1, 22.8, 0.3),

    # Grains and flour
    ("Basmati Rice", 356, 7.5, 78.0, 0.7),
    ("Broken Wheat", 342, 12.3, 75.9, 1.3),
    ("Bread", 265, 9.0, 49.0, 3.2),
    ("Bread Crumbs", 395, 13.4, 72.0, 5.3),
    ("Wheat Flour", 364, 10.3, 76.3, 1.0),
    ("Besan", 387, 22.4, 57.8, 6.7),
    ("Semolina", 360, 12.7, 72.8, 1.1),
    ("Poha", 350, 6.5, 77.0, 1.0),
    ("Oats", 389, 16.9, 66.3, 6.9),

    # Pulses and legumes
    ("Chickpeas", 364, 19.3, 60.7, 6.0),
    ("Kidney Beans", 333, 23.6, 60.0, 0.8),
    ("Moong Dal", 347, 24.0, 63.0, 1.2),
    ("Toor Dal", 343, 22.3, 62.8, 1.7),
    ("Moong Sprouts", 30, 3.0, 5.9, 0.2),
    ("Green Peas", 81, 5.4, 14.5, 0.4),
    ("Peanuts", 567, 25.8, 16.1, 49.2),

    # Dairy and eggs
    ("Milk", 61, 3.2, 4.8, 3.3),
    ("Curd", 61, 3.5, 4.7, 3.3),
    ("Paneer", 265, 18.3, 1.2, 20.8),
    ("Butter", 717, 0.9, 0.1, 81.1),
    ("Fresh Cream", 340, 2.8, 3.0, 36.0),
    ("Ghee", 900, 0.0, 0.0, 100.0),
    ("Eggs", 143, 12.6, 0.7, 9.5),

    # Vegetables
    ("Cabbage", 25, 1.3, 5.8, 0.1),
    ("Capsicum", 31, 1.0, 6.0, 0.3),
    ("Carrots", 41, 0.9, 9.6, 0.2),
    ("Cauliflower", 25, 1.9, 5.0, 0.3),
    ("Cucumber", 15, 0.7, 3.6, 0.1),
    ("Drumsticks", 37, 2.1, 8.5, 0.2),
    ("Eggplant", 25, 1.0, 5.9, 0.2),
    ("Garlic", 149, 6.4, 33.1, 0.5),
    ("Ginger", 80, 1.8, 17.8, 0.8),
    ("Green Chilli", 40, 2.0, 9.5, 0.2),
    ("Mushrooms", 22, 3.1, 3.3, 0.3),
    ("Onion", 40, 1.1, 9.3, 0.1),
    ("Potato", 77, 2.0, 17.5, 0.1),
    ("Spinach", 23, 2.9, 3.6, 0.4),
    ("Spring Onions", 32, 1.8, 7.3, 0.2),
    ("Sweet Corn", 86, 3.3, 19.0, 1.4),
    ("Tomato", 18, 0.9, 3.9, 0.2),
    ("Coriander Leaves", 23, 2.1, 3.7, 0.5),
    ("Curry Leaves", 108, 6.1, 18.7, 1.0),

    # Fruits and other ingredients
    ("Lemon Juice", 22, 0.4, 6.9, 0.2),
    ("Tamarind", 239, 2.8, 62.5, 0.6),
    ("Coconut Milk", 230, 2.3, 5.5, 23.8),
    ("Honey", 304, 0.3, 82.4, 0.0),
    ("Water", 0, 0, 0, 0),

    # Oils
    ("Cooking Oil", 884, 0, 0, 100),
    ("Olive Oil", 884, 0, 0, 100),

    # Spices and seasonings
    ("Ajwain", 305, 16.0, 43.0, 25.0),
    ("Baking Powder", 53, 0, 28.0, 0),
    ("Black Pepper", 251, 10.4, 64.0, 3.3),
    ("Chaat Masala", 250, 10.0, 45.0, 5.0),
    ("Chole Masala", 300, 12.0, 45.0, 10.0),
    ("Cinnamon Powder", 247, 4.0, 81.0, 1.2),
    ("Coriander Powder", 298, 12.4, 54.0, 17.8),
    ("Cumin Powder", 375, 18.0, 44.0, 22.0),
    ("Cumin Seeds", 375, 18.0, 44.0, 22.0),
    ("Garam Masala", 379, 12.0, 49.0, 15.0),
    ("Mustard Seeds", 508, 26.1, 28.1, 36.2),
    ("Red Chilli Powder", 282, 13.5, 50.0, 14.3),
    ("Sambar Powder", 300, 12.0, 50.0, 8.0),
    ("Salt", 0, 0, 0, 0),
    ("Turmeric Powder", 312, 9.7, 67.1, 3.3),

    # Prepared ingredients and pastes
    ("Dosa Batter", 120, 3.0, 24.0, 1.0),
    ("Idli Batter", 120, 3.0, 24.0, 1.0),
    ("Ginger-Garlic Paste", 100, 4.0, 18.0, 1.0),
    ("Green Chutney", 80, 3.0, 10.0, 3.0),
    ("Soy Sauce", 53, 8.1, 4.9, 0.6),
]


# Recipe ingredient variations mapped to standard food names.
# This prevents duplicate entries for plural forms.

ingredient_aliases = {
    "Bananas": "Banana",
    "Onions": "Onion",
    "Potatoes": "Potato",
    "Green Chillies": "Green Chilli",
    "Tomatoes": "Tomato",
}


def seed_nutrition_foods():

    with get_db_connection() as connection:

        # Make sure the sequence starts after the highest existing ID.
        connection.execute("""
            SELECT setval(
                'public.nutrition_foods_food_id_seq',
                GREATEST(
                    COALESCE(
                        (SELECT MAX(food_id) FROM nutrition_foods), 0
                    ) + 1,
                    1
                ),
                false
            )
        """)

        inserted = 0
        updated = 0

        for food_name, calories, protein, carbs, fats in nutrition_foods:

            food_name = ingredient_aliases.get(
                food_name, food_name
            )

            existing = connection.execute("""
                SELECT food_id
                FROM nutrition_foods
                WHERE user_id IS NULL
                  AND LOWER(food_name) = LOWER(%s)
                LIMIT 1
            """, (food_name,)).fetchone()

            if existing:

                # Update only predefined foods.
                connection.execute("""
                    UPDATE nutrition_foods
                    SET
                        food_name = %s,
                        calories = %s,
                        protein = %s,
                        carbohydrates = %s,
                        fats = %s,
                        is_custom = FALSE
                    WHERE food_id = %s
                      AND user_id IS NULL
                """, (
                    food_name,
                    calories,
                    protein,
                    carbs,
                    fats,
                    existing["food_id"]
                ))

                updated += 1

            else:

                connection.execute("""
                    INSERT INTO nutrition_foods (
                        user_id,
                        food_name,
                        calories,
                        protein,
                        carbohydrates,
                        fats,
                        is_custom
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, FALSE)
                    ON CONFLICT DO NOTHING
                """, (
                    None,
                    food_name,
                    calories,
                    protein,
                    carbs,
                    fats
                ))                
        inserted += 1

    print("Nutrition food seeding completed.")
    print(f"New foods added: {inserted}")
    print(f"Existing predefined foods updated: {updated}")


if __name__ == "__main__":
    seed_nutrition_foods()
