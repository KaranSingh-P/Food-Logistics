import json

from flask import Blueprint, request, redirect, session, render_template, flash
from werkzeug.security import generate_password_hash
from database import get_db_connection

settings_bp = Blueprint("settings", __name__)


@settings_bp.route("/user-settings", methods=["GET", "POST"])
def user_settings_page():

    if "user_id" not in session:
        return redirect("/")

    user_id = session["user_id"]

    # Retrieve existing user data from PostgreSQL.
    with get_db_connection() as connection:

        # Retrieve user's email.
        user = connection.execute(
            """
            SELECT email
            FROM users
            WHERE user_id = %s
            """,
            (user_id,)
        ).fetchone()

        # Retrieve username and theme.
        settings_record = connection.execute(
            """
            SELECT username, theme
            FROM user_settings
            WHERE user_id = %s
            """,
            (user_id,)
        ).fetchone()

        # Check whether the user has configured Account Recovery.
        security_record = connection.execute(
            """
            SELECT security_question
            FROM user_security
            WHERE user_id = %s
            """,
            (user_id,)
        ).fetchone()

        # Retrieve all available allergies.
        allergy_records = connection.execute(
            """
            SELECT allergy_id, allergy_name
            FROM allergies
            ORDER BY allergy_name
            """
        ).fetchall()

        # Retrieve this user's selected allergies.
        selected_records = connection.execute(
            """
            SELECT a.allergy_name
            FROM user_allergies ua
            JOIN allergies a
                ON ua.allergy_id = a.allergy_id
            WHERE ua.user_id = %s
            ORDER BY a.allergy_name
            """,
            (user_id,)
        ).fetchall()

        recovery_configured = security_record is not None

    if not user or not settings_record:
        return "User settings could not be found.", 404

    email = user["email"]

    # Available allergy names and their corresponding IDs.
    available_allergies = [
        allergy["allergy_name"] for allergy in allergy_records
    ]

    allergy_ids_by_name = {
        allergy["allergy_name"]: allergy["allergy_id"]
        for allergy in allergy_records
    }

    # Retrieve saved username and theme.
    settings = {
        "username": settings_record["username"],
        "theme": settings_record["theme"],
        "allergies": [
            allergy["allergy_name"] for allergy in selected_records
        ]
    }

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        theme = request.form.get("theme", "light")
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm-password", "")

        # Read and validate submitted allergies.
        try:
            allergies = json.loads(request.form.get("allergies", "[]"))

            if not isinstance(allergies, list):
                raise ValueError()

            if not all(
                isinstance(item, str) and item in allergy_ids_by_name
                for item in allergies
            ):
                raise ValueError()

            allergies = list(dict.fromkeys(allergies))

        except (ValueError, TypeError):
            flash("Invalid allergy selection.", "error")

            return render_template(
                "user-setting.html",
                email=email,
                settings=settings,
                available_allergies=available_allergies,
                recovery_configured=recovery_configured
            )

        # Validate theme.
        if theme not in ["light", "dark"]:
            flash("Invalid theme selection.", "error")

            return render_template(
                "user-setting.html",
                email=email,
                settings={
                    "username": username,
                    "theme": settings["theme"],
                    "allergies": allergies
                },
                available_allergies=available_allergies,
                recovery_configured=recovery_configured
            )

        # Check password confirmation.
        if password != confirm_password:
            flash("Passwords do not match!", "error")


        # Read Account Recovery fields.
        security_question = request.form.get("security-question", "").strip()
        security_answer = request.form.get("security-answer", "").strip()
        security_pin = request.form.get("security-pin", "")
        confirm_security_pin = request.form.get("confirm-security-pin", "")

        # Available security questions.
        allowed_security_questions = {
            "first_school",
            "first_pet",
            "birth_city",
            "childhood_friend",
            "favourite_food"
        }

        # Check whether recovery details have been entered.
        recovery_fields = [
            security_question,
            security_answer,
            security_pin,
            confirm_security_pin
        ]

        filled_fields = sum(bool(value) for value in recovery_fields)

        # All recovery fields must be filled or all must be empty.
        if filled_fields not in [0, 4]:
            flash("Please complete all Account Recovery fields.", "error")

            return render_template(
                "user-setting.html",
                email=email,
                settings={
                    "username": username,
                    "theme": theme,
                    "allergies": allergies
                },
                available_allergies=available_allergies,
                recovery_configured=recovery_configured
            )


        # Validate recovery details if provided.
        if filled_fields == 4:

            if security_question not in allowed_security_questions:
                flash("Please select a valid security question.", "error")

                return render_template(
                    "user-setting.html",
                    email=email,
                    settings={
                        "username": username,
                        "theme": theme,
                        "allergies": allergies
                    },
                    available_allergies=available_allergies,
                    recovery_configured=recovery_configured
                )

            if not security_answer:
                flash("Security answer cannot be empty.", "error")

                return render_template(
                    "user-setting.html",
                    email=email,
                    settings={
                        "username": username,
                        "theme": theme,
                        "allergies": allergies
                    },
                    available_allergies=available_allergies,
                    recovery_configured=recovery_configured
                )

            if len(security_pin) != 6 or not security_pin.isdigit():
                flash("Security PIN must contain exactly 6 digits.", "error")

                return render_template(
                    "user-setting.html",
                    email=email,
                    settings={
                        "username": username,
                        "theme": theme,
                        "allergies": allergies
                    },
                    available_allergies=available_allergies,
                    recovery_configured=recovery_configured
                )

            if security_pin != confirm_security_pin:
                flash("Security PINs do not match!", "error")

                return render_template(
                    "user-setting.html",
                    email=email,
                    settings={
                        "username": username,
                        "theme": theme,
                        "allergies": allergies
                    },
                    available_allergies=available_allergies,
                    recovery_configured=recovery_configured
                )

        # Continue to database saving if validation succeeds.
        print("DEBUG: Reached database-saving section.")
        # Convert allergy names into their database IDs.
        allergy_ids = [
            allergy_ids_by_name[name] for name in allergies
        ]

        # Save all settings in PostgreSQL.
        with get_db_connection() as connection:

            # Save username and theme.
            connection.execute(
                """
                UPDATE user_settings
                SET username = %s,
                    theme = %s
                WHERE user_id = %s
                """,
                (username, theme, user_id)
            )

            # Update password if provided.
            if password:
                password_hash = generate_password_hash(password)

                connection.execute(
                    """
                    UPDATE users
                    SET password_hash = %s
                    WHERE user_id = %s
                    """,
                    (password_hash, user_id)
                )

            # Save Account Recovery details if all fields were provided.
            if filled_fields == 4:

                # Normalize the answer so capitalization doesn't matter.
                normalized_answer = security_answer.strip().casefold()

                answer_hash = generate_password_hash(normalized_answer)
                pin_hash = generate_password_hash(security_pin)

                connection.execute(
                    """
                    INSERT INTO user_security (
                        user_id,
                        security_question,
                        security_answer_hash,
                        security_pin_hash,
                        updated_at
                    )
                    VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)

                    ON CONFLICT (user_id)
                    DO UPDATE SET
                        security_question = EXCLUDED.security_question,
                        security_answer_hash = EXCLUDED.security_answer_hash,
                        security_pin_hash = EXCLUDED.security_pin_hash,
                        updated_at = CURRENT_TIMESTAMP
                    """,
                    (
                        user_id,
                        security_question,
                        answer_hash,
                        pin_hash
                    )
                )



            # Remove previous allergy selections.
            connection.execute(
                """
                DELETE FROM user_allergies
                WHERE user_id = %s
                """,
                (user_id,)
            )

            # Insert newly selected allergies.
            if allergy_ids:
                connection.cursor().executemany(
                    """
                    INSERT INTO user_allergies (user_id, allergy_id)
                    VALUES (%s, %s)
                    """,
                    [
                        (user_id, allergy_id)
                        for allergy_id in allergy_ids
                    ]
                )

        flash("Settings saved successfully!", "success")

        return redirect("/user-settings")

    return render_template(
        "user-setting.html",
        email=email,
        settings=settings,
        available_allergies=available_allergies,
        recovery_configured=recovery_configured
    )