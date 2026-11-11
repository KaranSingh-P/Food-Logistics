document.addEventListener("DOMContentLoaded", () => {
    const shoppingHistory = document.getElementById("shoppingHistory");
    if (!shoppingHistory) return;
    loadShoppingHistory();

    async function loadShoppingHistory() {
        try {
            shoppingHistory.textContent = "Loading shopping history...";
            const response = await fetch("/api/shopping-history");
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.error || "Unable to load shopping history.");
            }
            displayShoppingHistory(data.shopping_history);
        }
        catch (error) {
            console.error("Shopping history error:", error);
            shoppingHistory.textContent = "Unable to load shopping history.";
        }
    }

    function displayShoppingHistory(lists) {
        shoppingHistory.replaceChildren();
        if (!lists || lists.length === 0) {
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

                historyItem.append(shoppingName, itemCount);
                shoppingHistory.appendChild(historyItem);
            });
        });
    }
});

document.addEventListener("DOMContentLoaded", () => {
    const generatedShopping = document.getElementById("generatedShopping");
    if (!generatedShopping) return;
    loadGeneratedShoppingList();

    async function loadGeneratedShoppingList() {
        try {
            generatedShopping.textContent = "Loading shopping list...";
            const response = await fetch("/api/generated-shopping-list");
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.error || "Unable to load shopping list.");
            }
            displayGeneratedShoppingList(data.shopping_list);
        }
        catch (error) {
            console.error("Shopping list error:", error);
            generatedShopping.textContent = "Unable to load shopping list.";
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

    function displayGeneratedShoppingList(shoppingList) {
        if (!shoppingList || !Array.isArray(shoppingList.items)) {
            throw new Error("Invalid shopping list data received.");
        }
        generatedShopping.replaceChildren();
        const items = shoppingList.items;
        const totalItems = items.length;
        const completedItems = items.filter(item => item.completed).length;
        const remainingItems = totalItems - completedItems;
        const progress = totalItems === 0
            ? 0
            : (completedItems / totalItems) * 100;
        const header = createElement("div", "generated-shopping-header");
        header.appendChild(
            createElement("h2", "", "Generated Shopping List")
        );
        header.appendChild(
            createElement("p", "", "Here's your grocery list based on your selected preferences.")
        );
        generatedShopping.appendChild(header);

        const titleSection = createElement("div", "generated-shopping-title");
        titleSection.appendChild(
            createElement("h1", "", shoppingList.name)
        );
        titleSection.appendChild(
            createElement("p", "", shoppingList.description)
        );
        const meta = createElement("div", "shopping-meta");
        const itemCount = createElement("span");
        const basketIcon = createElement("i", "fa-solid fa-basket-shopping");
        itemCount.append(basketIcon, document.createTextNode(` ${totalItems} food items`));
        const shoppingType = createElement("span");
        const calendarIcon = createElement("i", "fa-regular fa-calendar");
        shoppingType.append(
            calendarIcon,
            document.createTextNode(` ${shoppingList.shopping_type}`)
        );
        meta.append(itemCount, shoppingType);
        titleSection.appendChild(meta);
        generatedShopping.appendChild(titleSection);

        const progressSection = createElement("div", "shopping-progress-section");
        const progressHeader = createElement("div", "shopping-progress-header");
        const progressText = createElement(
            "span",
            "",
            `${completedItems} of ${totalItems} items completed`
        );

        progressHeader.append(
            createElement("h3", "", "Shopping Progress"),
            progressText
        );
        const progressBar = createElement("div", "shopping-progress-bar");
        const progressFill = createElement("div", "shopping-progress-fill");
        progressFill.style.width = `${progress}%`;
        progressBar.appendChild(progressFill);
        progressSection.append(progressHeader, progressBar);
        generatedShopping.appendChild(progressSection);

        const shoppingSection = createElement("div", "shopping-section");
        shoppingSection.append(
            createElement("h3", "", "Shopping Items"),
            createElement(
                "p",
                "shopping-section-description",
                "Check off the food items as you add them to your shopping cart."
            )
        );
        const shoppingItemsList = createElement("div", "shopping-items-list");

        items.forEach(item => {
            const shoppingItem = createElement(
                "div",
                `shopping-item ${item.completed ? "completed" : ""}`
            );
            const checkbox = createElement("input");
            checkbox.type = "checkbox";
            checkbox.checked = item.completed;
            const name = createElement(
                "span",
                "shopping-item-name",
                item.name
            );
            const quantity = createElement(
                "span",
                "shopping-item-quantity",
                item.quantity
            );
            shoppingItem.append(checkbox, name, quantity);
            checkbox.addEventListener("change", () => {
                item.completed = checkbox.checked;
                shoppingItem.classList.toggle("completed", item.completed);
                const completedCount = items.filter(
                    item => item.completed
                ).length;
                const remainingCount = totalItems - completedCount;
                const progressPercentage = totalItems === 0
                    ? 0
                    : (completedCount / totalItems) * 100;
                progressFill.style.width = `${progressPercentage}%`;
                progressText.textContent =
                    `${completedCount} of ${totalItems} items completed`;
                completedRow.querySelector("strong").textContent = completedCount;
                remainingRow.querySelector("strong").textContent = remainingCount;
            });
            shoppingItemsList.appendChild(shoppingItem);
        });
        shoppingSection.appendChild(shoppingItemsList);
        generatedShopping.appendChild(shoppingSection);

        const summary = createElement("div", "shopping-summary");
        summary.appendChild(
            createElement("h3", "", "Shopping Summary")
        );

        function createSummaryRow(label, value, extraClass = "") {
            const row = createElement(
                "div",
                `shopping-summary-row ${extraClass}`
            );
            row.append(
                createElement("span", "", label),
                createElement("strong", "", value)
            );
            return row;
        }

        const totalRow = createSummaryRow("Total Food Items", totalItems);
        const completedRow = createSummaryRow("Completed Items", completedItems);
        const remainingRow = createSummaryRow("Items Remaining", remainingItems, "total-row");

        summary.append(totalRow, completedRow, remainingRow);

        generatedShopping.appendChild(summary);

        const actions = createElement("div", "shopping-actions");
        const actionButtons = [
            ["fa-plus", "Add Item", "add-shopping-item-button"],
            ["fa-floppy-disk", "Save List", "save-shopping-list-button"],
            ["fa-download", "Download List", "download-shopping-list-button"],
            ["fa-trash", "Clear List", "clear-shopping-list-button"]
        ];

        actionButtons.forEach(([iconClass, label, className]) => {
            const button = createElement("button", className);
            button.type = "button";
            const icon = createElement("i", `fa-solid ${iconClass}`);
            button.append(icon, document.createTextNode(` ${label}`));
            actions.appendChild(button);
        });
        generatedShopping.appendChild(actions);
    }
});