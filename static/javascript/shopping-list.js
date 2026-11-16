document.addEventListener("DOMContentLoaded", () => {
    const shoppingHistory = document.getElementById("shoppingHistory");
    // Historical shopping list modal elements
    const historyModalOverlay = document.getElementById("historyModalOverlay");
    const historyModalTitle = document.getElementById("historyModalTitle");
    const historyModalDate = document.getElementById("historyModalDate");
    const historyModalItems = document.getElementById("historyModalItems");
    // Shopping Template Modal
    const createTemplateButton = document.getElementById("createTemplateButton");
    const templateModalOverlay = document.getElementById("templateModalOverlay");
    const closeTemplateModal = document.getElementById("closeTemplateModal");
    // Add Template Item Modal
    const templateItemModalOverlay = document.getElementById("templateItemModalOverlay");
    const closeTemplateItemModal = document.getElementById("closeTemplateItemModal");
    const templateItemSearch = document.getElementById("templateItemSearch");
    const templateItemSearchResults = document.getElementById("templateItemSearchResults");

    const addTemplateItemButtons = document.querySelectorAll(".add-template-item-button");

    let activeTemplateFrequency = null;

    let templateItems = {
        frequent: [],
        occasional: [],
        rare: []
    };

    let savedTemplateItems = {
        frequent: [],
        occasional: [],
        rare: []
    };


    let currentHistoricalShoppingList = null;
    const closeHistoryModalButton = document.getElementById("closeHistoryModalButton");
    const downloadHistoryListButton = document.getElementById("downloadHistoryListButton");
    if (!shoppingHistory) return;
    loadShoppingHistory();
    document.addEventListener("shoppingHistoryUpdated", () => {
        loadShoppingHistory();
    });

    async function loadShoppingHistory() {
        try {
            shoppingHistory.classList.add("loading-message");
            shoppingHistory.textContent = "Loading shopping history...";
            const response = await fetch("/api/shopping-history");
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.error || "Unable to load shopping history.");
            }
            shoppingHistory.classList.remove("loading-message");
            displayShoppingHistory(data.shopping_history);
        }
        catch (error) {
            console.error("Shopping history error:", error);
            shoppingHistory.classList.remove("loading-message");
            shoppingHistory.classList.add("error-message");
            shoppingHistory.textContent = "Unable to load shopping history.";
        }
    }

    function displayShoppingHistory(lists) {
        shoppingHistory.classList.remove("loading-message", "error-message");
        shoppingHistory.replaceChildren();

        if (!lists || lists.length === 0) {
            shoppingHistory.classList.add("empty-message");
            shoppingHistory.textContent = "No shopping lists generated yet.";
            return;
        }
        const groupedLists = {};
        lists.forEach(list => {
            if (!groupedLists[list.date]) {
                groupedLists[list.date] = [];
            }
            groupedLists[list.date].push(list);
        });

        Object.entries(groupedLists).forEach(([date, lists]) => {
            const dateHeading = document.createElement("div");
            dateHeading.className = "history-date";
            dateHeading.textContent = date;
            shoppingHistory.appendChild(dateHeading);
            lists.forEach(list => {
                const historyItem = document.createElement("div");
                historyItem.className = "history-item";

                const shoppingName = document.createElement("div");
                shoppingName.className = "shopping-name";
                shoppingName.textContent = list.name;

                const itemCount = document.createElement("div");
                itemCount.className = "shopping-item-count";
                itemCount.textContent = `${list.item_count} items`;

                historyItem.style.cursor = "pointer";

                historyItem.addEventListener("click", () => {
                    loadHistoricalShoppingList(list.id);
                });

                // Delete history button
                const deleteButton = document.createElement("button");
                deleteButton.type = "button";
                deleteButton.className = "delete-history-button";
                deleteButton.innerHTML = '<i class="fa-solid fa-trash"></i>';
                deleteButton.title = "Delete shopping history";

                // Prevent clicking the delete button from opening the history modal
                deleteButton.addEventListener("click", async event => {

                    event.stopPropagation();

                    try {
                        const response = await fetch(
                            `/api/shopping-history/${list.id}`,
                            {
                                method: "DELETE"
                            }
                        );

                        const data = await response.json();

                        if (!response.ok) {
                            throw new Error(data.error || "Unable to delete shopping history.");
                        }

                        // Refresh shopping history
                        loadShoppingHistory();

                    } catch (error) {
                        console.error("Delete shopping history error:", error);
                        alert(error.message);
                    }
                });

                historyItem.append(shoppingName, itemCount, deleteButton);
                shoppingHistory.appendChild(historyItem);
            });
        });
    }
    async function loadHistoricalShoppingList(historyId) {

        try {
            const response = await fetch(
                `/api/shopping-history/${historyId}`
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.error || "Unable to load historical shopping list."
                );
            }

            // Update modal heading
            currentHistoricalShoppingList = data;
            historyModalTitle.textContent = `Shopping List #${data.history_id}`;
            historyModalDate.textContent = data.date;

            // Clear previous items
            historyModalItems.replaceChildren();

            if (data.items.length === 0) {
                historyModalItems.textContent = "This shopping list is empty.";
            } else {

                data.items.forEach(item => {

                    const itemRow = document.createElement("div");
                    itemRow.className = "history-modal-item";

                    if (item.completed) {
                        itemRow.classList.add("completed");
                    }

                    const itemName = document.createElement("span");
                    itemName.className = "history-modal-item-name";
                    itemName.textContent = item.name;

                    const itemQuantity = document.createElement("span");
                    itemQuantity.className = "history-modal-item-quantity";
                    itemQuantity.textContent = item.quantity || "—";

                    itemRow.append(itemName, itemQuantity);
                    historyModalItems.appendChild(itemRow);
                });
            }

            // Show modal
            historyModalOverlay.hidden = false;

        } catch (error) {
            console.error("Historical shopping list error:", error);
            alert(error.message);
        }
    }

    // Close historical shopping list modal
    closeHistoryModalButton.addEventListener("click", () => {
        historyModalOverlay.hidden = true;
    });

    // Close modal when clicking outside it
    historyModalOverlay.addEventListener("click", event => {
        if (event.target === historyModalOverlay) {
            historyModalOverlay.hidden = true;
        }
    });

    downloadHistoryListButton.addEventListener("click", () => {

        if (!currentHistoricalShoppingList) return;

        const data = currentHistoricalShoppingList;

        let content = `Shopping List #${data.history_id}\n`;
        content += `Date: ${data.date}\n\n`;
        content += "Items:\n";

        data.items.forEach((item, index) => {

            const status = item.completed ? "[Completed]" : "[Pending]";

            content += `${index + 1}. ${item.name} - ${item.quantity || "—"} ${status}\n`;

        });

        const blob = new Blob([content], {
            type: "text/plain;charset=utf-8"
        });

        const url = URL.createObjectURL(blob);

        const link = document.createElement("a");
        link.href = url;
        link.download = `shopping-list-${data.history_id}.txt`;

        document.body.appendChild(link);
        link.click();
        link.remove();

        URL.revokeObjectURL(url);

    });

    // Open template modal and load saved items
    createTemplateButton.addEventListener("click", async () => {

        templateModalOverlay.hidden = false;

        try {

            const response = await fetch("/api/shopping-template");
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Unable to load template.");
            }

            templateItems = data.template;

            savedTemplateItems = JSON.parse(JSON.stringify(data.template));

            displayTemplateItems();

        } catch (error) {

            console.error("Load shopping template error:", error);

        }

    });

    // Close template modal
    closeTemplateModal.addEventListener("click", closeShoppingTemplate);

    // Close when clicking outside the modal
    templateModalOverlay.addEventListener("click", (event) => {
        if (event.target === templateModalOverlay) {
            templateModalOverlay.hidden = true;
        }
    });

    // Close with Escape key
    document.addEventListener("keydown", (event) => {

        if (event.key === "Escape") {

            // Close Add Template Item popup first
            if (!templateItemModalOverlay.hidden) {
                templateItemModalOverlay.hidden = true;
            }

            // Otherwise close the main Template popup
            else if (!templateModalOverlay.hidden) {
                closeShoppingTemplate();
            }

        }

    });

    // Open Add Item popup
    addTemplateItemButtons.forEach(button => {

        button.addEventListener("click", () => {

            activeTemplateFrequency = button.dataset.frequency;

            templateItemModalOverlay.hidden = false;

            templateItemSearch.value = "";
            templateItemSearchResults.innerHTML = "";

            templateItemSearch.focus();
        });

    });


    // Close Add Item popup
    closeTemplateItemModal.addEventListener("click", () => {
        templateItemModalOverlay.hidden = true;
    });


    // Close when clicking outside
    templateItemModalOverlay.addEventListener("click", (event) => {

        if (event.target === templateItemModalOverlay) {
            templateItemModalOverlay.hidden = true;
        }

    });

    // Search food items for shopping templates
    templateItemSearch.addEventListener("input", async () => {

        const query = templateItemSearch.value.trim();

        templateItemSearchResults.innerHTML = "";

        if (query.length < 3) {
            return;
        }

        templateItemSearchResults.textContent = "Searching...";

        try {

            const response = await fetch(
                `/api/shopping-food-suggestions?q=${encodeURIComponent(query)}`
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Unable to search food items.");
            }

            templateItemSearchResults.innerHTML = "";

            if (data.suggestions.length === 0) {
                templateItemSearchResults.textContent = "No matching food items found.";
            }

            data.suggestions.forEach(item => {

                const resultButton = document.createElement("button");

                resultButton.type = "button";
                resultButton.className = "template-item-search-result";
                resultButton.textContent = item.food_name;

                resultButton.addEventListener("click", () => {

                    // Prevent the same food from appearing in multiple sections
                    const alreadyAdded = Object.values(templateItems)
                        .some(items => items.some(existing =>
                            existing.food_name.trim().toLowerCase() ===
                            item.food_name.trim().toLowerCase()
                        ));

                    if (alreadyAdded) {
                        templateItemSearchResults.textContent = "This item is already in your template.";
                        return;
                    }

                    // Add item to the selected frequency section
                    templateItems[activeTemplateFrequency].push({
                        food_id: item.food_id,
                        food_name: item.food_name
                    });

                    displayTemplateItems();

                    // Close the item picker
                    templateItemModalOverlay.hidden = true;

                });

                templateItemSearchResults.appendChild(resultButton);

            });

            // Allow users to add a custom food name
            const customName = query;

            if (customName.length >= 3) {

                const customButton = document.createElement("button");

                customButton.type = "button";
                customButton.className = "template-item-search-result";
                customButton.textContent = `Add "${customName}"`;

                customButton.addEventListener("click", () => {

                    const alreadyAdded = Object.values(templateItems)
                        .some(items => items.some(existing =>
                            existing.food_name.trim().toLowerCase() ===
                            customName.toLowerCase()
                        ));

                    if (alreadyAdded) {
                        templateItemSearchResults.textContent =
                            "This item is already in your template.";
                        return;
                    }

                    templateItems[activeTemplateFrequency].push({
                        food_id: null,
                        food_name: customName
                    });

                    displayTemplateItems();

                    templateItemModalOverlay.hidden = true;

                });

                customButton.addEventListener("keydown", (event) => {
                    if (event.key === "Enter") {
                        event.preventDefault();
                        customButton.click();
                    }
                });

                templateItemSearchResults.appendChild(customButton);
            }

        } catch (error) {

            console.error("Template food search error:", error);
            templateItemSearchResults.textContent = "Unable to search food items.";

        }

    });

    templateItemSearch.addEventListener("keydown", (event) => {
        if (event.key !== "Enter") return;

        event.preventDefault();

        const customButton = templateItemSearchResults.querySelector(
            ".template-item-search-result:last-child"
        );

        if (customButton && customButton.textContent.startsWith('Add "')) {
            customButton.click();
        }
    });

    // Display selected template items
    function displayTemplateItems() {

        const containers = {
            frequent: document.getElementById("frequentTemplateItems"),
            occasional: document.getElementById("occasionalTemplateItems"),
            rare: document.getElementById("rareTemplateItems")
        };

        Object.keys(containers).forEach(frequency => {

            const container = containers[frequency];
            container.innerHTML = "";

            templateItems[frequency].forEach(item => {

                const tag = document.createElement("span");
                tag.className = "template-item-tag";

                const name = document.createElement("span");
                name.textContent = item.food_name;

                const removeButton = document.createElement("button");
                removeButton.type = "button";
                removeButton.className = "remove-template-item";
                removeButton.textContent = "×";
                removeButton.title = "Remove item";

                removeButton.addEventListener("click", () => {
                    templateItems[frequency] =
                        templateItems[frequency].filter(
                            existing =>
                                existing.food_name.trim().toLowerCase() !==
                                item.food_name.trim().toLowerCase()
                        );

                    displayTemplateItems();

                });

                tag.appendChild(name);
                tag.appendChild(removeButton);

                container.appendChild(tag);

            });

        });
    }

    // Save shopping template to PostgreSQL
    const saveTemplateButton = document.getElementById("saveTemplateButton");


    const templateSaveMessage = document.getElementById("templateSaveMessage");
    function closeShoppingTemplate() {

        templateModalOverlay.hidden = true;

        templateSaveMessage.textContent = "";
        templateSaveMessage.classList.remove("error");

    }

    saveTemplateButton.addEventListener("click", async () => {

        try {

            saveTemplateButton.disabled = true;
            saveTemplateButton.textContent = "Saving...";

            templateSaveMessage.textContent = "";
            templateSaveMessage.classList.remove("error");

            const response = await fetch("/api/shopping-template", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(templateItems)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Unable to save template.");
            }

            // Count items that were not present in the previous saved template
            // Get IDs from the previously saved template
            const previouslySavedIds = new Set(
                Object.values(savedTemplateItems)
                    .flat()
                    .map(item => item.food_id)
            );

            // Get IDs from the current template
            const currentIds = new Set(
                Object.values(templateItems)
                    .flat()
                    .map(item => item.food_id)
            );

            // Count newly added and removed items
            const newlyAddedCount = [...currentIds]
                .filter(id => !previouslySavedIds.has(id)).length;

            const removedCount = [...previouslySavedIds]
                .filter(id => !currentIds.has(id)).length;

            // Update the saved template snapshot
            savedTemplateItems = JSON.parse(JSON.stringify(templateItems));

            templateSaveMessage.textContent =
                `Template saved successfully! ${newlyAddedCount} added, ${removedCount} removed.`;

            // Refresh the Suggested Items section
            document.dispatchEvent(new Event("shoppingSuggestionsUpdated"));

        } catch (error) {

            console.error("Save template error:", error);

            templateSaveMessage.textContent = error.message;
            templateSaveMessage.classList.add("error");

        } finally {

            saveTemplateButton.disabled = false;
            saveTemplateButton.textContent = "Save Template";

        }

    });

    // Close template modal when clicking outside the popup
    templateModalOverlay.addEventListener("click", (event) => {

        if (event.target === templateModalOverlay) {
            closeShoppingTemplate();
        }

    });

});


document.addEventListener("DOMContentLoaded", () => {

    const addButton = document.getElementById("addShoppingItemButton");
    const saveShoppingListButton = document.getElementById("saveShoppingListButton");
    const downloadShoppingListButton = document.getElementById("downloadShoppingListButton");
    const clearShoppingListButton = document.getElementById("clearShoppingListButton");
    const addForm = document.getElementById("addShoppingItemForm");
    const itemNameInput = document.getElementById("shoppingItemName");
    const quantityInput = document.getElementById("shoppingItemQuantity");
    const confirmAddButton = document.getElementById("confirmAddShoppingItemButton");
    const cancelAddButton = document.getElementById("cancelAddShoppingItemButton");

    const shoppingItemsContainer = document.getElementById("activeShoppingItems");
    const emptyMessage = document.getElementById("emptyShoppingMessage");
    // Shopping progress and summary elements

    const shoppingProgressText = document.getElementById("shoppingProgressText");
    const shoppingProgressFill = document.getElementById("shoppingProgressFill");

    const totalFoodItems = document.getElementById("totalFoodItems");
    const completedFoodItems = document.getElementById("completedFoodItems");
    const remainingFoodItems = document.getElementById("remainingFoodItems");

    const itemSuggestions = document.getElementById("shoppingItemSuggestions");
    let selectedSuggestion = null;
    let suggestionRequestId = 0;

    // Suggested Items section
    const suggestionFilter = document.getElementById("suggestionFilter");
    const suggestionTags = document.getElementById("suggestionTags");
    const noSuggestionsMessage = document.getElementById("noSuggestionsMessage");

    // Load suggested items
    loadSuggestedItems();

    // Load suggested items
    loadSuggestedItems();

    let allSuggestions = [];

    async function loadSuggestedItems() {

        try {
            suggestionTags.textContent = "Loading suggestions...";
            noSuggestionsMessage.hidden = true;

            const response = await fetch("/api/shopping-suggestions");
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Unable to load suggestions.");
            }

            const suggestions = data.suggestions;

            allSuggestions = [
                ...suggestions.essential.map(item => ({ ...item, type: "essential" })),
                ...suggestions.near_expiry.map(item => ({ ...item, type: "near-expiry" })),
                ...suggestions.previously_bought.map(item => ({ ...item, type: "previously-bought" })),
                ...suggestions.templates.map(item => ({ ...item, type: "template" }))
            ];

            // Randomize the placement of all suggestions
            for (let i = allSuggestions.length - 1; i > 0; i--) {

                const j = Math.floor(Math.random() * (i + 1));

                [allSuggestions[i], allSuggestions[j]] =
                    [allSuggestions[j], allSuggestions[i]];

            }

            displaySuggestedItems("all");

        } catch (error) {
            console.error("Shopping suggestions error:", error);
            suggestionTags.textContent = "Unable to load suggestions.";
        }
    }

    // Refresh suggestions when the shopping template is updated
    document.addEventListener("shoppingSuggestionsUpdated", () => {
        loadSuggestedItems();
    });


    // Display suggested items
    function displaySuggestedItems(filter) {

        suggestionTags.innerHTML = "";

        const filteredSuggestions = filter === "all"
            ? allSuggestions
            : allSuggestions.filter(item => item.type === filter);

        if (filteredSuggestions.length === 0) {
            noSuggestionsMessage.hidden = false;
            return;
        }

        noSuggestionsMessage.hidden = true;

        filteredSuggestions.forEach(item => {
            // Create suggestion wrapper
            const tag = document.createElement("div");
            tag.className = "suggestion-tag-wrapper";

            // Create clickable suggestion button
            const button = document.createElement("button");
            button.type = "button";
            button.className = `suggestion-tag ${item.type}-tag`;
            button.textContent = item.food_name;

            // Message displayed after clicking
            const message = document.createElement("span");
            message.className = "suggestion-added-message";
            message.hidden = true;

            if (item.type === "near-expiry" && item.expiration_date) {
                button.title = `Expires on ${item.expiration_date}`;
            }

            tag.append(button, message);
            suggestionTags.appendChild(tag);


            button.addEventListener("click", async () => {

                button.disabled = true;

                try {

                    const response = await fetch("/api/active-shopping-list/items", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            name: item.food_name,
                            quantity: "",
                            food_id: item.food_id || null
                        })
                    });

                    const data = await response.json();

                    if (!response.ok) {
                        throw new Error(data.error || "Unable to add item.");
                    }

                    if (data.already_exists) {
                        message.textContent = "Already in list";
                    } else {

                        // Update the active shopping list
                        shoppingItems.push(data.item);
                        displayShoppingItems();

                        message.textContent = "Added!";
                    }

                    // Remove the suggestion from the data
                    allSuggestions = allSuggestions.filter(
                        suggestion => suggestion !== item
                    );

                    // Replace the button text with the feedback
                    button.textContent = message.textContent;
                    button.disabled = true;

                    // Hide the button after 2 seconds
                    setTimeout(() => {
                        tag.remove();
                    }, 2000);

                    // Show empty message if no suggestions remain
                    if (allSuggestions.length === 0) {
                        noSuggestionsMessage.hidden = false;
                    }

                } catch (error) {

                    console.error("Add suggested item error:", error);
                    button.textContent = "Unable to add";
                    button.disabled = true;

                    setTimeout(() => {
                        message.remove();
                    }, 2000);

                    button.disabled = false;

                }

            });

        });
    }


    // Suggestion filter
    suggestionFilter.addEventListener("change", () => {
        displaySuggestedItems(suggestionFilter.value);
    });

    // Shopping list data
    let shoppingItems = [];
    let nextItemId = 1;

    // Load active shopping list from the database
    loadActiveShoppingList();

    // Save Shopping List
    saveShoppingListButton.addEventListener("click", async () => {

        try {
            const response = await fetch("/api/active-shopping-list/save", {
                method: "POST"
            });

            const data = await response.json();

            if (!response.ok) {
                alert(data.error || "Unable to save shopping list.");
                return;
            }

            // Refresh shopping history without reloading the page
            document.dispatchEvent(new Event("shoppingHistoryUpdated"));

        } catch (error) {
            console.error("Error saving shopping list:", error);
            alert("Something went wrong while saving the shopping list.");
        }
    });

    // Download Active Shopping List
    downloadShoppingListButton.addEventListener("click", () => {

        if (shoppingItems.length === 0) {
            alert("Your shopping list is empty.");
            return;
        }

        let content = "Active Shopping List\n";
        content += `Date: ${new Date().toLocaleDateString()}\n\n`;
        content += "Items:\n";

        shoppingItems.forEach((item, index) => {

            const status = item.completed ? "[Completed]" : "[Pending]";

            content += `${index + 1}. ${item.name} - ${item.quantity || "—"} ${status}\n`;

        });

        const blob = new Blob([content], {
            type: "text/plain;charset=utf-8"
        });

        const url = URL.createObjectURL(blob);

        const link = document.createElement("a");
        link.href = url;
        link.download = "active-shopping-list.txt";

        document.body.appendChild(link);
        link.click();
        link.remove();

        URL.revokeObjectURL(url);

    });

    // Clear Active Shopping List
    clearShoppingListButton.addEventListener("click", async () => {

        if (shoppingItems.length === 0) {
            alert("Your shopping list is already empty.");
            return;
        }

        try {
            const response = await fetch("/api/active-shopping-list/items", {
                method: "DELETE"
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Unable to clear shopping list.");
            }

            shoppingItems = [];

            displayShoppingItems();

        } catch (error) {
            console.error("Clear shopping list error:", error);
            alert(error.message);
        }

    });

    async function loadActiveShoppingList() {

        try {
            shoppingItemsContainer.textContent = "Loading shopping list...";

            const response = await fetch("/api/active-shopping-list");
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Unable to load shopping list.");
            }

            shoppingItems = data.items;

            // Set the next ID based on the existing items
            if (shoppingItems.length > 0) {
                nextItemId = Math.max(...shoppingItems.map(item => item.id)) + 1;
            }

            displayShoppingItems();

        } catch (error) {
            console.error("Active shopping list error:", error);
            shoppingItemsContainer.textContent = "Unable to load shopping list.";
        }
    }

    // Open Add Item form
    addButton.addEventListener("click", () => {
        addForm.hidden = false;
        itemNameInput.focus();
    });

    // Close Add Item form
    cancelAddButton.addEventListener("click", () => {
        closeAddForm();
    });

    function closeAddForm() {
        addForm.hidden = true;
        itemNameInput.value = "";
        quantityInput.value = "";
    }


    // Search food suggestions
    itemNameInput.addEventListener("input", async () => {

        const query = itemNameInput.value.trim();
        selectedSuggestion = null;

        if (query.length < 3) {
            itemSuggestions.replaceChildren();
            itemSuggestions.style.display = "none";
            return;
        }

        const currentRequestId = ++suggestionRequestId;

        try {
            const response = await fetch(
                `/api/shopping-food-suggestions?q=${encodeURIComponent(query)}`
            );

            const data = await response.json();

            // Ignore outdated search responses
            if (currentRequestId !== suggestionRequestId) return;

            if (!response.ok) {
                throw new Error(data.error || "Unable to fetch suggestions.");
            }

            displayFoodSuggestions(data.suggestions);

        } catch (error) {
            console.error("Food suggestion error:", error);
        }
    });

    // Display matching suggestions
    function displayFoodSuggestions(suggestions) {

        itemSuggestions.replaceChildren();

        if (!suggestions || suggestions.length === 0) {
            itemSuggestions.style.display = "none";
            return;
        }

        suggestions.forEach(food => {

            const suggestion = document.createElement("button");
            suggestion.type = "button";
            suggestion.className = "shopping-food-suggestion";

            const name = document.createElement("span");
            name.textContent = food.food_name;

            const category = document.createElement("small");
            category.textContent = food.category;

            suggestion.append(name, category);

            suggestion.addEventListener("click", () => {
                itemNameInput.value = food.food_name;
                selectedSuggestion = food;
                itemSuggestions.replaceChildren();
                itemSuggestions.style.display = "none";
                quantityInput.focus();
            });

            itemSuggestions.appendChild(suggestion);
        });

        itemSuggestions.style.display = "block";
    }

    // Hide suggestions when clicking outside the input area
    document.addEventListener("click", event => {
        if (
            !itemNameInput.contains(event.target) &&
            !itemSuggestions.contains(event.target)
        ) {
            itemSuggestions.style.display = "none";
        }
    });


    // Add item
    confirmAddButton.addEventListener("click", async () => {

        const name = itemNameInput.value.trim();
        const quantity = quantityInput.value.trim();

        if (name.length < 3) {
            alert("Please enter a food item with at least 3 characters.");
            itemNameInput.focus();
            return;
        }

        try {
            const response = await fetch("/api/active-shopping-list/items", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    name: name,
                    quantity: quantity,
                    food_id: selectedSuggestion ? selectedSuggestion.food_id : null
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Unable to add item.");
            }

            shoppingItems.push(data.item);

            displayShoppingItems();
            closeAddForm();

        } catch (error) {
            console.error("Add shopping item error:", error);
            alert(error.message);
        }
    });

    // Add item when Enter is pressed
    [itemNameInput, quantityInput].forEach(input => {
        input.addEventListener("keydown", event => {
            if (event.key === "Enter") {
                event.preventDefault();
                confirmAddButton.click();
            }
        });
    });

    // Update shopping progress and summary
    function updateShoppingProgress() {

        const total = shoppingItems.length;

        const completed = shoppingItems.filter(
            item => item.completed
        ).length;

        const remaining = total - completed;

        const percentage = total > 0
            ? (completed / total) * 100
            : 0;

        // Update progress text
        shoppingProgressText.textContent =
            `${completed} of ${total} items bought`;

        // Update progress bar
        shoppingProgressFill.style.width = `${percentage}%`;

        // Update shopping summary
        totalFoodItems.textContent = total;
        completedFoodItems.textContent = completed;
        remainingFoodItems.textContent = remaining;
    }



    // Display shopping items
    function displayShoppingItems() {

        shoppingItemsContainer.replaceChildren();
        updateShoppingProgress();

        if (shoppingItems.length === 0) {
            shoppingItemsContainer.appendChild(emptyMessage);
            emptyMessage.hidden = false;
            return;
        }

        emptyMessage.hidden = true;

        shoppingItems.forEach(item => {

            const itemRow = document.createElement("div");
            itemRow.className = "active-shopping-item";

            const checkbox = document.createElement("input");
            checkbox.type = "checkbox";
            checkbox.checked = item.completed;

            const name = document.createElement("span");
            name.className = "active-shopping-item-name";
            name.textContent = item.name;

            const quantity = document.createElement("span");
            quantity.className = "active-shopping-item-quantity";
            quantity.textContent = item.quantity || "—";

            // Edit button
            const editButton = document.createElement("button");
            editButton.type = "button";
            editButton.className = "edit-shopping-item";
            editButton.innerHTML = '<i class="fa-solid fa-pen"></i>';
            editButton.title = "Edit item";

            // Remove button
            const removeButton = document.createElement("button");
            removeButton.type = "button";
            removeButton.className = "remove-shopping-item";
            removeButton.innerHTML = '<i class="fa-solid fa-trash"></i>';
            removeButton.title = "Remove item";

            itemRow.append(checkbox, name, quantity, editButton, removeButton);

            // Mark item as bought or unbought
            checkbox.addEventListener("change", async () => {

                const newStatus = checkbox.checked;

                try {
                    const response = await fetch(
                        `/api/active-shopping-list/items/${item.id}`,
                        {
                            method: "PATCH",
                            headers: {
                                "Content-Type": "application/json"
                            },
                            body: JSON.stringify({
                                completed: newStatus
                            })
                        }
                    );

                    const data = await response.json();

                    if (!response.ok) {
                        throw new Error(data.error || "Unable to update item status.");
                    }

                    item.completed = data.item.completed;
                    itemRow.classList.toggle("completed", item.completed);
                    updateShoppingProgress();

                } catch (error) {
                    console.error("Update item status error:", error);
                    alert(error.message);

                    // Restore the previous checkbox state
                    checkbox.checked = item.completed;
                }
            });

            // Remove item
            removeButton.addEventListener("click", async () => {

                try {
                    const response = await fetch(
                        `/api/active-shopping-list/items/${item.id}`,
                        {
                            method: "DELETE"
                        }
                    );

                    const data = await response.json();

                    if (!response.ok) {
                        throw new Error(data.error || "Unable to delete item.");
                    }

                    shoppingItems = shoppingItems.filter(
                        currentItem => currentItem.id !== item.id
                    );

                    displayShoppingItems();

                } catch (error) {
                    console.error("Delete shopping item error:", error);
                    alert(error.message);
                }
            });

            // Edit item
            editButton.addEventListener("click", () => {

                const nameInput = document.createElement("input");
                nameInput.type = "text";
                nameInput.value = item.name;
                nameInput.className = "edit-item-name";

                const quantityInput = document.createElement("input");
                quantityInput.type = "text";
                quantityInput.value = item.quantity;
                quantityInput.className = "edit-item-quantity";

                const saveButton = document.createElement("button");
                saveButton.type = "button";
                saveButton.className = "save-edited-item";
                saveButton.innerHTML = '<i class="fa-solid fa-check"></i>';
                saveButton.title = "Save changes";

                const cancelButton = document.createElement("button");
                cancelButton.type = "button";
                cancelButton.className = "cancel-edited-item";
                cancelButton.innerHTML = '<i class="fa-solid fa-xmark"></i>';
                cancelButton.title = "Cancel editing";

                itemRow.replaceChildren(
                    nameInput,
                    quantityInput,
                    saveButton,
                    cancelButton
                );

                nameInput.focus();

                saveButton.addEventListener("click", async () => {

                    const newName = nameInput.value.trim();
                    const newQuantity = quantityInput.value.trim();

                    if (newName.length < 3) {
                        alert("Food item must contain at least 3 characters.");
                        nameInput.focus();
                        return;
                    }

                    try {
                        const response = await fetch(
                            `/api/active-shopping-list/items/${item.id}`,
                            {
                                method: "PUT",
                                headers: {
                                    "Content-Type": "application/json"
                                },
                                body: JSON.stringify({
                                    name: newName,
                                    quantity: newQuantity
                                })
                            }
                        );

                        const data = await response.json();

                        if (!response.ok) {
                            alert(data.error || "Unable to update shopping item.");
                            return;
                        }

                        // Update the local item using the database response
                        item.name = data.item.name;
                        item.quantity = data.item.quantity;

                        displayShoppingItems();

                    } catch (error) {
                        console.error("Error updating shopping item:", error);
                        alert("Something went wrong while updating the item.");
                    }
                });

                cancelButton.addEventListener("click", () => {
                    displayShoppingItems();
                });

                // Keyboard shortcuts while editing
                [nameInput, quantityInput].forEach(input => {
                    input.addEventListener("keydown", event => {

                        if (event.key === "Enter") {
                            event.preventDefault();
                            saveButton.click();
                        }

                        if (event.key === "Escape") {
                            event.preventDefault();
                            cancelButton.click();
                        }
                    });
                });
            });

            if (item.completed) {
                itemRow.classList.add("completed");
            }

            shoppingItemsContainer.appendChild(itemRow);
        });
    }

});
