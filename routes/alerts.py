
from flask import Blueprint, jsonify, request

alerts_bp = Blueprint("alerts", __name__)


@alerts_bp.route("/api/allergen-alerts")
def allergen_alerts():

    allergen_data = [
        {"s_no": 1, "item_name": "Item 1", "allergy": "Peanuts"},
        {"s_no": 2, "item_name": "Item 2", "allergy": "Milk"},
        {"s_no": 3, "item_name": "Item 3", "allergy": "Gluten"},
    ]

    return jsonify(allergen_data)


@alerts_bp.route("/api/expiring-soon")
def expiring_soon():

    expiring_data = [
        {"id": 17, "s_no": 1, "item_name": "Milk", "days_left": 2},
        {"id": 23, "s_no": 2, "item_name": "Bread", "days_left": 4},
    ]

    return jsonify(expiring_data)


@alerts_bp.route("/api/remove-item", methods=["POST"])
def remove_item():

    data = request.get_json()

    item_id = data["id"]

    # TODO: Delete item from database here.

    return jsonify({"success": True})
