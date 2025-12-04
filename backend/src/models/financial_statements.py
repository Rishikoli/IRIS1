"""
Project IRIS - Financial Statements Database Models
SQLAlchemy models for financial data storage
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, BigInteger, ForeignKey, Index, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from src.database.base import BaseModel, JSONBType


class StatementType(enum.Enum):
    """Financial statement types"""
    BALANCE_SHEET = "balance_sheet"
    INCOME_STATEMENT = "income_statement"
    CASH_FLOW = "cash_flow"
    EQUITY_STATEMENT = "equity_statement"


class ReportingPeriod(enum.Enum):
    """Financial reporting periods"""
    ANNUAL = "annual"
    QUARTERLY = "quarterly"
    HALF_YEARLY = "half_yearly"


class FinancialStatement(BaseModel):
    """Financial statements data model"""

    __tablename__ = "financial_statements"

    # Foreign key to company
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)

    # Statement metadata
    statement_type = Column(Enum(StatementType), nullable=False, index=True)
    period_type = Column(Enum(ReportingPeriod), nullable=False, index=True)
    fiscal_year = Column(Integer, nullable=False, index=True)
    fiscal_quarter = Column(Integer)  # 1, 2, 3, 4 for quarterly reports
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False, index=True)

    # Filing information
    filing_date = Column(DateTime)
    source = Column(String(50), default="indian_api")  # indian_api, nse, bse, manual
    document_url = Column(String(500))
    
    # Currency and units
    currency = Column(String(3), default="INR")
    units = Column(String(20), default="lakhs")  # lakhs, crores, thousands

    # Balance Sheet Items (in lakhs)
    total_assets = Column(BigInteger)
    current_assets = Column(BigInteger)
    non_current_assets = Column(BigInteger)
    cash_and_equivalents = Column(BigInteger)
    inventory = Column(BigInteger)
    trade_receivables = Column(BigInteger)
    
    total_liabilities = Column(BigInteger)
    current_liabilities = Column(BigInteger)
    non_current_liabilities = Column(BigInteger)
    total_debt = Column(BigInteger)
    short_term_debt = Column(BigInteger)
    long_term_debt = Column(BigInteger)
    trade_payables = Column(BigInteger)
    
    total_equity = Column(BigInteger)
    share_capital = Column(BigInteger)
    reserves_surplus = Column(BigInteger)

    # Income Statement Items (in lakhs)
    total_revenue = Column(BigInteger)
    operating_revenue = Column(BigInteger)
    other_income = Column(BigInteger)
    
    total_expenses = Column(BigInteger)
    cost_of_goods_sold = Column(BigInteger)
    operating_expenses = Column(BigInteger)
    employee_expenses = Column(BigInteger)
    depreciation = Column(BigInteger)
    interest_expense = Column(BigInteger)
    tax_expense = Column(BigInteger)
    
    gross_profit = Column(BigInteger)
    operating_profit = Column(BigInteger)
    ebitda = Column(BigInteger)
    ebit = Column(BigInteger)
    profit_before_tax = Column(BigInteger)
    net_profit = Column(BigInteger)
    
    # Per share data
    earnings_per_share = Column(Float)
    book_value_per_share = Column(Float)
    
    # Cash Flow Items (in lakhs)
    operating_cash_flow = Column(BigInteger)
    investing_cash_flow = Column(BigInteger)
    financing_cash_flow = Column(BigInteger)
    net_cash_flow = Column(BigInteger)
    free_cash_flow = Column(BigInteger)

    # Ratios (calculated)
    current_ratio = Column(Float)
    quick_ratio = Column(Float)
    debt_to_equity = Column(Float)
    return_on_equity = Column(Float)
    return_on_assets = Column(Float)
    gross_margin = Column(Float)
    operating_margin = Column(Float)
    net_margin = Column(Float)

    # Data quality flags
    is_audited = Column(Boolean, default=False)
    is_consolidated = Column(Boolean, default=True)
    has_exceptional_items = Column(Boolean, default=False)
    
    # Raw data storage
    raw_data = Column(JSONBType)  # Original API response
    line_items = Column(JSONBType)  # Detailed line items
    notes = Column(Text)  # Additional notes or disclosures

    # Relationships
    company = relationship("Company", back_populates="financial_statements")

    # Indexes for performance
    __table_args__ = (
        Index('idx_financial_company_period', 'company_id', 'period_end'),
        Index('idx_financial_type_period', 'statement_type', 'period_type'),
        Index('idx_financial_fiscal_year', 'fiscal_year', 'fiscal_quarter'),
    )

    def __repr__(self):
        return f"<FinancialStatement(id={self.id}, company_id={self.company_id}, type={self.statement_type.value}, period_end={self.period_end})>"


class FinancialRatio(BaseModel):
    """Calculated financial ratios model"""

    __tablename__ = "financial_ratios"

    # Foreign key to financial statement
    financial_statement_id = Column(Integer, ForeignKey("financial_statements.id"), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)

    # Ratio categories
    ratio_category = Column(String(50), nullable=False, index=True)  # liquidity, profitability, leverage, efficiency
    ratio_name = Column(String(100), nullable=False, index=True)
    ratio_value = Column(Float)
    
    # Calculation metadata
    calculation_formula = Column(Text)
    calculation_date = Column(DateTime, default=datetime.utcnow)
    
    # Benchmarking data
    industry_median = Column(Float)
    industry_percentile = Column(Float)
    peer_group_median = Column(Float)
    
    # Relationships
    financial_statement = relationship("FinancialStatement")
    company = relationship("Company")

    # Indexes
    __table_args__ = (
        Index('idx_ratio_company_category', 'company_id', 'ratio_category'),
        Index('idx_ratio_name_value', 'ratio_name', 'ratio_value'),
    )

    def __repr__(self):
        return f"<FinancialRatio(id={self.id}, company_id={self.company_id}, name={self.ratio_name}, value={self.ratio_value})>"
