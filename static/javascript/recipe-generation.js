async function loadRecipeHistory() {
    const recipeHistory = document.getElementById("recipeHistory");
    if (!recipeHistory) return;

    try {
        const response = await fetch("/api/recipe-history");
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || "Unable to load recipe history.");
        }

        displayRecipeHistory(data.recipes);
    }
    catch (error) {
        console.error("Recipe history error:", error);
        recipeHistory.classList.add("error-message");
        recipeHistory.textContent = "Unable to load recipe history.";
    }
}

async function loadHistoricalRecipe(historyId) {
    const generatedRecipe = document.getElementById("generatedRecipe");
    document.getElementById("generate-recipe-preferences").style.display = "none";
    try {
        generatedRecipe.className = "loading-message";
        generatedRecipe.textContent = "Loading recipe...";

        const response = await fetch(`/api/recipe-history/${historyId}`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Unable to load recipe.");
        }

        displayGeneratedRecipe(data.recipe);
        await loadRecipeHistory();
    }
    catch (error) {
        console.error("Historical recipe error:", error);
        generatedRecipe.className = "error-message";
        generatedRecipe.textContent = "Unable to load recipe. Please try again.";
    }
}

async function deleteRecipeHistory(historyId) {
    try {
        const response = await fetch(`/api/recipe-history/${historyId}`, {
            method: "DELETE"
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Unable to delete recipe.");
        }

        await loadRecipeHistory();
    }
    catch (error) {
        console.error("Recipe deletion error:", error);
        alert("Unable to delete recipe from history. Please try again.");
    }
}

function displayRecipeHistory(recipes) {
    const recipeHistory = document.getElementById("recipeHistory");
    if (!recipeHistory) return;

    recipeHistory.classList.remove("loading-message", "error-message");
    recipeHistory.replaceChildren();

    if (!recipes || recipes.length === 0) {
        recipeHistory.className = "empty-message";
        recipeHistory.textContent = "No recipes generated yet.";
        return;
    }

    const groupedRecipes = {};

    recipes.forEach(recipe => {
        if (!groupedRecipes[recipe.date]) {
            groupedRecipes[recipe.date] = [];
        }

        groupedRecipes[recipe.date].push(recipe);
    });

    Object.entries(groupedRecipes).forEach(([date, recipes]) => {
        const dateHeading = document.createElement("div");
        dateHeading.className = "history-date";
        dateHeading.textContent = date;
        recipeHistory.appendChild(dateHeading);

        recipes.forEach(recipe => {
            const historyItem = document.createElement("div");
            historyItem.className = "history-item";

            const recipeButton = document.createElement("button");
            recipeButton.className = "history-recipe-button";
            recipeButton.type = "button";

            const recipeName = document.createElement("div");
            recipeName.className = "recipe-name";
            recipeName.textContent = recipe.name;

            const recipeTime = document.createElement("div");
            recipeTime.className = "recipe-time";
            recipeTime.textContent = recipe.time;

            recipeButton.append(recipeName, recipeTime);
            recipeButton.addEventListener("click", () => {
                loadHistoricalRecipe(recipe.id);
            });

            const deleteButton = document.createElement("button");
            deleteButton.className = "history-delete-button";
            deleteButton.type = "button";
            deleteButton.title = "Delete recipe from history";
            deleteButton.innerHTML = '<i class="fa-solid fa-trash"></i>';
            deleteButton.addEventListener("click", () => {
                deleteRecipeHistory(recipe.id);
            });

            historyItem.append(recipeButton, deleteButton);
            recipeHistory.appendChild(historyItem);
        });
    });
}

document.addEventListener("DOMContentLoaded", () => {
    const recipeHistory = document.getElementById("recipeHistory");

    if (recipeHistory) {
        recipeHistory.classList.add("loading-message");
        recipeHistory.textContent = "Loading recipe history...";
    }

    loadRecipeHistory();

    // Automatically select meal type based on local time
    function setMealTypeByTime() {
        const hour = new Date().getHours();

        let mealType;

        if (hour >= 5 && hour < 11) {
            mealType = "Breakfast";
        } else if (hour >= 11 && hour < 15) {
            mealType = "Lunch";
        } else if (hour >= 15 && hour < 18) {
            mealType = "Snack";
        } else if (hour >= 18 && hour < 22) {
            mealType = "Dinner";
        } else {
            mealType = "Snack";
        }

        const mealTypeInput = document.querySelector(
            `input[name="mealType"][value="${mealType}"]`
        );

        if (mealTypeInput) {
            mealTypeInput.checked = true;
        }
    }

    setMealTypeByTime();
});

document.addEventListener("DOMContentLoaded", () => {
    const generatedRecipe = document.getElementById("generatedRecipe");
    const generateRecipeButton = document.getElementById("generateRecipeButton");
    if (!generatedRecipe) return;
    generateRecipeButton.addEventListener("click", () => {
        const preferences = collectRecipePreferences();
        document.getElementById("generate-recipe-preferences").style.display = "none";
        loadGeneratedRecipe(preferences);
    });

    async function loadGeneratedRecipe(preferences) {
        try {
            generateRecipeButton.disabled = true;
            generatedRecipe.className = "loading-message";
            generateRecipeButton.textContent = "Generating Recipe...";
            generatedRecipe.textContent = "Generating your recipe...";

            const response = await fetch("/api/generated-recipe", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(preferences)
            });

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.error || "Unable to generate recipe.");
            }
            displayGeneratedRecipe(data.recipe);
            await loadRecipeHistory();
        }
        catch (error) {
            console.error("Recipe generation error:", error);
            generatedRecipe.className = "error-message";
            generatedRecipe.textContent = "Unable to generate recipe. Please try again.";
        }
        finally {
            generateRecipeButton.disabled = false;
            generateRecipeButton.textContent = "Generate Recipe";
        }
    }

    function createElement(tag, className, text = "") {
        const element = document.createElement(tag);
        if (className) {
            element.className = className;
        }
        element.textContent = text;
        return element;
    }

    window.displayGeneratedRecipe = function (recipe) {
        if (
            !recipe ||
            !Array.isArray(recipe.ingredients) ||
            !Array.isArray(recipe.instructions)
        ) {
            throw new Error("Invalid recipe data received.");
        }
        generatedRecipe.className = "";
        generatedRecipe.replaceChildren();

        const header = createElement("div", "generated-recipe-header");

        header.appendChild(createElement("h2", "", "Generated Recipe"));
        header.appendChild(createElement("p", "", "Here's a recipe based on your selected preferences."));
        generatedRecipe.appendChild(header);

        const titleSection = createElement("div", "generated-recipe-title");

        titleSection.appendChild(createElement("h1", "", recipe.name));
        titleSection.appendChild(createElement("p", "", recipe.description));

        const meta = createElement("div", "recipe-meta");
        const preparationTime = createElement("span");
        const clockIcon = createElement("i", "fa-regular fa-clock");
        preparationTime.appendChild(clockIcon);
        preparationTime.appendChild(document.createTextNode(" " + recipe.preparation_time));

        const servings = createElement("span");
        const usersIcon = createElement("i", "fa-solid fa-users");
        servings.appendChild(usersIcon);
        servings.appendChild(document.createTextNode(" " + recipe.servings + " servings"));

        meta.append(preparationTime, servings);
        titleSection.appendChild(meta);
        generatedRecipe.appendChild(titleSection);

        const ingredientsSection = createElement("div", "recipe-section");
        ingredientsSection.appendChild(createElement("h3", "", "Ingredients"));
        ingredientsSection.appendChild(
            createElement(
                "p",
                "recipe-section-description",
                "Ingredients currently available in your inventory are shown normally. Missing ingredients are faded."
            )
        );

        const ingredientsList = createElement("div", "ingredients-list");

        recipe.ingredients.forEach(ingredient => {
            const isAvailable = ingredient.available === true;
            const ingredientItem = createElement("div", `ingredient-item ${isAvailable ? "" : "missing"}`);

            const status = createElement("div", `ingredient-status ${isAvailable ? "available" : ""}`);
            const icon = createElement("i", `fa-solid ${isAvailable ? "fa-check" : "fa-plus"}`);
            status.appendChild(icon);

            const name = createElement("span", "ingredient-name", ingredient.name);
            const amount = createElement("span", "ingredient-amount", ingredient.amount);

            ingredientItem.append(status, name, amount);
            ingredientsList.appendChild(ingredientItem);
        });

        // Identify missing ingredients
        const missingIngredients = recipe.ingredients.filter(
            ingredient => ingredient.available !== true
        );

        // Add missing ingredients button
        if (missingIngredients.length > 0) {

            const addMissingIngredientsButton = createElement(
                "button",
                "add-missing-ingredients-button",
                "Add Missing Ingredients to Active Shopping List"
            );

            addMissingIngredientsButton.addEventListener("click", async () => {

                try {
                    addMissingIngredientsButton.disabled = true;
                    addMissingIngredientsButton.textContent = "Adding Ingredients...";

                    const response = await fetch("/api/active-shopping-list/missing-items", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            recipe_id: recipe.id,
                            ingredients: missingIngredients.map(ingredient => ingredient.name)
                        })
                    });

                    const data = await response.json();

                    if (!response.ok) {
                        throw new Error(data.error || "Unable to add ingredients.");
                    }

                    missingIngredientsFeedback.textContent =
                        `${data.added_count} ingredients added. ` +
                        `${data.updated_count} existing quantities doubled.`;

                    missingIngredientsFeedback.hidden = false;
                    addMissingIngredientsButton.textContent = "Ingredients Added";

                } catch (error) {
                    missingIngredientsFeedback.textContent =
                        error.message || "Unable to add ingredients. Please try again.";

                    missingIngredientsFeedback.hidden = false;
                    missingIngredientsFeedback.className =
                        "missing-ingredients-feedback error";

                    addMissingIngredientsButton.disabled = false;
                    addMissingIngredientsButton.textContent =
                        "Add Missing Ingredients to Shopping List";
                }
            });

            const cartIcon = createElement("i", "fa-solid fa-cart-plus");
            addMissingIngredientsButton.prepend(cartIcon);

            ingredientsSection.appendChild(addMissingIngredientsButton);
            // Feedback message
            const missingIngredientsFeedback = createElement(
                "p",
                "missing-ingredients-feedback"
            );

            missingIngredientsFeedback.hidden = true;

            ingredientsSection.appendChild(missingIngredientsFeedback);
        }

        ingredientsSection.appendChild(ingredientsList);
        generatedRecipe.appendChild(ingredientsSection);

        const instructionsSection = createElement("div", "recipe-section instructions-section");
        instructionsSection.appendChild(createElement("h3", "", "Step-by-Step Instructions"));
        const instructionsList = createElement("div", "instructions-list");

        recipe.instructions.forEach((step, index) => {
            const instructionItem = createElement("div", "instruction-item");
            const number = createElement("div", "instruction-number", index + 1);

            const content = createElement("div", "instruction-content");
            content.appendChild(createElement("h4", "", step.title));
            content.appendChild(createElement("p", "", step.description));

            instructionItem.append(number, content);
            instructionsList.appendChild(instructionItem);
        });

        instructionsSection.appendChild(instructionsList);
        generatedRecipe.appendChild(instructionsSection);
    };

    function collectRecipePreferences() {
        const mealType = document.querySelector(
            'input[name="mealType"]:checked'
        )?.value;

        const dietaryPreferences = Array.from(
            document.querySelectorAll(
                'input[name="dietary-preference"]:checked'
            )
        ).map(option => option.value);

        return {
            mealType: mealType,
            useInventory: document.getElementById("useInventory").checked,
            expiringIngredients: document.getElementById("expiringIngredients").checked,
            avoidAllergens: document.getElementById("avoidAllergens").checked,
            dietaryPreferences: dietaryPreferences
        };
    }

    // Check if the user came from the Expiring Soon section
    const urlParams = new URLSearchParams(window.location.search);
    const fromExpiringSoon = urlParams.get("expiring") === "true";

    if (fromExpiringSoon) {
        document.getElementById("useInventory").checked = true;
        document.getElementById("expiringIngredients").checked = true;

        const preferences = collectRecipePreferences();

        document.getElementById("generate-recipe-preferences").style.display = "none";

        loadGeneratedRecipe(preferences);
    }


});