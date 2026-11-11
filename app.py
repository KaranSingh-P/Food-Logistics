from flask import Flask
from database import init_db

from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.inventory import inventory_bp
from routes.recipes import recipes_bp
from routes.alerts import alerts_bp

app = Flask(__name__)

app.secret_key = "my-secret-key"

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(inventory_bp)
app.register_blueprint(recipes_bp)
app.register_blueprint(alerts_bp)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)