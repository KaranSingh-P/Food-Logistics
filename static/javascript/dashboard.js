
async function loadAllergenAlerts() {

    try {
        const response = await fetch("/api/inventory-allergens");
        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(data.message || "Failed to fetch allergen data.");
        }
        const unverifiedItemsBtn = document.getElementById("unverifiedItemsBtn");

        unverifiedItemsBtn.style.display =
            data.unverified.length > 0 ? "inline-block" : "none";

        const table = document.getElementById("allergenTable");
        const tableBody = document.getElementById("allergenTableBody");
        const noAllergensMessage = document.getElementById("noAllergensMessage");
        const setupAllergiesMessage = document.getElementById("setupAllergiesMessage");
        const hasUserAllergies = data.user_allergies.length > 0;

        // Clear previous rows
        tableBody.replaceChildren();

        // Display detected allergens
        if (!hasUserAllergies) {

            // User has not selected any allergies
            table.style.display = "none";
            noAllergensMessage.style.display = "none";
            setupAllergiesMessage.style.display = "block";

        } else {

            setupAllergiesMessage.style.display = "none";

            if (data.detected.length === 0) {

                table.style.display = "none";
                noAllergensMessage.style.display = "block";

            } else {

                table.style.display = "table";
                noAllergensMessage.style.display = "none";

                data.detected.forEach(item => {

                    const row = document.createElement("tr");
                    row.dataset.id = item.inventory_id;

                    const idCell = document.createElement("td");
                    idCell.textContent = item.s_no;

                    const nameCell = document.createElement("td");
                    nameCell.textContent = item.name;

                    const allergyCell = document.createElement("td");
                    allergyCell.textContent = item.allergens.join(", ");

                    row.append(idCell, nameCell, allergyCell);
                    tableBody.appendChild(row);
                });
            }
        }

    } catch (error) {
        console.error("Error loading allergen alerts:", error);
    }
}


async function loadExpiringSoon() {

    try {
        const response = await fetch("/api/expiring-soon");
        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(data.message || "Failed to fetch expiring items.");
        }

        const table = document.getElementById("expiringSoonTable");
        const tableBody = document.getElementById("expiringSoonTableBody");
        const noItemsMessage = document.getElementById("noExpiringItemsMessage");

        // Clear previous rows
        tableBody.replaceChildren();

        const items = data.items;

        if (items.length === 0) {

            table.style.display = "none";
            noItemsMessage.style.display = "flex";

        } else {

            table.style.display = "table";
            noItemsMessage.style.display = "none";

            items.forEach(item => {

                const row = document.createElement("tr");

                row.dataset.id = item.id;

                row.innerHTML = `
                    <td>${item.s_no}</td>
                    <td>${item.item_name}</td>
                    <td>${item.days_left} days</td>
                    <td>
                        <button
                            class="remove-btn"
                            type="button"
                            data-item-id="${item.id}">
                            <i class="fa-solid fa-trash"></i>
                        </button>
                    </td>
                `;

                row.querySelector(".remove-btn").addEventListener("click", () => {
                    removeItem(item.id);
                });

                tableBody.appendChild(row);
            });
        }

    } catch (error) {
        console.error("Error loading expiring items:", error);
    }
}


loadAllergenAlerts();
setInterval(loadAllergenAlerts, 5000);

loadExpiringSoon();
setInterval(loadExpiringSoon, 5000);


async function removeItem(itemId) {

    try {
        const response = await fetch("/api/remove-item-inventory", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                id: itemId
            })
        });

        const result = await response.json();

        if (!response.ok || !result.success) {
            throw new Error(result.message || "Failed to remove item.");
        }

        console.log("Item removed successfully:", itemId);

        // Refresh both tables
        await loadExpiringSoon();
        await loadAllergenAlerts();

    } catch (error) {
        console.error("Error removing item:", error);
    }
}

const selectAllBtn = document.getElementById("selectAllBtn");
const selectNoneBtn = document.getElementById("selectNoneBtn");

selectAllBtn.addEventListener("click", () => {
    const checkboxes = document.querySelectorAll(".shopping-item-checkbox");

    checkboxes.forEach(checkbox => {
        checkbox.checked = true;
    });
});

selectNoneBtn.addEventListener("click", () => {
    const checkboxes = document.querySelectorAll(".shopping-item-checkbox");

    checkboxes.forEach(checkbox => {
        checkbox.checked = false;
    });
});


let dashboardSuggestions = {
    essential: [],
    near_expiry: [],
    previously_bought: [],
    templates: []
};

async function loadDashboardSuggestions() {

    try {
        const response = await fetch("/api/shopping-suggestions");
        const data = await response.json();

        if (!response.ok || !data.suggestions) {
            throw new Error("Failed to fetch shopping suggestions.");
        }

        dashboardSuggestions = data.suggestions;

        displayDashboardSuggestions();

    } catch (error) {
        console.error("Error loading dashboard suggestions:", error);
    }
}


function displayDashboardSuggestions() {

    const table = document.getElementById("dashboardSuggestionsTable");
    const tableBody = document.getElementById("dashboardSuggestionsTableBody");
    const noSuggestionsMessage = document.getElementById("noDashboardSuggestionsMessage");

    tableBody.replaceChildren();

    let items = [];

    const categories = [
        "essential",
        "near_expiry",
        "previously_bought",
        "templates"
    ];

    categories.forEach(category => {

        dashboardSuggestions[category].forEach(item => {

            items.push({
                ...item,
                suggestion_type: category
            });

        });

    });

    // Randomize suggestions
    items.sort(() => Math.random() - 0.5);

    // Display a maximum of 10 suggestions
    items = items.slice(0, 10);
    if (items.length === 0) {
        table.style.display = "none";
        noSuggestionsMessage.style.display = "block";
        return;
    }

    table.style.display = "table";
    noSuggestionsMessage.style.display = "none";

    items.forEach((item, index) => {

        const row = document.createElement("tr");

        const actionCell = document.createElement("td");
        const checkbox = document.createElement("input");

        checkbox.type = "checkbox";
        checkbox.className = "shopping-item-checkbox";
        checkbox.dataset.itemName = item.food_name;
        checkbox.dataset.foodId = item.food_id ?? "";

        actionCell.appendChild(checkbox);

        const nameCell = document.createElement("td");
        nameCell.textContent = item.food_name;

        const categoryCell = document.createElement("td");

        const suggestionLabels = {
            essential: "Essential",
            near_expiry: "Near Expiry",
            previously_bought: "Previously Bought",
            templates: "Template"
        };

        categoryCell.textContent = suggestionLabels[item.suggestion_type];

        row.append(
            actionCell,
            nameCell,
            categoryCell
        );

        tableBody.appendChild(row);

    });
}


loadDashboardSuggestions();


const addDashboardSuggestionsBtn = document.getElementById("addDashboardSuggestionsBtn");

addDashboardSuggestionsBtn.addEventListener("click", async () => {
    const selectedCheckboxes = document.querySelectorAll(
        ".shopping-item-checkbox:checked"
    );

    const message = document.getElementById("dashboardSuggestionsMessage");

    if (selectedCheckboxes.length === 0) {
        message.textContent = "Please select at least one item.";
        message.style.display = "block";
        return;
    }

    message.style.display = "none";
    try {
        const listResponse = await fetch("/api/active-shopping-list");

        if (!listResponse.ok) {
            throw new Error("Unable to access the active shopping list.");
        }

        const items = Array.from(selectedCheckboxes).map(checkbox => ({
            name: checkbox.dataset.itemName,
            food_id: checkbox.dataset.foodId
                ? Number(checkbox.dataset.foodId)
                : null,
            quantity: ""
        }));

        let addedCount = 0;
        let duplicateCount = 0;

        for (const item of items) {
            const response = await fetch("/api/active-shopping-list/items", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(item)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || "Unable to add an item.");
            }

            if (result.already_exists) {
                duplicateCount++;
            } else {
                addedCount++;
            }
        }

        let resultMessage = `${addedCount} item${addedCount !== 1 ? "s" : ""} added successfully.`;

        if (duplicateCount > 0) {
            resultMessage += ` ${duplicateCount} item${duplicateCount !== 1 ? "s" : ""} already existed in your active list.`;
        }

        message.textContent = resultMessage;
        message.style.display = "block";

        setTimeout(() => {
            message.style.display = "none";
        }, 2000);

        await loadDashboardSuggestions();

    } catch (error) {
        console.error("Error accessing active shopping list:", error);
        message.textContent = "Unable to access your active shopping list. Please try again.";
        message.style.display = "block";
        return;
    }
});

const suggestionsScrollArea = document.querySelector(
    ".shopping-list-generation .table-scroll"
);

let autoScrollInterval = null;
let inactivityTimer = null;
let scrollDirection = 1;

function startAutoScroll() {
    if (autoScrollInterval) return;

    autoScrollInterval = setInterval(() => {
        const maxScroll =
            suggestionsScrollArea.scrollHeight -
            suggestionsScrollArea.clientHeight;

        if (maxScroll <= 0) return;

        suggestionsScrollArea.scrollTop += scrollDirection * 1.5;

        if (suggestionsScrollArea.scrollTop >= maxScroll) {
            scrollDirection = -1;
        } else if (suggestionsScrollArea.scrollTop <= 0) {
            scrollDirection = 1;
        }
    }, 20);
}

function pauseAutoScroll() {
    clearInterval(autoScrollInterval);
    autoScrollInterval = null;

    clearTimeout(inactivityTimer);

    inactivityTimer = setTimeout(() => {
        startAutoScroll();
    }, 3000);
}

["mousemove", "mousedown", "wheel", "keydown", "touchstart"].forEach(event => {
    document.addEventListener(event, pauseAutoScroll);
});

pauseAutoScroll();