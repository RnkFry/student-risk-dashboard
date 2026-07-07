import sqlite3
import os

DB_PATH = "student_risk_db.sqlite"

def get_db_connection():
    """Create SQLite database connection"""
    return sqlite3.connect(DB_PATH)

def init_db():
    """Create tables if not exist"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Raw student data table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS raw_student_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kode_periode TEXT,
        kode_kelas TEXT,
        nim INTEGER,
        tp1_total REAL, tp2_total REAL,
        tk1_total REAL, tk2_total REAL, tk3_total REAL, tk4_total REAL,
        quiz1_total REAL, quiz2_total REAL, final_exam_total REAL,
        avg_tp_awal REAL, avg_tk_awal REAL, quiz1_score REAL, avg_lo1_awal REAL,
        trend_tp REAL, trend_tk REAL, early_academic_score REAL,
        avg_days_before_deadline REAL, pct_submission_h_minus_1 REAL,
        pct_late_submission REAL, fd_ratio REAL, download_ratio REAL, vbl_ratio REAL,
        avg_tle REAL, count_tle_below_3 INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Processed student data table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS processed_student_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kode_gabungan TEXT UNIQUE,
        nim INTEGER,
        kode_kelas TEXT,
        kode_periode TEXT,
        avg_tp REAL,
        avg_tk REAL,
        risk_probability REAL,
        risk_label INTEGER,
        lo1_score REAL,
        lo2_score REAL,
        lo3_score REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # ETL logs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS etl_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_name TEXT,
        status TEXT,
        records_processed INTEGER,
        records_failed INTEGER,
        error_message TEXT,
        started_at TIMESTAMP,
        ended_at TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()

# Initialize on import
if not os.path.exists(DB_PATH):
    init_db()

def execute_query(query, params=None):
    """Execute query dan return results"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(query, params)
        conn.commit()
        return cursor.fetchall()
    except Exception as e:
        conn.rollback()
        print(f"❌ Query error: {e}")
        raise
    finally:
        cursor.close()
        conn.close()