from flask import Blueprint, jsonify, render_template, request, redirect, session
from database import get_db_connection
import random


def normalize_ingredient_name(name):
    name = name.strip().lower()

    if name.endswith("ies"):
        return name[:-3] + "y"

    if name.endswith("oes"):
        return name[:-2]

    if name.endswith("s") and not name.endswith(("ss", "us", "is")):
        return name[:-1]

    return name

recipes_bp = Blueprint("recipes", __name__)
def get_recipe_by_id(connection, recipe_id, user_id):
    # Retrieve main recipe information
    recipe = connection.execute("""
        SELECT *
        FROM recipes
        WHERE recipe_id = %s
    """, (recipe_id,)).fetchone()

    if not recipe:
        return None

    # Retrieve the user's non-expired inventory
    inventory_items = connection.execute("""
        SELECT item_name
        FROM inventory
        WHERE user_id = %s
        AND expiration_date >= CURRENT_DATE
    """, (user_id,)).fetchall()

    # Normalize inventory ingredient names
    available_ingredients = {
        normalize_ingredient_name(item["item_name"])
        for item in inventory_items
    }

    # Retrieve recipe ingredients
    ingredients = connection.execute("""
        SELECT ingredient_name, amount
        FROM recipe_ingredients
        WHERE recipe_id = %s
        ORDER BY recipe_ingredient_id
    """, (recipe_id,)).fetchall()

    # Retrieve recipe instructions
    instructions = connection.execute("""
        SELECT title, description
        FROM recipe_instructions
        WHERE recipe_id = %s
        ORDER BY step_number
    """, (recipe_id,)).fetchall()

    return {
        "id": recipe["recipe_id"],
        "name": recipe["recipe_name"],
        "description": recipe["description"],
        "preparation_time": f'{recipe["preparation_time"]} minutes',
        "servings": recipe["servings"],

        "ingredients": [
            {
                "name": item["ingredient_name"],
                "amount": item["amount"],
                "available": (
                    normalize_ingredient_name(item["ingredient_name"])
                    in available_ingredients
                )
            }
            for item in ingredients
        ],

        "instructions": instructions
    }


def get_recipe_ids_by_meal_type(connection, meal_type):

    allowed_meal_types = (
        "Breakfast", "Lunch", "Dinner",
        "Brunch", "Snack", "Dessert"
    )

    if not isinstance(meal_type, str) or meal_type not in allowed_meal_types:
        return []

    recipes = connection.execute("""
        SELECT recipe_id
        FROM recipes
        WHERE meal_type = %s
        ORDER BY recipe_id
    """, (meal_type,)).fetchall()

    return [recipe["recipe_id"] for recipe in recipes]


def filter_recipes_by_dietary_preferences(
    connection,
    recipe_ids,
    dietary_preferences
):
    if not recipe_ids or not dietary_preferences:
        return recipe_ids

    recipes = connection.execute("""
        SELECT recipe_id
        FROM recipes
        WHERE recipe_id = ANY(%s)
        AND dietary_preferences @> %s
    """, (recipe_ids, dietary_preferences)).fetchall()

    return [recipe["recipe_id"] for recipe in recipes]



def filter_recipes_by_allergies(connection, recipe_ids, user_id):

    if not recipe_ids:
        return []

    # Retrieve ingredients associated with the user's selected allergens
    allergenic_foods = connection.execute("""
        SELECT DISTINCT fs.food_name
        FROM food_suggestions fs
        JOIN food_allergens fa
            ON fs.food_id = fa.food_id
        JOIN user_allergies ua
            ON fa.allergy_id = ua.allergy_id
        WHERE ua.user_id = %s
    """, (user_id,)).fetchall()

    # If the user has no mapped allergens, allow all recipes
    if not allergenic_foods:
        return recipe_ids

    # Normalize allergenic ingredient names
    unsafe_ingredients = {
        normalize_ingredient_name(food["food_name"])
        for food in allergenic_foods
    }

    # Retrieve ingredients belonging to the selected recipes
    ingredients = connection.execute("""
        SELECT recipe_id, ingredient_name
        FROM recipe_ingredients
        WHERE recipe_id = ANY(%s)
    """, (recipe_ids,)).fetchall()

    # Identify recipes containing allergenic ingredients
    unsafe_recipe_ids = {
        item["recipe_id"]
        for item in ingredients
        if normalize_ingredient_name(item["ingredient_name"])
        in unsafe_ingredients
    }

    # Return only recipes without the user's selected allergens
    return [
        recipe_id
        for recipe_id in recipe_ids
        if recipe_id not in unsafe_recipe_ids
    ]


def rank_recipes_by_inventory(
    connection,
    recipe_ids,
    user_id,
    expiring_ingredients=False
):
    if not recipe_ids:
        return {}

    # Retrieve the user's non-expired inventory
    inventory_items = connection.execute("""
        SELECT item_name, expiration_date
        FROM inventory
        WHERE user_id = %s
        AND expiration_date >= CURRENT_DATE
    """, (user_id,)).fetchall()

    # Store normalized names and expiration status
    available_ingredients = {}

    for item in inventory_items:
        ingredient = normalize_ingredient_name(item["item_name"])

    expiry_limit = connection.execute("""
        SELECT CURRENT_DATE + 7 AS expiry_limit
    """).fetchone()["expiry_limit"]

    # Store normalized names and expiration status
    available_ingredients = {}

    for item in inventory_items:
        ingredient = normalize_ingredient_name(item["item_name"])

        is_expiring = item["expiration_date"] <= expiry_limit

        available_ingredients[ingredient] = (
            available_ingredients.get(ingredient, False) or is_expiring
        )

        available_ingredients[ingredient] = (
            available_ingredients.get(ingredient, False) or is_expiring
        )

    # Retrieve recipe ingredients
    recipe_ingredients = connection.execute("""
        SELECT recipe_id, ingredient_name
        FROM recipe_ingredients
        WHERE recipe_id = ANY(%s)
    """, (recipe_ids,)).fetchall()

    # Initialize scores
    scores = {recipe_id: 0 for recipe_id in recipe_ids}

    for item in recipe_ingredients:
        ingredient = normalize_ingredient_name(item["ingredient_name"])

        if ingredient in available_ingredients:
            scores[item["recipe_id"]] += 1

            if expiring_ingredients and available_ingredients[ingredient]:
                scores[item["recipe_id"]] += 2

    # Return recipes ordered by score, with scores preserved
    return dict(
        sorted(
            scores.items(),
            key=lambda item: item[1],
            reverse=True
        )
    )


def select_recipe(
    connection,
    user_id,
    preferences
):
    # Step 1: Filter by meal type
    meal_type = preferences.get("mealType")

    if not isinstance(meal_type, str):
        return None
    recipe_ids = get_recipe_ids_by_meal_type(
        connection,
        meal_type
    )

    if not recipe_ids:
        return None

    # Step 2: Filter by dietary preferences
    dietary_preferences = preferences.get(
        "dietaryPreferences", []
    )

    allowed_dietary_preferences = {
        "vegetarian",
        "vegan",
        "high-protein",
        "low-calorie"
    }

    if not isinstance(dietary_preferences, list):
        return None

    if not all(
        isinstance(item, str) and item in allowed_dietary_preferences
        for item in dietary_preferences
    ):
        return None

    # Remove duplicate preferences
    dietary_preferences = list(set(dietary_preferences))

    recipe_ids = filter_recipes_by_dietary_preferences(
        connection,
        recipe_ids,
        dietary_preferences
    )

    if not recipe_ids:
        return None

    boolean_preferences = [
        "avoidAllergens",
        "useInventory",
        "expiringIngredients"
    ]

    if any(
        key in preferences and not isinstance(preferences[key], bool)
        for key in boolean_preferences
    ):
        return None

    # Step 3: Filter by allergies
    if preferences.get("avoidAllergens", True):
        recipe_ids = filter_recipes_by_allergies(
            connection,
            recipe_ids,
            user_id
        )

    if not recipe_ids:
        return None

    # Step 4: Rank using inventory
    use_inventory = preferences.get("useInventory", True)
    expiring_ingredients = preferences.get("expiringIngredients", False)

    if use_inventory:
        recipe_scores = rank_recipes_by_inventory(
            connection,
            recipe_ids,
            user_id,
            expiring_ingredients
        )
    else:
        recipe_scores = {
            recipe_id: 1
            for recipe_id in recipe_ids
        }

    # Step 5: Exclude recently generated recipes when alternatives exist
    eligible_ids = exclude_recent_recipes(
        connection,
        list(recipe_scores.keys()),
        user_id
    )

    # Step 6: Select using inventory scores as weights

    weights = [
        recipe_scores[recipe_id]
        for recipe_id in eligible_ids
    ]

    # If all scores are zero, give every recipe equal weight
    if sum(weights) == 0:
        weights = [1] * len(eligible_ids)

    selected_id = random.choices(
        eligible_ids,
        weights=weights,
        k=1
    )[0]

    return get_recipe_by_id(
        connection,
        selected_id,
        user_id
    )


def save_recipe_to_history(connection, user_id, recipe_id):

    connection.execute("""
        INSERT INTO user_recipe_history (
            user_id,
            recipe_id
        )
        VALUES (%s, %s)
    """, (user_id, recipe_id))


def get_recently_generated_recipes(connection, user_id):

    history = connection.execute("""
        SELECT DISTINCT recipe_id
        FROM user_recipe_history
        WHERE user_id = %s
        AND generated_at >= CURRENT_TIMESTAMP - INTERVAL '7 days'
    """, (user_id,)).fetchall()

    return {
        item["recipe_id"]
        for item in history
    }


def exclude_recent_recipes(connection, recipe_ids, user_id):

    if not recipe_ids:
        return []

    recent_recipes = get_recently_generated_recipes(
        connection,
        user_id
    )

    available_recipes = [
        recipe_id
        for recipe_id in recipe_ids
        if recipe_id not in recent_recipes
    ]

    # If all recipes were recently generated, allow them again
    if not available_recipes:
        return recipe_ids

    return available_recipes

@recipes_bp.route("/recipe-generation")
def recipe_generation():
    if "user_id" not in session:
        return redirect("/")

    return render_template("recipe-generation.html")


@recipes_bp.route("/api/recipe-history", methods=["GET"])
def get_recipe_history():

    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    user_id = session["user_id"]

    connection = get_db_connection()

    try:
        history = connection.execute("""
            SELECT
                h.history_id AS id,
                r.recipe_name AS name,
                TO_CHAR(h.generated_at, 'DD Mon YYYY') AS date,
                TO_CHAR(h.generated_at, 'HH12:MI AM') AS time
            FROM user_recipe_history h
            JOIN recipes r
                ON h.recipe_id = r.recipe_id
            WHERE h.user_id = %s
            ORDER BY h.generated_at DESC
        """, (user_id,)).fetchall()

        return jsonify({
            "recipes": history
        })

    except Exception as error:
        print("Recipe history error:", error)
        return jsonify({
            "error": "Unable to retrieve recipe history."
        }), 500

    finally:
        connection.close()


@recipes_bp.route("/api/generated-recipe", methods=["POST"])
def generate_recipe():

    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    preferences = request.get_json()

    if not isinstance(preferences, dict) or not preferences:
        return jsonify({
            "error": "Invalid or missing recipe preferences."
        }), 400

    user_id = session["user_id"]

    connection = get_db_connection()

    try:
        # Generate a recipe based on user preferences
        recipe = select_recipe(
            connection,
            user_id,
            preferences
        )

        if not recipe:
            return jsonify({
                "error": "No matching recipes found. Try changing your preferences."
            }), 404

        # Save the generated recipe to history
        save_recipe_to_history(
            connection,
            user_id,
            recipe["id"]
        )

        connection.commit()

        return jsonify({
            "recipe": recipe
        })

    except Exception as error:
        connection.rollback()
        print("Recipe generation error:", error)
        return jsonify({
            "error": "An unexpected error occurred while generating the recipe."
        }), 500

    finally:
        connection.close()


@recipes_bp.route("/api/recipe-history/<int:history_id>", methods=["GET"])
def get_historical_recipe(history_id):

    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    user_id = session["user_id"]

    connection = get_db_connection()

    try:
        # Retrieve the history entry and its generation date
        history_entry = connection.execute("""
            SELECT
                recipe_id,
                generated_at::DATE AS generation_date,
                CURRENT_DATE AS today
            FROM user_recipe_history
            WHERE history_id = %s
            AND user_id = %s
        """, (history_id, user_id)).fetchone()

        if not history_entry:
            return jsonify({
                "error": "Recipe history entry not found."
            }), 404

        # Add a new history entry only if the recipe is from an earlier day
        if history_entry["generation_date"] < history_entry["today"]:

            save_recipe_to_history(
                connection,
                user_id,
                history_entry["recipe_id"]
            )

            connection.commit()

        # Retrieve the recipe
        recipe = get_recipe_by_id(
            connection,
            history_entry["recipe_id"],
            user_id
        )

        return jsonify({
            "recipe": recipe
        })

    except Exception as error:
        connection.rollback()
        print("Historical recipe error:", error)
        return jsonify({
            "error": "Unable to retrieve the historical recipe."
        }), 500

    finally:
        connection.close()


@recipes_bp.route("/api/recipe-history/<int:history_id>", methods=["DELETE"])
def delete_recipe_history(history_id):

    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    user_id = session["user_id"]

    connection = get_db_connection()

    try:
        result = connection.execute("""
            DELETE FROM user_recipe_history
            WHERE history_id = %s
            AND user_id = %s
            RETURNING history_id
        """, (history_id, user_id)).fetchone()

        if not result:
            return jsonify({
                "error": "Recipe history entry not found."
            }), 404

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Recipe removed from history."
        })

    except Exception as error:
        connection.rollback()
        print("Recipe deletion error:", error)
        return jsonify({
            "error": "Unable to delete recipe from history."
        }), 500

    finally:
        connection.close()
