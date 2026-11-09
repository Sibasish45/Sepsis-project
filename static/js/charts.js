/**
 * Patient Vital History Trend Charts Module
 */
let chartRiskTrendInstance = null;
let chartVitalsTrendInstance = null;

window.loadPatientHistoryView = async function(patientId) {
    if (!patientId) return;

    try {
        const [patRes, histRes] = await Promise.all([
            fetch(`/api/patients/${patientId}`),
            fetch(`/api/patients/${patientId}/vitals`)
        ]);

        const patData = await patRes.json();
        const histData = await histRes.json();

        if (!patData.success) return;

        const patient = patData.data;
        const history = histData.data || [];

        // Show Content Wrapper
        const contentBox = document.getElementById("patientTimelineContent");
        if (contentBox) contentBox.classList.remove("hidden");

        // Set Patient Metadata
        document.getElementById("profPatientName").textContent = patient.full_name;
        const initials = patient.full_name ? patient.full_name.split(" ").map(n => n[0]).join("").substring(0, 2).toUpperCase() : "P";
        const profAvatar = document.getElementById("profAvatar");
        if (profAvatar) profAvatar.textContent = initials;

        document.getElementById("profPatientMeta").textContent = `Code: ${patient.patient_code} | Age: ${patient.age} yrs | Gender: ${patient.gender === 1 ? 'Male' : 'Female'} | Medical Notes: ${patient.medical_history || 'None'}`;

        const btnNewAss = document.getElementById("btnNewAssessmentForPatient");
        if (btnNewAss) {
            btnNewAss.onclick = () => window.startAssessmentForPatient(patient.id);
        }

        // Render Historical Readings Table
        renderHistoryTable(history);

        // Render Trend Charts
        renderTrendCharts(history);

    } catch (err) {
        console.error("Error loading patient history view:", err);
    }
};

function renderHistoryTable(history) {
    const tbody = document.getElementById("tbodyHistory");
    if (!tbody) return;

    if (!history || history.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" class="text-center text-muted" style="padding: 30px;">No historical assessments recorded yet for this patient.</td></tr>`;
        return;
    }

    tbody.innerHTML = history.map(h => {
        const recordedTime = h.recorded_at ? new Date(h.recorded_at).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' }) : "--";
        const probPct = (h.model_probability * 100).toFixed(1) + "%";

        let bClass = "badge-secondary";
        if (h.risk_category === "High") bClass = "badge-danger";
        else if (h.risk_category === "Moderate") bClass = "badge-warning";
        else if (h.risk_category === "Low") bClass = "badge-success";

        return `
            <tr>
                <td style="font-size: 12px;" class="text-muted">${recordedTime}</td>
                <td><strong>${h.hr || '--'} bpm</strong></td>
                <td>${h.temp || '--'} °C</td>
                <td>${h.sbp || '--'} / ${h.dbp || '--'}</td>
                <td>${h.wbc || '--'} k/uL</td>
                <td><strong style="font-family: var(--font-mono);">${probPct}</strong></td>
                <td><span class="badge ${bClass}">${h.risk_category}</span></td>
                <td>${h.sirs_score}/4</td>
            </tr>
        `;
    }).join("");
}

function renderTrendCharts(history) {
    // Reverse array to show chronological order (oldest to newest)
    const chronoHistory = [...history].reverse();

    const labels = chronoHistory.map(h => h.recorded_at ? new Date(h.recorded_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : "T");
    const riskScores = chronoHistory.map(h => (h.model_probability * 100).toFixed(1));
    const hrData = chronoHistory.map(h => h.hr || null);
    const tempData = chronoHistory.map(h => h.temp || null);
    const sbpData = chronoHistory.map(h => h.sbp || null);

    const isLight = document.documentElement.getAttribute("data-theme") === "light";
    const gridColor = isLight ? 'rgba(0, 0, 0, 0.06)' : 'rgba(255, 255, 255, 0.06)';
    const textColor = isLight ? '#64748b' : '#94a3b8';

    // 1. Sepsis Risk Score Trend Chart
    const ctxRisk = document.getElementById("chartRiskTrend");
    if (ctxRisk) {
        if (chartRiskTrendInstance) chartRiskTrendInstance.destroy();

        chartRiskTrendInstance = new Chart(ctxRisk, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Sepsis Risk Score (%)',
                    data: riskScores,
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.15)',
                    fill: true,
                    tension: 0.35,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    pointBackgroundColor: '#ef4444'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: textColor, font: { family: 'Plus Jakarta Sans' } } }
                },
                scales: {
                    x: { grid: { color: gridColor }, ticks: { color: textColor } },
                    y: { 
                        min: 0, 
                        max: 100, 
                        grid: { color: gridColor }, 
                        ticks: { color: textColor },
                        title: { display: true, text: 'Risk Score (%)', color: textColor } 
                    }
                }
            }
        });
    }

    // 2. Vitals Signs Trend Chart (HR, Temp, SBP)
    const ctxVitals = document.getElementById("chartVitalsTrend");
    if (ctxVitals) {
        if (chartVitalsTrendInstance) chartVitalsTrendInstance.destroy();

        chartVitalsTrendInstance = new Chart(ctxVitals, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    { label: 'Heart Rate (bpm)', data: hrData, borderColor: '#3b82f6', backgroundColor: '#3b82f6', tension: 0.3, pointRadius: 4 },
                    { label: 'Systolic BP (mmHg)', data: sbpData, borderColor: '#10b981', backgroundColor: '#10b981', tension: 0.3, pointRadius: 4 },
                    { label: 'Temp (°C)', data: tempData, borderColor: '#f59e0b', backgroundColor: '#f59e0b', tension: 0.3, pointRadius: 4, yAxisID: 'y1' }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: textColor, font: { family: 'Plus Jakarta Sans' } } }
                },
                scales: {
                    x: { grid: { color: gridColor }, ticks: { color: textColor } },
                    y: { 
                        type: 'linear', 
                        display: true, 
                        position: 'left', 
                        grid: { color: gridColor }, 
                        ticks: { color: textColor },
                        title: { display: true, text: 'bpm / mmHg', color: textColor } 
                    },
                    y1: { 
                        type: 'linear', 
                        display: true, 
                        position: 'right', 
                        grid: { drawOnChartArea: false }, 
                        ticks: { color: textColor },
                        title: { display: true, text: '°C', color: textColor } 
                    }
                }
            }
        });
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const selTimeline = document.getElementById("selectTimelinePatient");
    if (selTimeline) {
        selTimeline.addEventListener("change", (e) => {
            const val = e.target.value;
            if (val) window.loadPatientHistoryView(parseInt(val, 10));
        });
    }
});
