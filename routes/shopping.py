from flask import Blueprint, render_template, redirect, session, jsonify, request
from database import get_db_connection
import re
from fractions import Fraction

def normalize_shopping_ingredient(name):
    name = name.strip().lower()

    if name.endswith("ies"):
        return name[:-3] + "y"

    if name.endswith("oes"):
        return name[:-2]

    if name.endswith("s") and not name.endswith(("ss", "us", "is")):
        return name[:-1]

    return name


def double_ingredient_quantity(quantity):

    if not quantity:
        return quantity

    match = re.match(
        r"^\s*(\d+/\d+|\d+(?:\.\d+)?)(.*)$",
        quantity
    )

    if not match:
        return quantity

    number = Fraction(match.group(1))
    doubled = number * 2

    return f"{doubled}{match.group(2)}"

shopping_bp = Blueprint("shopping", __name__)

@shopping_bp.route("/shopping-list")
def shopping_list():
    if "user_id" not in session:
        return redirect("/")

    return render_template("shopping-list.html")

@shopping_bp.route("/api/shopping-history/<int:history_id>", methods=["GET"])
def get_historical_shopping_list(history_id):

    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    user_id = session["user_id"]
    connection = get_db_connection()

    try:
        # Step 1: Verify that the history belongs to the logged-in user
        history = connection.execute("""
            SELECT history_id, saved_at
            FROM shopping_history
            WHERE history_id = %s
              AND user_id = %s
        """, (history_id, user_id)).fetchone()

        if not history:
            return jsonify({
                "error": "Shopping history not found."
            }), 404

        # Step 2: Retrieve the historical shopping items
        result = connection.execute("""
            SELECT
                history_item_id,
                food_id,
                item_name,
                quantity,
                is_completed
            FROM shopping_history_items
            WHERE history_id = %s
            ORDER BY history_item_id ASC
        """, (history_id,)).fetchall()

        items = [
            {
                "id": row["history_item_id"],
                "food_id": row["food_id"],
                "name": row["item_name"],
                "quantity": row["quantity"],
                "completed": row["is_completed"]
            }
            for row in result
        ]

        return jsonify({
            "history_id": history["history_id"],
            "date": history["saved_at"].strftime("%B %d, %Y"),
            "items": items
        })

    except Exception as error:
        print("Historical shopping list error:", error)
        return jsonify({
            "error": "Unable to retrieve historical shopping list."
        }), 500

    finally:
        connection.close()

@shopping_bp.route("/api/shopping-history/<int:history_id>", methods=["DELETE"])
def delete_historical_shopping_list(history_id):

    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    user_id = session["user_id"]
    connection = get_db_connection()

    try:
        result = connection.execute("""
            DELETE FROM shopping_history
            WHERE history_id = %s
              AND user_id = %s
            RETURNING history_id
        """, (history_id, user_id)).fetchone()

        if not result:
            return jsonify({
                "error": "Shopping history not found."
            }), 404

        connection.commit()

        return jsonify({
            "message": "Shopping history deleted successfully.",
            "history_id": result["history_id"]
        })

    except Exception as error:
        connection.rollback()
        print("Delete shopping history error:", error)

        return jsonify({
            "error": "Unable to delete shopping history."
        }), 500

    finally:
        connection.close()

@shopping_bp.route("/api/shopping-history", methods=["GET"])
def get_shopping_history():

    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    user_id = session["user_id"]
    connection = get_db_connection()

    try:
        result = connection.execute("""
            SELECT
                history.history_id,
                history.saved_at,
                COUNT(items.history_item_id) AS item_count
            FROM shopping_history AS history
            LEFT JOIN shopping_history_items AS items
                ON history.history_id = items.history_id
            WHERE history.user_id = %s
            GROUP BY history.history_id, history.saved_at
            ORDER BY history.saved_at DESC
        """, (user_id,)).fetchall()

        shopping_history = [
            {
                "id": row["history_id"],
                "name": f"Shopping List #{row['history_id']}",
                "date": row["saved_at"].strftime("%B %d, %Y"),
                "item_count": row["item_count"]
            }
            for row in result
        ]

        return jsonify({"shopping_history": shopping_history})

    except Exception as error:
        print("Shopping history error:", error)
        return jsonify({
            "error": "Unable to fetch shopping history."
        }), 500

    finally:
        connection.close()

@shopping_bp.route("/api/shopping-food-suggestions", methods=["GET"])
def get_shopping_food_suggestions():

    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    query = request.args.get("q", "").strip()

    if len(query) < 3:
        return jsonify({"suggestions": []})

    connection = get_db_connection()

    try:
        result = connection.execute("""
            SELECT food_id, food_name, category
            FROM food_suggestions
            WHERE food_name ILIKE %s
            ORDER BY food_name ASC
            LIMIT 10
        """, (f"%{query}%",)).fetchall()

        suggestions = [
            {
                "food_id": row["food_id"],
                "food_name": row["food_name"],
                "category": row["category"]
            }
            for row in result
        ]

        return jsonify({"suggestions": suggestions})

    except Exception as error:
        print("Food suggestions error:", error)
        return jsonify({"error": "Unable to fetch food suggestions."}), 500

    finally:
        connection.close()

@shopping_bp.route("/api/shopping-suggestions", methods=["GET"])
def get_shopping_suggestions():

    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    user_id = session["user_id"]

    connection = get_db_connection()

    try:

        # ESSENTIAL FOODS
        essential_result = connection.execute("""
        SELECT
            fs.food_id,
            fs.food_name,
            fs.category
        FROM essential_foods ef
        JOIN food_suggestions fs
            ON fs.food_id = ef.food_id
        WHERE NOT EXISTS (
            SELECT 1
            FROM inventory i
            WHERE i.user_id = %s
            AND LOWER(TRIM(i.item_name)) = LOWER(TRIM(fs.food_name))
        )
        AND NOT EXISTS (
            SELECT 1
            FROM active_shopping_items asi
            JOIN active_shopping_lists asl
                ON asl.list_id = asi.list_id
            WHERE asl.user_id = %s
            AND LOWER(TRIM(asi.item_name)) = LOWER(TRIM(fs.food_name))
        )
        ORDER BY RANDOM()
        LIMIT 25
        """, (user_id, user_id)).fetchall()

        # NEAR-EXPIRY INVENTORY ITEMS
        near_expiry_result = connection.execute("""
            SELECT
                i.inventory_id,
                fs.food_id,
                i.item_name AS food_name,
                i.category,
                i.expiration_date
            FROM inventory i
            LEFT JOIN food_suggestions fs
                ON LOWER(TRIM(fs.food_name)) = LOWER(TRIM(i.item_name))
            WHERE i.user_id = %s
            AND i.expiration_date BETWEEN CURRENT_DATE
                AND CURRENT_DATE + INTERVAL '7 days'
            AND NOT EXISTS (
                SELECT 1
                FROM active_shopping_items asi
                JOIN active_shopping_lists asl
                    ON asl.list_id = asi.list_id
                WHERE asl.user_id = %s
                AND LOWER(TRIM(asi.item_name)) = LOWER(TRIM(i.item_name))
            )
            ORDER BY RANDOM()
            LIMIT 7
        """, (user_id, user_id)).fetchall()

        # PREVIOUSLY BOUGHT ITEMS
        previously_bought_result = connection.execute("""
            WITH unique_items AS (
                SELECT DISTINCT ON (LOWER(TRIM(shi.item_name)))
                    shi.food_id,
                    shi.item_name AS food_name,
                    fs.category,
                    sh.saved_at
                FROM shopping_history_items shi
                JOIN shopping_history sh
                    ON sh.history_id = shi.history_id
                LEFT JOIN food_suggestions fs
                    ON fs.food_id = shi.food_id
                WHERE sh.user_id = %s
                AND shi.is_completed = TRUE
                AND NOT EXISTS (
                    SELECT 1
                    FROM inventory i
                    WHERE i.user_id = %s
                        AND LOWER(TRIM(i.item_name)) =
                            LOWER(TRIM(shi.item_name))
                )
                AND NOT EXISTS (
                    SELECT 1
                    FROM active_shopping_items asi
                    JOIN active_shopping_lists asl
                        ON asl.list_id = asi.list_id
                    WHERE asl.user_id = %s
                    AND LOWER(TRIM(asi.item_name)) =
                        LOWER(TRIM(shi.item_name))
                )
                ORDER BY
                    LOWER(TRIM(shi.item_name)),
                    sh.saved_at DESC
            )

            SELECT
                food_id,
                food_name,
                category
            FROM unique_items
            ORDER BY RANDOM()
            LIMIT 8
        """, (user_id, user_id, user_id)).fetchall()

        # USER SHOPPING TEMPLATE ITEMS
        templates_result = connection.execute("""
            SELECT
                items.food_id,
                items.item_name AS food_name,
                items.frequency
            FROM shopping_templates AS templates
            JOIN shopping_template_items AS items
                ON templates.template_id = items.template_id
            WHERE templates.user_id = %s
            AND NOT EXISTS (
                SELECT 1
                FROM inventory i
                WHERE i.user_id = %s
                    AND LOWER(TRIM(i.item_name)) =
                        LOWER(TRIM(items.item_name))
            )
            AND NOT EXISTS (
                SELECT 1
                FROM active_shopping_items asi
                JOIN active_shopping_lists asl
                    ON asl.list_id = asi.list_id
                WHERE asl.user_id = %s
                AND LOWER(TRIM(asi.item_name)) =
                    LOWER(TRIM(items.item_name))
            )
            ORDER BY RANDOM()
            LIMIT 6
        """, (user_id, user_id, user_id)).fetchall()

        suggestions = {
            "essential": [
                dict(row) for row in essential_result
            ],

            "near_expiry": [
                dict(row) for row in near_expiry_result
            ],

            "previously_bought": [
                dict(row) for row in previously_bought_result
            ],

            "templates": [
                dict(row) for row in templates_result
            ]        }

        return jsonify({"suggestions": suggestions})

    except Exception as error:
        print("Shopping suggestions error:", error)
        return jsonify({
            "error": "Unable to fetch shopping suggestions."
        }), 500

    finally:
        connection.close()


@shopping_bp.route("/api/shopping-template", methods=["GET"])
def get_shopping_template():

    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    user_id = session["user_id"]
    connection = get_db_connection()

    try:
        result = connection.execute("""
            SELECT
                items.food_id,
                items.item_name AS food_name,
                items.frequency
            FROM shopping_templates AS templates
            JOIN shopping_template_items AS items
                ON templates.template_id = items.template_id
            WHERE templates.user_id = %s
            ORDER BY items.template_item_id ASC
        """, (user_id,)).fetchall()

        template = {
            "frequent": [],
            "occasional": [],
            "rare": []
        }

        for row in result:
            template[row["frequency"]].append({
                "food_id": row["food_id"],
                "food_name": row["food_name"]
            })

        return jsonify({"template": template})

    except Exception as error:
        print("Get shopping template error:", error)
        return jsonify({
            "error": "Unable to retrieve shopping template."
        }), 500

    finally:
        connection.close()


@shopping_bp.route("/api/shopping-template", methods=["POST"])
def save_shopping_template():

    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    user_id = session["user_id"]
    data = request.get_json()

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid request data."}), 400

    frequencies = ["frequent", "occasional", "rare"]

    # Validate the submitted template
    for frequency in frequencies:

        items = data.get(frequency)

        if not isinstance(items, list):
            return jsonify({
                "error": f"Invalid {frequency} items."
            }), 400

        if not all(
            isinstance(item, dict)
            and (
                (
                    isinstance(item.get("food_id"), int)
                    and not isinstance(item.get("food_id"), bool)
                    and item["food_id"] > 0
                )
                or (
                    item.get("food_id") is None
                    and isinstance(item.get("food_name"), str)
                    and len(item["food_name"].strip()) >= 3
                )
            )
            for item in items
        ):
            return jsonify({
                "error": f"Invalid items in {frequency} section."
            }), 400

    # Prevent the same food from appearing in multiple sections
    all_food_ids = [
        item["food_id"]
        for frequency in frequencies
        for item in data[frequency]
        if item["food_id"] is not None
    ]

    all_food_names = [
        item["food_name"].strip().lower()
        for frequency in frequencies
        for item in data[frequency]
        if item["food_id"] is None
    ]

    if (
        len(all_food_ids) != len(set(all_food_ids))
        or len(all_food_names) != len(set(all_food_names))
    ):
        return jsonify({
            "error": "An item cannot appear in multiple frequency sections."
        }), 400

    connection = get_db_connection()

    try:

        # Step 1: Verify that all submitted food IDs exist
        if all_food_ids:

            valid_foods = connection.execute("""
                SELECT food_id, food_name
                FROM food_suggestions
                WHERE food_id = ANY(%s)
            """, (all_food_ids,)).fetchall()

            if len(valid_foods) != len(all_food_ids):
                return jsonify({
                    "error": "One or more selected food items are invalid."
                }), 400

            food_names = {
                row["food_id"]: row["food_name"]
                for row in valid_foods
            }

        else:
            food_names = {}

        # Step 2: Create the user's template if it doesn't exist
        result = connection.execute("""
            INSERT INTO shopping_templates (user_id)
            VALUES (%s)
            ON CONFLICT (user_id) DO NOTHING
            RETURNING template_id
        """, (user_id,)).fetchone()

        if result:
            template_id = result["template_id"]

        else:
            result = connection.execute("""
                SELECT template_id
                FROM shopping_templates
                WHERE user_id = %s
            """, (user_id,)).fetchone()

            template_id = result["template_id"]

        # Step 3: Replace the existing template items
        connection.execute("""
            DELETE FROM shopping_template_items
            WHERE template_id = %s
        """, (template_id,))

        # Step 4: Insert the updated items
        saved_count = 0

        for frequency in frequencies:

            for item in data[frequency]:

                food_id = item["food_id"]

                item_name = (
                    food_names[food_id]
                    if food_id is not None
                    else item["food_name"].strip()
                )

                connection.execute("""
                    INSERT INTO shopping_template_items (
                        template_id,
                        food_id,
                        item_name,
                        frequency
                    )
                    VALUES (%s, %s, %s, %s)
                """, (
                    template_id,
                    food_id,
                    item_name,
                    frequency
                ))

                saved_count += 1

        # Step 5: Update template modification time
        connection.execute("""
            UPDATE shopping_templates
            SET updated_at = CURRENT_TIMESTAMP
            WHERE template_id = %s
        """, (template_id,))

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Shopping template saved successfully.",
            "template_id": template_id,
            "saved_items": saved_count
        })

    except Exception as error:
        connection.rollback()
        print("Save shopping template error:", error)

        return jsonify({
            "error": "Unable to save shopping template."
        }), 500

    finally:
        connection.close()


@shopping_bp.route("/api/active-shopping-list", methods=["GET"])
def get_active_shopping_list():

    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    user_id = session["user_id"]
    connection = get_db_connection()

    try:
        # Step 1: Create an active list if the user doesn't already have one
        result = connection.execute("""
            INSERT INTO active_shopping_lists (user_id)
            VALUES (%s)
            ON CONFLICT (user_id) DO NOTHING
            RETURNING list_id
        """, (user_id,)).fetchone()

        if result:
            list_id = result["list_id"]
        else:
            # Retrieve the user's existing active list
            result = connection.execute("""
                SELECT list_id
                FROM active_shopping_lists
                WHERE user_id = %s
            """, (user_id,)).fetchone()

            list_id = result["list_id"]

        connection.commit()

        # Step 2: Retrieve the items in the active list
        result = connection.execute("""
            SELECT item_id, food_id, item_name, quantity, is_completed
            FROM active_shopping_items
            WHERE list_id = %s
            ORDER BY item_id ASC
        """, (list_id,)).fetchall()

        items = [
            {
                "id": row["item_id"],
                "food_id": row["food_id"],
                "name": row["item_name"],
                "quantity": row["quantity"],
                "completed": row["is_completed"]
            }
            for row in result
        ]

        return jsonify({
            "list_id": list_id,
            "items": items
        })

    except Exception as error:
        connection.rollback()
        print("Active shopping list error:", error)
        return jsonify({"error": "Unable to retrieve shopping list."}), 500

    finally:
        connection.close()

@shopping_bp.route("/api/active-shopping-list/items", methods=["POST"])
def add_active_shopping_item():

    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    user_id = session["user_id"]
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid request data."}), 400

    item_name = data.get("name", "").strip()
    quantity = data.get("quantity", "").strip()
    food_id = data.get("food_id")

    if len(item_name) < 3:
        return jsonify({"error": "Food item must contain at least 3 characters."}), 400

    connection = get_db_connection()

    try:
        # Retrieve the user's active shopping list
        result = connection.execute("""
            SELECT list_id
            FROM active_shopping_lists
            WHERE user_id = %s
        """, (user_id,)).fetchone()

        if not result:
            return jsonify({"error": "Active shopping list not found."}), 404

        list_id = result["list_id"]

        # Check whether the item already exists in the active shopping list
        existing_item = connection.execute("""
            SELECT item_id
            FROM active_shopping_items
            WHERE list_id = %s
            AND LOWER(TRIM(item_name)) = LOWER(TRIM(%s))
        """, (list_id, item_name)).fetchone()

        if existing_item:
            return jsonify({
                "success": False,
                "already_exists": True,
                "message": "This item is already in your shopping list."
            }), 200

        # Insert the new item
        result = connection.execute("""
            INSERT INTO active_shopping_items
                (list_id, food_id, item_name, quantity)
            VALUES (%s, %s, %s, %s)
            RETURNING item_id, food_id, item_name, quantity, is_completed
        """, (list_id, food_id, item_name, quantity)).fetchone()

        connection.commit()

        return jsonify({
            "message": "Item added successfully.",
            "item": {
                "id": result["item_id"],
                "food_id": result["food_id"],
                "name": result["item_name"],
                "quantity": result["quantity"],
                "completed": result["is_completed"]
            }
        }), 201

    except Exception as error:
        connection.rollback()
        print("Add shopping item error:", error)
        return jsonify({"error": "Unable to add shopping item."}), 500

    finally:
        connection.close()

@shopping_bp.route("/api/active-shopping-list/items", methods=["DELETE"])
def clear_active_shopping_list():

    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    user_id = session["user_id"]

    connection = get_db_connection()

    try:
        connection.execute("""
            DELETE FROM active_shopping_items
            WHERE list_id = (
                SELECT list_id
                FROM active_shopping_lists
                WHERE user_id = %s
            )
        """, (user_id,))

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Shopping list cleared successfully."
        })

    except Exception as error:
        print("Clear shopping list error:", error)
        return jsonify({"error": "Unable to clear shopping list."}), 500

    finally:
        connection.close()

@shopping_bp.route("/api/active-shopping-list/items/<int:item_id>", methods=["PATCH"])
def update_shopping_item_status(item_id):

    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()

    if not data or "completed" not in data:
        return jsonify({"error": "Completion status is required."}), 400

    completed = data["completed"]

    if not isinstance(completed, bool):
        return jsonify({"error": "Invalid completion status."}), 400

    user_id = session["user_id"]
    connection = get_db_connection()

    try:
        result = connection.execute("""
            UPDATE active_shopping_items AS items
            SET is_completed = %s
            FROM active_shopping_lists AS lists
            WHERE items.item_id = %s
              AND items.list_id = lists.list_id
              AND lists.user_id = %s
            RETURNING items.item_id, items.is_completed
        """, (completed, item_id, user_id)).fetchone()

        if not result:
            return jsonify({"error": "Shopping item not found."}), 404

        connection.commit()

        return jsonify({
            "message": "Shopping item status updated successfully.",
            "item": {
                "id": result["item_id"],
                "completed": result["is_completed"]
            }
        })

    except Exception as error:
        connection.rollback()
        print("Update shopping item status error:", error)
        return jsonify({"error": "Unable to update shopping item status."}), 500

    finally:
        connection.close()

@shopping_bp.route("/api/active-shopping-list/items/<int:item_id>", methods=["PUT"])
def edit_active_shopping_item(item_id):

    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid request data."}), 400

    item_name = data.get("name", "").strip()
    quantity = data.get("quantity", "").strip()

    if len(item_name) < 3:
        return jsonify({"error": "Food item must contain at least 3 characters."}), 400

    user_id = session["user_id"]
    connection = get_db_connection()

    try:
        result = connection.execute("""
            UPDATE active_shopping_items AS items
            SET item_name = %s,
                quantity = %s
            FROM active_shopping_lists AS lists
            WHERE items.item_id = %s
              AND items.list_id = lists.list_id
              AND lists.user_id = %s
            RETURNING items.item_id, items.food_id,
                      items.item_name, items.quantity,
                      items.is_completed
        """, (item_name, quantity, item_id, user_id)).fetchone()

        if not result:
            return jsonify({"error": "Shopping item not found."}), 404

        connection.commit()

        return jsonify({
            "message": "Shopping item updated successfully.",
            "item": {
                "id": result["item_id"],
                "food_id": result["food_id"],
                "name": result["item_name"],
                "quantity": result["quantity"],
                "completed": result["is_completed"]
            }
        })

    except Exception as error:
        connection.rollback()
        print("Edit shopping item error:", error)
        return jsonify({"error": "Unable to update shopping item."}), 500

    finally:
        connection.close()

@shopping_bp.route("/api/active-shopping-list/save", methods=["POST"])
def save_active_shopping_list():

    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    user_id = session["user_id"]
    connection = get_db_connection()

    try:
        # Step 1: Find the user's active shopping list
        result = connection.execute("""
            SELECT list_id
            FROM active_shopping_lists
            WHERE user_id = %s
        """, (user_id,)).fetchone()

        if not result:
            return jsonify({"error": "Active shopping list not found."}), 404

        list_id = result["list_id"]

        # Step 2: Check whether the list contains items
        result = connection.execute("""
            SELECT COUNT(*) AS item_count
            FROM active_shopping_items
            WHERE list_id = %s
        """, (list_id,)).fetchone()

        if result["item_count"] == 0:
            return jsonify({
                "error": "Your shopping list must contain at least one item."
            }), 400

        # Step 3: Create a shopping history record
        result = connection.execute("""
            INSERT INTO shopping_history (user_id)
            VALUES (%s)
            RETURNING history_id
        """, (user_id,)).fetchone()

        history_id = result["history_id"]

        # Step 4: Copy active items into shopping history
        result = connection.execute("""
            INSERT INTO shopping_history_items (
                history_id,
                food_id,
                item_name,
                quantity,
                is_completed
            )
            SELECT
                %s,
                food_id,
                item_name,
                quantity,
                is_completed
            FROM active_shopping_items
            WHERE list_id = %s
            RETURNING history_item_id
        """, (history_id, list_id)).fetchall()

        connection.commit()

        return jsonify({
            "message": "Shopping list saved successfully.",
            "history_id": history_id,
            "saved_items": len(result)
        })

    except Exception as error:
        connection.rollback()
        print("Save shopping list error:", error)
        return jsonify({
            "error": "Unable to save shopping list."
        }), 500

    finally:
        connection.close()

@shopping_bp.route("/api/active-shopping-list/missing-items", methods=["POST"])
def add_missing_recipe_ingredients():

    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    user_id = session["user_id"]
    data = request.get_json()

    recipe_id = data.get("recipe_id") if isinstance(data, dict) else None
    missing_ingredients = data.get("ingredients", []) if isinstance(data, dict) else []

    if not isinstance(recipe_id, int) or isinstance(recipe_id, bool) or recipe_id <= 0:
        return jsonify({"error": "Invalid recipe ID."}), 400

    if not isinstance(missing_ingredients, list) or not missing_ingredients:
        return jsonify({"error": "No missing ingredients provided."}), 400

    if not all(isinstance(name, str) and name.strip() for name in missing_ingredients):
        return jsonify({"error": "Invalid ingredient names."}), 400

    missing_ingredients = list(dict.fromkeys(
        name.strip() for name in missing_ingredients
    ))

    connection = get_db_connection()

    try:
        # Get or create the user's active shopping list
        connection.execute("""
            INSERT INTO active_shopping_lists (user_id)
            VALUES (%s)
            ON CONFLICT (user_id) DO NOTHING
        """, (user_id,))

        result = connection.execute("""
            SELECT list_id
            FROM active_shopping_lists
            WHERE user_id = %s
        """, (user_id,)).fetchone()

        list_id = result["list_id"]
        # Retrieve the requested missing ingredients from the recipe
        recipe_ingredients = connection.execute("""
            SELECT ingredient_name, amount
            FROM recipe_ingredients
            WHERE recipe_id = %s
            AND ingredient_name = ANY(%s)
        """, (recipe_id, missing_ingredients)).fetchall()

        added_count = 0
        updated_count = 0

        # Retrieve existing shopping list items
        existing_items = connection.execute("""
            SELECT item_id, item_name, quantity
            FROM active_shopping_items
            WHERE list_id = %s
        """, (list_id,)).fetchall()

        for ingredient in recipe_ingredients:

            name = ingredient["ingredient_name"]
            quantity = ingredient["amount"]

            normalized_name = normalize_shopping_ingredient(name)

            # Find an existing item, treating singular and plural names equally
            existing = next(
                (
                    item for item in existing_items
                    if normalize_shopping_ingredient(item["item_name"]) == normalized_name
                ),
                None
            )

            if existing:
                new_quantity = double_ingredient_quantity(
                    existing["quantity"]
                )

                connection.execute("""
                    UPDATE active_shopping_items
                    SET quantity = %s
                    WHERE item_id = %s
                """, (new_quantity, existing["item_id"]))

                updated_count += 1
                continue
            connection.execute("""
                INSERT INTO active_shopping_items
                    (list_id, item_name, quantity)
                VALUES (%s, %s, %s)
            """, (list_id, name, quantity or ""))

            added_count += 1

        connection.commit()

        return jsonify({
            "success": True,
            "added_count": added_count,
            "updated_count": updated_count
        })

    except Exception as error:
        connection.rollback()
        print("Add missing ingredients error:", error)
        return jsonify({
            "error": "Unable to add missing ingredients."
        }), 500

    finally:
        connection.close()

