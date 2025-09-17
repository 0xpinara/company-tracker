"""
Minimal Alert system for demo purposes
Uses simple print statements and console output instead of email/Slack
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime
import json

from config_minimal import DEMO_MODE, DEMO_ALERT_EMAIL, DEMO_ALERT_SLACK
from database import MentionDatabase

logger = logging.getLogger(__name__)

class MinimalAlertSystem:
    def __init__(self, db: MentionDatabase):
        self.db = db
    
    def format_mention_for_alert(self, mention: Dict) -> Dict:
        """Format a mention for alert display"""
        sentiment_emoji = self._get_sentiment_emoji(mention.get('sentiment_score', 0))
        
        return {
            'company': mention['company_name'],
            'title': mention['title'],
            'content': mention.get('content', '')[:150] + '...' if len(mention.get('content', '')) > 150 else mention.get('content', ''),
            'url': mention['url'],
            'source': mention['source'],
            'published_date': mention.get('published_date', ''),
            'sentiment_score': mention.get('sentiment_score', 0),
            'sentiment_emoji': sentiment_emoji,
            'created_at': mention.get('created_at', '')
        }
    
    def _get_sentiment_emoji(self, score: float) -> str:
        """Get emoji based on sentiment score"""
        if score > 0.3:
            return "😊"  # Positive
        elif score < -0.3:
            return "😟"  # Negative
        else:
            return "😐"  # Neutral
    
    def send_console_alert(self, mentions: List[Dict]) -> bool:
        """Send alert to console (perfect for demo)"""
        if not mentions:
            print("ℹ️  No new mentions to alert about")
            return True
        
        print("\n" + "="*80)
        print("🚀 SCALEX VENTURES PORTFOLIO ALERT")
        print("="*80)
        print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 Total New Mentions: {len(mentions)}")
        print("="*80)
        
        # Group mentions by company
        mentions_by_company = {}
        for mention in mentions:
            company = mention['company_name']
            if company not in mentions_by_company:
                mentions_by_company[company] = []
            mentions_by_company[company].append(self.format_mention_for_alert(mention))
        
        for company, company_mentions in mentions_by_company.items():
            print(f"\n📈 {company.upper()} ({len(company_mentions)} mentions)")
            print("-" * 50)
            
            for i, mention in enumerate(company_mentions, 1):
                print(f"\n{i}. {mention['title']} {mention['sentiment_emoji']}")
                print(f"   📝 {mention['content']}")
                print(f"   🔗 {mention['url']}")
                print(f"   📰 Source: {mention['source']}")
                print(f"   📊 Sentiment: {mention['sentiment_score']:.2f}")
                if mention['published_date']:
                    print(f"   📅 Published: {mention['published_date']}")
        
        print("\n" + "="*80)
        print("💡 DEMO MODE: In production, these would be sent via email/Slack")
        print("="*80)
        
        return True
    
    def send_demo_email_alert(self, mentions: List[Dict]) -> bool:
        """Simulate email alert (demo mode)"""
        if not mentions:
            return True
        
        print(f"\n📧 DEMO EMAIL ALERT")
        print(f"To: {DEMO_ALERT_EMAIL}")
        print(f"Subject: ScaleX Ventures Portfolio Alert - {len(mentions)} New Mentions")
        print("-" * 50)
        
        # Group by company
        mentions_by_company = {}
        for mention in mentions:
            company = mention['company_name']
            if company not in mentions_by_company:
                mentions_by_company[company] = []
            mentions_by_company[company].append(self.format_mention_for_alert(mention))
        
        for company, company_mentions in mentions_by_company.items():
            print(f"\n{company} ({len(company_mentions)} mentions):")
            for mention in company_mentions:
                print(f"• {mention['title']} {mention['sentiment_emoji']}")
                print(f"  {mention['content']}")
                print(f"  Read more: {mention['url']}")
        
        return True
    
    def send_demo_slack_alert(self, mentions: List[Dict]) -> bool:
        """Simulate Slack alert (demo mode)"""
        if not mentions:
            return True
        
        print(f"\n💬 DEMO SLACK ALERT")
        print(f"Webhook: {DEMO_ALERT_SLACK}")
        print("-" * 50)
        
        # Group by company
        mentions_by_company = {}
        for mention in mentions:
            company = mention['company_name']
            if company not in mentions_by_company:
                mentions_by_company[company] = []
            mentions_by_company[company].append(self.format_mention_for_alert(mention))
        
        print("🚀 *ScaleX Ventures Portfolio Alert*")
        print(f"Found {len(mentions)} new mentions")
        
        for company, company_mentions in mentions_by_company.items():
            print(f"\n*📊 {company}* ({len(company_mentions)} mentions)")
            for mention in company_mentions[:2]:  # Show top 2 per company
                print(f"• *{mention['title']}* {mention['sentiment_emoji']}")
                print(f"  {mention['content']}")
                print(f"  _Source: {mention['source']}_")
        
        return True
    
    def send_alerts(self, mentions: List[Dict]) -> Dict[str, bool]:
        """Send all configured alerts (demo mode)"""
        if not mentions:
            logger.info("No mentions to alert about")
            return {}
        
        results = {}
        
        # Always send console alert
        results['console'] = self.send_console_alert(mentions)
        
        # Send demo email alert
        results['email_demo'] = self.send_demo_email_alert(mentions)
        
        # Send demo Slack alert
        results['slack_demo'] = self.send_demo_slack_alert(mentions)
        
        # Record alert attempts in database
        for mention in mentions:
            if mention.get('id'):
                self.db.add_alert_record(mention['id'], 'console', 'sent')
                self.db.add_alert_record(mention['id'], 'email_demo', 'sent')
                self.db.add_alert_record(mention['id'], 'slack_demo', 'sent')
        
        logger.info(f"Demo alert results: {results}")
        return results
    
    def create_daily_summary(self) -> Dict:
        """Create daily summary of mentions"""
        mentions = self.db.get_recent_mentions(24)
        
        summary = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'total_mentions': len(mentions),
            'mentions_by_company': {},
            'sentiment_analysis': {},
            'top_sources': {},
            'trending_topics': []
        }
        
        # Analyze mentions
        for mention in mentions:
            company = mention['company_name']
            source = mention['source']
            
            # Count by company
            summary['mentions_by_company'][company] = \
                summary['mentions_by_company'].get(company, 0) + 1
            
            # Count by source
            summary['top_sources'][source] = \
                summary['top_sources'].get(source, 0) + 1
            
            # Sentiment analysis
            if company not in summary['sentiment_analysis']:
                summary['sentiment_analysis'][company] = []
            
            if mention.get('sentiment_score') is not None:
                summary['sentiment_analysis'][company].append(mention['sentiment_score'])
        
        # Calculate average sentiment
        for company, scores in summary['sentiment_analysis'].items():
            if scores:
                summary['sentiment_analysis'][company] = {
                    'average': sum(scores) / len(scores),
                    'count': len(scores)
                }
        
        return summary
