"""
Project IRIS - Compliance Database Models
SQLAlchemy models for compliance validation and regulatory monitoring
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, ForeignKey, Index, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from src.database.base import BaseModel, JSONBType


class ComplianceFramework(enum.Enum):
    """Compliance frameworks"""
    IND_AS = "ind_as"
    SEBI_LODR = "sebi_lodr"
    COMPANIES_ACT = "companies_act"
    RBI_GUIDELINES = "rbi_guidelines"
    FEMA = "fema"
    INCOME_TAX = "income_tax"


class ViolationType(enum.Enum):
    """Types of compliance violations"""
    FILING_DELAY = "filing_delay"
    DISCLOSURE_MISSING = "disclosure_missing"
    ACCOUNTING_STANDARD = "accounting_standard"
    GOVERNANCE_FAILURE = "governance_failure"
    RELATED_PARTY_TRANSACTION = "related_party_transaction"
    INSIDER_TRADING = "insider_trading"
    PRICE_MANIPULATION = "price_manipulation"
    AUDIT_QUALIFICATION = "audit_qualification"


class ComplianceStatus(enum.Enum):
    """Compliance status"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    UNDER_REVIEW = "under_review"
    NOT_APPLICABLE = "not_applicable"


class ComplianceValidation(BaseModel):
    """Compliance validation results model"""

    __tablename__ = "compliance_validation"

    # Foreign keys
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    
    # Validation details
    validation_date = Column(DateTime, default=datetime.utcnow, index=True)
    framework = Column(Enum(ComplianceFramework), nullable=False, index=True)
    regulation_code = Column(String(50), nullable=False)  # e.g., "LODR_31", "IND_AS_1"
    regulation_title = Column(String(200), nullable=False)
    
    # Assessment period
    assessment_period_start = Column(DateTime)
    assessment_period_end = Column(DateTime)
    
    # Compliance status
    status = Column(Enum(ComplianceStatus), nullable=False, index=True)
    compliance_score = Column(Float)  # 0-100 compliance score
    
    # Violation details
    violation_type = Column(Enum(ViolationType), index=True)
    violation_severity = Column(String(20))  # LOW, MEDIUM, HIGH, CRITICAL
    violation_description = Column(Text)
    
    # Filing information
    required_filing_date = Column(DateTime)
    actual_filing_date = Column(DateTime)
    days_delayed = Column(Integer)
    
    # Financial impact
    penalty_amount = Column(Float)
    estimated_impact = Column(Float)
    
    # Evidence and documentation
    evidence = Column(JSONBType)  # Supporting evidence
    source_documents = Column(JSONBType)  # List of source documents
    
    # Remediation
    remediation_required = Column(Boolean, default=False)
    remediation_deadline = Column(DateTime)
    remediation_status = Column(String(50))
    remediation_notes = Column(Text)
    
    # Analyst assessment
    analyst_notes = Column(Text)
    is_material = Column(Boolean, default=False)
    risk_rating = Column(String(20))
    
    # Relationships
    company = relationship("Company", back_populates="compliance_records")

    # Indexes
    __table_args__ = (
        Index('idx_compliance_company_framework', 'company_id', 'framework'),
        Index('idx_compliance_status_date', 'status', 'validation_date'),
        Index('idx_compliance_violation_type', 'violation_type'),
    )

    def __repr__(self):
        return f"<ComplianceValidation(id={self.id}, company_id={self.company_id}, framework={self.framework.value}, status={self.status.value})>"


class RegulatoryAction(BaseModel):
    """Regulatory actions and enforcement"""

    __tablename__ = "regulatory_actions"

    # Foreign key
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    
    # Action details
    action_date = Column(DateTime, nullable=False, index=True)
    regulator = Column(String(50), nullable=False, index=True)  # SEBI, RBI, MCA, etc.
    action_type = Column(String(50), nullable=False, index=True)  # SCN, Adjudication, Penalty, etc.
    
    # Case information
    case_number = Column(String(100))
    order_number = Column(String(100))
    action_title = Column(String(500), nullable=False)
    
    # Violation details
    violation_period_start = Column(DateTime)
    violation_period_end = Column(DateTime)
    violation_description = Column(Text)
    regulations_violated = Column(JSONBType)  # List of violated regulations
    
    # Financial impact
    penalty_amount = Column(Float)
    disgorgement_amount = Column(Float)
    total_financial_impact = Column(Float)
    
    # Action status
    action_status = Column(String(50), index=True)  # PENDING, SETTLED, APPEALED, CLOSED
    is_settled = Column(Boolean, default=False)
    settlement_amount = Column(Float)
    
    # Appeal information
    is_appealed = Column(Boolean, default=False)
    appeal_status = Column(String(50))
    appeal_outcome = Column(String(100))
    
    # Documentation
    order_document_url = Column(String(500))
    press_release_url = Column(String(500))
    
    # Impact assessment
    reputational_impact = Column(String(20))  # LOW, MEDIUM, HIGH
    market_impact = Column(Float)  # Stock price impact %
    
    # Relationships
    company = relationship("Company")

    # Indexes
    __table_args__ = (
        Index('idx_regulatory_company_date', 'company_id', 'action_date'),
        Index('idx_regulatory_type_status', 'action_type', 'action_status'),
        Index('idx_regulatory_regulator', 'regulator'),
    )

    def __repr__(self):
        return f"<RegulatoryAction(id={self.id}, company_id={self.company_id}, regulator={self.regulator}, type={self.action_type})>"


class ComplianceDeadline(BaseModel):
    """Upcoming compliance deadlines"""

    __tablename__ = "compliance_deadlines"

    # Foreign key
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    
    # Deadline details
    deadline_date = Column(DateTime, nullable=False, index=True)
    requirement_type = Column(String(100), nullable=False, index=True)
    requirement_description = Column(Text, nullable=False)
    
    # Regulatory framework
    framework = Column(Enum(ComplianceFramework), nullable=False)
    regulation_reference = Column(String(100))
    
    # Filing information
    filing_frequency = Column(String(20))  # ANNUAL, QUARTERLY, MONTHLY, etc.
    fiscal_year = Column(Integer)
    fiscal_quarter = Column(Integer)
    
    # Status tracking
    is_completed = Column(Boolean, default=False, index=True)
    completion_date = Column(DateTime)
    filing_reference = Column(String(100))
    
    # Risk assessment
    criticality = Column(String(20), index=True)  # LOW, MEDIUM, HIGH, CRITICAL
    penalty_for_delay = Column(Float)
    
    # Notifications
    reminder_sent = Column(Boolean, default=False)
    escalation_sent = Column(Boolean, default=False)
    
    # Relationships
    company = relationship("Company")

    # Indexes
    __table_args__ = (
        Index('idx_deadline_company_date', 'company_id', 'deadline_date'),
        Index('idx_deadline_type_completed', 'requirement_type', 'is_completed'),
        Index('idx_deadline_criticality', 'criticality'),
    )

    def __repr__(self):
        return f"<ComplianceDeadline(id={self.id}, company_id={self.company_id}, deadline={self.deadline_date}, type={self.requirement_type})>"
