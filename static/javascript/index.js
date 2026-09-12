document.querySelectorAll(".login").forEach((login) => {
    login.addEventListener("click", () => {
        
        document.querySelector(".hero").style.display = "none";
        document.querySelector(".features").style.display = "none";
        document.querySelector(".about").style.display = "none";
        document.querySelectorAll(".next")[0].style.display = "none";
        document.querySelectorAll(".next")[1].style.display = "none";
        document.querySelector(".login-page").style.display = "flex";
        console.log("Non-Login Page Hidden.");

        document.querySelector(".login-page").display="flex";
        document.querySelector(".login-page").scrollIntoView({
            behavior: "smooth",
            block: "start"
        });
    });
});

document.querySelectorAll(".home-page").forEach((homep) => {
    homep.addEventListener("click", () => {
        document.querySelector(".hero").style.display = "flex";
        document.querySelector(".features").style.display = "block";
        document.querySelector(".about").style.display = "block";
        document.querySelectorAll(".next")[0].style.display = "block";
        document.querySelectorAll(".next")[1].style.display = "block";
        document.querySelector(".login-page").style.display = "none";
        console.log("Non-Login Page Displayed.");
    });
});