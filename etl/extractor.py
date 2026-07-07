import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
import logging
from datetime import datetime
from etl.config import (
    DB_CONFIG, RAW_TABLE, LOGS_TABLE, 
    EXCEL_TRAINING_DATA, EXCEL_ALERT_DATA
)
from config.database import get_db_connection

# ════════════════════════════════════════
# SETUP LOGGING
# ════════════════════════════════════════
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/etl_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ════════════════════════════════════════
# EXTRACT EXCEL
# ════════════════════════════════════════
def extract_from_excel(file_path):
    """
    Load data dari Excel file.
    
    Args:
        file_path: Path ke Excel file
        
    Returns:
        pandas DataFrame
    """
    try:
        logger.info(f"📥 Extracting from Excel: {file_path}")
        df = pd.read_excel(file_path)
        
        # Normalize column names (lowercase, replace spaces)
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        
        logger.info(f"✅ Successfully extracted {len(df)} rows from {file_path}")
        return df
        
    except FileNotFoundError:
        logger.error(f"❌ File not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"❌ Error extracting from Excel: {e}")
        raise


# ════════════════════════════════════════
# EXTRACT GOOGLE SHEETS (untuk nanti)
# ════════════════════════════════════════
def extract_from_google_sheets(sheet_url):
    """
    Load data dari Google Sheets (CSV export URL).
    
    Args:
        sheet_url: Google Sheets export URL (CSV format)
        
    Returns:
        pandas DataFrame
    """
    try:
        logger.info(f"📥 Extracting from Google Sheets: {sheet_url}")
        df = pd.read_csv(sheet_url)
        
        # Normalize column names
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        
        logger.info(f"✅ Successfully extracted {len(df)} rows from Google Sheets")
        return df
        
    except Exception as e:
        logger.error(f"❌ Error extracting from Google Sheets: {e}")
        raise


# ════════════════════════════════════════
# LOAD TO DATABASE
# ════════════════════════════════════════
def load_to_raw_table(df, table_name=RAW_TABLE):
    """
    Insert DataFrame ke raw table PostgreSQL.
    
    Args:
        df: pandas DataFrame
        table_name: Target table name
    """
    conn = None
    cursor = None
    start_time = datetime.now()
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Bersihkan table dulu (truncate)
        logger.info(f"🗑️  Truncating {table_name}")
        cursor.execute(f"TRUNCATE TABLE {table_name} CASCADE")
        conn.commit()
        
        # Prepare data untuk insert
        df = df.fillna(0)  # Replace NaN dengan 0
        
        # Siapkan kolom dan values
        columns = ', '.join(df.columns)
        placeholders = ', '.join(['%s'] * len(df.columns))
        insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        
        # Convert DataFrame ke list of tuples
        data = [tuple(row) for row in df.values]
        
        # Batch insert
        logger.info(f"📤 Loading {len(data)} rows to {table_name}")
        execute_batch(cursor, insert_query, data, page_size=1000)
        conn.commit()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"✅ Successfully loaded {len(data)} rows in {duration:.2f}s")
        
        # Log success ke etl_logs
        log_etl_success(
            job_name="extract_and_load",
            records_processed=len(data),
            records_failed=0,
            started_at=start_time,
            ended_at=end_time
        )
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error loading to database: {e}")
        if conn:
            conn.rollback()
        
        # Log failure
        log_etl_failure(
            job_name="extract_and_load",
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
# ETL LOGGING
# ════════════════════════════════════════
def log_etl_success(job_name, records_processed, records_failed, started_at, ended_at):
    """Log ETL job success"""
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


def log_etl_failure(job_name, error_message, started_at):
    """Log ETL job failure"""
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
def run_extractor():
    """
    Main function untuk jalankan extraction pipeline.
    """
    try:
        logger.info("=" * 60)
        logger.info("🚀 STARTING ETL EXTRACTOR")
        logger.info("=" * 60)
        
        # Extract dari Excel
        df = extract_from_excel(EXCEL_TRAINING_DATA)
        
        # Load ke database
        load_to_raw_table(df)
        
        logger.info("=" * 60)
        logger.info("✅ ETL EXTRACTOR COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"❌ ETL EXTRACTOR FAILED: {e}")
        logger.error("=" * 60)
        return False


if __name__ == "__main__":
    run_extractor()