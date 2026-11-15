# This is for testing purposes only.

from database import get_db_connection
from routes.recipes import get_recipe_by_id
from routes.recipes import get_recipe_ids_by_meal_type
from routes.recipes import filter_recipes_by_dietary_preferences
from routes.recipes import filter_recipes_by_allergies
from routes.recipes import rank_recipes_by_inventory
from routes.recipes import select_recipe
from routes.recipes import save_recipe_to_history
from routes.recipes import get_recently_generated_recipes
from routes.recipes import exclude_recent_recipes


connection = get_db_connection()

try:
    recipe_record = connection.execute("""
        SELECT recipe_id
        FROM recipes
        WHERE recipe_name = %s
    """, ("Paneer Butter Masala",)).fetchone()

    if recipe_record:
        recipe = get_recipe_by_id(
            connection,
            recipe_record["recipe_id"],
            1  # Replace 1 with your actual user_id
        )
        # print(recipe)
        recipe_ids = get_recipe_ids_by_meal_type(
            connection,
            "Dinner"
        )

        print("Matching recipe IDs:", recipe_ids)
        recipe_ids = get_recipe_ids_by_meal_type(
            connection,
            "Dinner"
        )

        filtered_ids = filter_recipes_by_dietary_preferences(
            connection,
            recipe_ids,
            ["vegetarian"]
        )

        print("Vegetarian dinner recipes:", filtered_ids)
        safe_ids = filter_recipes_by_allergies(
            connection,
            filtered_ids,
            1  # Use your actual user_id
        )

        print("Recipes safe for user:", safe_ids)
        ranked_ids = rank_recipes_by_inventory(
            connection,
            safe_ids,
            1,  # Your actual user_id
            expiring_ingredients=True
        )

        print("Recipes prioritizing expiring ingredients:", ranked_ids)
        test_preferences = {
            "mealType": "Dinner",
            "useInventory": True,
            "expiringIngredients": True,
            "avoidAllergens": True,
            "dietaryPreferences": ["vegetarian"]
        }

        selected_recipe = select_recipe(
            connection,
            1,  # Your actual user_id
            test_preferences
        )

        print("Selected recipe:", selected_recipe["name"] if selected_recipe else "No recipe found")
        save_recipe_to_history(
            connection,
            1,  # Your actual user_id
            2   # Paneer Butter Masala's recipe_id
        )

        connection.commit()

        print("Recipe saved to history!")
        recent_recipes = get_recently_generated_recipes(
            connection,
            1  # Your actual user_id
        )

        print("Recently generated recipes:", recent_recipes)
        eligible_ids = exclude_recent_recipes(
            connection,
            [2, 3, 4],
            1  # Your actual user_id
        )

        print("Eligible recipes:", eligible_ids)

        fallback_ids = exclude_recent_recipes(
            connection,
            [2],
            1
        )

        print("Fallback recipes:", fallback_ids)
        recipe_scores = rank_recipes_by_inventory(
            connection,
            [2, 3, 4],
            1,
            expiring_ingredients=True
        )

        print("Recipe scores:", recipe_scores)
    else:
        print("Recipe not found.")

finally:
    connection.close()