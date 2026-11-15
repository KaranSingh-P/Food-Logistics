const hamburger = document.getElementById("hamburger");

if (hamburger) {
    hamburger.onclick = function () {
        const menu = document.querySelector("#menu");

        if (menu.style.display === "none") {
            menu.style.display = "flex";
        } else {
            menu.style.display = "none";
        }
    };
}


const showPreferencesButton = document.getElementById("showPreferencesButton");

if (showPreferencesButton) {
    showPreferencesButton.onclick = function () {
        const preferences = document.querySelector("#generate-recipe-preferences");

        if (preferences.style.display === "none") {
            preferences.style.display = "block";
        } else {
            preferences.style.display = "none";
        }
    };
}