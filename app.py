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