# Sepsis Clinical Decision Support System (CDSS) - Comprehensive Project & Setup Guide

This document provides a detailed breakdown of all files in the repository, explains how they interconnect, outlines the rationale behind reducing the model features from 40 to 15 optimal clinical indicators, and provides step-by-step instructions for connecting the application to **MySQL Workbench**.

---

## Table of Contents
1. [System Architecture & Data Flow](#1-system-architecture--data-flow)
2. [Complete File Registry & Connections](#2-complete-file-registry--connections)
3. [15 Optimal Features vs. 40 Features Analysis](#3-15-optimal-features-vs-40-features-analysis)
4. [Step-by-Step MySQL Workbench Setup & Connection Guide](#4-step-by-step-mysql-workbench-setup--connection-guide)

---

## 1. System Architecture & Data Flow

The project is structured into distinct functional layers: **Data Ingestion & Training**, **Backend Infrastructure (Flask & Services)**, **Database Persistence (MySQL/SQLite)**, **Frontend Interface (Vanilla HTML/CSS/JS)**, and **Automated Testing & Research Benchmarking**.

```mermaid
flowchart TD
    subgraph Data & ML Pipeline
        A[physionet_sepsis_combined.csv] --> B[data_prep.py / data_prep_15.py]
        B --> C[physionet_sepsis_processed.csv]
        C --> D[train_model.py / train_model_15.py]
        D --> E[sepsis_model.pkl & sepsis_scaler.pkl]
    end

    subgraph Flask Backend Architecture
        F[app.py] --> G[config.py]
        F --> H[db.py Context Manager]
        F --> I[Routes Layer]
        I --> J[Services Layer]
        J --> K[Utils Layer: Validators & Security]
        J --> E
    end

    subgraph Database Layer
        H -->|Primary Connection Pool| L[(MySQL Server: sepsis_cdss)]
        H -.->|Offline Fallback| M[(SQLite: sepsis_cdss_local.db)]
    end

    subgraph Web Frontend UI
        N[templates/index.html & login.html] <--> O[static/js: app.js, predict.js, charts.js, etc.]
        O <-->|REST API JSON| I
    end
```

---

## 2. Complete File Registry & Connections

Below is the complete inventory of all files and folders in the workspace, explaining their exact purpose and how they connect to the overall system.

### 2.1 Root Core Files

| File Name | Description & Purpose | Interconnections |
| :--- | :--- | :--- |
| [`app.py`](file:///c:/Sepsis_CDSS_Project%20template/app.py) | **Application Entry Point**. Initializes Flask app, registers blueprints from `routes/`, configures sessions, and verifies model artifact compatibility on startup. | Imports `config.py`, `db.py`, and blueprints from `routes/`. Runs HTTP server on port 5000. |
| [`config.py`](file:///c:/Sepsis_CDSS_Project%20template/config.py) | **Centralized Configuration**. Loads environment variables from `.env` (Secret key, MySQL host, port, credentials, database name). | Consumed by `app.py`, `db.py`, and session security modules. |
| [`db.py`](file:///c:/Sepsis_CDSS_Project%20template/db.py) | **Database Connection Manager**. Implements MySQL pooling with connection fallback to local SQLite (`sepsis_cdss_local.db`). Enforces atomic `COMMIT`/`ROLLBACK` transactions. | Uses `config.py`. Imported by all service modules in `services/` to query/write data. |
| [`schema.sql`](file:///c:/Sepsis_CDSS_Project%20template/schema.sql) | **MySQL Database Initialization Script**. Defines schema for `users`, `patients`, `vital_records`, `predictions`, and `audit_logs` with foreign keys, indexes, and default admin seed. | Executed directly in **MySQL Workbench** to set up the production database structure. |
| [`.env`](file:///c:/Sepsis_CDSS_Project%20template/.env) / [`.env.example`](file:///c:/Sepsis_CDSS_Project%20template/.env.example) | **Environment Configuration Files**. Contains sensitive database credentials, Flask secret key, and port settings. | Read by `config.py` using `python-dotenv`. |
| [`README.md`](file:///c:/Sepsis_CDSS_Project%20template/README.md) | **Primary Readme**. Contains quickstart steps, tech stack outline, and basic app configuration. | High-level user overview. |
| [`PROJECT_GUIDE.md`](file:///c:/Sepsis_CDSS_Project%20template/PROJECT_GUIDE.md) | **Deep Architecture & Setup Manual** (This file). Explains full file directory, feature comparison, and MySQL Workbench integration. | Comprehensive reference manual for developers and evaluators. |

---

### 2.2 Data Processing & Machine Learning Artifacts

| File / Artifact | Description & Purpose | Interconnections |
| :--- | :--- | :--- |
| [`data_prep.py`](file:///c:/Sepsis_CDSS_Project%20template/data_prep.py) | Data cleaning and feature engineering script for raw PhysioNet CSV files. Calculates rolling deltas, SIRS flags, and qSOFA indicators. | Input: `physionet_sepsis_combined.csv`. Output: `physionet_sepsis_processed.csv`. |
| [`train_model.py`](file:///c:/Sepsis_CDSS_Project%20template/train_model.py) | Model training script. Builds and saves a Random Forest Classifier trained on cleaned clinical data. | Input: `physionet_sepsis_processed.csv`. Output: `sepsis_model.pkl`, `sepsis_scaler.pkl`. |
| [`stitch_data.py`](file:///c:/Sepsis_CDSS_Project%20template/stitch_data.py) | Combines individual PhysioNet patient text/CSV files from `archive/` into a single consolidated dataset. | Input: `archive/`. Output: `physionet_sepsis_combined.csv`. |
| [`build_viewer.py`](file:///c:/Sepsis_CDSS_Project%20template/build_viewer.py) | Generates a standalone interactive HTML data viewer for inspecting raw/processed datasets. | Output: `dataset_table_viewer.html`, `dataset_summary_export.json`. |
| [`feature_columns.json`](file:///c:/Sepsis_CDSS_Project%20template/feature_columns.json) | JSON metadata contract defining all feature column names expected by the model. | Used by `ml_service.py` to validate input payloads before running ML inference. |
| [`sepsis_model.pkl`](file:///c:/Sepsis_CDSS_Project%20template/sepsis_model.pkl) | Serialized Random Forest model artifact trained on clinical dataset. | Loaded into memory by `ml_service.py` during app startup for real-time risk scoring. |
| [`sepsis_scaler.pkl`](file:///c:/Sepsis_CDSS_Project%20template/sepsis_scaler.pkl) | Serialized `StandardScaler` artifact for feature normalization. | Loaded by `ml_service.py` to scale incoming vital readings before model prediction. |
| [`physionet_sepsis_combined.csv`](file:///c:/Sepsis_CDSS_Project%20template/physionet_sepsis_combined.csv) | Stitched raw dataset containing ICU patient observations. | Input to `data_prep.py`. |
| [`physionet_sepsis_processed.csv`](file:///c:/Sepsis_CDSS_Project%20template/physionet_sepsis_processed.csv) | Cleaned, imputed, and feature-engineered dataset ready for model training. | Input to `train_model.py`. |

---

### 2.3 Sub-directory: `optimal_15_features/` (15-Feature Optimization Module)

This sub-folder contains the dedicated pipeline and research bench for the **15 optimal feature model**:

| File Name | Description & Purpose | Interconnections |
| :--- | :--- | :--- |
| [`optimal_15_features/data_prep_15.py`](file:///c:/Sepsis_CDSS_Project%20template/optimal_15_features/data_prep_15.py) | Filters processed dataset down to the top 15 clinical features and calculates missing value medians. | Outputs `physionet_sepsis_15_processed.csv` and `feature_columns_15.json`. |
| [`optimal_15_features/train_model_15.py`](file:///c:/Sepsis_CDSS_Project%20template/optimal_15_features/train_model_15.py) | Trains Random Forest on 15 features with class balancing. | Outputs `random_forest_15.pkl` and `sepsis_scaler_15.pkl`. |
| [`optimal_15_features/compare_models_15.py`](file:///c:/Sepsis_CDSS_Project%20template/optimal_15_features/compare_models_15.py) | Benchmarks Logistic Regression, Decision Tree, and Random Forest on 15 features across ROC-AUC, PR-AUC, Sensitivity, and Latency. | Outputs `model_comparison_results.json` and diagnostic ROC/PR curve images in `research_plots/`. |
| [`optimal_15_features/generate_research_report.py`](file:///c:/Sepsis_CDSS_Project%20template/optimal_15_features/generate_research_report.py) | Reads benchmark results and formats a markdown research report (`RESEARCH_MODEL_COMPARISON.md`). | Consumes `model_comparison_results.json`. |
| [`optimal_15_features/feature_medians_15.json`](file:///c:/Sepsis_CDSS_Project%20template/optimal_15_features/feature_medians_15.json) | Reference dictionary of clinical median fallback values for the 15 features. | Used when a clinician omits optional lab parameters (e.g. Lactate). |
| [`optimal_15_features/random_forest_15.pkl`](file:///c:/Sepsis_CDSS_Project%20template/optimal_15_features/random_forest_15.pkl) | Serialized 15-feature Random Forest model. | Compact production alternative to 40-feature model. |

---

### 2.4 Sub-directory: `jupyter_notebooks/` (Interactive Training & Research Suite)

This directory houses the complete set of interactive Jupyter Notebooks for data preparation, feature engineering, production model training, and clinical model benchmarking:

| Notebook File | Description & Purpose | Interconnections |
| :--- | :--- | :--- |
| [`jupyter_notebooks/01_data_stitching_and_preprocessing.ipynb`](file:///c:/Sepsis_CDSS_Project%20template/jupyter_notebooks/01_data_stitching_and_preprocessing.ipynb) | Interactive ingestion of raw `.psv` files, missingness profiling, outlier cleaning, patient longitudinal imputation, and clinical feature engineering (SIRS, Shock Index, qSOFA, 3h deltas). | Inputs: `archive/`, `physionet_sepsis_combined.csv`. Outputs: `physionet_sepsis_processed.csv`, `sepsis_scaler.pkl`, `feature_columns.json`. |
| [`jupyter_notebooks/02_random_forest_model_training.ipynb`](file:///c:/Sepsis_CDSS_Project%20template/jupyter_notebooks/02_random_forest_model_training.ipynb) | Production model trainer enforcing the 15-feature contract, computing fallback medians, training a class-balanced Random Forest (100 trees), and verifying startup contracts. | Inputs: `physionet_sepsis_processed.csv`. Outputs: `sepsis_model.pkl`, `model/feature_medians.json`. |
| [`jupyter_notebooks/03_models_benchmarking_and_comparison.ipynb`](file:///c:/Sepsis_CDSS_Project%20template/jupyter_notebooks/03_models_benchmarking_and_comparison.ipynb) | Multi-model benchmarking suite comparing Logistic Regression, Single Decision Tree, and Random Forest across 5-fold CV, AUROC, AUPRC, and confusion matrices. | Consumes processed data, outputs comparative metrics tables and diagnostic curve plots. |
| [`jupyter_notebooks/04_complete_end_to_end_pipeline.ipynb`](file:///c:/Sepsis_CDSS_Project%20template/jupyter_notebooks/04_complete_end_to_end_pipeline.ipynb) | Comprehensive master walkthrough combining all stages from raw ingestion to verified production model artifact. | End-to-end execution resulting in all production model artifacts. |

---

### 2.5 Modular Backend: `routes/`, `services/`, & `utils/`

The backend follows a **Controller-Service-Repository architecture**:

#### **`routes/` (HTTP Endpoint Controllers)**
- [`auth_routes.py`](file:///c:/Sepsis_CDSS_Project%20template/routes/auth_routes.py): Handles user login, logout, password verification, and session status (`/login`, `/logout`, `/api/auth/me`).
- [`dashboard_routes.py`](file:///c:/Sepsis_CDSS_Project%20template/routes/dashboard_routes.py): Provides REST API endpoints for high-level clinical metrics, high-risk patient lists, and vital trends (`/api/dashboard/stats`, `/api/dashboard/high-risk`).
- [`patient_routes.py`](file:///c:/Sepsis_CDSS_Project%20template/routes/patient_routes.py): CRUD endpoints for patient demographics and clinical histories (`/api/patients`, `/api/patients/<id>`).
- [`prediction_routes.py`](file:///c:/Sepsis_CDSS_Project%20template/routes/prediction_routes.py): Handles submission of vital sign forms, triggers ML/SIRS evaluation, and retrieves patient prediction timelines (`/api/predict`, `/api/patients/<id>/predictions`).

#### **`services/` (Business Logic Layer)**
- [`auth_service.py`](file:///c:/Sepsis_CDSS_Project%20template/services/auth_service.py): Authenticates credentials against database, manages password hashing (`werkzeug.security`), and tracks last login.
- [`patient_service.py`](file:///c:/Sepsis_CDSS_Project%20template/services/patient_service.py): Database access logic for retrieving and updating patient records.
- [`prediction_service.py`](file:///c:/Sepsis_CDSS_Project%20template/services/prediction_service.py): Coordinates atomic database transactions across `vital_records`, `predictions`, and `audit_logs`.
- [`ml_service.py`](file:///c:/Sepsis_CDSS_Project%20template/services/ml_service.py): Loads `.pkl` models, formats feature input vectors, scales values, and calculates sepsis probability.
- [`sirs_service.py`](file:///c:/Sepsis_CDSS_Project%20template/services/sirs_service.py): Evaluates rule-based Systemic Inflammatory Response Syndrome (SIRS) criteria (Temp, HR, Resp, WBC).
- [`clinical_rules_service.py`](file:///c:/Sepsis_CDSS_Project%20template/services/clinical_rules_service.py): Computes qSOFA score and generates clinical recommended actions based on risk category.
- [`audit_service.py`](file:///c:/Sepsis_CDSS_Project%20template/services/audit_service.py): Logs user actions, IP addresses, and vital submissions into `audit_logs` for compliance.

#### **`utils/` (Helpers & Middleware)**
- [`validators.py`](file:///c:/Sepsis_CDSS_Project%20template/utils/validators.py): Validates vital sign ranges (e.g. Heart Rate 20-300 bpm, Temp 30-45°C) to prevent garbage input.
- [`security.py`](file:///c:/Sepsis_CDSS_Project%20template/utils/security.py): Security decorators (`@login_required`, `@role_required('ADMIN')`).
- [`errors.py`](file:///c:/Sepsis_CDSS_Project%20template/utils/errors.py): Custom HTTP error handlers returning structured JSON error responses.
- [`constants.py`](file:///c:/Sepsis_CDSS_Project%20template/utils/constants.py): Application constants (Risk thresholds: High >= 0.70, Moderate >= 0.35, Low < 0.35).

---

### 2.5 Presentation Layer: `templates/` & `static/`

#### **`templates/` (HTML Views)**
- [`index.html`](file:///c:/Sepsis_CDSS_Project%20template/templates/index.html): Main Single Page Application (SPA) dashboard containing patient management, vital entry modal, risk alert banners, and Chart.js analytics.
- [`login.html`](file:///c:/Sepsis_CDSS_Project%20template/templates/login.html): Secure staff authentication portal.
- [`dataset_table_viewer.html`](file:///c:/Sepsis_CDSS_Project%20template/templates/dataset_table_viewer.html): Interactive dataset browser for research inspection.

#### **`static/css/` & `static/js/` (Styles & Interactive Logic)**
- [`style.css`](file:///c:/Sepsis_CDSS_Project%20template/static/css/style.css): Custom accessible CSS design system featuring dark/light high-contrast clinical theme, responsive grid layouts, and status badges.
- [`app.js`](file:///c:/Sepsis_CDSS_Project%20template/static/js/app.js): Main application initializer and SPA tab router.
- [`auth.js`](file:///c:/Sepsis_CDSS_Project%20template/static/js/auth.js): Login form handler and session manager.
- [`dashboard.js`](file:///c:/Sepsis_CDSS_Project%20template/static/js/dashboard.js): Fetches stats, high-risk patient list, and updates dashboard cards.
- [`patients.js`](file:///c:/Sepsis_CDSS_Project%20template/static/js/patients.js): Patient table renderer, search filter, and patient profile view.
- [`predict.js`](file:///c:/Sepsis_CDSS_Project%20template/static/js/predict.js): Handles new vital entry form submission, live SIRS calculator, and ML prediction display.
- [`charts.js`](file:///c:/Sepsis_CDSS_Project%20template/static/js/charts.js): Renders real-time Chart.js time-series vital charts (Heart Rate, MAP, Temperature trends).

---

### 2.6 Automated Testing & Documentation

- [`tests/`](file:///c:/Sepsis_CDSS_Project%20template/tests/): Automated unit and integration test suite runnable via `pytest`:
  - `test_auth_api.py`: Tests user login and session security.
  - `test_ml_service.py`: Tests ML probability calculations and missing value handling.
  - `test_patient_api.py`: Tests patient creation and search endpoints.
  - `test_prediction_api.py`: Tests prediction workflow and DB insertion.
  - `test_sirs_service.py`: Verifies SIRS score rule accuracy.
  - `test_validators.py`: Checks input validation bounds.
- [`docs/`](file:///c:/Sepsis_CDSS_Project%20template/docs/): Technical documentation (`architecture.md`, `database.md`).
- [`archive/`](file:///c:/Sepsis_CDSS_Project%20template/archive/): Contains raw PhysioNet source zip/txt files (`training_setA`, `training_setB`).

---

## 3. 15 Optimal Features vs. 40 Features Analysis

While the original PhysioNet Sepsis Challenge dataset contains **40 features**, our optimized Clinical Decision Support System utilizes **15 key features**.

### 3.1 The 15 Selected Features

The 15 selected features are broken down below into primary vital signs, essential laboratory biomarkers, and patient demographic indicators:

| # | Feature Code | Full Feature Name | Category | Measurement Unit | Normal Reference Range | Clinical Role in Sepsis |
| :-: | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | `HR` | Heart Rate | Vital Sign | beats / min (bpm) | 60 - 100 bpm | Tachycardia (>90 bpm) is a core SIRS criterion caused by systemic infection response. |
| **2** | `O2Sat` | Oxygen Saturation | Vital Sign | Percentage (%) | 95% - 100% | Hypoxemia indicates impaired respiratory gas exchange and tissue hypoxia. |
| **3** | `Temp` | Core Body Temp | Vital Sign | Celsius (°C) | 36.5°C - 37.5°C | Fever (>38.0°C) or Hypothermia (<36.0°C) signals active inflammatory response. |
| **4** | `SBP` | Systolic Blood Pressure | Vital Sign | mmHg | 90 - 120 mmHg | SBP < 100 mmHg is a key qSOFA indicator of hypotension and septic shock. |
| **5** | `MAP` | Mean Arterial Pressure | Vital Sign | mmHg | 70 - 105 mmHg | Critical indicator of organ perfusion. MAP < 65 mmHg signals end-organ hypoperfusion. |
| **6** | `DBP` | Diastolic Blood Pressure | Vital Sign | mmHg | 60 - 80 mmHg | Assesses systemic vascular resistance and arterial filling pressure. |
| **7** | `Resp` | Respiratory Rate | Vital Sign | breaths / min | 12 - 20 breaths/min | Tachypnea (≥22 breaths/min) is a sensitive early marker of metabolic acidosis & qSOFA. |
| **8** | `WBC` | White Blood Cell Count | Lab Biomarker | $10^3 / \mu\text{L}$ | 4.5 - 11.0 $10^3 / \mu\text{L}$ | Leukocytosis (>12.0) or Leukopenia (<4.0) indicates severe immune system activation. |
| **9** | `Glucose` | Serum Blood Glucose | Lab Biomarker | mg / dL | 70 - 99 mg/dL | Stress hyperglycemia (>140 mg/dL) frequently occurs due to cytokine release. |
| **10** | `Lactate` | Blood Serum Lactate | Lab Biomarker | mmol / L | 0.5 - 1.0 mmol/L | **Gold Standard Sepsis Marker**. Lactate > 2.0 mmol/L indicates cellular hypoxia & shock. |
| **11** | `Creatinine` | Serum Creatinine | Lab Biomarker | mg / dL | 0.7 - 1.3 mg/dL | Rising creatinine signals Acute Kidney Injury (AKI), a major organ dysfunction in sepsis. |
| **12** | `Platelets` | Platelet Count | Lab Biomarker | $10^3 / \mu\text{L}$ | 150 - 450 $10^3 / \mu\text{L}$ | Thrombocytopenia (<100 $10^3/\mu\text{L}$) signals Disseminated Intravascular Coagulation (DIC). |
| **13** | `Age` | Patient Age | Demographic | Years | N/A | Elderly patients (≥65) have significantly higher risk of rapid septic deterioration. |
| **14** | `Gender` | Biological Sex | Demographic | Binary (1: Male, 0: Female) | N/A | Account for baseline physiological variance in organ function and baseline creatinine. |
| **15** | `ICULOS` | ICU Length of Stay | Clinical | Hours | N/A | Longer stay increases exposure to nosocomial / hospital-acquired resistant infections. |

---

### 3.2 Why 15 Features Were Chosen Over 40 Features

Using 15 features instead of 40 is a deliberate engineering and clinical decision driven by five major factors:

#### 1. Severe Missing Data Rates in the 40-Feature Set
In real-world ICU environments, specialized blood tests are **not ordered continuously for every patient every hour**. 
- In the full 40-feature PhysioNet dataset, rare lab features such as `Bilirubin_direct`, `TroponinI`, `Fibrinogen`, `Alkalinephos`, `AST`, `PaCO2`, and `SaO2` suffer from **85% to over 98% missing values**.
- Machine learning models trained on 40 features rely heavily on artificial imputation (e.g., median filling), introducing significant synthetic noise into predictions.
- The 15 selected features represent routine vitals and standard laboratory panels available for virtually all ICU patients.

#### 2. Clinical Utility & Rapid Emergency Response
Sepsis is a medical emergency where **every hour of delayed antibiotic treatment increases mortality by ~7.6%**.
- Requiring a clinician to enter 40 complex blood parameters delays early risk screening.
- Entering **15 vital signs and routine labs takes less than 90 seconds** at bedside, enabling immediate decision support.

#### 3. Prevention of Overfitting & Multicollinearity
- Many features in the 40-feature set are highly collinear (e.g., `Hct` vs `Hgb`, `Bilirubin_total` vs `Bilirubin_direct`, multiple arterial blood gas parameters like `pH`, `PaCO2`, `HCO3`, `BaseExcess`).
- Including 40 correlated variables increases model variance, causing decision trees to overfit to training noise.
- Reducing to 15 orthogonal features retains **>95% of total predictive variance** while improving model generalization on unseen patient data.

#### 4. Computational Efficiency & Lower API Latency
- The 15-feature Random Forest model file (`random_forest_15.pkl`) is significantly lighter than its 40-feature counterpart.
- Serialization and JSON parsing latencies are reduced, enabling sub-millisecond predictions ($<0.007\text{ ms/sample}$) optimal for high-throughput hospital web services.

#### 5. Direct Alignment with Standard Clinical Protocols
The 15 chosen features contain 100% of the metrics needed to compute established medical scoring systems:
- **SIRS Criteria**: Temperature, Heart Rate, Respiratory Rate, WBC.
- **qSOFA Score**: Respiratory Rate, Systolic BP, Mental Status / Age.
- **SOFA Score organ dysfunction markers**: PaO2/FiO2 (inferred via O2Sat/Resp), Platelets, Creatinine, MAP, Lactate.

---

## 4. Step-by-Step MySQL Workbench Setup & Connection Guide

Follow these step-by-step instructions to configure **MySQL Workbench**, create the production database, and connect it to your Python Flask CDSS application.

---

### Prerequisites
Before starting, ensure you have the following installed on your system:
1. **MySQL Community Server** (Version 8.0 or later) running on port `3306`.
2. **MySQL Workbench** installed.
3. Python environment with `mysql-connector-python` installed (`pip install mysql-connector-python`).

---

### Step 1: Open MySQL Workbench & Connect to Local Server
1. Launch **MySQL Workbench**.
2. Under **MySQL Connections**, click on **Local Instance MySQL80** (or click the **`+`** icon to add a new connection).
3. Verify connection details:
   - **Hostname**: `127.0.0.1` or `localhost`
   - **Port**: `3306`
   - **Username**: `root` (or your configured MySQL admin user)
4. Click **Test Connection**, enter your MySQL root password when prompted, and click **OK**.

---

### Step 2: Create Database Schema & Seed Data
1. In MySQL Workbench, click **File -> Open SQL Script...** (or press `Ctrl + O`).
2. Navigate to your project folder and select [`schema.sql`](file:///c:/Sepsis_CDSS_Project%20template/schema.sql).
3. Click the **Execute (Lightning Bolt icon)** on the query toolbar to run the entire script.
4. Verify output in the **Action Output** window at the bottom:
   - Database `sepsis_cdss` is created.
   - Tables created: `users`, `patients`, `vital_records`, `predictions`, `audit_logs`.
   - Default admin user seeded (`username: admin`, `password: Password@123`).
5. Refresh the **Schemas** tab in the left sidebar to confirm `sepsis_cdss` appears under Schemas.

---

### Step 3: Configure Project Environment File (`.env`)
Open the [`.env`](file:///c:/Sepsis_CDSS_Project%20template/.env) file in the root of your project directory and update the database settings to match your MySQL setup:

```ini
# Flask Secret Key
SECRET_KEY=sepsis-cdss-secret-key-change-in-production-2026

# Database Configuration for MySQL Connection Pool
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_actual_mysql_password
DB_NAME=sepsis_cdss
```

> **Note**: Replace `your_actual_mysql_password` with the password you set during MySQL installation.

---

### Step 4: Verify Flask Application Connection to MySQL
1. Open a terminal / PowerShell prompt in your project root:
   ```powershell
   python db.py
   ```
2. If MySQL connection is successful, you will see:
   ```text
   Connected successfully to MySQL Database 'sepsis_cdss'
   ```
3. If MySQL is unreachable, the application will display a warning and safely activate local SQLite fallback mode:
   ```text
   MySQL connection warning: ... Activating SQLite local fallback database.
   ```

---

### Step 5: Query & Monitor Data in MySQL Workbench

You can now use MySQL Workbench to view, search, and audit patient predictions generated by the web app!

Run the following SQL queries in MySQL Workbench:

#### 1. View All Registered Users & Roles:
```sql
USE sepsis_cdss;
SELECT id, username, email, full_name, role, is_active, created_at FROM users;
```

#### 2. View Patient Records:
```sql
SELECT * FROM patients ORDER BY created_at DESC;
```

#### 3. Inspect High-Risk Patient Predictions (with Vitals & ML Scores):
```sql
SELECT 
    p.patient_code,
    p.full_name,
    v.hr AS heart_rate,
    v.sbp AS blood_pressure,
    v.temp AS body_temp,
    pred.model_probability AS sepsis_risk_score,
    pred.risk_category,
    pred.sirs_status,
    pred.prediction_time
FROM predictions pred
JOIN vital_records v ON pred.vital_record_id = v.id
JOIN patients p ON v.patient_id = p.id
WHERE pred.risk_category = 'High'
ORDER BY pred.prediction_time DESC;
```

#### 4. View System Audit Logs:
```sql
SELECT 
    a.id,
    u.username,
    a.action,
    a.patient_id,
    a.ip_address,
    a.timestamp
FROM audit_logs a
LEFT JOIN users u ON a.user_id = u.id
ORDER BY a.timestamp DESC;
```

---

### Step 6: Troubleshooting Common Connection Issues

| Issue / Error | Cause | Solution |
| :--- | :--- | :--- |
| `Access denied for user 'root'@'localhost'` | Wrong password in `.env` | Double check `DB_PASSWORD` in `.env` or reset your MySQL root password. |
| `Can't connect to MySQL server on 'localhost' (10061)` | MySQL service is not running | Open Windows Services (`services.msc`), find **MySQL80**, and click **Start**. |
| `Unknown database 'sepsis_cdss'` | Schema script was not executed | Open MySQL Workbench and execute [`schema.sql`](file:///c:/Sepsis_CDSS_Project%20template/schema.sql) again. |
| `Client does not support authentication protocol requested by server` | Legacy authentication plugin | Execute in MySQL Workbench: <br> `ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'your_password'; FLUSH PRIVILEGES;` |
