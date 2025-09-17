"""
Real Slack Alert system for live demo
Sends actual alerts to your Slack workspace
"""

import logging
import requests
import json
from typing import List, Dict, Optional
from datetime import datetime

from config_complete import PORTFOLIO_COMPANIES
from database import MentionDatabase

logger = logging.getLogger(__name__)

class SlackAlertSystem:
    def __init__(self, db: MentionDatabase, slack_webhook_url: str):
        self.db = db
        self.slack_webhook_url = slack_webhook_url
    
    def format_mention_for_alert(self, mention: Dict) -> Dict:
        """Format a mention for alert display"""
        sentiment_emoji = self._get_sentiment_emoji(mention.get('sentiment_score', 0))
        
        return {
            'company': mention['company_name'],
            'title': mention['title'],
            'content': mention.get('content', '')[:200] + '...' if len(mention.get('content', '')) > 200 else mention.get('content', ''),
            'url': mention['url'],
            'source': mention['source'],
            'published_date': mention.get('published_date', ''),
            'sentiment_emoji': sentiment_emoji,
            'sentiment_score': mention.get('sentiment_score', 0)
        }
    
    def _get_sentiment_emoji(self, sentiment_score: float) -> str:
        """Get emoji based on sentiment score"""
        if sentiment_score > 0.1:
            return "😊"
        elif sentiment_score < -0.1:
            return "😟"
        else:
            return "😐"
    
    def send_slack_alert(self, mentions: List[Dict]) -> bool:
        """Send alert to Slack"""
        if not self.slack_webhook_url or not mentions:
            return False
        
        try:
            # Group mentions by company
            company_mentions = {}
            for mention in mentions:
                company = mention['company_name']
                if company not in company_mentions:
                    company_mentions[company] = []
                company_mentions[company].append(mention)
            
            # Create Slack message
            blocks = self._create_slack_blocks(company_mentions)
            
            payload = {
                "text": f"🚀 ScaleX Ventures Portfolio Alert - {len(mentions)} new mentions found!",
                "blocks": blocks
            }
            
            response = requests.post(
                self.slack_webhook_url,
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("✅ Slack alert sent successfully")
                return True
            else:
                logger.error(f"❌ Slack alert failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Slack alert error: {e}")
            return False
    
    def _create_slack_blocks(self, company_mentions: Dict) -> List[Dict]:
        """Create Slack message blocks"""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🚀 ScaleX Ventures Portfolio Alert"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Found *{sum(len(mentions) for mentions in company_mentions.values())}* new mentions across *{len(company_mentions)}* companies"
                }
            },
            {
                "type": "divider"
            }
        ]
        
        # Add each company's mentions
        for company, mentions in company_mentions.items():
            # Company header
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*📊 {company}* ({len(mentions)} mentions)"
                }
            })
            
            # Add each mention
            for mention in mentions[:3]:  # Limit to 3 mentions per company for readability
                formatted = self.format_mention_for_alert(mention)
                
                # Truncate title if too long
                title = formatted['title']
                if len(title) > 80:
                    title = title[:77] + "..."
                
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"• *{title}* {formatted['sentiment_emoji']}\n  <{formatted['url']}|Read more>\n  _{formatted['source']}_"
                    }
                })
            
            # Add "View more" if there are more mentions
            if len(mentions) > 3:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"  _... and {len(mentions) - 3} more mentions_"
                    }
                })
            
            blocks.append({"type": "divider"})
        
        # Add footer
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | ScaleX Ventures Portfolio Monitor"
                }
            ]
        })
        
        return blocks
    
    def send_test_alert(self) -> bool:
        """Send a test alert to verify Slack integration"""
        test_mentions = [
            {
                'company_name': 'Test Company',
                'title': 'Test Alert - ScaleX Ventures Portfolio Monitor',
                'content': 'This is a test alert to verify your Slack integration is working correctly.',
                'url': 'https://scalexventures.com',
                'source': 'Test Source',
                'published_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'sentiment_score': 0.5
            }
        ]
        
        return self.send_slack_alert(test_mentions)
    
    def send_daily_summary(self) -> bool:
        """Send daily summary of all mentions"""
        try:
            # Get all mentions from today
            today = datetime.now().strftime('%Y-%m-%d')
            mentions = self.db.get_mentions_by_date(today)
            
            if not mentions:
                logger.info("No mentions found for today")
                return True
            
            # Group by company
            company_mentions = {}
            for mention in mentions:
                company = mention['company_name']
                if company not in company_mentions:
                    company_mentions[company] = []
                company_mentions[company].append(mention)
            
            # Create summary message
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "📊 Daily Portfolio Summary"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{today}* - Found *{len(mentions)}* mentions across *{len(company_mentions)}* companies"
                    }
                },
                {
                    "type": "divider"
                }
            ]
            
            # Add company summaries
            for company, company_mentions_list in company_mentions.items():
                positive_count = sum(1 for m in company_mentions_list if m.get('sentiment_score', 0) > 0.1)
                negative_count = sum(1 for m in company_mentions_list if m.get('sentiment_score', 0) < -0.1)
                neutral_count = len(company_mentions_list) - positive_count - negative_count
                
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{company}*: {len(company_mentions_list)} mentions (😊 {positive_count} | 😐 {neutral_count} | 😟 {negative_count})"
                    }
                })
            
            payload = {
                "text": f"📊 Daily Portfolio Summary - {today}",
                "blocks": blocks
            }
            
            response = requests.post(
                self.slack_webhook_url,
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("✅ Daily summary sent successfully")
                return True
            else:
                logger.error(f"❌ Daily summary failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Daily summary error: {e}")
            return False
