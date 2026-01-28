"""
Scheduler for periodic news monitoring

Runs news monitoring at specified intervals (hourly, daily, etc.)
"""

import os
import sys
import schedule
import time
import logging
from pathlib import Path
from dotenv import load_dotenv
from news_monitor import NewsMonitor
from database import get_db

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_monitoring_job():
    """Job to run news monitoring"""
    try:
        logger.info("\n" + "="*60)
        logger.info("SCHEDULED MONITORING JOB STARTED")
        logger.info("="*60)
        
        monitor = NewsMonitor()
        result = monitor.run_once(max_articles_per_source=50)
        
        logger.info("="*60)
        logger.info(f"JOB COMPLETE - Articles: {result['articles_processed']}, "
                   f"Alerts: {result['alerts_triggered']}")
        logger.info("="*60 + "\n")
        
    except Exception as e:
        logger.error(f"Monitoring job failed: {e}", exc_info=True)


def main():
    """Main scheduler function"""
    logger.info("="*60)
    logger.info("News Monitoring Scheduler Started")
    logger.info("="*60)
    
    # Test database connection
    db = get_db()
    if not db.test_connection():
        logger.error("❌ Database connection failed!")
        return 1
    
    db.create_tables()
    logger.info("✓ Database ready")
    
    # Schedule jobs
    # Run every hour
    schedule.every().hour.do(run_monitoring_job)
    
    # Alternative schedules (uncomment as needed):
    # schedule.every(30).minutes.do(run_monitoring_job)  # Every 30 minutes
    # schedule.every().day.at("09:00").do(run_monitoring_job)  # Daily at 9 AM
    # schedule.every().day.at("15:00").do(run_monitoring_job)  # Daily at 3 PM
    
    logger.info("\n📅 Scheduled: Hourly news monitoring")
    logger.info("Press Ctrl+C to stop\n")
    
    # Run once immediately
    logger.info("Running initial monitoring cycle...")
    run_monitoring_job()
    
    # Keep running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    except KeyboardInterrupt:
        logger.info("\n\n🛑 Scheduler stopped by user")
        return 0


if __name__ == "__main__":
    exit(main())
