
from flask import Blueprint, request, redirect, session
from database import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]

    with get_db_connection() as connection:
        user = connection.execute(
            """
            SELECT user_id, password_hash
            FROM users
            WHERE email = %s
            """,
            (email,)
        ).fetchone()

    if user and check_password_hash(user["password_hash"], password):
        session.clear()
        session["user_id"] = user["user_id"]
        return redirect("/dashboard")

    return "Invalid email or password!"



@auth_bp.route("/register", methods=["POST"])
def register():
    email = request.form["email"]
    password = request.form["password"]
    password_hash = generate_password_hash(password)

    try:
        with get_db_connection() as connection:
            user = connection.execute(
                """
                INSERT INTO users (email, password_hash)
                VALUES (%s, %s)
                RETURNING user_id
                """,
                (email, password_hash)
            ).fetchone()
            # Create default settings for the new user.
            connection.execute(
                """
                INSERT INTO user_settings (user_id)
                VALUES (%s)
                """,
                (user["user_id"],)
            )
        session.clear()
        session["user_id"] = user["user_id"]

    except psycopg.errors.UniqueViolation:
        return "Email already registered. Please use another email."
    return redirect("/dashboard")

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")
