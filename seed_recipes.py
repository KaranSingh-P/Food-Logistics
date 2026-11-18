
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
            },

            {
                "recipe_name": "Masala Dosa",
                "description": "A crispy South Indian crepe filled with spiced potato masala and served with chutney.",
                "meal_type": "Breakfast",
                "dietary_preferences": ["vegetarian", "vegan"],
                "preparation_time": 30,
                "servings": 2,
                "calories": 320,
                "protein": 7,
                "carbohydrates": 52,
                "fat": 9,
                "ingredients": [
                    ("Dosa Batter", "2 cups"),
                    ("Potatoes", "2 medium"),
                    ("Onions", "1 medium"),
                    ("Green Chillies", "2"),
                    ("Mustard Seeds", "1/2 tsp"),
                    ("Turmeric Powder", "1/4 tsp"),
                    ("Curry Leaves", "8"),
                    ("Cooking Oil", "2 tbsp"),
                    ("Salt", "To taste")
                ],
                "instructions": [
                    (1, "Prepare the potato masala", "Boil and mash the potatoes. Chop the onions and green chillies."),
                    (2, "Prepare the tempering", "Heat oil in a pan. Add mustard seeds, curry leaves, onions, green chillies, and turmeric."),
                    (3, "Cook the filling", "Add mashed potatoes and salt. Mix well and cook for a few minutes."),
                    (4, "Prepare the dosa", "Spread dosa batter thinly on a hot greased pan. Cook until crispy."),
                    (5, "Add the filling", "Place potato masala in the centre and fold the dosa."),
                    (6, "Serve", "Serve hot with coconut chutney or sambar.")
                ]
            },

            {
                "recipe_name": "Vegetable Upma",
                "description": "A savoury South Indian breakfast prepared with roasted semolina and mixed vegetables.",
                "meal_type": "Breakfast",
                "dietary_preferences": ["vegetarian"],
                "preparation_time": 25,
                "servings": 2,
                "calories": 270,
                "protein": 7,
                "carbohydrates": 42,
                "fat": 8,
                "ingredients": [
                    ("Semolina", "1 cup"),
                    ("Onions", "1 medium"),
                    ("Carrots", "1 small"),
                    ("Green Peas", "1/4 cup"),
                    ("Green Chillies", "2"),
                    ("Mustard Seeds", "1/2 tsp"),
                    ("Curry Leaves", "8"),
                    ("Cooking Oil", "1 tbsp"),
                    ("Water", "2 cups"),
                    ("Salt", "To taste")
                ],
                "instructions": [
                    (1, "Roast the semolina", "Dry roast semolina in a pan until lightly fragrant. Keep aside."),
                    (2, "Prepare the vegetables", "Chop the onions, carrots, and green chillies."),
                    (3, "Prepare the tempering", "Heat oil and add mustard seeds, curry leaves, onions, and green chillies."),
                    (4, "Cook the vegetables", "Add carrots, peas, and salt. Cook until slightly tender."),
                    (5, "Prepare the upma", "Add water and bring to a boil. Gradually add semolina while stirring."),
                    (6, "Serve", "Cook until the mixture thickens and serve warm.")
                ]
            },

            {
                "recipe_name": "Idli with Sambar",
                "description": "Soft steamed rice cakes served with a nutritious lentil and vegetable curry.",
                "meal_type": "Breakfast",
                "dietary_preferences": ["vegetarian", "vegan"],
                "preparation_time": 35,
                "servings": 2,
                "calories": 290,
                "protein": 10,
                "carbohydrates": 55,
                "fat": 3,
                "ingredients": [
                    ("Idli Batter", "2 cups"),
                    ("Toor Dal", "1/2 cup"),
                    ("Tomatoes", "1 medium"),
                    ("Onions", "1 small"),
                    ("Carrots", "1 small"),
                    ("Drumsticks", "1"),
                    ("Sambar Powder", "1 tbsp"),
                    ("Tamarind", "1 tbsp"),
                    ("Mustard Seeds", "1/2 tsp"),
                    ("Salt", "To taste")
                ],
                "instructions": [
                    (1, "Prepare the dal", "Wash and pressure-cook toor dal until soft. Mash it well."),
                    (2, "Prepare the vegetables", "Chop the tomatoes, onion, carrot, and drumstick."),
                    (3, "Cook the sambar", "Boil the vegetables with tamarind water, sambar powder, and salt."),
                    (4, "Finish the sambar", "Add mashed dal and simmer until the flavours combine."),
                    (5, "Steam the idlis", "Pour idli batter into greased idli moulds and steam for 10–12 minutes."),
                    (6, "Serve", "Serve the hot idlis with sambar.")
                ]
            },

            {
                "recipe_name": "Besan Chilla",
                "description": "A savoury Indian pancake made with gram flour, onions, tomatoes, and spices.",
                "meal_type": "Breakfast",
                "dietary_preferences": ["vegetarian", "vegan", "high-protein"],
                "preparation_time": 20,
                "servings": 2,
                "calories": 240,
                "protein": 11,
                "carbohydrates": 30,
                "fat": 8,
                "ingredients": [
                    ("Besan", "1 cup"),
                    ("Onions", "1 small"),
                    ("Tomatoes", "1 small"),
                    ("Green Chillies", "1"),
                    ("Coriander Leaves", "2 tbsp"),
                    ("Turmeric Powder", "1/4 tsp"),
                    ("Cumin Seeds", "1/2 tsp"),
                    ("Water", "3/4 cup"),
                    ("Cooking Oil", "1 tbsp"),
                    ("Salt", "To taste")
                ],
                "instructions": [
                    (1, "Prepare the vegetables", "Finely chop the onions, tomatoes, green chillies, and coriander leaves."),
                    (2, "Prepare the batter", "Mix besan, turmeric, cumin seeds, salt, and water into a smooth batter."),
                    (3, "Add vegetables", "Mix the chopped vegetables and coriander leaves into the batter."),
                    (4, "Cook the chilla", "Pour a portion of batter onto a greased hot pan and spread evenly."),
                    (5, "Flip and cook", "Cook both sides until golden brown."),
                    (6, "Serve", "Serve hot with green chutney or curd.")
                ]
            },

            {
                "recipe_name": "Vegetable Paratha",
                "description": "A filling Indian flatbread stuffed with seasoned and mashed vegetables.",
                "meal_type": "Breakfast",
                "dietary_preferences": ["vegetarian"],
                "preparation_time": 30,
                "servings": 2,
                "calories": 310,
                "protein": 8,
                "carbohydrates": 45,
                "fat": 11,
                "ingredients": [
                    ("Wheat Flour", "2 cups"),
                    ("Potatoes", "1 medium"),
                    ("Carrots", "1 small"),
                    ("Green Peas", "1/4 cup"),
                    ("Green Chillies", "1"),
                    ("Coriander Leaves", "2 tbsp"),
                    ("Garam Masala", "1/2 tsp"),
                    ("Cooking Oil", "2 tbsp"),
                    ("Water", "As required"),
                    ("Salt", "To taste")
                ],
                "instructions": [
                    (1, "Prepare the dough", "Mix wheat flour, water, and salt. Knead into a soft dough."),
                    (2, "Prepare the filling", "Boil and mash potatoes and peas. Add grated carrots, chillies, coriander, and garam masala."),
                    (3, "Stuff the parathas", "Divide the dough into balls, flatten, add filling, and seal."),
                    (4, "Roll the parathas", "Gently roll each stuffed ball into a flatbread."),
                    (5, "Cook", "Cook on a hot pan using oil until both sides are golden."),
                    (6, "Serve", "Serve warm with curd or pickle.")
                ]
            },

            {
                "recipe_name": "Sprouts Salad",
                "description": "A refreshing and protein-rich breakfast salad made with sprouted legumes and fresh vegetables.",
                "meal_type": "Breakfast",
                "dietary_preferences": ["vegetarian", "vegan", "high-protein"],
                "preparation_time": 15,
                "servings": 2,
                "calories": 190,
                "protein": 12,
                "carbohydrates": 28,
                "fat": 4,
                "ingredients": [
                    ("Moong Sprouts", "1 cup"),
                    ("Onions", "1 small"),
                    ("Tomatoes", "1 medium"),
                    ("Cucumber", "1/2 medium"),
                    ("Lemon Juice", "1 tbsp"),
                    ("Coriander Leaves", "2 tbsp"),
                    ("Black Pepper", "1/4 tsp"),
                    ("Salt", "To taste")
                ],
                "instructions": [
                    (1, "Prepare the sprouts", "Wash the moong sprouts and steam them lightly if desired."),
                    (2, "Chop the vegetables", "Finely chop onions, tomatoes, and cucumber."),
                    (3, "Combine ingredients", "Add sprouts and chopped vegetables to a bowl."),
                    (4, "Season", "Add lemon juice, black pepper, and salt."),
                    (5, "Mix", "Toss everything until evenly combined."),
                    (6, "Serve", "Garnish with coriander leaves and serve fresh.")
                ]
            },

            {
                "recipe_name": "Rajma Chawal",
                "description": "A classic North Indian meal consisting of kidney beans cooked in a spiced tomato gravy with rice.",
                "meal_type": "Lunch",
                "dietary_preferences": ["vegetarian", "vegan", "high-protein"],
                "preparation_time": 45,
                "servings": 2,
                "calories": 420,
                "protein": 15,
                "carbohydrates": 68,
                "fat": 10,
                "ingredients": [
                    ("Kidney Beans", "1 cup"),
                    ("Rice", "1 cup"),
                    ("Onions", "1 medium"),
                    ("Tomatoes", "2 medium"),
                    ("Ginger-Garlic Paste", "1 tbsp"),
                    ("Cumin Seeds", "1/2 tsp"),
                    ("Garam Masala", "1 tsp"),
                    ("Red Chilli Powder", "1/2 tsp"),
                    ("Cooking Oil", "1 tbsp"),
                    ("Salt", "To taste")
                ],
                "instructions": [
                    (1, "Prepare the kidney beans", "Soak kidney beans overnight and pressure-cook until soft."),
                    (2, "Prepare the gravy", "Heat oil, add cumin seeds and chopped onions, and cook until golden."),
                    (3, "Add spices", "Add ginger-garlic paste, tomatoes, chilli powder, and garam masala."),
                    (4, "Cook the rajma", "Add cooked kidney beans and some cooking water. Simmer until thick."),
                    (5, "Prepare the rice", "Wash and cook rice until soft and fluffy."),
                    (6, "Serve", "Serve hot rajma with steamed rice.")
                ]
            },

            {
                "recipe_name": "Vegetable Pulao",
                "description": "A fragrant one-pot rice dish prepared with mixed vegetables and aromatic Indian spices.",
                "meal_type": "Lunch",
                "dietary_preferences": ["vegetarian", "vegan"],
                "preparation_time": 30,
                "servings": 2,
                "calories": 350,
                "protein": 8,
                "carbohydrates": 58,
                "fat": 10,
                "ingredients": [
                    ("Basmati Rice", "1 cup"),
                    ("Carrots", "1 small"),
                    ("Green Peas", "1/4 cup"),
                    ("Potatoes", "1 small"),
                    ("Onions", "1 medium"),
                    ("Ginger-Garlic Paste", "1 tsp"),
                    ("Cumin Seeds", "1/2 tsp"),
                    ("Garam Masala", "1/2 tsp"),
                    ("Cooking Oil", "1 tbsp"),
                    ("Salt", "To taste")
                ],
                "instructions": [
                    (1, "Prepare the rice", "Wash and soak basmati rice for 15 minutes."),
                    (2, "Prepare the vegetables", "Chop carrots, potatoes, and onions into small pieces."),
                    (3, "Prepare the base", "Heat oil and add cumin seeds, onions, and ginger-garlic paste."),
                    (4, "Cook the vegetables", "Add carrots, peas, potatoes, garam masala, and salt."),
                    (5, "Cook the pulao", "Add drained rice and water. Cover and cook until the rice is tender."),
                    (6, "Serve", "Fluff gently and serve hot with curd or raita.")
                ]
            },

            {
                "recipe_name": "Palak Paneer",
                "description": "A nutritious North Indian curry made with paneer cubes in a smooth spinach gravy.",
                "meal_type": "Lunch",
                "dietary_preferences": ["vegetarian", "high-protein"],
                "preparation_time": 35,
                "servings": 2,
                "calories": 330,
                "protein": 19,
                "carbohydrates": 16,
                "fat": 21,
                "ingredients": [
                    ("Paneer", "200 g"),
                    ("Spinach", "250 g"),
                    ("Onions", "1 medium"),
                    ("Tomatoes", "1 medium"),
                    ("Ginger-Garlic Paste", "1 tbsp"),
                    ("Fresh Cream", "2 tbsp"),
                    ("Cumin Seeds", "1/2 tsp"),
                    ("Garam Masala", "1/2 tsp"),
                    ("Cooking Oil", "1 tbsp"),
                    ("Salt", "To taste")
                ],
                "instructions": [
                    (1, "Prepare the spinach", "Wash spinach and blanch it in boiling water for 2 minutes."),
                    (2, "Make the puree", "Cool the spinach and blend into a smooth paste."),
                    (3, "Prepare the gravy", "Heat oil, add cumin seeds and onions, then cook with ginger-garlic paste and tomatoes."),
                    (4, "Add spinach", "Add the spinach puree, garam masala, and salt. Simmer for a few minutes."),
                    (5, "Add paneer", "Add paneer cubes and fresh cream. Cook gently for 5 minutes."),
                    (6, "Serve", "Serve hot with roti or rice.")
                ]
            },

            {
                "recipe_name": "Chole Masala",
                "description": "A popular North Indian chickpea curry cooked in a rich and tangy onion-tomato gravy.",
                "meal_type": "Lunch",
                "dietary_preferences": ["vegetarian", "vegan", "high-protein"],
                "preparation_time": 40,
                "servings": 2,
                "calories": 360,
                "protein": 15,
                "carbohydrates": 48,
                "fat": 12,
                "ingredients": [
                    ("Chickpeas", "1 cup"),
                    ("Onions", "1 medium"),
                    ("Tomatoes", "2 medium"),
                    ("Ginger-Garlic Paste", "1 tbsp"),
                    ("Chole Masala", "1 tbsp"),
                    ("Cumin Seeds", "1/2 tsp"),
                    ("Red Chilli Powder", "1/2 tsp"),
                    ("Coriander Leaves", "2 tbsp"),
                    ("Cooking Oil", "1 tbsp"),
                    ("Salt", "To taste")
                ],
                "instructions": [
                    (1, "Prepare the chickpeas", "Soak chickpeas overnight and pressure-cook until tender."),
                    (2, "Prepare the base", "Heat oil and add cumin seeds and chopped onions. Cook until golden."),
                    (3, "Add tomatoes", "Add ginger-garlic paste and tomatoes. Cook until soft."),
                    (4, "Add spices", "Add chole masala, chilli powder, and salt."),
                    (5, "Cook the curry", "Add chickpeas and cooking water. Simmer until the gravy thickens."),
                    (6, "Serve", "Garnish with coriander leaves and serve with rice or roti.")
                ]
            },

            {
                "recipe_name": "Vegetable Fried Rice",
                "description": "A quick rice dish tossed with mixed vegetables, soy sauce, and mild seasonings.",
                "meal_type": "Lunch",
                "dietary_preferences": ["vegetarian", "vegan"],
                "preparation_time": 20,
                "servings": 2,
                "calories": 340,
                "protein": 8,
                "carbohydrates": 57,
                "fat": 9,
                "ingredients": [
                    ("Rice", "2 cups cooked"),
                    ("Carrots", "1 small"),
                    ("Cabbage", "1 cup"),
                    ("Capsicum", "1 small"),
                    ("Spring Onions", "2 tbsp"),
                    ("Garlic", "3 cloves"),
                    ("Soy Sauce", "1 tbsp"),
                    ("Black Pepper", "1/2 tsp"),
                    ("Cooking Oil", "1 tbsp"),
                    ("Salt", "To taste")
                ],
                "instructions": [
                    (1, "Prepare the rice", "Cook rice and allow it to cool completely."),
                    (2, "Chop the vegetables", "Finely chop carrots, cabbage, capsicum, spring onions, and garlic."),
                    (3, "Cook the vegetables", "Heat oil in a wok and stir-fry garlic and vegetables over high heat."),
                    (4, "Add rice", "Add cooked rice and toss gently."),
                    (5, "Season", "Add soy sauce, black pepper, and salt. Mix well."),
                    (6, "Serve", "Garnish with spring onions and serve hot.")
                ]
            },

            {
                "recipe_name": "Vegetable Khichdi",
                "description": "A comforting one-pot meal made with rice, lentils, and vegetables.",
                "meal_type": "Lunch",
                "dietary_preferences": ["vegetarian", "vegan"],
                "preparation_time": 30,
                "servings": 2,
                "calories": 310,
                "protein": 11,
                "carbohydrates": 52,
                "fat": 7,
                "ingredients": [
                    ("Rice", "1/2 cup"),
                    ("Moong Dal", "1/2 cup"),
                    ("Carrots", "1 small"),
                    ("Green Peas", "1/4 cup"),
                    ("Potatoes", "1 small"),
                    ("Turmeric Powder", "1/2 tsp"),
                    ("Cumin Seeds", "1/2 tsp"),
                    ("Ginger", "1 tsp grated"),
                    ("Ghee", "1 tbsp"),
                    ("Salt", "To taste")
                ],
                "instructions": [
                    (1, "Wash the grains", "Wash rice and moong dal thoroughly and soak for 10 minutes."),
                    (2, "Prepare the vegetables", "Chop carrots and potatoes into small pieces."),
                    (3, "Prepare the tempering", "Heat ghee and add cumin seeds and grated ginger."),
                    (4, "Combine ingredients", "Add rice, dal, vegetables, turmeric, salt, and water."),
                    (5, "Cook", "Pressure-cook for 3–4 whistles until everything is soft."),
                    (6, "Serve", "Mix gently and serve warm with curd or pickle.")
                ]
            },

            {
                "recipe_name": "Matar Paneer",
                "description": "A North Indian curry combining paneer cubes and green peas in a spiced tomato gravy.",
                "meal_type": "Lunch",
                "dietary_preferences": ["vegetarian", "high-protein"],
                "preparation_time": 35,
                "servings": 2,
                "calories": 350,
                "protein": 19,
                "carbohydrates": 22,
                "fat": 20,
                "ingredients": [
                    ("Paneer", "200 g"),
                    ("Green Peas", "1/2 cup"),
                    ("Onions", "1 medium"),
                    ("Tomatoes", "2 medium"),
                    ("Ginger-Garlic Paste", "1 tbsp"),
                    ("Cumin Seeds", "1/2 tsp"),
                    ("Coriander Powder", "1 tsp"),
                    ("Garam Masala", "1/2 tsp"),
                    ("Cooking Oil", "1 tbsp"),
                    ("Salt", "To taste")
                ],
                "instructions": [
                    (1, "Prepare the ingredients", "Cut paneer into cubes and chop the onions and tomatoes."),
                    (2, "Prepare the gravy", "Heat oil, add cumin seeds and onions, then cook until golden."),
                    (3, "Add spices", "Add ginger-garlic paste, tomatoes, coriander powder, and garam masala."),
                    (4, "Cook the peas", "Add green peas and a little water. Cook until tender."),
                    (5, "Add paneer", "Add paneer cubes and simmer for 5 minutes."),
                    (6, "Serve", "Serve hot with chapati, naan, or rice.")
                ]
            },

            {
                "recipe_name": "Dal Tadka",
                "description": "A comforting Indian lentil curry finished with a fragrant tempering of spices and garlic.",
                "meal_type": "Dinner",
                "dietary_preferences": ["vegetarian", "vegan", "high-protein"],
                "preparation_time": 30,
                "servings": 2,
                "calories": 280,
                "protein": 14,
                "carbohydrates": 38,
                "fat": 8,
                "ingredients": [
                    ("Toor Dal", "1/2 cup"),
                    ("Moong Dal", "1/4 cup"),
                    ("Tomatoes", "1 medium"),
                    ("Onions", "1 small"),
                    ("Garlic", "4 cloves"),
                    ("Cumin Seeds", "1/2 tsp"),
                    ("Turmeric Powder", "1/4 tsp"),
                    ("Red Chilli Powder", "1/2 tsp"),
                    ("Ghee", "1 tbsp"),
                    ("Salt", "To taste")
                ],
                "instructions": [
                    (1, "Wash the lentils", "Wash toor dal and moong dal thoroughly."),
                    (2, "Cook the lentils", "Pressure-cook the lentils with turmeric and water until soft."),
                    (3, "Prepare the tempering", "Heat ghee in a pan and add cumin seeds, chopped garlic, and onions."),
                    (4, "Add tomatoes", "Add tomatoes, red chilli powder, and salt. Cook until soft."),
                    (5, "Combine", "Add cooked lentils and simmer for 5–7 minutes."),
                    (6, "Serve", "Serve hot with rice or chapati.")
                ]
            },

            {
                "recipe_name": "Aloo Gobi",
                "description": "A traditional Indian dry curry made with potatoes, cauliflower, and aromatic spices.",
                "meal_type": "Dinner",
                "dietary_preferences": ["vegetarian", "vegan"],
                "preparation_time": 30,
                "servings": 2,
                "calories": 230,
                "protein": 6,
                "carbohydrates": 32,
                "fat": 9,
                "ingredients": [
                    ("Potatoes", "2 medium"),
                    ("Cauliflower", "2 cups"),
                    ("Onions", "1 medium"),
                    ("Tomatoes", "1 medium"),
                    ("Ginger", "1 tsp grated"),
                    ("Turmeric Powder", "1/2 tsp"),
                    ("Cumin Seeds", "1/2 tsp"),
                    ("Coriander Powder", "1 tsp"),
                    ("Cooking Oil", "1 tbsp"),
                    ("Salt", "To taste")
                ],
                "instructions": [
                    (1, "Prepare the vegetables", "Cut potatoes into cubes and cauliflower into small florets."),
                    (2, "Prepare the base", "Heat oil, add cumin seeds and onions, and cook until soft."),
                    (3, "Add spices", "Add ginger, turmeric, coriander powder, and chopped tomatoes."),
                    (4, "Cook the vegetables", "Add potatoes, cauliflower, and salt. Mix well."),
                    (5, "Simmer", "Cover and cook on low heat until the vegetables are tender."),
                    (6, "Serve", "Garnish with coriander leaves and serve with chapati.")
                ]
            },

            {
                "recipe_name": "Vegetable Korma",
                "description": "A creamy mixed vegetable curry prepared with a mildly spiced cashew and coconut gravy.",
                "meal_type": "Dinner",
                "dietary_preferences": ["vegetarian"],
                "preparation_time": 40,
                "servings": 2,
                "calories": 340,
                "protein": 9,
                "carbohydrates": 30,
                "fat": 21,
                "ingredients": [
                    ("Carrots", "1 medium"),
                    ("Potatoes", "1 medium"),
                    ("Green Peas", "1/4 cup"),
                    ("Cauliflower", "1 cup"),
                    ("Onions", "1 medium"),
                    ("Cashews", "10"),
                    ("Coconut Milk", "1/2 cup"),
                    ("Ginger-Garlic Paste", "1 tsp"),
                    ("Garam Masala", "1/2 tsp"),
                    ("Cooking Oil", "1 tbsp"),
                    ("Salt", "To taste")
                ],
                "instructions": [
                    (1, "Prepare the vegetables", "Chop carrots, potatoes, and cauliflower into small pieces."),
                    (2, "Prepare the cashew paste", "Soak cashews in warm water and blend into a smooth paste."),
                    (3, "Cook the base", "Heat oil and cook chopped onions with ginger-garlic paste."),
                    (4, "Cook the vegetables", "Add the vegetables, peas, garam masala, and salt. Cook until tender."),
                    (5, "Prepare the gravy", "Add cashew paste and coconut milk. Simmer until creamy."),
                    (6, "Serve", "Serve hot with naan, chapati, or rice.")
                ]
            },

            {
                "recipe_name": "Baingan Bharta",
                "description": "A smoky Indian eggplant preparation mashed and cooked with onions, tomatoes, and spices.",
                "meal_type": "Dinner",
                "dietary_preferences": ["vegetarian", "vegan"],
                "preparation_time": 35,
                "servings": 2,
                "calories": 210,
                "protein": 5,
                "carbohydrates": 24,
                "fat": 11,
                "ingredients": [
                    ("Eggplant", "1 large"),
                    ("Onions", "1 medium"),
                    ("Tomatoes", "2 medium"),
                    ("Green Chillies", "2"),
                    ("Garlic", "4 cloves"),
                    ("Ginger", "1 tsp grated"),
                    ("Cumin Seeds", "1/2 tsp"),
                    ("Red Chilli Powder", "1/2 tsp"),
                    ("Cooking Oil", "1 tbsp"),
                    ("Salt", "To taste")
                ],
                "instructions": [
                    (1, "Roast the eggplant", "Roast the eggplant over a flame or in an oven until the skin is charred and the inside is soft."),
                    (2, "Prepare the eggplant", "Allow it to cool, remove the skin, and mash the flesh."),
                    (3, "Prepare the base", "Heat oil and add cumin seeds, garlic, ginger, and onions."),
                    (4, "Add tomatoes", "Add tomatoes, green chillies, red chilli powder, and salt."),
                    (5, "Combine", "Add mashed eggplant and cook for 5–7 minutes."),
                    (6, "Serve", "Garnish with coriander leaves and serve with roti.")
                ]
            },

            {
                "recipe_name": "Mushroom Masala",
                "description": "A flavourful mushroom curry cooked in an onion-tomato gravy with Indian spices.",
                "meal_type": "Dinner",
                "dietary_preferences": ["vegetarian", "vegan"],
                "preparation_time": 30,
                "servings": 2,
                "calories": 240,
                "protein": 9,
                "carbohydrates": 18,
                "fat": 14,
                "ingredients": [
                    ("Mushrooms", "200 g"),
                    ("Onions", "1 medium"),
                    ("Tomatoes", "2 medium"),
                    ("Ginger-Garlic Paste", "1 tbsp"),
                    ("Cumin Seeds", "1/2 tsp"),
                    ("Coriander Powder", "1 tsp"),
                    ("Turmeric Powder", "1/4 tsp"),
                    ("Garam Masala", "1/2 tsp"),
                    ("Cooking Oil", "1 tbsp"),
                    ("Salt", "To taste")
                ],
                "instructions": [
                    (1, "Prepare the mushrooms", "Wash and slice the mushrooms."),
                    (2, "Prepare the gravy", "Heat oil and add cumin seeds and onions. Cook until golden."),
                    (3, "Add aromatics", "Add ginger-garlic paste and chopped tomatoes."),
                    (4, "Season", "Add coriander powder, turmeric, garam masala, and salt."),
                    (5, "Cook the mushrooms", "Add mushrooms and cook until tender and the gravy thickens."),
                    (6, "Serve", "Garnish with coriander leaves and serve with rice or roti.")
                ]
            },

            {
                "recipe_name": "Vegetable Jalfrezi",
                "description": "A colourful Indian stir-fried vegetable curry with capsicum, carrots, onions, and tangy tomato sauce.",
                "meal_type": "Dinner",
                "dietary_preferences": ["vegetarian", "vegan"],
                "preparation_time": 25,
                "servings": 2,
                "calories": 220,
                "protein": 6,
                "carbohydrates": 28,
                "fat": 10,
                "ingredients": [
                    ("Capsicum", "1 medium"),
                    ("Carrots", "1 medium"),
                    ("Onions", "1 medium"),
                    ("Tomatoes", "2 medium"),
                    ("Cauliflower", "1 cup"),
                    ("Ginger-Garlic Paste", "1 tsp"),
                    ("Cumin Seeds", "1/2 tsp"),
                    ("Red Chilli Powder", "1/2 tsp"),
                    ("Cooking Oil", "1 tbsp"),
                    ("Salt", "To taste")
                ],
                "instructions": [
                    (1, "Prepare the vegetables", "Slice capsicum, carrots, onions, tomatoes, and cauliflower."),
                    (2, "Prepare the base", "Heat oil and add cumin seeds, onions, and ginger-garlic paste."),
                    (3, "Add tomatoes", "Add chopped tomatoes, chilli powder, and salt. Cook until soft."),
                    (4, "Cook the vegetables", "Add carrots and cauliflower and cook until slightly tender."),
                    (5, "Finish the curry", "Add capsicum and cook briefly while keeping the vegetables slightly crisp."),
                    (6, "Serve", "Serve hot with chapati, naan, or rice.")
                ]
            },

            {
                "recipe_name": "Vegetable Dalia",
                "description": "A wholesome and light Indian meal made with broken wheat and mixed vegetables.",
                "meal_type": "Dinner",
                "dietary_preferences": ["vegetarian", "vegan", "high-protein"],
                "preparation_time": 30,
                "servings": 2,
                "calories": 260,
                "protein": 9,
                "carbohydrates": 45,
                "fat": 6,
                "ingredients": [
                    ("Broken Wheat", "1 cup"),
                    ("Carrots", "1 small"),
                    ("Green Peas", "1/4 cup"),
                    ("Onions", "1 small"),
                    ("Tomatoes", "1 small"),
                    ("Cumin Seeds", "1/2 tsp"),
                    ("Turmeric Powder", "1/4 tsp"),
                    ("Ginger", "1 tsp grated"),
                    ("Cooking Oil", "1 tbsp"),
                    ("Salt", "To taste")
                ],
                "instructions": [
                    (1, "Prepare the dalia", "Wash broken wheat and drain the water."),
                    (2, "Prepare the vegetables", "Chop carrots, onions, and tomatoes."),
                    (3, "Prepare the tempering", "Heat oil and add cumin seeds, ginger, and onions."),
                    (4, "Add vegetables", "Add carrots, peas, tomatoes, turmeric, and salt."),
                    (5, "Cook", "Add broken wheat and water. Pressure-cook until soft."),
                    (6, "Serve", "Mix well and serve warm.")
                ]
            },

            {
                "recipe_name": "Aloo Tikki",
                "description": "Crispy shallow-fried potato patties seasoned with Indian spices and fresh coriander.",
                "meal_type": "Snack",
                "dietary_preferences": ["vegetarian", "vegan"],
                "preparation_time": 25,
                "servings": 2,
                "calories": 260,
                "protein": 5,
                "carbohydrates": 38,
                "fat": 10,
                "ingredients": [
                    ("Potatoes", "3 medium"),
                    ("Green Chillies", "1"),
                    ("Coriander Leaves", "2 tbsp"),
                    ("Bread Crumbs", "1/4 cup"),
                    ("Cumin Powder", "1/2 tsp"),
                    ("Red Chilli Powder", "1/4 tsp"),
                    ("Garam Masala", "1/4 tsp"),
                    ("Cooking Oil", "2 tbsp"),
                    ("Salt", "To taste")
                ],
                "instructions": [
                    (1, "Prepare the potatoes", "Boil, peel, and mash the potatoes."),
                    (2, "Prepare the mixture", "Add green chillies, coriander, breadcrumbs, and spices."),
                    (3, "Shape the patties", "Mix well and shape into small flat patties."),
                    (4, "Heat the pan", "Heat oil in a shallow frying pan."),
                    (5, "Cook the tikkis", "Shallow-fry the patties on both sides until golden and crispy."),
                    (6, "Serve", "Serve hot with mint chutney or tomato sauce.")
                ]
            },

            {
                "recipe_name": "Paneer Tikka",
                "description": "A popular Indian snack made with marinated paneer cubes grilled with vegetables and spices.",
                "meal_type": "Snack",
                "dietary_preferences": ["vegetarian", "high-protein"],
                "preparation_time": 30,
                "servings": 2,
                "calories": 290,
                "protein": 18,
                "carbohydrates": 12,
                "fat": 19,
                "ingredients": [
                    ("Paneer", "200 g"),
                    ("Curd", "1/2 cup"),
                    ("Capsicum", "1 medium"),
                    ("Onions", "1 medium"),
                    ("Ginger-Garlic Paste", "1 tsp"),
                    ("Turmeric Powder", "1/4 tsp"),
                    ("Red Chilli Powder", "1/2 tsp"),
                    ("Garam Masala", "1/2 tsp"),
                    ("Lemon Juice", "1 tbsp"),
                    ("Cooking Oil", "1 tbsp"),
                    ("Salt", "To taste")
                ],
                "instructions": [
                    (1, "Prepare the paneer", "Cut paneer, capsicum, and onions into medium-sized cubes."),
                    (2, "Prepare the marinade", "Mix curd, ginger-garlic paste, spices, lemon juice, oil, and salt."),
                    (3, "Marinate", "Coat paneer and vegetables with the marinade and rest for 15 minutes."),
                    (4, "Arrange the skewers", "Thread paneer and vegetables onto skewers."),
                    (5, "Grill", "Grill or cook in a pan until lightly charred on all sides."),
                    (6, "Serve", "Serve hot with mint chutney.")
                ]
            },

            {
                "recipe_name": "Vegetable Pakora",
                "description": "Crispy Indian fritters prepared with sliced vegetables coated in seasoned gram flour batter.",
                "meal_type": "Snack",
                "dietary_preferences": ["vegetarian", "vegan"],
                "preparation_time": 25,
                "servings": 2,
                "calories": 280,
                "protein": 8,
                "carbohydrates": 35,
                "fat": 13,
                "ingredients": [
                    ("Besan", "1 cup"),
                    ("Onions", "1 medium"),
                    ("Potatoes", "1 small"),
                    ("Spinach", "1/2 cup"),
                    ("Green Chillies", "1"),
                    ("Red Chilli Powder", "1/2 tsp"),
                    ("Turmeric Powder", "1/4 tsp"),
                    ("Ajwain", "1/4 tsp"),
                    ("Cooking Oil", "For frying"),
                    ("Salt", "To taste")
                ],
                "instructions": [
                    (1, "Prepare the vegetables", "Thinly slice onions and potatoes. Chop spinach and green chillies."),
                    (2, "Prepare the batter", "Mix besan, chilli powder, turmeric, ajwain, and salt with a little water."),
                    (3, "Combine", "Add the vegetables to the batter and mix until coated."),
                    (4, "Heat the oil", "Heat oil in a deep frying pan."),
                    (5, "Fry the pakoras", "Drop small portions of the mixture into hot oil and fry until golden."),
                    (6, "Serve", "Drain excess oil and serve hot with chutney.")
                ]
            },

            {
                "recipe_name": "Corn Chaat",
                "description": "A tangy and refreshing Indian street-style snack made with sweet corn, vegetables, and spices.",
                "meal_type": "Snack",
                "dietary_preferences": ["vegetarian", "vegan"],
                "preparation_time": 15,
                "servings": 2,
                "calories": 180,
                "protein": 6,
                "carbohydrates": 32,
                "fat": 4,
                "ingredients": [
                    ("Sweet Corn", "1 cup"),
                    ("Onions", "1 small"),
                    ("Tomatoes", "1 small"),
                    ("Cucumber", "1/2 medium"),
                    ("Lemon Juice", "1 tbsp"),
                    ("Chaat Masala", "1/2 tsp"),
                    ("Red Chilli Powder", "1/4 tsp"),
                    ("Coriander Leaves", "2 tbsp"),
                    ("Salt", "To taste")
                ],
                "instructions": [
                    (1, "Cook the corn", "Boil sweet corn until tender and drain."),
                    (2, "Prepare the vegetables", "Finely chop onions, tomatoes, and cucumber."),
                    (3, "Combine ingredients", "Add corn and chopped vegetables to a bowl."),
                    (4, "Season", "Add lemon juice, chaat masala, chilli powder, and salt."),
                    (5, "Mix", "Toss everything until evenly combined."),
                    (6, "Serve", "Garnish with coriander leaves and serve immediately.")
                ]
            },

            {
                "recipe_name": "Bread Upma",
                "description": "A quick Indian snack made by tossing bread pieces with onions, tomatoes, and aromatic spices.",
                "meal_type": "Snack",
                "dietary_preferences": ["vegetarian", "vegan"],
                "preparation_time": 15,
                "servings": 2,
                "calories": 250,
                "protein": 7,
                "carbohydrates": 38,
                "fat": 8,
                "ingredients": [
                    ("Bread", "6 slices"),
                    ("Onions", "1 medium"),
                    ("Tomatoes", "1 medium"),
                    ("Green Chillies", "1"),
                    ("Mustard Seeds", "1/2 tsp"),
                    ("Turmeric Powder", "1/4 tsp"),
                    ("Curry Leaves", "6"),
                    ("Cooking Oil", "1 tbsp"),
                    ("Coriander Leaves", "2 tbsp"),
                    ("Salt", "To taste")
                ],
                "instructions": [
                    (1, "Prepare the bread", "Cut bread slices into small cubes."),
                    (2, "Prepare the tempering", "Heat oil and add mustard seeds, curry leaves, and green chillies."),
                    (3, "Cook the vegetables", "Add onions and tomatoes and cook until soft."),
                    (4, "Add spices", "Add turmeric powder and salt. Mix well."),
                    (5, "Add bread", "Add bread cubes and toss gently until coated and heated through."),
                    (6, "Serve", "Garnish with coriander leaves and serve warm.")
                ]
            },

            {
                "recipe_name": "Moong Dal Chilla",
                "description": "A protein-rich savoury pancake prepared with ground moong dal and mild Indian spices.",
                "meal_type": "Snack",
                "dietary_preferences": ["vegetarian", "vegan", "high-protein"],
                "preparation_time": 25,
                "servings": 2,
                "calories": 220,
                "protein": 13,
                "carbohydrates": 30,
                "fat": 6,
                "ingredients": [
                    ("Moong Dal", "1 cup"),
                    ("Onions", "1 small"),
                    ("Green Chillies", "1"),
                    ("Ginger", "1 tsp grated"),
                    ("Cumin Seeds", "1/2 tsp"),
                    ("Coriander Leaves", "2 tbsp"),
                    ("Turmeric Powder", "1/4 tsp"),
                    ("Cooking Oil", "1 tbsp"),
                    ("Water", "As required"),
                    ("Salt", "To taste")
                ],
                "instructions": [
                    (1, "Soak the dal", "Wash moong dal and soak it in water for 3–4 hours."),
                    (2, "Prepare the batter", "Drain and blend the dal with water into a smooth batter."),
                    (3, "Add seasonings", "Add chopped onions, green chillies, ginger, cumin, turmeric, coriander, and salt."),
                    (4, "Prepare the pan", "Heat a non-stick pan and lightly grease it with oil."),
                    (5, "Cook the chilla", "Spread batter evenly and cook both sides until golden."),
                    (6, "Serve", "Serve hot with mint chutney or tomato sauce.")
                ]
            },

            {
                "recipe_name": "Vegetable Cutlets",
                "description": "Crispy vegetable patties prepared with mashed potatoes, peas, carrots, and breadcrumbs.",
                "meal_type": "Snack",
                "dietary_preferences": ["vegetarian", "vegan"],
                "preparation_time": 30,
                "servings": 2,
                "calories": 270,
                "protein": 7,
                "carbohydrates": 39,
                "fat": 10,
                "ingredients": [
                    ("Potatoes", "2 medium"),
                    ("Carrots", "1 small"),
                    ("Green Peas", "1/4 cup"),
                    ("Bread Crumbs", "1/2 cup"),
                    ("Onions", "1 small"),
                    ("Garam Masala", "1/2 tsp"),
                    ("Red Chilli Powder", "1/4 tsp"),
                    ("Coriander Leaves", "2 tbsp"),
                    ("Cooking Oil", "2 tbsp"),
                    ("Salt", "To taste")
                ],
                "instructions": [
                    (1, "Cook the vegetables", "Boil potatoes, carrots, and green peas until tender."),
                    (2, "Prepare the mixture", "Mash the vegetables and mix with chopped onions, coriander, and spices."),
                    (3, "Shape the cutlets", "Add some breadcrumbs and shape the mixture into flat patties."),
                    (4, "Coat the cutlets", "Coat each patty with breadcrumbs."),
                    (5, "Cook", "Shallow-fry the cutlets in oil until golden and crispy on both sides."),
                    (6, "Serve", "Serve hot with green chutney or tomato sauce.")
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
