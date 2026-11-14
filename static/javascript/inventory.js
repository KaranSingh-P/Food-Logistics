const addItemForm = document.getElementById("add-item-form");
const purchaseDateInput = document.getElementById("item-date");
const expiryDateInput = document.getElementById("item-expiry");
const itemFeedback = document.getElementById("item-feedback");
const purchaseTodayButton = document.getElementById("purchase-today");

// Date restrictions
function getTodayDate() {
    const today = new Date();

    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, "0");
    const day = String(today.getDate()).padStart(2, "0");

    return `${year}-${month}-${day}`;
}

purchaseDateInput.min = "2000-01-01";
purchaseDateInput.max = getTodayDate();

expiryDateInput.min = "2000-01-01";
expiryDateInput.max = "2100-12-31";
const insertItemContainer = document.querySelector(".insert-item");
let detailsHiddenByOutsideClick = false;

function showItemFeedback(message, type) {
    itemFeedback.textContent = message;
    itemFeedback.className = "";
    itemFeedback.classList.add(type);
    setTimeout(() => {
        itemFeedback.textContent = "";
        itemFeedback.className = "";
    }, 5000);
}

function clearItemFeedback() {
    itemFeedback.textContent = "";
    itemFeedback.className = "";
}

let suggestionRequestId = 0;

const itemInput = document.getElementById("type-item");
const suggestionContainer = document.getElementById("item-suggestions");
const itemDetails = document.querySelector(".item-details");
const categorySelect = document.getElementById("item-category");


// Initially hide both sections
suggestionContainer.style.display = "none";
itemDetails.style.display = "none";


// Display matching suggestions while typing

// Display matching suggestions while typing

itemInput.addEventListener("input", async () => {
    clearItemFeedback();
    const query = itemInput.value.trim();
    selectedFood = null;
    categorySelect.value = "";
    itemDetails.style.display = "none";
    itemInput.setCustomValidity("");
    // Generate a new request ID
    const requestId = ++suggestionRequestId;
    // Show how many more characters are required
    if (query.length < 3) {
        suggestionContainer.innerHTML = "";
        const remaining = 3 - query.length;
        const message = document.createElement("div");
        message.className = "suggestion-message";
        message.textContent =
            `Enter ${remaining} more character${remaining === 1 ? "" : "s"} for suggestions`;
        suggestionContainer.appendChild(message);
        suggestionContainer.style.display = "flex";
        return;
    }
    try {
        // Request suggestions from Flask
        const response = await fetch(
            `/api/food-suggestions?q=${encodeURIComponent(query)}`
        );
        if (!response.ok) {
            throw new Error("Failed to retrieve food suggestions.");
        }
        const data = await response.json();
        // Ignore outdated responses
        if (requestId !== suggestionRequestId) {
            return;
        }
        const matches = data.suggestions;
        suggestionContainer.innerHTML = "";
        // Hide suggestions if no matches exist
        if (matches.length === 0) {
            suggestionContainer.style.display = "none";
            return;
        }
        suggestionContainer.style.display = "flex";
        // Display up to 5 suggestions
        matches.slice(0, 5).forEach(food => {
            const button = document.createElement("button");
            button.type = "button";
            button.textContent = food.name;
            button.addEventListener("click", () => {
                selectSuggestedFood(food);
            });
            suggestionContainer.appendChild(button);
        });
        itemFeedback.textContent = "";
        itemFeedback.className = "";
    } catch (error) {
        if (requestId !== suggestionRequestId) {
            return;
        }
        console.error("Error retrieving food suggestions:", error);
        suggestionContainer.style.display = "none";
    }
});

// When the user selects a suggestion
function selectSuggestedFood(food) {
    selectedFood = food;
    itemInput.value = food.name;
    itemInput.readOnly = true;
    categorySelect.value = food.category
        .toLowerCase()
        .replaceAll(" ", "-");
    suggestionContainer.style.display = "none";
    itemDetails.style.display = "flex";
}

// When the user presses Enter without selecting a suggestion
itemInput.addEventListener("keydown", event => {
    if (event.key === "Enter") {
        event.preventDefault();
        const itemName = itemInput.value.trim();
        if (itemName.length < 3) {
            itemInput.setCustomValidity(
                "Please enter at least 3 characters."
            );
            itemInput.reportValidity();
            return;
        }
        selectedFood = null;
        categorySelect.value = "";
        itemInput.readOnly = true;
        suggestionContainer.style.display = "none";
        itemDetails.style.display = "flex";
    }
});

itemInput.addEventListener("click", () => {
    clearItemFeedback();
    if (itemInput.readOnly) {
        itemInput.readOnly = false;
    }
    // If the input is empty, show suggestions instead
    if (itemInput.value.trim() === "") {
        itemDetails.style.display = "none";
        suggestionContainer.innerHTML = "";
        const message = document.createElement("div");
        message.className = "suggestion-message";
        message.textContent = "Enter 3 more characters for suggestions";
        suggestionContainer.appendChild(message);
        suggestionContainer.style.display = "flex";
        detailsHiddenByOutsideClick = false;
        return;
    }
    // Restore details only if the input contains text
    if (detailsHiddenByOutsideClick) {
        itemDetails.style.display = "flex";
        detailsHiddenByOutsideClick = false;
    }
});


addItemForm.addEventListener("submit", async event => {
    event.preventDefault();
    const itemName = itemInput.value.trim();
    const category = categorySelect.value;
    const purchaseDate = purchaseDateInput.value;
    const expiryDate = expiryDateInput.value;
    // Validate item name
    if (itemName.length < 3) {
        showItemFeedback(
            "Food name must contain at least 3 characters.",
            "error"
        );
        itemInput.focus();
        return;
    }
    // Validate category
    if (!category) {
        showItemFeedback(
            "Please select a food category.",
            "error"
        );
        categorySelect.focus();
        return;
    }
    // Validate purchase date
    if (!purchaseDate) {
        showItemFeedback(
            "Please enter the purchase date.",
            "error"
        );
        purchaseDateInput.focus();
        return;
    }
    // Validate expiry date
    if (!expiryDate) {
        showItemFeedback(
            "Please enter the expiration date.",
            "error"
        );
        expiryDateInput.focus();
        return;
    }
    // Compare dates
    if (expiryDate < purchaseDate) {
        showItemFeedback(
            "Expiration date cannot be earlier than purchase date.",
            "error"
        );
        expiryDateInput.focus();
        return;
    }
    // Prepare item data
    const newItem = {
        name: itemName,
        category: category,
        purchase_date: purchaseDate,
        expiration_date: expiryDate
    };
    try {
        const response = await fetch("/api/add-item-inventory", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(newItem)
        });
        const result = await response.json();
        if (!response.ok || !result.success) {
            throw new Error(
                result.message || "Unable to add item."
            );
        }
        console.log("Flask received:", result.item);
        showItemFeedback(
            "Item data successfully sent to Flask!",
            "success"
        );
        loadInventory(1, currentPerPage);

        // Reset all entered values
        addItemForm.reset();
        selectedFood = null;
        itemInput.readOnly = false;
        // Hide suggestions and details
        suggestionContainer.innerHTML = "";
        suggestionContainer.style.display = "none";
        itemDetails.style.display = "none";
        detailsHiddenByOutsideClick = false;
        // Restore date restrictions
        purchaseDateInput.min = "2000-01-01";
        purchaseDateInput.max = getTodayDate();
        expiryDateInput.min = "2000-01-01";
        expiryDateInput.max = "2100-12-31";
        // Refresh inventory
        loadInventory(1, currentPerPage);
        loadAllergenAlerts();
    } catch (error) {
        console.error("Error sending item:", error);
        showItemFeedback(
            error.message || "Something went wrong.",
            "error"
        );
    }
});

[purchaseDateInput, expiryDateInput, categorySelect].forEach(input => {

    input.addEventListener("input", () => {
        itemFeedback.textContent = "";
        itemFeedback.className = "";
    });

});

document.addEventListener("click", event => {
    // Check whether the click happened outside the Add Item box
    if (!insertItemContainer.contains(event.target)) {
        // Hide suggestions
        suggestionContainer.style.display = "none";
        // If the food name is empty, clear its associated details
        if (itemInput.value.trim() === "") {
            selectedFood = null;
            categorySelect.value = "";
            purchaseDateInput.value = "";
            expiryDateInput.value = "";
            // Restore the default date restriction
            expiryDateInput.min = "2000-01-01";
            // Clear suggestions
            suggestionContainer.innerHTML = "";
        }
        // Hide item details
        itemDetails.style.display = "none";
        detailsHiddenByOutsideClick = true;
    }
});

categorySelect.addEventListener("change", clearItemFeedback);
purchaseDateInput.addEventListener("change", clearItemFeedback);
expiryDateInput.addEventListener("change", clearItemFeedback);

purchaseDateInput.addEventListener("change", () => {
    expiryDateInput.min = purchaseDateInput.value || "2000-01-01";
});

purchaseTodayButton.addEventListener("click", () => {
    purchaseDateInput.value = getTodayDate();

    // Update the minimum allowed expiration date
    expiryDateInput.min = purchaseDateInput.value;

    // Clear any previous feedback
    itemFeedback.textContent = "";
    itemFeedback.className = "";
});

// Expiration date shortcuts

document.querySelectorAll(".expiry-shortcuts button").forEach(button => {

    button.addEventListener("click", () => {

        const purchaseDate = purchaseDateInput.value;
        const currentExpiryDate = expiryDateInput.value;

        const days = Number(button.dataset.days);

        // Determine the starting date
        let startingDate = currentExpiryDate || purchaseDate;

        // If the expiration date is invalid, use purchase date
        if (
            !startingDate ||
            Number.isNaN(Date.parse(startingDate))
        ) {
            startingDate = purchaseDate;
        }

        // Check whether a purchase date is available
        if (!startingDate) {
            showItemFeedback(
                "Please select a purchase date first.",
                "error"
            );
            return;
        }

        // Convert starting date into a Date object
        const [year, month, day] = startingDate.split("-").map(Number);

        const expiryDate = new Date(year, month - 1, day);

        // Add selected days
        expiryDate.setDate(expiryDate.getDate() + days);

        // Format as YYYY-MM-DD
        const formattedDate = [
            expiryDate.getFullYear(),
            String(expiryDate.getMonth() + 1).padStart(2, "0"),
            String(expiryDate.getDate()).padStart(2, "0")
        ].join("-");

        // Check maximum allowed date
        if (formattedDate > expiryDateInput.max) {
            showItemFeedback(
                "The calculated expiration date exceeds the allowed range.",
                "error"
            );
            return;
        }

        expiryDateInput.value = formattedDate;

        expiryDateInput.dispatchEvent(new Event("change"));

    });

});

async function loadAllergenAlerts() {

    const allergenTable = document.getElementById("allergenTable");
    const allergenTableBody = document.getElementById("allergenTableBody");
    const noAllergensMessage = document.getElementById("noAllergensMessage");

    const unverifiedTable = document.getElementById("unverifiedTable");
    const unverifiedTableBody = document.getElementById("unverifiedTableBody");
    const noUnverifiedMessage = document.getElementById("noUnverifiedMessage");

    try {
        const response = await fetch("/api/inventory-allergens");
        const data = await response.json();
        if (!response.ok || !data.success) {
            throw new Error(data.message || "Unable to load allergen information.");
        }
        // Clear previous rows
        allergenTableBody.replaceChildren();
        unverifiedTableBody.replaceChildren();
        // Populate detected allergens
        data.detected.forEach((item, index) => {
            const row = document.createElement("tr");
            // Keep the actual database ID for future actions
            row.dataset.id = item.inventory_id;
            const idCell = document.createElement("td");
            idCell.textContent = item.s_no;
            const nameCell = document.createElement("td");
            nameCell.textContent = item.name;
            const allergyCell = document.createElement("td");
            allergyCell.textContent = item.allergens.join(", ");
            row.append(idCell, nameCell, allergyCell);
            allergenTableBody.appendChild(row);
        });        // Populate unverified items

        // Populate unverified items

        data.unverified.forEach(item => {

            const row = document.createElement("tr");
            row.dataset.id = item.inventory_id;

            const idCell = document.createElement("td");
            idCell.textContent = item.s_no;

            const nameCell = document.createElement("td");
            nameCell.textContent = item.name;

            const actionCell = document.createElement("td");
            actionCell.classList.add("verification-actions");

            // Green button
            const safeButton = document.createElement("button");
            safeButton.textContent = "Verify allergen-free";
            safeButton.classList.add("verify-safe");

            safeButton.addEventListener("click", () => {
                saveInventoryVerification(
                    item.inventory_id,
                    "allergen_free",
                    null
                );
            });

            // Red button
            const allergicButton = document.createElement("button");
            allergicButton.textContent = "Verify allergic";
            allergicButton.classList.add("verify-allergic");

            // Dropdown container
            const dropdownContainer = document.createElement("div");
            dropdownContainer.classList.add("allergy-dropdown");
            dropdownContainer.style.display = "none";

            const allergySelect = document.createElement("select");

            const defaultOption = document.createElement("option");
            defaultOption.value = "";
            defaultOption.textContent = "Select an allergy";
            defaultOption.disabled = true;
            defaultOption.selected = true;

            allergySelect.appendChild(defaultOption);

            // Populate saved user allergies
            data.user_allergies.forEach(allergy => {

                const option = document.createElement("option");
                option.value = allergy.allergy_id;
                option.textContent = allergy.allergy_name;

                allergySelect.appendChild(option);
            });

            // Unspecified option
            const unspecifiedOption = document.createElement("option");
            unspecifiedOption.value = "unspecified";
            unspecifiedOption.textContent = "Unspecified";

            allergySelect.appendChild(unspecifiedOption);

            // Confirm button
            const confirmButton = document.createElement("button");
            confirmButton.textContent = "Confirm";
            confirmButton.classList.add("confirm-allergy");

            confirmButton.addEventListener("click", () => {

                if (!allergySelect.value) {
                    alert("Please select an allergy.");
                    return;
                }

                const allergyId =
                    allergySelect.value === "unspecified"
                        ? null
                        : Number(allergySelect.value);

                saveInventoryVerification(
                    item.inventory_id,
                    "allergic",
                    allergyId
                );
            });

            // Toggle dropdown and buttons
            allergicButton.addEventListener("click", () => {

                const isOpen = dropdownContainer.style.display === "flex";

                if (isOpen) {
                    dropdownContainer.style.display = "none";
                    allergicButton.textContent = "Verify allergic";
                    safeButton.style.display = "inline-block";

                } else {
                    dropdownContainer.style.display = "flex";
                    allergicButton.textContent = "X";
                    safeButton.style.display = "none";
                }
            });

            dropdownContainer.append(allergySelect, confirmButton);

            actionCell.append(
                safeButton,
                allergicButton,
                dropdownContainer
            );

            row.append(idCell, nameCell, actionCell);
            unverifiedTableBody.appendChild(row);
        });
        // Toggle tables and empty messages
        allergenTable.style.display =
            data.detected.length > 0 ? "table" : "none";
        noAllergensMessage.style.display =
            data.detected.length > 0 ? "none" : "block";
        unverifiedTable.style.display =
            data.unverified.length > 0 ? "table" : "none";
        noUnverifiedMessage.style.display =
            data.unverified.length > 0 ? "none" : "block";
    } catch (error) {
        console.error("Allergen detection error:", error);
    }
}


async function saveInventoryVerification(inventoryId, status, allergyId) {

    try {

        const response = await fetch("/api/verify-inventory-allergen", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                inventory_id: inventoryId,
                verification_status: status,
                allergy_id: allergyId
            })
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(data.message || "Unable to save verification.");
        }

        // Refresh the allergen tables
        await loadAllergenAlerts();

    } catch (error) {

        console.error("Verification error:", error);
        alert(error.message);
    }
}


let currentPage = 1;
let currentPerPage = 20;
let currentSortBy = "id";
let currentSortOrder = "desc";

function updateSortArrows() {
    // Clear all arrows
    document.querySelectorAll(".sort-arrow").forEach(arrow => {
        arrow.textContent = "";
    });
    // Find the currently active header
    const activeArrow = document.querySelector(
        `#sort-${currentSortBy} .sort-arrow`
    );
    if (!activeArrow) return;
    // S.No. uses the opposite arrow direction
    if (currentSortBy === "id") {
        activeArrow.textContent =
            currentSortOrder === "desc" ? "↑" : "↓";
    } else {
        activeArrow.textContent =
            currentSortOrder === "asc" ? "↓" : "↑";
    }
}

function changeInventorySort(sortBy) {
    if (currentSortBy === sortBy) {
        // Toggle sorting direction
        currentSortOrder =
            currentSortOrder === "asc" ? "desc" : "asc";
    } else {
        // Switch to the newly selected column
        currentSortBy = sortBy;
        // Set its default sorting direction
        currentSortOrder = sortBy === "id" ? "desc" : "asc";
    }
    updateSortArrows();
    // Start from the first page after changing sorting
    loadInventory(1, currentPerPage);
}

document.getElementById("sort-id").addEventListener("click", () => {
    changeInventorySort("id");
});
document.getElementById("sort-name").addEventListener("click", () => {
    changeInventorySort("name");
});
document.getElementById("sort-expiration").addEventListener("click", () => {
    changeInventorySort("expiration");
});
updateSortArrows();

async function loadInventory(page = 1, perPage = currentPerPage) {
    try {
        const response = await fetch(
            `/api/inventory?page=${page}&per_page=${perPage}&sort_by=${currentSortBy}&sort_order=${currentSortOrder}`
        );
        if (!response.ok) {
            throw new Error("Failed to fetch inventory");
        }
        const data = await response.json();
        currentPage = data.page;
        currentPerPage = data.per_page;
        renderInventory(data.items);
        renderPagination(data);
        updateURL();
    } catch (error) {
        console.error("Error loading inventory:", error);
    }
}

function renderInventory(items) {
    const tableBody = document.getElementById("inventoryTableBody");
    tableBody.innerHTML = "";
    items.forEach(item => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${item.s_no}</td>
            <td>${item.name}</td>
            <td>
                <span class="tag ${item.tag.toLowerCase().replace(/\s+/g, "-")}">
                    ${item.tag}
                </span>
            </td>
            <td>${item.purchase_date}</td>
            <td>${item.expiration_date}</td>
            <td>
                <div class="action-buttons">
                    <button
                        class="edit-btn"
                        type="button"
                        data-id="${item.id}">
                        <i class="fa-solid fa-pen"></i>
                    </button>
                    <button
                        class="remove-btn"
                        type="button"
                        data-id="${item.id}">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </div>
            </td>
        `;
        // Edit button
        row.querySelector(".edit-btn").addEventListener("click", () => {
            editInventoryRow(item, row, items);
        });
        // Delete button
        row.querySelector(".remove-btn").addEventListener("click", () => {
            removeItem(item.id);
        });
        tableBody.appendChild(row);
    });
}

function editInventoryRow(item, row, items) {
    const category = item.tag.toLowerCase().replace(/\s+/g, "-");
    // Convert displayed dates (13 Nov 2026) into date input format (2026-11-13)
    function convertDate(date) {
        const [day, month, year] = date.split(" ");
        const months = {
            Jan: "01", Feb: "02", Mar: "03",
            Apr: "04", May: "05", Jun: "06",
            Jul: "07", Aug: "08", Sep: "09",
            Oct: "10", Nov: "11", Dec: "12"
        };
        return `${year}-${months[month]}-${day.padStart(2, "0")}`;
    }
    row.innerHTML = `
        <td>${item.s_no}</td>
        <td>
            <input
                type="text"
                class="edit-name"
                value="${item.name}"
                minlength="3"
                required>
        </td>
        <td>
            <select class="edit-category">
                <option value="perishable">Perishable</option>
                <option value="highly-perishable">Highly perishable</option>
                <option value="semi-perishable">Semi-perishable</option>
                <option value="non-perishable">Non-perishable</option>
                <option value="canned">Canned</option>
                <option value="frozen">Frozen</option>
                <option value="dehydrated">Dehydrated</option>
                <option value="fermented">Fermented</option>
            </select>
        </td>
        <td>
            <input
                type="date"
                class="edit-purchase-date"
                value="${convertDate(item.purchase_date)}">
        </td>
        <td>
            <input
                type="date"
                class="edit-expiry-date"
                value="${convertDate(item.expiration_date)}">
        </td>
        <td>
            <div class="action-buttons">
                <button type="button" class="save-edit-btn">
                    Save
                </button>
                <button type="button" class="cancel-edit-btn">
                    Cancel
                </button>
            </div>
        </td>
    `;
    // Select the item's existing category
    row.querySelector(".edit-category").value = category;
    // Save edited item
    row.querySelector(".save-edit-btn").addEventListener("click", () => {
        saveEditedItem(item, row);
    });
    // Cancel editing and restore the original row
    row.querySelector(".cancel-edit-btn").addEventListener("click", () => {
        renderInventory(items);
    });
}

async function saveEditedItem(item, row) {
    const name = row.querySelector(".edit-name").value.trim();
    const category = row.querySelector(".edit-category").value;
    const purchaseDate = row.querySelector(".edit-purchase-date").value;
    const expiryDate = row.querySelector(".edit-expiry-date").value;
    // Validate item name
    if (name.length < 3) {
        alert("Food name must contain at least 3 characters.");
        return;
    }
    // Validate dates
    if (!purchaseDate || !expiryDate) {
        alert("Please select both dates.");
        return;
    }
    if (expiryDate < purchaseDate) {
        alert("Expiration date cannot be earlier than purchase date.");
        return;
    }
    try {
        const response = await fetch("/api/edit-item-inventory", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                id: item.id,
                name: name,
                category: category,
                purchase_date: purchaseDate,
                expiration_date: expiryDate
            })
        });
        const result = await response.json();
        if (!response.ok || !result.success) {
            alert(result.message || "Unable to update item.");
            return;
        }
        // Refresh inventory after successful update
        loadInventory(currentPage, currentPerPage);
        loadAllergenAlerts();
    } catch (error) {
        console.error("Error updating inventory item:", error);
        alert("Something went wrong while updating the item.");
    }
}

async function removeItem(itemId) {
    try {
        const response = await fetch(
            "/api/remove-item-inventory",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    id: itemId
                })
            }
        );

        if (!response.ok) {
            throw new Error("Failed to remove item");
        }

        const result = await response.json();
        if (!result.success) {
            throw new Error(
                result.message || "Failed to remove item"
            );
        }
        // Reload current page
        loadInventory(
            currentPage,
            currentPerPage
        );
        loadAllergenAlerts();
    } catch (error) {
        console.error(
            "Error removing inventory item:",
            error
        );
    }
}

function renderPagination(data) {

    const paginationTop = document.getElementById("paginationTop");
    const paginationBottom = document.getElementById("paginationBottom");

    // Clear both pagination containers
    paginationTop.innerHTML = "";
    paginationBottom.innerHTML = "";

    // Create pagination for both locations
    createPagination(paginationTop, data);
    createPagination(paginationBottom, data);
}

function createPagination(container, data) {

    const total = data.total;
    const page = data.page;
    const perPage = data.per_page;
    const totalPages = data.total_pages;


    // Summary
    const summary = document.createElement("div");

    summary.className = "pagination-summary";


    if (total === 0) {

        summary.textContent = "Showing 0–0 of 0";

    } else {

        const start = (page - 1) * perPage + 1;
        const end = Math.min(page * perPage, total);

        summary.textContent =
            `Showing ${start}–${end} of ${total}`;
    }


    container.appendChild(summary);


    // Controls
    const controls = document.createElement("div");

    controls.className = "pagination-controls";


    // Previous button
    const previousButton = document.createElement("button");

    previousButton.textContent = "‹ Previous";

    previousButton.setAttribute(
        "aria-label",
        "Previous page"
    );

    previousButton.disabled = page === 1;

    previousButton.addEventListener("click", () => {

        if (page > 1) {
            loadInventory(page - 1);
        }

    });

    controls.appendChild(previousButton);


    // Page numbers
    const pages = getPageNumbers(page, totalPages);

    pages.forEach(pageNumber => {

        if (pageNumber === "...") {

            const ellipsis = document.createElement("span");

            ellipsis.textContent = "…";

            ellipsis.setAttribute(
                "aria-hidden",
                "true"
            );

            controls.appendChild(ellipsis);

            return;
        }


        const pageButton = document.createElement("button");

        pageButton.textContent = pageNumber;


        if (pageNumber === page) {

            pageButton.setAttribute(
                "aria-current",
                "page"
            );

        }


        pageButton.addEventListener("click", () => {

            loadInventory(pageNumber);

        });


        controls.appendChild(pageButton);
    });


    // Next button
    const nextButton = document.createElement("button");

    nextButton.textContent = "Next ›";

    nextButton.setAttribute(
        "aria-label",
        "Next page"
    );

    nextButton.disabled =
        page === totalPages || totalPages === 0;


    nextButton.addEventListener("click", () => {

        if (page < totalPages) {
            loadInventory(page + 1);
        }

    });


    controls.appendChild(nextButton);


    container.appendChild(controls);


    // Page size
    const pageSizeLabel = document.createElement("label");

    pageSizeLabel.className = "page-size";


    const select = document.createElement("select");

    select.innerHTML = `
        <option value="20">20</option>
        <option value="50">50</option>
        <option value="100">100</option>
    `;


    select.value = perPage;


    select.addEventListener("change", event => {

        const newPerPage =
            parseInt(event.target.value, 10);

        currentPerPage = newPerPage;

        currentPage = 1;

        loadInventory(
            currentPage,
            currentPerPage
        );

    });


    pageSizeLabel.appendChild(select);

    pageSizeLabel.appendChild(
        document.createTextNode(" per page")
    );


    container.appendChild(pageSizeLabel);
}

function getPageNumbers(currentPage, totalPages) {

    // Small number of pages
    if (totalPages <= 7) {

        return Array.from(
            { length: totalPages },
            (_, index) => index + 1
        );

    }


    const pages = [];

    pages.push(1);


    if (currentPage > 4) {
        pages.push("...");
    }


    const start = Math.max(2, currentPage - 1);
    const end = Math.min(
        totalPages - 1,
        currentPage + 1
    );


    for (let page = start; page <= end; page++) {
        pages.push(page);
    }


    if (currentPage < totalPages - 3) {
        pages.push("...");
    }


    pages.push(totalPages);

    return pages;
}

function updateURL() {

    const params = new URLSearchParams();

    params.set("page", currentPage);
    params.set("per_page", currentPerPage);

    const newURL =
        `${window.location.pathname}?${params.toString()}`;

    window.history.pushState({}, "", newURL);
}

function getInitialPage() {

    const params = new URLSearchParams(
        window.location.search
    );

    const page = parseInt(
        params.get("page"),
        10
    );

    const perPage = parseInt(
        params.get("per_page"),
        10
    );


    if ([20, 50, 100].includes(perPage)) {
        currentPerPage = perPage;
    }


    if (page && page > 0) {
        currentPage = page;
    }


    return currentPage;
}

// Initial load
const initialPage = getInitialPage();

loadInventory(initialPage, currentPerPage);
loadAllergenAlerts();

