"""
Scheduler for automated portfolio monitoring
Handles periodic execution of monitoring tasks
"""

import schedule
import time
import logging
from datetime import datetime
from typing import Optional
import threading
import signal
import sys

from news_monitor import NewsMonitor
from linkedin_monitor import LinkedInMonitor
from alerts import AlertSystem
from database import MentionDatabase
from config import CHECK_INTERVAL_MINUTES

logger = logging.getLogger(__name__)

class PortfolioMonitorScheduler:
    def __init__(self):
        self.db = MentionDatabase()
        self.news_monitor = NewsMonitor(self.db)
        self.linkedin_monitor = LinkedInMonitor(self.db)
        self.alert_system = AlertSystem(self.db)
        self.running = False
        self.scheduler_thread = None
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop()
        sys.exit(0)
    
    def run_monitoring_cycle(self):
        """Run a complete monitoring cycle"""
        try:
            logger.info("=" * 50)
            logger.info("Starting monitoring cycle")
            logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            all_new_mentions = []
            
            # Monitor news sources
            logger.info("Monitoring news sources...")
            news_mentions = self.news_monitor.monitor_all_companies()
            all_new_mentions.extend(news_mentions)
            
            # Monitor LinkedIn
            logger.info("Monitoring LinkedIn...")
            linkedin_mentions = self.linkedin_monitor.monitor_all_companies()
            all_new_mentions.extend(linkedin_mentions)
            
            # Send alerts if new mentions found
            if all_new_mentions:
                logger.info(f"Found {len(all_new_mentions)} new mentions, sending alerts...")
                alert_results = self.alert_system.send_alerts(all_new_mentions)
                logger.info(f"Alert results: {alert_results}")
            else:
                logger.info("No new mentions found")
            
            # Log statistics
            stats = self.db.get_statistics()
            logger.info(f"Database statistics: {stats}")
            
            logger.info("Monitoring cycle completed successfully")
            logger.info("=" * 50)
            
        except Exception as e:
            logger.error(f"Error during monitoring cycle: {e}")
            raise
    
    def run_daily_summary(self):
        """Generate and send daily summary"""
        try:
            logger.info("Generating daily summary...")
            summary = self.alert_system.create_daily_summary()
            
            # You could send this summary via email or Slack
            logger.info(f"Daily summary: {summary}")
            
            # Optionally send summary as alert
            if summary['total_mentions'] > 0:
                # Create a summary "mention" for alerting
                summary_mention = {
                    'company_name': 'Daily Summary',
                    'title': f"Daily Portfolio Monitoring Summary - {summary['total_mentions']} mentions",
                    'content': f"Summary for {summary['date']}",
                    'url': '',
                    'source': 'Internal Summary',
                    'published_date': datetime.now().isoformat(),
                    'sentiment_score': 0.0
                }
                
                # Send summary alert (you might want to create a separate method for this)
                # self.alert_system.send_alerts([summary_mention])
            
        except Exception as e:
            logger.error(f"Error generating daily summary: {e}")
    
    def setup_schedule(self):
        """Set up the monitoring schedule"""
        # Main monitoring cycle
        schedule.every(CHECK_INTERVAL_MINUTES).minutes.do(self.run_monitoring_cycle)
        
        # Daily summary at 9 AM
        schedule.every().day.at("09:00").do(self.run_daily_summary)
        
        # Weekly cleanup (optional)
        schedule.every().sunday.at("02:00").do(self.cleanup_old_data)
        
        logger.info(f"Scheduler configured:")
        logger.info(f"- Monitoring cycle: every {CHECK_INTERVAL_MINUTES} minutes")
        logger.info(f"- Daily summary: 09:00")
        logger.info(f"- Weekly cleanup: Sunday 02:00")
    
    def cleanup_old_data(self):
        """Clean up old data from database"""
        try:
            logger.info("Running weekly cleanup...")
            # This would implement cleanup logic
            # For example, delete mentions older than 30 days
            # or archive old data
            pass
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def start(self, run_immediately: bool = True):
        """Start the scheduler"""
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        self.setup_schedule()
        self.running = True
        
        # Run monitoring cycle immediately if requested
        if run_immediately:
            logger.info("Running initial monitoring cycle...")
            self.run_monitoring_cycle()
        
        # Start scheduler in a separate thread
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("Portfolio monitoring scheduler started")
    
    def _run_scheduler(self):
        """Internal method to run the scheduler loop"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(60)  # Wait a minute before retrying
    
    def stop(self):
        """Stop the scheduler"""
        logger.info("Stopping scheduler...")
        self.running = False
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        
        logger.info("Scheduler stopped")
    
    def run_once(self):
        """Run monitoring cycle once (for testing or manual execution)"""
        logger.info("Running single monitoring cycle...")
        self.run_monitoring_cycle()
    
    def get_status(self) -> dict:
        """Get current status of the scheduler"""
        return {
            'running': self.running,
            'next_jobs': [
                {
                    'job': str(job.job_func),
                    'next_run': job.next_run.strftime('%Y-%m-%d %H:%M:%S') if job.next_run else None
                }
                for job in schedule.jobs
            ],
            'database_stats': self.db.get_statistics()
        }

def main():
    """Main entry point for running the scheduler"""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('portfolio_monitor.log'),
            logging.StreamHandler()
        ]
    )
    
    logger.info("Starting ScaleX Ventures Portfolio Monitor")
    
    # Create and start scheduler
    scheduler = PortfolioMonitorScheduler()
    
    try:
        scheduler.start()
        
        # Keep the main thread alive
        while scheduler.running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        scheduler.stop()
        logger.info("Portfolio monitor shutdown complete")

if __name__ == "__main__":
    main()
