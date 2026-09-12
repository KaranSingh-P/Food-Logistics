from flask import Flask, render_template, request, redirect, session
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


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")




if __name__ == "__main__":
    init_db()
    app.run(debug=True)