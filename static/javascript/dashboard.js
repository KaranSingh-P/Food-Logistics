async function loadAllergenAlerts() {
    try {
        const response = await fetch("/api/allergen-alerts");

        if (!response.ok) {
            throw new Error("Failed to fetch allergen data");
        }

        const allergens = await response.json();

        const table = document.getElementById("allergenTable");
        const tableBody = document.getElementById("allergenTableBody");
        const noAllergensMessage = document.getElementById("noAllergensMessage");

        tableBody.innerHTML = "";

        if (allergens.length === 0) {

            table.style.display = "none";

            noAllergensMessage.style.display = "block";

        } else {

            table.style.display = "table";

            noAllergensMessage.style.display = "none";

            allergens.forEach(item => {
                const row = document.createElement("tr");

                row.innerHTML = `
                    <td>${item.s_no}</td>
                    <td>${item.item_name}</td>
                    <td>${item.allergy}</td>
                `;

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

        if (!response.ok) {
            throw new Error("Failed to fetch expiring items");
        }

        const items = await response.json();

        const table = document.getElementById("expiringSoonTable");
        const tableBody = document.getElementById("expiringSoonTableBody");
        const noItemsMessage = document.getElementById("noExpiringItemsMessage");

        tableBody.innerHTML = "";

        if (items.length === 0) {

            table.style.display = "none";
            noItemsMessage.style.display = "flex";

        } else {

            table.style.display = "table";
            noItemsMessage.style.display = "none";

            items.forEach(item => {

                const row = document.createElement("tr");

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
                    removeItem(item.id, row);
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


async function removeItem(itemId, row) {
    try {
        const response = await fetch("/api/remove-item", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                id: itemId
            })
        });

        if (!response.ok) {
            throw new Error("Failed to remove item");
        }

        const result = await response.json();

        if (result.success) {
            console.log("The request to delete was successfully sent. Item to be removed:", itemId);
            row.remove();
        }

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
