# SDK & API Reference

## Database Connection
The API connects to PostgreSQL using the `DATABASE_URL` environment variable:
`DATABASE_URL=postgresql://postgres:iris_monitor_2024@localhost:5432/iris_monitoring`

## Base URL
`/api/v1/sentiment`

## Endpoints

### 1. Latest News 📰
`GET /news/latest`
Get latest news articles with sentiment analysis.
- **Params**: `limit` (max 100), `hours` (window), `sentiment_filter`, `min_confidence`
- **Response**: List of articles with `positive_score`, `confidence`, etc.

### 2. Company Sentiment 🏢
`GET /company/{company_name}`
Get aggregated sentiment analysis for a specific company.
- **Params**: `hours` (lookback period)
- **Response**: `sentiment_breakdown`, `avg_confidence`, `trending` ("up"/"down"/"neutral").

### 3. Sentiment Trends 📈
`GET /trends`
Get sentiment trends over time.
- **Params**: `hours` (total window), `interval_hours` (grouping)
- **Response**: Time-series data points.

### 4. Alerts 🚨
`GET /alerts`
Get triggered sentiment alerts.
- **Params**: `severity` (critical/high), `acknowledged` (bool)
- **Response**: List of alerts with `message`, `triggered_at`.

### 5. Health Check ❤️
`GET /health`
System status check.
- **Response**: `status`, `database_connected`.

## Agent Integration (SDK)

### Python Example
```python
import requests

def get_real_time_sentiment(company):
    response = requests.get(
        f"http://localhost:8000/api/v1/sentiment/company/{company}",
        params={"hours": 24}
    )
    if response.status_code == 200:
        return response.json()
    return None
```
