/**
 * Authentication Module for Staff Login Page
 */
document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("loginForm");
    const loginAlert = document.getElementById("loginAlert");
    const btnLogin = document.getElementById("btnLogin");
    const btnTogglePassword = document.getElementById("btnTogglePassword");
    const btnFillDemo = document.getElementById("btnFillDemoCredentials");

    // Password Show/Hide Toggle
    if (btnTogglePassword) {
        btnTogglePassword.addEventListener("click", () => {
            const passInput = document.getElementById("password");
            if (passInput) {
                const isPass = passInput.type === "password";
                passInput.type = isPass ? "text" : "password";
                btnTogglePassword.innerHTML = isPass ? 
                    `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>` : 
                    `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>`;
            }
        });
    }

    // Click to Auto-fill Demo Credentials
    if (btnFillDemo) {
        btnFillDemo.addEventListener("click", () => {
            const userInput = document.getElementById("username");
            const passInput = document.getElementById("password");
            if (userInput) userInput.value = "admin";
            if (passInput) passInput.value = "Password@123";
            hideLoginAlert();
        });
    }

    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            
            const username = document.getElementById("username").value.trim();
            const password = document.getElementById("password").value;

            if (!username || !password) {
                showLoginAlert("Please enter both username and password.");
                return;
            }

            btnLogin.disabled = true;
            btnLogin.innerHTML = "<span>Authenticating Staff...</span>";
            hideLoginAlert();

            try {
                const response = await fetch("/api/auth/login", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ username, password })
                });

                const data = await response.json();

                if (response.ok && data.success) {
                    window.location.href = "/";
                } else {
                    showLoginAlert(data.error?.message || "Authentication failed.");
                    btnLogin.disabled = false;
                    btnLogin.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" y2="12"/></svg><span>Sign In to Clinical Portal</span>`;
                }
            } catch (err) {
                showLoginAlert("Server network error. Please try again.");
                btnLogin.disabled = false;
                btnLogin.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" y2="12"/></svg><span>Sign In to Clinical Portal</span>`;
            }
        });
    }

    function showLoginAlert(msg) {
        if (loginAlert) {
            loginAlert.textContent = msg;
            loginAlert.classList.remove("hidden");
        }
    }

    function hideLoginAlert() {
        if (loginAlert) {
            loginAlert.classList.add("hidden");
        }
    }
});
