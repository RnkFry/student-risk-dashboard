import os
from dotenv import load_dotenv

load_dotenv()

# ════════════════════════════════════════
# DATABASE CONFIG
# ════════════════════════════════════════
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'student_risk_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '')
}

# ════════════════════════════════════════
# DATA SOURCE CONFIG
# ════════════════════════════════════════
# Google Sheets (nanti kita set)
GOOGLE_SHEETS_URL = "https://docs.google.com/spreadsheets/d/..."  # UPDATE NANTI

# Excel file paths
EXCEL_TRAINING_DATA = "data/data.xlsx"
EXCEL_ALERT_DATA = "data/alert_data.xlsx"

# ════════════════════════════════════════
# DATABASE TABLES
# ════════════════════════════════════════
RAW_TABLE = "risk_data.raw_student_data"
PROCESSED_TABLE = "risk_data.processed_student_data"
LOGS_TABLE = "risk_data.etl_logs"

# ════════════════════════════════════════
# FEATURE COLUMNS (untuk transformation)
# ════════════════════════════════════════
FEATURE_COLS = [
    'TP1', 'TP2', 'TK1', 'TK2', 'TK3', 'TK4',
    'Quiz1', 'Quiz2', 'Final_Exam',
    'FD1', 'FD2', 'FD3', 'FD4', 'FD5', 'FD6', 'FD7', 'FD8', 'FD9', 'FD10',
    'LN1', 'LN2', 'LN3', 'LN4', 'LN5', 'LN6', 'LN7', 'LN8', 'LN9', 'LN10',
    'PPT1', 'PPT2', 'PPT3', 'PPT4', 'PPT5', 'PPT6', 'PPT7', 'PPT8', 'PPT9', 'PPT10',
    'VBL1', 'VBL2', 'VBL3', 'VBL4', 'VBL5', 'VBL6', 'VBL7', 'VBL8', 'VBL9', 'VBL10',
]

TLE_COLS = [f'TLE_P{i}' for i in range(1, 10)]

# LO Mapping
LO_WEIGHTS = {
    'TP1':        {'LO1': 1.0, 'LO2': 0.0, 'LO3': 0.0},
    'TP2':        {'LO1': 0.2, 'LO2': 0.8, 'LO3': 0.0},
    'TK1':        {'LO1': 1.0, 'LO2': 0.0, 'LO3': 0.0},
    'TK2':        {'LO1': 0.0, 'LO2': 1.0, 'LO3': 0.0},
    'TK3':        {'LO1': 0.0, 'LO2': 0.6, 'LO3': 0.4},
    'TK4':        {'LO1': 0.0, 'LO2': 0.5, 'LO3': 0.5},
    'Quiz1':      {'LO1': 0.8, 'LO2': 0.2, 'LO3': 0.0},
    'Quiz2':      {'LO1': 0.0, 'LO2': 0.4, 'LO3': 0.6},
    'Final_Exam': {'LO1': 0.2, 'LO2': 0.4, 'LO3': 0.4},
}