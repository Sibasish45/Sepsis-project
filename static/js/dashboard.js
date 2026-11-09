/**
 * Dashboard Overview Module
 */
let riskChartInstance = null;
let cachedAlerts = [];
let currentAlertFilter = "all";

window.loadDashboardStats = async function() {
    try {
        const response = await fetch("/api/dashboard/stats");
        const resData = await response.json();

        if (!response.ok || !resData.success) {
            console.error("Failed to load stats");
            return;
        }

        const data = resData.data;

        // 1. Update KPI Values
        document.getElementById("kpiTotalPatients").textContent = data.total_patients || 0;
        document.getElementById("kpiTotalAssessments").textContent = data.total_assessments || 0;
        document.getElementById("kpiHighRisk").textContent = data.high_risk_count || 0;
        document.getElementById("kpiSirsPositive").textContent = data.sirs_positive_count || 0;

        // Cache alerts feed for client-side filtering
        cachedAlerts = data.recent_alerts || [];

        // 2. Render Risk Distribution Doughnut Chart
        renderRiskChart(data.distribution);

        // 3. Render Recent Alert Feed Table
        applyAlertFilter(currentAlertFilter);

    } catch (err) {
        console.error("Dashboard stats fetch error:", err);
    }
};

function renderRiskChart(dist) {
    const ctx = document.getElementById("chartRiskDistribution");
    if (!ctx) return;

    const low = dist.Low || 0;
    const mod = dist.Moderate || 0;
    const high = dist.High || 0;
    const total = low + mod + high;

    document.getElementById("legendLow").textContent = low;
    document.getElementById("legendMod").textContent = mod;
    document.getElementById("legendHigh").textContent = high;

    if (riskChartInstance) {
        riskChartInstance.destroy();
    }

    const isLight = document.documentElement.getAttribute("data-theme") === "light";

    riskChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Low Risk', 'Moderate Risk', 'High Risk'],
            datasets: [{
                data: [low, mod, high],
                backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
                hoverBackgroundColor: ['#34d399', '#fbbf24', '#f87171'],
                borderWidth: 2,
                borderColor: isLight ? '#ffffff' : '#0f172a'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const val = context.raw || 0;
                            const pct = total > 0 ? ((val / total) * 100).toFixed(1) : 0;
                            return ` ${context.label}: ${val} (${pct}%)`;
                        }
                    }
                }
            },
            cutout: '72%'
        }
    });
}

function applyAlertFilter(filterKey) {
    currentAlertFilter = filterKey;

    // Update active state on filter pills
    const pills = document.querySelectorAll("#alertFilterPills .filter-pill");
    pills.forEach(p => {
        if (p.getAttribute("data-filter") === filterKey) {
            p.classList.add("active");
        } else {
            p.classList.remove("active");
        }
    });

    let filtered = cachedAlerts;
    if (filterKey === "high") {
        filtered = cachedAlerts.filter(a => a.risk_category === "High");
    } else if (filterKey === "moderate") {
        filtered = cachedAlerts.filter(a => a.risk_category === "Moderate");
    } else if (filterKey === "sirs") {
        filtered = cachedAlerts.filter(a => a.sirs_score >= 2);
    }

    renderAlertsTable(filtered);
}

function renderAlertsTable(alerts) {
    const tbody = document.getElementById("tbodyAlerts");
    if (!tbody) return;

    if (!alerts || alerts.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted" style="padding: 30px;">No alerts match the selected filter criteria.</td></tr>`;
        return;
    }

    tbody.innerHTML = alerts.map(a => {
        const probPct = (a.model_probability * 100).toFixed(1);
        let badgeClass = "badge-secondary";
        let fillBg = "#94a3b8";

        if (a.risk_category === "High") {
            badgeClass = "badge-danger";
            fillBg = "#ef4444";
        } else if (a.risk_category === "Moderate") {
            badgeClass = "badge-warning";
            fillBg = "#f59e0b";
        } else if (a.risk_category === "Low") {
            badgeClass = "badge-success";
            fillBg = "#10b981";
        }

        const initials = a.full_name ? a.full_name.split(" ").map(n => n[0]).join("").substring(0, 2).toUpperCase() : "P";
        const formattedDate = a.prediction_time ? new Date(a.prediction_time).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' }) : "--";
        const sirsBadge = a.sirs_score >= 2 ? `<span class="text-warning font-weight-bold">⚠️ ${a.sirs_score}/4</span>` : `<span class="text-muted">${a.sirs_score}/4</span>`;

        return `
            <tr>
                <td>
                    <div class="patient-avatar-pill">
                        <div class="avatar-circle">${initials}</div>
                        <div>
                            <strong>${escapeHtml(a.full_name)}</strong>
                            <div style="font-size: 11px; color: var(--text-muted);">${escapeHtml(a.patient_code)}</div>
                        </div>
                    </div>
                </td>
                <td>
                    <div style="font-family: var(--font-mono); font-weight: 700; margin-bottom: 4px;">${probPct}%</div>
                    <div style="height: 6px; width: 100px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden;">
                        <div style="height: 100%; width: ${probPct}%; background: ${fillBg};"></div>
                    </div>
                </td>
                <td><span class="badge ${badgeClass}">${escapeHtml(a.risk_category)}</span></td>
                <td>${sirsBadge}</td>
                <td class="text-muted" style="font-size: 12px;">${formattedDate}</td>
                <td>
                    <button class="btn btn-outline btn-sm" onclick="viewPatientTimeline(${a.patient_id})">
                        Timeline
                    </button>
                </td>
            </tr>
        `;
    }).join("");
}

function escapeHtml(str) {
    if (!str) return "";
    return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

document.addEventListener("DOMContentLoaded", () => {
    const btnRefresh = document.getElementById("btnRefreshAlerts");
    if (btnRefresh) {
        btnRefresh.addEventListener("click", () => window.loadDashboardStats());
    }

    const pills = document.querySelectorAll("#alertFilterPills .filter-pill");
    pills.forEach(p => {
        p.addEventListener("click", () => {
            const key = p.getAttribute("data-filter");
            applyAlertFilter(key);
        });
    });
});
