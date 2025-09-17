#!/bin/bash

# ScaleX Ventures Portfolio Monitoring System Setup Script

echo "🚀 Setting up ScaleX Ventures Portfolio Monitoring System"
echo "=========================================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7+ and try again."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install Python dependencies"
    exit 1
fi

# Download NLTK data for sentiment analysis
echo "📚 Downloading NLTK data for sentiment analysis..."
python3 -c "import nltk; nltk.download('punkt'); nltk.download('brown')"

# Create logs directory
echo "📁 Creating logs directory..."
mkdir -p logs

# Copy environment template
if [ ! -f .env ]; then
    echo "📝 Creating environment configuration template..."
    cp env_example.txt .env
    echo "⚠️  Please edit .env file with your API keys and configuration"
else
    echo "✅ .env file already exists"
fi

# Test the system
echo "🧪 Testing system configuration..."
python3 main.py companies --skip-config-check

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Setup completed successfully!"
    echo ""
    echo "🔧 Next steps:"
    echo "1. Edit .env file with your API keys:"
    echo "   - Get NewsAPI key from: https://newsapi.org/"
    echo "   - Configure email settings for Gmail"
    echo "   - Set up Slack webhook URL"
    echo ""
    echo "2. Test the system:"
    echo "   python3 main.py test-alerts"
    echo ""
    echo "3. Run a single monitoring cycle:"
    echo "   python3 main.py run-once"
    echo ""
    echo "4. Start continuous monitoring:"
    echo "   python3 main.py start"
    echo ""
    echo "📖 See README.md for detailed documentation"
else
    echo "❌ Setup test failed. Please check the error messages above."
    exit 1
fi
