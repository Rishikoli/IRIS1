"""
Sentiment Analysis API Routes

Provides endpoints for:
1. Agent 8 market sentiment analysis (existing)
2. News monitoring sentiment data (NEW)
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, timezone
from src.agents.agent8_market_sentiment import market_sentiment_agent
from src.agents.agent8_market_sentinel import market_sentinel_agent
import logging
import os
import sys

# Add monitoring module to path
monitoring_path = os.path.join(os.path.dirname(__file__), '../../monitoring')
sys.path.insert(0, monitoring_path)

from database import get_db, NewsArticle, NewsSentiment, SentimentAlert
from sqlalchemy import func, desc

router = APIRouter()
logger = logging.getLogger(__name__)

# ============================================================================
# Pydantic Models for Request/Response
# ============================================================================

class SentimentRequest(BaseModel):
    """Request model for Agent 8 sentiment analysis"""
    company_symbol: str

class MarketSentinelRequest(BaseModel):
    """Request model for Agent 8 technical analysis (Market Sentinel)"""
    company_symbol: str

class NewsArticleResponse(BaseModel):
    """Response model for news article with sentiment"""
    id: int
    title: str
    url: str
    source: str
    published_date: Optional[datetime]
    scraped_at: datetime
    company: Optional[str]
    sentiment: str
    confidence: float
    positive_score: Optional[float]
    negative_score: Optional[float]
    neutral_score: Optional[float]

class CompanySentimentResponse(BaseModel):
    """Response model for company sentiment aggregation"""
    company: str
    total_articles: int
    sentiment_breakdown: Dict[str, int]
    avg_confidence: float
    avg_positive_score: float
    avg_negative_score: float
    avg_neutral_score: float
    trending: str  # "up", "down", "neutral"

class AlertResponse(BaseModel):
    """Response model for sentiment alert"""
    id: int
    article_id: Optional[int]
    alert_type: str
    severity: str
    message: str
    triggered_at: datetime
    acknowledged: bool

class SourceStatsResponse(BaseModel):
    """Response model for news source statistics"""
    source: str
    total_articles: int
    avg_sentiment_score: float
    sentiment_distribution: Dict[str, int]

# ============================================================================
# Agent 8 Market Sentiment Endpoint (Existing)
# ============================================================================

@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_sentiment(request: SentimentRequest):
    """
    Analyze market sentiment for a company using Google Trends and News
    (Agent 8 integration)
    """
    try:
        logger.info(f"Sentiment analysis request for: {request.company_symbol}")
        
        if not request.company_symbol.strip():
            raise HTTPException(status_code=400, detail="Company symbol cannot be empty")

        result = market_sentiment_agent.get_sentiment_analysis(request.company_symbol)
        
        if "error" in result:
             logger.error(f"Sentiment analysis failed: {result['error']}")
        
        return {
            "success": True,
            "data": result
        }

    except Exception as e:
        logger.error(f"Error in sentiment endpoint: {str(e)}")
        return {
            "success": False,
            "data": {
                "company": request.company_symbol,
                "error": str(e),
                "overall_sentiment": "Neutral",
                "trends": {"status": "error", "data": []},
                "news_sentiment": {"status": "error", "sentiment": "neutral"}
            }
        }

# ============================================================================
# Agent 8 Market Sentinel Endpoint (Technical / Pump & Dump)
# ============================================================================

@router.post("/technical/analyze", response_model=Dict[str, Any])
async def analyze_technical(request: MarketSentinelRequest):
    """
    Analyze market technicals for a company using Price/Volume data
    (Agent 8 Market Sentinel - Pump & Dump Detection)
    """
    try:
        logger.info(f"Technical analysis request for: {request.company_symbol}")
        
        if not request.company_symbol.strip():
            raise HTTPException(status_code=400, detail="Company symbol cannot be empty")

        result = market_sentinel_agent.analyze_stock(request.company_symbol)
        
        if not result.get("success"):
             logger.warning(f"Technical analysis failed: {result.get('error')}")
        
        return {
            "success": True,
            "data": result
        }

    except Exception as e:
        logger.error(f"Error in technical endpoint: {str(e)}")
        return {
            "success": False,
            "data": {
                "symbol": request.company_symbol,
                "error": str(e),
                "risk_level": "UNKNOWN",
                "signals": []
            }
        }

# ============================================================================
# News Monitoring Endpoints (NEW)
# ============================================================================

@router.get("/news/latest", response_model=List[NewsArticleResponse])
async def get_latest_news(
    limit: int = Query(default=20, le=100, description="Maximum number of articles to return"),
    hours: int = Query(default=24, le=168, description="Look back period in hours"),
    sentiment_filter: Optional[str] = Query(default=None, description="Filter by sentiment: positive, negative, neutral"),
    min_confidence: Optional[float] = Query(default=None, ge=0, le=1, description="Minimum confidence score")
):
    """
    Get latest news articles with sentiment analysis
    
    **Parameters:**
    - **limit**: Number of articles (max 100)
    - **hours**: Time window in hours (max 168 = 1 week)
    - **sentiment_filter**: Filter by positive/negative/neutral
    - **min_confidence**: Minimum confidence threshold (0-1)
    
    **Returns:** List of news articles with sentiment analysis
    """
    try:
        db = get_db()
        session = db.get_session()
        
        # Calculate time threshold
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        # Build query
        query = session.query(NewsArticle, NewsSentiment).join(NewsSentiment)
        query = query.filter(NewsArticle.scraped_at >= since)
        
        # Apply filters
        if sentiment_filter:
            query = query.filter(NewsSentiment.sentiment == sentiment_filter.lower())
        
        if min_confidence:
            query = query.filter(NewsSentiment.confidence >= min_confidence)
        
        # Order by newest first
        query = query.order_by(desc(NewsArticle.scraped_at))
        query = query.limit(limit)
        
        results = query.all()
        session.close()
        
        # Format response
        articles = []
        for article, sentiment in results:
            articles.append(NewsArticleResponse(
                id=article.id,
                title=article.title,
                url=article.url,
                source=article.source,
                published_date=article.published_date,
                scraped_at=article.scraped_at,
                company=article.company,
                sentiment=sentiment.sentiment,
                confidence=sentiment.confidence,
                positive_score=sentiment.positive_score,
                negative_score=sentiment.negative_score,
                neutral_score=sentiment.neutral_score
            ))
        
        return articles
        
    except Exception as e:
        logger.error(f"Error fetching latest news: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/company/{company_name}", response_model=CompanySentimentResponse)
async def get_company_sentiment(
    company_name: str,
    hours: int = Query(default=24, le=168, description="Look back period in hours")
):
    """
    Get aggregated sentiment analysis for a specific company
    
    **Parameters:**
    - **company_name**: Company name (e.g., "Reliance", "TCS", "HDFC")
    - **hours**: Time window in hours (default: 24)
    
    **Returns:** Aggregated sentiment metrics for the company
    """
    try:
        db = get_db()
        session = db.get_session()
        
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        # Search for company mentions in title OR content OR company field
        # More flexible matching for Indian company names
        search_patterns = [
            company_name,  # Exact match
            company_name.upper(),  # RELIANCE
            f"{company_name} Industries",  # Reliance Industries
            f"{company_name} Ltd",  # Reliance Ltd
            f"{company_name} Limited",  # Reliance Limited
        ]
        
        articles = session.query(NewsArticle, NewsSentiment).join(NewsSentiment).filter(
            NewsArticle.scraped_at >= since
        ).filter(
            # Search in title OR content
            (NewsArticle.title.ilike(f"%{company_name}%")) |
            (NewsArticle.content.ilike(f"%{company_name}%")) |
            (NewsArticle.company.ilike(f"%{company_name}%"))
        ).all()
        
        if not articles:
            session.close()
            raise HTTPException(status_code=404, detail=f"No recent news found for {company_name}")
        
        # Calculate aggregations
        total = len(articles)
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        total_confidence = 0
        total_pos = 0
        total_neg = 0
        total_neu = 0
        
        for _, sentiment in articles:
            sentiment_counts[sentiment.sentiment] += 1
            total_confidence += sentiment.confidence
            total_pos += sentiment.positive_score or 0
            total_neg += sentiment.negative_score or 0
            total_neu += sentiment.neutral_score or 0
        
        # Determine trend
        trending = "neutral"
        if sentiment_counts["positive"] > sentiment_counts["negative"] * 1.5:
            trending = "up"
        elif sentiment_counts["negative"] > sentiment_counts["positive"] * 1.5:
            trending = "down"
        
        session.close()
        
        return CompanySentimentResponse(
            company=company_name,
            total_articles=total,
            sentiment_breakdown=sentiment_counts,
            avg_confidence=total_confidence / total,
            avg_positive_score=total_pos / total,
            avg_negative_score=total_neg / total,
            avg_neutral_score=total_neu / total,
            trending=trending
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching company sentiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trends", response_model=Dict[str, Any])
async def get_sentiment_trends(
    hours: int = Query(default=168, le=720, description="Look back period in hours (max 30 days)"),
    interval_hours: int = Query(default=24, description="Grouping interval in hours")
):
    """
    Get sentiment trends over time
    
    **Parameters:**
    - **hours**: Total time window (default: 168 hours = 1 week)
    - **interval_hours**: Group data by this interval (default: 24 hours)
    
    **Returns:** Time-series sentiment data grouped by interval
    """
    try:
        db = get_db()
        session = db.get_session()
        
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        # Get all articles in time window
        articles = session.query(NewsArticle, NewsSentiment).join(NewsSentiment).filter(
            NewsArticle.scraped_at >= since
        ).order_by(NewsArticle.scraped_at).all()
        
        session.close()
        
        # Group by interval
        intervals = {}
        for article, sentiment in articles:
            # Calculate interval bucket
            time_diff = article.scraped_at - since
            bucket = int(time_diff.total_seconds() / (interval_hours * 3600))
            bucket_time = since + timedelta(hours=bucket * interval_hours)
            
            bucket_key = bucket_time.isoformat()
            if bucket_key not in intervals:
                intervals[bucket_key] = {
                    "timestamp": bucket_key,
                    "positive": 0,
                    "negative": 0,
                    "neutral": 0,
                    "total": 0
                }
            
            intervals[bucket_key][sentiment.sentiment] += 1
            intervals[bucket_key]["total"] += 1
        
        # Convert to sorted list
        trend_data = sorted(intervals.values(), key=lambda x: x["timestamp"])
        
        return {
            "success": True,
            "period_hours": hours,
            "interval_hours": interval_hours,
            "data_points": len(trend_data),
            "trends": trend_data
        }
        
    except Exception as e:
        logger.error(f"Error fetching sentiment trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts", response_model=List[AlertResponse])
async def get_alerts(
    acknowledged: bool = Query(default=False, description="Show acknowledged alerts"),
    severity: Optional[str] = Query(default=None, description="Filter by severity: critical, high, medium, low"),
    limit: int = Query(default=50, le=200)
):
    """
    Get sentiment alerts
    
    **Parameters:**
    - **acknowledged**: Include acknowledged alerts (default: False)
    - **severity**: Filter by severity level
    - **limit**: Maximum number of alerts
    
    **Returns:** List of triggered alerts
    """
    try:
        db = get_db()
        session = db.get_session()
        
        query = session.query(SentimentAlert)
        
        if not acknowledged:
            query = query.filter(SentimentAlert.acknowledged == False)
        
        if severity:
            query = query.filter(SentimentAlert.severity == severity)
        
        query = query.order_by(desc(SentimentAlert.triggered_at)).limit(limit)
        
        alerts = query.all()
        session.close()
        
        return [
            AlertResponse(
                id=alert.id,
                article_id=alert.article_id,
                alert_type=alert.alert_type,
                severity=alert.severity,
                message=alert.message,
                triggered_at=alert.triggered_at,
                acknowledged=alert.acknowledged
            )
            for alert in alerts
        ]
        
    except Exception as e:
        logger.error(f"Error fetching alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: int):
    """
    Acknowledge a sentiment alert
    
    **Parameters:**
    - **alert_id**: ID of the alert to acknowledge
    
    **Returns:** Success confirmation
    """
    try:
        db = get_db()
        session = db.get_session()
        
        alert = session.query(SentimentAlert).get(alert_id)
        
        if not alert:
            session.close()
            raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
        
        alert.acknowledged = True
        alert.acknowledged_at = datetime.now(timezone.utc)
        
        session.commit()
        session.close()
        
        return {
            "success": True,
            "message": f"Alert {alert_id} acknowledged",
            "acknowledged_at": alert.acknowledged_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error acknowledging alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sources", response_model=List[SourceStatsResponse])
async def get_source_statistics(
    hours: int = Query(default=24, le=168)
):
    """
    Get statistics by news source
    
    **Parameters:**
    - **hours**: Look back period in hours
    
    **Returns:** Article counts and sentiment distribution by source
    """
    try:
        db = get_db()
        session = db.get_session()
        
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        # Get articles grouped by source
        articles = session.query(NewsArticle, NewsSentiment).join(NewsSentiment).filter(
            NewsArticle.scraped_at >= since
        ).all()
        
        session.close()
        
        # Group by source
        sources = {}
        for article, sentiment in articles:
            source = article.source
            if source not in sources:
                sources[source] = {
                    "articles": [],
                    "sentiments": {"positive": 0, "negative": 0, "neutral": 0}
                }
            
            sources[source]["articles"].append(sentiment.confidence)
            sources[source]["sentiments"][sentiment.sentiment] += 1
        
        # Calculate statistics
        source_stats = []
        for source, data in sources.items():
            source_stats.append(SourceStatsResponse(
                source=source,
                total_articles=len(data["articles"]),
                avg_sentiment_score=sum(data["articles"]) / len(data["articles"]) if data["articles"] else 0,
                sentiment_distribution=data["sentiments"]
            ))
        
        # Sort by article count
        source_stats.sort(key=lambda x: x.total_articles, reverse=True)
        
        return source_stats
        
    except Exception as e:
        logger.error(f"Error fetching source statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def sentiment_health_check():
    """
    Health check for sentiment monitoring system
    
    **Returns:** System status and database connectivity
    """
    try:
        db = get_db()
        if not db.test_connection():
            return {
                "status": "degraded",
                "database": "disconnected",
                "message": "Sentiment database is not accessible"
            }
        
        session = db.get_session()
        total_articles = session.query(NewsArticle).count()
        total_alerts = session.query(SentimentAlert).filter(
            SentimentAlert.acknowledged == False
        ).count()
        session.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "total_articles": total_articles,
            "active_alerts": total_alerts
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "error",
            "error": str(e)
        }
