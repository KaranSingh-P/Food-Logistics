document.querySelectorAll(".login").forEach((login) => {
    login.addEventListener("click", () => {

        document.querySelector(".hero").style.display = "none";
        document.querySelector(".features").style.display = "none";
        document.querySelector(".about").style.display = "none";
        document.querySelectorAll(".next")[0].style.display = "none";
        document.querySelectorAll(".next")[1].style.display = "none";
        document.querySelector(".login-page").style.display = "flex";
        console.log("Non-Login Page Hidden.");

        document.querySelector(".login-page").display = "flex";
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


// Handle login and registration without page refresh
document.addEventListener("DOMContentLoaded", () => {

    const authForms = [
        {
            form: document.getElementById("loginForm"),
            message: document.getElementById("login-message")
        },
        {
            form: document.getElementById("registerForm"),
            message: document.getElementById("register-message")
        }
    ];

    authForms.forEach(({ form, message }) => {

        if (!form || !message) return;

        form.addEventListener("submit", async (event) => {
            event.preventDefault();

            message.textContent = "";
            message.className = "auth-message";

            const submitButton = form.querySelector('button[type="submit"]');
            const originalText = submitButton.textContent;

            submitButton.disabled = true;
            submitButton.textContent = "Please wait...";

            try {
                const response = await fetch(form.action, {
                    method: "POST",
                    body: new FormData(form)
                });

                const data = await response.json();

                if (data.success) {
                    window.location.href = data.redirect;
                    return;
                }

                message.textContent = data.message || "Something went wrong.";
                message.classList.add("error");

            } catch (error) {
                message.textContent = "Unable to connect. Please try again.";
                message.classList.add("error");

            } finally {
                submitButton.disabled = false;
                submitButton.textContent = originalText;
            }
        });
    });
});



// Forgot Password Popup
document.addEventListener("DOMContentLoaded", () => {

    const forgotPasswordLink = document.getElementById("forgotPasswordLink");
    const forgotPasswordOverlay = document.getElementById("forgotPasswordOverlay");
    const closeForgotPassword = document.getElementById("closeForgotPassword");


    // Recovery email elements
    const recoveryEmail = document.getElementById("recovery-email");
    const recoveryQuestion = document.getElementById("recovery-question");
    const recoveryMessage = document.getElementById("recovery-message");

    let recoveryEmailTimer;

    // Load security question when email is entered
    recoveryEmail.addEventListener("input", () => {

        clearTimeout(recoveryEmailTimer);

        recoveryQuestion.value = "";
        recoveryMessage.textContent = "";

        const email = recoveryEmail.value.trim();

        if (!email || !recoveryEmail.validity.valid) {
            return;
        }

        recoveryEmailTimer = setTimeout(async () => {

            try {
                const response = await fetch("/api/recovery-question", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ email: email })
                });

                const data = await response.json();

                if (data.success) {
                    recoveryQuestion.value = data.question;
                } else {
                    recoveryMessage.textContent = data.message;
                }

            } catch (error) {
                recoveryMessage.textContent =
                    "Unable to retrieve your security question. Please try again.";
            }

        }, 500);
    });


    // Verify recovery details
    const forgotPasswordForm = document.getElementById("forgotPasswordForm");
    const recoveryAnswer = document.getElementById("recovery-answer");
    const recoveryPin = document.getElementById("recovery-pin");
    const verifyRecoveryButton = document.getElementById("verifyRecoveryButton");


    forgotPasswordForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        recoveryMessage.textContent = "";
        recoveryMessage.className = "auth-message";

        verifyRecoveryButton.disabled = true;
        verifyRecoveryButton.textContent = "Verifying...";

        try {
            const response = await fetch("/api/verify-recovery", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    email: recoveryEmail.value.trim(),
                    answer: recoveryAnswer.value.trim(),
                    pin: recoveryPin.value
                })
            });

            const data = await response.json();

            console.log("Recovery verification response:", data);

            if (data.success) {
                recoveryMessage.textContent = data.message;
                recoveryMessage.classList.add("success");

                setTimeout(() => {
                    window.location.href = data.redirect;
                }, 1000);
            } else {
                recoveryMessage.textContent = data.message;
                recoveryMessage.classList.add("error");
            }

        } catch (error) {
            console.error("Recovery verification error:", error);

            recoveryMessage.textContent =
                "Unable to verify your details. Please try again.";
            recoveryMessage.classList.add("error");

        } finally {
            verifyRecoveryButton.disabled = false;
            verifyRecoveryButton.textContent = "Verify Details";
        }
    });



    // Open popup
    forgotPasswordLink.addEventListener("click", (event) => {
        event.preventDefault();
        forgotPasswordOverlay.style.display = "flex";
    });

    // Close popup using the close button
    closeForgotPassword.addEventListener("click", () => {
        forgotPasswordOverlay.style.display = "none";
    });

    // Close popup when clicking outside the modal
    forgotPasswordOverlay.addEventListener("click", (event) => {
        if (event.target === forgotPasswordOverlay) {
            forgotPasswordOverlay.style.display = "none";
        }
    });

    // Close popup using Escape key
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            forgotPasswordOverlay.style.display = "none";
        }
    });

});
