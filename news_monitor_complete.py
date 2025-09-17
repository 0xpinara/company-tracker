"""
Complete News monitoring module for ALL ScaleX Ventures portfolio companies
"""

import feedparser
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from urllib.parse import quote_plus
import time
from textblob import TextBlob

from config_complete import PORTFOLIO_COMPANIES, NEWS_API_KEY, DAYS_LOOKBACK, MAX_ARTICLES_PER_CHECK
from database import MentionDatabase

logger = logging.getLogger(__name__)

class CompleteNewsMonitor:
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
        
        # Use only the first 2 keywords to avoid rate limiting
        for keyword in company['keywords'][:2]:
            try:
                # Google News RSS URL - FREE!
                encoded_keyword = quote_plus(keyword)
                url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=en-US&gl=US&ceid=US:en"
                
                logger.info(f"Searching Google News for: {keyword}")
                feed = feedparser.parse(url)
                
                for entry in feed.entries[:MAX_ARTICLES_PER_CHECK]:
                    if self._is_relevant_mention({'title': entry.title, 'description': entry.get('summary', '')}, company):
                        # Parse the actual publication date
                        published_date = ''
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            from datetime import datetime
                            published_date = datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d %H:%M:%S')
                        elif entry.get('published'):
                            published_date = entry.get('published')
                        
                        mention = {
                            'company_name': company['name'],
                            'title': entry.title,
                            'content': entry.get('summary', ''),
                            'url': entry.link,
                            'source': f"Google News - {entry.get('source', {}).get('href', 'Unknown')}",
                            'published_date': published_date,
                            'sentiment_score': self.analyze_sentiment(
                                f"{entry.title} {entry.get('summary', '')}"
                            )
                        }
                        mentions.append(mention)
                        logger.info(f"Found mention: {entry.title[:50]}...")
                
                # Small delay to be respectful
                time.sleep(0.3)
                
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
            
            # Use only the first keyword to avoid rate limiting
            for keyword in company['keywords'][:1]:
                url = "https://newsapi.org/v2/everything"
                params = {
                    'q': keyword,
                    'sortBy': 'publishedAt',
                    'language': 'en',
                    'pageSize': 3,  # Small number for demo
                    'apiKey': NEWS_API_KEY
                }
                
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get('status') == 'ok':
                    for article in data.get('articles', []):
                        if self._is_relevant_mention(article, company):
                            # Parse the actual publication date from NewsAPI
                            published_date = article.get('publishedAt', '')
                            if published_date:
                                try:
                                    from datetime import datetime
                                    # NewsAPI uses ISO format, convert to readable format
                                    dt = datetime.fromisoformat(published_date.replace('Z', '+00:00'))
                                    published_date = dt.strftime('%Y-%m-%d %H:%M:%S')
                                except:
                                    published_date = published_date[:10]  # Just the date part
                            
                            mention = {
                                'company_name': company['name'],
                                'title': article.get('title', ''),
                                'content': article.get('description', ''),
                                'url': article.get('url', ''),
                                'source': f"NewsAPI - {article.get('source', {}).get('name', 'Unknown')}",
                                'published_date': published_date,
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
        full_text = f"{title} {content}"
        
        # Special handling for problematic companies that have generic names (check first!)
        if company['name'] == 'Coqui':
            # Only match if it's clearly about the AI company, not frogs
            tech_indicators = ['ai', 'artificial intelligence', 'text-to-speech', 'tts', 'voice', 'speech', 'generative', 'coqui.ai']
            if any(indicator in full_text for indicator in tech_indicators):
                return True
            return False
        
        if company['name'] == 'The Blue Dot':
            # Only match if it's clearly about the company, not Android blue dots
            # Check for negative indicators (Android, text messages, etc.)
            negative_indicators = ['android', 'text message', 'text messages', 'message', 'notification', 'unread']
            if any(indicator in full_text for indicator in negative_indicators):
                return False
            
            # Check for positive indicators (company-related terms)
            company_indicators = ['thebluedot', 'thebluedot.co', 'bluedot', 'charging', 'electric car', 'expense management', 'fleet', 'ev charging']
            if any(indicator in full_text for indicator in company_indicators):
                return True
            return False
        
        # Check if company name appears as a complete word in title or content
        company_name_lower = company['name'].lower()
        
        # Use word boundaries to ensure exact company name match
        import re
        company_pattern = r'\b' + re.escape(company_name_lower) + r'\b'
        if re.search(company_pattern, title) or re.search(company_pattern, content):
            return True
        
        # Check for very specific company identifiers (domain names, exact product names)
        specific_identifiers = []
        for kw in company['keywords']:
            kw_lower = kw.lower()
            # Only include very specific identifiers that are clearly company-related
            if ('.com' in kw_lower or 
                kw_lower in ['vectroid', 'kuzudb', 'finchnow', 'buluttan', 'opnova', 'hyperbee', 
                           'ubicloud', 'icosacomputing', 'kondukto', 'peaka', 
                           'flowla', 'figopara', 'altogic', 'atlas-robotics', 'upstash', 
                           'locomation', 'invidyo', 'hipporello', 'cerebra', 'genomize', 'genialis', 
                           'quantive', 'thundra', 'cybeats', 'resmo', 'datarow']):
                specific_identifiers.append(kw_lower)
        
        for identifier in specific_identifiers:
            if identifier in full_text:
                return True
        
        return False
    
    def monitor_all_companies(self) -> List[Dict]:
        """Monitor all portfolio companies for news mentions"""
        all_mentions = []
        
        logger.info(f"🔍 Starting COMPLETE news monitoring for {len(PORTFOLIO_COMPANIES)} companies")
        logger.info("=" * 70)
        
        for i, company in enumerate(PORTFOLIO_COMPANIES, 1):
            logger.info(f"📰 [{i:2d}/{len(PORTFOLIO_COMPANIES)}] Monitoring {company['name']} ({company['fund']})")
            
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
            
            # Rate limiting between companies
            time.sleep(0.5)
        
        logger.info(f"🎉 Total new mentions found: {len(all_mentions)}")
        return all_mentions
