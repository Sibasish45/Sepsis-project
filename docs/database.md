# Database Schema & Entity Documentation

## Database Overview
The database layer uses MySQL (with SQLite local fallback for development) to persist patient demographics, clinical vital observations, ML predictions, user credentials, and audit logs.

## Entity Relationship Diagram
- **`users` (1) ── (M) `vital_records`**: Staff member who recorded the vitals.
- **`patients` (1) ── (M) `vital_records`**: Patient receiving measurements.
- **`vital_records` (1) ── (1) `predictions`**: ML prediction & SIRS calculation output.
- **`users` (1) ── (M) `audit_logs`**: System audit trail.

## Database Indexing Strategy
- `idx_patient_code` on `patients(patient_code)`
- `idx_vital_patient_recorded` on `vital_records(patient_id, recorded_at DESC)`
- `idx_prediction_vital` on `predictions(vital_record_id)`
- `idx_prediction_time` on `predictions(prediction_time DESC)`
- `idx_prediction_risk` on `predictions(risk_category)`
- `idx_audit_user` on `audit_logs(user_id)`
- `idx_audit_patient` on `audit_logs(patient_id)`
