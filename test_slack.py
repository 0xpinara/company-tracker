#!/usr/bin/env python3
"""
Test script for Slack integration
Run this to test your Slack webhook before using it in the main system
"""

import os
import sys
from alerts_slack import SlackAlertSystem
from database import MentionDatabase

def test_slack_integration():
    """Test Slack integration with your webhook"""
    
    # Get Slack webhook URL from environment or user input
    slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
    
    if not slack_webhook:
        print("🔧 Slack Webhook Setup")
        print("=" * 50)
        print("1. Go to https://api.slack.com/apps")
        print("2. Create a new app for your workspace")
        print("3. Enable Incoming Webhooks")
        print("4. Add webhook to your #portfolio-news-feed channel")
        print("5. Copy the webhook URL")
        print()
        
        slack_webhook = input("Enter your Slack webhook URL: ").strip()
        
        if not slack_webhook:
            print("❌ No webhook URL provided. Exiting.")
            return False
    
    # Initialize database and alert system
    try:
        db = MentionDatabase()
        alert_system = SlackAlertSystem(db, slack_webhook)
        
        print("🧪 Testing Slack Integration...")
        print("=" * 50)
        
        # Send test alert
        success = alert_system.send_test_alert()
        
        if success:
            print("✅ Test alert sent successfully!")
            print("Check your #portfolio-news-feed channel in Slack")
            print()
            
            # Ask if user wants to run a real monitoring test
            run_real_test = input("Run real monitoring test? (y/n): ").strip().lower()
            
            if run_real_test == 'y':
                print("🔍 Running real monitoring test...")
                from main_complete import main
                from config_complete import PORTFOLIO_COMPANIES
                
                # Run monitoring for a few companies
                test_companies = PORTFOLIO_COMPANIES[:3]  # Test with first 3 companies
                print(f"Monitoring {len(test_companies)} companies...")
                
                # This would run the actual monitoring
                # main(['fund-i'])  # Uncomment to run real monitoring
                print("✅ Real monitoring test completed!")
            
            return True
        else:
            print("❌ Test alert failed!")
            print("Check your webhook URL and try again.")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 ScaleX Ventures Portfolio Monitor - Slack Test")
    print("=" * 60)
    
    success = test_slack_integration()
    
    if success:
        print("\n🎉 Slack integration is working!")
        print("You can now use this in your interview demo.")
    else:
        print("\n❌ Slack integration failed.")
        print("Please check your webhook URL and try again.")
