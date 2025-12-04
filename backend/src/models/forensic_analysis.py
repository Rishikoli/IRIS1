"""
Project IRIS - Forensic Analysis Database Models
SQLAlchemy models for forensic analysis results
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, BigInteger, ForeignKey, Index, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from src.database.base import BaseModel, JSONBType


class AnalysisStatus(enum.Enum):
    """Analysis job status"""
    CREATED = "created"
    INGESTING_DATA = "ingesting_data"
    ANALYZING = "analyzing"
    CALCULATING_RATIOS = "calculating_ratios"
    SCORING_RISK = "scoring_risk"
    VALIDATING_COMPLIANCE = "validating_compliance"
    GENERATING_REPORT = "generating_report"
    COMPLETED = "completed"
    FAILED = "failed"


class AnomalyType(enum.Enum):
    """Types of financial anomalies"""
    BENFORD_LAW_VIOLATION = "benford_law_violation"
    REVENUE_RECOGNITION = "revenue_recognition"
    EXPENSE_MANIPULATION = "expense_manipulation"
    ASSET_OVERSTATEMENT = "asset_overstatement"
    LIABILITY_UNDERSTATEMENT = "liability_understatement"
    CASH_FLOW_DIVERGENCE = "cash_flow_divergence"
    RELATED_PARTY_TRANSACTIONS = "related_party_transactions"
    INVENTORY_MANIPULATION = "inventory_manipulation"
    DEPRECIATION_ANOMALY = "depreciation_anomaly"
    WORKING_CAPITAL_ANOMALY = "working_capital_anomaly"


class SeverityLevel(enum.Enum):
    """Severity levels for anomalies and risks"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AnalysisJob(BaseModel):
    """Analysis job tracking model"""

    __tablename__ = "analysis_jobs"

    # Job identification
    job_id = Column(String(36), unique=True, index=True, nullable=False)  # UUID
    job_type = Column(String(50), nullable=False, index=True)  # FORENSIC, SENTIMENT, PEER_BENCHMARK
    
    # Job parameters
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    analysis_type = Column(String(50), default="comprehensive")  # comprehensive, quick, custom
    
    # Job status
    status = Column(Enum(AnalysisStatus), default=AnalysisStatus.CREATED, index=True)
    progress_percentage = Column(Integer, default=0)
    current_step = Column(String(100))
    
    # Timing information
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    estimated_completion = Column(DateTime)
    
    # Results
    result_summary = Column(JSONBType)
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # Relationships
    company = relationship("Company")
    forensic_analysis = relationship("ForensicAnalysis", back_populates="job", uselist=False)

    # Indexes
    __table_args__ = (
        Index('idx_job_company_status', 'company_id', 'status'),
        Index('idx_job_type_created', 'job_type', 'created_at'),
    )

    def __repr__(self):
        return f"<AnalysisJob(id={self.id}, job_id={self.job_id}, status={self.status.value})>"


class ForensicAnalysis(BaseModel):
    """Forensic analysis results model"""

    __tablename__ = "forensic_analysis"

    # Foreign keys
    job_id = Column(Integer, ForeignKey("analysis_jobs.id"), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    
    # Analysis period
    analysis_start_date = Column(DateTime, nullable=False)
    analysis_end_date = Column(DateTime, nullable=False)
    
    # Benford's Law Analysis
    benford_chi_square = Column(Float)
    benford_p_value = Column(Float)
    benford_passes_test = Column(Boolean)
    benford_suspicious_digits = Column(JSONBType)  # List of suspicious digit patterns
    
    # Altman Z-Score
    z_score = Column(Float)
    z_score_category = Column(String(20))  # SAFE, GREY, DISTRESS
    z_score_components = Column(JSONBType)  # Individual component values
    
    # Beneish M-Score
    m_score = Column(Float)
    m_score_probability = Column(Float)  # Probability of manipulation
    m_score_variables = Column(JSONBType)  # DSRI, GMI, AQI, SGI, DEPI, SGAI, LVGI, TATA
    
    # Financial Health Indicators
    working_capital_trend = Column(String(20))  # IMPROVING, STABLE, DETERIORATING
    cash_conversion_cycle = Column(Float)
    days_sales_outstanding = Column(Float)
    days_inventory_outstanding = Column(Float)
    days_payable_outstanding = Column(Float)
    
    # Revenue Quality Analysis
    revenue_growth_rate = Column(Float)
    revenue_volatility = Column(Float)
    revenue_seasonality_index = Column(Float)
    accounts_receivable_growth = Column(Float)
    
    # Expense Analysis
    expense_growth_rate = Column(Float)
    expense_ratio_trend = Column(String(20))
    unusual_expense_items = Column(JSONBType)
    
    # Cash Flow Analysis
    operating_cash_flow_ratio = Column(Float)
    free_cash_flow_margin = Column(Float)
    cash_flow_earnings_ratio = Column(Float)
    
    # Overall Assessment
    overall_risk_score = Column(Float)  # 0-100 scale
    manipulation_probability = Column(Float)  # 0-1 probability
    financial_health_grade = Column(String(2))  # A+, A, B+, B, C+, C, D
    
    # Analyst Notes
    key_findings = Column(Text)
    red_flags = Column(JSONBType)  # List of identified red flags
    recommendations = Column(Text)
    
    # Relationships
    job = relationship("AnalysisJob", back_populates="forensic_analysis")
    company = relationship("Company", back_populates="forensic_analyses")
    anomalies = relationship("FinancialAnomaly", back_populates="forensic_analysis", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_forensic_company_date', 'company_id', 'analysis_end_date'),
        Index('idx_forensic_risk_score', 'overall_risk_score'),
        Index('idx_forensic_m_score', 'm_score'),
    )

    def __repr__(self):
        return f"<ForensicAnalysis(id={self.id}, company_id={self.company_id}, risk_score={self.overall_risk_score})>"


class FinancialAnomaly(BaseModel):
    """Individual financial anomalies detected"""

    __tablename__ = "financial_anomalies"

    # Foreign keys
    forensic_analysis_id = Column(Integer, ForeignKey("forensic_analysis.id"), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    
    # Anomaly details
    anomaly_type = Column(Enum(AnomalyType), nullable=False, index=True)
    severity = Column(Enum(SeverityLevel), nullable=False, index=True)
    confidence_score = Column(Float)  # 0-1 confidence in detection
    
    # Description and evidence
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    evidence = Column(JSONBType)  # Supporting data and calculations
    affected_periods = Column(JSONBType)  # List of affected reporting periods
    
    # Financial impact
    estimated_impact_amount = Column(BigInteger)  # In lakhs
    impact_percentage = Column(Float)  # % of revenue/assets affected
    
    # Detection metadata
    detection_method = Column(String(100))  # benford_law, ratio_analysis, trend_analysis
    detection_date = Column(DateTime, default=datetime.utcnow)
    
    # Status
    is_confirmed = Column(Boolean, default=False)
    is_resolved = Column(Boolean, default=False)
    analyst_notes = Column(Text)
    
    # Relationships
    forensic_analysis = relationship("ForensicAnalysis", back_populates="anomalies")
    company = relationship("Company")

    # Indexes
    __table_args__ = (
        Index('idx_anomaly_type_severity', 'anomaly_type', 'severity'),
        Index('idx_anomaly_company_date', 'company_id', 'detection_date'),
        Index('idx_anomaly_confidence', 'confidence_score'),
    )

    def __repr__(self):
        return f"<FinancialAnomaly(id={self.id}, type={self.anomaly_type.value}, severity={self.severity.value})>"
