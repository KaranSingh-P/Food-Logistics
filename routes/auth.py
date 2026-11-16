
from flask import Blueprint, request, redirect, session, jsonify
from database import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg

auth_bp = Blueprint("auth", __name__)



@auth_bp.route("/login", methods=["POST"])
def login():
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    if not email or not password:
        return jsonify({
            "success": False,
            "message": "Please enter both email and password."
        }), 400

    with get_db_connection() as connection:
        user = connection.execute(
            """
            SELECT user_id, password_hash
            FROM users
            WHERE email = %s
            """,
            (email,)
        ).fetchone()

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({
            "success": False,
            "message": "Invalid email or password."
        }), 401

    session.clear()
    session["user_id"] = user["user_id"]

    return jsonify({
        "success": True,
        "redirect": "/dashboard"
    })


@auth_bp.route("/register", methods=["POST"])
def register():
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    if not email or not password:
        return jsonify({
            "success": False,
            "message": "Please enter both email and password."
        }), 400

    if len(password) < 8:
        return jsonify({
            "success": False,
            "message": "Password must be at least 8 characters long."
        }), 400

    if len(password) > 128:
        return jsonify({
            "success": False,
            "message": "Password cannot exceed 128 characters."
        }), 400

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
        return jsonify({
            "success": False,
            "message": "This email is already registered. Please use another email."
        }), 409

    return jsonify({
        "success": True,
        "redirect": "/dashboard"
    })



@auth_bp.route("/api/recovery-question", methods=["POST"])
def get_recovery_question():

    email = request.json.get("email", "").strip()

    if not email:
        return jsonify({
            "success": False,
            "message": "Please enter your registered email."
        }), 400

    with get_db_connection() as connection:

        user = connection.execute(
            """
            SELECT us.security_question
            FROM users u
            JOIN user_security us
                ON u.user_id = us.user_id
            WHERE LOWER(u.email) = LOWER(%s)
            """,
            (email,)
        ).fetchone()

    if not user:
        return jsonify({
            "success": False,
            "message": "No recovery details found for this email."
        }), 404

    questions = {
        "first_school": "What was the name of your first school?",
        "first_pet": "What was the name of your first pet?",
        "birth_city": "In which city were you born?",
        "childhood_friend": "What was the name of your childhood best friend?",
        "favourite_food": "What was your favourite childhood food?"
    }

    question_text = questions.get(user["security_question"])

    if not question_text:
        return jsonify({
            "success": False,
            "message": "Invalid security question configuration."
        }), 500

    return jsonify({
        "success": True,
        "question": question_text
    })


@auth_bp.route("/api/verify-recovery", methods=["POST"])
def verify_recovery():

    data = request.get_json() or {}

    email = data.get("email", "").strip()
    answer = data.get("answer", "").strip().casefold()
    pin = data.get("pin", "")

    if not email or not answer or not pin:
        return jsonify({
            "success": False,
            "message": "Please complete all recovery fields."
        }), 400

    with get_db_connection() as connection:
        user = connection.execute(
            """
            SELECT u.user_id,
                us.security_answer_hash,
                us.security_pin_hash
            FROM users u
            JOIN user_security us
                ON u.user_id = us.user_id
            WHERE LOWER(u.email) = LOWER(%s)
            """,
            (email,)
        ).fetchone()

    if not user:
        return jsonify({
            "success": False,
            "message": "Invalid recovery details."
        }), 400

    answer_valid = check_password_hash(
        user["security_answer_hash"], answer
    )

    pin_valid = check_password_hash(
        user["security_pin_hash"], pin
    )

    if not answer_valid or not pin_valid:
        return jsonify({
            "success": False,
            "message": "Incorrect security answer or PIN."
        }), 401

    # Log the user into their existing account.
    session.clear()
    session["user_id"] = user["user_id"]

    return jsonify({
        "success": True,
        "message": "Verification successful. Logging you in...",
        "redirect": "/dashboard"
    })



@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")
