
from flask import Blueprint, request, redirect, session
from database import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]
    connection = get_db_connection()
    user = connection.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,)
    ).fetchone()
    connection.close()

    if user and check_password_hash(user["password"], password):
        session["email"] = email
        return redirect("/dashboard")
    return "Invalid email or password!"

@auth_bp.route("/register", methods=["POST"])
def register():
    email = request.form["email"]
    password = request.form["password"]

    # Generate password hash
    password_hash = generate_password_hash(password)
    connection = get_db_connection()

    try:
        connection.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (email, password_hash)
        )
        connection.commit()

    except Exception as e:
        connection.close()
        if "UNIQUE constraint failed" in str(e):
            return "Email already registered. Please use another email."
        raise

    connection.close()
    session["email"] = email
    return redirect("/dashboard")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")
