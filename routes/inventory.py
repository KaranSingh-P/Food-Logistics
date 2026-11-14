from flask import Blueprint, jsonify, render_template, request, redirect, session
from datetime import datetime
from database import get_db_connection
inventory_bp = Blueprint("inventory", __name__)

@inventory_bp.route("/api/add-item-inventory", methods=["POST"])
def add_item_inventory():
    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "Please log in first."
        }), 401
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "No valid item data received."
        }), 400
    
    item_name = data.get("name", "")
    if not isinstance(item_name, str):
        item_name = ""
    item_name = item_name.strip()

    category = data.get("category", "")
    purchase_date = data.get("purchase_date", "")
    expiration_date = data.get("expiration_date", "")
    if len(item_name) < 3:
        return jsonify({
            "success": False,
            "message": "Food name must contain at least 3 characters."
        }), 400
    allowed_categories = {
        "perishable",
        "highly-perishable",
        "semi-perishable",
        "non-perishable",
        "canned",
        "frozen",
        "dehydrated",
        "fermented"
    }
    if category not in allowed_categories:
        return jsonify({
            "success": False,
            "message": "Invalid food category."
        }), 400
    try:
        purchase = datetime.strptime(
            purchase_date, "%Y-%m-%d"
        ).date()
        expiry = datetime.strptime(
            expiration_date, "%Y-%m-%d"
        ).date()
    except (ValueError, TypeError):
        return jsonify({
            "success": False,
            "message": "Please provide valid dates."
        }), 400
    if expiry < purchase:
        return jsonify({
            "success": False,
            "message": "Expiration date cannot be earlier than purchase date."
        }), 400
    try:
        with get_db_connection() as connection:
            result = connection.execute("""
                INSERT INTO inventory (
                    user_id,
                    item_name,
                    category,
                    purchase_date,
                    expiration_date
                )
                VALUES (%s, %s, %s, %s, %s)
                RETURNING inventory_id
            """, (
                session["user_id"],
                item_name,
                category,
                purchase,
                expiry
            ))
            new_item = result.fetchone()
        return jsonify({
            "success": True,
            "message": "Item successfully added to inventory.",
            "item": {
                "inventory_id": new_item["inventory_id"],
                "name": item_name,
                "category": category,
                "purchase_date": purchase.isoformat(),
                "expiration_date": expiry.isoformat()
            }
        }), 201
    except Exception as error:
        print("Database error while adding inventory item:", error)
        return jsonify({
            "success": False,
            "message": "Unable to save the item. Please try again."
        }), 500


@inventory_bp.route("/api/inventory-allergens")
def get_inventory_allergens():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "Please log in first."
        }), 401

    try:
        with get_db_connection() as connection:

            result = connection.execute("""
                WITH ranked_inventory AS (
                    SELECT
                        inventory_id,
                        user_id,
                        item_name,
                        ROW_NUMBER() OVER (
                            ORDER BY inventory_id ASC
                        ) AS s_no
                    FROM inventory
                    WHERE user_id = %s
                )

                SELECT
                    ri.inventory_id,
                    ri.item_name,
                    ri.s_no,
                    fs.food_id,

                    iv.verification_status,
                    verified_allergy.allergy_name AS verified_allergy,

                    detected_allergy.allergy_name AS detected_allergy

                FROM ranked_inventory ri

                LEFT JOIN food_suggestions fs
                    ON LOWER(TRIM(ri.item_name)) =
                       LOWER(TRIM(fs.food_name))

                LEFT JOIN inventory_verifications iv
                    ON ri.inventory_id = iv.inventory_id

                LEFT JOIN allergies verified_allergy
                    ON iv.allergy_id = verified_allergy.allergy_id

                LEFT JOIN food_allergens fa
                    ON fs.food_id = fa.food_id

                LEFT JOIN user_allergies ua
                    ON fa.allergy_id = ua.allergy_id
                    AND ua.user_id = ri.user_id

                LEFT JOIN allergies detected_allergy
                    ON ua.allergy_id = detected_allergy.allergy_id

                ORDER BY ri.inventory_id DESC
            """, (session["user_id"],))

            rows = result.fetchall()

        inventory_items = {}

        for row in rows:

            inventory_id = row["inventory_id"]

            if inventory_id not in inventory_items:
                inventory_items[inventory_id] = {
                    "inventory_id": inventory_id,
                    "s_no": row["s_no"],
                    "name": row["item_name"],
                    "food_id": row["food_id"],
                    "verification_status": row["verification_status"],
                    "allergens": []
                }

                if row["verified_allergy"]:
                    inventory_items[inventory_id]["allergens"].append(
                        row["verified_allergy"]
                    )

            if row["detected_allergy"]:
                inventory_items[inventory_id]["allergens"].append(
                    row["detected_allergy"]
                )

        detected = []
        unverified = []

        for item in inventory_items.values():

            status = item["verification_status"]

            if status == "allergen_free":
                continue

            if status == "allergic":
                if not item["allergens"]:
                    item["allergens"].append("Unspecified")

                detected.append(item)

            elif item["allergens"]:
                detected.append(item)

            elif item["food_id"] is None:
                unverified.append(item)
        # Retrieve the user's selected allergies for the verification dropdown
        with get_db_connection() as connection:

            result = connection.execute("""
                SELECT
                    a.allergy_id,
                    a.allergy_name
                FROM user_allergies ua
                JOIN allergies a
                    ON ua.allergy_id = a.allergy_id
                WHERE ua.user_id = %s
                ORDER BY a.allergy_name ASC
            """, (session["user_id"],))

            user_allergies = result.fetchall()

        return jsonify({
            "success": True,
            "detected": detected,
            "unverified": unverified,
            "user_allergies": user_allergies
        })

    except Exception as error:

        print("Error detecting inventory allergens:", error)

        return jsonify({
            "success": False,
            "message": "Unable to retrieve allergen information."
        }), 500

@inventory_bp.route("/api/verify-inventory-allergen", methods=["POST"])
def verify_inventory_allergen():

    # Check whether the user is logged in
    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "Please log in first."
        }), 401

    data = request.get_json()

    inventory_id = data.get("inventory_id")
    verification_status = data.get("verification_status")
    allergy_id = data.get("allergy_id")

    # Validate verification status
    if verification_status not in ["allergen_free", "allergic"]:
        return jsonify({
            "success": False,
            "message": "Invalid verification status."
        }), 400

    # Allergen-free items cannot have an allergy ID
    if verification_status == "allergen_free":
        allergy_id = None

    try:
        with get_db_connection() as connection:

            # Check whether the inventory item belongs to the logged-in user
            result = connection.execute("""
                SELECT inventory_id
                FROM inventory
                WHERE inventory_id = %s AND user_id = %s
            """, (inventory_id, session["user_id"]))

            if not result.fetchone():
                return jsonify({
                    "success": False,
                    "message": "Inventory item not found."
                }), 404

            # If a specific allergy was selected, verify that it exists
            if allergy_id is not None:

                result = connection.execute("""
                    SELECT allergy_id
                    FROM user_allergies
                    WHERE user_id = %s AND allergy_id = %s
                """, (session["user_id"], allergy_id))

                if not result.fetchone():
                    return jsonify({
                        "success": False,
                        "message": "Invalid allergy selection."
                    }), 400

            # Save or update the verification
            connection.execute("""
                INSERT INTO inventory_verifications (
                    inventory_id,
                    verification_status,
                    allergy_id
                )
                VALUES (%s, %s, %s)

                ON CONFLICT (inventory_id)
                DO UPDATE SET
                    verification_status = EXCLUDED.verification_status,
                    allergy_id = EXCLUDED.allergy_id,
                    verified_at = CURRENT_TIMESTAMP
            """, (inventory_id, verification_status, allergy_id))

        return jsonify({
            "success": True,
            "message": "Item verification saved."
        })

    except Exception as error:

        print("Error verifying inventory item:", error)

        return jsonify({
            "success": False,
            "message": "Unable to save item verification."
        }), 500

@inventory_bp.route("/api/food-suggestions")
def get_food_suggestions():
    # Check whether the user is logged in
    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "Please log in first."
        }), 401
    # Get the search query
    query = request.args.get("q", "").strip()
    # Require at least 3 characters
    if len(query) < 3:
        return jsonify({
            "suggestions": []
        })
    try:
        with get_db_connection() as connection:
            result = connection.execute("""
                SELECT food_name, category
                FROM food_suggestions
                WHERE food_name ILIKE %s
                ORDER BY food_name ASC
                LIMIT 10
            """, (f"%{query}%",))
            rows = result.fetchall()
        suggestions = []
        for item in rows:
            suggestions.append({
                "name": item["food_name"],
                "category": item["category"]
            })
        return jsonify({
            "suggestions": suggestions
        })
    except Exception as error:
        print("Database error while retrieving food suggestions:", error)
        return jsonify({
            "success": False,
            "message": "Unable to retrieve food suggestions."
        }), 500
    
@inventory_bp.route("/inventory")
def inventory():
    if "user_id" not in session:
        return redirect("/")

    return render_template("inventory.html")


@inventory_bp.route("/api/inventory")
def get_inventory():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "Please log in first."
        }), 401

    # Pagination parameters
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    if page < 1:
        page = 1

    if per_page not in [20, 50, 100]:
        per_page = 20

    # Sorting parameters
    sort_by = request.args.get("sort_by", "id")
    sort_order = request.args.get("sort_order", "desc")

    # Only allow specific columns
    allowed_columns = {
        "id": "inventory_id",
        "name": "item_name",
        "expiration": "expiration_date"
    }

    if sort_by not in allowed_columns:
        sort_by = "id"

    if sort_order not in ["asc", "desc"]:
        sort_order = "desc"

    order_column = allowed_columns[sort_by]

    user_id = session["user_id"]

    try:
        with get_db_connection() as connection:

            # Get total number of items
            result = connection.execute("""
                SELECT COUNT(*) AS total
                FROM inventory
                WHERE user_id = %s
            """, (user_id,))

            total = result.fetchone()["total"]

            total_pages = (total + per_page - 1) // per_page

            if total_pages > 0 and page > total_pages:
                page = total_pages

            offset = (page - 1) * per_page

            # Retrieve sorted inventory
            result = connection.execute(f"""
                SELECT
                    inventory_id,
                    item_name,
                    category,
                    purchase_date,
                    expiration_date,
                    ROW_NUMBER() OVER (
                        ORDER BY inventory_id ASC
                    ) AS s_no
                FROM inventory
                WHERE user_id = %s
                ORDER BY {order_column} {sort_order.upper()},
                         inventory_id DESC
                LIMIT %s OFFSET %s
            """, (user_id, per_page, offset))

            rows = result.fetchall()

        # Format records for JavaScript
        page_items = []

        for item in rows:
            page_items.append({
                "id": item["inventory_id"],
                "name": item["item_name"],
                "tag": item["category"].replace("-", " ").title(),
                "purchase_date": item["purchase_date"].strftime("%d %b %Y"),
                "expiration_date": item["expiration_date"].strftime("%d %b %Y"),
                "s_no": item["s_no"]
            })

        return jsonify({
            "items": page_items,
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages
        })

    except Exception as error:

        print("Database error while retrieving inventory:", error)

        return jsonify({
            "success": False,
            "message": "Unable to retrieve inventory."
        }), 500
    
@inventory_bp.route("/api/remove-item-inventory", methods=["POST"])
def remove_item_inventory():
    # Check whether the user is logged in
    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "Please log in first."
        }), 401
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Invalid request."
        }), 400
    item_id = data.get("id")
    try:
        item_id = int(item_id)
        if item_id < 1:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({
            "success": False,
            "message": "Invalid item ID."
        }), 400
    try:
        with get_db_connection() as connection:
            result = connection.execute("""
                DELETE FROM inventory
                WHERE inventory_id = %s
                AND user_id = %s
                RETURNING inventory_id
            """, (item_id, session["user_id"]))
            deleted_item = result.fetchone()
        if deleted_item is None:
            return jsonify({
                "success": False,
                "message": "Item not found."
            }), 404
        return jsonify({
            "success": True,
            "message": "Item removed successfully."
        })
    except Exception as error:
        print("Database error while removing inventory item:", error)
        return jsonify({
            "success": False,
            "message": "Unable to remove item."
        }), 500

@inventory_bp.route("/api/edit-item-inventory", methods=["POST"])
def edit_item_inventory():
    # Check whether the user is logged in
    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "Please log in first."
        }), 401
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Invalid request."
        }), 400
    # Retrieve submitted values
    item_id = data.get("id")
    item_name = data.get("name", "")
    category = data.get("category", "")
    purchase_date = data.get("purchase_date", "")
    expiration_date = data.get("expiration_date", "")
    # Validate item ID
    try:
        item_id = int(item_id)
        if item_id < 1:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({
            "success": False,
            "message": "Invalid item ID."
        }), 400
    # Validate item name
    if not isinstance(item_name, str):
        item_name = ""
    item_name = item_name.strip()
    if len(item_name) < 3:
        return jsonify({
            "success": False,
            "message": "Food name must contain at least 3 characters."
        }), 400
    # Validate category
    allowed_categories = {
        "perishable",
        "highly-perishable",
        "semi-perishable",
        "non-perishable",
        "canned",
        "frozen",
        "dehydrated",
        "fermented"
    }
    if category not in allowed_categories:
        return jsonify({
            "success": False,
            "message": "Invalid food category."
        }), 400
    # Validate dates
    try:
        purchase = datetime.strptime(
            purchase_date, "%Y-%m-%d"
        ).date()
        expiry = datetime.strptime(
            expiration_date, "%Y-%m-%d"
        ).date()
    except (ValueError, TypeError):
        return jsonify({
            "success": False,
            "message": "Please provide valid dates."
        }), 400
    if expiry < purchase:
        return jsonify({
            "success": False,
            "message": "Expiration date cannot be earlier than purchase date."
        }), 400
    # Update database
    try:
        with get_db_connection() as connection:
            result = connection.execute("""
                UPDATE inventory
                SET
                    item_name = %s,
                    category = %s,
                    purchase_date = %s,
                    expiration_date = %s
                WHERE inventory_id = %s
                AND user_id = %s
                RETURNING inventory_id
            """, (
                item_name,
                category,
                purchase,
                expiry,
                item_id,
                session["user_id"]
            ))
            updated_item = result.fetchone()
        if updated_item is None:
            return jsonify({
                "success": False,
                "message": "Item not found."
            }), 404
        return jsonify({
            "success": True,
            "message": "Item updated successfully."
        })

    except Exception as error:
        print("Database error while updating inventory item:", error)
        return jsonify({
            "success": False,
            "message": "Unable to update item."
        }), 500