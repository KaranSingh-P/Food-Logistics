const availableAllergies = Array.isArray(window.availableAllergies)
    ? window.availableAllergies
    : [];

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

    const securityQuestion = document.getElementById("security-question").value;
    const securityAnswer = document.getElementById("security-answer").value.trim();
    const securityPin = document.getElementById("security-pin").value;
    const confirmSecurityPin = document.getElementById("confirm-security-pin").value;

    // Display validation errors.
    function showError(message) {
        event.preventDefault();

        let errorBox = document.querySelector(".settings-error");

        if (!errorBox) {
            errorBox = document.createElement("div");
            errorBox.className = "settings-error";

            document.getElementById("save-settings").before(errorBox);
        }

        errorBox.textContent = message;
    }

    // Remove any previous error.
    const previousError = document.querySelector(".settings-error");

    if (previousError) {
        previousError.remove();
    }

    // Remove previous success messages.
    document.querySelectorAll(".settings-success").forEach(message => {
        message.remove();
    });

    // Validate password confirmation.
    if (password !== confirmPassword) {
        showError("Passwords do not match!");
        return;
    }

    // Check whether recovery details have been entered.
    const recoveryFields = [
        securityQuestion,
        securityAnswer,
        securityPin,
        confirmSecurityPin
    ];

    const filledFields = recoveryFields.filter(value => value !== "").length;

    // Either all recovery fields must be filled or all must be empty.
    if (filledFields !== 0 && filledFields !== 4) {
        showError("Please complete all Account Recovery fields.");
        return;
    }

    // Validate the security PIN.
    if (filledFields === 4) {

        if (!/^\d{6}$/.test(securityPin)) {
            showError("Security PIN must contain exactly 6 digits.");
            return;
        }

        if (securityPin !== confirmSecurityPin) {
            showError("Security PINs do not match!");
            return;
        }
    }

    // Save selected allergies.
    document.getElementById("allergies-input").value =
        JSON.stringify(selectedAllergies);
});
