
from flask import Blueprint, request, redirect, session
from database import get_db_connection

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]

    connection = get_db_connection()

    user = connection.execute(
        "SELECT * FROM users WHERE email = ? AND password = ?",
        (email, password)
    ).fetchone()

    connection.close()

    if user:
        session["email"] = email
        return redirect("/dashboard")

    return "Invalid email or password!"


@auth_bp.route("/register", methods=["POST"])
def register():
    email = request.form["email"]
    password = request.form["password"]

    connection = get_db_connection()

    try:
        connection.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (email, password)
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
