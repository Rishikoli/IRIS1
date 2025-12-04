"""
Project IRIS - Additional Database Models
SQLAlchemy models for reports, peer benchmarking, and sentiment analysis
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, ForeignKey, Index, Enum, BigInteger
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from src.database.base import BaseModel, JSONBType


class ReportType(enum.Enum):
    """Types of generated reports"""
    FORENSIC_ANALYSIS = "forensic_analysis"
    RISK_ASSESSMENT = "risk_assessment"
    COMPLIANCE_SUMMARY = "compliance_summary"
    PEER_BENCHMARK = "peer_benchmark"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    EXECUTIVE_SUMMARY = "executive_summary"


class ReportFormat(enum.Enum):
    """Report output formats"""
    PDF = "pdf"
    EXCEL = "excel"
    JSON = "json"
    HTML = "html"


class Report(BaseModel):
    """Generated reports model"""

    __tablename__ = "reports"

    # Report identification
    report_id = Column(String(36), unique=True, index=True, nullable=False)  # UUID
    
    # Foreign keys
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("analysis_jobs.id"), index=True)
    
    # Report metadata
    report_type = Column(Enum(ReportType), nullable=False, index=True)
    report_format = Column(Enum(ReportFormat), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    
    # Report period
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Generation details
    generated_by = Column(String(100))  # User or system
    generation_time_ms = Column(Integer)
    template_version = Column(String(20))
    
    # File information
    file_path = Column(String(1000))
    file_size_bytes = Column(BigInteger)
    file_hash = Column(String(64))
    
    # Content summary
    page_count = Column(Integer)
    section_count = Column(Integer)
    chart_count = Column(Integer)
    table_count = Column(Integer)
    
    # Report data
    executive_summary = Column(Text)
    key_findings = Column(JSONBType)
    recommendations = Column(JSONBType)
    data_sources = Column(JSONBType)
    
    # Access control
    is_confidential = Column(Boolean, default=True)
    access_level = Column(String(20), default="INTERNAL")  # PUBLIC, INTERNAL, RESTRICTED
    
    # Usage tracking
    download_count = Column(Integer, default=0)
    last_accessed = Column(DateTime)
    
    # Relationships
    company = relationship("Company")
    job = relationship("AnalysisJob")

    # Indexes
    __table_args__ = (
        Index('idx_report_company_type', 'company_id', 'report_type'),
        Index('idx_report_period', 'period_start', 'period_end'),
        Index('idx_report_generated', 'created_at'),
    )

    def __repr__(self):
        return f"<Report(id={self.id}, report_id={self.report_id}, type={self.report_type.value})>"


class PeerBenchmark(BaseModel):
    """Peer benchmarking results"""

    __tablename__ = "peer_benchmarks"

    # Foreign keys
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    
    # Benchmarking period
    benchmark_date = Column(DateTime, default=datetime.utcnow, index=True)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Peer group information
    peer_group_size = Column(Integer)
    peer_selection_criteria = Column(JSONBType)
    peer_companies = Column(JSONBType)  # List of peer company IDs and names
    
    # Benchmark metrics
    metric_name = Column(String(100), nullable=False, index=True)
    metric_category = Column(String(50), index=True)  # profitability, liquidity, leverage, etc.
    
    # Company performance
    company_value = Column(Float, nullable=False)
    company_rank = Column(Integer)
    company_percentile = Column(Float)
    
    # Peer statistics
    peer_median = Column(Float)
    peer_mean = Column(Float)
    peer_std_dev = Column(Float)
    peer_min = Column(Float)
    peer_max = Column(Float)
    peer_q1 = Column(Float)  # 25th percentile
    peer_q3 = Column(Float)  # 75th percentile
    
    # Statistical analysis
    z_score = Column(Float)
    is_outlier = Column(Boolean, default=False)
    outlier_type = Column(String(20))  # HIGH, LOW
    
    # Performance assessment
    performance_vs_peers = Column(String(20))  # OUTPERFORMING, INLINE, UNDERPERFORMING
    performance_score = Column(Float)  # 0-100 relative performance score
    
    # Trend analysis
    trend_direction = Column(String(20))  # IMPROVING, STABLE, DETERIORATING
    trend_strength = Column(Float)
    
    # Relationships
    company = relationship("Company", back_populates="peer_benchmarks")

    # Indexes
    __table_args__ = (
        Index('idx_benchmark_company_metric', 'company_id', 'metric_name'),
        Index('idx_benchmark_date_category', 'benchmark_date', 'metric_category'),
        Index('idx_benchmark_percentile', 'company_percentile'),
    )

    def __repr__(self):
        return f"<PeerBenchmark(id={self.id}, company_id={self.company_id}, metric={self.metric_name}, percentile={self.company_percentile})>"


class SentimentAnalysis(BaseModel):
    """Market sentiment analysis results"""

    __tablename__ = "sentiment_analysis"

    # Foreign keys
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    
    # Analysis period
    analysis_date = Column(DateTime, default=datetime.utcnow, index=True)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Sentiment sources
    news_sentiment_score = Column(Float)  # -1 to +1
    social_sentiment_score = Column(Float)
    analyst_sentiment_score = Column(Float)
    overall_sentiment_score = Column(Float)
    
    # Sentiment classification
    sentiment_label = Column(String(20), index=True)  # VERY_NEGATIVE, NEGATIVE, NEUTRAL, POSITIVE, VERY_POSITIVE
    confidence_level = Column(Float)  # 0-1 confidence in classification
    
    # Volume metrics
    news_article_count = Column(Integer)
    social_mention_count = Column(Integer)
    analyst_report_count = Column(Integer)
    total_mention_count = Column(Integer)
    
    # Trend analysis
    sentiment_trend = Column(String(20))  # IMPROVING, STABLE, DETERIORATING
    trend_strength = Column(Float)
    volatility_score = Column(Float)
    
    # Key topics and themes
    positive_themes = Column(JSONBType)
    negative_themes = Column(JSONBType)
    trending_keywords = Column(JSONBType)
    
    # Geographic distribution
    sentiment_by_region = Column(JSONBType)
    
    # Impact assessment
    estimated_stock_impact = Column(Float)  # Estimated % impact on stock price
    market_correlation = Column(Float)  # Correlation with market sentiment
    
    # Relationships
    company = relationship("Company")

    # Indexes
    __table_args__ = (
        Index('idx_sentiment_company_date', 'company_id', 'analysis_date'),
        Index('idx_sentiment_score_label', 'overall_sentiment_score', 'sentiment_label'),
        Index('idx_sentiment_trend', 'sentiment_trend'),
    )

    def __repr__(self):
        return f"<SentimentAnalysis(id={self.id}, company_id={self.company_id}, score={self.overall_sentiment_score}, label={self.sentiment_label})>"


class GoogleTrendsData(BaseModel):
    """Google Trends data for companies"""

    __tablename__ = "google_trends_data"

    # Foreign keys
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    
    # Search data
    search_date = Column(DateTime, default=datetime.utcnow, index=True)
    keyword = Column(String(100), nullable=False, index=True)
    search_volume = Column(Integer)
    interest_score = Column(Float)  # 0-100 Google Trends interest score
    
    # Geographic data
    country = Column(String(2), default="IN")  # ISO country code
    region = Column(String(100))
    city = Column(String(100))
    
    # Trend analysis
    trend_direction = Column(String(20))  # UP, DOWN, STABLE
    change_percentage = Column(Float)
    volatility = Column(Float)
    
    # Related queries
    related_queries = Column(JSONBType)
    rising_queries = Column(JSONBType)
    
    # Context flags
    is_crisis_related = Column(Boolean, default=False)
    is_positive_news = Column(Boolean, default=False)
    is_negative_news = Column(Boolean, default=False)
    
    # Relationships
    company = relationship("Company")

    # Indexes
    __table_args__ = (
        Index('idx_trends_company_keyword', 'company_id', 'keyword'),
        Index('idx_trends_date_score', 'search_date', 'interest_score'),
        Index('idx_trends_region', 'country', 'region'),
    )

    def __repr__(self):
        return f"<GoogleTrendsData(id={self.id}, company_id={self.company_id}, keyword={self.keyword}, score={self.interest_score})>"
