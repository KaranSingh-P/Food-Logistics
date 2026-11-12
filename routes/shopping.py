from flask import Blueprint, render_template, redirect, session, jsonify, request

shopping_bp = Blueprint("shopping", __name__)

@shopping_bp.route("/shopping-list")
def shopping_list():
    if "user_id" not in session:
        return redirect("/")

    return render_template("shopping-list.html")

shopping_history = [
    {
        "id": 1,
        "name": "Weekly Grocery Shopping",
        "date": "Today",
        "item_count": 12
    },
    {
        "id": 2,
        "name": "Quick Essentials",
        "date": "Today",
        "item_count": 4
    },
    {
        "id": 3,
        "name": "Monthly Grocery Shopping",
        "date": "October 09, 2026",
        "item_count": 20
    },
    {
        "id": 4,
        "name": "Weekend Shopping List",
        "date": "October 09, 2026",
        "item_count": 8
    }
]

@shopping_bp.route("/api/shopping-history", methods=["GET"])
def get_shopping_history():

    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    return jsonify({"shopping_history": shopping_history})

generated_shopping_list = {
    "id": 1,
    "name": "Weekly Grocery Shopping",
    "description": "A grocery list of food items based on your selected categories and inventory needs.",
    "shopping_type": "Weekly Shopping",

    "items": [
        {"id": 1, "name": "Milk", "quantity": "2 litres", "completed": True},
        {"id": 2, "name": "Bread", "quantity": "2 packets", "completed": True},
        {"id": 3, "name": "Eggs", "quantity": "12 pieces", "completed": True},
        {"id": 4, "name": "Rice", "quantity": "2 kg", "completed": False},
        {"id": 5, "name": "Potatoes", "quantity": "1 kg", "completed": False},
        {"id": 6, "name": "Tomatoes", "quantity": "1 kg", "completed": False},
        {"id": 7, "name": "Onions", "quantity": "1 kg", "completed": False},
        {"id": 8, "name": "Cooking Oil", "quantity": "1 litre", "completed": False},
        {"id": 9, "name": "Sugar", "quantity": "1 kg", "completed": False},
        {"id": 10, "name": "Tea Powder", "quantity": "250 g", "completed": False},
        {"id": 11, "name": "Apples", "quantity": "1 kg", "completed": False},
        {"id": 12, "name": "Biscuits", "quantity": "2 packets", "completed": False}
    ]
}


@shopping_bp.route("/api/generated-shopping-list", methods=["GET"])
def get_generated_shopping_list():

    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    return jsonify({"shopping_list": generated_shopping_list})