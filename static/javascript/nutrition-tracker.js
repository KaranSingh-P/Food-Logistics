
document.addEventListener("DOMContentLoaded", function () {

    // =========================================
    // ELEMENTS
    // =========================================

    const modal = document.getElementById("food-modal");

    const addFoodButton = document.getElementById("add-food-button");
    const closeFoodButton = document.getElementById("close-food-modal");
    const cancelFoodButton = document.getElementById("cancel-food-modal");

    const foodSelect = document.getElementById("food-select");
    const quantityInput = document.getElementById("food-quantity");
    const manageCustomFoodsButton = document.getElementById("manage-custom-foods");
    const customFoodList = document.getElementById("custom-food-list");

    const customFoodButton = document.getElementById("create-custom-food");
    const customFoodForm = document.getElementById("custom-food-form");
    const saveCustomFoodButton = document.getElementById("save-custom-food");

    const confirmAddButton = document.getElementById("confirm-add-food");

    const foodLogList = document.getElementById("food-log-list");

    const foodSelectionSection = document.getElementById("food-selection-section");
    const foodQuantitySection = document.getElementById("food-quantity-section");
    const foodNutritionPreview = document.getElementById("food-nutrition-preview");

    const nutritionDateInput = document.getElementById("nutrition-date");
    const previousDayButton = document.getElementById("previous-day");
    const nextDayButton = document.getElementById("next-day");
    const todayButton = document.getElementById("today-button");

    const editNutritionGoalsButton =
        document.getElementById("edit-nutrition-goals");

    const nutritionGoalsForm =
        document.getElementById("nutrition-goals-form");

    const saveNutritionGoalsButton =
        document.getElementById("save-nutrition-goals");

    const cancelNutritionGoalsButton =
        document.getElementById("cancel-nutrition-goals");

    let selectedFood = null;

    let dailyGoals = {
        calories: 2000,
        protein: 75,
        carbs: 250,
        fats: 65
    };


    // =========================================
    // API HELPER
    // =========================================

    async function apiRequest(url, options = {}) {

        const response = await fetch(url, {
            credentials: "same-origin",
            ...options
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(data.message || "Something went wrong.");
        }

        return data;
    }


    // =========================================
    // HELPER FUNCTIONS
    // =========================================

    function getNumber(value) {
        return Number(value) || 0;
    }


    function formatNumber(value) {
        return Number(value.toFixed(2)).toString();
    }


    function calculateNutrition(food, quantity) {

        return {
            calories: food.calories * quantity,
            protein: food.protein * quantity,
            carbs: food.carbs * quantity,
            fats: food.fats * quantity
        };

    }

    // =========================================
    // NON-BLOCKING NOTIFICATIONS
    // =========================================

    function showMessage(message, type = "success") {

        let notification = document.getElementById("nutrition-notification");

        if (!notification) {

            notification = document.createElement("div");

            notification.id = "nutrition-notification";

            document.body.appendChild(notification);

        }

        notification.textContent = message;

        notification.style.position = "fixed";
        notification.style.top = "75px";
        notification.style.right = "25px";
        notification.style.zIndex = "10000";
        notification.style.padding = "13px 20px";
        notification.style.borderRadius = "8px";
        notification.style.fontSize = "14px";
        notification.style.boxShadow = "0 4px 15px rgba(0,0,0,0.15)";
        notification.style.backgroundColor =
            type === "error" ? "#fee2e2" : "#dcfce7";
        notification.style.color =
            type === "error" ? "#991b1b" : "#166534";

        notification.style.opacity = "1";
        notification.style.transition = "opacity 0.3s";

        clearTimeout(notification.hideTimer);

        notification.hideTimer = setTimeout(() => {

            notification.style.opacity = "0";

        }, 3000);

    }


    // =========================================
    // UPDATE DAILY NUTRITION TOTALS
    // =========================================

    async function loadNutritionGoals() {

        try {

            const data = await apiRequest("/api/nutrition/goals");

            dailyGoals = {
                calories: Number(data.goals.calories),
                protein: Number(data.goals.protein),
                carbs: Number(data.goals.carbohydrates),
                fats: Number(data.goals.fats)
            };

        } catch (error) {

            showMessage(error.message, "error");

        }

    }

    // =========================================
    // EDIT DAILY NUTRITION GOALS
    // =========================================

    function openNutritionGoalsForm() {

        document.getElementById("goal-calories").value =
            dailyGoals.calories;

        document.getElementById("goal-protein").value =
            dailyGoals.protein;

        document.getElementById("goal-carbs").value =
            dailyGoals.carbs;

        document.getElementById("goal-fats").value =
            dailyGoals.fats;

        nutritionGoalsForm.style.display = "block";

    }

    function closeNutritionGoalsForm() {

        nutritionGoalsForm.style.display = "none";

    }

    editNutritionGoalsButton.addEventListener("click", function () {

        const isOpen = nutritionGoalsForm.style.display === "block";

        if (isOpen) {
            closeNutritionGoalsForm();
        } else {
            openNutritionGoalsForm();
        }

    });

    cancelNutritionGoalsButton.addEventListener(
        "click",
        closeNutritionGoalsForm
    );

    saveNutritionGoalsButton.addEventListener("click", async function () {

        const goals = {
            calories: document.getElementById("goal-calories").value,
            protein: document.getElementById("goal-protein").value,
            carbohydrates: document.getElementById("goal-carbs").value,
            fats: document.getElementById("goal-fats").value
        };

        const values = Object.values(goals);

        if (values.some(value =>
            value.trim() === "" ||
            !Number.isFinite(Number(value)) ||
            Number(value) <= 0
        )) {

            showMessage(
                "Please enter valid nutrition goals greater than zero.",
                "error"
            );

            return;

        }

        try {

            const data = await apiRequest("/api/nutrition/goals", {

                method: "PUT",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(goals)

            });

            dailyGoals = {
                calories: Number(goals.calories),
                protein: Number(goals.protein),
                carbs: Number(goals.carbohydrates),
                fats: Number(goals.fats)
            };

            updateDailyNutrition();

            closeNutritionGoalsForm();

            showMessage(data.message);

        } catch (error) {

            showMessage(error.message, "error");

        }

    });

    function updateDailyNutrition() {

        const totals = {
            calories: 0,
            protein: 0,
            carbs: 0,
            fats: 0
        };

        document.querySelectorAll(".food-log-item").forEach(item => {

            totals.calories += getNumber(item.dataset.calories);
            totals.protein += getNumber(item.dataset.protein);
            totals.carbs += getNumber(item.dataset.carbs);
            totals.fats += getNumber(item.dataset.fats);

        });

        const goals = dailyGoals;

        document.getElementById("total-calories").textContent =
            formatNumber(totals.calories) + " / " + goals.calories + " kcal";

        document.getElementById("total-protein").textContent =
            formatNumber(totals.protein) + " / " + goals.protein + " g";

        document.getElementById("total-carbs").textContent =
            formatNumber(totals.carbs) + " / " + goals.carbs + " g";

        document.getElementById("total-fats").textContent =
            formatNumber(totals.fats) + " / " + goals.fats + " g";


        // Update progress bars.

        const progress = {
            calories: totals.calories / goals.calories * 100,
            protein: totals.protein / goals.protein * 100,
            carbs: totals.carbs / goals.carbs * 100,
            fats: totals.fats / goals.fats * 100
        };

        document.querySelector(".calories .nutrition-progress-fill").style.width =
            Math.min(progress.calories, 100) + "%";

        document.querySelector(".protein .nutrition-progress-fill").style.width =
            Math.min(progress.protein, 100) + "%";

        document.querySelector(".carbohydrates .nutrition-progress-fill").style.width =
            Math.min(progress.carbs, 100) + "%";

        document.querySelector(".fats .nutrition-progress-fill").style.width =
            Math.min(progress.fats, 100) + "%";


        // Update calorie odometer.

        const percentage = Math.round(progress.calories);

        document.getElementById("odometer-percentage").textContent =
            percentage + "%";

        document.getElementById("odometer-consumed").textContent =
            formatNumber(totals.calories) + " kcal";

    }


    // =========================================
    // LOAD AVAILABLE FOODS FROM DATABASE
    // =========================================



    async function loadFoods() {

        try {

            const data = await apiRequest("/api/nutrition/foods");

            const foods = (data.foods || []).map(food => ({
                ...food,
                item_type: "food",
                option_value: "food-" + food.food_id,
                carbs: food.carbohydrates
            }));

            const recipes = (data.recipes || []).map(recipe => ({
                ...recipe,
                item_type: "recipe",
                option_value: "recipe-" + recipe.recipe_id,
                carbs: recipe.carbohydrates
            }));

            window.nutritionFoods = [...foods, ...recipes];

            foodSelect.value = "";
            foodSearchResults.innerHTML = "";
            foodSearchResults.style.display = "none";

        } catch (error) {

            console.error("Food loading error:", error);

            window.nutritionFoods = [];

            foodSelect.value = "Unable to load foods";

            showMessage(error.message, "error");

        }

    }


    async function loadCustomFoods() {

        try {

            const data = await apiRequest("/api/nutrition/foods");

            const customFoods = data.foods.filter(food => food.is_custom);

            customFoodList.innerHTML = "";

            if (customFoods.length === 0) {

                customFoodList.textContent = "You haven't created any custom foods yet.";

                return;
            }

            customFoods.forEach(food => {

                const foodItem = document.createElement("div");
                foodItem.className = "custom-food-item";

                const foodName = document.createElement("span");
                foodName.textContent = food.food_name;

                const deleteButton = document.createElement("button");
                deleteButton.type = "button";
                deleteButton.textContent = "×";
                deleteButton.title = "Delete custom food";
                deleteButton.className = "delete-custom-food-button";

                deleteButton.addEventListener("click", async function () {

                    try {

                        await apiRequest(
                            "/api/nutrition/foods/" + food.food_id,
                            {
                                method: "DELETE"
                            }
                        );

                        showMessage("Custom food deleted.");

                        await loadFoods();
                        await loadCustomFoods();

                    } catch (error) {

                        showMessage(error.message, "error");

                    }

                });

                foodItem.appendChild(foodName);
                foodItem.appendChild(deleteButton);

                customFoodList.appendChild(foodItem);

            });

        } catch (error) {

            showMessage(error.message, "error");

        }

    }


    // =========================================
    // LOAD TODAY'S FOOD LOG FROM DATABASE
    // =========================================


    async function loadTodayLogs() {

        try {

            const selectedDate = nutritionDateInput.value;

            const data = await apiRequest(
                "/api/nutrition/logs/date/" + selectedDate
            );

            foodLogList.innerHTML = "";

            data.logs.forEach(log => {
                renderFoodLogItem(log);
            });

            updateDailyNutrition();

        } catch (error) {

            console.error("Food log loading error:", error);

            showMessage(error.message, "error");

        }

    }


    // =========================================
    // RENDER FOOD LOG ENTRY
    // =========================================

    function renderFoodLogItem(log) {

        const item = document.createElement("div");

        item.className = "food-log-item";

        item.dataset.logId = log.log_id;
        item.dataset.calories = log.calories;
        item.dataset.protein = log.protein;
        item.dataset.carbs = log.carbohydrates;
        item.dataset.fats = log.fats;


        // Food name and quantity.

        const nameContainer = document.createElement("div");
        nameContainer.className = "food-log-name";

        const name = document.createElement("span");
        name.textContent = log.food_name;

        const servings = document.createElement("small");

        servings.textContent =
            formatNumber(log.quantity) +
            (log.quantity === 1 ? " serving" : " servings");

        nameContainer.appendChild(name);
        nameContainer.appendChild(servings);


        // Nutrition information.

        const nutritionContainer = document.createElement("div");
        nutritionContainer.className = "food-log-nutrition";

        const calories = document.createElement("span");

        calories.textContent =
            formatNumber(log.calories) + " kcal";

        const info = document.createElement("span");

        info.className = "food-info";
        info.textContent = "i";

        info.title =
            "Calories: " + formatNumber(log.calories) + " kcal | " +
            "Protein: " + formatNumber(log.protein) + " g | " +
            "Carbs: " + formatNumber(log.carbohydrates) + " g | " +
            "Fats: " + formatNumber(log.fats) + " g";


        nutritionContainer.appendChild(calories);
        nutritionContainer.appendChild(info);


        // Remove button.

        const removeButton = document.createElement("button");

        removeButton.type = "button";
        removeButton.className = "remove-food-button";
        removeButton.textContent = "×";
        removeButton.title = "Remove food entry";

        removeButton.addEventListener("click", async function () {

            try {

                await apiRequest(
                    "/api/nutrition/logs/" + log.log_id,
                    {
                        method: "DELETE"
                    }
                );

                showMessage("Food entry removed.");
                await loadTodayLogs();

            } catch (error) {

                showMessage(error.message, "error");

            }

        });

        nutritionContainer.appendChild(removeButton);


        item.appendChild(nameContainer);
        item.appendChild(nutritionContainer);

        foodLogList.appendChild(item);

    }


    // =========================================
    // NUTRITION PREVIEW
    // =========================================

    function updatePreview() {

        const quantity = getNumber(quantityInput.value);

        if (!selectedFood || quantity <= 0) {

            document.getElementById("preview-calories").textContent = "0 kcal";
            document.getElementById("preview-protein").textContent = "0 g";
            document.getElementById("preview-carbs").textContent = "0 g";
            document.getElementById("preview-fats").textContent = "0 g";

            return;

        }

        const nutrition = calculateNutrition(selectedFood, quantity);

        document.getElementById("preview-calories").textContent =
            formatNumber(nutrition.calories) + " kcal";

        document.getElementById("preview-protein").textContent =
            formatNumber(nutrition.protein) + " g";

        document.getElementById("preview-carbs").textContent =
            formatNumber(nutrition.carbs) + " g";

        document.getElementById("preview-fats").textContent =
            formatNumber(nutrition.fats) + " g";

    }


    // =========================================
    // OPEN AND CLOSE MODAL
    // =========================================

    function openModal() {
        modal.style.display = "flex";
    }


    function closeModal() {

        modal.style.display = "none";

        foodSelectionSection.style.display = "";
        foodQuantitySection.style.display = "";
        foodNutritionPreview.style.display = "";

        foodSelect.value = "";
        quantityInput.value = "1";

        selectedFood = null;

        customFoodForm.style.display = "none";

        updatePreview();

    }


    addFoodButton.addEventListener("click", openModal);

    closeFoodButton.addEventListener("click", closeModal);
    cancelFoodButton.addEventListener("click", closeModal);


    modal.addEventListener("click", function (event) {

        if (event.target === modal) {
            closeModal();
        }

    });


    // =========================================
    // SELECT FOOD
    // =========================================



    const foodSearchResults = document.getElementById("food-search-results");


    // Display matching foods and recipes.

    function renderFoodSearchResults(searchTerm = "") {

        const query = searchTerm.trim().toLowerCase();

        foodSearchResults.innerHTML = "";

        const matchingFoods = window.nutritionFoods.filter(item =>
            item.item_type === "food" &&
            item.food_name.toLowerCase().includes(query)
        );

        const matchingRecipes = window.nutritionFoods.filter(item =>
            item.item_type === "recipe" &&
            item.food_name.toLowerCase().includes(query)
        );


        function addGroup(label, items) {

            if (items.length === 0) return;

            const heading = document.createElement("div");
            heading.className = "food-search-group-heading";
            heading.textContent = label;

            foodSearchResults.appendChild(heading);


            items.forEach(item => {

                const option = document.createElement("button");

                option.type = "button";
                option.className = "food-search-option";
                option.textContent = item.food_name;
                option.dataset.optionValue = item.option_value;

                foodSearchResults.appendChild(option);

            });

        }


        addGroup("Foods", matchingFoods);
        addGroup("My Recipes", matchingRecipes);


        if (matchingFoods.length === 0 && matchingRecipes.length === 0) {

            const message = document.createElement("div");

            message.className = "food-search-empty";
            message.textContent = "No matching foods or recipes found.";

            foodSearchResults.appendChild(message);

        }

        foodSearchResults.style.display = "block";

    }


    // Filter as the user types.

    foodSelect.addEventListener("input", function () {

        selectedFood = null;

        updatePreview();

        renderFoodSearchResults(foodSelect.value);

    });


    // Show all items when the search field is focused.

    foodSelect.addEventListener("focus", function () {

        renderFoodSearchResults(foodSelect.value);

    });


    // Handle selection.

    foodSearchResults.addEventListener("click", function (event) {

        const option = event.target.closest(".food-search-option");

        if (!option) return;

        const selectedValue = option.dataset.optionValue;

        selectedFood = window.nutritionFoods.find(
            item => item.option_value === selectedValue
        ) || null;

        if (!selectedFood) return;

        foodSelect.value = selectedFood.food_name;

        foodSearchResults.style.display = "none";

        updatePreview();

    });



    quantityInput.addEventListener("input", updatePreview);


    // =========================================
    // CREATE CUSTOM FOOD FORM
    // =========================================

    customFoodButton.addEventListener("click", function () {

        const isOpening = customFoodForm.style.display === "none";

        customFoodForm.style.display = isOpening ? "block" : "none";

        foodSelectionSection.style.display = isOpening ? "none" : "";
        foodQuantitySection.style.display = isOpening ? "none" : "";
        foodNutritionPreview.style.display = isOpening ? "none" : "";

    });


    // =========================================
    // SAVE CUSTOM FOOD TO DATABASE
    // =========================================

    saveCustomFoodButton.addEventListener("click", async function () {

        const name = document.getElementById("custom-food-name").value.trim();

        const calories = document.getElementById("custom-calories").value;
        const protein = document.getElementById("custom-protein").value;
        const carbs = document.getElementById("custom-carbs").value;
        const fats = document.getElementById("custom-fats").value;


        if (name.length < 2 || name.length > 100) {

            showMessage("Food name must contain 2 to 100 characters.", "error");

            return;

        }


        const values = [calories, protein, carbs, fats];

        if (values.some(value =>
            value.trim() === "" ||
            !Number.isFinite(Number(value)) ||
            Number(value) < 0
        )) {

            showMessage("Please enter valid nutritional values. All fields are required.", "error");

            return;

        }


        try {

            const data = await apiRequest("/api/nutrition/foods", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    food_name: name,
                    calories: Number(calories),
                    protein: Number(protein),
                    carbohydrates: Number(carbs),
                    fats: Number(fats)

                })

            });


            // Reload foods from the database.

            selectedFood = window.nutritionFoods?.find(
                food => food.option_value === "food-" + data.food_id
            ) || null;

            foodSelect.value = selectedFood ? selectedFood.food_name : "";


            // Return to the normal food selection view.

            customFoodForm.style.display = "none";

            foodSelectionSection.style.display = "";
            foodQuantitySection.style.display = "";
            foodNutritionPreview.style.display = "";


            // Reset custom food inputs.

            document.getElementById("custom-food-name").value = "";
            document.getElementById("custom-calories").value = "";
            document.getElementById("custom-protein").value = "";
            document.getElementById("custom-carbs").value = "";
            document.getElementById("custom-fats").value = "";


            updatePreview();

            showMessage(data.message);

        } catch (error) {

            showMessage(error.message, "error");

        }

    });


    // =========================================
    // ADD FOOD TO DATABASE LOG
    // =========================================


    confirmAddButton.addEventListener("click", async function () {

        const quantity = getNumber(quantityInput.value);

        if (!foodSelect.value || !selectedFood) {

            showMessage("Please select a food or recipe.", "error");

            return;

        }

        if (!Number.isFinite(quantity) || quantity <= 0) {

            showMessage("Please enter a valid quantity.", "error");

            return;

        }

        try {

            await apiRequest("/api/nutrition/logs", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    item_type: selectedFood.item_type,

                    item_id: selectedFood.item_type === "food"
                        ? selectedFood.food_id
                        : selectedFood.recipe_id,

                    quantity: quantity

                })

            });

            // Reload today's food log.

            await loadTodayLogs();

            closeModal();

        } catch (error) {

            showMessage(error.message, "error");

        }

    });

    manageCustomFoodsButton.addEventListener("click", async function () {

        const isOpening = customFoodList.style.display === "none";

        if (isOpening) {

            customFoodList.style.display = "block";

            await loadCustomFoods();

            manageCustomFoodsButton.textContent = "Hide Custom Foods";

        } else {

            customFoodList.style.display = "none";

            manageCustomFoodsButton.textContent = "Manage Custom Foods";

        }

    });



    // =========================================
    // DOWNLOAD NUTRITION REPORTS
    // =========================================

    async function downloadNutritionReport(period, apiPeriod) {

        try {

            // Fetch historical food logs from the database.

            const data = await apiRequest(
                "/api/nutrition/reports/" + apiPeriod
            );

            const entries = data.logs;

            let report = "FOOD LOG - NUTRITION REPORT\n";
            report += "====================================\n\n";

            report += "Report Period: " + period + "\n";
            report += "Generated On: " + new Date().toLocaleDateString() + "\n\n";

            const totals = {
                calories: 0,
                protein: 0,
                carbs: 0,
                fats: 0
            };

            report += "FOOD ENTRIES\n";
            report += "------------------------------------\n";

            if (entries.length === 0) {

                report += "No food entries found for this period.\n\n";

            } else {

                entries.forEach((item, index) => {

                    const name = item.food_name;
                    const quantity = getNumber(item.quantity);

                    const calories = getNumber(item.calories);
                    const protein = getNumber(item.protein);
                    const carbs = getNumber(item.carbohydrates);
                    const fats = getNumber(item.fats);

                    const loggedDate = new Date(item.logged_at);

                    totals.calories += calories;
                    totals.protein += protein;
                    totals.carbs += carbs;
                    totals.fats += fats;

                    report += (index + 1) + ". " + name + "\n";
                    report += "   Date: " + loggedDate.toLocaleString() + "\n";
                    report += "   Quantity: " + formatNumber(quantity) + " serving(s)\n";
                    report += "   Calories: " + formatNumber(calories) + " kcal\n";
                    report += "   Protein: " + formatNumber(protein) + " g\n";
                    report += "   Carbohydrates: " + formatNumber(carbs) + " g\n";
                    report += "   Fats: " + formatNumber(fats) + " g\n\n";

                });

            }

            report += "====================================\n";
            report += "TOTAL NUTRITION FOR THE PERIOD\n";
            report += "------------------------------------\n";

            report += "Calories: " + formatNumber(totals.calories) + " kcal\n";
            report += "Protein: " + formatNumber(totals.protein) + " g\n";
            report += "Carbohydrates: " + formatNumber(totals.carbs) + " g\n";
            report += "Fats: " + formatNumber(totals.fats) + " g\n";

            report += "\n====================================\n";
            report += "Generated by Food Logistics\n";

            // Create and download the TXT file.

            const blob = new Blob([report], {
                type: "text/plain;charset=utf-8"
            });

            const url = URL.createObjectURL(blob);

            const link = document.createElement("a");

            link.href = url;

            link.download =
                "Food-Log-" + apiPeriod + ".txt";

            document.body.appendChild(link);

            link.click();

            link.remove();

            URL.revokeObjectURL(url);

            showMessage("Nutrition report downloaded.");

        } catch (error) {

            showMessage(error.message, "error");

        }

    }


    // Download last 30 days.

    document.getElementById("download-30-days").addEventListener("click", function () {

        downloadNutritionReport("Last 30 Days", "30-days");

    });


    // Download last year.

    document.getElementById("download-last-year").addEventListener("click", function () {

        downloadNutritionReport("Last Year", "1-year");

    });


    // =========================================
    // NUTRITION DATE NAVIGATION
    // =========================================

    function getLocalDateString(date) {

        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, "0");
        const day = String(date.getDate()).padStart(2, "0");

        return `${year}-${month}-${day}`;

    }


    function updateDateControls() {

        const today = getLocalDateString(new Date());

        nutritionDateInput.max = today;

        nextDayButton.disabled = nutritionDateInput.value >= today;

        const addFoodButton = document.getElementById("add-food-button");

        const isToday = nutritionDateInput.value === today;

        addFoodButton.disabled = !isToday;

        addFoodButton.title = isToday
            ? "Add a food entry"
            : "You can only add food entries for today.";

    }

    // Previous day.

    previousDayButton.addEventListener("click", async function () {

        const selectedDate = new Date(nutritionDateInput.value + "T12:00:00");

        selectedDate.setDate(selectedDate.getDate() - 1);

        nutritionDateInput.value = getLocalDateString(selectedDate);

        updateDateControls();

        await loadTodayLogs();

    });


    // Next day.

    nextDayButton.addEventListener("click", async function () {

        const today = getLocalDateString(new Date());

        const selectedDate = new Date(nutritionDateInput.value + "T12:00:00");

        selectedDate.setDate(selectedDate.getDate() + 1);

        const nextDate = getLocalDateString(selectedDate);

        if (nextDate > today) return;

        nutritionDateInput.value = nextDate;

        updateDateControls();

        await loadTodayLogs();

    });


    // Select a date manually.

    nutritionDateInput.addEventListener("change", async function () {

        updateDateControls();

        await loadTodayLogs();

    });


    // Return to today.

    todayButton.addEventListener("click", async function () {

        nutritionDateInput.value = getLocalDateString(new Date());

        updateDateControls();

        await loadTodayLogs();

    });



    // =========================================
    // INITIALIZE PAGE
    // =========================================

    async function initializeNutritionTracker() {

        const today = getLocalDateString(new Date());

        nutritionDateInput.value = today;

        updateDateControls();

        await loadNutritionGoals();

        await loadFoods();

        await loadTodayLogs();

    }

    initializeNutritionTracker();

});
