#!/usr/bin/env python3
"""
ScaleX Ventures Portfolio Monitor - Vercel Version
Web interface for monitoring portfolio company mentions
"""

import os
import sqlite3
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request
from news_monitor_complete import CompleteNewsMonitor
from config_complete import PORTFOLIO_COMPANIES

app = Flask(__name__)

# Initialize database
def init_database():
    """Initialize database with portfolio companies"""
    from database import MentionDatabase
    db = MentionDatabase()
    db.populate_portfolio_companies(PORTFOLIO_COMPANIES)
    return db

# Initialize on startup
db = init_database()

@app.route('/')
def index():
    """Dashboard page"""
    stats = get_portfolio_stats()
    return render_template('index.html', stats=stats)

@app.route('/portfolio')
def portfolio():
    """Portfolio companies page"""
    companies = PORTFOLIO_COMPANIES
    return render_template('portfolio.html', companies=companies)

@app.route('/mentions')
def mentions():
    """Recent mentions page"""
    mentions = get_recent_mentions()
    return render_template('mentions.html', mentions=mentions)

@app.route('/api/stats')
def api_stats():
    """API endpoint for portfolio statistics"""
    stats = get_portfolio_stats()
    return jsonify(stats)

@app.route('/api/run-monitoring', methods=['POST'])
def api_run_monitoring():
    """API endpoint to trigger monitoring manually"""
    try:
        # Run monitoring for a few companies (to avoid timeout)
        monitor = CompleteNewsMonitor()
        
        # Monitor only first 5 companies to avoid Vercel timeout
        companies_to_monitor = PORTFOLIO_COMPANIES[:5]
        mentions = []
        
        for company in companies_to_monitor:
            company_mentions = monitor.search_google_news_rss(company)
            mentions.extend(company_mentions)
        
        # Store mentions in database
        for mention in mentions:
            db.add_mention(mention)
        
        return jsonify({
            'success': True,
            'mentions_found': len(mentions),
            'companies_monitored': len(companies_to_monitor)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def get_portfolio_stats():
    """Get portfolio statistics"""
    try:
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            
            # Total mentions
            cursor.execute("SELECT COUNT(*) FROM mentions")
            total_mentions = cursor.fetchone()[0]
            
            # Recent mentions (last 24 hours)
            yesterday = datetime.now() - timedelta(days=1)
            cursor.execute("SELECT COUNT(*) FROM mentions WHERE created_at >= ?", (yesterday,))
            recent_mentions = cursor.fetchone()[0]
            
            # Mentions by company
            cursor.execute("""
                SELECT company_name, COUNT(*) as count 
                FROM mentions 
                GROUP BY company_name 
                ORDER BY count DESC 
                LIMIT 10
            """)
            top_companies = [{'name': row[0], 'count': row[1]} for row in cursor.fetchall()]
            
            # Mentions by source
            cursor.execute("""
                SELECT source, COUNT(*) as count 
                FROM mentions 
                GROUP BY source 
                ORDER BY count DESC 
                LIMIT 10
            """)
            top_sources = [{'source': row[0], 'count': row[1]} for row in cursor.fetchall()]
            
            return {
                'total_mentions': total_mentions,
                'recent_mentions': recent_mentions,
                'companies_monitored': len(PORTFOLIO_COMPANIES),
                'top_companies': top_companies,
                'top_sources': top_sources
            }
            
    except Exception as e:
        print(f"Error getting stats: {e}")
        return {
            'total_mentions': 0,
            'recent_mentions': 0,
            'companies_monitored': len(PORTFOLIO_COMPANIES),
            'top_companies': [],
            'top_sources': []
        }

def get_recent_mentions(limit=100):
    """Get recent mentions"""
    try:
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT company_name, title, content, url, source, 
                       published_date, sentiment_score, created_at
                FROM mentions 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
            
            mentions = []
            for row in cursor.fetchall():
                mentions.append({
                    'company_name': row[0],
                    'title': row[1],
                    'content': row[2],
                    'url': row[3],
                    'source': row[4],
                    'published_date': row[5],
                    'sentiment_score': row[6],
                    'created_at': row[7]
                })
            
            return mentions
            
    except Exception as e:
        print(f"Error getting mentions: {e}")
        return []

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
