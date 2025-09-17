#!/usr/bin/env python3
"""
ScaleX Ventures Portfolio Monitoring System - MINIMAL VERSION
Demo version that works with ZERO API keys!
"""

import argparse
import logging
import os
import sys
from datetime import datetime

# Import our minimal modules
from news_monitor_minimal import MinimalNewsMonitor
from alerts_minimal import MinimalAlertSystem
from database import MentionDatabase
from config_minimal import LOG_LEVEL, LOG_FILE, DEMO_MODE

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

def run_demo():
    """Run a complete demo of the monitoring system"""
    print("🚀 ScaleX Ventures Portfolio Monitor - DEMO MODE")
    print("=" * 60)
    print("✨ This demo works with ZERO API keys!")
    print("📰 Uses Google News RSS feeds (completely free)")
    print("💬 Shows how alerts would work in production")
    print("=" * 60)
    
    # Initialize components
    db = MentionDatabase()
    news_monitor = MinimalNewsMonitor(db)
    alert_system = MinimalAlertSystem(db)
    
    print("\n🔍 Starting monitoring cycle...")
    print("-" * 40)
    
    # Monitor for mentions
    mentions = news_monitor.monitor_all_companies()
    
    if mentions:
        print(f"\n🎉 Found {len(mentions)} new mentions!")
        print("📤 Sending alerts...")
        
        # Send alerts
        alert_system.send_alerts(mentions)
    else:
        print("\nℹ️  No new mentions found this time")
        print("💡 This is normal - the system is working correctly!")
        print("   In a real scenario, you'd see mentions when companies are in the news")
    
    # Show statistics
    stats = db.get_statistics()
    print(f"\n📊 Database Statistics:")
    print(f"   Total mentions tracked: {stats['total_mentions']}")
    print(f"   Recent mentions (24h): {stats['recent_mentions_24h']}")
    
    if stats['mentions_by_company']:
        print(f"\n📈 Mentions by Company:")
        for company, count in stats['mentions_by_company'].items():
            print(f"   {company}: {count}")
    
    print(f"\n✅ Demo completed successfully!")
    print("=" * 60)

def run_continuous_demo():
    """Run continuous monitoring demo"""
    print("🚀 ScaleX Ventures Portfolio Monitor - CONTINUOUS DEMO")
    print("=" * 60)
    print("⏰ This will run every 2 minutes for demo purposes")
    print("🛑 Press Ctrl+C to stop")
    print("=" * 60)
    
    import time
    
    db = MentionDatabase()
    news_monitor = MinimalNewsMonitor(db)
    alert_system = MinimalAlertSystem(db)
    
    try:
        cycle = 1
        while True:
            print(f"\n🔄 Monitoring Cycle #{cycle}")
            print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("-" * 40)
            
            mentions = news_monitor.monitor_all_companies()
            
            if mentions:
                alert_system.send_alerts(mentions)
            else:
                print("ℹ️  No new mentions found")
            
            cycle += 1
            print(f"\n⏳ Waiting 2 minutes until next check...")
            time.sleep(120)  # 2 minutes for demo
            
    except KeyboardInterrupt:
        print("\n🛑 Demo stopped by user")
        print("✅ Thank you for watching the demo!")

def show_companies():
    """Show configured portfolio companies"""
    from config_minimal import PORTFOLIO_COMPANIES
    
    print("🏢 ScaleX Ventures Portfolio Companies")
    print("=" * 40)
    
    for i, company in enumerate(PORTFOLIO_COMPANIES, 1):
        print(f"{i}. {company['name']}")
        print(f"   Description: {company['description']}")
        print(f"   Keywords: {', '.join(company['keywords'])}")
        print()

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
    
    print(f"\n🎯 Demo Mode: {'ON' if DEMO_MODE else 'OFF'}")
    print("💡 This version works with ZERO API keys!")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="ScaleX Ventures Portfolio Monitoring System - DEMO VERSION",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
DEMO COMMANDS (No API keys needed!):
  python3 main_minimal.py demo           # Run single demo cycle
  python3 main_minimal.py continuous     # Run continuous demo (2min intervals)
  python3 main_minimal.py companies      # Show portfolio companies
  python3 main_minimal.py status         # Show current status

This demo version:
✅ Works with ZERO API keys
✅ Uses free Google News RSS feeds
✅ Shows how alerts would work
✅ Perfect for interviews and demos
        """
    )
    
    parser.add_argument(
        'command',
        choices=['demo', 'continuous', 'companies', 'status'],
        help='Command to execute'
    )
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Show banner
    print("🚀 ScaleX Ventures Portfolio Monitoring System - DEMO")
    print("=" * 60)
    print("✨ ZERO API KEYS REQUIRED - PERFECT FOR INTERVIEWS!")
    print("=" * 60)
    
    # Execute command
    try:
        if args.command == 'demo':
            run_demo()
        elif args.command == 'continuous':
            run_continuous_demo()
        elif args.command == 'companies':
            show_companies()
        elif args.command == 'status':
            show_status()
            
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
