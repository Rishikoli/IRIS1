"""
Project IRIS - Company Database Models
SQLAlchemy models for company-related data
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, BigInteger, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import BaseModel, JSONBType


class Company(BaseModel):
    """Company master data model"""

    __tablename__ = "companies"

    # Basic company information
    cin = Column(String(21), unique=True, index=True, nullable=False)  # Company Identification Number
    name = Column(String(500), nullable=False, index=True)
    sector = Column(String(100), index=True)
    industry = Column(String(100), index=True)
    incorporation_date = Column(DateTime)

    # Contact information
    registered_address = Column(Text)
    email = Column(String(255))
    phone = Column(String(20))
    website = Column(String(255))

    # Financial information
    face_value = Column(Float)  # Face value per share
    paid_up_capital = Column(BigInteger)  # Total paid-up capital
    market_cap = Column(BigInteger)  # Current market capitalization
    currency = Column(String(3), default="INR")

    # Stock exchange information
    nse_symbol = Column(String(20), index=True)
    bse_symbol = Column(String(20), index=True)
    isin = Column(String(12), unique=True, index=True)

    # Status flags
    is_active = Column(Boolean, default=True, index=True)
    is_listed = Column(Boolean, default=True, index=True)
    is_suspended = Column(Boolean, default=False)

    # Metadata
    data_source = Column(String(50), default="indian_api")  # indian_api, nse, bse, manual
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    api_response = Column(JSONBType)  # Raw API response data

    # Relationships
    financial_statements = relationship("FinancialStatement", back_populates="company", cascade="all, delete-orphan")
    forensic_analyses = relationship("ForensicAnalysis", back_populates="company", cascade="all, delete-orphan")
    risk_scores = relationship("RiskScore", back_populates="company", cascade="all, delete-orphan")
    compliance_records = relationship("ComplianceValidation", back_populates="company", cascade="all, delete-orphan")
    peer_benchmarks = relationship("PeerBenchmark", back_populates="company", cascade="all, delete-orphan")

    # Indexes for performance
    __table_args__ = (
        Index('idx_company_sector_industry', 'sector', 'industry'),
        Index('idx_company_symbols', 'nse_symbol', 'bse_symbol'),
        Index('idx_company_active_listed', 'is_active', 'is_listed'),
    )

    def __repr__(self):
        return f"<Company(id={self.id}, cin={self.cin}, name={self.name[:50]}...)>"


class CompanyAlias(BaseModel):
    """Alternative names and tickers for companies"""

    __tablename__ = "company_aliases"

    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    alias_type = Column(String(20), nullable=False)  # old_name, ticker, acronym, etc.
    alias_value = Column(String(100), nullable=False)
    is_primary = Column(Boolean, default=False)

    # Relationship
    company = relationship("Company", back_populates="aliases")

    # Indexes
    __table_args__ = (
        Index('idx_company_alias_value', 'alias_value'),
        Index('idx_company_alias_type', 'alias_type'),
    )

    def __repr__(self):
        return f"<CompanyAlias(id={self.id}, company_id={self.company_id}, type={self.alias_type}, value={self.alias_value})>"


# Add relationship to Company model
Company.aliases = relationship("CompanyAlias", back_populates="company", cascade="all, delete-orphan")
