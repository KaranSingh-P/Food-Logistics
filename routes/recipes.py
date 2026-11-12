
from flask import Blueprint, jsonify, render_template, request, redirect, session

recipes_bp = Blueprint("recipes", __name__)


# Temporary recipe history
recipe_history = [
    {
        "id": 1,
        "name": "Creamy Garlic Chicken Pasta",
        "date": "10 Nov 2026",
        "time": "8:42 PM"
    },
    {
        "id": 2,
        "name": "Vegetable Fried Rice",
        "date": "10 Nov 2026",
        "time": "3:18 PM"
    },
    {
        "id": 3,
        "name": "Paneer Butter Masala",
        "date": "09 Nov 2026",
        "time": "7:30 PM"
    },
    {
        "id": 4,
        "name": "Vegetable Sandwich",
        "date": "08 Nov 2026",
        "time": "11:15 AM"
    }
]


# Temporary generated recipe
generated_recipe = {
    "id": 1,
    "name": "Creamy Garlic Chicken Pasta",
    "description": "A creamy and comforting chicken pasta made with garlic, herbs, and Parmesan cheese.",
    "preparation_time": "35 minutes",
    "servings": 4,

    "ingredients": [
        {
            "name": "Chicken Breast",
            "amount": "500 g",
            "available": True
        },
        {
            "name": "Penne Pasta",
            "amount": "300 g",
            "available": True
        },
        {
            "name": "Garlic",
            "amount": "4 cloves",
            "available": True
        },
        {
            "name": "Heavy Cream",
            "amount": "200 ml",
            "available": False
        },
        {
            "name": "Parmesan Cheese",
            "amount": "75 g",
            "available": False
        },
        {
            "name": "Olive Oil",
            "amount": "2 tbsp",
            "available": True
        },
        {
            "name": "Italian Herbs",
            "amount": "1 tsp",
            "available": True
        },
        {
            "name": "Salt & Pepper",
            "amount": "To taste",
            "available": True
        }
    ],

    "instructions": [
        {
            "title": "Cook the pasta",
            "description": "Bring a large pot of salted water to a boil. Cook the pasta according to the package instructions until al dente. Drain and set aside."
        },
        {
            "title": "Prepare the chicken",
            "description": "Cut the chicken breast into bite-sized pieces. Season with salt, pepper, and Italian herbs."
        },
        {
            "title": "Cook the chicken",
            "description": "Heat olive oil in a large pan over medium-high heat. Add the chicken and cook until golden brown and fully cooked."
        },
        {
            "title": "Prepare the sauce",
            "description": "Add minced garlic and cook for one minute. Add the heavy cream and Parmesan cheese. Stir until the sauce becomes smooth and creamy."
        },
        {
            "title": "Combine the ingredients",
            "description": "Add the cooked pasta and chicken to the sauce. Toss everything together until evenly coated."
        },
        {
            "title": "Serve",
            "description": "Divide the pasta between four plates. Garnish with Parmesan cheese and fresh herbs. Serve immediately."
        }
    ]
}


@recipes_bp.route("/recipe-generation")
def recipe_generation():
    if "user_id" not in session:
        return redirect("/")

    return render_template("recipe-generation.html")


@recipes_bp.route("/api/recipe-history", methods=["GET"])
def get_recipe_history():

    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    return jsonify({
        "recipes": recipe_history
    })


@recipes_bp.route("/api/generated-recipe", methods=["POST"])
def generate_recipe():

    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    preferences = request.get_json()

    if not preferences:
        return jsonify({"error": "No preferences received"}), 400

    # TODO: Generate a recipe using the received preferences.

    return jsonify({
        "recipe": generated_recipe
    })


@recipes_bp.route("/api/generated-recipe", methods=["GET"])
def get_generated_recipe():

    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    return jsonify({
        "recipe": generated_recipe
    })
