#!/usr/bin/env python3
"""
Clear the database to test improved relevance checking
"""

import os
import sqlite3

def clear_database():
    """Clear all mentions from the database"""
    if os.path.exists('portfolio_mentions.db'):
        conn = sqlite3.connect('portfolio_mentions.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM mentions")
        conn.commit()
        conn.close()
        print("✅ Database cleared successfully")
    else:
        print("❌ Database not found")

if __name__ == "__main__":
    clear_database()
