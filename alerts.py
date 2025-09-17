"""
Alert system for ScaleX Ventures portfolio monitoring
Supports email, Slack, and webhook notifications
"""

import smtplib
import requests
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional
from datetime import datetime
import json

from config import (
    SLACK_WEBHOOK_URL, EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT,
    EMAIL_USERNAME, EMAIL_PASSWORD, ALERT_EMAIL_RECIPIENTS
)
from database import MentionDatabase

logger = logging.getLogger(__name__)

class AlertSystem:
    def __init__(self, db: MentionDatabase):
        self.db = db
    
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
    
    def send_email_alert(self, mentions: List[Dict]) -> bool:
        """Send email alert for new mentions"""
        if not EMAIL_USERNAME or not EMAIL_PASSWORD or not ALERT_EMAIL_RECIPIENTS:
            logger.warning("Email configuration not complete")
            return False
        
        try:
            # Create email content
            subject = f"ScaleX Ventures Portfolio Alert - {len(mentions)} New Mentions"
            
            # HTML email body
            html_body = self._create_email_html(mentions)
            
            # Text email body
            text_body = self._create_email_text(mentions)
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = EMAIL_USERNAME
            msg['To'] = ', '.join(ALERT_EMAIL_RECIPIENTS)
            
            # Add text and HTML parts
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT) as server:
                server.starttls()
                server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
                server.sendmail(EMAIL_USERNAME, ALERT_EMAIL_RECIPIENTS, msg.as_string())
            
            logger.info(f"Email alert sent successfully to {len(ALERT_EMAIL_RECIPIENTS)} recipients")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            return False
    
    def _create_email_html(self, mentions: List[Dict]) -> str:
        """Create HTML email body"""
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f8ff; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
                .mention {{ border: 1px solid #ddd; padding: 15px; margin-bottom: 15px; border-radius: 5px; }}
                .company {{ font-weight: bold; color: #2c5aa0; font-size: 16px; }}
                .title {{ font-size: 14px; margin: 5px 0; }}
                .meta {{ font-size: 12px; color: #666; }}
                .sentiment {{ font-size: 18px; }}
                .positive {{ background-color: #d4edda; }}
                .negative {{ background-color: #f8d7da; }}
                .neutral {{ background-color: #e2e3e5; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>🚀 ScaleX Ventures Portfolio Alert</h2>
                <p>Found {len(mentions)} new mentions of portfolio companies</p>
                <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        """
        
        # Group mentions by company
        mentions_by_company = {}
        for mention in mentions:
            company = mention['company_name']
            if company not in mentions_by_company:
                mentions_by_company[company] = []
            mentions_by_company[company].append(self.format_mention_for_alert(mention))
        
        for company, company_mentions in mentions_by_company.items():
            html += f"<h3>📊 {company} ({len(company_mentions)} mentions)</h3>"
            
            for mention in company_mentions:
                sentiment_class = self._get_sentiment_class(mention['sentiment_score'])
                html += f"""
                <div class="mention {sentiment_class}">
                    <div class="company">{mention['company']} <span class="sentiment">{mention['sentiment_emoji']}</span></div>
                    <div class="title"><strong>{mention['title']}</strong></div>
                    <div>{mention['content']}</div>
                    <div class="meta">
                        <strong>Source:</strong> {mention['source']} | 
                        <strong>Published:</strong> {mention['published_date']} | 
                        <strong>Sentiment:</strong> {mention['sentiment_score']:.2f} |
                        <a href="{mention['url']}" target="_blank">Read More</a>
                    </div>
                </div>
                """
        
        html += """
            <div style="margin-top: 30px; padding: 15px; background-color: #f8f9fa; border-radius: 5px;">
                <p><strong>💡 Next Steps:</strong></p>
                <ul>
                    <li>Review mentions for potential PR opportunities</li>
                    <li>Monitor sentiment trends for portfolio companies</li>
                    <li>Consider reaching out to journalists for additional coverage</li>
                </ul>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _create_email_text(self, mentions: List[Dict]) -> str:
        """Create plain text email body"""
        text = f"""
ScaleX Ventures Portfolio Alert
===============================

Found {len(mentions)} new mentions of portfolio companies
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
        
        # Group mentions by company
        mentions_by_company = {}
        for mention in mentions:
            company = mention['company_name']
            if company not in mentions_by_company:
                mentions_by_company[company] = []
            mentions_by_company[company].append(self.format_mention_for_alert(mention))
        
        for company, company_mentions in mentions_by_company.items():
            text += f"\n{company} ({len(company_mentions)} mentions)\n"
            text += "=" * (len(company) + 20) + "\n\n"
            
            for mention in company_mentions:
                text += f"Title: {mention['title']}\n"
                text += f"Content: {mention['content']}\n"
                text += f"Source: {mention['source']}\n"
                text += f"Published: {mention['published_date']}\n"
                text += f"Sentiment: {mention['sentiment_score']:.2f} {mention['sentiment_emoji']}\n"
                text += f"URL: {mention['url']}\n"
                text += "-" * 50 + "\n\n"
        
        return text
    
    def _get_sentiment_class(self, score: float) -> str:
        """Get CSS class based on sentiment score"""
        if score > 0.3:
            return "positive"
        elif score < -0.3:
            return "negative"
        else:
            return "neutral"
    
    def send_slack_alert(self, mentions: List[Dict]) -> bool:
        """Send Slack alert for new mentions"""
        if not SLACK_WEBHOOK_URL:
            logger.warning("Slack webhook URL not configured")
            return False
        
        try:
            # Group mentions by company
            mentions_by_company = {}
            for mention in mentions:
                company = mention['company_name']
                if company not in mentions_by_company:
                    mentions_by_company[company] = []
                mentions_by_company[company].append(self.format_mention_for_alert(mention))
            
            # Create Slack message
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"🚀 ScaleX Portfolio Alert - {len(mentions)} New Mentions"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "plain_text",
                            "text": f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        }
                    ]
                }
            ]
            
            for company, company_mentions in mentions_by_company.items():
                # Company header
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*📊 {company}* ({len(company_mentions)} mentions)"
                    }
                })
                
                # Add top mentions (limit to 3 per company to avoid message length issues)
                for mention in company_mentions[:3]:
                    blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*{mention['title']}* {mention['sentiment_emoji']}\n"
                                   f"{mention['content']}\n"
                                   f"_Source: {mention['source']} | Sentiment: {mention['sentiment_score']:.2f}_"
                        },
                        "accessory": {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Read More"
                            },
                            "url": mention['url']
                        }
                    })
                
                if len(company_mentions) > 3:
                    blocks.append({
                        "type": "context",
                        "elements": [
                            {
                                "type": "plain_text",
                                "text": f"... and {len(company_mentions) - 3} more mentions"
                            }
                        ]
                    })
                
                blocks.append({"type": "divider"})
            
            # Send to Slack
            payload = {
                "blocks": blocks,
                "username": "ScaleX Portfolio Monitor",
                "icon_emoji": ":rocket:"
            }
            
            response = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=30)
            response.raise_for_status()
            
            logger.info("Slack alert sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
            return False
    
    def send_webhook_alert(self, mentions: List[Dict], webhook_url: str) -> bool:
        """Send generic webhook alert"""
        try:
            payload = {
                "timestamp": datetime.now().isoformat(),
                "alert_type": "portfolio_mentions",
                "total_mentions": len(mentions),
                "mentions": [self.format_mention_for_alert(m) for m in mentions]
            }
            
            response = requests.post(webhook_url, json=payload, timeout=30)
            response.raise_for_status()
            
            logger.info(f"Webhook alert sent successfully to {webhook_url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")
            return False
    
    def send_alerts(self, mentions: List[Dict]) -> Dict[str, bool]:
        """Send all configured alerts"""
        if not mentions:
            logger.info("No mentions to alert about")
            return {}
        
        results = {}
        
        # Send email alert
        if EMAIL_USERNAME and ALERT_EMAIL_RECIPIENTS:
            results['email'] = self.send_email_alert(mentions)
            
            # Record alert attempts in database
            for mention in mentions:
                if mention.get('id'):
                    self.db.add_alert_record(
                        mention['id'], 
                        'email', 
                        'sent' if results['email'] else 'failed'
                    )
        
        # Send Slack alert
        if SLACK_WEBHOOK_URL:
            results['slack'] = self.send_slack_alert(mentions)
            
            # Record alert attempts in database
            for mention in mentions:
                if mention.get('id'):
                    self.db.add_alert_record(
                        mention['id'], 
                        'slack', 
                        'sent' if results['slack'] else 'failed'
                    )
        
        logger.info(f"Alert results: {results}")
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
