"""
Database Connection & Transaction Manager for Sepsis CDSS.
Provides MySQL connection pooling and transaction context management with SQLite fallback for offline development.
"""
import os
import sqlite3
import json
from contextlib import contextmanager
from config import Config

# Global Flag for active connection type
USE_SQLITE_FALLBACK = False

try:
    import mysql.connector
    from mysql.connector import pooling
    
    # Try initializing MySQL Connection Pool
    db_pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="sepsis_pool",
        pool_size=5,
        pool_reset_session=True,
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME
    )
    print(f"Connected successfully to MySQL Database '{Config.DB_NAME}'")
except Exception as e:
    print(f"MySQL connection warning: {e}. Activating SQLite local fallback database.")
    USE_SQLITE_FALLBACK = True

SQLITE_DB_PATH = "sepsis_cdss_local.db"

def init_sqlite_schema():
    """Initializes SQLite tables if MySQL is unavailable."""
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'NURSE',
            is_active INTEGER NOT NULL DEFAULT 1,
            last_login TEXT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_code TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender INTEGER NOT NULL,
            date_of_birth TEXT NULL,
            medical_history TEXT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS vital_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            recorded_by INTEGER NOT NULL,
            recorded_at TEXT DEFAULT CURRENT_TIMESTAMP,
            hr REAL, o2sat REAL, temp REAL, sbp REAL, map_val REAL, dbp REAL, resp REAL, wbc REAL, glucose REAL, iculos INTEGER,
            input_features_json TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vital_record_id INTEGER NOT NULL,
            model_version TEXT NOT NULL DEFAULT 'RF_v1.0',
            model_probability REAL NOT NULL,
            risk_category TEXT NOT NULL,
            sirs_score INTEGER NOT NULL,
            sirs_status TEXT NOT NULL,
            prediction_time TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            patient_id INTEGER,
            vital_record_id INTEGER,
            prediction_id INTEGER,
            ip_address TEXT,
            user_agent TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            details TEXT
        );

        INSERT OR IGNORE INTO users (id, username, email, password_hash, full_name, role, is_active) 
        VALUES (1, 'admin', 'admin@sepsis-cdss.hospital.org', 'scrypt:32768:8:1$n180JvSEVWmXhZD5$5edb75a03021be8f090e4cc629a5074b85683e0ed9b8fe8fc3c2c9022ce81a9455cce3b06cb847e080f5929d58b416d2f7029f816779af92e94dde7fe3f2ceaa', 'System Administrator', 'ADMIN', 1);
    """)
    conn.commit()
    conn.close()

if USE_SQLITE_FALLBACK:
    init_sqlite_schema()

@contextmanager
def get_db_cursor(commit=False):
    """
    Context manager for acquiring a database cursor.
    Enforces atomic transaction (COMMIT on success, ROLLBACK on failure).
    """
    if USE_SQLITE_FALLBACK:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            yield cursor
            if commit:
                conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    else:
        conn = db_pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            yield cursor
            if commit:
                conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()
