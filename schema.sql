-- Sepsis CDSS MySQL Schema Initialization Script
CREATE DATABASE IF NOT EXISTS sepsis_cdss CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE sepsis_cdss;

-- 1. Users Table (Role-based access: DOCTOR, NURSE, ADMIN)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role ENUM('DOCTOR', 'NURSE', 'ADMIN') NOT NULL DEFAULT 'NURSE',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_login TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Patients Table
CREATE TABLE IF NOT EXISTS patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_code VARCHAR(20) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    gender TINYINT NOT NULL COMMENT '1 = Male, 0 = Female',
    date_of_birth DATE NULL,
    medical_history TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 3. Vital Records Table (Clinical Measurements)
CREATE TABLE IF NOT EXISTS vital_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    recorded_by INT NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Primary Clinical Vitals
    hr FLOAT NULL COMMENT 'Heart Rate (bpm)',
    o2sat FLOAT NULL COMMENT 'O2 Saturation (%)',
    temp FLOAT NULL COMMENT 'Temperature (°C)',
    sbp FLOAT NULL COMMENT 'Systolic BP (mmHg)',
    map_val FLOAT NULL COMMENT 'Mean Arterial Pressure (mmHg)',
    dbp FLOAT NULL COMMENT 'Diastolic BP (mmHg)',
    resp FLOAT NULL COMMENT 'Respiratory Rate (breaths/min)',
    wbc FLOAT NULL COMMENT 'White Blood Cell Count (10^3/uL)',
    glucose FLOAT NULL COMMENT 'Glucose (mg/dL)',
    iculos INT NULL COMMENT 'ICU Length of Stay (hours)',
    
    -- Complete 40-Feature Snapshot JSON
    input_features_json JSON NOT NULL COMMENT 'Full 40 feature vector for 100% ML reproducibility',
    
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (recorded_by) REFERENCES users(id)
);

-- 4. Predictions Table (System Calculated Outputs)
CREATE TABLE IF NOT EXISTS predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vital_record_id INT NOT NULL,
    model_version VARCHAR(50) NOT NULL DEFAULT 'RF_v1.0',
    model_probability DECIMAL(6,5) NOT NULL COMMENT 'Model predicted score 0.00000 to 1.00000',
    risk_category ENUM('Low', 'Moderate', 'High') NOT NULL,
    sirs_score TINYINT NOT NULL COMMENT 'SIRS criteria count (0 to 4)',
    sirs_status VARCHAR(100) NOT NULL COMMENT 'e.g. SIRS Criteria Met (3/4)',
    prediction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (vital_record_id) REFERENCES vital_records(id) ON DELETE CASCADE,
    CONSTRAINT chk_prob CHECK (model_probability >= 0.0 AND model_probability <= 1.0),
    CONSTRAINT chk_sirs CHECK (sirs_score >= 0 AND sirs_score <= 4)
);

-- 5. System Audit Logs Table
CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    action VARCHAR(100) NOT NULL,
    patient_id INT NULL,
    vital_record_id INT NULL,
    prediction_id INT NULL,
    ip_address VARCHAR(45) NULL,
    user_agent VARCHAR(255) NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details JSON NULL,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE SET NULL,
    FOREIGN KEY (vital_record_id) REFERENCES vital_records(id) ON DELETE SET NULL,
    FOREIGN KEY (prediction_id) REFERENCES predictions(id) ON DELETE SET NULL
);

-- Indexes for Fast Query Execution
CREATE INDEX idx_patient_code ON patients(patient_code);
CREATE INDEX idx_vital_patient_recorded ON vital_records(patient_id, recorded_at DESC);
CREATE INDEX idx_prediction_vital ON predictions(vital_record_id);
CREATE INDEX idx_prediction_time ON predictions(prediction_time DESC);
CREATE INDEX idx_prediction_risk ON predictions(risk_category);
CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_patient ON audit_logs(patient_id);

-- Seed Default Admin User if not exists (Username: admin, Password: Password@123)
-- Password hash generated using pbkdf2:sha256
INSERT IGNORE INTO users (id, username, email, password_hash, full_name, role, is_active) 
VALUES (1, 'admin', 'admin@sepsis-cdss.hospital.org', 'scrypt:32768:8:1$n180JvSEVWmXhZD5$5edb75a03021be8f090e4cc629a5074b85683e0ed9b8fe8fc3c2c9022ce81a9455cce3b06cb847e080f5929d58b416d2f7029f816779af92e94dde7fe3f2ceaa', 'System Administrator', 'ADMIN', TRUE);
