document.querySelectorAll(".login").forEach((login) => {
    login.addEventListener("click", () => {
        document.querySelector(".hero").style.display = "none";
        document.querySelector(".features").style.display = "none";
        document.querySelector(".about").style.display = "none";
        document.querySelectorAll(".next")[0].style.display = "none";
        document.querySelectorAll(".next")[1].style.display = "none";
        console.log("Non-Login Page Hidden.");
    });
});

document.querySelectorAll(".home-page").forEach((homep) => {
    homep.addEventListener("click", () => {
        document.querySelector(".hero").style.display = "flex";
        document.querySelector(".features").style.display = "block";
        document.querySelector(".about").style.display = "block";
        document.querySelectorAll(".next")[0].style.display = "block";
        document.querySelectorAll(".next")[1].style.display = "block";
        console.log("Non-Login Page Displayed.");
    });
});