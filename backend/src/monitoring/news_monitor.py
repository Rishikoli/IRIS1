"""
Real-time News Monitor

Automatically scrapes news, analyzes sentiment, stores in database,
and triggers alerts on major sentiment shifts.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ml.data_collection.scrape_news import FinancialNewsScraper
from monitoring.database import get_db, NewsArticle, NewsSentiment, SentimentAlert
from monitoring.sentiment_analyzer import get_analyzer
from datetime import datetime, timedelta, timezone
from typing import List, Dict
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NewsMonitor:
    """Automated news monitoring and sentiment analysis"""
    
    def __init__(self):
        self.db = get_db()
        self.analyzer = get_analyzer()
        self.scraper = FinancialNewsScraper()
        
        # Alert thresholds
        self.alert_thresholds = {
            'high_confidence_negative': 0.85,  # Confidence > 85% for negative
            'high_confidence_positive': 0.90,  # Confidence > 90% for positive
            'negative_batch_threshold': 5,     # 5+ negative articles in last hour
        }
    
    def run_once(self, max_articles_per_source: int = 50):
        """
        Run monitoring cycle once
        
        Executes:
        1. Scrape latest news
        2. Filter new articles
        3. Analyze sentiment
        4. Store results
        5. Check for alerts
        
        Args:
            max_articles_per_source: Max articles to scrape per source
        """
        logger.info("="*50)
        logger.info("Starting news monitoring cycle")
        logger.info("="*50)
        
        # Step 1: Scrape news
        logger.info("Scraping latest news...")
        news_df = self.scraper.scrape_all_sources(
            max_articles_per_source=max_articles_per_source
        )
        
        if news_df.empty:
            logger.warning("No news articles scraped")
            return
        
        logger.info(f"Scraped {len(news_df)} articles")
        
        # Step 2: Filter new articles
        new_articles = self._filter_new_articles(news_df)
        logger.info(f"Found {len(new_articles)} new articles")
        
        if not new_articles:
            logger.info("No new articles to process")
            return {
                'articles_processed': 0,
                'alerts_triggered': 0
            }
        
        # Step 3: Analyze sentiment
        logger.info("Analyzing sentiment...")
        articles_with_sentiment = self._analyze_articles(new_articles)
        
        # Step 4: Store in database
        logger.info("Storing results in database...")
        article_ids = self._store_articles(articles_with_sentiment)
        
        # Step 5: Check for alerts
        logger.info("Checking for alerts...")
        alerts = self._check_alerts(article_ids)
        
        logger.info("="*50)
        logger.info(f"✓ Monitoring cycle complete")
        logger.info(f"  New articles: {len(article_ids)}")
        logger.info(f"  Alerts triggered: {len(alerts)}")
        logger.info("="*50)
        
        return {
            'articles_processed': len(article_ids),
            'alerts_triggered': len(alerts)
        }
    
    def _filter_new_articles(self, news_df) -> List[Dict]:
        """Filter out articles already in database"""
        session = self.db.get_session()
        
        new_articles = []
        for _, row in news_df.iterrows():
            url = row.get('url', '')
            if not url:
                continue
            
            # Check if exists
            exists = session.query(NewsArticle).filter_by(url=url).first()
            if not exists:
                new_articles.append(row.to_dict())
        
        session.close()
        return new_articles
    
    def _analyze_articles(self, articles: List[Dict]) -> List[Dict]:
        """Analyze sentiment for articles"""
        if not articles:
            return []
        
        # Batch analysis for efficiency
        texts = [a['text'] for a in articles]
        sentiments = self.analyzer.analyze_batch(texts)
        
        # Add sentiment to articles
        for article, sentiment in zip(articles, sentiments):
            # Get detailed scores
            detailed = self.analyzer.get_detailed_scores(article['text'])
            article['sentiment'] = detailed
        
        return articles
    
    def _store_articles(self, articles: List[Dict]) -> List[int]:
        """Store articles and sentiment in database, returns article IDs"""
        session = self.db.get_session()
        stored_ids = []
        
        try:
            for article_data in articles:
                # Create article
                article = NewsArticle(
                    title=article_data.get('title', ''),
                    content=article_data['text'],
                    url=article_data['url'],
                    source=article_data.get('source', 'unknown'),
                    published_date=self._parse_date(article_data.get('date')),
                    company=self._extract_company(article_data['text']),
                    scraped_at=datetime.now(timezone.utc)
                )
                
                session.add(article)
                session.flush()  # Get article ID
                
                # Create sentiment
                sentiment_data = article_data['sentiment']
                sentiment = NewsSentiment(
                    article_id=article.id,
                    sentiment=sentiment_data['sentiment'],
                    confidence=sentiment_data['confidence'],
                    positive_score=sentiment_data.get('positive_score'),
                    negative_score=sentiment_data.get('negative_score'),
                    neutral_score=sentiment_data.get('neutral_score'),
                    model_version=sentiment_data.get('model', 'unknown'),
                    analyzed_at=datetime.now(timezone.utc)
                )
                
                session.add(sentiment)
                stored_ids.append(article.id)
            
            session.commit()
            logger.info(f"✓ Stored {len(stored_ids)} articles in database")
            
        except Exception as e:
            logger.error(f"Error storing articles: {e}")
            session.rollback()
        finally:
            session.close()
        
        return stored_ids
    
    def _check_alerts(self, article_ids: List[int]) -> List[SentimentAlert]:
        """Check if any alerts should be triggered"""
        session = self.db.get_session()
        alerts = []
        
        try:
            for article_id in article_ids:
                # Query both article and sentiment in this session
                article = session.query(NewsArticle).get(article_id)
                sentiment = session.query(NewsSentiment).filter_by(
                    article_id=article_id
                ).first()
                
                if not sentiment:
                    continue
                
                # Check thresholds
                alert = None
                
                # High confidence negative
                if (sentiment.sentiment == 'negative' and 
                    sentiment.confidence >= self.alert_thresholds['high_confidence_negative']):
                    alert = SentimentAlert(
                        article_id=article.id,
                        alert_type='major_negative',
                        severity='high',
                        message=f"High-confidence negative sentiment detected: {article.title[:100]}",
                        triggered_at=datetime.now(timezone.utc)
                    )
                
                # High confidence positive
                elif (sentiment.sentiment == 'positive' and 
                      sentiment.confidence >= self.alert_thresholds['high_confidence_positive']):
                    alert = SentimentAlert(
                        article_id=article.id,
                        alert_type='major_positive',
                        severity='medium',
                        message=f"High-confidence positive sentiment detected: {article.title[:100]}",
                        triggered_at=datetime.now(timezone.utc)
                    )
                
                if alert:
                    session.add(alert)
                    alerts.append(alert)
            
            # Check for negative batch (multiple negative articles in last hour)
            batch_alert = self._check_negative_batch(session)
            if batch_alert:
                session.add(batch_alert)
                alerts.append(batch_alert)
            
            session.commit()
            
            if alerts:
                logger.warning(f"⚠️  {len(alerts)} alert(s) triggered!")
                for alert in alerts:
                    logger.warning(f"  - {alert.alert_type}: {alert.message[:80]}...")
        
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")
            session.rollback()
        finally:
            session.close()
        
        return alerts
    
    def _check_negative_batch(self, session) -> SentimentAlert:
        """Check if too many negative articles in last hour"""
        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        
        negative_count = session.query(NewsSentiment).join(NewsArticle).filter(
            NewsArticle.scraped_at >= one_hour_ago,
            NewsSentiment.sentiment == 'negative'
        ).count()
        
        if negative_count >= self.alert_thresholds['negative_batch_threshold']:
            return SentimentAlert(
                article_id=None,  # Not tied to specific article
                alert_type='high_volatility',
                severity='critical',
                message=f"High volume of negative news detected: {negative_count} negative articles in last hour",
                triggered_at=datetime.now(timezone.utc)
            )
        
        return None
    
    @staticmethod
    def _parse_date(date_str):
        """Parse date string to datetime"""
        if not date_str:
            return None
        
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return None
    
    @staticmethod
    def _extract_company(text: str) -> str:
        """Extract company name (simple version)"""
        # Common Indian companies
        companies = [
            'Reliance', 'TCS', 'HDFC', 'Infosys', 'ICICI',
            'Wipro', 'Bharti', 'HCL', 'ITC', 'SBI', 'Adani'
        ]
        
        for company in companies:
            if company in text:
                return company
        
        return None


def main():
    """Main monitoring function"""
    logger.info("Initializing News Monitor...")
    
    # Test database connection
    db = get_db()
    if not db.test_connection():
        logger.error("Database connection failed!")
        return 1
    
    # Create tables if needed
    db.create_tables()
    
    # Run monitoring
    monitor = NewsMonitor()
    result = monitor.run_once(max_articles_per_source=50)
    
    logger.info(f"\n✓ Monitoring complete!")
    logger.info(f"Articles processed: {result['articles_processed']}")
    logger.info(f"Alerts triggered: {result['alerts_triggered']}")
    
    return 0


if __name__ == "__main__":
    exit(main())
