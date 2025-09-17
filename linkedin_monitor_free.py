"""
Free LinkedIn monitoring using Google site search
No API keys needed - uses Google search with site:linkedin.com
"""

import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time
from bs4 import BeautifulSoup
from textblob import TextBlob
from urllib.parse import quote_plus

from config_minimal import PORTFOLIO_COMPANIES
from database import MentionDatabase

logger = logging.getLogger(__name__)

class FreeLinkedInMonitor:
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
    
    def search_linkedin_google(self, company: Dict) -> List[Dict]:
        """
        Search for LinkedIn mentions using Google site search
        Format: site:linkedin.com "company name"
        """
        mentions = []
        
        for keyword in company['keywords'][:2]:  # Limit to 2 keywords to avoid rate limiting
            try:
                # Google search for LinkedIn posts
                query = f'site:linkedin.com "{keyword}"'
                encoded_query = quote_plus(query)
                
                # Use Google search URL
                url = f"https://www.google.com/search?q={encoded_query}&num=10&tbm=nws"
                
                logger.info(f"Searching LinkedIn via Google for: {keyword}")
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Parse Google search results
                search_results = soup.find_all('div', class_='g')
                
                for result in search_results[:5]:  # Limit to 5 results per keyword
                    try:
                        # Extract title
                        title_elem = result.find('h3')
                        if not title_elem:
                            continue
                        title = title_elem.get_text()
                        
                        # Extract link
                        link_elem = result.find('a')
                        if not link_elem or 'linkedin.com' not in link_elem.get('href', ''):
                            continue
                        url = link_elem.get('href')
                        
                        # Extract snippet
                        snippet_elem = result.find('span', class_='st')
                        snippet = snippet_elem.get_text() if snippet_elem else ''
                        
                        # Extract source
                        source_elem = result.find('cite')
                        source = source_elem.get_text() if source_elem else 'LinkedIn'
                        
                        # Check if it's relevant
                        if self._is_relevant_mention({'title': title, 'content': snippet}, company):
                            mention = {
                                'company_name': company['name'],
                                'title': title,
                                'content': snippet,
                                'url': url,
                                'source': f"LinkedIn - {source}",
                                'published_date': datetime.now().isoformat(),
                                'sentiment_score': self.analyze_sentiment(f"{title} {snippet}")
                            }
                            mentions.append(mention)
                            logger.info(f"Found LinkedIn mention: {title[:50]}...")
                    
                    except Exception as e:
                        logger.warning(f"Error parsing search result: {e}")
                        continue
                
                # Rate limiting to avoid being blocked
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"LinkedIn Google search failed for {keyword}: {e}")
        
        return mentions
    
    def search_linkedin_company_pages(self, company: Dict) -> List[Dict]:
        """
        Try to find LinkedIn company page RSS feeds
        Format: https://www.linkedin.com/company/COMPANY_NAME/rss/
        """
        mentions = []
        
        # Try different company name variations
        company_variations = [
            company['name'].lower().replace(' ', '-'),
            company['name'].lower().replace(' ', ''),
            company['name'].lower()
        ]
        
        for company_slug in company_variations:
            try:
                rss_url = f"https://www.linkedin.com/company/{company_slug}/rss/"
                
                logger.info(f"Trying LinkedIn RSS for: {company_slug}")
                
                response = self.session.get(rss_url, timeout=10)
                
                if response.status_code == 200:
                    import feedparser
                    feed = feedparser.parse(response.content)
                    
                    if feed.entries:
                        logger.info(f"Found LinkedIn RSS feed for {company['name']}")
                        
                        for entry in feed.entries[:3]:  # Limit to 3 entries
                            mention = {
                                'company_name': company['name'],
                                'title': entry.title,
                                'content': entry.get('summary', ''),
                                'url': entry.link,
                                'source': 'LinkedIn Company Page',
                                'published_date': entry.get('published', ''),
                                'sentiment_score': self.analyze_sentiment(
                                    f"{entry.title} {entry.get('summary', '')}"
                                )
                            }
                            mentions.append(mention)
                            logger.info(f"Found LinkedIn company post: {entry.title[:50]}...")
                        break  # Found working RSS, no need to try other variations
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.debug(f"LinkedIn RSS not available for {company_slug}: {e}")
                continue
        
        return mentions
    
    def _is_relevant_mention(self, article: Dict, company: Dict) -> bool:
        """Check if an article is a relevant mention of the company"""
        title = article.get('title', '').lower()
        content = article.get('content', '').lower()
        
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
        """Monitor all portfolio companies for LinkedIn mentions"""
        all_mentions = []
        
        logger.info("🔍 Starting FREE LinkedIn monitoring (Google site search)")
        logger.info("=" * 60)
        
        for company in PORTFOLIO_COMPANIES:
            logger.info(f"💼 Monitoring LinkedIn for {company['name']}")
            
            # Use Google site search
            google_mentions = self.search_linkedin_google(company)
            
            # Try company page RSS feeds
            rss_mentions = self.search_linkedin_company_pages(company)
            
            company_mentions = google_mentions + rss_mentions
            
            # Store new mentions in database
            new_mentions = []
            for mention in company_mentions:
                mention_id = self.db.add_mention(mention)
                if mention_id:
                    mention['id'] = mention_id
                    new_mentions.append(mention)
            
            all_mentions.extend(new_mentions)
            logger.info(f"✅ Found {len(new_mentions)} new LinkedIn mentions for {company['name']}")
            
            # Rate limiting between companies
            time.sleep(2)
        
        logger.info(f"🎉 Total new LinkedIn mentions found: {len(all_mentions)}")
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
            'source_breakdown': {}
        }
        
        # Analyze by company
        for mention in recent_mentions:
            company = mention['company_name']
            source = mention['source']
            
            insights['mentions_by_company'][company] = \
                insights['mentions_by_company'].get(company, 0) + 1
            
            insights['source_breakdown'][source] = \
                insights['source_breakdown'].get(source, 0) + 1
        
        return insights
