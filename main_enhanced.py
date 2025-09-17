#!/usr/bin/env python3
"""
ScaleX Ventures Portfolio Monitoring System - ENHANCED VERSION
Includes NewsAPI + Free LinkedIn monitoring
"""

import argparse
import logging
import os
import sys
from datetime import datetime

# Import our modules
from news_monitor_minimal import MinimalNewsMonitor
from linkedin_monitor_free import FreeLinkedInMonitor
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

def run_enhanced_demo():
    """Run enhanced demo with NewsAPI + LinkedIn monitoring"""
    print("🚀 ScaleX Ventures Portfolio Monitor - ENHANCED DEMO")
    print("=" * 60)
    print("✨ Now with NewsAPI + Free LinkedIn monitoring!")
    print("📰 NewsAPI: Better precision and historical data")
    print("💼 LinkedIn: Free Google site search + company RSS")
    print("=" * 60)
    
    # Initialize components
    db = MentionDatabase()
    news_monitor = MinimalNewsMonitor(db)
    linkedin_monitor = FreeLinkedInMonitor(db)
    alert_system = MinimalAlertSystem(db)
    
    print("\n🔍 Starting enhanced monitoring cycle...")
    print("-" * 40)
    
    all_mentions = []
    
    # Monitor news sources
    print("\n📰 Monitoring NEWS sources...")
    news_mentions = news_monitor.monitor_all_companies()
    all_mentions.extend(news_mentions)
    
    # Monitor LinkedIn
    print("\n💼 Monitoring LINKEDIN sources...")
    linkedin_mentions = linkedin_monitor.monitor_all_companies()
    all_mentions.extend(linkedin_mentions)
    
    if all_mentions:
        print(f"\n🎉 Found {len(all_mentions)} total new mentions!")
        print(f"   📰 News: {len(news_mentions)} mentions")
        print(f"   💼 LinkedIn: {len(linkedin_mentions)} mentions")
        print("\n📤 Sending alerts...")
        
        # Send alerts
        alert_system.send_alerts(all_mentions)
    else:
        print("\nℹ️  No new mentions found this time")
        print("💡 This is normal - the system is working correctly!")
    
    # Show statistics
    stats = db.get_statistics()
    print(f"\n📊 Database Statistics:")
    print(f"   Total mentions tracked: {stats['total_mentions']}")
    print(f"   Recent mentions (24h): {stats['recent_mentions_24h']}")
    
    if stats['mentions_by_company']:
        print(f"\n📈 Mentions by Company:")
        for company, count in stats['mentions_by_company'].items():
            print(f"   {company}: {count}")
    
    if stats['mentions_by_source']:
        print(f"\n📰 Mentions by Source:")
        for source, count in stats['mentions_by_source'].items():
            print(f"   {source}: {count}")
    
    print(f"\n✅ Enhanced demo completed successfully!")
    print("=" * 60)

def run_news_only_demo():
    """Run news-only demo (NewsAPI + Google News)"""
    print("🚀 ScaleX Ventures Portfolio Monitor - NEWS ONLY DEMO")
    print("=" * 60)
    print("📰 NewsAPI + Google News RSS feeds")
    print("=" * 60)
    
    db = MentionDatabase()
    news_monitor = MinimalNewsMonitor(db)
    alert_system = MinimalAlertSystem(db)
    
    print("\n🔍 Starting news monitoring...")
    mentions = news_monitor.monitor_all_companies()
    
    if mentions:
        print(f"\n🎉 Found {len(mentions)} news mentions!")
        alert_system.send_alerts(mentions)
    else:
        print("\nℹ️  No new news mentions found")
    
    # Show statistics
    stats = db.get_statistics()
    print(f"\n📊 News Statistics:")
    print(f"   Total mentions: {stats['total_mentions']}")
    print(f"   Recent (24h): {stats['recent_mentions_24h']}")

def run_linkedin_only_demo():
    """Run LinkedIn-only demo"""
    print("🚀 ScaleX Ventures Portfolio Monitor - LINKEDIN ONLY DEMO")
    print("=" * 60)
    print("💼 Free LinkedIn monitoring via Google search")
    print("=" * 60)
    
    db = MentionDatabase()
    linkedin_monitor = FreeLinkedInMonitor(db)
    alert_system = MinimalAlertSystem(db)
    
    print("\n🔍 Starting LinkedIn monitoring...")
    mentions = linkedin_monitor.monitor_all_companies()
    
    if mentions:
        print(f"\n🎉 Found {len(mentions)} LinkedIn mentions!")
        alert_system.send_alerts(mentions)
    else:
        print("\nℹ️  No new LinkedIn mentions found")
        print("💡 LinkedIn monitoring uses Google site search")
        print("   Results may vary based on search availability")
    
    # Show LinkedIn insights
    insights = linkedin_monitor.get_linkedin_insights()
    print(f"\n📊 LinkedIn Insights:")
    print(f"   Total LinkedIn mentions: {insights['total_linkedin_mentions']}")
    
    if insights['mentions_by_company']:
        print(f"   By company: {insights['mentions_by_company']}")

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
    
    # Check if NewsAPI key is configured
    news_api_key = os.getenv('NEWS_API_KEY', '')
    if news_api_key:
        print(f"\n✅ NewsAPI configured: {news_api_key[:8]}...")
    else:
        print(f"\n⚠️  NewsAPI not configured (using Google News only)")
    
    print(f"\n🎯 Demo Mode: {'ON' if DEMO_MODE else 'OFF'}")
    print("💡 Enhanced version with NewsAPI + Free LinkedIn monitoring!")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="ScaleX Ventures Portfolio Monitoring System - ENHANCED VERSION",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
ENHANCED COMMANDS:
  python3 main_enhanced.py enhanced     # Full demo (NewsAPI + LinkedIn)
  python3 main_enhanced.py news         # News only (NewsAPI + Google News)
  python3 main_enhanced.py linkedin     # LinkedIn only (Google search)
  python3 main_enhanced.py companies    # Show portfolio companies
  python3 main_enhanced.py status       # Show current status

This enhanced version includes:
✅ NewsAPI integration (better precision)
✅ Free LinkedIn monitoring (Google site search)
✅ Company RSS feeds (when available)
✅ All previous features (sentiment analysis, database, alerts)
        """
    )
    
    parser.add_argument(
        'command',
        choices=['enhanced', 'news', 'linkedin', 'companies', 'status'],
        help='Command to execute'
    )
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Show banner
    print("🚀 ScaleX Ventures Portfolio Monitoring System - ENHANCED")
    print("=" * 60)
    print("✨ NewsAPI + Free LinkedIn Monitoring - Perfect for Interviews!")
    print("=" * 60)
    
    # Execute command
    try:
        if args.command == 'enhanced':
            run_enhanced_demo()
        elif args.command == 'news':
            run_news_only_demo()
        elif args.command == 'linkedin':
            run_linkedin_only_demo()
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
