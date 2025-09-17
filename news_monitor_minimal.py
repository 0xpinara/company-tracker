"""
Minimal News monitoring module - works with just Google News RSS (no API keys needed)
"""

import feedparser
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from urllib.parse import quote_plus
import time
from textblob import TextBlob

from config_minimal import PORTFOLIO_COMPANIES, NEWS_API_KEY, DAYS_LOOKBACK, MAX_ARTICLES_PER_CHECK
from database import MentionDatabase

logger = logging.getLogger(__name__)

class MinimalNewsMonitor:
    def __init__(self, db: MentionDatabase):
        self.db = db
        self.session = None  # We'll use feedparser directly
    
    def analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment of text using TextBlob"""
        try:
            blob = TextBlob(text)
            return blob.sentiment.polarity  # Returns -1 to 1
        except Exception as e:
            logger.warning(f"Sentiment analysis failed: {e}")
            return 0.0
    
    def search_google_news_rss(self, company: Dict) -> List[Dict]:
        """Search for company mentions using Google News RSS (FREE - no API key needed)"""
        mentions = []
        
        for keyword in company['keywords'][:2]:  # Limit to 2 keywords for demo
            try:
                # Google News RSS URL - FREE!
                encoded_keyword = quote_plus(keyword)
                url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=en-US&gl=US&ceid=US:en"
                
                logger.info(f"Searching Google News for: {keyword}")
                feed = feedparser.parse(url)
                
                for entry in feed.entries[:MAX_ARTICLES_PER_CHECK]:
                    if self._is_relevant_mention({'title': entry.title, 'description': entry.get('summary', '')}, company):
                        mention = {
                            'company_name': company['name'],
                            'title': entry.title,
                            'content': entry.get('summary', ''),
                            'url': entry.link,
                            'source': f"Google News - {entry.get('source', {}).get('href', 'Unknown')}",
                            'published_date': entry.get('published', ''),
                            'sentiment_score': self.analyze_sentiment(
                                f"{entry.title} {entry.get('summary', '')}"
                            )
                        }
                        mentions.append(mention)
                        logger.info(f"Found mention: {entry.title[:50]}...")
                
                # Small delay to be respectful
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Google News search failed for {keyword}: {e}")
        
        return mentions
    
    def search_newsapi_if_available(self, company: Dict) -> List[Dict]:
        """Search NewsAPI if key is available (optional)"""
        if not NEWS_API_KEY:
            return []
        
        mentions = []
        try:
            import requests
            
            for keyword in company['keywords'][:1]:  # Just 1 keyword for demo
                url = "https://newsapi.org/v2/everything"
                params = {
                    'q': keyword,
                    'sortBy': 'publishedAt',
                    'language': 'en',
                    'pageSize': 5,  # Small number for demo
                    'apiKey': NEWS_API_KEY
                }
                
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get('status') == 'ok':
                    for article in data.get('articles', []):
                        if self._is_relevant_mention(article, company):
                            mention = {
                                'company_name': company['name'],
                                'title': article.get('title', ''),
                                'content': article.get('description', ''),
                                'url': article.get('url', ''),
                                'source': f"NewsAPI - {article.get('source', {}).get('name', 'Unknown')}",
                                'published_date': article.get('publishedAt', ''),
                                'sentiment_score': self.analyze_sentiment(
                                    f"{article.get('title', '')} {article.get('description', '')}"
                                )
                            }
                            mentions.append(mention)
                            logger.info(f"Found NewsAPI mention: {article.get('title', '')[:50]}...")
                
        except Exception as e:
            logger.warning(f"NewsAPI search failed (this is OK if no key): {e}")
        
        return mentions
    
    def _is_relevant_mention(self, article: Dict, company: Dict) -> bool:
        """Check if an article is a relevant mention of the company"""
        title = article.get('title', '').lower()
        content = article.get('description', '').lower()
        
        # Check if company name appears in title or content
        company_name_lower = company['name'].lower()
        if company_name_lower in title or company_name_lower in content:
            return True
        
        # Check for other relevant keywords
        for keyword in company['keywords']:
            if keyword.lower() in title or keyword.lower() in content:
                return True
        
        return False
    
    def monitor_all_companies(self) -> List[Dict]:
        """Monitor all portfolio companies for news mentions"""
        all_mentions = []
        
        logger.info("🔍 Starting MINIMAL news monitoring (Google News RSS - FREE)")
        logger.info("=" * 60)
        
        for company in PORTFOLIO_COMPANIES:
            logger.info(f"📰 Monitoring news for {company['name']}")
            
            # Try NewsAPI first if available
            newsapi_mentions = self.search_newsapi_if_available(company)
            
            # Always use Google News RSS (free)
            google_mentions = self.search_google_news_rss(company)
            
            company_mentions = newsapi_mentions + google_mentions
            
            # Store new mentions in database
            new_mentions = []
            for mention in company_mentions:
                mention_id = self.db.add_mention(mention)
                if mention_id:
                    mention['id'] = mention_id
                    new_mentions.append(mention)
            
            all_mentions.extend(new_mentions)
            logger.info(f"✅ Found {len(new_mentions)} new mentions for {company['name']}")
        
        logger.info(f"🎉 Total new mentions found: {len(all_mentions)}")
        return all_mentions
