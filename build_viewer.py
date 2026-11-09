import json

with open('dataset_summary_export.json', 'r') as f:
    data = json.load(f)

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PhysioNet Sepsis CSV Dataset Table Visualizer</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --border-color: #334155;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent-cyan: #06b6d4;
            --accent-blue: #3b82f6;
            --accent-green: #10b981;
            --accent-red: #ef4444;
            --accent-amber: #f59e0b;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Inter', sans-serif; }}
        body {{ background: #0b0f19; color: var(--text-main); min-height: 100vh; padding: 24px; }}
        
        .header-container {{
            background: linear-gradient(135deg, rgba(30,41,59,0.9), rgba(15,23,42,0.9));
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
        .header-title h1 {{ font-size: 1.75rem; font-weight: 700; color: #fff; display: flex; align-items: center; gap: 12px; }}
        .header-title h1 i {{ color: var(--accent-cyan); }}
        .header-title p {{ color: var(--text-muted); font-size: 0.95rem; margin-top: 4px; }}
        
        .badge {{ padding: 6px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 600; display: inline-flex; align-items: center; gap: 6px; }}
        .badge-cyan {{ background: rgba(6,182,212,0.15); color: #38bdf8; border: 1px solid rgba(6,182,212,0.3); }}
        .badge-red {{ background: rgba(239,68,68,0.15); color: #f87171; border: 1px solid rgba(239,68,68,0.3); }}
        .badge-green {{ background: rgba(16,185,129,0.15); color: #34d399; border: 1px solid rgba(16,185,129,0.3); }}

        /* Stats Grid */
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 24px; }}
        .stat-card {{
            background: rgba(30,41,59,0.7);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 20px;
            display: flex;
            align-items: center;
            gap: 16px;
            transition: all 0.3s ease;
        }}
        .stat-card:hover {{ transform: translateY(-2px); border-color: var(--accent-cyan); }}
        .stat-icon {{
            width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.25rem;
            background: rgba(6,182,212,0.1); color: var(--accent-cyan); border: 1px solid rgba(6,182,212,0.2);
        }}
        .stat-val {{ font-size: 1.5rem; font-weight: 700; color: #fff; }}
        .stat-lbl {{ font-size: 0.85rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-top: 2px; }}

        /* Main View Container */
        .card {{
            background: rgba(30,41,59,0.8);
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
            background: #0f172a;
            border: 1px solid var(--border-color);
            border-radius: 10px;
            color: #fff;
            font-size: 0.9rem;
            outline: none;
            transition: border-color 0.2s;
        }}
        .search-box input:focus {{ border-color: var(--accent-cyan); }}
        .search-box i {{ position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: var(--text-muted); }}

        .filter-group {{ display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }}
        .select-input {{
            background: #0f172a;
            border: 1px solid var(--border-color);
            color: var(--text-main);
            padding: 10px 14px;
            border-radius: 10px;
            font-size: 0.9rem;
            outline: none;
            cursor: pointer;
        }}

        /* Table Design */
        .table-responsive {{
            width: 100%;
            overflow-x: auto;
            border-radius: 12px;
            border: 1px solid var(--border-color);
            max-height: 600px;
            position: relative;
        }}
        table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; text-align: left; }}
        thead {{ position: sticky; top: 0; background: #0f172a; z-index: 10; }}
        th {{
            padding: 12px 14px;
            color: #cbd5e1;
            font-weight: 600;
            border-bottom: 2px solid var(--border-color);
            white-space: nowrap;
            cursor: pointer;
            user-select: none;
        }}
        th:hover {{ color: var(--accent-cyan); }}
        td {{
            padding: 10px 14px;
            border-bottom: 1px solid rgba(51,65,85,0.5);
            color: #e2e8f0;
            white-space: nowrap;
            font-family: 'JetBrains Mono', monospace;
        }}
        tbody tr:hover {{ background: rgba(51,65,85,0.4); }}
        tbody tr:nth-child(even) {{ background: rgba(15,23,42,0.3); }}
        .null-val {{ color: #64748b; font-style: italic; font-family: sans-serif; font-size: 0.8rem; }}

        /* Tabs */
        .tab-menu {{ display: flex; gap: 8px; margin-bottom: 20px; border-bottom: 1px solid var(--border-color); padding-bottom: 12px; }}
        .tab-btn {{
            background: transparent;
            border: none;
            color: var(--text-muted);
            padding: 8px 18px;
            font-size: 0.95rem;
            font-weight: 600;
            border-radius: 8px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.2s;
        }}
        .tab-btn.active {{ background: rgba(6,182,212,0.15); color: var(--accent-cyan); border: 1px solid rgba(6,182,212,0.3); }}
        .tab-btn:hover:not(.active) {{ color: #fff; background: rgba(255,255,255,0.05); }}

        /* Pagination */
        .pagination-bar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 16px;
            padding-top: 12px;
            border-top: 1px solid var(--border-color);
        }}
        .btn {{
            background: #0f172a;
            border: 1px solid var(--border-color);
            color: #fff;
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .btn:hover:not(:disabled) {{ border-color: var(--accent-cyan); color: var(--accent-cyan); }}
        .btn:disabled {{ opacity: 0.4; cursor: not-allowed; }}

        /* Progress bar */
        .progress-container {{ width: 100px; height: 6px; background: #334155; border-radius: 3px; overflow: hidden; display: inline-block; vertical-align: middle; }}
        .progress-fill {{ height: 100%; background: linear-gradient(90deg, var(--accent-cyan), var(--accent-blue)); }}
    </style>
</head>
<body>

    <!-- Header -->
    <div class="header-container">
        <div class="header-title">
            <h1><i class="fa-solid fa-table-cells"></i> PhysioNet Sepsis Dataset Table Visualizer</h1>
            <p>Interactive table view & statistical breakdown of <code>physionet_sepsis_combined.csv</code></p>
        </div>
        <div>
            <span class="badge badge-cyan"><i class="fa-solid fa-database"></i> 790,215 Rows</span>
            <span class="badge badge-green" style="margin-left: 8px;"><i class="fa-solid fa-user-doctor"></i> 20,336 ICU Patients</span>
        </div>
    </div>

    <!-- Stat Cards -->
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-icon"><i class="fa-solid fa-list-ol"></i></div>
            <div>
                <div class="stat-val">790,215</div>
                <div class="stat-lbl">Hourly Observations</div>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-icon" style="background: rgba(59,130,246,0.1); color: var(--accent-blue); border-color: rgba(59,130,246,0.2);"><i class="fa-solid fa-hospital-user"></i></div>
            <div>
                <div class="stat-val">20,336</div>
                <div class="stat-lbl">Total ICU Patients</div>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-icon" style="background: rgba(245,158,11,0.1); color: var(--accent-amber); border-color: rgba(245,158,11,0.2);"><i class="fa-solid fa-vial"></i></div>
            <div>
                <div class="stat-val">42</div>
                <div class="stat-lbl">Clinical Features</div>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-icon" style="background: rgba(239,68,68,0.1); color: var(--accent-red); border-color: rgba(239,68,68,0.2);"><i class="fa-solid fa-triangle-exclamation"></i></div>
            <div>
                <div class="stat-val">427</div>
                <div class="stat-lbl">Sepsis (+) Patients (Sampled)</div>
            </div>
        </div>
    </div>

    <!-- Main Card -->
    <div class="card">
        <!-- Tabs -->
        <div class="tab-menu">
            <button class="tab-btn active" onclick="switchTab('explorer')"><i class="fa-solid fa-table"></i> Data Explorer Table</button>
            <button class="tab-btn" onclick="switchTab('schema')"><i class="fa-solid fa-diagram-project"></i> Schema & Column Statistics</button>
        </div>

        <!-- TAB 1: DATA EXPLORER -->
        <div id="tab-explorer">
            <div class="controls-bar">
                <div class="search-box">
                    <i class="fa-solid fa-magnifying-glass"></i>
                    <input type="text" id="searchInput" placeholder="Search by Patient ID (e.g. p000001), Age, or HR..." oninput="applyFilter()">
                </div>
                <div class="filter-group">
                    <label style="color: var(--text-muted); font-size: 0.85rem;">Sepsis Label:</label>
                    <select class="select-input" id="sepsisFilter" onchange="applyFilter()">
                        <option value="ALL">All Records</option>
                        <option value="1">Sepsis Positive (1)</option>
                        <option value="0">Sepsis Negative (0)</option>
                    </select>

                    <label style="color: var(--text-muted); font-size: 0.85rem; margin-left: 10px;">Page Size:</label>
                    <select class="select-input" id="pageSizeSelect" onchange="changePageSize()">
                        <option value="15">15 rows</option>
                        <option value="25" selected>25 rows</option>
                        <option value="50">50 rows</option>
                        <option value="100">100 rows</option>
                    </select>
                </div>
            </div>

            <!-- Table Container -->
            <div class="table-responsive">
                <table id="dataTable">
                    <thead>
                        <tr id="tableHead"></tr>
                    </thead>
                    <tbody id="tableBody"></tbody>
                </table>
            </div>

            <!-- Pagination -->
            <div class="pagination-bar">
                <div style="color: var(--text-muted); font-size: 0.85rem;" id="pageInfo">Showing 1-25 of 350 records</div>
                <div style="display: flex; gap: 8px;">
                    <button class="btn" id="prevBtn" onclick="prevPage()"><i class="fa-solid fa-chevron-left"></i> Previous</button>
                    <button class="btn" id="nextBtn" onclick="nextPage()">Next <i class="fa-solid fa-chevron-right"></i></button>
                </div>
            </div>
        </div>

        <!-- TAB 2: SCHEMA & COLUMN METRICS -->
        <div id="tab-schema" style="display: none;">
            <h3 style="margin-bottom: 16px; font-size: 1.1rem; color: #fff;">Dataset Schema, Feature Categories & Missing Data Rates</h3>
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>Column Name</th>
                            <th>Category</th>
                            <th>Missingness %</th>
                            <th>Missingness Gauge</th>
                            <th>Mean Value</th>
                            <th>Median Value</th>
                        </tr>
                    </thead>
                    <tbody id="schemaBody"></tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        const dataset = {json.dumps(data['sample_data'])};
        const metadata = {json.dumps(data['column_metadata'])};

        let filteredData = [...dataset];
        let currentPage = 1;
        let pageSize = 25;

        // Populate Schema Table
        function renderSchema() {{
            const tbody = document.getElementById('schemaBody');
            tbody.innerHTML = metadata.map(m => `
                <tr>
                    <td><strong style="color: #fff;">${{m.name}}</strong></td>
                    <td><span class="badge badge-cyan">${{m.category}}</span></td>
                    <td style="font-family: monospace;">${{m.missing_pct}}%</td>
                    <td>
                        <div class="progress-container">
                            <div class="progress-fill" style="width: ${{100 - m.missing_pct}}%; background: ${{m.missing_pct > 80 ? '#ef4444' : (m.missing_pct > 30 ? '#f59e0b' : '#10b981')}};"></div>
                        </div>
                    </td>
                    <td>${{m.mean !== null ? m.mean : '-'}}</td>
                    <td>${{m.median !== null ? m.median : '-'}}</td>
                </tr>
            `).join('');
        }}

        // Render Main Table Headers
        function renderTableHead() {{
            const keyCols = ['Patient_ID', 'ICULOS', 'Age', 'Gender', 'HR', 'O2Sat', 'Temp', 'SBP', 'MAP', 'DBP', 'Resp', 'WBC', 'Glucose', 'Lactate', 'SepsisLabel'];
            const tr = document.getElementById('tableHead');
            tr.innerHTML = keyCols.map(col => `<th>${{col}}</th>`).join('');
        }}

        // Render Table Body
        function renderTableBody() {{
            const keyCols = ['Patient_ID', 'ICULOS', 'Age', 'Gender', 'HR', 'O2Sat', 'Temp', 'SBP', 'MAP', 'DBP', 'Resp', 'WBC', 'Glucose', 'Lactate', 'SepsisLabel'];
            const tbody = document.getElementById('tableBody');
            
            const startIdx = (currentPage - 1) * pageSize;
            const endIdx = startIdx + pageSize;
            const pageRecords = filteredData.slice(startIdx, endIdx);

            if (pageRecords.length === 0) {{
                tbody.innerHTML = `<tr><td colspan="${{keyCols.length}}" style="text-align: center; padding: 40px; color: var(--text-muted);">No records matching filter.</td></tr>`;
                return;
            }}

            tbody.innerHTML = pageRecords.map(row => `
                <tr>
                    ${{keyCols.map(col => {{
                        const val = row[col];
                        if (col === 'SepsisLabel') {{
                            return `<td>${{val === 1 ? '<span class="badge badge-red"><i class="fa-solid fa-circle-exclamation"></i> Sepsis (1)</span>' : '<span class="badge badge-green">Normal (0)</span>'}}</td>`;
                        }}
                        if (col === 'Patient_ID') {{
                            return `<td><strong style="color: var(--accent-cyan);">${{val}}</strong></td>`;
                        }}
                        if (col === 'Gender') {{
                            return `<td>${{val === 1 ? 'Male (1)' : 'Female (0)'}}</td>`;
                        }}
                        return `<td>${{val !== null ? val : '<span class="null-val">NaN</span>'}}</td>`;
                    }}).join('')}}
                </tr>
            `).join('');

            // Update Pagination Controls
            document.getElementById('pageInfo').innerText = `Showing ${{startIdx + 1}}-${{Math.min(endIdx, filteredData.length)}} of ${{filteredData.length}} records`;
            document.getElementById('prevBtn').disabled = currentPage === 1;
            document.getElementById('nextBtn').disabled = endIdx >= filteredData.length;
        }}

        function applyFilter() {{
            const searchTerm = document.getElementById('searchInput').value.toLowerCase().trim();
            const sepsisVal = document.getElementById('sepsisFilter').value;

            filteredData = dataset.filter(r => {{
                const matchesSearch = !searchTerm || 
                    (r.Patient_ID && r.Patient_ID.toLowerCase().includes(searchTerm)) ||
                    (r.Age && r.Age.toString().includes(searchTerm)) ||
                    (r.HR && r.HR.toString().includes(searchTerm));

                const matchesSepsis = sepsisVal === 'ALL' || r.SepsisLabel.toString() === sepsisVal;

                return matchesSearch && matchesSepsis;
            }});

            currentPage = 1;
            renderTableBody();
        }}

        function changePageSize() {{
            pageSize = parseInt(document.getElementById('pageSizeSelect').value);
            currentPage = 1;
            renderTableBody();
        }}

        function prevPage() {{
            if (currentPage > 1) {{
                currentPage--;
                renderTableBody();
            }}
        }}

        function nextPage() {{
            if ((currentPage * pageSize) < filteredData.length) {{
                currentPage++;
                renderTableBody();
            }}
        }}

        function switchTab(tabName) {{
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.getElementById('tab-explorer').style.display = tabName === 'explorer' ? 'block' : 'none';
            document.getElementById('tab-schema').style.display = tabName === 'schema' ? 'block' : 'none';
            event.target.classList.add('active');
        }}

        // Initialize Page
        renderSchema();
        renderTableHead();
        renderTableBody();
    </script>
</body>
</html>
"""

with open('dataset_table_viewer.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print('dataset_table_viewer.html generated successfully!')
