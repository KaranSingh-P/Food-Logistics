
const availableAllergies = [
    "Peanuts",
    "Tree Nuts",
    "Milk",
    "Eggs",
    "Wheat",
    "Soy",
    "Fish",
    "Shellfish",
    "Sesame",
    "Gluten",
    "Mustard",
    "Corn",
    "Strawberries",
    "Chocolate"
];

let selectedAllergies = Array.isArray(window.initialAllergies)
    ? [...window.initialAllergies]
    : [];
const searchInput = document.getElementById("allergy-search");
const dropdown = document.getElementById("allergy-dropdown");
const selectedContainer = document.getElementById("selected-allergies");

function updateDropdown() {
    const searchValue = searchInput.value.toLowerCase();
    const filtered = availableAllergies.filter(allergy =>
        allergy.toLowerCase().includes(searchValue) &&
        !selectedAllergies.includes(allergy)
    );
    dropdown.innerHTML = "";
    if (filtered.length === 0) {
        dropdown.innerHTML =
            "<div class='no-results'>No allergies found.</div>";
        dropdown.style.display = "block";
        return;
    }

    filtered.forEach(allergy => {
        const option = document.createElement("div");
        option.className = "allergy-option";
        option.textContent = allergy;
        option.addEventListener("click", () => {
            selectedAllergies.push(allergy);
            searchInput.value = "";
            updateDropdown();
            updateSelectedAllergies();
        });
        dropdown.appendChild(option);
    });
    dropdown.style.display = "block";
}

function updateSelectedAllergies() {
    selectedContainer.innerHTML = "";
    if (selectedAllergies.length === 0) {
        selectedContainer.innerHTML =
            "<span class='no-allergies'>No allergies selected.</span>";
        return;
    }
    selectedAllergies.forEach(allergy => {
        const tag = document.createElement("span");
        tag.className = "allergy-tag";

        const name = document.createElement("span");
        name.textContent = allergy;

        const removeButton = document.createElement("button");

        removeButton.type = "button";
        removeButton.textContent = "×";
        removeButton.setAttribute("aria-label", `Remove ${allergy}`);
        removeButton.addEventListener("click", () => {
            selectedAllergies = selectedAllergies.filter(
                item => item !== allergy
            );
            updateSelectedAllergies();
            updateDropdown();
        });

        tag.appendChild(name);
        tag.appendChild(removeButton);
        selectedContainer.appendChild(tag);
    });
}

searchInput.addEventListener("input", updateDropdown);
searchInput.addEventListener("focus", updateDropdown);

document.addEventListener("click", (event) => {
    if (!event.target.closest(".allergy-search-container")) {
        dropdown.style.display = "none";
    }
});
updateSelectedAllergies();

const settingsForm = document.getElementById("settings-form");
settingsForm.addEventListener("submit", (event) => {
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirm-password").value;
    if (password !== confirmPassword) {
        event.preventDefault();
        let errorBox = document.querySelector(".settings-error");
        if (!errorBox) {
            errorBox = document.createElement("div");
            errorBox.className = "settings-error";
            document.getElementById("save-settings")
                .before(errorBox);
        }
        errorBox.textContent = "Passwords do not match!";
        return;
    }

    document.getElementById("allergies-input").value =
        JSON.stringify(selectedAllergies);
});