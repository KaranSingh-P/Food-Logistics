document.addEventListener("DOMContentLoaded", () => {
    const recipeHistory = document.getElementById("recipeHistory");
    if (!recipeHistory) return;
    loadRecipeHistory();

    async function loadRecipeHistory() {
        try {
            recipeHistory.textContent = "Loading recipe history...";
            const response = await fetch("/api/recipe-history");
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.error || "Unable to load recipe history.");
            }
            displayRecipeHistory(data.recipes);
        }
        catch (error) {
            console.error("Recipe history error:", error);
            recipeHistory.textContent = "Unable to load recipe history.";
        }
    }

    function displayRecipeHistory(recipes) {
        recipeHistory.replaceChildren();

        if (!recipes || recipes.length === 0) {
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

                const recipeName = document.createElement("div");
                recipeName.className = "recipe-name";
                recipeName.textContent = recipe.name;

                const recipeTime = document.createElement("div");
                recipeTime.className = "recipe-time";
                recipeTime.textContent = recipe.time;

                historyItem.appendChild(recipeName);
                historyItem.appendChild(recipeTime);

                recipeHistory.appendChild(historyItem);
            });
        });
    }
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
        }
        catch (error) {
            console.error("Recipe generation error:", error);
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

    function displayGeneratedRecipe(recipe) {
        if (
            !recipe ||
            !Array.isArray(recipe.ingredients) ||
            !Array.isArray(recipe.instructions)
        ) {
            throw new Error("Invalid recipe data received.");
        }
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
    }

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
});