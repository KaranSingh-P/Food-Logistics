
from database import get_db_connection


def insert_recipe(connection, recipe_data):

    recipe_name = recipe_data["recipe_name"]

    # Check whether the recipe already exists
    existing_recipe = connection.execute("""
        SELECT recipe_id
        FROM recipes
        WHERE recipe_name = %s
    """, (recipe_name,)).fetchone()

    if existing_recipe:
        print(f"{recipe_name} already exists. Skipping.")
        return

    # Insert recipe
    recipe = connection.execute("""
        INSERT INTO recipes (
            recipe_name,
            description,
            meal_type,
            dietary_preferences,
            preparation_time,
            servings,
            calories,
            protein,
            carbohydrates,
            fat
        )
        VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s
        )
        RETURNING recipe_id
    """, (
        recipe_name,
        recipe_data["description"],
        recipe_data["meal_type"],
        recipe_data["dietary_preferences"],
        recipe_data["preparation_time"],
        recipe_data["servings"],
        recipe_data["calories"],
        recipe_data["protein"],
        recipe_data["carbohydrates"],
        recipe_data["fat"]
    )).fetchone()

    recipe_id = recipe["recipe_id"]

    # Insert ingredients
    for name, amount in recipe_data["ingredients"]:
        connection.execute("""
            INSERT INTO recipe_ingredients (
                recipe_id,
                ingredient_name,
                amount
            )
            VALUES (%s, %s, %s)
        """, (recipe_id, name, amount))

    # Insert instructions
    for step, title, description in recipe_data["instructions"]:
        connection.execute("""
            INSERT INTO recipe_instructions (
                recipe_id,
                step_number,
                title,
                description
            )
            VALUES (%s, %s, %s, %s)
        """, (recipe_id, step, title, description))

    print(f"{recipe_name} inserted successfully.")


def seed_recipes():

    connection = get_db_connection()

    try:
        recipes = [
            {
                "recipe_name": "Paneer Butter Masala",
                "description": "A rich and creamy Indian curry made with paneer and a spiced tomato-based gravy.",
                "meal_type": "Dinner",
                "dietary_preferences": ["vegetarian", "high-protein"],
                "preparation_time": 40,
                "servings": 2,
                "calories": 380,
                "protein": 18,
                "carbohydrates": 22,
                "fat": 25,

                "ingredients": [
                    ("Paneer", "200 g"),
                    ("Tomatoes", "3 medium"),
                    ("Onions", "2 medium"),
                    ("Butter", "2 tbsp"),
                    ("Fresh Cream", "3 tbsp"),
                    ("Ginger-Garlic Paste", "1 tbsp"),
                    ("Cashews", "10"),
                    ("Garam Masala", "1 tsp"),
                    ("Red Chilli Powder", "1/2 tsp"),
                    ("Salt", "To taste")
                ],

                "instructions": [
                    (1, "Prepare the ingredients",
                     "Chop the onions and tomatoes. Cut the paneer into cubes."),

                    (2, "Prepare the cashew paste",
                     "Soak the cashews in warm water for 10 minutes and blend them into a smooth paste."),

                    (3, "Cook the base gravy",
                     "Heat butter in a pan. Add onions and cook until soft. Add ginger-garlic paste and tomatoes."),

                    (4, "Prepare the curry",
                     "Add red chilli powder, garam masala, salt, and cashew paste. Mix well and cook for a few minutes."),

                    (5, "Add paneer",
                     "Add paneer cubes and fresh cream. Stir gently and simmer for 5 minutes."),

                    (6, "Serve",
                     "Garnish with fresh cream if desired. Serve hot with naan, roti, or rice.")
                ]
            },

            {
                "recipe_name": "Vegetable Poha",
                "description": "A light Indian breakfast made with flattened rice, vegetables, peanuts, and mild spices.",
                "meal_type": "Breakfast",
                "dietary_preferences": ["vegetarian", "vegan"],
                "preparation_time": 20,
                "servings": 2,
                "calories": 250,
                "protein": 6,
                "carbohydrates": 42,
                "fat": 7,

                "ingredients": [
                    ("Poha", "2 cups"),
                    ("Onions", "1 medium"),
                    ("Potatoes", "1 small"),
                    ("Green Peas", "1/4 cup"),
                    ("Peanuts", "2 tbsp"),
                    ("Mustard Seeds", "1/2 tsp"),
                    ("Turmeric Powder", "1/4 tsp"),
                    ("Lemon Juice", "1 tbsp"),
                    ("Coriander Leaves", "2 tbsp"),
                    ("Salt", "To taste")
                ],

                "instructions": [
                    (1, "Prepare the poha",
                     "Rinse the poha gently under water, drain, and let it rest for a few minutes."),

                    (2, "Prepare the vegetables",
                     "Chop the onion and potato. Keep the green peas ready."),

                    (3, "Prepare the tempering",
                     "Heat oil in a pan. Add mustard seeds and peanuts. Cook until the peanuts are lightly roasted."),

                    (4, "Cook the vegetables",
                     "Add onions, potatoes, and peas. Add turmeric and salt, then cook until the vegetables soften."),

                    (5, "Add the poha",
                     "Add the soaked poha and mix gently. Cook for a few minutes."),

                    (6, "Finish and serve",
                     "Add lemon juice and coriander leaves. Mix and serve warm.")
                ]
            },

            {
                "recipe_name": "Chickpea Salad",
                "description": "A refreshing and protein-rich salad made with chickpeas, fresh vegetables, and lemon dressing.",
                "meal_type": "Lunch",
                "dietary_preferences": ["vegetarian", "vegan", "high-protein"],
                "preparation_time": 15,
                "servings": 2,
                "calories": 280,
                "protein": 12,
                "carbohydrates": 38,
                "fat": 8,

                "ingredients": [
                    ("Chickpeas", "1 cup"),
                    ("Cucumber", "1 medium"),
                    ("Tomatoes", "1 medium"),
                    ("Onion", "1 small"),
                    ("Lemon Juice", "2 tbsp"),
                    ("Olive Oil", "1 tbsp"),
                    ("Black Pepper", "1/2 tsp"),
                    ("Coriander Leaves", "2 tbsp"),
                    ("Salt", "To taste")
                ],

                "instructions": [
                    (1, "Prepare the chickpeas",
                     "If using dried chickpeas, soak and cook them until tender. Drain and cool."),

                    (2, "Chop the vegetables",
                     "Dice the cucumber, tomatoes, and onion into small pieces."),

                    (3, "Prepare the dressing",
                     "Mix lemon juice, olive oil, black pepper, and salt in a small bowl."),

                    (4, "Combine the ingredients",
                     "Add chickpeas and chopped vegetables to a large bowl."),

                    (5, "Add the dressing",
                     "Pour the dressing over the salad and toss gently."),

                    (6, "Serve",
                     "Garnish with coriander leaves and serve fresh.")
                ]
            },

            {
                "recipe_name": "Vegetable Sandwich",
                "description": "A simple and filling sandwich made with fresh vegetables, butter, and seasoned bread.",
                "meal_type": "Snack",
                "dietary_preferences": ["vegetarian"],
                "preparation_time": 15,
                "servings": 2,
                "calories": 290,
                "protein": 9,
                "carbohydrates": 36,
                "fat": 12,

                "ingredients": [
                    ("Bread", "4 slices"),
                    ("Cucumber", "1/2 medium"),
                    ("Tomatoes", "1 medium"),
                    ("Onion", "1 small"),
                    ("Butter", "2 tbsp"),
                    ("Green Chutney", "2 tbsp"),
                    ("Black Pepper", "1/4 tsp"),
                    ("Salt", "To taste")
                ],

                "instructions": [
                    (1, "Prepare the vegetables",
                     "Wash and thinly slice the cucumber, tomatoes, and onion."),

                    (2, "Prepare the bread",
                     "Spread butter evenly on one side of each bread slice."),

                    (3, "Add the chutney",
                     "Spread green chutney over the unbuttered side of two bread slices."),

                    (4, "Assemble the sandwich",
                     "Arrange the sliced vegetables over the chutney. Season with salt and black pepper."),

                    (5, "Close the sandwich",
                     "Cover with the remaining bread slices, keeping the buttered sides facing outward."),

                    (6, "Toast and serve",
                     "Toast the sandwiches on a pan until golden brown. Cut and serve.")
                ]
            },

            {
                "recipe_name": "Banana Oat Pancakes",
                "description": "Soft and naturally sweet pancakes made with bananas, oats, and milk.",
                "meal_type": "Breakfast",
                "dietary_preferences": ["vegetarian"],
                "preparation_time": 20,
                "servings": 2,
                "calories": 310,
                "protein": 11,
                "carbohydrates": 48,
                "fat": 9,

                "ingredients": [
                    ("Bananas", "2 medium"),
                    ("Oats", "1 cup"),
                    ("Milk", "1/2 cup"),
                    ("Eggs", "2"),
                    ("Baking Powder", "1/2 tsp"),
                    ("Cinnamon Powder", "1/4 tsp"),
                    ("Butter", "1 tbsp"),
                    ("Honey", "1 tbsp")
                ],

                "instructions": [
                    (1, "Prepare the banana",
                     "Peel the bananas and mash them in a bowl until smooth."),

                    (2, "Prepare the oats",
                     "Grind the oats into a coarse flour using a blender."),

                    (3, "Make the batter",
                     "Mix the mashed bananas, oat flour, milk, eggs, baking powder, and cinnamon until combined."),

                    (4, "Heat the pan",
                     "Heat a non-stick pan over medium heat and lightly grease it with butter."),

                    (5, "Cook the pancakes",
                     "Pour small portions of batter onto the pan. Cook until bubbles appear, then flip and cook the other side."),

                    (6, "Serve",
                     "Stack the pancakes and drizzle with honey before serving.")
                ]
            }


        ]

        with connection.transaction():
            for recipe_data in recipes:
                insert_recipe(connection, recipe_data)

    finally:
        connection.close()


if __name__ == "__main__":
    seed_recipes()
