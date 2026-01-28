"""
Database Connection and Models for News Monitoring

Handles PostgreSQL connection and ORM models.
"""

import os
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()


class NewsArticle(Base):
    """News article model"""
    __tablename__ = 'news_articles'
    
    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    url = Column(Text, unique=True, nullable=False)
    source = Column(String(50), nullable=False)
    published_date = Column(DateTime)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    company = Column(String(100))
    sector = Column(String(50))
    
    # Relationships
    sentiment = relationship("NewsSentiment", back_populates="article", uselist=False)
    alerts = relationship("SentimentAlert", back_populates="article")
    
    def __repr__(self):
        return f"<NewsArticle(id={self.id}, title='{self.title[:50]}...', source='{self.source}')>"


class NewsSentiment(Base):
    """Sentiment analysis results model"""
    __tablename__ = 'news_sentiment'
    
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('news_articles.id'), nullable=False, unique=True)
    
    sentiment = Column(String(20), nullable=False)
    confidence = Column(Float, nullable=False)
    
    positive_score = Column(Float)
    negative_score = Column(Float)
    neutral_score = Column(Float)
    
    model_version = Column(String(50), default='ProsusAI/finbert')
    analyzed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    article = relationship("NewsArticle", back_populates="sentiment")
    
    def __repr__(self):
        return f"<NewsSentiment(article_id={self.article_id}, sentiment='{self.sentiment}', confidence={self.confidence:.2f})>"


class SentimentAlert(Base):
    """Sentiment alerts model"""
    __tablename__ = 'sentiment_alerts'
    
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('news_articles.id'), nullable=False)
    
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    
    triggered_at = Column(DateTime, default=datetime.utcnow)
    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime)
    acknowledged_by = Column(String(100))
    
    # Relationships
    article = relationship("NewsArticle", back_populates="alerts")
    
    def __repr__(self):
        return f"<SentimentAlert(id={self.id}, type='{self.alert_type}', severity='{self.severity}')>"


class Database:
    """Database connection manager"""
    
    def __init__(self, db_url: Optional[str] = None):
        """
        Initialize database connection
        
        Args:
            db_url: PostgreSQL connection URL
                   Format: postgresql://user:password@localhost:5432/dbname
                   If None, reads from environment variable DATABASE_URL
        """
        self.db_url = db_url or os.getenv(
            'DATABASE_URL',
            'postgresql://postgres:postgres@localhost:5432/iris_monitoring'
        )
        
        logger.info(f"Connecting to database...")
        self.engine = create_engine(self.db_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
    def create_tables(self):
        """Create all tables"""
        logger.info("Creating database tables...")
        Base.metadata.create_all(self.engine)
        logger.info("✓ Tables created successfully")
    
    def get_session(self):
        """Get a new database session"""
        return self.SessionLocal()
    
    def test_connection(self):
        """Test database connection"""
        try:
            from sqlalchemy import text
            session = self.get_session()
            session.execute(text("SELECT 1"))
            session.close()
            logger.info("✓ Database connection successful")
            return True
        except Exception as e:
            logger.error(f"✗ Database connection failed: {e}")
            return False


# Singleton instance
_db_instance = None

def get_db() -> Database:
    """Get database instance (singleton)"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance


if __name__ == "__main__":
    # Test database connection and create tables
    db = get_db()
    
    if db.test_connection():
        db.create_tables()
        print("\n✓ Database setup complete!")
    else:
        print("\n✗ Database setup failed!")
        print("\nMake sure PostgreSQL is running and connection details are correct.")
        print("Set DATABASE_URL environment variable or update db_url in Database()")
