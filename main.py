#!/usr/bin/env python3
"""
ScaleX Ventures Portfolio Monitoring System
Main entry point for the monitoring system
"""

import argparse
import logging
import os
import sys
from datetime import datetime

# Import our modules
from scheduler import PortfolioMonitorScheduler
from news_monitor import NewsMonitor
from linkedin_monitor import LinkedInMonitor
from alerts import AlertSystem
from database import MentionDatabase
from config import LOG_LEVEL, LOG_FILE

def setup_logging():
    """Set up logging configuration"""
    log_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'logs/{LOG_FILE}'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Reduce noise from external libraries
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

def check_configuration():
    """Check if required configuration is available"""
    issues = []
    
    # Check API keys
    from config import NEWS_API_KEY, LINKEDIN_ACCESS_TOKEN
    if not NEWS_API_KEY:
        issues.append("NEWS_API_KEY not configured (get from https://newsapi.org/)")
    
    # Check alert configuration
    from config import EMAIL_USERNAME, EMAIL_PASSWORD, SLACK_WEBHOOK_URL
    if not EMAIL_USERNAME and not SLACK_WEBHOOK_URL:
        issues.append("No alert method configured (EMAIL or SLACK)")
    
    if issues:
        print("⚠️  Configuration Issues:")
        for issue in issues:
            print(f"   - {issue}")
        print("\n💡 Create a .env file with the required configuration:")
        print("   NEWS_API_KEY=your_newsapi_key")
        print("   EMAIL_USERNAME=your_email@gmail.com")
        print("   EMAIL_PASSWORD=your_app_password")
        print("   SLACK_WEBHOOK_URL=your_slack_webhook_url")
        print("   ALERT_EMAIL_RECIPIENTS=team@example.com,alerts@example.com")
        return False
    
    return True

def run_once():
    """Run monitoring cycle once"""
    print("🚀 Running ScaleX Ventures Portfolio Monitor (Single Run)")
    print("=" * 60)
    
    scheduler = PortfolioMonitorScheduler()
    scheduler.run_once()
    
    print("\n✅ Single monitoring cycle completed")

def run_scheduler():
    """Run continuous monitoring with scheduler"""
    print("🚀 Starting ScaleX Ventures Portfolio Monitor (Continuous)")
    print("=" * 60)
    
    scheduler = PortfolioMonitorScheduler()
    
    try:
        scheduler.start()
        print("📊 Monitor is running... Press Ctrl+C to stop")
        
        # Keep main thread alive
        while scheduler.running:
            import time
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping monitor...")
    finally:
        scheduler.stop()
        print("✅ Monitor stopped")

def show_status():
    """Show current monitoring status"""
    print("📊 ScaleX Ventures Portfolio Monitor Status")
    print("=" * 50)
    
    db = MentionDatabase()
    stats = db.get_statistics()
    
    print(f"📈 Total mentions tracked: {stats['total_mentions']}")
    print(f"🔥 Recent mentions (24h): {stats['recent_mentions_24h']}")
    
    print("\n📊 Mentions by Company:")
    for company, count in stats['mentions_by_company'].items():
        print(f"   {company}: {count}")
    
    print("\n📰 Mentions by Source:")
    for source, count in stats['mentions_by_source'].items():
        print(f"   {source}: {count}")

def test_alerts():
    """Test alert system"""
    print("🔔 Testing Alert System")
    print("=" * 30)
    
    # Create test mention
    test_mention = {
        'company_name': 'Test Company',
        'title': 'Test Alert - ScaleX Portfolio Monitor',
        'content': 'This is a test alert to verify the monitoring system is working correctly.',
        'url': 'https://example.com/test',
        'source': 'Test Source',
        'published_date': datetime.now().isoformat(),
        'sentiment_score': 0.5
    }
    
    db = MentionDatabase()
    alert_system = AlertSystem(db)
    
    results = alert_system.send_alerts([test_mention])
    
    print("Alert test results:")
    for alert_type, success in results.items():
        status = "✅ Success" if success else "❌ Failed"
        print(f"   {alert_type}: {status}")

def show_companies():
    """Show configured portfolio companies"""
    from config import PORTFOLIO_COMPANIES
    
    print("🏢 ScaleX Ventures Portfolio Companies")
    print("=" * 40)
    
    for i, company in enumerate(PORTFOLIO_COMPANIES, 1):
        print(f"{i}. {company['name']}")
        print(f"   Description: {company['description']}")
        print(f"   Keywords: {', '.join(company['keywords'])}")
        print()

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="ScaleX Ventures Portfolio Monitoring System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py run-once          # Run monitoring once
  python main.py start            # Start continuous monitoring
  python main.py status           # Show current status
  python main.py test-alerts      # Test alert system
  python main.py companies        # Show portfolio companies
        """
    )
    
    parser.add_argument(
        'command',
        choices=['run-once', 'start', 'status', 'test-alerts', 'companies'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '--skip-config-check',
        action='store_true',
        help='Skip configuration validation'
    )
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Show banner
    print("🚀 ScaleX Ventures Portfolio Monitoring System")
    print("=" * 50)
    
    # Check configuration (unless skipped)
    if not args.skip_config_check and args.command not in ['companies', 'status']:
        if not check_configuration():
            sys.exit(1)
    
    # Execute command
    try:
        if args.command == 'run-once':
            run_once()
        elif args.command == 'start':
            run_scheduler()
        elif args.command == 'status':
            show_status()
        elif args.command == 'test-alerts':
            test_alerts()
        elif args.command == 'companies':
            show_companies()
            
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
