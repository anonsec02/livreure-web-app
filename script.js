// Enhanced JavaScript for Livreure Web App

document.addEventListener("DOMContentLoaded", () => {
    const loginBtn = document.getElementById("loginBtn");
    const signupBtn = document.getElementById("signupBtn");
    const loginModal = document.getElementById("loginModal");
    const signupModal = document.getElementById("signupModal");
    const closeButtons = document.querySelectorAll(".close-button");
    const switchToSignup = document.getElementById("switchToSignup");
    const switchToLogin = document.getElementById("switchToLogin");
    const menuToggle = document.querySelector(".menu-toggle");
    const mainNav = document.querySelector(".main-nav");

    function openModal(modal) {
        modal.style.display = "flex";
    }

    function closeModal(modal) {
        modal.style.display = "none";
    }

    loginBtn.addEventListener("click", () => openModal(loginModal));
    signupBtn.addEventListener("click", () => openModal(signupModal));

    closeButtons.forEach(button => {
        button.addEventListener("click", (event) => {
            closeModal(event.target.closest(".modal"));
        });
    });

    window.addEventListener("click", (event) => {
        if (event.target === loginModal) {
            closeModal(loginModal);
        } else if (event.target === signupModal) {
            closeModal(signupModal);
        }
    });

    switchToSignup.addEventListener("click", (event) => {
        event.preventDefault();
        closeModal(loginModal);
        openModal(signupModal);
    });

    switchToLogin.addEventListener("click", (event) => {
        event.preventDefault();
        closeModal(signupModal);
        openModal(loginModal);
    });

    menuToggle.addEventListener("click", () => {
        mainNav.classList.toggle("active");
    });
});


