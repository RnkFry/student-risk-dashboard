import pandas as pd
import psycopg2
from datetime import datetime
import logging
import joblib
import numpy as np
from etl.config import (
    DB_CONFIG, RAW_TABLE, PROCESSED_TABLE, LOGS_TABLE,
    LO_WEIGHTS
)
from config.database import get_db_connection

# ════════════════════════════════════════
# SETUP LOGGING
# ════════════════════════════════════════
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/etl_pipeline.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


# ════════════════════════════════════════
# LOAD RAW DATA FROM DATABASE
# ════════════════════════════════════════
def load_raw_data():
    try:
        conn = get_db_connection()
        logger.info(f"📥 Loading raw data from raw_student_data")
        
        df = pd.read_sql("SELECT * FROM raw_student_data", conn)
        conn.close()
        
        logger.info(f"✅ Loaded {len(df)} rows from raw table")
        return df
        
    except Exception as e:
        logger.error(f"❌ Error loading raw data: {e}")
        return pd.DataFrame()


# ════════════════════════════════════════
# AGGREGATE SCORES (TP, TK, Quiz, FE)
# ════════════════════════════════════════
def aggregate_scores(df):
    """
    Aggregate individual LO scores ke satu nilai per tugas.
    """
    logger.info("📊 Aggregating assessment scores")
    
    df = df.copy()
    
    # TP — take tp1_total dan tp2_total
    df['tp1'] = df['tp1_total'].fillna(0)
    df['tp2'] = df['tp2_total'].fillna(0)
    df['avg_tp'] = df[['tp1', 'tp2']].mean(axis=1)
    
    # TK — aggregate TK1–TK4
    tk_cols = ['tk1_total', 'tk2_total', 'tk3_total', 'tk4_total']
    df['avg_tk'] = df[tk_cols].mean(axis=1)
    
    # Quiz — aggregate Quiz1 dan Quiz2
    df['quiz1'] = df['quiz1_total'].fillna(0)
    df['quiz2'] = df['quiz2_total'].fillna(0)
    df['avg_quiz'] = df[['quiz1', 'quiz2']].mean(axis=1)
    
    # Final Exam
    df['final_exam'] = df['final_exam_total'].fillna(0)
    
    logger.info("✅ Scores aggregated")
    
    return df


# ════════════════════════════════════════
# CALCULATE LO SCORES
# ════════════════════════════════════════
def calculate_lo_scores(df):
    """
    Hitung LO1, LO2, LO3 untuk setiap mahasiswa menggunakan weighted average.
    
    Rumus:
        LO_x = sum(nilai_tugas * bobot_tugas_ke_LO_x) / sum(bobot_tugas_ke_LO_x)
    """
    logger.info("🎯 Calculating LO scores")
    
    df = df.copy()
    
    # Mapping tugas ke kolom di DataFrame
    task_mapping = {
        'TP1': 'tp1_total',
        'TP2': 'tp2_total',
        'TK1': 'tk1_total',
        'TK2': 'tk2_total',
        'TK3': 'tk3_total',
        'TK4': 'tk4_total',
        'Quiz1': 'quiz1_total',
        'Quiz2': 'quiz2_total',
        'Final_Exam': 'final_exam_total',
    }
    
    # Hitung per LO
    for lo in ['LO1', 'LO2', 'LO3']:
        weighted_sum = None
        total_weight = 0.0
        
        for task, col in task_mapping.items():
            if task not in LO_WEIGHTS or col not in df.columns:
                continue
            
            w = LO_WEIGHTS[task][lo]
            if w == 0:
                continue
            
            nilai = df[col].fillna(0)
            if weighted_sum is None:
                weighted_sum = nilai * w
            else:
                weighted_sum = weighted_sum + nilai * w
            total_weight += w
        
        # Weighted average
        col_name = f'lo{lo[-1]}_score'  # lo1_score, lo2_score, lo3_score
        df[col_name] = (weighted_sum / total_weight) if total_weight > 0 else 0
    
    logger.info("✅ LO scores calculated")
    
    return df


# ════════════════════════════════════════
# CALCULATE RISK PROBABILITY
# ════════════════════════════════════════
def calculate_risk(df):
    """
    Load pre-trained model dan predict risk probability.
    Model expect exactly 15 features (aggregated).
    """
    logger.info("🤖 Calculating risk probability")
    
    df = df.copy()
    
    try:
        # Load model
        model = joblib.load('models/model.pkl')
        
        # Feature columns — EXACTLY seperti training (15 features)
        feature_cols_mapping = {
            'avg_days_before_deadline': 'Avg_days_before_deadline',
            'pct_submission_h_minus_1': 'pct_submission_H_minus_1',
            'pct_late_submission': 'pct_late_submission',
            'fd_ratio': 'FD_ratio',
            'download_ratio': 'Download_ratio',
            'vbl_ratio': 'VBL_ratio',
            'avg_tle': 'Avg_TLE',
            'count_tle_below_3': 'Count_TLE_below_3',
            'avg_tp_awal': 'Avg_TP_awal',
            'avg_tk_awal': 'Avg_TK_awal',
            'quiz1_score': 'Quiz1_score',
            'avg_lo1_awal': 'Avg_LO1_awal',
            'trend_tp': 'Trend_TP',
            'trend_tk': 'Trend_TK',
            'early_academic_score': 'Early_academic_score'
        }
        
        # Prepare features dengan exact training names
        feature_cols_db = list(feature_cols_mapping.keys())
        X = df[feature_cols_db].fillna(0).copy()
        X.columns = [feature_cols_mapping[c] for c in X.columns]
        
        # Predict
        risk_proba = model.predict_proba(X)[:, 1]
        
        df['risk_probability'] = risk_proba
        df['risk_label'] = (risk_proba > 0.6).astype(int)
        
        logger.info(f"✅ Risk calculated — {df['risk_label'].sum()} high-risk students")
        
        return df
        
    except FileNotFoundError:
        logger.error("❌ Model file not found: models/model.pkl")
        raise
    except KeyError as e:
        logger.error(f"❌ Missing feature column: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Error calculating risk: {e}")
        raise

# ════════════════════════════════════════
# PREPARE DATA FOR PROCESSED TABLE
# ════════════════════════════════════════
def prepare_processed_data(df):
    """
    Select dan prepare kolom untuk dimasukkan ke processed_student_data table.
    """
    logger.info("🔧 Preparing data for processed table")
    
    df = df.copy()
    
    # Select kolom yang diperlukan (termasuk kode_gabungan)
    processed_cols = [
        'kode_gabungan',  # TAMBAH ini
        'nim',
        'kode_kelas',
        'kode_periode',
        'avg_tp',
        'avg_tk',
        'risk_probability',
        'risk_label',
        'lo1_score',
        'lo2_score',
        'lo3_score'
    ]
    
    processed_df = df[processed_cols].copy()
    processed_df = processed_df.dropna(subset=['kode_gabungan'])  # Remove rows tanpa kode_gabungan
    
    # Tidak perlu drop duplicates — setiap kode_gabungan unique per semester
    
    logger.info(f"✅ Prepared {len(processed_df)} records for processed table")
    
    return processed_df


# ════════════════════════════════════════
# LOAD TO PROCESSED TABLE
# ════════════════════════════════════════
def load_processed_data(df, table_name=PROCESSED_TABLE):
    """
    Insert processed data ke PostgreSQL.
    """
    conn = None
    cursor = None
    start_time = datetime.now()
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Truncate table
        logger.info(f"🗑️  Truncating {table_name}")
        cursor.execute(f"TRUNCATE TABLE {table_name} CASCADE")
        conn.commit()
        
        # Prepare data
        df = df.fillna(0)
        data = [tuple(row) for row in df.values]
        
        # Insert
        columns = ', '.join(df.columns)
        placeholders = ', '.join(['%s'] * len(df.columns))
        insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        
        logger.info(f"📤 Loading {len(data)} records to {table_name}")
        
        from psycopg2.extras import execute_batch
        execute_batch(cursor, insert_query, data, page_size=1000)
        conn.commit()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"✅ Successfully loaded {len(data)} records in {duration:.2f}s")
        
        # Log success
        _log_etl_success(
            job_name="transform_and_load",
            records_processed=len(data),
            records_failed=0,
            started_at=start_time,
            ended_at=end_time
        )
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error loading processed data: {e}")
        if conn:
            conn.rollback()
        
        _log_etl_failure(
            job_name="transform_and_load",
            error_message=str(e),
            started_at=start_time
        )
        
        raise
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ════════════════════════════════════════
# ETL LOGGING HELPERS
# ════════════════════════════════════════
def _log_etl_success(job_name, records_processed, records_failed, started_at, ended_at):
    """Log ETL success"""
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = f"""
            INSERT INTO {LOGS_TABLE}
            (job_name, status, records_processed, records_failed, started_at, ended_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(query, (
            job_name,
            'SUCCESS',
            records_processed,
            records_failed,
            started_at,
            ended_at
        ))
        
        conn.commit()
        
    except Exception as e:
        logger.error(f"❌ Error logging success: {e}")
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def _log_etl_failure(job_name, error_message, started_at):
    """Log ETL failure"""
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = f"""
            INSERT INTO {LOGS_TABLE}
            (job_name, status, records_processed, records_failed, error_message, started_at, ended_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(query, (
            job_name,
            'FAILED',
            0,
            0,
            error_message,
            started_at,
            datetime.now()
        ))
        
        conn.commit()
        
    except Exception as e:
        logger.error(f"❌ Error logging failure: {e}")
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ════════════════════════════════════════
# MAIN FUNCTION
# ════════════════════════════════════════
def run_transformer():
    """
    Main transformer pipeline.
    """
    try:
        logger.info("=" * 60)
        logger.info("🚀 STARTING ETL TRANSFORMER")
        logger.info("=" * 60)
        
        # Load raw data
        df = load_raw_data()
        
        # Transform
        df = aggregate_scores(df)
        df = calculate_lo_scores(df)
        df = calculate_risk(df)
        
        # Prepare untuk processed table
        processed_df = prepare_processed_data(df)
        
        # Load ke database
        load_processed_data(processed_df)
        
        logger.info("=" * 60)
        logger.info("✅ ETL TRANSFORMER COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"❌ ETL TRANSFORMER FAILED: {e}")
        logger.error("=" * 60)
        return False


if __name__ == "__main__":
    run_transformer()