/**
 * Sepsis Risk Prediction & Assessment Form Handler
 */
document.addEventListener("DOMContentLoaded", () => {
    const predictForm = document.getElementById("predictForm");
    
    // Quick Clinical Presets
    const btnPresetNormal = document.getElementById("btnPresetNormal");
    const btnPresetSirs = document.getElementById("btnPresetSirs");
    const btnPresetHighRisk = document.getElementById("btnPresetHighRisk");
    const btnPrintReport = document.getElementById("btnPrintReport");

    if (btnPresetNormal) {
        btnPresetNormal.addEventListener("click", () => {
            fillFormValues({
                HR: 75, Temp: 36.8, O2Sat: 98, SBP: 120, DBP: 80, MAP: 93.3, Resp: 14, WBC: 6.5, Glucose: 95, Lactate: 1.0, Platelets: 220, Creatinine: 0.8, BUN: 14, pH: 7.40, ICULOS: 12
            });
        });
    }

    if (btnPresetSirs) {
        btnPresetSirs.addEventListener("click", () => {
            fillFormValues({
                HR: 98, Temp: 38.4, O2Sat: 94, SBP: 102, DBP: 65, MAP: 77.3, Resp: 22, WBC: 12.8, Glucose: 140, Lactate: 2.1, Platelets: 170, Creatinine: 1.1, BUN: 22, pH: 7.36, ICULOS: 24
            });
        });
    }

    if (btnPresetHighRisk) {
        btnPresetHighRisk.addEventListener("click", () => {
            fillFormValues({
                HR: 125, Temp: 39.4, O2Sat: 89, SBP: 82, DBP: 50, MAP: 60.7, Resp: 28, WBC: 18.5, Glucose: 210, Lactate: 4.2, Platelets: 95, Creatinine: 2.1, BUN: 38, pH: 7.28, ICULOS: 48
            });
        });
    }

    if (btnPrintReport) {
        btnPrintReport.addEventListener("click", () => {
            window.print();
        });
    }

    function fillFormValues(vals) {
        Object.keys(vals).forEach(key => {
            const el = document.getElementById(`input${key}`);
            if (el) el.value = vals[key];
        });

        // Ensure accordion is expanded if lab values are filled
        const detailsAcc = document.querySelector(".lab-details-accordion");
        if (detailsAcc) detailsAcc.open = true;
    }

    if (!predictForm) return;

    predictForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const btnRun = document.getElementById("btnRunPrediction");
        const patientId = document.getElementById("selectPatient").value;

        if (!patientId) {
            alert("Please select a ward patient profile before running the risk evaluation.");
            return;
        }

        // Form Data Extraction
        const formData = new FormData(predictForm);
        const payload = {};
        formData.forEach((value, key) => {
            if (value !== "" && value !== null) {
                payload[key] = isNaN(value) ? value : parseFloat(value);
            }
        });
        payload.patient_id = parseInt(patientId, 10);

        btnRun.disabled = true;
        btnRun.innerHTML = "<span>Evaluating ML Sepsis Model & SIRS...</span>";

        try {
            const response = await fetch("/api/predict", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const resData = await response.json();

            if (response.ok && resData.success) {
                renderAssessmentResult(resData.data);
                if (window.loadDashboardStats) window.loadDashboardStats();
                if (window.loadPatientsDirectory) window.loadPatientsDirectory();
            } else {
                alert(resData.error?.message || "Assessment error.");
            }
        } catch (err) {
            console.error("Prediction submission error:", err);
            alert("Network error while communicating with CDSS server.");
        } finally {
            btnRun.disabled = false;
            btnRun.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg><span>Evaluate Sepsis Risk Score</span>`;
        }
    });
});

function renderAssessmentResult(data) {
    const placeholder = document.getElementById("resultPlaceholder");
    const content = document.getElementById("resultContent");
    const btnPrint = document.getElementById("btnPrintReport");

    if (placeholder) placeholder.classList.add("hidden");
    if (content) content.classList.remove("hidden");
    if (btnPrint) btnPrint.classList.remove("hidden");

    // 1. Model Details
    const model = data.model;
    const sirs = data.sirs;
    const indicators = data.follow_up_indicators || [];

    document.getElementById("resModelVersion").textContent = model.version || "RF_v1.0";
    document.getElementById("resRiskPercent").textContent = `${model.risk_score_percent}%`;

    const boxCategory = document.getElementById("boxRiskCategory");
    const tagCategory = document.getElementById("resRiskCategory");
    const fillMeter = document.getElementById("resRiskFill");

    // Clear previous risk classes
    boxCategory.className = "risk-display-box";

    if (model.risk_category === "High") {
        boxCategory.classList.add("risk-high");
        tagCategory.textContent = "CRITICAL / HIGH RISK";
    } else if (model.risk_category === "Moderate") {
        boxCategory.classList.add("risk-mod");
        tagCategory.textContent = "MODERATE RISK";
    } else {
        boxCategory.classList.add("risk-low");
        tagCategory.textContent = "LOW RISK";
    }

    fillMeter.style.width = `${Math.min(model.risk_score_percent, 100)}%`;

    // 2. SIRS Breakdown
    const sirsBadge = document.getElementById("resSirsBadge");
    sirsBadge.textContent = sirs.status;
    sirsBadge.className = sirs.score >= 2 ? "badge badge-danger" : "badge badge-success";

    const sirsList = document.getElementById("resSirsList");
    if (sirsList && sirs.criteria_breakdown) {
        sirsList.innerHTML = Object.keys(sirs.criteria_breakdown).map(k => {
            const item = sirs.criteria_breakdown[k];
            const icon = item.met ? '<span class="text-danger status-icon">✓ CRITERIA MET</span>' : '<span class="text-muted status-icon">✕ WITHIN NORMAL</span>';
            const valStr = item.value !== null && item.value !== undefined ? ` (${item.value})` : "";
            return `
                <li class="sirs-item">
                    <span><strong>${escapeHtml(item.name)}</strong>${valStr}</span>
                    ${icon}
                </li>
            `;
        }).join("");
    }

    // 3. Clinical Follow-Up Indicators & Bundle Advice
    const indList = document.getElementById("resIndicatorsList");
    if (indList) {
        let itemsHtml = "";
        
        if (model.risk_category === "High" || sirs.score >= 2) {
            itemsHtml += `
                <div class="indicator-card high">
                    <h5>🚨 Emergency 1-Hour Sepsis Bundle Recommended</h5>
                    <p class="mb-0">Measure blood lactate, obtain blood cultures before antibiotics, administer broad-spectrum IV antimicrobials, and begin rapid administration of 30ml/kg crystalloid for hypotension or lactate ≥ 4 mmol/L.</p>
                </div>
            `;
        }

        if (indicators.length > 0) {
            itemsHtml += indicators.map(ind => `
                <div class="indicator-card ${ind.severity}">
                    <h5>${escapeHtml(ind.title)}</h5>
                    <p class="mb-0">${escapeHtml(ind.message)}</p>
                </div>
            `).join("");
        } else if (model.risk_category === "Low") {
            itemsHtml += `
                <div class="indicator-card low">
                    <h5>🟢 Standard Routine Ward Surveillance</h5>
                    <p class="mb-0">Patient currently meets low risk threshold. Continue standard vital sign monitoring every 4-6 hours as per ward protocol.</p>
                </div>
            `;
        }

        indList.innerHTML = itemsHtml;
    }

    // 4. Clinical Disclaimer
    if (data.disclaimer) {
        document.getElementById("resDisclaimer").textContent = data.disclaimer;
    }
}

function escapeHtml(str) {
    if (!str) return "";
    return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
