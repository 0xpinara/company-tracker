# 🌐 ScaleX Ventures Portfolio Monitor - Web Interface

## 🚀 Quick Start

### Option 1: Simple Launch
```bash
# Set your NewsAPI key
export NEWS_API_KEY=9cee5ca0f989440394094acacad4cae0

# Start the web application
python3 start_web_app.py
```

### Option 2: Direct Launch
```bash
# Set your NewsAPI key
export NEWS_API_KEY=9cee5ca0f989440394094acacad4cae0

# Start Flask directly
python3 app.py
```

## 🌐 Access the Web Interface

Once started, open your browser and go to:
- **Main Dashboard**: http://localhost:5000
- **Portfolio View**: http://localhost:5000/portfolio
- **Mentions View**: http://localhost:5000/mentions

## ✨ Features

### 📊 Dashboard
- **Real-time Statistics**: Total mentions, recent activity, active companies
- **Interactive Charts**: Company mentions pie chart, source mentions bar chart
- **Portfolio Breakdown**: Fund I, Acquired, Angel investments
- **Recent Mentions**: Latest 10 mentions with sentiment analysis
- **Run Monitoring**: One-click monitoring execution

### 🏢 Portfolio View
- **Complete Portfolio**: All 29 ScaleX Ventures companies
- **Organized by Fund**: Fund I, Acquired, Angel investments
- **Company Details**: Description, website, fund type
- **Visual Cards**: Beautiful card layout for each company

### 📰 Mentions View
- **Filterable Table**: Filter by company, source, sentiment
- **Search Functionality**: Search through titles and content
- **Sentiment Analysis**: Color-coded sentiment indicators
- **External Links**: Direct links to original articles
- **Real-time Updates**: Auto-refresh every 30 seconds

## 🎯 Perfect for Interviews

### What to Show:
1. **"I built a complete web interface for portfolio monitoring"**
2. **"Real-time dashboard with live data and charts"**
3. **"Interactive filtering and search capabilities"**
4. **"Professional UI with Bootstrap and Chart.js"**
5. **"One-click monitoring execution"**

### Demo Flow:
1. **Show Dashboard**: "Here's the main dashboard with real-time stats"
2. **Run Monitoring**: Click "Run Monitoring" to show live data collection
3. **Show Portfolio**: "All 29 ScaleX Ventures companies organized by fund"
4. **Show Mentions**: "Filterable table with sentiment analysis"
5. **Show Charts**: "Interactive visualizations of the data"

## 🛠️ Technical Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **UI Framework**: Bootstrap 5
- **Charts**: Chart.js
- **Icons**: Font Awesome
- **Database**: SQLite
- **APIs**: NewsAPI, Google News RSS

## 📱 Responsive Design

- **Mobile-friendly**: Works on all screen sizes
- **Modern UI**: Clean, professional design
- **Interactive Elements**: Hover effects, animations
- **Real-time Updates**: Auto-refresh capabilities

## 🔧 Customization

### Adding New Companies:
Edit `config_complete.py` to add new portfolio companies.

### Styling:
Modify `static/css/style.css` for custom styling.

### Functionality:
Update `static/js/main.js` for additional JavaScript features.

## 🚀 Deployment Options

### Local Development:
```bash
python3 start_web_app.py
```

### Production Deployment:
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker Deployment:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "app.py"]
```

## 🎉 Ready for Your Interview!

This web interface demonstrates:
- ✅ **Full-stack development** (Python Flask + HTML/CSS/JS)
- ✅ **Real-time data processing** (NewsAPI + RSS feeds)
- ✅ **Professional UI/UX** (Bootstrap + responsive design)
- ✅ **Data visualization** (Chart.js charts and graphs)
- ✅ **Database management** (SQLite with proper schema)
- ✅ **API integration** (RESTful endpoints)
- ✅ **Business value** (VC portfolio monitoring)

**You're ready to impress!** 🚀
