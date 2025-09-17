#!/usr/bin/env python3
"""
Main entry point for Railway deployment
"""

import os
from app import app, init_database

if __name__ == '__main__':
    # Initialize database on startup
    init_database()
    
    # Get port from environment (Railway provides this)
    port = int(os.environ.get('PORT', 5000))
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=port, debug=False)