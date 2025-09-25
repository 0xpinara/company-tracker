#!/usr/bin/env python3
"""
ScaleX Ventures Portfolio Monitoring System - Web UI
Beautiful web interface for portfolio monitoring
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for
import sqlite3
import json
from datetime import datetime, timedelta
import os
from config_complete import PORTFOLIO_COMPANIES, TOTAL_COMPANIES, FUND_I_COMPANIES, ACQUIRED_COMPANIES, ANGEL_COMPANIES
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass
try:
    from alerts_slack import SlackAlertSystem
except Exception:
    SlackAlertSystem = None

app = Flask(__name__)

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('portfolio_mentions.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize database with portfolio companies"""
    from database import MentionDatabase
    db = MentionDatabase()
    db.populate_portfolio_companies(PORTFOLIO_COMPANIES)
    return db

def get_portfolio_stats():
    """Get comprehensive portfolio statistics"""
    conn = get_db_connection()
    
    # Total mentions
    total_mentions = conn.execute('SELECT COUNT(*) as count FROM mentions').fetchone()['count']
    
    # Recent mentions (24h)
    recent_mentions = conn.execute(
        'SELECT COUNT(*) as count FROM mentions WHERE created_at >= datetime("now", "-1 day")'
    ).fetchone()['count']
    
    # Mentions by company
    company_mentions = conn.execute(
        'SELECT company_name, COUNT(*) as count FROM mentions GROUP BY company_name ORDER BY count DESC'
    ).fetchall()
    
    # Mentions by source
    source_mentions = conn.execute(
        'SELECT source, COUNT(*) as count FROM mentions GROUP BY source ORDER BY count DESC'
    ).fetchall()
    
    # Mentions by fund
    fund_mentions = conn.execute(
        'SELECT m.company_name, m.source, c.fund FROM mentions m '
        'JOIN (SELECT DISTINCT name, fund FROM portfolio_companies) c ON m.company_name = c.name '
        'GROUP BY c.fund'
    ).fetchall()
    
    # Recent mentions details
    recent_details = conn.execute(
        'SELECT * FROM mentions WHERE created_at >= datetime("now", "-1 day") ORDER BY created_at DESC LIMIT 20'
    ).fetchall()
    
    conn.close()
    
    return {
        'total_mentions': total_mentions,
        'recent_mentions': recent_mentions,
        'company_mentions': [dict(row) for row in company_mentions],
        'source_mentions': [dict(row) for row in source_mentions],
        'fund_mentions': [dict(row) for row in fund_mentions],
        'recent_details': [dict(row) for row in recent_details]
    }

@app.route('/')
def index():
    """Main dashboard"""
    stats = get_portfolio_stats()
    return render_template('index.html', 
                         stats=stats,
                         portfolio_companies=PORTFOLIO_COMPANIES,
                         total_companies=TOTAL_COMPANIES,
                         fund_i_companies=FUND_I_COMPANIES,
                         acquired_companies=ACQUIRED_COMPANIES,
                         angel_companies=ANGEL_COMPANIES)

@app.route('/api/stats')
def api_stats():
    """API endpoint for stats"""
    return jsonify(get_portfolio_stats())

@app.route('/api/companies')
def api_companies():
    """API endpoint for companies"""
    return jsonify(PORTFOLIO_COMPANIES)

@app.route('/api/mentions')
def api_mentions():
    """API endpoint for recent mentions"""
    conn = get_db_connection()
    mentions = conn.execute(
        'SELECT * FROM mentions ORDER BY published_date DESC, created_at DESC LIMIT 50'
    ).fetchall()
    conn.close()
    return jsonify([dict(row) for row in mentions])

@app.route('/api/run-monitoring')
def api_run_monitoring():
    """API endpoint to run monitoring"""
    try:
        # Import and run the monitoring system
        from main_complete import run_complete_demo
        result = run_complete_demo()
        return jsonify({'success': True, 'message': 'Monitoring completed successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/clean-false-positives')
def api_clean_false_positives():
    """API endpoint to clean false positive mentions"""
    try:
        from database import MentionDatabase
        db = MentionDatabase()
        deleted_count = db.clean_false_positives()
        
        return jsonify({
            'success': True,
            'message': f'Removed {deleted_count} false positive mentions',
            'deleted_count': deleted_count
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/slack-test', methods=['POST'])
def api_slack_test():
    """Send a simple Slack test message to verify webhook works"""
    try:
        webhook = os.getenv('SLACK_WEBHOOK_URL', '').strip()
        if not webhook:
            return jsonify({'success': False, 'message': 'SLACK_WEBHOOK_URL not set'}), 400
        if not SlackAlertSystem:
            return jsonify({'success': False, 'message': 'Slack alerts module not available'}), 500

        from database import MentionDatabase
        db = MentionDatabase()
        slack = SlackAlertSystem(db, webhook)
        ok = slack.send_test_alert()
        if ok:
            return jsonify({'success': True, 'message': 'Test alert sent to Slack'})
        return jsonify({'success': False, 'message': 'Failed to send Slack test alert'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/portfolio')
def portfolio():
    """Portfolio companies page"""
    return render_template('portfolio.html', 
                         portfolio_companies=PORTFOLIO_COMPANIES,
                         total_companies=TOTAL_COMPANIES)

@app.route('/mentions')
def mentions():
    """Recent mentions page"""
    conn = get_db_connection()
    mentions = conn.execute(
        'SELECT * FROM mentions ORDER BY published_date DESC, created_at DESC LIMIT 100'
    ).fetchall()
    conn.close()
    return render_template('mentions.html', mentions=[dict(row) for row in mentions])

if __name__ == '__main__':
    # Initialize database on startup
    init_database()
    app.run(debug=True, host='0.0.0.0', port=5000)
