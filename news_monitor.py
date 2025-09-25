"""
News monitoring module for ScaleX Ventures portfolio companies
"""

import requests
import feedparser
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from urllib.parse import quote_plus
import time
from textblob import TextBlob

from config import PORTFOLIO_COMPANIES, NEWS_API_KEY, DAYS_LOOKBACK, MAX_ARTICLES_PER_CHECK
from database import MentionDatabase

logger = logging.getLogger(__name__)

class NewsMonitor:
    def __init__(self, db: MentionDatabase):
        self.db = db
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ScaleX Ventures Portfolio Monitor/1.0'
        })
    
    def analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment of text using TextBlob"""
        try:
            blob = TextBlob(text)
            return blob.sentiment.polarity  # Returns -1 to 1
        except Exception as e:
            logger.warning(f"Sentiment analysis failed: {e}")
            return 0.0
    
    def search_newsapi(self, company: Dict) -> List[Dict]:
        """Search for company mentions using NewsAPI"""
        if not NEWS_API_KEY:
            logger.warning("NewsAPI key not configured")
            return []
        
        mentions = []
        for keyword in company['keywords']:
            try:
                # Calculate date range
                from_date = (datetime.now() - timedelta(days=DAYS_LOOKBACK)).strftime('%Y-%m-%d')
                
                url = "https://newsapi.org/v2/everything"
                params = {
                    'q': keyword,
                    'from': from_date,
                    'sortBy': 'publishedAt',
                    'language': 'en',
                    'pageSize': min(MAX_ARTICLES_PER_CHECK, 100),
                    'apiKey': NEWS_API_KEY
                }
                
                response = self.session.get(url, params=params, timeout=30)
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
                
                # Rate limiting
                time.sleep(0.1)
                
            except requests.exceptions.RequestException as e:
                logger.error(f"NewsAPI request failed for {keyword}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error in NewsAPI search for {keyword}: {e}")
        
        return mentions
    
    def search_google_news(self, company: Dict) -> List[Dict]:
        """Search for company mentions using Google News RSS"""
        mentions = []
        
        for keyword in company['keywords']:
            try:
                # Google News RSS URL
                encoded_keyword = quote_plus(keyword)
                url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=en-US&gl=US&ceid=US:en"
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                feed = feedparser.parse(response.content)
                
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
                
                # Rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Google News search failed for {keyword}: {e}")
        
        return mentions
    
    def search_bing_news(self, company: Dict) -> List[Dict]:
        """Search for company mentions using Bing News API (alternative to NewsAPI)"""
        # This would require Bing Search API key
        # Implementation placeholder for additional news source
        return []
    
    def _is_relevant_mention(self, article: Dict, company: Dict) -> bool:
        """Check if an article is a relevant mention of the company"""
        title = article.get('title', '').lower()
        content = article.get('description', '').lower()
        full_text = title + ' ' + content
        
        # Company-specific false positive filtering
        if not self._company_specific_filter(full_text, company):
            return False
        
        # Check if company name appears in title or content
        company_name_lower = company['name'].lower()
        if company_name_lower in title or company_name_lower in content:
            # Additional relevance check for company name mentions
            if self._additional_relevance_check(full_text, company):
                return True
        
        # Check for other relevant keywords
        for keyword in company['keywords']:
            if keyword.lower() in title or keyword.lower() in content:
                # Additional relevance check to reduce false positives
                if self._additional_relevance_check(full_text, company):
                    return True
        
        return False
    
    def _company_specific_filter(self, text: str, company: Dict) -> bool:
        """Company-specific filtering to remove false positives"""
        text_lower = text.lower()
        company_name = company['name'].lower()
        
        # Finch-specific filters
        if company_name == 'finch':
            # Exclude if it's about people with Finch as last name
            person_indicators = [
                'obituary', 'died', 'death', 'funeral', 'memorial',
                'birthday', 'anniversary', 'wedding', 'married',
                'graduated', 'student', 'teacher', 'professor',
                'mayor', 'politician', 'election', 'candidate',
                'chris finch', 'beth finch', 'tess finch', 'spencer finch',
                'christine finch', 'evelyn finch', 'elisabeth finch',
                'real estate agent', 'coach', 'athlete', 'player',
                'timberwolves', 'nba', 'basketball', 'sports'
            ]
            
            for indicator in person_indicators:
                if indicator in text_lower:
                    return False
                    
            # Only include if it has business/tech context
            business_keywords = [
                'app', 'platform', 'software', 'startup', 'company',
                'venue marketing', 'ai-powered', 'technology', 'funding'
            ]
            
            has_business_context = any(keyword in text_lower for keyword in business_keywords)
            if not has_business_context:
                return False
        
        # Cerebra-specific filters (exclude cerebral palsy mentions)
        if company_name == 'cerebra':
            medical_indicators = [
                'cerebral palsy', 'cerebral', 'patient', 'medical',
                'hospital', 'treatment', 'therapy', 'disability',
                'palsy', 'brain injury', 'neurological'
            ]
            
            for indicator in medical_indicators:
                if indicator in text_lower:
                    return False
                    
            # Only include if it has AI/tech context
            ai_keywords = [
                'ai', 'artificial intelligence', 'machine learning',
                'computer vision', 'startup', 'funding', 'technology'
            ]
            
            has_ai_context = any(keyword in text_lower for keyword in ai_keywords)
            if not has_ai_context:
                return False
        
        return True
    
    def _additional_relevance_check(self, text: str, company: Dict) -> bool:
        """Additional checks to ensure the mention is relevant"""
        text_lower = text.lower()
        
        # Exclude common false positives
        false_positives = [
            'recipe', 'cooking', 'food blog', 'restaurant menu',
            'weather forecast', 'entertainment news', 'movie review',
            'zelda', 'gaming', 'video game', 'nintendo'
        ]
        
        for fp in false_positives:
            if fp in text_lower:
                return False
        
        # Check for business/tech context indicators
        business_indicators = [
            'startup', 'company', 'business', 'technology', 'tech',
            'funding', 'investment', 'venture', 'innovation',
            'platform', 'software', 'service', 'solution', 'ai',
            'artificial intelligence', 'machine learning', 'saas'
        ]
        
        for indicator in business_indicators:
            if indicator in text_lower:
                return True
        
        return False  # Default to excluding if no clear business context
    
    def monitor_all_companies(self) -> List[Dict]:
        """Monitor all portfolio companies for news mentions"""
        all_mentions = []
        
        logger.info("Starting news monitoring for all portfolio companies")
        
        for company in PORTFOLIO_COMPANIES:
            logger.info(f"Monitoring news for {company['name']}")
            
            # Search multiple news sources
            newsapi_mentions = self.search_newsapi(company)
            google_mentions = self.search_google_news(company)
            # bing_mentions = self.search_bing_news(company)  # Uncomment if Bing API is available
            
            company_mentions = newsapi_mentions + google_mentions
            
            # Store new mentions in database
            new_mentions = []
            for mention in company_mentions:
                mention_id = self.db.add_mention(mention)
                if mention_id:
                    mention['id'] = mention_id
                    new_mentions.append(mention)
            
            all_mentions.extend(new_mentions)
            logger.info(f"Found {len(new_mentions)} new mentions for {company['name']}")
        
        logger.info(f"Total new mentions found: {len(all_mentions)}")
        return all_mentions
    
    def get_trending_mentions(self, hours: int = 24) -> Dict:
        """Get trending mentions analysis"""
        recent_mentions = self.db.get_recent_mentions(hours)
        
        # Analyze trends
        company_counts = {}
        sentiment_analysis = {}
        source_distribution = {}
        
        for mention in recent_mentions:
            company = mention['company_name']
            
            # Count mentions per company
            company_counts[company] = company_counts.get(company, 0) + 1
            
            # Sentiment analysis
            if company not in sentiment_analysis:
                sentiment_analysis[company] = []
            if mention.get('sentiment_score') is not None:
                sentiment_analysis[company].append(mention['sentiment_score'])
            
            # Source distribution
            source = mention['source']
            source_distribution[source] = source_distribution.get(source, 0) + 1
        
        # Calculate average sentiment
        avg_sentiment = {}
        for company, scores in sentiment_analysis.items():
            if scores:
                avg_sentiment[company] = sum(scores) / len(scores)
        
        return {
            'total_mentions': len(recent_mentions),
            'mentions_by_company': company_counts,
            'average_sentiment': avg_sentiment,
            'source_distribution': source_distribution,
            'time_period_hours': hours
        }
