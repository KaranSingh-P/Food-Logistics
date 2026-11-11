
from flask import Blueprint, jsonify, render_template, request, redirect, session

inventory_bp = Blueprint("inventory", __name__)


# Temporary inventory data
inventory_items = [
    {
        "id": 1,
        "name": "Food",
        "tag": "Perishable",
        "purchase_date": "01 Jan 2026",
        "expiration_date": "01 Jan 2026"
    },
    {
        "id": 2,
        "name": "Canned Beans",
        "tag": "Canned",
        "purchase_date": "05 Jan 2026",
        "expiration_date": "05 Jan 2027"
    },
    {
        "id": 3,
        "name": "Milk",
        "tag": "Perishable",
        "purchase_date": "10 Jan 2026",
        "expiration_date": "17 Jan 2026"
    },
    # More Items will go here.
]


@inventory_bp.route("/inventory")
def inventory():
    if "email" not in session:
        return redirect("/")

    return render_template("inventory.html")


@inventory_bp.route("/api/inventory")
def get_inventory():

    # Get pagination parameters
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    # Prevent invalid values
    if page < 1:
        page = 1

    if per_page not in [20, 50, 100]:
        per_page = 20

    # Total number of inventory items
    total = len(inventory_items)

    # Calculate total pages
    total_pages = (total + per_page - 1) // per_page

    # Prevent requesting a page beyond the last page
    if total_pages > 0 and page > total_pages:
        page = total_pages

    # Calculate which items belong to this page
    start = (page - 1) * per_page
    end = start + per_page

    page_items = inventory_items[start:end]

    # Add S.No for the current page
    for index, item in enumerate(page_items):
        item["s_no"] = start + index + 1

    return jsonify({
        "items": page_items,
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages
    })


@inventory_bp.route("/api/remove-item-inventory", methods=["POST"])
def remove_item_inventory():

    data = request.get_json()

    item_id = data.get("id")

    if item_id is None:
        return jsonify({
            "success": False,
            "message": "Item ID is required"
        }), 400

    item = next(
        (item for item in inventory_items if item["id"] == item_id),
        None
    )

    if item is None:
        return jsonify({
            "success": False,
            "message": "Item not found"
        }), 404

    inventory_items.remove(item)

    return jsonify({
        "success": True,
        "message": "Item removed successfully"
    })
