from flask import Flask, jsonify, render_template, request, redirect, session
import sqlite3
import os


app = Flask(__name__)

app.secret_key = "my-secret-key"
DATABASE = os.path.join(os.path.dirname(__file__), "users.db")

def init_db():
    connection = sqlite3.connect(DATABASE)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]

    connection = sqlite3.connect(DATABASE)

    user = connection.execute(
        "SELECT * FROM users WHERE email = ? AND password = ?",
        (email, password)
    ).fetchone()

    connection.close()

    if user:
        session["email"] = email
        return redirect("/dashboard")

    return "Invalid email or password!"


@app.route("/register", methods=["POST"])
def register():
    email = request.form["email"]
    password = request.form["password"]

    connection = sqlite3.connect(DATABASE)

    try:
        connection.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (email, password)
        )

        connection.commit()

    except sqlite3.IntegrityError:
        connection.close()
        return "Email already registered. Please use another email."

    connection.close()

    session["email"] = email

    return redirect("/dashboard")


@app.route("/dashboard")
def dashboard():
    if "email" not in session:
        return redirect("/")

    return render_template("dashboard.html")


@app.route("/inventory")
def inventory():
    if "email" not in session:
        return redirect("/")

    return render_template("inventory.html")

inventory = [
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

@app.route("/api/inventory")
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
    total = len(inventory)

    # Calculate total pages
    total_pages = (total + per_page - 1) // per_page

    # If requested page is beyond the last page
    if total_pages > 0 and page > total_pages:
        page = total_pages

    # Calculate which items belong to this page
    start = (page - 1) * per_page
    end = start + per_page

    page_items = inventory[start:end]

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

@app.route("/api/remove-item-inventory", methods=["POST"])
def remove_item_inventory():
    data = request.get_json()

    item_id = data.get("id")

    if item_id is None:
        return jsonify({
            "success": False,
            "message": "Item ID is required"
        }), 400

    item = next(
        (item for item in inventory if item["id"] == item_id),
        None
    )

    if item is None:
        return jsonify({
            "success": False,
            "message": "Item not found"
        }), 404

    inventory.remove(item)

    return jsonify({
        "success": True,
        "message": "Item removed successfully"
    })

@app.route("/recipe-generation")
def recipe_generation():
    if "email" not in session:
        return redirect("/")

    return render_template("recipe-generation.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/api/allergen-alerts")
def allergen_alerts():
    allergen_data= [
        {"s_no": 1, "item_name": "Item 1", "allergy": "Peanuts"},
        {"s_no": 2, "item_name": "Item 2", "allergy": "Milk"},
        {"s_no": 3, "item_name": "Item 3", "allergy": "Gluten"},
    ]

    return jsonify(allergen_data)

@app.route("/api/expiring-soon")
def expiring_soon():

    expiring_data = [
        {"id": 17, "s_no": 1, "item_name": "Milk", "days_left": 2},
        {"id": 23, "s_no": 2, "item_name": "Bread", "days_left": 4},
    ]

    return jsonify(expiring_data)

@app.route("/api/remove-item", methods=["POST"])
def remove_item():
    data = request.get_json()

    item_id = data["id"]

    #TO-DO Delete item from database here

    return jsonify({"success": True})


if __name__ == "__main__":
    init_db()
    app.run(debug=True)