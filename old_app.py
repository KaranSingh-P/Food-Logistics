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

recipe_history = [
    {
        "id": 1,
        "name": "Creamy Garlic Chicken Pasta",
        "date": "10 Nov 2026",
        "time": "8:42 PM"
    },
    {
        "id": 2,
        "name": "Vegetable Fried Rice",
        "date": "10 Nov 2026",
        "time": "3:18 PM"
    },
    {
        "id": 3,
        "name": "Paneer Butter Masala",
        "date": "09 Nov 2026",
        "time": "7:30 PM"
    },
    {
        "id": 4,
        "name": "Vegetable Sandwich",
        "date": "08 Nov 2026",
        "time": "11:15 AM"
    }
]

@app.route("/api/recipe-history",methods=["GET"])
def get_recipe_history():

    if "email" not in session:
        return jsonify({"error": "Not logged in"}), 401

    return jsonify({
        "recipes": recipe_history
    })

@app.route("/api/generated-recipe", methods=["POST"])
def generate_recipe():
    if "email" not in session:
        return jsonify({"error": "Not logged in"}), 401

    preferences = request.get_json()
    if not preferences:
        return jsonify({"error": "No preferences received"}), 400
    # print("Received Recipe Preferences:", preferences)
    return jsonify({"recipe": generated_recipe})

generated_recipe = {
    "id": 1,
    "name": "Creamy Garlic Chicken Pasta",
    "description": "A creamy and comforting chicken pasta made with garlic, herbs, and Parmesan cheese.",
    "preparation_time": "35 minutes",
    "servings": 4,

    "ingredients": [
        {
            "name": "Chicken Breast",
            "amount": "500 g",
            "available": True
        },
        {
            "name": "Penne Pasta",
            "amount": "300 g",
            "available": True
        },
        {
            "name": "Garlic",
            "amount": "4 cloves",
            "available": True
        },
        {
            "name": "Heavy Cream",
            "amount": "200 ml",
            "available": False
        },
        {
            "name": "Parmesan Cheese",
            "amount": "75 g",
            "available": False
        },
        {
            "name": "Olive Oil",
            "amount": "2 tbsp",
            "available": True
        },
        {
            "name": "Italian Herbs",
            "amount": "1 tsp",
            "available": True
        },
        {
            "name": "Salt & Pepper",
            "amount": "To taste",
            "available": True
        }
    ],

    "instructions": [
        {
            "title": "Cook the pasta",
            "description": "Bring a large pot of salted water to a boil. Cook the pasta according to the package instructions until al dente. Drain and set aside."
        },
        {
            "title": "Prepare the chicken",
            "description": "Cut the chicken breast into bite-sized pieces. Season with salt, pepper, and Italian herbs."
        },
        {
            "title": "Cook the chicken",
            "description": "Heat olive oil in a large pan over medium-high heat. Add the chicken and cook until golden brown and fully cooked."
        },
        {
            "title": "Prepare the sauce",
            "description": "Add minced garlic and cook for one minute. Add the heavy cream and Parmesan cheese. Stir until the sauce becomes smooth and creamy."
        },
        {
            "title": "Combine the ingredients",
            "description": "Add the cooked pasta and chicken to the sauce. Toss everything together until evenly coated."
        },
        {
            "title": "Serve",
            "description": "Divide the pasta between four plates. Garnish with Parmesan cheese and fresh herbs. Serve immediately."
        }
    ]
}

@app.route("/api/generated-recipe", methods=["GET"])
def get_generated_recipe():

    if "email" not in session:
        return jsonify({"error": "Not logged in"}), 401

    return jsonify({
        "recipe": generated_recipe
    })


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