# Real-time News Monitoring System

Automated system for monitoring Indian financial news with sentiment analysis and alerts.

## 🎯 Features

- **Automated News Scraping**: Fetches latest news from Economic Times, Moneycontrol, LiveMint
- **Sentiment Analysis**: Uses FinBERT to analyze financial sentiment
- **PostgreSQL Storage**: Stores articles, sentiment, and alerts
- **Smart Alerting**: Triggers alerts on major sentiment shifts
- **Scheduled Monitoring**: Runs hourly/daily automatically

---

## 📋 Prerequisites

1. **PostgreSQL Database** running
2. **Python dependencies** installed
3. **FinBERT model** (auto-downloaded on first run)

---

## 🚀 Quick Start

### 1. Install PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**Create database:**
```bash
sudo -u postgres psql
CREATE DATABASE iris_monitoring;
CREATE USER iris_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE iris_monitoring TO iris_user;
\q
```

### 2. Install Dependencies

```bash
cd src/monitoring
pip install -r requirements_monitoring.txt
```

### 3. Configure Database Connection

**Option A: Environment variable** (recommended)
```bash
export DATABASE_URL="postgresql://iris_user:your_password@localhost:5432/iris_monitoring"
```

**Option B: Edit database.py**
Update the default URL in `database.py`:
```python
'postgresql://iris_user:your_password@localhost:5432/iris_monitoring'
```

### 4. Initialize Database

```bash
python database.py
```

Expected output:
```
✓ Database connection successful
Creating database tables...
✓ Tables created successfully
```

### 5. Test Sentiment Analyzer

```bash
python sentiment_analyzer.py
```

### 6. Run Monitoring Once

```bash
python news_monitor.py
```

---

## 📅 Automated Scheduling

### Option A: Python Scheduler (Recommended)

Run continuously:
```bash
python scheduler.py
```

Monitors news every hour and logs to console.

### Option B: Cron Job

Add to crontab:
```bash
crontab -e
```

Add line:
```
0 * * * * cd /path/to/backend/src/monitoring && /path/to/python news_monitor.py >> monitor.log 2>&1
```

This runs every hour on the hour.

### Option C: Systemd Service

Create `/etc/systemd/system/news-monitor.service`:
```ini
[Unit]
Description=News Monitoring Service
After=postgresql.service

[Service]
Type=simple
User=your_user
WorkingDirectory=/home/your_user/IRIS1/backend/src/monitoring
Environment="DATABASE_URL=postgresql://iris_user:password@localhost:5432/iris_monitoring"
ExecStart=/home/your_user/IRIS1/backend/iris_venv/bin/python scheduler.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable news-monitor
sudo systemctl start news-monitor
sudo systemctl status news-monitor
```

---

## 📊 Database Schema

### Tables

**news_articles**
- Stores scraped news articles
- Fields: title, content, url, source, published_date, company, sector

**news_sentiment**
- Sentiment analysis results for each article
- Fields: sentiment, confidence, positive/negative/neutral scores

**sentiment_alerts**
- Triggered alerts for major sentiment events
- Fields: alert_type, severity, message, acknowledged

### Views

**latest_news_with_sentiment**
- Combined view of articles + sentiment

**unacknowledged_alerts**
- Active alerts needing attention

---

## 🔔 Alert Types

| Alert Type | Trigger Condition | Severity |
|------------|-------------------|----------|
| `major_negative` | Confidence > 85% on negative sentiment | High |
| `major_positive` | Confidence > 90% on positive sentiment | Medium |
| `high_volatility` | 5+ negative articles in last hour | Critical |

---

## 🔧 Configuration

### Adjust Alert Thresholds

Edit `news_monitor.py`:
```python
self.alert_thresholds = {
    'high_confidence_negative': 0.85,  # Default: 85%
    'high_confidence_positive': 0.90,  # Default: 90%
    'negative_batch_threshold': 5,     # Default: 5 articles
}
```

### Change Monitoring Frequency

Edit `scheduler.py`:
```python
# Hourly (default)
schedule.every().hour.do(run_monitoring_job)

# Every 30 minutes
schedule.every(30).minutes.do(run_monitoring_job)

# Daily at specific times
schedule.every().day.at("09:00").do(run_monitoring_job)
schedule.every().day.at("15:00").do(run_monitoring_job)
```

---

## 📈 Querying Data

### View Latest Articles with Sentiment

```sql
SELECT * FROM latest_news_with_sentiment
ORDER BY scraped_at DESC
LIMIT 10;
```

### Check Unacknowledged Alerts

```sql
SELECT * FROM unacknowledged_alerts;
```

### Get Sentiment Trend for Company

```sql
SELECT * FROM get_company_sentiment_trend('Reliance', 30);
```

### Python Queries

```python
from monitoring.database import get_db, NewsArticle, NewsSentiment

db = get_db()
session = db.get_session()

# Get latest articles
latest = session.query(NewsArticle).order_by(
    NewsArticle.scraped_at.desc()
).limit(10).all()

for article in latest:
    print(f"{article.title} - {article.sentiment.sentiment if article.sentiment else 'N/A'}")
```

---

## 🐛 Troubleshooting

### Database Connection Failed

```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U iris_user -d iris_monitoring -h localhost
```

### No Articles Scraped

- Check internet connection
- Verify news source URLs are accessible
- Check logs for specific errors

### Sentiment Analysis Slow

- First run downloads FinBERT model (~440MB)
- Use GPU for faster analysis
- Reduce `max_articles_per_source`

### Alerts Not Triggering

- Check `alert_thresholds` in `news_monitor.py`
- Verify sentiment analysis is running
- Check database for stored alerts

---

## 📂 File Structure

```
monitoring/
├── schema.sql                  # Database schema
├── database.py                 # SQLAlchemy models & connection
├── sentiment_analyzer.py       # FinBERT sentiment analysis
├── news_monitor.py             # Main monitoring logic
├── scheduler.py                # Automated scheduling
├── requirements_monitoring.txt # Dependencies
└── README.md                   # This file
```

---

## 🔄 Workflow

```mermaid
graph LR
    A[Scheduler] --> B[Scrape News]
    B --> C[Filter New Articles]
    C --> D[Analyze Sentiment]
    D --> E[Store in PostgreSQL]
    E --> F{Check Thresholds}
    F -->|High Confidence| G[Trigger Alert]
    F -->|Normal| H[No Action]
```

---

## 🎓 Next Steps

1. **Integrate with Agent 8**: Query database for market sentiment
2. **Add Notifications**: Email/Slack alerts on critical events
3. **Build Dashboard**: Streamlit UI to visualize trends
4. **Company Tracking**: Track specific stocks/sectors
5. **Historical Analysis**: Backtest sentiment vs stock performance

---

## 📄 License

Part of the I.R.I.S. project. For internal use only.
