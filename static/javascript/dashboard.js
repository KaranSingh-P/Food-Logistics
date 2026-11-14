
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

        // Clear previous rows
        tableBody.replaceChildren();

        // Display detected allergens
        if (data.detected.length === 0) {

            table.style.display = "none";
            noAllergensMessage.style.display = "block";

        } else {

            table.style.display = "table";
            noAllergensMessage.style.display = "none";

            data.detected.forEach(item => {

                const row = document.createElement("tr");

                // Keep the actual inventory ID for future actions
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

