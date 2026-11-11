
import json

from flask import Blueprint, request, redirect, session, render_template, flash
from database import get_db_connection

settings_bp = Blueprint("settings", __name__)

# Temporary storage until we implement the proper database structure.
user_settings = {}

AVAILABLE_ALLERGIES = [
    "Peanuts", "Tree Nuts", "Milk", "Eggs", "Wheat", "Soy",
    "Fish", "Shellfish", "Sesame", "Gluten", "Mustard", "Corn",
    "Strawberries", "Chocolate"
]


@settings_bp.route("/user-settings", methods=["GET", "POST"])
def user_settings_page():

    if "email" not in session:
        return redirect("/")

    email = session["email"]

    settings = user_settings.get(email, {
        "username": "",
        "theme": "light",
        "allergies": []
    })

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        theme = request.form.get("theme", "light")
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm-password", "")

        # Read allergies submitted by JavaScript.
        try:
            allergies = json.loads(request.form.get("allergies", "[]"))

            if not isinstance(allergies, list):
                raise ValueError()

            if not all(
                isinstance(item, str) and item in AVAILABLE_ALLERGIES
                for item in allergies
            ):
                raise ValueError()

            allergies = list(dict.fromkeys(allergies))

        except (ValueError, TypeError):
            flash("Invalid allergy selection.", "error")
            return render_template(
                "user-setting.html",
                email=email,
                settings=settings
            )

        if theme not in ["light", "dark"]:
            flash("Invalid theme selection.", "error")
            return render_template(
                "user-setting.html",
                email=email,
                settings=settings
            )

        # Check password confirmation.
        if password != confirm_password:
            flash("Passwords do not match!", "error")

            return render_template(
                "user-setting.html",
                email=email,
                settings={
                    "username": username,
                    "theme": theme,
                    "allergies": allergies
                }
            )

        # Update password in the existing SQLite database.
        if password:
            connection = get_db_connection()

            connection.execute("""
                UPDATE users
                SET password = ?
                WHERE email = ?
            """, (password, email))

            connection.commit()
            connection.close()

        # Save the other settings temporarily.
        user_settings[email] = {
            "username": username,
            "theme": theme,
            "allergies": allergies
        }

        flash("Settings saved successfully!", "success")

        return redirect("/user-settings")

    return render_template(
        "user-setting.html",
        email=email,
        settings=settings
    )
