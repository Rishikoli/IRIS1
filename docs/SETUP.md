# Environment Setup for Gemini AI Integration

## Required Environment Variable

Add the following to your `.env.local` file in the frontend directory:

```bash
# Gemini AI API Key
GEMINI_API_KEY=your_gemini_api_key_here
```

## How to Get Your Gemini API Key

1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key
5. Add it to `.env.local` file

## Model Used

- **Model**: `gemini-2.0-flash-exp`
- **Purpose**: Real-time AI summary generation
- **Features**: 
  - Forensic analysis summaries
  - Risk intelligence summaries
  - Context-aware recommendations

## API Endpoint

The integration uses:
- **Route**: `/api/gemini-summary`
- **Method**: POST
- **Payload**: `{ analysisData, summaryType, companySymbol }`

## Testing

After adding the API key:
1. Restart the development server
2. Analyze a company
3. Navigate to Forensic or Risk tabs
4. AI summaries will generate automatically

# Automated Monitoring Setup Guide

This guide shows you how to set up the news monitoring system to run continuously in the background.

## Option 1: Run Manually (Simple)

### Start the scheduler in foreground:

```bash
cd /home/aditya/IRIS1/backend/src/monitoring
source ../../iris_venv/bin/activate
python3 scheduler.py
```

- Runs monitoring immediately, then hourly
- Press `Ctrl+C` to stop
- Logs appear in terminal

### Configuration

Edit [`/home/aditya/IRIS1/backend/src/monitoring/.env`](file:///home/aditya/IRIS1/backend/src/monitoring/.env):

```bash
# Alert thresholds
HIGH_CONFIDENCE_NEGATIVE=0.85    # Trigger alert at 85%+ negative confidence
HIGH_CONFIDENCE_POSITIVE=0.90    # Trigger alert at 90%+ positive confidence
NEGATIVE_BATCH_THRESHOLD=5       # Trigger alert with 5+ negative articles/hour

# Monitoring frequency (can be changed in scheduler.py)
MONITORING_INTERVAL_MINUTES=60

# Articles per source per cycle
MAX_ARTICLES_PER_SOURCE=50
```

---

## Option 2: Run as Background Service (Recommended)

This sets up the monitoring system to run automatically on system startup.

### 1. Install the service

```bash
# Copy service file to systemd
sudo cp /home/aditya/IRIS1/backend/src/monitoring/iris-news-monitor.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable iris-news-monitor

# Start the service
sudo systemctl start iris-news-monitor
```

### 2. Manage the service

```bash
# Check status
sudo systemctl status iris-news-monitor

# View logs
sudo journalctl -u iris-news-monitor -f

# Stop the service
sudo systemctl stop iris-news-monitor

# Restart the service
sudo systemctl restart iris-news-monitor

# Disable auto-start on boot
sudo systemctl disable iris-news-monitor
```

### 3. View logs

The service writes to two log files:

```bash
# Standard output (monitoring results)
sudo tail -f /var/log/iris-monitoring.log

# Errors only
sudo tail -f /var/log/iris-monitoring-error.log
```

### 4. Create log files (first time only)

```bash
sudo touch /var/log/iris-monitoring.log
sudo touch /var/log/iris-monitoring-error.log
sudo chown aditya:aditya /var/log/iris-monitoring*.log
```

---

## Option 3: Run with Screen/Tmux (Alternative)

Keep the scheduler running even when you disconnect from SSH.

### Using Screen:

```bash
# Start a named screen session
screen -S news-monitor

# Inside screen, run the scheduler
cd /home/aditya/IRIS1/backend/src/monitoring
source ../../iris_venv/bin/activate
python3 scheduler.py

# Detach from screen: Press Ctrl+A, then D

# Re-attach later
screen -r news-monitor

# List all screens
screen -ls

# Kill the screen session
screen -X -S news-monitor quit
```

### Using Tmux:

```bash
# Start a named tmux session
tmux new -s news-monitor

# Inside tmux, run the scheduler
cd /home/aditya/IRIS1/backend/src/monitoring
source ../../iris_venv/bin/activate
python3 scheduler.py

# Detach from tmux: Press Ctrl+B, then D

# Re-attach later
tmux attach -t news-monitor

# List all sessions
tmux ls

# Kill the session
tmux kill-session -t news-monitor
```

---

## Monitoring Dashboard Queries

### Quick Status Check

```bash
# Total articles in database
sudo -u postgres psql iris_monitoring -c "SELECT COUNT(*) as total FROM news_articles;"

# Sentiment breakdown
sudo -u postgres psql iris_monitoring -c "
  SELECT sentiment, COUNT(*) as count, ROUND(AVG(confidence)::NUMERIC, 2) as avg_conf
  FROM news_sentiment
  GROUP BY sentiment
  ORDER BY count DESC;
"

# Latest 5 articles
sudo -u postgres psql iris_monitoring -c "
  SELECT title, sentiment, confidence, analyzed_at
  FROM latest_news_with_sentiment
  ORDER BY analyzed_at DESC
  LIMIT 5;
"

# Active alerts
sudo -u postgres psql iris_monitoring -c "SELECT * FROM unacknowledged_alerts;"
```

### Company-specific sentiment

```bash
# Reliance sentiment in last 24 hours
sudo -u postgres psql iris_monitoring -c "
  SELECT * FROM get_company_sentiment_trend('Reliance', 24);
"
```

---

## Changing Monitoring Frequency

Edit [`scheduler.py`](file:///home/aditya/IRIS1/backend/src/monitoring/scheduler.py#L67) line 67:

```python
# Current: Every hour
schedule.every().hour.do(run_monitoring_job)

# Every 30 minutes
schedule.every(30).minutes.do(run_monitoring_job)

# Every 2 hours
schedule.every(2).hours.do(run_monitoring_job)

# Specific times
schedule.every().day.at("09:00").do(run_monitoring_job)
schedule.every().day.at("15:00").do(run_monitoring_job)
```

After changing, restart the service:
```bash
sudo systemctl restart iris-news-monitor
```

---

## Troubleshooting

### Service won't start

```bash
# Check service status
sudo systemctl status iris-news-monitor

# View detailed logs
sudo journalctl -u iris-news-monitor -n 50

# Check environment file exists
ls -la /home/aditya/IRIS1/backend/src/monitoring/.env

# Test manually first
cd /home/aditya/IRIS1/backend/src/monitoring
source ../../iris_venv/bin/activate
python3 scheduler.py
```

### Database connection errors

```bash
# Verify PostgreSQL is running
sudo systemctl status postgresql

# Test connection
sudo -u postgres psql iris_monitoring -c "SELECT 1;"

# Check DATABASE_URL in .env
cat /home/aditya/IRIS1/backend/src/monitoring/.env
```

### No new articles being collected

```bash
# Check if URLs are still valid
cd /home/aditya/IRIS1/backend/src/ml/data_collection
source ../../iris_venv/bin/activate
python3 scrape_news.py

# Verify internet connectivity
ping -c 3 economictimes.indiatimes.com
```

---

## Performance Tuning

### Reduce resource usage

1. **Decrease frequency**: Change to every 2-4 hours instead of hourly
2. **Reduce articles per source**: Change `MAX_ARTICLES_PER_SOURCE` from 50 to 25 in `.env`
3. **Use CPU instead of GPU**: Already configured by default

### Increase throughput

1. **Increase frequency**: Change to every 30 minutes
2. **More articles**: Increase `MAX_ARTICLES_PER_SOURCE` to 100
3. **Add more sources**: Edit [`scrape_news.py`](file:///home/aditya/IRIS1/backend/src/ml/data_collection/scrape_news.py)

---

## Integration with I.R.I.S. Backend

To integrate with Agent 8 (Market Sentiment), add this endpoint to your FastAPI backend:

```python
from monitoring.database import get_db, NewsArticle, NewsSentiment
from datetime import datetime, timedelta, timezone

@app.get("/api/v1/sentiment/latest")
async def get_latest_sentiment(
    company: str = None,
    hours: int = 24,
    limit: int = 10
):
    """Get latest sentiment analysis"""
    db = get_db()
    session = db.get_session()
    
    query = session.query(NewsArticle, NewsSentiment).join(NewsSentiment)
    
    # Filter by company if provided
    if company:
        query = query.filter(NewsArticle.company.ilike(f"%{company}%"))
    
    # Filter by time window
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    query = query.filter(NewsArticle.scraped_at >= since)
    
    # Get results
    results = query.order_by(NewsArticle.scraped_at.desc()).limit(limit).all()
    
    session.close()
    
    return {
        "company": company,
        "hours": hours,
        "count": len(results),
        "articles": [
            {
                "title": article.title,
                "url": article.url,
                "source": article.source,
                "published": article.published_date,
                "sentiment": sentiment.sentiment,
                "confidence": sentiment.confidence,
                "scores": {
                    "positive": sentiment.positive_score,
                    "negative": sentiment.negative_score,
                    "neutral": sentiment.neutral_score
                }
            }
            for article, sentiment in results
        ]
    }
```

---

## System Architecture

```
PostgreSQL Database
       ↓
News Monitor (scheduler.py)
       ↓
  1. Scrape News (every hour)
  2. Analyze Sentiment (FinBERT)
  3. Store Results
  4. Check Alert Thresholds
  5. Trigger Alerts
       ↓
I.R.I.S. Agent 8 (Market Sentiment)
```

---

## Next Steps

1. ✅ **Start monitoring**: Choose Option 1, 2, or 3 above
2. **Monitor for 24 hours**: Verify data collection is working
3. **Review alerts**: Check if thresholds need adjustment
4. **Integrate with I.R.I.S.**: Add API endpoints for agents
5. **Create dashboard**: Build Streamlit visualization (optional)

Happy monitoring! 🚀
