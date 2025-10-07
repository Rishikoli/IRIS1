"""
Project IRIS - API Schemas
Pydantic models for request/response validation
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


# Enums for type safety
class Exchange(str, Enum):
    NSE = "NSE"
    BSE = "BSE"
    BOTH = "BOTH"


class StatementType(str, Enum):
    INCOME_STATEMENT = "INCOME_STATEMENT"
    BALANCE_SHEET = "BALANCE_SHEET"
    CASH_FLOW = "CASH_FLOW"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AnalysisType(str, Enum):
    BENFORD = "BENFORD"
    Z_SCORE = "Z_SCORE"
    M_SCORE = "M_SCORE"
    RATIO_ANALYSIS = "RATIO_ANALYSIS"
    VERTICAL = "VERTICAL"
    HORIZONTAL = "HORIZONTAL"


# Company Schemas
class CompanyBase(BaseModel):
    name: str = Field(..., description="Company name")
    symbol: str = Field(..., description="Company symbol")
    exchange: Exchange = Field(..., description="Stock exchange")
    isin: Optional[str] = Field(None, description="ISIN number")
    sector: Optional[str] = Field(None, description="Company sector")
    industry: Optional[str] = Field(None, description="Company industry")


class CompanyCreate(CompanyBase):
    company_id: str = Field(..., description="Unique company identifier")


class CompanyResponse(CompanyBase):
    company_id: str
    market_cap: Optional[float] = None
    fiscal_year_end: Optional[datetime] = None
    currency: str = "INR"
    website: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# Financial Statement Schemas
class FinancialStatementData(BaseModel):
    """Flexible schema for financial statement data"""
    # This will accept any financial data structure
    class Config:
        extra = "allow"


class FinancialStatementCreate(BaseModel):
    company_id: str
    period: datetime = Field(..., description="Statement period")
    statement_type: StatementType
    fiscal_year: Optional[int] = None
    period_type: Optional[str] = None
    currency: str = "INR"
    data: Dict[str, Any] = Field(..., description="Financial statement data")
    source: str = "FMP_API"
    filing_url: Optional[str] = None
    filing_date: Optional[datetime] = None


class FinancialStatementResponse(BaseModel):
    id: int
    company_id: str
    period: datetime
    statement_type: StatementType
    fiscal_year: Optional[int]
    period_type: Optional[str]
    currency: str
    data: Dict[str, Any]
    source: str
    filing_url: Optional[str]
    filing_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime


# Financial Ratios Schema
class FinancialRatiosResponse(BaseModel):
    company_id: str
    period: str
    financial_ratios: Dict[str, float]
    analysis_timestamp: datetime


# Altman Z-Score Schema
class AltmanZScoreResponse(BaseModel):
    company_id: str
    z_score: float
    classification: str
    risk_level: str
    components: Dict[str, float]
    analysis_timestamp: datetime


# Beneish M-Score Schema
class BeneishMScoreResponse(BaseModel):
    company_id: str
    m_score: float
    risk_level: str
    components: Dict[str, float]
    analysis_timestamp: datetime


# Anomaly Detection Schema
class AnomalyResponse(BaseModel):
    type: str
    severity: str
    description: str
    evidence: Dict[str, Any]


class AnomalyDetectionResponse(BaseModel):
    company_id: str
    anomalies_detected: int
    anomalies: List[AnomalyResponse]
    analysis_timestamp: datetime


# Benford's Law Schema
class BenfordAnalysisResponse(BaseModel):
    company_id: str
    chi_square_statistic: float
    interpretation: str
    digit_frequencies: Dict[str, float]
    expected_frequencies: Dict[str, float]
    analysis_timestamp: datetime


# Risk Score Schema
class RiskCategoryScore(BaseModel):
    score: float
    interpretation: str
    components: Dict[str, float]


class RiskScoreResponse(BaseModel):
    company_id: str
    composite_risk_score: float
    risk_classification: Dict[str, str]
    category_scores: Dict[str, float]
    category_weights: Dict[str, float]
    analysis_timestamp: datetime


# Comprehensive Forensic Analysis Response
class ComprehensiveAnalysisResponse(BaseModel):
    company_id: str
    success: bool
    analysis_timestamp: datetime

    # Financial Analysis
    financial_ratios: Optional[Dict[str, Dict[str, float]]] = None
    vertical_analysis: Optional[Dict[str, Any]] = None
    horizontal_analysis: Optional[Dict[str, Any]] = None

    # Statistical Analysis
    altman_z_score: Optional[Dict[str, Any]] = None
    beneish_m_score: Optional[Dict[str, Any]] = None
    benford_analysis: Optional[Dict[str, Any]] = None

    # Risk Assessment
    anomaly_detection: Optional[Dict[str, Any]] = None
    risk_score: Optional[Dict[str, Any]] = None

    # Error handling
    error: Optional[str] = None


# Analysis Request Schema
class AnalysisRequest(BaseModel):
    company_id: str
    financial_statements: List[FinancialStatementCreate]
    include_benford: bool = True
    include_anomalies: bool = True
    include_risk_scoring: bool = True


# Error Response Schema
class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


# Success Response Schema
class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None
