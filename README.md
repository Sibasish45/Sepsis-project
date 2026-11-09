# Web-Based Clinical Decision Support System (CDSS) for Early Sepsis Risk Detection

An enterprise-grade, full-stack Clinical Decision Support System (CDSS) web application for early sepsis risk detection and patient record management.

## Tech Stack
- **Backend**: Python Flask, NumPy, Pandas, Scikit-learn, Joblib, MySQL (`mysql-connector-python`) / SQLite
- **Frontend**: Vanilla HTML5, Accessible CSS3, JavaScript (ES6+), Chart.js
- **Machine Learning**: Pre-trained Random Forest Classifier (`sepsis_model.pkl`, 40 features)
- **Testing**: `pytest`

## Key Features
1. **Startup Feature Contract Protection**: Verifies exact 40 features at application launch before inference.
2. **Decoupled Engines**: ML Random Forest Probability Engine operate independently alongside SIRS Criteria Evaluator.
3. **Atomic DB Persistence & Audit Logging**: `BEGIN TRANSACTION` saves vital readings, prediction outputs, and audit logs atomically.
4. **Role-Based Access Control (RBAC)**: Admin-only staff account registration, secure sessions, password hashing.
5. **Accessible Clinical Dashboard**: Responsive UI with high-contrast risk badges (`LOW RISK`, `MODERATE RISK`, `HIGH RISK`), vital trend charts, and patient timelines.

## Model Training & Jupyter Notebooks
All interactive training and analysis workflows are organized in the [`jupyter_notebooks/`](file:///C:/Sepsis_CDSS_Project%20template/jupyter_notebooks/) directory:
- **01 Data Stitching & Preprocessing**: [`jupyter_notebooks/01_data_stitching_and_preprocessing.ipynb`](file:///C:/Sepsis_CDSS_Project%20template/jupyter_notebooks/01_data_stitching_and_preprocessing.ipynb)
- **02 Production Random Forest Training**: [`jupyter_notebooks/02_random_forest_model_training.ipynb`](file:///C:/Sepsis_CDSS_Project%20template/jupyter_notebooks/02_random_forest_model_training.ipynb)
- **03 Model Benchmarking & Evaluation**: [`jupyter_notebooks/03_models_benchmarking_and_comparison.ipynb`](file:///C:/Sepsis_CDSS_Project%20template/jupyter_notebooks/03_models_benchmarking_and_comparison.ipynb)
- **04 Complete Master Pipeline**: [`jupyter_notebooks/04_complete_end_to_end_pipeline.ipynb`](file:///C:/Sepsis_CDSS_Project%20template/jupyter_notebooks/04_complete_end_to_end_pipeline.ipynb)

To launch Jupyter:
```bash
jupyter notebook
```

## Quick Start
1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Automated Tests**:
   ```bash
   python -m pytest tests/
   ```

3. **Start Application**:
   ```bash
   python app.py
   ```
   Access portal at `http://127.0.0.1:5000`.

## Documentation & Setup Guide
For a complete file-by-file architecture map, 15 vs 40 feature clinical comparison, and step-by-step MySQL Workbench setup guide, see:
👉 **[PROJECT_GUIDE.md](PROJECT_GUIDE.md)**

## Default Credentials
- **Username**: `admin`
- **Password**: `Password@123`

