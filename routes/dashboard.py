from flask import Blueprint, render_template, redirect, session
from flask import Blueprint, render_template, redirect, session, jsonify
from database import get_db_connection

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def home():
    return render_template("index.html")


@dashboard_bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/")

    return render_template("dashboard.html")

@dashboard_bp.route("/api/expiring-soon")
def get_expiring_soon():

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
                        expiration_date,
                        ROW_NUMBER() OVER (
                            ORDER BY inventory_id ASC
                        ) AS s_no
                    FROM inventory
                    WHERE user_id = %s
                )

                SELECT
                    inventory_id,
                    item_name,
                    expiration_date,
                    (expiration_date - CURRENT_DATE) AS days_left,
                    s_no
                FROM ranked_inventory
                WHERE expiration_date BETWEEN CURRENT_DATE
                    AND CURRENT_DATE + 7
                ORDER BY expiration_date ASC, inventory_id ASC
            """, (session["user_id"],))

            rows = result.fetchall()

        items = []

        for item in rows:
            items.append({
                "id": item["inventory_id"],
                "s_no": item["s_no"],
                "item_name": item["item_name"],
                "days_left": item["days_left"]
            })

        return jsonify({
            "success": True,
            "items": items
        })

    except Exception as error:
        print("Error retrieving expiring items:", error)

        return jsonify({
            "success": False,
            "message": "Unable to retrieve expiring items."
        }), 500
