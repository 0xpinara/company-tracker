#!/usr/bin/env python3
"""
ScaleX Ventures Portfolio Monitoring System - COMPLETE VERSION
Monitors ALL 30+ portfolio companies from their website
"""

import argparse
import logging
import os
import sys
from datetime import datetime

# Import our modules
from news_monitor_complete import CompleteNewsMonitor
from linkedin_monitor_free import FreeLinkedInMonitor
from alerts_minimal import MinimalAlertSystem
try:
    from alerts_slack import SlackAlertSystem
except Exception:
    SlackAlertSystem = None  # Fallback if module not available
from database import MentionDatabase
from config_complete import (
    LOG_LEVEL, LOG_FILE, DEMO_MODE, PORTFOLIO_COMPANIES,
    TOTAL_COMPANIES, FUND_I_COMPANIES, ACQUIRED_COMPANIES, ANGEL_COMPANIES
)

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

def run_complete_demo():
    """Run complete demo with ALL portfolio companies"""
    print("🚀 ScaleX Ventures Portfolio Monitor - COMPLETE DEMO")
    print("=" * 70)
    print(f"✨ Monitoring ALL {TOTAL_COMPANIES} portfolio companies!")
    print(f"📊 Fund I: {FUND_I_COMPANIES} companies | Acquired: {ACQUIRED_COMPANIES} | Angel: {ANGEL_COMPANIES}")
    print("📰 NewsAPI + Google News + Free LinkedIn monitoring")
    print("=" * 70)
    
    # Initialize components
    db = MentionDatabase()
    news_monitor = CompleteNewsMonitor(db)
    linkedin_monitor = FreeLinkedInMonitor(db)
    # Choose alert system: Slack if webhook configured, else minimal console alerts
    slack_webhook = os.getenv('SLACK_WEBHOOK_URL', '').strip()
    if SlackAlertSystem and slack_webhook:
        alert_system = SlackAlertSystem(db, slack_webhook)
    else:
        alert_system = MinimalAlertSystem(db)
    
    print("\n🔍 Starting complete monitoring cycle...")
    print("-" * 50)
    
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
        
        # Send alerts (Slack if available, otherwise console)
        if hasattr(alert_system, 'send_slack_alert'):
            alert_system.send_slack_alert(all_mentions)
        else:
            alert_system.send_alerts(all_mentions)
    else:
        print("\nℹ️  No new mentions found this time")
        print("💡 This is normal - the system is working correctly!")
    
    # Show comprehensive statistics
    stats = db.get_statistics()
    print(f"\n📊 Complete Portfolio Statistics:")
    print(f"   Total mentions tracked: {stats['total_mentions']}")
    print(f"   Recent mentions (24h): {stats['recent_mentions_24h']}")
    print(f"   Companies monitored: {TOTAL_COMPANIES}")
    
    if stats['mentions_by_company']:
        print(f"\n📈 Top Companies by Mentions:")
        sorted_companies = sorted(stats['mentions_by_company'].items(), key=lambda x: x[1], reverse=True)
        for company, count in sorted_companies[:10]:  # Show top 10
            print(f"   {company}: {count}")
        
        if len(sorted_companies) > 10:
            print(f"   ... and {len(sorted_companies) - 10} more companies")
    
    if stats['mentions_by_source']:
        print(f"\n📰 Mentions by Source:")
        for source, count in list(stats['mentions_by_source'].items())[:5]:  # Show top 5
            print(f"   {source}: {count}")
    
    print(f"\n✅ Complete demo finished successfully!")
    print("=" * 70)

def run_fund_i_demo():
    """Run demo for Fund I companies only"""
    print("🚀 ScaleX Ventures Portfolio Monitor - FUND I DEMO")
    print("=" * 60)
    print(f"✨ Monitoring {FUND_I_COMPANIES} Fund I companies")
    print("📰 NewsAPI + Google News + Free LinkedIn monitoring")
    print("=" * 60)
    
    # Filter to Fund I companies only
    fund_i_companies = [c for c in PORTFOLIO_COMPANIES if c['fund'] == 'FUND I']
    
    print(f"\n🏢 Fund I Companies:")
    for i, company in enumerate(fund_i_companies, 1):
        print(f"   {i:2d}. {company['name']} - {company['description']}")
    
    # Initialize components
    db = MentionDatabase()
    news_monitor = CompleteNewsMonitor(db)
    linkedin_monitor = FreeLinkedInMonitor(db)
    # Choose alert system: Slack if webhook configured, else minimal console alerts
    slack_webhook = os.getenv('SLACK_WEBHOOK_URL', '').strip()
    if SlackAlertSystem and slack_webhook:
        alert_system = SlackAlertSystem(db, slack_webhook)
    else:
        alert_system = MinimalAlertSystem(db)
    
    print(f"\n🔍 Starting Fund I monitoring...")
    print("-" * 40)
    
    all_mentions = []
    
    # Monitor news sources
    print("\n📰 Monitoring NEWS sources...")
    news_mentions = news_monitor.monitor_all_companies()
    all_mentions.extend(news_mentions)
    
    if all_mentions:
        print(f"\n🎉 Found {len(all_mentions)} new mentions!")
        if hasattr(alert_system, 'send_slack_alert'):
            alert_system.send_slack_alert(all_mentions)
        else:
            alert_system.send_alerts(all_mentions)
    else:
        print("\nℹ️  No new mentions found")
    
    print(f"\n✅ Fund I demo completed!")
    print("=" * 60)

def show_complete_portfolio():
    """Show ALL portfolio companies organized by fund"""
    print("🏢 ScaleX Ventures Complete Portfolio")
    print("=" * 50)
    
    # Group by fund
    fund_i = [c for c in PORTFOLIO_COMPANIES if c['fund'] == 'FUND I']
    acquired = [c for c in PORTFOLIO_COMPANIES if c['fund'] == 'ACQUIRED']
    angel = [c for c in PORTFOLIO_COMPANIES if c['fund'] == 'ANGEL']
    
    print(f"\n🚀 FUND I ({len(fund_i)} companies):")
    print("-" * 30)
    for i, company in enumerate(fund_i, 1):
        print(f"{i:2d}. {company['name']}")
        print(f"    {company['description']}")
        print(f"    Website: {company['website']}")
        print()
    
    print(f"\n💰 ACQUIRED ({len(acquired)} companies):")
    print("-" * 30)
    for i, company in enumerate(acquired, 1):
        print(f"{i:2d}. {company['name']}")
        print(f"    {company['description']}")
        print(f"    Website: {company['website']}")
        print()
    
    print(f"\n👼 ANGEL INVESTMENTS ({len(angel)} companies):")
    print("-" * 30)
    for i, company in enumerate(angel, 1):
        print(f"{i:2d}. {company['name']}")
        print(f"    {company['description']}")
        print(f"    Website: {company['website']}")
        print()
    
    print(f"📊 PORTFOLIO SUMMARY:")
    print(f"   Total Companies: {TOTAL_COMPANIES}")
    print(f"   Fund I: {FUND_I_COMPANIES}")
    print(f"   Acquired: {ACQUIRED_COMPANIES}")
    print(f"   Angel: {ANGEL_COMPANIES}")

def show_status():
    """Show current monitoring status"""
    print("📊 ScaleX Ventures Portfolio Monitor - COMPLETE STATUS")
    print("=" * 60)
    
    db = MentionDatabase()
    stats = db.get_statistics()
    
    print(f"📈 Total mentions tracked: {stats['total_mentions']}")
    print(f"🔥 Recent mentions (24h): {stats['recent_mentions_24h']}")
    print(f"🏢 Companies monitored: {TOTAL_COMPANIES}")
    
    print(f"\n📊 Portfolio Breakdown:")
    print(f"   Fund I: {FUND_I_COMPANIES} companies")
    print(f"   Acquired: {ACQUIRED_COMPANIES} companies")
    print(f"   Angel: {ANGEL_COMPANIES} companies")
    
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
    print("💡 Complete version monitoring ALL portfolio companies!")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="ScaleX Ventures Portfolio Monitoring System - COMPLETE VERSION",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
COMPLETE PORTFOLIO COMMANDS:
  python3 main_complete.py complete     # Monitor ALL {TOTAL_COMPANIES} companies
  python3 main_complete.py fund-i       # Monitor Fund I companies only
  python3 main_complete.py portfolio    # Show complete portfolio
  python3 main_complete.py status       # Show current status

This complete version monitors:
✅ ALL {TOTAL_COMPANIES} portfolio companies
✅ Fund I: {FUND_I_COMPANIES} companies
✅ Acquired: {ACQUIRED_COMPANIES} companies  
✅ Angel: {ANGEL_COMPANIES} companies
✅ NewsAPI + Google News + Free LinkedIn
        """
    )
    
    parser.add_argument(
        'command',
        choices=['complete', 'fund-i', 'portfolio', 'status'],
        help='Command to execute'
    )
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Show banner
    print("🚀 ScaleX Ventures Portfolio Monitoring System - COMPLETE")
    print("=" * 70)
    print(f"✨ Monitoring ALL {TOTAL_COMPANIES} Portfolio Companies!")
    print("=" * 70)
    
    # Execute command
    try:
        if args.command == 'complete':
            run_complete_demo()
        elif args.command == 'fund-i':
            run_fund_i_demo()
        elif args.command == 'portfolio':
            show_complete_portfolio()
        elif args.command == 'status':
            show_status()
            
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
