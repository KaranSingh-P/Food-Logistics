
from flask import Blueprint, render_template, redirect, session

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def home():
    return render_template("index.html")


@dashboard_bp.route("/dashboard")
def dashboard():
    if "email" not in session:
        return redirect("/")

    return render_template("dashboard.html")
