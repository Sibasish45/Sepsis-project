"""
Build Viewer Script for 15 Optimal Features.
Reads dataset_summary_15.json and generates professional dataset_table_viewer HTML files.
"""
import os
import json

def build_viewer_html(json_path="optimal_15_features/dataset_summary_15.json"):
    if not os.path.exists(json_path):
        json_path = "dataset_summary_export.json"

    with open(json_path, "r") as f:
        data = json.load(f)

    summary = data.get("summary", {})
    records_json_str = json.dumps(data.get("sample_records", []))
    stats_json_str = json.dumps(data.get("feature_stats", {}))

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PhysioNet Sepsis Dataset Visualizer (15 Core Features)</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{
            --bg-primary: #0b0f19;
            --bg-card: #151d2a;
            --bg-table-header: #1e293b;
            --border-color: #273549;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent-cyan: #06b6d4;
            --accent-blue: #3b82f6;
            --accent-green: #10b981;
            --accent-red: #ef4444;
            --accent-amber: #f59e0b;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Inter', sans-serif; }}
        body {{ background: var(--bg-primary); color: var(--text-main); min-height: 100vh; padding: 24px; }}
        
        .header-container {{
            background: linear-gradient(135deg, rgba(21, 29, 42, 0.95), rgba(15, 23, 42, 0.95));
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 24px 32px;
            margin-bottom: 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            backdrop-filter: blur(12px);
            box-shadow: 0 10px 25px -5px rgba(0,0,0,0.4);
        }}
        .header-title h1 {{ font-size: 1.6rem; font-weight: 700; color: #fff; display: flex; align-items: center; gap: 12px; }}
        .header-title h1 i {{ color: var(--accent-cyan); }}
        .header-title p {{ color: var(--text-muted); font-size: 0.9rem; margin-top: 6px; }}
        
        .badge {{ padding: 6px 14px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-flex; align-items: center; gap: 6px; letter-spacing: 0.3px; }}
        .badge-cyan {{ background: rgba(6,182,212,0.15); color: #38bdf8; border: 1px solid rgba(6,182,212,0.3); }}
        .badge-red {{ background: rgba(239,68,68,0.15); color: #f87171; border: 1px solid rgba(239,68,68,0.3); }}
        .badge-green {{ background: rgba(16,185,129,0.15); color: #34d399; border: 1px solid rgba(16,185,129,0.3); }}

        /* Stats Grid */
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 24px; }}
        .stat-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 20px;
            display: flex;
            align-items: center;
            gap: 16px;
            transition: all 0.2s ease;
        }}
        .stat-card:hover {{ transform: translateY(-2px); border-color: var(--accent-cyan); }}
        .stat-icon {{
            width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem;
            background: rgba(6,182,212,0.1); color: var(--accent-cyan); border: 1px solid rgba(6,182,212,0.2);
        }}
        .stat-val {{ font-size: 1.4rem; font-weight: 700; color: #fff; }}
        .stat-lbl {{ font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-top: 2px; }}

        /* Main View Container */
        .card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.3);
        }}
        .controls-bar {{
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            gap: 16px;
            margin-bottom: 20px;
        }}
        .search-box {{
            position: relative;
            flex: 1;
            min-width: 260px;
        }}
        .search-box input {{
            width: 100%;
            padding: 10px 16px 10px 40px;
            background: #0b0f19;
            border: 1px solid var(--border-color);
            border-radius: 10px;
            color: #fff;
            font-size: 0.9rem;
            outline: none;
            transition: border-color 0.2s;
        }}
        .search-box input:focus {{ border-color: var(--accent-cyan); }}
        .search-box i {{ position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: var(--text-muted); }}

        .filter-group {{ display: flex; align-items: center; gap: 12px; }}
        .select-custom {{
            background: #0b0f19;
            border: 1px solid var(--border-color);
            color: #fff;
            padding: 9px 16px;
            border-radius: 10px;
            font-size: 0.85rem;
            outline: none;
            cursor: pointer;
        }}

        /* Table Styling */
        .table-responsive {{ overflow-x: auto; border-radius: 12px; border: 1px solid var(--border-color); max-height: 600px; }}
        table {{ width: 100%; border-collapse: collapse; text-align: left; font-size: 0.85rem; white-space: nowrap; }}
        th {{
            background: var(--bg-table-header);
            color: var(--text-muted);
            font-weight: 600;
            padding: 14px 16px;
            position: sticky;
            top: 0;
            z-index: 10;
            border-bottom: 1px solid var(--border-color);
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.5px;
        }}
        td {{ padding: 12px 16px; border-bottom: 1px solid rgba(39, 53, 73, 0.5); color: #e2e8f0; font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; }}
        tr:hover td {{ background: rgba(30, 41, 59, 0.6); }}
        
        .val-missing {{ color: #475569; font-style: italic; }}
        .val-sepsis {{ color: #f87171; font-weight: 600; }}
        .val-normal {{ color: #34d399; font-weight: 500; }}

        /* Pagination */
        .pagination-container {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 20px;
            padding-top: 16px;
            border-top: 1px solid var(--border-color);
        }}
        .page-info {{ font-size: 0.85rem; color: var(--text-muted); }}
        .page-btns {{ display: flex; gap: 8px; }}
        .btn-page {{
            background: #0b0f19;
            border: 1px solid var(--border-color);
            color: #fff;
            padding: 6px 14px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.85rem;
            transition: all 0.2s;
        }}
        .btn-page:hover:not(:disabled) {{ background: var(--accent-cyan); border-color: var(--accent-cyan); color: #000; }}
        .btn-page:disabled {{ opacity: 0.4; cursor: not-allowed; }}
    </style>
</head>
<body>

    <!-- Header Section -->
    <div class="header-container">
        <div class="header-title">
            <h1><i class="fa-solid fa-notes-medical"></i> PhysioNet Sepsis Dataset Table Visualizer</h1>
            <p>Clean Processed Dataset • 15 Core Clinical Features • Updated from <code>physionet_sepsis_processed.csv</code></p>
        </div>
        <div>
            <span class="badge badge-cyan"><i class="fa-solid fa-shield-halved"></i> CDSS Verified</span>
            <span class="badge badge-green"><i class="fa-solid fa-check"></i> 100% Imputed</span>
        </div>
    </div>

    <!-- Executive Metrics Grid -->
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-icon"><i class="fa-solid fa-database"></i></div>
            <div>
                <div class="stat-val">{summary.get("total_records", 0):,}</div>
                <div class="stat-lbl">Total ICU Hours</div>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-icon"><i class="fa-solid fa-hospital-user"></i></div>
            <div>
                <div class="stat-val">{summary.get("total_patients", 0):,}</div>
                <div class="stat-lbl">Unique Patients</div>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-icon" style="color: var(--accent-red); background: rgba(239,68,68,0.1); border-color: rgba(239,68,68,0.2);"><i class="fa-solid fa-circle-exclamation"></i></div>
            <div>
                <div class="stat-val" style="color: #f87171;">{summary.get("sepsis_patients", 0):,}</div>
                <div class="stat-lbl">Sepsis Positive Cases</div>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-icon" style="color: var(--accent-green); background: rgba(16,185,129,0.1); border-color: rgba(16,185,129,0.2);"><i class="fa-solid fa-sliders"></i></div>
            <div>
                <div class="stat-val">{summary.get("feature_count", 15)}</div>
                <div class="stat-lbl">Optimal Clinical Features</div>
            </div>
        </div>
    </div>

    <!-- Data Table View -->
    <div class="card">
        <div class="controls-bar">
            <div class="search-box">
                <i class="fa-solid fa-magnifying-glass"></i>
                <input type="text" id="searchInput" placeholder="Search by Patient ID (e.g. p000001) or vital value...">
            </div>
            <div class="filter-group">
                <select id="statusFilter" class="select-custom">
                    <option value="ALL">All Statuses</option>
                    <option value="SEPSIS">Sepsis Positive (Label = 1)</option>
                    <option value="NORMAL">Normal (Label = 0)</option>
                </select>
                <select id="pageSizeSelect" class="select-custom">
                    <option value="15">15 per page</option>
                    <option value="25" selected>25 per page</option>
                    <option value="50">50 per page</option>
                    <option value="100">100 per page</option>
                </select>
            </div>
        </div>

        <div class="table-responsive">
            <table id="dataTable">
                <thead>
                    <tr>
                        <th>Patient ID</th>
                        <th>ICU Hour</th>
                        <th>HR <span style="font-weight:400; text-transform:none; opacity:0.7;">(bpm)</span></th>
                        <th>O2Sat <span style="font-weight:400; text-transform:none; opacity:0.7;">(%)</span></th>
                        <th>Temp <span style="font-weight:400; text-transform:none; opacity:0.7;">(°C)</span></th>
                        <th>SBP <span style="font-weight:400; text-transform:none; opacity:0.7;">(mmHg)</span></th>
                        <th>MAP <span style="font-weight:400; text-transform:none; opacity:0.7;">(mmHg)</span></th>
                        <th>DBP <span style="font-weight:400; text-transform:none; opacity:0.7;">(mmHg)</span></th>
                        <th>Resp <span style="font-weight:400; text-transform:none; opacity:0.7;">(bpm)</span></th>
                        <th>WBC <span style="font-weight:400; text-transform:none; opacity:0.7;">(k/µL)</span></th>
                        <th>Glucose <span style="font-weight:400; text-transform:none; opacity:0.7;">(mg/dL)</span></th>
                        <th>Lactate <span style="font-weight:400; text-transform:none; opacity:0.7;">(mmol/L)</span></th>
                        <th>Creatinine <span style="font-weight:400; text-transform:none; opacity:0.7;">(mg/dL)</span></th>
                        <th>Platelets <span style="font-weight:400; text-transform:none; opacity:0.7;">(k/µL)</span></th>
                        <th>Age</th>
                        <th>Gender</th>
                        <th>Sepsis Status</th>
                    </tr>
                </thead>
                <tbody id="tableBody">
                    <!-- Dynamic JavaScript Table Rows -->
                </tbody>
            </table>
        </div>

        <div class="pagination-container">
            <div class="page-info" id="pageInfo">Showing 0 to 0 of 0 entries</div>
            <div class="page-btns">
                <button class="btn-page" id="btnPrev"><i class="fa-solid fa-chevron-left"></i> Previous</button>
                <button class="btn-page" id="btnNext">Next <i class="fa-solid fa-chevron-right"></i></button>
            </div>
        </div>
    </div>

    <script>
        const rawRecords = {records_json_str};
        const featureStats = {stats_json_str};

        let filteredRecords = [...rawRecords];
        let currentPage = 1;
        let pageSize = 25;

        const tableBody = document.getElementById("tableBody");
        const searchInput = document.getElementById("searchInput");
        const statusFilter = document.getElementById("statusFilter");
        const pageSizeSelect = document.getElementById("pageSizeSelect");
        const pageInfo = document.getElementById("pageInfo");
        const btnPrev = document.getElementById("btnPrev");
        const btnNext = document.getElementById("btnNext");

        function filterData() {{
            const query = searchInput.value.toLowerCase().trim();
            const status = statusFilter.value;

            filteredRecords = rawRecords.filter(rec => {{
                // Status Filter
                if (status === "SEPSIS" && rec.SepsisLabel !== 1) return false;
                if (status === "NORMAL" && rec.SepsisLabel !== 0) return false;

                // Search query matching
                if (!query) return true;
                return Object.values(rec).some(val => 
                    val !== null && val !== undefined && String(val).toLowerCase().includes(query)
                );
            }});

            currentPage = 1;
            renderTable();
        }}

        function renderTable() {{
            const startIdx = (currentPage - 1) * pageSize;
            const endIdx = Math.min(startIdx + pageSize, filteredRecords.length);
            const pageData = filteredRecords.slice(startIdx, endIdx);

            if (pageData.length === 0) {{
                tableBody.innerHTML = `<tr><td colspan="17" style="text-align:center; padding:30px; color:var(--text-muted);">No matching clinical records found.</td></tr>`;
                pageInfo.innerText = "Showing 0 of 0 entries";
                btnPrev.disabled = true;
                btnNext.disabled = true;
                return;
            }}

            let rowsHtml = "";
            pageData.forEach(row => {{
                const isSepsis = row.SepsisLabel === 1;
                const statusBadge = isSepsis 
                    ? `<span class="badge badge-red"><i class="fa-solid fa-triangle-exclamation"></i> SEPSIS (1)</span>`
                    : `<span class="badge badge-green"><i class="fa-solid fa-check"></i> NORMAL (0)</span>`;

                const genderStr = row.Gender === 1 ? "Male" : (row.Gender === 0 ? "Female" : "-");

                rowsHtml += `
                    <tr>
                        <td style="font-weight:600; color:#38bdf8;">${{row.Patient_ID || '-'}}</td>
                        <td>Hour ${{row.ICULOS || 1}}</td>
                        <td>${{formatVal(row.HR)}}</td>
                        <td>${{formatVal(row.O2Sat)}}</td>
                        <td>${{formatVal(row.Temp)}}</td>
                        <td>${{formatVal(row.SBP)}}</td>
                        <td>${{formatVal(row.MAP)}}</td>
                        <td>${{formatVal(row.DBP)}}</td>
                        <td>${{formatVal(row.Resp)}}</td>
                        <td>${{formatVal(row.WBC)}}</td>
                        <td>${{formatVal(row.Glucose)}}</td>
                        <td>${{formatVal(row.Lactate)}}</td>
                        <td>${{formatVal(row.Creatinine)}}</td>
                        <td>${{formatVal(row.Platelets)}}</td>
                        <td>${{formatVal(row.Age)}}</td>
                        <td>${{genderStr}}</td>
                        <td>${{statusBadge}}</td>
                    </tr>
                `;
            }});

            tableBody.innerHTML = rowsHtml;

            const total = filteredRecords.length;
            pageInfo.innerText = `Showing ${{startIdx + 1}} to ${{endIdx}} of ${{total}} clinical records`;
            btnPrev.disabled = currentPage === 1;
            btnNext.disabled = endIdx >= total;
        }}

        function formatVal(v) {{
            if (v === null || v === undefined) return `<span class="val-missing">N/A</span>`;
            return typeof v === 'number' ? v.toFixed(1) : v;
        }}

        searchInput.addEventListener("input", filterData);
        statusFilter.addEventListener("change", filterData);
        pageSizeSelect.addEventListener("change", (e) => {{
            pageSize = parseInt(e.target.value);
            currentPage = 1;
            renderTable();
        }});

        btnPrev.addEventListener("click", () => {{
            if (currentPage > 1) {{ currentPage--; renderTable(); }}
        }});

        btnNext.addEventListener("click", () => {{
            const maxPages = Math.ceil(filteredRecords.length / pageSize);
            if (currentPage < maxPages) {{ currentPage++; renderTable(); }}
        }});

        // Initial Render
        renderTable();
    </script>
</body>
</html>
"""

    # Save to optimal_15_features/dataset_table_viewer_15.html
    out_15 = os.path.join(os.path.dirname(json_path) or ".", "dataset_table_viewer_15.html")
    with open(out_15, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated viewer HTML at '{out_15}'")

    # Save to templates/dataset_table_viewer.html
    os.makedirs("templates", exist_ok=True)
    with open("templates/dataset_table_viewer.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Updated 'templates/dataset_table_viewer.html'.")

    # Save to root dataset_table_viewer.html
    with open("dataset_table_viewer.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Updated root 'dataset_table_viewer.html'.")

if __name__ == "__main__":
    build_viewer_html()
