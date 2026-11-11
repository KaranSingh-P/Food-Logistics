from flask import Flask, session
from database import init_db

from routes.auth import auth_bp
from routes.settings import settings_bp, user_settings
from routes.dashboard import dashboard_bp
from routes.inventory import inventory_bp
from routes.recipes import recipes_bp
from routes.alerts import alerts_bp
from routes.shopping import shopping_bp

app = Flask(__name__)

app.secret_key = "my-secret-key"

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(inventory_bp)
app.register_blueprint(recipes_bp)
app.register_blueprint(alerts_bp)
app.register_blueprint(shopping_bp)


@app.context_processor
def inject_navbar_username():

    email = session.get("email")

    if not email:
        return {"navbar_username": ""}

    settings = user_settings.get(email, {})

    username = settings.get("username", "").strip()

    return {
        "navbar_username": username if username else email
    }

if __name__ == "__main__":
    init_db()
    app.run(debug=True)