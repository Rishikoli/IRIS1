"""
Project IRIS - Risk Scoring Database Models
SQLAlchemy models for risk assessment and scoring
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, ForeignKey, Index, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from src.database.base import BaseModel, JSONBType


class RiskCategory(enum.Enum):
    """Risk assessment categories"""
    FINANCIAL_HEALTH = "financial_health"
    EARNINGS_QUALITY = "earnings_quality"
    DISCLOSURE_QUALITY = "disclosure_quality"
    GOVERNANCE = "governance"
    MARKET_RISK = "market_risk"
    OPERATIONAL_RISK = "operational_risk"
    REGULATORY_RISK = "regulatory_risk"
    LIQUIDITY_RISK = "liquidity_risk"


class RiskLevel(enum.Enum):
    """Risk levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskScore(BaseModel):
    """Risk scoring results model"""

    __tablename__ = "risk_scores"

    # Foreign keys
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    forensic_analysis_id = Column(Integer, ForeignKey("forensic_analysis.id"), index=True)
    
    # Scoring period
    scoring_date = Column(DateTime, default=datetime.utcnow, index=True)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Overall Risk Score (0-100)
    overall_score = Column(Float, nullable=False, index=True)
    overall_level = Column(Enum(RiskLevel), nullable=False, index=True)
    
    # Category-wise Scores (0-100 each)
    financial_health_score = Column(Float)
    earnings_quality_score = Column(Float)
    disclosure_quality_score = Column(Float)
    governance_score = Column(Float)
    market_risk_score = Column(Float)
    operational_risk_score = Column(Float)
    regulatory_risk_score = Column(Float)
    liquidity_risk_score = Column(Float)
    
    # Category-wise Levels
    financial_health_level = Column(Enum(RiskLevel))
    earnings_quality_level = Column(Enum(RiskLevel))
    disclosure_quality_level = Column(Enum(RiskLevel))
    governance_level = Column(Enum(RiskLevel))
    market_risk_level = Column(Enum(RiskLevel))
    operational_risk_level = Column(Enum(RiskLevel))
    regulatory_risk_level = Column(Enum(RiskLevel))
    liquidity_risk_level = Column(Enum(RiskLevel))
    
    # Scoring methodology
    scoring_model_version = Column(String(20), default="1.0")
    weights_used = Column(JSONBType)  # Category weights used in calculation
    
    # Key Risk Factors
    top_risk_factors = Column(JSONBType)  # List of top risk contributors
    risk_factor_scores = Column(JSONBType)  # Detailed factor-wise scores
    
    # Trend Analysis
    score_trend = Column(String(20))  # IMPROVING, STABLE, DETERIORATING
    previous_score = Column(Float)
    score_change = Column(Float)
    score_volatility = Column(Float)
    
    # Peer Comparison
    peer_group_median = Column(Float)
    peer_percentile = Column(Float)
    industry_median = Column(Float)
    industry_percentile = Column(Float)
    
    # Confidence and Quality
    confidence_level = Column(Float)  # 0-1 confidence in the score
    data_quality_score = Column(Float)  # 0-1 quality of underlying data
    
    # Alerts and Flags
    critical_alerts = Column(JSONBType)  # List of critical risk alerts
    warning_flags = Column(JSONBType)  # List of warning flags
    
    # Analyst Assessment
    analyst_override = Column(Boolean, default=False)
    analyst_score = Column(Float)  # Manual override score
    analyst_notes = Column(Text)
    
    # Relationships
    company = relationship("Company", back_populates="risk_scores")
    forensic_analysis = relationship("ForensicAnalysis")
    risk_factors = relationship("RiskFactor", back_populates="risk_score", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_risk_company_date', 'company_id', 'scoring_date'),
        Index('idx_risk_overall_score', 'overall_score'),
        Index('idx_risk_level', 'overall_level'),
    )

    def __repr__(self):
        return f"<RiskScore(id={self.id}, company_id={self.company_id}, score={self.overall_score}, level={self.overall_level.value})>"


class RiskFactor(BaseModel):
    """Individual risk factors contributing to overall score"""

    __tablename__ = "risk_factors"

    # Foreign key
    risk_score_id = Column(Integer, ForeignKey("risk_scores.id"), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    
    # Factor details
    category = Column(Enum(RiskCategory), nullable=False, index=True)
    factor_name = Column(String(100), nullable=False, index=True)
    factor_code = Column(String(20), nullable=False)  # Unique identifier
    
    # Scoring
    raw_value = Column(Float)  # Original metric value
    normalized_score = Column(Float)  # 0-100 normalized score
    weight = Column(Float)  # Weight in category calculation
    contribution = Column(Float)  # Weighted contribution to category score
    
    # Thresholds
    low_threshold = Column(Float)
    medium_threshold = Column(Float)
    high_threshold = Column(Float)
    critical_threshold = Column(Float)
    
    # Assessment
    risk_level = Column(Enum(RiskLevel), nullable=False)
    is_outlier = Column(Boolean, default=False)
    
    # Description and context
    description = Column(Text)
    calculation_method = Column(Text)
    data_source = Column(String(100))
    
    # Trend information
    previous_value = Column(Float)
    change_percentage = Column(Float)
    trend_direction = Column(String(20))  # UP, DOWN, STABLE
    
    # Relationships
    risk_score = relationship("RiskScore", back_populates="risk_factors")
    company = relationship("Company")

    # Indexes
    __table_args__ = (
        Index('idx_risk_factor_category', 'category', 'factor_name'),
        Index('idx_risk_factor_score', 'normalized_score'),
        Index('idx_risk_factor_level', 'risk_level'),
    )

    def __repr__(self):
        return f"<RiskFactor(id={self.id}, name={self.factor_name}, score={self.normalized_score}, level={self.risk_level.value})>"


class RiskAlert(BaseModel):
    """Risk alerts and notifications"""

    __tablename__ = "risk_alerts"

    # Foreign keys
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    risk_score_id = Column(Integer, ForeignKey("risk_scores.id"), index=True)
    
    # Alert details
    alert_type = Column(String(50), nullable=False, index=True)  # SCORE_INCREASE, NEW_CRITICAL, TREND_CHANGE
    severity = Column(Enum(RiskLevel), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    
    # Trigger information
    trigger_value = Column(Float)
    threshold_value = Column(Float)
    trigger_factor = Column(String(100))
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String(100))
    acknowledged_at = Column(DateTime)
    
    # Resolution
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)
    resolution_notes = Column(Text)
    
    # Relationships
    company = relationship("Company")
    risk_score = relationship("RiskScore")

    # Indexes
    __table_args__ = (
        Index('idx_alert_company_active', 'company_id', 'is_active'),
        Index('idx_alert_severity_date', 'severity', 'created_at'),
        Index('idx_alert_type', 'alert_type'),
    )

    def __repr__(self):
        return f"<RiskAlert(id={self.id}, company_id={self.company_id}, type={self.alert_type}, severity={self.severity.value})>"
