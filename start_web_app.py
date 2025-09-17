#!/usr/bin/env python3
"""
ScaleX Ventures Portfolio Monitor - Web App Launcher
Simple script to start the web application
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import requests
        import feedparser
        from bs4 import BeautifulSoup
        from textblob import TextBlob
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Installing dependencies...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False

def check_database():
    """Check if database exists, create if not"""
    if not os.path.exists('portfolio_mentions.db'):
        print("📊 Creating database...")
        try:
            from database import MentionDatabase
            db = MentionDatabase()
            print("✅ Database created successfully")
        except Exception as e:
            print(f"❌ Failed to create database: {e}")
            return False
    else:
        print("✅ Database exists")
    return True

def start_web_app():
    """Start the Flask web application"""
    print("🚀 Starting ScaleX Ventures Portfolio Monitor Web App...")
    print("=" * 60)
    print("🌐 Web Interface: http://localhost:5000")
    print("📊 Dashboard: http://localhost:5000")
    print("🏢 Portfolio: http://localhost:5000/portfolio")
    print("📰 Mentions: http://localhost:5000/mentions")
    print("=" * 60)
    print("Press Ctrl+C to stop the server")
    print()
    
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Web app stopped")
    except Exception as e:
        print(f"❌ Error starting web app: {e}")

def main():
    """Main function"""
    print("🚀 ScaleX Ventures Portfolio Monitor - Web App Launcher")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ Please run this script from the project directory")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check database
    if not check_database():
        sys.exit(1)
    
    # Start web app
    start_web_app()

if __name__ == "__main__":
    main()
