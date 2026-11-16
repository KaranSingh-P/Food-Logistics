from flask import Flask, session
from database import init_db, get_db_connection

from routes.auth import auth_bp
from routes.settings import settings_bp
from routes.dashboard import dashboard_bp
from routes.inventory import inventory_bp
from routes.recipes import recipes_bp
from routes.shopping import shopping_bp

app = Flask(__name__)

app.secret_key = "my-secret-key"

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(inventory_bp)
app.register_blueprint(recipes_bp)
app.register_blueprint(shopping_bp)


@app.context_processor
def inject_global_settings():

    user_id = session.get("user_id")

    if not user_id:
        return {
            "navbar_username": "",
            "current_theme": "light"
        }

    with get_db_connection() as connection:

        user = connection.execute(
            """
            SELECT u.email, us.username, us.theme
            FROM users u
            JOIN user_settings us
                ON u.user_id = us.user_id
            WHERE u.user_id = %s
            """,
            (user_id,)
        ).fetchone()

    if not user:
        return {
            "navbar_username": "",
            "current_theme": "light"
        }

    username = user["username"].strip()

    return {
        "navbar_username": username if username else user["email"],
        "current_theme": user["theme"]
    }
if __name__ == "__main__":
    init_db()
    app.run(debug=True)