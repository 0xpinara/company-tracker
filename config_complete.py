"""
Complete Configuration for ScaleX Ventures Portfolio Monitoring System
Includes ALL portfolio companies from their website
"""

import os
from typing import List, Dict

# COMPLETE ScaleX Ventures Portfolio Companies
PORTFOLIO_COMPANIES = [
    # FUND I Companies
    {
        "name": "Vectroid",
        "keywords": ["Vectroid", "vector database", "AI-driven applications", "serverless vector database"],
        "description": "Next-generation vector database built for AI-driven applications",
        "website": "vectroid.com",
        "fund": "FUND I"
    },
    {
        "name": "Kuzudb",
        "keywords": ["Kuzudb", "graph database", "embedded database", "blazing fast graph database"],
        "description": "Embedded, scalable, blazing fast graph database",
        "website": "kuzudb.com",
        "fund": "FUND I"
    },
    {
        "name": "Finch",
        "keywords": ["Finch", "finchnow", "hospitality marketing", "loyalty platform", "payments platform"],
        "description": "All-in-one marketing, loyalty, and payments platform for hospitality",
        "website": "finchnow.com",
        "fund": "FUND I"
    },
    {
        "name": "Buluttan",
        "keywords": ["Buluttan", "buluttan.com", "hyperlocal weather intelligence"],
        "description": "AI-based hyperlocal weather intelligence",
        "website": "buluttan.com",
        "fund": "FUND I"
    },
    {
        "name": "Opnova",
        "keywords": ["Opnova", "opnova.ai", "ITSM", "hyperautomation", "AI automation platform"],
        "description": "AI-based hyperautomation platform for ITSM",
        "website": "opnova.ai",
        "fund": "FUND I"
    },
    {
        "name": "Hyperbee",
        "keywords": ["Hyperbee", "hyperbee.ai", "AI solution", "cloud-only LLMs", "local AI"],
        "description": "A small footprint AI solution that enables cloud-only LLMs to run locally",
        "website": "hyperbee.ai",
        "fund": "FUND I"
    },
    {
        "name": "Ubicloud",
        "keywords": ["Ubicloud", "ubicloud.com", "open cloud", "portable cloud", "free cloud"],
        "description": "An open, free, and portable cloud",
        "website": "ubicloud.com",
        "fund": "FUND I"
    },
    {
        "name": "Icosa Computing",
        "keywords": ["Icosa Computing", "icosacomputing.com", "Icosa quantum"],
        "description": "Quantum computing enhanced optimizers for AI models",
        "website": "icosacomputing.com",
        "fund": "FUND I"
    },
    {
        "name": "Kondukto",
        "keywords": ["Kondukto", "kondukto.io", "application security", "security testing", "security orchestration"],
        "description": "Application security testing orchestration platform for security teams",
        "website": "kondukto.io",
        "fund": "FUND I"
    },
    {
        "name": "Peaka",
        "keywords": ["Peaka", "peaka.com", "no-code platform", "application development", "low-code"],
        "description": "No-code application development platform",
        "website": "peaka.com",
        "fund": "FUND I"
    },
    {
        "name": "The Blue Dot",
        "keywords": ["The Blue Dot", "thebluedot.co", "electric car charging", "EV charging management", "fleet charging", "expense management"],
        "description": "Charging and expense management for electric car owners and fleets",
        "website": "thebluedot.co",
        "fund": "FUND I"
    },
    {
        "name": "Flowla",
        "keywords": ["Flowla", "flowla.com", "sales enablement", "remote selling", "sales teams"],
        "description": "Sales enablement tool that simplifies the remote selling process for sales teams",
        "website": "flowla.com",
        "fund": "FUND I"
    },
    {
        "name": "Coqui",
        "keywords": ["Coqui AI", "coqui.ai", "text-to-speech AI", "generative AI voice", "emotive TTS"],
        "description": "Emotive text-to-speech through generative AI",
        "website": "coqui.ai",
        "fund": "FUND I"
    },
    {
        "name": "Figopara",
        "keywords": ["Figopara", "figopara.com", "supplier financing", "SME financing", "fintech"],
        "description": "Supplier financing for SMEs",
        "website": "figopara.com",
        "fund": "FUND I"
    },
    {
        "name": "Altogic",
        "keywords": ["Altogic", "altogic.com", "no-code backend", "backend development", "low-code backend"],
        "description": "No-code backend development platform",
        "website": "altogic.com",
        "fund": "FUND I"
    },
    {
        "name": "Atlas Robotics",
        "keywords": ["Atlas Robotics", "atlas-robotics.com"],
        "description": "Next-gen AI-driven autonomous robot developer",
        "website": "atlas-robotics.com",
        "fund": "FUND I"
    },
    {
        "name": "Upstash",
        "keywords": ["Upstash", "upstash.com", "serverless database", "Redis API", "serverless Redis"],
        "description": "A serverless database with Redis API",
        "website": "upstash.com",
        "fund": "FUND I"
    },
    {
        "name": "Locomation",
        "keywords": ["Locomation", "locomation.ai", "autonomous trucking", "AI trucking", "logistics AI"],
        "description": "Leading AI-driven autonomous trucking tech platform",
        "website": "locomation.ai",
        "fund": "FUND I"
    },
    {
        "name": "Invidyo",
        "keywords": ["Invidyo", "invidyo.com", "smart baby monitor", "baby monitoring", "subscription service"],
        "description": "All-in-one smart baby monitor and subscription service",
        "website": "invidyo.com",
        "fund": "FUND I"
    },
    {
        "name": "Hipporello",
        "keywords": ["Hipporello", "hipporello.com", "Trello automation", "business automation", "no-code Trello"],
        "description": "No-code business automation platform for Trello",
        "website": "hipporello.com",
        "fund": "FUND I"
    },
    
    # ACQUIRED Companies
    {
        "name": "Cerebra",
        "keywords": ["Cerebra", "cerebra.ai", "decision intelligence", "retail AI", "no-code decision"],
        "description": "No-code decision intelligence solution for retailers",
        "website": "cerebra.ai",
        "fund": "ACQUIRED"
    },
    {
        "name": "Resmo",
        "keywords": ["Resmo", "resmo.com", "cyber asset management", "governance solution", "cybersecurity"],
        "description": "Cyber asset management and governance solution, providing visibility and security",
        "website": "resmo.com",
        "fund": "ACQUIRED"
    },
    {
        "name": "Cybeats",
        "keywords": ["Cybeats", "cybeats.com", "IoT security", "cybersecurity", "IoT devices"],
        "description": "Cybersecurity solution for IoT devices",
        "website": "cybeats.com",
        "fund": "ACQUIRED"
    },
    {
        "name": "Thundra",
        "keywords": ["Thundra", "thundra.io", "observability platform", "serverless monitoring", "container monitoring"],
        "description": "Observability platform for serverless, container, and virtual machine workloads",
        "website": "thundra.io",
        "fund": "ACQUIRED"
    },
    {
        "name": "Datarow",
        "keywords": ["Datarow", "datarow.com", "Amazon Redshift", "data analysis", "visual analysis"],
        "description": "Amazon Redshift client with visual analysis and collaboration features",
        "website": "datarow.com",
        "fund": "ACQUIRED"
    },
    
    # ANGEL Investments
    {
        "name": "Quantive",
        "keywords": ["Quantive", "quantive.com", "OKR platform", "employee success", "performance management"],
        "description": "OKR and employee success management platform",
        "website": "quantive.com",
        "fund": "ANGEL"
    },
    {
        "name": "Genomize",
        "keywords": ["Genomize", "genomize.com", "next-generation sequencing", "variant analysis", "genomics"],
        "description": "Next-generation sequencing based variant analysis platform",
        "website": "genomize.com",
        "fund": "ANGEL"
    },
    {
        "name": "Genialis",
        "keywords": ["Genialis", "genialis.com", "data science", "drug discovery", "biotech"],
        "description": "Data science based drug discovery company",
        "website": "genialis.com",
        "fund": "ANGEL"
    },
    {
        "name": "Picus Security",
        "keywords": ["Picus Security", "picussecurity.com", "breach simulation", "attack simulation", "security testing"],
        "description": "Breach and attack simulation platform",
        "website": "picussecurity.com",
        "fund": "ANGEL"
    }
]

# API Configuration
NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
GOOGLE_NEWS_API_KEY = os.getenv('GOOGLE_NEWS_API_KEY', '')
LINKEDIN_ACCESS_TOKEN = os.getenv('LINKEDIN_ACCESS_TOKEN', '')

# Demo Alert Configuration
DEMO_MODE = os.getenv('DEMO_MODE', 'true').lower() == 'true'
DEMO_ALERT_EMAIL = os.getenv('DEMO_ALERT_EMAIL', 'demo@scalexventures.com')
DEMO_ALERT_SLACK = os.getenv('DEMO_ALERT_SLACK', 'https://hooks.slack.com/demo')

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///portfolio_mentions.db')

# Monitoring Configuration
CHECK_INTERVAL_MINUTES = int(os.getenv('CHECK_INTERVAL_MINUTES', '5'))
MAX_ARTICLES_PER_CHECK = int(os.getenv('MAX_ARTICLES_PER_CHECK', '10'))
DAYS_LOOKBACK = int(os.getenv('DAYS_LOOKBACK', '1'))

# Sentiment Analysis
ENABLE_SENTIMENT_ANALYSIS = os.getenv('ENABLE_SENTIMENT_ANALYSIS', 'true').lower() == 'true'

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'portfolio_monitor.log')

# Portfolio Statistics
TOTAL_COMPANIES = len(PORTFOLIO_COMPANIES)
FUND_I_COMPANIES = len([c for c in PORTFOLIO_COMPANIES if c['fund'] == 'FUND I'])
ACQUIRED_COMPANIES = len([c for c in PORTFOLIO_COMPANIES if c['fund'] == 'ACQUIRED'])
ANGEL_COMPANIES = len([c for c in PORTFOLIO_COMPANIES if c['fund'] == 'ANGEL'])
