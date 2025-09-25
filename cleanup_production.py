#!/usr/bin/env python3
"""
Production database cleanup script
Run this to clean false positives from Railway database
"""

import os
import sys
import sqlite3
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_false_positives():
    """Remove false positive mentions from the database"""
    db_path = "portfolio_mentions.db"
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Get count before cleanup
            cursor.execute("SELECT COUNT(*) FROM mentions")
            total_before = cursor.fetchone()[0]
            logger.info(f"Total mentions before cleanup: {total_before}")
            
            # Define false positive patterns
            finch_false_positives = [
                "beth finch", "chris finch", "tess finch", "spencer finch",
                "christine finch", "evelyn finch", "elisabeth finch",
                "obituary", "mayor", "timberwolves", "nba", "basketball",
                "real estate agent", "grey's anatomy", "coach", "player",
                "olden polynice", "sports illustrate"
            ]
            
            cerebra_false_positives = [
                "cerebral palsy", "brain injury", "palsy",
                "patient", "medical", "hospital", "therapy", "disability",
                "neurological", "treatment", "delivery robot", "mobility scooter"
            ]
            
            deleted_count = 0
            
            # Remove Finch false positives
            for pattern in finch_false_positives:
                cursor.execute("""
                    DELETE FROM mentions 
                    WHERE company_name = 'Finch' 
                    AND (LOWER(title) LIKE ? OR LOWER(content) LIKE ?)
                """, (f'%{pattern}%', f'%{pattern}%'))
                deleted = cursor.rowcount
                if deleted > 0:
                    logger.info(f"Removed {deleted} Finch mentions containing '{pattern}'")
                deleted_count += deleted
            
            # Remove Cerebra false positives  
            for pattern in cerebra_false_positives:
                cursor.execute("""
                    DELETE FROM mentions 
                    WHERE company_name = 'Cerebra' 
                    AND (LOWER(title) LIKE ? OR LOWER(content) LIKE ?)
                """, (f'%{pattern}%', f'%{pattern}%'))
                deleted = cursor.rowcount
                if deleted > 0:
                    logger.info(f"Removed {deleted} Cerebra mentions containing '{pattern}'")
                deleted_count += deleted
            
            # Get count after cleanup
            cursor.execute("SELECT COUNT(*) FROM mentions")
            total_after = cursor.fetchone()[0]
            
            conn.commit()
            
            logger.info(f"✅ Cleanup completed!")
            logger.info(f"📊 Before: {total_before} mentions")
            logger.info(f"📊 After: {total_after} mentions") 
            logger.info(f"🗑️ Removed: {deleted_count} false positives")
            
            return deleted_count
            
    except Exception as e:
        logger.error(f"❌ Error during cleanup: {e}")
        return 0

if __name__ == "__main__":
    deleted = clean_false_positives()
    print(f"Done! Removed {deleted} false positive mentions.")
