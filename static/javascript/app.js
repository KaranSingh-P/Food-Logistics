
const hamburger = document.getElementById("hamburger");
const menu = document.getElementById("menu");

if (hamburger && menu) {
    hamburger.onclick = function (event) {
        event.stopPropagation();

        if (menu.style.display === "none") {
            menu.style.display = "flex";
        } else {
            menu.style.display = "none";
        }
    };

    // Close the menu when clicking outside it.
    document.addEventListener("click", function (event) {
        if (
            !hamburger.contains(event.target) &&
            !menu.contains(event.target)
        ) {
            menu.style.display = "none";
        }
    });

    // Close the menu after clicking a navigation link.
    menu.querySelectorAll("a").forEach(link => {
        link.addEventListener("click", function () {
            menu.style.display = "none";
        });
    });
}
