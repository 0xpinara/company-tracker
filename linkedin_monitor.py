"""
LinkedIn monitoring module for ScaleX Ventures portfolio companies
Note: LinkedIn's API has restrictions on public post access.
This module provides multiple approaches including web scraping and third-party services.
"""

import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time
import json
from bs4 import BeautifulSoup
from textblob import TextBlob

from config import PORTFOLIO_COMPANIES, LINKEDIN_ACCESS_TOKEN
from database import MentionDatabase

logger = logging.getLogger(__name__)

class LinkedInMonitor:
    def __init__(self, db: MentionDatabase):
        self.db = db
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment of text using TextBlob"""
        try:
            blob = TextBlob(text)
            return blob.sentiment.polarity
        except Exception as e:
            logger.warning(f"Sentiment analysis failed: {e}")
            return 0.0
    
    def search_linkedin_api(self, company: Dict) -> List[Dict]:
        """
        Search LinkedIn using official API (Limited access)
        Note: LinkedIn's API severely restricts access to public posts
        """
        if not LINKEDIN_ACCESS_TOKEN:
            logger.warning("LinkedIn access token not configured")
            return []
        
        mentions = []
        headers = {
            'Authorization': f'Bearer {LINKEDIN_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        try:
            # LinkedIn's API endpoints for searching posts are very limited
            # This is a placeholder for when/if LinkedIn provides better access
            url = "https://api.linkedin.com/v2/shares"
            params = {
                'q': 'owners',
                'owners': 'urn:li:organization:YOUR_ORG_ID'  # Would need specific org IDs
            }
            
            response = self.session.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                # Process LinkedIn API response
                # Note: Actual implementation would depend on available API endpoints
                pass
            
        except Exception as e:
            logger.error(f"LinkedIn API search failed: {e}")
        
        return mentions
    
    def search_linkedin_google(self, company: Dict) -> List[Dict]:
        """
        Search for LinkedIn mentions using Google site search
        Format: site:linkedin.com "company name"
        """
        mentions = []
        
        for keyword in company['keywords'][:3]:  # Limit to avoid rate limiting
            try:
                # Google search for LinkedIn posts
                query = f'site:linkedin.com "{keyword}"'
                url = "https://www.google.com/search"
                params = {
                    'q': query,
                    'num': 10,
                    'tbm': 'nws'  # News search
                }
                
                response = self.session.get(url, params=params, timeout=30)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Parse Google search results
                    for result in soup.find_all('div', class_='g')[:5]:  # Limit results
                        title_elem = result.find('h3')
                        link_elem = result.find('a')
                        snippet_elem = result.find('span', class_='st')
                        
                        if title_elem and link_elem and 'linkedin.com' in link_elem.get('href', ''):
                            title = title_elem.get_text()
                            url = link_elem.get('href')
                            snippet = snippet_elem.get_text() if snippet_elem else ''
                            
                            mention = {
                                'company_name': company['name'],
                                'title': title,
                                'content': snippet,
                                'url': url,
                                'source': 'LinkedIn (via Google)',
                                'published_date': datetime.now().isoformat(),
                                'sentiment_score': self.analyze_sentiment(f"{title} {snippet}")
                            }
                            mentions.append(mention)
                
                # Rate limiting to avoid being blocked
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"LinkedIn Google search failed for {keyword}: {e}")
        
        return mentions
    
    def search_linkedin_rss_feeds(self, company: Dict) -> List[Dict]:
        """
        Monitor LinkedIn company RSS feeds if available
        Note: LinkedIn has limited RSS feed availability
        """
        mentions = []
        
        # Some LinkedIn company pages have RSS feeds
        # Format: https://www.linkedin.com/company/COMPANY_NAME/rss/
        company_name_slug = company['name'].lower().replace(' ', '-')
        rss_url = f"https://www.linkedin.com/company/{company_name_slug}/rss/"
        
        try:
            import feedparser
            
            response = self.session.get(rss_url, timeout=30)
            if response.status_code == 200:
                feed = feedparser.parse(response.content)
                
                for entry in feed.entries[:10]:  # Limit entries
                    mention = {
                        'company_name': company['name'],
                        'title': entry.title,
                        'content': entry.get('summary', ''),
                        'url': entry.link,
                        'source': 'LinkedIn RSS',
                        'published_date': entry.get('published', ''),
                        'sentiment_score': self.analyze_sentiment(
                            f"{entry.title} {entry.get('summary', '')}"
                        )
                    }
                    mentions.append(mention)
            
        except Exception as e:
            logger.error(f"LinkedIn RSS search failed for {company['name']}: {e}")
        
        return mentions
    
    def search_third_party_apis(self, company: Dict) -> List[Dict]:
        """
        Search using third-party social media monitoring APIs
        Examples: Mention.com, Brand24, Hootsuite Insights
        """
        mentions = []
        
        # Example integration with a third-party service
        # This would require API keys for services like:
        # - Mention.com API
        # - Brand24 API
        # - Hootsuite Insights API
        # - Brandwatch API
        
        try:
            # Placeholder for third-party API integration
            # Each service would have its own implementation
            
            # Example structure for Mention.com API:
            """
            mention_api_key = os.getenv('MENTION_API_KEY')
            if mention_api_key:
                url = "https://web.mention.com/api/accounts/ACCOUNT_ID/alerts/ALERT_ID/mentions"
                headers = {'Authorization': f'Bearer {mention_api_key}'}
                response = requests.get(url, headers=headers)
                # Process response...
            """
            
            pass
            
        except Exception as e:
            logger.error(f"Third-party API search failed: {e}")
        
        return mentions
    
    def monitor_all_companies(self) -> List[Dict]:
        """Monitor all portfolio companies for LinkedIn mentions"""
        all_mentions = []
        
        logger.info("Starting LinkedIn monitoring for all portfolio companies")
        
        for company in PORTFOLIO_COMPANIES:
            logger.info(f"Monitoring LinkedIn for {company['name']}")
            
            # Use multiple search methods
            google_mentions = self.search_linkedin_google(company)
            rss_mentions = self.search_linkedin_rss_feeds(company)
            # api_mentions = self.search_linkedin_api(company)  # Limited availability
            # third_party_mentions = self.search_third_party_apis(company)  # Requires additional APIs
            
            company_mentions = google_mentions + rss_mentions
            
            # Store new mentions in database
            new_mentions = []
            for mention in company_mentions:
                mention_id = self.db.add_mention(mention)
                if mention_id:
                    mention['id'] = mention_id
                    new_mentions.append(mention)
            
            all_mentions.extend(new_mentions)
            logger.info(f"Found {len(new_mentions)} new LinkedIn mentions for {company['name']}")
            
            # Rate limiting between companies
            time.sleep(1)
        
        logger.info(f"Total new LinkedIn mentions found: {len(all_mentions)}")
        return all_mentions
    
    def get_linkedin_insights(self, hours: int = 24) -> Dict:
        """Get LinkedIn-specific insights"""
        recent_mentions = [
            m for m in self.db.get_recent_mentions(hours) 
            if 'linkedin' in m['source'].lower()
        ]
        
        insights = {
            'total_linkedin_mentions': len(recent_mentions),
            'mentions_by_company': {},
            'average_sentiment': {},
            'engagement_indicators': []
        }
        
        # Analyze by company
        for mention in recent_mentions:
            company = mention['company_name']
            insights['mentions_by_company'][company] = \
                insights['mentions_by_company'].get(company, 0) + 1
        
        return insights
    
    def suggest_monitoring_improvements(self) -> List[str]:
        """Suggest improvements for LinkedIn monitoring"""
        suggestions = [
            "Consider subscribing to third-party social media monitoring services like:",
            "- Mention.com for real-time social media monitoring",
            "- Brand24 for comprehensive social listening",
            "- Hootsuite Insights for LinkedIn analytics",
            "- Brandwatch for enterprise social intelligence",
            "",
            "Alternative approaches:",
            "- Set up Google Alerts for 'site:linkedin.com \"Company Name\"'",
            "- Monitor company LinkedIn pages directly for posts and comments",
            "- Use LinkedIn Sales Navigator for advanced company monitoring",
            "- Implement webhook notifications from LinkedIn company pages",
            "",
            "Technical improvements:",
            "- Add proxy rotation for web scraping",
            "- Implement CAPTCHA solving for automated searches",
            "- Use headless browser automation (Selenium/Playwright)",
            "- Set up monitoring for LinkedIn company hashtags"
        ]
        
        return suggestions
