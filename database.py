"""
Database models and operations for the portfolio monitoring system
"""

import sqlite3
import hashlib
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class MentionDatabase:
    def __init__(self, db_path: str = "portfolio_mentions.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create mentions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mentions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_name TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT,
                    url TEXT UNIQUE NOT NULL,
                    source TEXT NOT NULL,
                    published_date TEXT,
                    sentiment_score REAL,
                    hash TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create alerts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mention_id INTEGER,
                    alert_type TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    sent_at TIMESTAMP,
                    error_message TEXT,
                    FOREIGN KEY (mention_id) REFERENCES mentions (id)
                )
            """)
            
            # Create portfolio_companies table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS portfolio_companies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    fund TEXT NOT NULL,
                    website TEXT,
                    description TEXT,
                    keywords TEXT
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_company_name ON mentions (company_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_source ON mentions (source)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_published_date ON mentions (published_date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_hash ON mentions (hash)")
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def populate_portfolio_companies(self, companies_data):
        """Populate the portfolio_companies table with company data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for company in companies_data:
                try:
                    cursor.execute("""
                        INSERT OR REPLACE INTO portfolio_companies 
                        (name, fund, website, description, keywords)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        company['name'],
                        company['fund'],
                        company['website'],
                        company['description'],
                        ','.join(company['keywords'])
                    ))
                except Exception as e:
                    logger.warning(f"Failed to insert company {company['name']}: {e}")
            
            conn.commit()
            logger.info(f"Populated portfolio_companies table with {len(companies_data)} companies")
    
    def generate_hash(self, title: str, url: str, company: str) -> str:
        """Generate a unique hash for a mention to avoid duplicates"""
        content = f"{title}|{url}|{company}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def mention_exists(self, hash_value: str) -> bool:
        """Check if a mention already exists in the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM mentions WHERE hash = ?", (hash_value,))
            return cursor.fetchone() is not None
    
    def add_mention(self, mention_data: Dict) -> Optional[int]:
        """Add a new mention to the database"""
        hash_value = self.generate_hash(
            mention_data['title'], 
            mention_data['url'], 
            mention_data['company_name']
        )
        
        if self.mention_exists(hash_value):
            logger.debug(f"Mention already exists: {mention_data['title']}")
            return None
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO mentions (
                        company_name, title, content, url, source, 
                        published_date, sentiment_score, hash
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    mention_data['company_name'],
                    mention_data['title'],
                    mention_data.get('content', ''),
                    mention_data['url'],
                    mention_data['source'],
                    mention_data.get('published_date', ''),
                    mention_data.get('sentiment_score'),
                    hash_value
                ))
                mention_id = cursor.lastrowid
                conn.commit()
                logger.info(f"Added new mention for {mention_data['company_name']}: {mention_data['title']}")
                return mention_id
            except sqlite3.IntegrityError as e:
                logger.warning(f"Failed to add mention due to integrity constraint: {e}")
                return None
    
    def get_recent_mentions(self, hours: int = 24) -> List[Dict]:
        """Get mentions from the last N hours"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM mentions 
                WHERE created_at >= datetime('now', '-{} hours')
                ORDER BY created_at DESC
            """.format(hours))
            
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_mentions_by_company(self, company_name: str, limit: int = 50) -> List[Dict]:
        """Get mentions for a specific company"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM mentions 
                WHERE company_name = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (company_name, limit))
            
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def add_alert_record(self, mention_id: int, alert_type: str, status: str = 'pending'):
        """Record an alert attempt"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO alerts (mention_id, alert_type, status)
                VALUES (?, ?, ?)
            """, (mention_id, alert_type, status))
            conn.commit()
    
    def update_alert_status(self, alert_id: int, status: str, error_message: str = None):
        """Update the status of an alert"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE alerts 
                SET status = ?, sent_at = CURRENT_TIMESTAMP, error_message = ?
                WHERE id = ?
            """, (status, error_message, alert_id))
            conn.commit()
    
    def clean_false_positives(self) -> int:
        """Remove false positive mentions from the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Define false positive patterns
            finch_false_positives = [
                "beth finch", "chris finch", "tess finch", "spencer finch",
                "christine finch", "evelyn finch", "elisabeth finch",
                "obituary", "mayor", "timberwolves", "nba", "basketball",
                "real estate agent", "grey's anatomy", "coach", "player"
            ]
            
            cerebra_false_positives = [
                "cerebral palsy", "cerebral", "brain injury", "palsy",
                "patient", "medical", "hospital", "therapy", "disability",
                "neurological", "treatment"
            ]
            
            deleted_count = 0
            
            # Remove Finch false positives
            for pattern in finch_false_positives:
                cursor.execute("""
                    DELETE FROM mentions 
                    WHERE company_name = 'Finch' 
                    AND (LOWER(title) LIKE ? OR LOWER(content) LIKE ?)
                """, (f'%{pattern}%', f'%{pattern}%'))
                deleted_count += cursor.rowcount
            
            # Remove Cerebra false positives
            for pattern in cerebra_false_positives:
                cursor.execute("""
                    DELETE FROM mentions 
                    WHERE company_name = 'Cerebra' 
                    AND (LOWER(title) LIKE ? OR LOWER(content) LIKE ?)
                """, (f'%{pattern}%', f'%{pattern}%'))
                deleted_count += cursor.rowcount
            
            conn.commit()
            logger.info(f"Removed {deleted_count} false positive mentions from database")
            return deleted_count
    
    def get_statistics(self) -> Dict:
        """Get monitoring statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total mentions
            cursor.execute("SELECT COUNT(*) FROM mentions")
            total_mentions = cursor.fetchone()[0]
            
            # Mentions by company
            cursor.execute("""
                SELECT company_name, COUNT(*) as count 
                FROM mentions 
                GROUP BY company_name 
                ORDER BY count DESC
            """)
            mentions_by_company = dict(cursor.fetchall())
            
            # Recent mentions (last 24 hours)
            cursor.execute("""
                SELECT COUNT(*) FROM mentions 
                WHERE created_at >= datetime('now', '-24 hours')
            """)
            recent_mentions = cursor.fetchone()[0]
            
            # Mentions by source
            cursor.execute("""
                SELECT source, COUNT(*) as count 
                FROM mentions 
                GROUP BY source 
                ORDER BY count DESC
            """)
            mentions_by_source = dict(cursor.fetchall())
            
            return {
                'total_mentions': total_mentions,
                'recent_mentions_24h': recent_mentions,
                'mentions_by_company': mentions_by_company,
                'mentions_by_source': mentions_by_source
            }

