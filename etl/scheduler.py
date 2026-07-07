import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from etl.loader import run_etl_pipeline

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
# SCHEDULER INSTANCE
# ════════════════════════════════════════
scheduler = BackgroundScheduler()


# ════════════════════════════════════════
# JOB FUNCTION
# ════════════════════════════════════════
def scheduled_etl_job():
    """
    Job yang dijalankan secara berkala.
    Ini adalah wrapper untuk run_etl_pipeline dengan error handling.
    """
    logger.info("\n" + "=" * 70)
    logger.info(f"⏰ SCHEDULED ETL JOB STARTED at {datetime.now()}")
    logger.info("=" * 70)
    
    try:
        success = run_etl_pipeline()
        
        if success:
            logger.info(f"✅ Scheduled job completed successfully at {datetime.now()}")
        else:
            logger.error(f"❌ Scheduled job failed at {datetime.now()}")
            
    except Exception as e:
        logger.error(f"❌ Scheduled job crashed: {e}")


# ════════════════════════════════════════
# SCHEDULER START/STOP
# ════════════════════════════════════════
def start_scheduler(hour=2, minute=0):
    """
    Start background scheduler.
    
    Args:
        hour: Hour to run (0-23, default 2 = 2 AM)
        minute: Minute to run (0-59, default 0)
    
    Example:
        start_scheduler(hour=2, minute=0)  # Run at 2:00 AM every day
    """
    global scheduler
    
    try:
        if scheduler.running:
            logger.warning("⚠️  Scheduler already running")
            return False
        
        # Add job: run every day at specified time
        scheduler.add_job(
            scheduled_etl_job,
            trigger=CronTrigger(hour=hour, minute=minute),
            id='etl_daily_job',
            name='Daily ETL Pipeline',
            replace_existing=True
        )
        
        scheduler.start()
        
        logger.info("=" * 70)
        logger.info(f"✅ Scheduler started successfully")
        logger.info(f"📅 Next run: {scheduler.get_job('etl_daily_job').next_run_time}")
        logger.info(f"⏰ Schedule: Every day at {hour:02d}:{minute:02d}")
        logger.info("=" * 70)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to start scheduler: {e}")
        return False


def stop_scheduler():
    """Stop the scheduler"""
    global scheduler
    
    try:
        if not scheduler.running:
            logger.warning("⚠️  Scheduler is not running")
            return False
        
        scheduler.shutdown()
        logger.info("✅ Scheduler stopped successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to stop scheduler: {e}")
        return False


def get_scheduler_status():
    """Get scheduler status and next run time"""
    global scheduler
    
    if not scheduler.running:
        return {
            'running': False,
            'message': 'Scheduler is not running'
        }
    
    job = scheduler.get_job('etl_daily_job')
    
    return {
        'running': True,
        'job_name': job.name if job else 'N/A',
        'next_run': str(job.next_run_time) if job else 'N/A',
        'jobs_count': len(scheduler.get_jobs())
    }


# ════════════════════════════════════════
# ENTRY POINT (untuk testing)
# ════════════════════════════════════════
if __name__ == "__main__":
    import time
    
    logger.info("Starting scheduler for testing...")
    
    # Start scheduler untuk jalan setiap hari jam 2 pagi
    start_scheduler(hour=2, minute=0)
    
    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping scheduler...")
        stop_scheduler()