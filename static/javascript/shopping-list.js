document.addEventListener("DOMContentLoaded", () => {
    const shoppingHistory = document.getElementById("shoppingHistory");
    // Historical shopping list modal elements
    const historyModalOverlay = document.getElementById("historyModalOverlay");
    const historyModalTitle = document.getElementById("historyModalTitle");
    const historyModalDate = document.getElementById("historyModalDate");
    const historyModalItems = document.getElementById("historyModalItems");
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

    async function loadSuggestedItems() {

        try {
            suggestionTags.textContent = "Loading suggestions...";

            const response = await fetch("/api/shopping-suggestions");
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Unable to load suggestions.");
            }

            console.log("Shopping suggestions:", data.suggestions);

        } catch (error) {
            console.error("Shopping suggestions error:", error);
            suggestionTags.textContent = "Unable to load suggestions.";
        }
    }

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
