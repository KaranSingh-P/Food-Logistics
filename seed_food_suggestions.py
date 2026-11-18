
from database import get_db_connection


# Storage categories for recipe ingredients
categories = {
    # Highly perishable
    "Bananas": "Highly perishable",
    "Coriander Leaves": "Highly perishable",
    "Cucumber": "Highly perishable",
    "Green Chillies": "Highly perishable",
    "Green Chutney": "Highly perishable",
    "Mushrooms": "Highly perishable",
    "Spinach": "Highly perishable",
    "Tomatoes": "Highly perishable",
    "Spring Onions": "Highly perishable",
    "Cabbage": "Highly perishable",
    "Capsicum": "Highly perishable",
    "Cauliflower": "Highly perishable",
    "Drumsticks": "Highly perishable",
    "Eggplant": "Highly perishable",
    "Green Peas": "Highly perishable",
    "Moong Sprouts": "Highly perishable",
    "Fresh Cream": "Perishable",

    # Perishable
    "Butter": "Perishable",
    "Curd": "Perishable",
    "Eggs": "Perishable",
    "Milk": "Perishable",
    "Paneer": "Perishable",
    "Ghee": "Perishable",
    "Coconut Milk": "Perishable",

    # Semi-perishable
    "Carrots": "Semi-perishable",
    "Garlic": "Semi-perishable",
    "Ginger": "Semi-perishable",
    "Ginger-Garlic Paste": "Perishable",
    "Onion": "Semi-perishable",
    "Onions": "Semi-perishable",
    "Potatoes": "Semi-perishable",

    # Non-perishable
    "Ajwain": "Non-perishable",
    "Baking Powder": "Non-perishable",
    "Basmati Rice": "Non-perishable",
    "Besan": "Non-perishable",
    "Black Pepper": "Non-perishable",
    "Bread Crumbs": "Non-perishable",
    "Broken Wheat": "Non-perishable",
    "Cashews": "Non-perishable",
    "Chaat Masala": "Non-perishable",
    "Chickpeas": "Non-perishable",
    "Chole Masala": "Non-perishable",
    "Cinnamon Powder": "Non-perishable",
    "Cooking Oil": "Non-perishable",
    "Coriander Powder": "Non-perishable",
    "Cumin Powder": "Non-perishable",
    "Cumin Seeds": "Non-perishable",
    "Curry Leaves": "Highly perishable",
    "Dosa Batter": "Perishable",
    "Garam Masala": "Non-perishable",
    "Honey": "Non-perishable",
    "Idli Batter": "Perishable",
    "Kidney Beans": "Non-perishable",
    "Moong Dal": "Non-perishable",
    "Mustard Seeds": "Non-perishable",
    "Oats": "Non-perishable",
    "Olive Oil": "Non-perishable",
    "Peanuts": "Non-perishable",
    "Poha": "Non-perishable",
    "Red Chilli Powder": "Non-perishable",
    "Rice": "Non-perishable",
    "Salt": "Non-perishable",
    "Sambar Powder": "Non-perishable",
    "Semolina": "Non-perishable",
    "Soy Sauce": "Non-perishable",
    "Tamarind": "Non-perishable",
    "Toor Dal": "Non-perishable",
    "Turmeric Powder": "Non-perishable",
    "Water": "Non-perishable",
    "Wheat Flour": "Non-perishable",
}


# Allergen mappings using existing allergy names
food_allergen_names = {
    # Milk
    "Butter": ["Milk"],
    "Curd": ["Milk"],
    "Fresh Cream": ["Milk"],
    "Ghee": ["Milk"],
    "Milk": ["Milk"],
    "Paneer": ["Milk"],

    # Tree nuts
    "Cashews": ["Tree Nuts"],

    # Peanuts
    "Peanuts": ["Peanuts"],

    # Wheat
    "Bread": ["Wheat"],
    "Bread Crumbs": ["Wheat"],
    "Broken Wheat": ["Wheat"],
    "Semolina": ["Wheat"],
    "Wheat Flour": ["Wheat"],

    # Eggs
    "Eggs": ["Eggs"],

    # Soy and wheat (regular soy sauce commonly contains wheat)
    "Soy Sauce": ["Soy", "Wheat"],

    # Mustard
    "Mustard Seeds": ["Mustard"],
}


def seed_food_suggestions():

    connection = get_db_connection()

    try:
        with connection.transaction():

            # Get all unique recipe ingredients
            ingredients = connection.execute("""
                SELECT DISTINCT TRIM(ingredient_name) AS ingredient_name
                FROM recipe_ingredients
                WHERE ingredient_name IS NOT NULL
                  AND TRIM(ingredient_name) <> ''
                ORDER BY ingredient_name
            """).fetchall()

            # Get existing food suggestions
            existing_foods = connection.execute("""
                SELECT food_id, food_name
                FROM food_suggestions
            """).fetchall()

            food_ids = {
                row["food_name"].casefold(): row["food_id"]
                for row in existing_foods
            }

            # Get existing allergen IDs
            allergen_rows = connection.execute("""
                SELECT allergy_id, allergy_name
                FROM allergies
            """).fetchall()

            allergen_ids = {
                row["allergy_name"].casefold(): row["allergy_id"]
                for row in allergen_rows
            }

            inserted_foods = 0
            inserted_mappings = 0

            for ingredient in ingredients:

                food_name = ingredient["ingredient_name"]
                food_key = food_name.casefold()

                # Insert missing food suggestion
                if food_key not in food_ids:

                    category = categories.get(
                        food_name,
                        "Non-perishable"
                    )

                    result = connection.execute("""
                        INSERT INTO food_suggestions
                            (food_name, category)
                        VALUES (%s, %s)
                        RETURNING food_id
                    """, (food_name, category)).fetchone()

                    food_id = result["food_id"]
                    food_ids[food_key] = food_id

                    inserted_foods += 1

                else:
                    food_id = food_ids[food_key]

                # Insert applicable allergen mappings
                allergens = food_allergen_names.get(food_name, [])

                for allergen_name in allergens:

                    allergy_id = allergen_ids.get(
                        allergen_name.casefold()
                    )

                    if allergy_id is None:
                        print(
                            f"Warning: Allergen not found: {allergen_name}"
                        )
                        continue

                    existing_mapping = connection.execute("""
                        SELECT 1
                        FROM food_allergens
                        WHERE food_id = %s
                          AND allergy_id = %s
                    """, (food_id, allergy_id)).fetchone()

                    if not existing_mapping:

                        connection.execute("""
                            INSERT INTO food_allergens
                                (food_id, allergy_id)
                            VALUES (%s, %s)
                        """, (food_id, allergy_id))

                        inserted_mappings += 1

        print("Food suggestion seeding completed!")
        print("New food suggestions inserted:", inserted_foods)
        print("New allergen mappings inserted:", inserted_mappings)

    finally:
        connection.close()


if __name__ == "__main__":
    seed_food_suggestions()
