# System Architecture Specification - Sepsis CDSS

## Architectural Overview
The Sepsis Clinical Decision Support System (CDSS) is designed as a decoupled, modular full-stack web application.

```
                    ┌─────────────────────────┐
                    │  Web Browser Interface  │
                    │  (HTML/CSS/JS/Chart.js) │
                    └────────────┬────────────┘
                                 │
                            HTTP REST API
                                 │
                    ┌────────────▼────────────┐
                    │      Flask App          │
                    │  (app.py & Routing)     │
                    └──────┬──────────┬───────┘
                           │          │
             ┌─────────────▼───┐  ┌───▼─────────────────────┐
             │  MySQL Database │  │ Prediction Orchestrator │
             │                 │  │ (prediction_service.py) │
             │  - Patients     │  └───┬─────────┬─────────┬─┘
             │  - Vitals       │      │         │         │
             │  - Predictions  │  ┌───▼───┐ ┌───▼───┐ ┌───▼───────────┐
             │  - Users        │  │  ML   │ │ SIRS  │ │ Clinical Rules│
             │  - Audit Logs   │  │Engine │ │Engine │ │    Engine     │
             └─────────────────┘  └───┬───┘ └───────┘ └───────────────┘
                                      │
                              sepsis_model.pkl
```

## Key Subsystems
1. **Validation Layer (`utils/validators.py`)**: 3-level verification (Type, Range, Missing strategy).
2. **ML Engine (`services/ml_service.py`)**: Startup feature contract check (40 features), median imputation, random forest probability calculation.
3. **SIRS Engine (`services/sirs_service.py`)**: Independent clinical criteria evaluator (HR > 90, Temp < 36 or > 38, Resp > 20, WBC < 4 or > 12).
4. **Clinical Rules Engine (`services/clinical_rules_service.py`)**: Non-prescriptive decision-support follow-up indicators.
5. **Persistence & Audit (`services/patient_service.py`, `services/audit_service.py`)**: Atomic database transaction manager (`BEGIN TRANSACTION` -> `vital_records` -> `predictions` -> `audit_logs` -> `COMMIT`).
