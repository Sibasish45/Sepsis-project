/** Sepsis CDSS Core Application Script */
document.addEventListener("DOMContentLoaded", () => {
    initSession();
    initNavigation();
    initThemeToggle();
    initLogout();
});
// Session Verification
async function initSession() {
    try {
        const response = await fetch("/api/session");
        const data = await response.json();

        if (!data.authenticated) {
            window.location.href = "/login";
            return;
        }

        const user = data.user;
        const navUserName = document.getElementById("navUserName");
        const navUserRole = document.getElementById("navUserRole");

        if (navUserName) navUserName.textContent = user.full_name || user.username;
        if (navUserRole) navUserRole.textContent = user.role || "STAFF";
        // Store active user in global object
        window.currentUser = user;

        // Initialize Dashboard & Patients Data
        if (window.loadDashboardStats) window.loadDashboardStats();
        if (window.loadPatientOptions) window.loadPatientOptions();
        if (window.loadPatientsDirectory) window.loadPatientsDirectory();

    } catch (err) {
        console.error("Session check failed:", err);
    }
}
// Navigation Tabs
function initNavigation() {
    const navItems = document.querySelectorAll(".nav-item");
    const sections = document.querySelectorAll(".content-section");

    navItems.forEach(item => {
        item.addEventListener("click", () => {
            const targetId = item.getAttribute("data-target");

            navItems.forEach(n => n.classList.remove("active"));
            sections.forEach(s => s.classList.remove("active"));

            item.classList.add("active");
            const targetSec = document.getElementById(targetId);
            if (targetSec) targetSec.classList.add("active");

            // Section Specific Refresh Logic
            if (targetId === "overview-section" && window.loadDashboardStats) {
                window.loadDashboardStats();
            } else if (targetId === "patients-section" && window.loadPatientsDirectory) {
                window.loadPatientsDirectory();
            } else if (targetId === "predict-section" && window.loadPatientOptions) {
                window.loadPatientOptions();
            }
        });
    });
}

// Theme Toggle
function initThemeToggle() {
    const btnToggle = document.getElementById("btnThemeToggle");
    if (!btnToggle) return;

    const savedTheme = localStorage.getItem("theme") || "dark";
    document.documentElement.setAttribute("data-theme", savedTheme);

    btnToggle.addEventListener("click", () => {
        const current = document.documentElement.getAttribute("data-theme");
        const next = current === "light" ? "dark" : "light";
        document.documentElement.setAttribute("data-theme", next);
        localStorage.setItem("theme", next);
    });
}
// Logout Handler
function initLogout() {
    const btnLogout = document.getElementById("btnLogout");
    if (!btnLogout) return;

    btnLogout.addEventListener("click", async () => {
        try {
            await fetch("/api/auth/logout", { method: "POST" });
            window.location.href = "/login";
        } catch (err) {
            console.error("Logout error:", err);
        }
    });
}
// Global Alert Utility
window.showGlobalAlert = function (msg, type = "danger") {
    const alertBox = document.getElementById("globalAlert");
    if (!alertBox) return;

    alertBox.className = `alert alert-${type}`;
    alertBox.textContent = msg;
    alertBox.classList.remove("hidden");

    setTimeout(() => {
        alertBox.classList.add("hidden");
    }, 6000);
};