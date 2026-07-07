import logging
from datetime import datetime
from etl.extractor import run_extractor
from etl.transformer import run_transformer
from config.database import init_db

# ════════════════════════════════════════
# SETUP LOGGING
# ════════════════════════════════════════
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/etl_pipeline.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ════════════════════════════════════════
# MAIN ETL PIPELINE
# ════════════════════════════════════════
def run_etl_pipeline():
    """
    Run complete ETL pipeline:
    1. Extract dari Excel ke raw_student_data table
    2. Transform raw data ke processed_student_data table
    """
    try:
        init_db()
        logger.info("\n" + "=" * 70)
        logger.info("🚀 STARTING COMPLETE ETL PIPELINE")
        logger.info("=" * 70)
        
        start_time = datetime.now()
        
        # ── STEP 1: EXTRACT ──────────────────────────────────────────
        logger.info("\n📥 STEP 1: EXTRACT")
        logger.info("-" * 70)
        
        extract_success = run_extractor()
        if not extract_success:
            logger.error("❌ Extract failed, stopping pipeline")
            return False
        
        # ── STEP 2: TRANSFORM ────────────────────────────────────────
        logger.info("\n🔄 STEP 2: TRANSFORM")
        logger.info("-" * 70)
        
        transform_success = run_transformer()
        if not transform_success:
            logger.error("❌ Transform failed, stopping pipeline")
            return False
        
        # ── PIPELINE SUCCESS ─────────────────────────────────────────
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("\n" + "=" * 70)
        logger.info(f"✅ ETL PIPELINE COMPLETED SUCCESSFULLY")
        logger.info(f"⏱️  Total duration: {duration:.2f} seconds")
        logger.info("=" * 70 + "\n")
        
        return True
        
    except Exception as e:
        logger.error("\n" + "=" * 70)
        logger.error(f"❌ ETL PIPELINE FAILED: {e}")
        logger.error("=" * 70 + "\n")
        return False


# ════════════════════════════════════════
# ENTRY POINT
# ════════════════════════════════════════
if __name__ == "__main__":
    success = run_etl_pipeline()
    exit(0 if success else 1)