/**
 * Patient Management Module
 */
window.loadPatientsDirectory = async function(searchQuery = "") {
    try {
        const url = searchQuery ? `/api/patients?search=${encodeURIComponent(searchQuery)}` : "/api/patients";
        const response = await fetch(url);
        const resData = await response.json();

        if (!response.ok || !resData.success) {
            console.error("Failed to fetch patients.");
            return;
        }

        const patients = resData.data;
        const tbody = document.getElementById("tbodyPatients");
        const countLabel = document.getElementById("patientCountLabel");

        if (countLabel) countLabel.textContent = `Showing ${patients.length} ward patients`;

        if (!tbody) return;

        if (patients.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted" style="padding: 30px;">No patients found. Click "Register New Patient" to create a patient profile.</td></tr>`;
            return;
        }

        tbody.innerHTML = patients.map(p => {
            const genderStr = p.gender === 1 ? "Male" : "Female";
            const initials = p.full_name ? p.full_name.split(" ").map(n => n[0]).join("").substring(0, 2).toUpperCase() : "P";
            
            let riskBadge = `<span class="badge badge-secondary">Not Assessed</span>`;
            if (p.last_risk_category) {
                let bClass = "badge-secondary";
                if (p.last_risk_category === "High") bClass = "badge-danger";
                else if (p.last_risk_category === "Moderate") bClass = "badge-warning";
                else if (p.last_risk_category === "Low") bClass = "badge-success";
                const pct = p.last_model_probability !== undefined && p.last_model_probability !== null ? (p.last_model_probability * 100).toFixed(1) + "%" : "";
                riskBadge = `<span class="badge ${bClass}">${p.last_risk_category} (${pct})</span>`;
            }

            const lastTime = p.last_assessment_time ? new Date(p.last_assessment_time).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' }) : "Never";
            const notes = p.medical_history ? escapeHtml(p.medical_history.length > 35 ? p.medical_history.substring(0, 35) + "..." : p.medical_history) : "<span class='text-muted'>None</span>";

            return `
                <tr>
                    <td>
                        <div class="patient-avatar-pill">
                            <div class="avatar-circle">${initials}</div>
                            <div>
                                <strong>${escapeHtml(p.full_name)}</strong>
                                <div style="font-size: 11px; color: var(--text-muted);">${escapeHtml(p.patient_code)}</div>
                            </div>
                        </div>
                    </td>
                    <td><strong>${p.age} yrs</strong> / ${genderStr}</td>
                    <td>${notes}</td>
                    <td>${riskBadge}</td>
                    <td class="text-muted" style="font-size: 12px;">${lastTime}</td>
                    <td>
                        <div style="display: flex; gap: 6px;">
                            <button class="btn btn-primary btn-sm" onclick="startAssessmentForPatient(${p.id})">
                                Assess
                            </button>
                            <button class="btn btn-outline btn-sm" onclick="viewPatientTimeline(${p.id})">
                                Timeline
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }).join("");

    } catch (err) {
        console.error("Error loading patients directory:", err);
    }
};

window.loadPatientOptions = async function() {
    try {
        const response = await fetch("/api/patients");
        const resData = await response.json();

        if (!resData.success) return;

        const patients = resData.data;
        const selPredict = document.getElementById("selectPatient");
        const selTimeline = document.getElementById("selectTimelinePatient");

        const optionsHtml = '<option value="">-- Choose Patient Profile --</option>' +
            patients.map(p => `<option value="${p.id}">${escapeHtml(p.patient_code)} - ${escapeHtml(p.full_name)} (${p.age} yrs, ${p.gender === 1 ? 'M' : 'F'})</option>`).join("");

        if (selPredict) {
            const currentVal = selPredict.value;
            selPredict.innerHTML = optionsHtml;
            selPredict.value = currentVal;
        }

        if (selTimeline) {
            const currentVal = selTimeline.value;
            selTimeline.innerHTML = optionsHtml;
            selTimeline.value = currentVal;
        }

    } catch (err) {
        console.error("Error loading patient dropdowns:", err);
    }
};

// Global Action Helpers
window.startAssessmentForPatient = function(patientId) {
    const selPredict = document.getElementById("selectPatient");
    if (selPredict) selPredict.value = patientId;

    // Switch Tab to predict-section
    const navBtn = document.querySelector('[data-target="predict-section"]');
    if (navBtn) navBtn.click();
};

window.viewPatientTimeline = function(patientId) {
    const selTimeline = document.getElementById("selectTimelinePatient");
    if (selTimeline) selTimeline.value = patientId;

    // Switch Tab to profile-section
    const navBtn = document.querySelector('[data-target="profile-section"]');
    if (navBtn) navBtn.click();

    if (window.loadPatientHistoryView) {
        window.loadPatientHistoryView(patientId);
    }
};

// Search & Modal Handlers
document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("inputSearchPatients");
    if (searchInput) {
        let timer;
        searchInput.addEventListener("input", (e) => {
            clearTimeout(timer);
            timer = setTimeout(() => {
                window.loadPatientsDirectory(e.target.value.trim());
            }, 300);
        });
    }

    // Modal Add Patient
    const modal = document.getElementById("modalAddPatient");
    const btnOpen = document.getElementById("btnOpenAddPatientModal");
    const btnClose = document.getElementById("btnCloseModal");
    const btnCancel = document.getElementById("btnCancelAddPatient");
    const form = document.getElementById("addPatientForm");

    if (btnOpen && modal) {
        btnOpen.addEventListener("click", () => modal.classList.remove("hidden"));
    }

    const closeModal = () => {
        if (modal) modal.classList.add("hidden");
        if (form) form.reset();
    };

    if (btnClose) btnClose.addEventListener("click", closeModal);
    if (btnCancel) btnCancel.addEventListener("click", closeModal);

    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const fullName = document.getElementById("newFullName").value.trim();
            const age = parseInt(document.getElementById("newAge").value, 10);
            const gender = parseInt(document.getElementById("newGender").value, 10);
            const medHist = document.getElementById("newMedicalHistory").value.trim();

            try {
                const response = await fetch("/api/patients", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ full_name: fullName, age, gender, medical_history: medHist })
                });

                const data = await response.json();

                if (response.ok && data.success) {
                    closeModal();
                    if (window.showGlobalAlert) window.showGlobalAlert(`Patient '${fullName}' registered successfully!`, "success");
                    window.loadPatientsDirectory();
                    window.loadPatientOptions();
                } else {
                    alert(data.error?.message || "Failed to create patient.");
                }
            } catch (err) {
                alert("Network error. Could not save patient.");
            }
        });
    }
});

function escapeHtml(str) {
    if (!str) return "";
    return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
