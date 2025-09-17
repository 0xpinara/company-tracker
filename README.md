# ScaleX Ventures Portfolio Monitoring System

A comprehensive real-time monitoring system that tracks mentions of ScaleX Ventures portfolio companies across news sources and LinkedIn.

## 🏢 Portfolio Companies Monitored

- **Finch** - AI-powered platform to enhance venue marketing
- **Ubicloud** - Open-source alternative to AWS
- **Opnova** - Intelligent automation for IT, security, and compliance
- **Vectroid** - Next-generation vector database for AI applications
- **Kuzudb** - Embedded, scalable, and fast graph database
- **Buluttan** - AI-based hyperlocal weather intelligence

## ✨ Features

- **Real-time Monitoring**: Continuous monitoring of news sources and LinkedIn
- **Multiple Data Sources**: NewsAPI, Google News, LinkedIn (via multiple methods)
- **Intelligent Filtering**: Reduces false positives with relevance checking
- **Sentiment Analysis**: Analyzes sentiment of mentions using TextBlob
- **Duplicate Prevention**: Prevents duplicate alerts using content hashing
- **Multi-channel Alerts**: Email and Slack notifications
- **Comprehensive Database**: SQLite database for storing and tracking mentions
- **Scheduling System**: Automated periodic monitoring with configurable intervals
- **Rich Reporting**: HTML emails and formatted Slack messages

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or create the project directory
cd scalex

# Install dependencies
pip install -r requirements.txt

# Download TextBlob corpora (required for sentiment analysis)
python -c "import nltk; nltk.download('punkt'); nltk.download('brown')"
```

### 2. Configuration

Create a `.env` file in the project root:

```env
# News API Configuration
NEWS_API_KEY=your_newsapi_key_from_newsapi.org

# Email Alert Configuration
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
ALERT_EMAIL_RECIPIENTS=team@scalexventures.com,alerts@scalexventures.com

# Slack Alert Configuration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK

# Optional: LinkedIn Configuration
LINKEDIN_ACCESS_TOKEN=your_linkedin_token

# Monitoring Configuration
CHECK_INTERVAL_MINUTES=30
MAX_ARTICLES_PER_CHECK=50
DAYS_LOOKBACK=1
ENABLE_SENTIMENT_ANALYSIS=true

# Logging
LOG_LEVEL=INFO
LOG_FILE=portfolio_monitor.log
```

### 3. Usage

```bash
# Show portfolio companies
python main.py companies

# Test the system with a single run
python main.py run-once

# Test alert system
python main.py test-alerts

# Start continuous monitoring
python main.py start

# Check status and statistics
python main.py status
```

## 📊 System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   News Sources  │    │  LinkedIn Sources│    │   Database      │
│                 │    │                  │    │                 │
│ • NewsAPI       │    │ • Google Search  │    │ • Mentions      │
│ • Google News   │    │ • RSS Feeds      │    │ • Alerts        │
│ • Bing News     │    │ • Third-party APIs│   │ • Statistics    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────────┐
                    │  Monitoring Engine  │
                    │                     │
                    │ • Content Filtering │
                    │ • Sentiment Analysis│
                    │ • Duplicate Detection│
                    └─────────────────────┘
                                 │
                    ┌─────────────────────┐
                    │   Alert System      │
                    │                     │
                    │ • Email Alerts      │
                    │ • Slack Alerts      │
                    │ • Webhook Support   │
                    └─────────────────────┘
```

## 📁 File Structure

```
scalex/
├── main.py              # Main entry point
├── config.py            # Configuration management
├── database.py          # Database models and operations
├── news_monitor.py      # News monitoring implementation
├── linkedin_monitor.py  # LinkedIn monitoring implementation
├── alerts.py            # Alert system (email, Slack)
├── scheduler.py         # Task scheduling system
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── .env                # Configuration file (create this)
└── logs/               # Log files directory
    └── portfolio_monitor.log
```

## 🔧 Configuration Options

### API Keys Required

1. **NewsAPI Key** (Primary news source)
   - Get from: https://newsapi.org/
   - Free tier: 1,000 requests/day
   - Set as: `NEWS_API_KEY`

2. **LinkedIn Access** (Optional, limited)
   - LinkedIn API has severe restrictions
   - Alternative methods implemented (Google search, RSS)

3. **Email Configuration**
   - Gmail App Password recommended
   - Configure SMTP settings in `.env`

4. **Slack Webhook** (Optional)
   - Create incoming webhook in Slack
   - Set as: `SLACK_WEBHOOK_URL`

### Monitoring Settings

- `CHECK_INTERVAL_MINUTES`: How often to check for new mentions (default: 30)
- `MAX_ARTICLES_PER_CHECK`: Maximum articles to process per check (default: 50)
- `DAYS_LOOKBACK`: How many days back to search (default: 1)
- `ENABLE_SENTIMENT_ANALYSIS`: Enable/disable sentiment analysis (default: true)

## 📧 Alert Examples

### Email Alert
- **Subject**: "ScaleX Ventures Portfolio Alert - X New Mentions"
- **Format**: Rich HTML with company grouping, sentiment indicators, and direct links
- **Content**: Title, snippet, source, sentiment score, and read-more links

### Slack Alert
- **Format**: Structured blocks with company headers
- **Features**: Sentiment emojis, action buttons, source attribution
- **Limits**: Top 3 mentions per company to avoid message length issues

## 🔍 Monitoring Sources

### News Sources
1. **NewsAPI** - Primary news aggregator
2. **Google News RSS** - Free alternative source
3. **Bing News API** - Additional coverage (requires API key)

### LinkedIn Sources
1. **Google Site Search** - Search LinkedIn via Google
2. **Company RSS Feeds** - Direct LinkedIn company feeds (limited availability)
3. **Third-party APIs** - Integration ready for services like Mention.com, Brand24

## 📈 Sentiment Analysis

The system uses TextBlob for sentiment analysis:
- **Score Range**: -1.0 (very negative) to +1.0 (very positive)
- **Emojis**: 😊 Positive (>0.3), 😐 Neutral (-0.3 to 0.3), 😟 Negative (<-0.3)
- **Application**: Applied to title + content of each mention

## 🗄️ Database Schema

### Mentions Table
- `id`: Primary key
- `company_name`: Portfolio company name
- `title`: Article/post title
- `content`: Article snippet or content
- `url`: Direct link to article
- `source`: Source of the mention
- `published_date`: When the article was published
- `sentiment_score`: Calculated sentiment score
- `hash`: Unique hash to prevent duplicates
- `created_at`: When the mention was discovered

### Alerts Table
- `id`: Primary key
- `mention_id`: Foreign key to mentions
- `alert_type`: Type of alert (email, slack, webhook)
- `status`: Alert status (pending, sent, failed)
- `sent_at`: When alert was sent
- `error_message`: Error details if failed

## 🚨 Troubleshooting

### Common Issues

1. **No mentions found**
   - Check API keys are configured correctly
   - Verify internet connection
   - Check rate limiting hasn't been exceeded

2. **Alerts not sending**
   - Verify email/Slack configuration
   - Check credentials and permissions
   - Review logs for error messages

3. **Too many false positives**
   - Adjust keyword filtering in `config.py`
   - Modify relevance checking in monitoring modules
   - Add more false-positive filters

4. **LinkedIn monitoring limited**
   - LinkedIn heavily restricts API access
   - Consider third-party monitoring services
   - Use Google Alerts as supplement: `site:linkedin.com "Company Name"`

### Logs

- Main log file: `logs/portfolio_monitor.log`
- Log level configurable via `LOG_LEVEL` in `.env`
- Includes timestamps, modules, and detailed error information

## 🔄 Scheduling

Default schedule:
- **Monitoring**: Every 30 minutes
- **Daily Summary**: 9:00 AM
- **Weekly Cleanup**: Sunday 2:00 AM

Modify in `scheduler.py` or via environment variables.

## 🚀 Deployment Options

### Local Development
```bash
python main.py start
```

### Production Deployment
```bash
# Using systemd (Linux)
sudo systemctl enable portfolio-monitor
sudo systemctl start portfolio-monitor

# Using Docker
docker build -t scalex-monitor .
docker run -d --env-file .env scalex-monitor

# Using supervisor
supervisorctl start portfolio-monitor
```

### Cloud Deployment
- **AWS**: EC2 + CloudWatch
- **Google Cloud**: Compute Engine + Cloud Logging
- **Azure**: VM + Application Insights
- **Heroku**: Worker dyno with Scheduler add-on

## 📊 Monitoring and Maintenance

### Health Checks
```bash
# Check system status
python main.py status

# Test alert system
python main.py test-alerts

# View recent logs
tail -f logs/portfolio_monitor.log
```

### Database Maintenance
- Automatic cleanup runs weekly
- Manual cleanup: modify `cleanup_old_data()` in `scheduler.py`
- Backup: SQLite file at `portfolio_mentions.db`

## 🔐 Security Considerations

1. **API Keys**: Store in `.env` file, never commit to version control
2. **Email Passwords**: Use app-specific passwords, not account passwords
3. **Rate Limiting**: Respect API rate limits to avoid being blocked
4. **Data Privacy**: Consider data retention policies for mentions
5. **Access Control**: Secure the server running the monitoring system

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is proprietary to ScaleX Ventures.

## 📞 Support

For issues or questions:
- Check the logs first: `logs/portfolio_monitor.log`
- Review configuration in `.env`
- Test components individually using `main.py` commands
- Contact the development team for additional support

---

**Built with ❤️ for ScaleX Ventures Portfolio Monitoring**
