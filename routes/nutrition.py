from datetime import datetime
from flask import (
    Blueprint,
    render_template,
    session,
    redirect,
    url_for,
    jsonify,
    request
)

from database import get_db_connection
from decimal import Decimal, InvalidOperation
import psycopg


nutrition_tracker_bp = Blueprint("nutrition_tracker", __name__)


# =========================================
# NUTRITION TRACKER PAGE
# =========================================

@nutrition_tracker_bp.route("/nutrition-tracker")
def nutrition_tracker_page():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    return render_template("nutrition-tracker.html")


# =========================================
# HELPER FUNCTIONS
# =========================================

def get_user_id():
    return session.get("user_id")


def get_nutrition_number(value):

    try:
        number = Decimal(str(value))

        if not number.is_finite() or number < 0:
            return None

        return number

    except (InvalidOperation, TypeError, ValueError):
        return None


# =========================================
# GET AVAILABLE FOODS
# =========================================

@nutrition_tracker_bp.route("/api/nutrition/foods", methods=["GET"])
def get_nutrition_foods():

    user_id = get_user_id()

    if not user_id:
        return jsonify({
            "success": False,
            "message": "Please log in."
        }), 401

    with get_db_connection() as connection:

        # Retrieve predefined and custom foods.

        foods = connection.execute("""
            SELECT
                food_id,
                food_name,
                calories,
                protein,
                carbohydrates,
                fats,
                is_custom
            FROM nutrition_foods
            WHERE user_id IS NULL OR user_id = %s
            ORDER BY is_custom, LOWER(food_name)
        """, (user_id,)).fetchall()

        # Retrieve existing recipes.

        recipes = connection.execute("""
            SELECT
                recipe_id,
                recipe_name,
                calories,
                protein,
                carbohydrates,
                fat
            FROM recipes
            ORDER BY LOWER(recipe_name)
        """).fetchall()

    return jsonify({
        "success": True,

        "foods": [
            {
                "food_id": food["food_id"],
                "food_name": food["food_name"],
                "calories": float(food["calories"]),
                "protein": float(food["protein"]),
                "carbohydrates": float(food["carbohydrates"]),
                "fats": float(food["fats"]),
                "is_custom": food["is_custom"],
                "item_type": "food"
            }
            for food in foods
        ],

        "recipes": [
            {
                "recipe_id": recipe["recipe_id"],
                "food_name": recipe["recipe_name"],
                "calories": float(recipe["calories"] or 0),
                "protein": float(recipe["protein"] or 0),
                "carbohydrates": float(recipe["carbohydrates"] or 0),
                "fats": float(recipe["fat"] or 0),
                "item_type": "recipe"
            }
            for recipe in recipes
        ]
    })


# =========================================
# CREATE CUSTOM FOOD
# =========================================

@nutrition_tracker_bp.route("/api/nutrition/foods", methods=["POST"])
def create_custom_food():

    user_id = get_user_id()

    if not user_id:
        return jsonify({
            "success": False,
            "message": "Please log in."
        }), 401

    data = request.get_json(silent=True) or {}

    food_name = str(data.get("food_name", "")).strip()

    if len(food_name) < 2 or len(food_name) > 100:
        return jsonify({
            "success": False,
            "message": "Food name must contain 2 to 100 characters."
        }), 400

    calories = get_nutrition_number(data.get("calories"))
    protein = get_nutrition_number(data.get("protein"))
    carbohydrates = get_nutrition_number(data.get("carbohydrates"))
    fats = get_nutrition_number(data.get("fats"))

    if any(value is None for value in [
        calories, protein, carbohydrates, fats
    ]):
        return jsonify({
            "success": False,
            "message": "Enter valid, non-negative nutritional values."
        }), 400

    try:
        with get_db_connection() as connection:

            food = connection.execute("""
                INSERT INTO nutrition_foods (
                    user_id,
                    food_name,
                    calories,
                    protein,
                    carbohydrates,
                    fats,
                    is_custom
                )
                VALUES (%s, %s, %s, %s, %s, %s, TRUE)
                RETURNING food_id
            """, (
                user_id,
                food_name,
                calories,
                protein,
                carbohydrates,
                fats
            )).fetchone()

        return jsonify({
            "success": True,
            "message": "Custom food created successfully.",
            "food_id": food["food_id"]
        }), 201

    except psycopg.errors.UniqueViolation:
        return jsonify({
            "success": False,
            "message": "You have already created a food with this name."
        }), 409


# =========================================
# ADD FOOD TO DAILY LOG
# =========================================


@nutrition_tracker_bp.route("/api/nutrition/logs", methods=["POST"])
def add_nutrition_log():

    user_id = get_user_id()

    if not user_id:
        return jsonify({
            "success": False,
            "message": "Please log in."
        }), 401

    data = request.get_json(silent=True) or {}

    # Identify whether the selected item is a food or recipe.

    item_type = data.get("item_type", "food")

    if item_type not in ["food", "recipe"]:
        return jsonify({
            "success": False,
            "message": "Invalid item type."
        }), 400

    try:
        item_id = int(data.get("item_id", data.get("food_id")))
    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "message": "Select a valid food or recipe."
        }), 400

    quantity = get_nutrition_number(data.get("quantity"))

    if quantity is None or quantity <= 0:
        return jsonify({
            "success": False,
            "message": "Quantity must be greater than zero."
        }), 400

    with get_db_connection() as connection:

        # Retrieve a regular or custom food.

        if item_type == "food":

            item = connection.execute("""
                SELECT
                    food_id AS item_id,
                    food_name,
                    calories,
                    protein,
                    carbohydrates,
                    fats
                FROM nutrition_foods
                WHERE food_id = %s
                  AND (user_id IS NULL OR user_id = %s)
            """, (item_id, user_id)).fetchone()

            food_id = item["item_id"] if item else None

        # Retrieve a recipe.

        else:

            item = connection.execute("""
                SELECT
                    recipe_id AS item_id,
                    recipe_name AS food_name,
                    calories,
                    protein,
                    carbohydrates,
                    fat AS fats
                FROM recipes
                WHERE recipe_id = %s
            """, (item_id,)).fetchone()

            # Recipes are not stored in nutrition_foods.
            # Therefore, their food_id must remain NULL.

            food_id = None

        if not item:
            return jsonify({
                "success": False,
                "message": "Selected item not found."
            }), 404

        # Treat missing recipe nutrition values as zero.

        calories = item["calories"] or 0
        protein = item["protein"] or 0
        carbohydrates = item["carbohydrates"] or 0
        fats = item["fats"] or 0

        # Calculate nutrition based on quantity.

        total_calories = calories * quantity
        total_protein = protein * quantity
        total_carbohydrates = carbohydrates * quantity
        total_fats = fats * quantity

        log = connection.execute("""
            INSERT INTO nutrition_food_log (
                user_id,
                food_id,
                food_name,
                quantity,
                calories,
                protein,
                carbohydrates,
                fats
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING log_id
        """, (
            user_id,
            food_id,
            item["food_name"],
            quantity,
            total_calories,
            total_protein,
            total_carbohydrates,
            total_fats
        )).fetchone()

    return jsonify({
        "success": True,
        "message": "Item added to your food log.",
        "log_id": log["log_id"]
    }), 201


# =========================================
# GET TODAY'S FOOD LOG
# =========================================

@nutrition_tracker_bp.route("/api/nutrition/logs/today", methods=["GET"])
def get_today_nutrition_logs():

    user_id = get_user_id()

    if not user_id:
        return jsonify({
            "success": False,
            "message": "Please log in."
        }), 401

    with get_db_connection() as connection:

        logs = connection.execute("""
            SELECT
                log_id,
                food_name,
                quantity,
                calories,
                protein,
                carbohydrates,
                fats,
                logged_at
            FROM nutrition_food_log
            WHERE user_id = %s
            AND logged_at::date = CURRENT_DATE
            ORDER BY logged_at DESC
        """, (user_id,)).fetchall()

    food_logs = [
        {
            "log_id": log["log_id"],
            "food_name": log["food_name"],
            "quantity": float(log["quantity"]),
            "calories": float(log["calories"]),
            "protein": float(log["protein"]),
            "carbohydrates": float(log["carbohydrates"]),
            "fats": float(log["fats"]),
            "logged_at": log["logged_at"].isoformat()
        }
        for log in logs
    ]

    totals = {
        "calories": sum(item["calories"] for item in food_logs),
        "protein": sum(item["protein"] for item in food_logs),
        "carbohydrates": sum(item["carbohydrates"] for item in food_logs),
        "fats": sum(item["fats"] for item in food_logs)
    }

    return jsonify({
        "success": True,
        "logs": food_logs,
        "totals": totals
    })


# =========================================
# DELETE FOOD LOG ENTRY
# =========================================

@nutrition_tracker_bp.route(
    "/api/nutrition/logs/<int:log_id>",
    methods=["DELETE"]
)
def delete_nutrition_log(log_id):

    user_id = get_user_id()

    if not user_id:
        return jsonify({
            "success": False,
            "message": "Please log in."
        }), 401

    with get_db_connection() as connection:

        deleted = connection.execute("""
            DELETE FROM nutrition_food_log
            WHERE log_id = %s
            AND user_id = %s
            RETURNING log_id
        """, (log_id, user_id)).fetchone()

    if not deleted:
        return jsonify({
            "success": False,
            "message": "Food log entry not found."
        }), 404

    return jsonify({
        "success": True,
        "message": "Food log entry deleted."
    })


@nutrition_tracker_bp.route("/api/nutrition/foods/<int:food_id>", methods=["DELETE"])
def delete_custom_food(food_id):

    user_id = get_user_id()

    if not user_id:
        return jsonify({
            "success": False,
            "message": "Please log in first."
        }), 401

    with get_db_connection() as connection:

        deleted_food = connection.execute(
            """
            DELETE FROM nutrition_foods
            WHERE food_id = %s
              AND user_id = %s
              AND is_custom = TRUE
            RETURNING food_id
            """,
            (food_id, user_id)
        ).fetchone()

    if not deleted_food:
        return jsonify({
            "success": False,
            "message": "Custom food not found."
        }), 404

    return jsonify({
        "success": True,
        "message": "Custom food deleted successfully."
    })

@nutrition_tracker_bp.route("/api/nutrition/reports/<period>", methods=["GET"])
def get_nutrition_report(period):

    user_id = get_user_id()

    if not user_id:
        return jsonify({
            "success": False,
            "message": "Please log in first."
        }), 401

    if period == "30-days":
        date_condition = "CURRENT_DATE - INTERVAL '29 days'"

    elif period == "1-year":
        date_condition = "CURRENT_DATE - INTERVAL '364 days'"

    else:
        return jsonify({
            "success": False,
            "message": "Invalid report period."
        }), 400

    with get_db_connection() as connection:

        logs = connection.execute(
            f"""
            SELECT
                log_id,
                food_name,
                quantity,
                calories,
                protein,
                carbohydrates,
                fats,
                logged_at
            FROM nutrition_food_log
            WHERE user_id = %s
              AND logged_at >= {date_condition}
              AND logged_at < CURRENT_DATE + INTERVAL '1 day'
            ORDER BY logged_at ASC
            """,
            (user_id,)
        ).fetchall()

    report_logs = []

    for log in logs:

        report_logs.append({
            "log_id": log["log_id"],
            "food_name": log["food_name"],
            "quantity": float(log["quantity"]),
            "calories": float(log["calories"]),
            "protein": float(log["protein"]),
            "carbohydrates": float(log["carbohydrates"]),
            "fats": float(log["fats"]),
            "logged_at": log["logged_at"].isoformat()
        })

    return jsonify({
        "success": True,
        "period": period,
        "logs": report_logs
    })

@nutrition_tracker_bp.route("/api/nutrition/logs/date/<date_string>", methods=["GET"])
def get_nutrition_logs_by_date(date_string):

    user_id = get_user_id()

    if not user_id:
        return jsonify({
            "success": False,
            "message": "Please log in first."
        }), 401

    # Validate the requested date.

    try:
        selected_date = datetime.strptime(
            date_string, "%Y-%m-%d"
        ).date()

    except ValueError:
        return jsonify({
            "success": False,
            "message": "Invalid date format."
        }), 400

    with get_db_connection() as connection:

        logs = connection.execute(
            """
            SELECT
                log_id,
                food_name,
                quantity,
                calories,
                protein,
                carbohydrates,
                fats,
                logged_at
            FROM nutrition_food_log
            WHERE user_id = %s
              AND logged_at::date = %s
            ORDER BY logged_at ASC
            """,
            (user_id, selected_date)
        ).fetchall()

    report_logs = []

    totals = {
        "calories": 0,
        "protein": 0,
        "carbohydrates": 0,
        "fats": 0
    }

    for log in logs:

        entry = {
            "log_id": log["log_id"],
            "food_name": log["food_name"],
            "quantity": float(log["quantity"]),
            "calories": float(log["calories"]),
            "protein": float(log["protein"]),
            "carbohydrates": float(log["carbohydrates"]),
            "fats": float(log["fats"]),
            "logged_at": log["logged_at"].isoformat()
        }

        report_logs.append(entry)

        totals["calories"] += entry["calories"]
        totals["protein"] += entry["protein"]
        totals["carbohydrates"] += entry["carbohydrates"]
        totals["fats"] += entry["fats"]

    return jsonify({
        "success": True,
        "date": date_string,
        "logs": report_logs,
        "totals": totals
    })

# =========================================
# DAILY NUTRITION GOALS
# =========================================

@nutrition_tracker_bp.route("/api/nutrition/goals", methods=["GET"])
def get_nutrition_goals():

    user_id = get_user_id()

    if not user_id:
        return jsonify({
            "success": False,
            "message": "Please log in."
        }), 401

    with get_db_connection() as connection:

        connection.execute("""
            INSERT INTO nutrition_goals (user_id)
            VALUES (%s)
            ON CONFLICT (user_id) DO NOTHING
        """, (user_id,))

        goals = connection.execute("""
            SELECT calories, protein, carbohydrates, fats
            FROM nutrition_goals
            WHERE user_id = %s
        """, (user_id,)).fetchone()

    return jsonify({
        "success": True,
        "goals": goals
    })

@nutrition_tracker_bp.route("/api/nutrition/goals", methods=["PUT"])
def update_nutrition_goals():

    user_id = get_user_id()

    if not user_id:
        return jsonify({
            "success": False,
            "message": "Please log in."
        }), 401

    data = request.get_json()

    calories = get_nutrition_number(data.get("calories"))
    protein = get_nutrition_number(data.get("protein"))
    carbohydrates = get_nutrition_number(data.get("carbohydrates"))
    fats = get_nutrition_number(data.get("fats"))

    values = [calories, protein, carbohydrates, fats]

    if any(value is None or value <= 0 for value in values):
        return jsonify({
            "success": False,
            "message": "All nutrition goals must be valid numbers greater than zero."
        }), 400

    with get_db_connection() as connection:

        connection.execute("""
            INSERT INTO nutrition_goals (
                user_id, calories, protein, carbohydrates, fats
            )
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (user_id)
            DO UPDATE SET
                calories = EXCLUDED.calories,
                protein = EXCLUDED.protein,
                carbohydrates = EXCLUDED.carbohydrates,
                fats = EXCLUDED.fats,
                updated_at = CURRENT_TIMESTAMP
        """, (
            user_id,
            calories,
            protein,
            carbohydrates,
            fats
        ))

    return jsonify({
        "success": True,
        "message": "Daily nutrition goals updated successfully."
    })