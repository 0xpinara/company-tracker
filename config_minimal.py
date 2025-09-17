"""
Minimal Configuration for ScaleX Ventures Portfolio Monitoring System
Simplified for demo purposes - works with minimal API keys
"""

import os
from typing import List, Dict

# ScaleX Ventures Portfolio Companies
PORTFOLIO_COMPANIES = [
    {
        "name": "Finch",
        "keywords": ["Finch", "venue marketing", "AI-powered platform marketing"],
        "description": "AI-powered platform to enhance venue marketing"
    },
    {
        "name": "Ubicloud",
        "keywords": ["Ubicloud", "open-source AWS", "cloud services", "bare metal cloud"],
        "description": "Open-source alternative to AWS"
    },
    {
        "name": "Opnova",
        "keywords": ["Opnova", "intelligent automation", "IT automation", "security compliance"],
        "description": "Intelligent automation for IT, security, and compliance"
    },
    {
        "name": "Vectroid",
        "keywords": ["Vectroid", "vector database", "AI-driven applications"],
        "description": "Next-generation vector database for AI applications"
    },
    {
        "name": "Kuzudb",
        "keywords": ["Kuzudb", "graph database", "embedded database"],
        "description": "Embedded, scalable, and fast graph database"
    },
    {
        "name": "Buluttan",
        "keywords": ["Buluttan", "hyperlocal weather", "AI weather intelligence"],
        "description": "AI-based hyperlocal weather intelligence"
    }
]

# MINIMAL API Configuration - Only ONE API key needed!
NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
# If no NewsAPI key, we'll use free Google News RSS feeds

# DEMO Alert Configuration - Uses simple print statements instead of email/Slack
DEMO_MODE = os.getenv('DEMO_MODE', 'true').lower() == 'true'

# Optional: If you have a NewsAPI key, set it here
# NEWS_API_KEY = 'your_newsapi_key_here'  # Get free from https://newsapi.org/

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///portfolio_mentions.db')

# Monitoring Configuration
CHECK_INTERVAL_MINUTES = int(os.getenv('CHECK_INTERVAL_MINUTES', '5'))  # Faster for demo
MAX_ARTICLES_PER_CHECK = int(os.getenv('MAX_ARTICLES_PER_CHECK', '10'))  # Fewer for demo
DAYS_LOOKBACK = int(os.getenv('DAYS_LOOKBACK', '1'))

# Sentiment Analysis
ENABLE_SENTIMENT_ANALYSIS = os.getenv('ENABLE_SENTIMENT_ANALYSIS', 'true').lower() == 'true'

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'portfolio_monitor.log')

# Demo settings
DEMO_ALERT_EMAIL = os.getenv('DEMO_ALERT_EMAIL', 'demo@scalexventures.com')
DEMO_ALERT_SLACK = os.getenv('DEMO_ALERT_SLACK', 'https://hooks.slack.com/demo')
