"""
Configuration file for ScaleX Ventures Portfolio Monitoring System
"""

import os
from typing import List, Dict

# ScaleX Ventures Portfolio Companies
PORTFOLIO_COMPANIES = [
    {
        "name": "Finch",
        "keywords": ["Finch app", "Finch platform", "venue marketing platform", "AI venue marketing", "Finch startup"],
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

# API Configuration
NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
GOOGLE_NEWS_API_KEY = os.getenv('GOOGLE_NEWS_API_KEY', '')
LINKEDIN_ACCESS_TOKEN = os.getenv('LINKEDIN_ACCESS_TOKEN', '')

# Alert Configuration
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL', '')
EMAIL_SMTP_SERVER = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
EMAIL_SMTP_PORT = int(os.getenv('EMAIL_SMTP_PORT', '587'))
EMAIL_USERNAME = os.getenv('EMAIL_USERNAME', '')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
ALERT_EMAIL_RECIPIENTS = os.getenv('ALERT_EMAIL_RECIPIENTS', '').split(',')

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///portfolio_mentions.db')

# Monitoring Configuration
CHECK_INTERVAL_MINUTES = int(os.getenv('CHECK_INTERVAL_MINUTES', '30'))
MAX_ARTICLES_PER_CHECK = int(os.getenv('MAX_ARTICLES_PER_CHECK', '50'))
DAYS_LOOKBACK = int(os.getenv('DAYS_LOOKBACK', '1'))

# Sentiment Analysis
ENABLE_SENTIMENT_ANALYSIS = os.getenv('ENABLE_SENTIMENT_ANALYSIS', 'true').lower() == 'true'

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'portfolio_monitor.log')

