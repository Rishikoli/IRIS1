"""
Project IRIS - Database Models Package
Import all models for easy access
"""

# Import base classes and utilities
from src.database.base import Base, BaseModel, JSONBType, serialize_jsonb, deserialize_jsonb
from src.database.base import engine, SessionLocal, get_db, create_tables, drop_tables

# Import all model classes
from .company import Company, CompanyAlias
from .financial_statements import FinancialStatement, FinancialRatio, StatementType, ReportingPeriod
from .forensic_analysis import (
    AnalysisJob, ForensicAnalysis, FinancialAnomaly,
    AnalysisStatus, AnomalyType, SeverityLevel
)
from .risk_scores import (
    RiskScore, RiskFactor, RiskAlert,
    RiskCategory, RiskLevel
)
from .compliance import (
    ComplianceValidation, RegulatoryAction, ComplianceDeadline,
    ComplianceFramework, ViolationType, ComplianceStatus
)
from .chat import (
    ChatSession, ChatMessage, DocumentChunk, QueryAnalytics,
    AgentType, MessageType
)
from .additional import (
    Report, PeerBenchmark, SentimentAnalysis, GoogleTrendsData,
    ReportType, ReportFormat
)
from .user import User

# List all models for easy iteration
ALL_MODELS = [
    Company,
    CompanyAlias,
    FinancialStatement,
    FinancialRatio,
    AnalysisJob,
    ForensicAnalysis,
    FinancialAnomaly,
    RiskScore,
    RiskFactor,
    RiskAlert,
    ComplianceValidation,
    RegulatoryAction,
    ComplianceDeadline,
    ChatSession,
    ChatMessage,
    DocumentChunk,
    QueryAnalytics,
    Report,
    PeerBenchmark,
    SentimentAnalysis,
    GoogleTrendsData,
    User,
]

__all__ = [
    # Base classes
    'Base', 'BaseModel', 'JSONBType', 'serialize_jsonb', 'deserialize_jsonb',
    'engine', 'SessionLocal', 'get_db', 'create_tables', 'drop_tables',
    
    # Core models
    'Company', 'CompanyAlias',
    
    # Financial models
    'FinancialStatement', 'FinancialRatio', 'StatementType', 'ReportingPeriod',
    
    # Analysis models
    'AnalysisJob', 'ForensicAnalysis', 'FinancialAnomaly',
    'AnalysisStatus', 'AnomalyType', 'SeverityLevel',
    
    # Risk models
    'RiskScore', 'RiskFactor', 'RiskAlert',
    'RiskCategory', 'RiskLevel',
    
    # Compliance models
    'ComplianceValidation', 'RegulatoryAction', 'ComplianceDeadline',
    'ComplianceFramework', 'ViolationType', 'ComplianceStatus',
    
    # Chat models
    'ChatSession', 'ChatMessage', 'DocumentChunk', 'QueryAnalytics',
    'AgentType', 'MessageType',
    
    # Additional models
    'Report', 'PeerBenchmark', 'SentimentAnalysis', 'GoogleTrendsData',
    'ReportType', 'ReportFormat',
    'User',
    
    # Model collections
    'ALL_MODELS',
]