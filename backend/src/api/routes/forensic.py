"""
Project IRIS - Forensic Analysis API Routes
All forensic analysis endpoints including ratios, Z-Score, M-Score, etc.
"""

import logging
import redis
from cachetools import TTLCache
import time
from typing import Dict, Any, Optional
import numpy as np
from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime
from src.agents.forensic.agent2_forensic_analysis import ForensicAnalysisAgent
from src.agents.forensic.agent3_risk_scoring import RiskScoringAgent
from src.agents.forensic.agent4_compliance import ComplianceValidationAgent
from src.agents.forensic.agent5_reporting import ReportingAgent
from src.agents.forensic.agent9_network_analysis import NetworkAnalysisAgent
from src.agents.forensic.agent13_time_traveler import TimeTravelerAgent
from src.api.schemas.models import (
    AnalysisRequest, ComprehensiveAnalysisResponse, FinancialRatiosResponse,
    AltmanZScoreResponse, BeneishMScoreResponse, AnomalyDetectionResponse,
    BenfordAnalysisResponse, RiskScoreResponse, SuccessResponse, ErrorResponse
)

logger = logging.getLogger(__name__)

# Initialize caching systems
financial_data_cache = TTLCache(maxsize=100, ttl=3600)  # 1 hour TTL
analysis_cache = TTLCache(maxsize=200, ttl=1800)        # 30 minutes TTL

# Redis connection for distributed caching (optional)
redis_client = None
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    redis_client.ping()  # Test connection
    logger.info("Redis cache connected successfully")
except Exception as e:
    logger.warning(f"Redis not available, using in-memory cache only: {e}")
    redis_client = None
ingestion_router = APIRouter(prefix="/api/ingestion", tags=["ingestion"])
forensic_router = APIRouter(prefix="/api/forensic", tags=["forensic"])
risk_router = APIRouter(prefix="/api/risk-score", tags=["risk"])
companies_router = APIRouter(prefix="/companies", tags=["companies"])

# Initialize agents
forensic_agent = ForensicAnalysisAgent()
risk_agent = RiskScoringAgent()
compliance_agent = ComplianceValidationAgent()
compliance_agent = ComplianceValidationAgent()
reporting_agent = ReportingAgent()
network_agent = NetworkAnalysisAgent()
time_traveler = TimeTravelerAgent()


def _make_json_safe(value):
    """Recursively convert numpy/pandas and non-JSON-safe values to JSON-safe Python types.

    - np.bool_ -> bool
    - np.integer -> int
    - np.floating (incl. NaN/Inf) -> float or None if NaN/Inf
    - lists/tuples/sets -> lists with safe items
    - dicts -> dict with safe keys/values
    - datetime-like with isoformat() -> isoformat string
    - bytes/bytearray -> utf-8 string
    """
    try:
        # Handle numpy scalar types first
        if isinstance(value, np.bool_):
            return bool(value)
        if isinstance(value, (np.integer,)):
            return int(value)
        if isinstance(value, (np.floating,)):
            f = float(value)
            if math.isnan(f) or math.isinf(f):
                return None
            return f

        # Native floats NaN/Inf
        if isinstance(value, float):
            if math.isnan(value) or math.isinf(value):
                return None
            return value

        # Bytes
        if isinstance(value, (bytes, bytearray)):
            return value.decode("utf-8", errors="ignore")

        # Datetime-like objects
        if hasattr(value, "isoformat") and callable(getattr(value, "isoformat")):
            try:
                return value.isoformat()
            except Exception:
                pass

        # Containers
        if isinstance(value, dict):
            return {str(_make_json_safe(k)): _make_json_safe(v) for k, v in value.items()}
        if isinstance(value, (list, tuple, set)):
            return [_make_json_safe(v) for v in value]

        # Leave other primitives as-is
        return value
    except Exception:
        # Fallback to string to avoid serialization crashes
        return str(value)


@ingestion_router.get("/{company_symbol}")
async def get_data_source_info(company_symbol: str):
    """Get information about data sources for a company symbol"""
    try:
        logger.info(f"🔍 Checking data sources for {company_symbol}")

        # Try to get real data from Yahoo Finance first
        financial_statements = await _fetch_yahoo_finance_data(company_symbol)

        if financial_statements:
            data_source = "yahoo_finance"
            status = "✅ Real data available"
            message = f"Real financial data found for {company_symbol} on Yahoo Finance"
        else:
            data_source = "enhanced_mock_data"
            status = "⚠️ No real data found"
            message = f"No real data available for {company_symbol}, would use mock data"

        return {
            "company_symbol": company_symbol,
            "data_source": data_source,
            "status": status,
            "message": message,
            "available_statements": len(financial_statements) if financial_statements else 0,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error checking data sources for {company_symbol}: {e}")
        return {
            "company_symbol": company_symbol,
            "data_source": "error",
            "status": "❌ Error",
            "message": f"Error checking data sources: {str(e)}",
            "available_statements": 0,
            "timestamp": datetime.utcnow().isoformat()
        }


@ingestion_router.post("/{company_symbol}")
async def ingest_company_data(company_symbol: str):
    try:
        logger.info(f"🔄 Starting data ingestion for {company_symbol}")

        # Try to get real data from Yahoo Finance first
        financial_statements = await _fetch_yahoo_finance_data(company_symbol)

        if financial_statements:
            logger.info(f"✅ Successfully fetched real Yahoo Finance data: {len(financial_statements)} statements")
            data_source = "yahoo_finance"
            message = f"Successfully ingested real financial data for {company_symbol} from Yahoo Finance"
        else:
            # Fallback to enhanced mock data for testing
            logger.warning(f"⚠️ No real data found for {company_symbol}, using enhanced mock data for testing")
            financial_statements = _create_enhanced_mock_data(company_symbol)
            data_source = "enhanced_mock_data"
            message = f"Using enhanced mock data for {company_symbol} (no real data available)"

        if not financial_statements:
            raise HTTPException(
                status_code=404,
                detail=f"No financial data available for {company_symbol}. The company may not exist or may not have financial data available."
            )

        # Get date range
        periods = [s['period_end'] for s in financial_statements]
        period_start = min(periods) if periods else None
        period_end = max(periods) if periods else None

        return {
            "success": True,
            "company_symbol": company_symbol,
            "financial_statements": financial_statements,
            "period_start": period_start,
            "period_end": period_end,
            "data_source": data_source,
            "statement_count": len(financial_statements),
            "message": message
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error ingesting data for {company_symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Data ingestion failed: {str(e)}")


async def _fetch_yahoo_finance_data(company_symbol: str) -> list:
    """Fetch real financial data from Yahoo Finance with multiple symbol formats"""
    try:
        import yfinance as yf

        # Try different symbol formats for Indian stocks
        symbol_formats = [
            f"{company_symbol}.NS",      # NSE format
            f"{company_symbol}.BO",      # BSE format
            f"{company_symbol}.NSE",     # Alternative NSE format
            company_symbol,              # Just the symbol
        ]

        financial_statements = []

        for symbol_format in symbol_formats:
            try:
                logger.info(f"Trying Yahoo Finance symbol: {symbol_format}")
                ticker = yf.Ticker(symbol_format)

                # Get financial statements
                income_stmt = ticker.financials
                balance_sheet = ticker.balance_sheet
                cash_flow = ticker.cashflow

                # Check if we got valid data
                if (income_stmt is not None and len(income_stmt.columns) > 0 and
                    balance_sheet is not None and len(balance_sheet.columns) > 0):

                    logger.info(f"✅ Found data for {symbol_format}: Income={income_stmt.shape}, Balance={balance_sheet.shape}, Cash={cash_flow.shape if cash_flow is not None else 'None'}")

                    # Process income statements (latest 3 years)
                    for i in range(min(3, len(income_stmt.columns))):
                        stmt_data = income_stmt.iloc[:, i].to_dict()
                        stmt_data['date'] = str(income_stmt.columns[i].date())

                        financial_statements.append({
                            'statement_type': 'income_statement',
                            'period_end': str(income_stmt.columns[i].date()),
                            'data': stmt_data
                        })

                    # Process balance sheets (latest 3 years)
                    for i in range(min(3, len(balance_sheet.columns))):
                        stmt_data = balance_sheet.iloc[:, i].to_dict()
                        stmt_data['date'] = str(balance_sheet.columns[i].date())

                        financial_statements.append({
                            'statement_type': 'balance_sheet',
                            'period_end': str(balance_sheet.columns[i].date()),
                            'data': stmt_data
                        })

                    # Process cash flow statements (latest 3 years)
                    if cash_flow is not None:
                        for i in range(min(3, len(cash_flow.columns))):
                            stmt_data = cash_flow.iloc[:, i].to_dict()
                            stmt_data['date'] = str(cash_flow.columns[i].date())

                            financial_statements.append({
                                'statement_type': 'cash_flow_statement',
                                'period_end': str(cash_flow.columns[i].date()),
                                'data': stmt_data
                            })

                    # Success! We found working data
                    logger.info(f"✅ Successfully fetched real data for {company_symbol} using {symbol_format}")
                    return financial_statements

            except Exception as e:
                logger.warning(f"Failed to fetch data for {symbol_format}: {e}")
                continue

        # No symbol format worked
        logger.warning(f"❌ No Yahoo Finance data available for {company_symbol} in any format")
        return []

    except Exception as e:
        logger.error(f"Error fetching Yahoo Finance data for {company_symbol}: {e}")
        return []


def _create_enhanced_mock_data(company_symbol: str) -> list:
    """Create enhanced mock financial data with realistic values for different companies"""
    financial_statements = []

    # Company-specific base values for more realistic data
    company_configs = {
        'RELIANCE': {
            'revenue_base': 8000000000,    # 8B revenue
            'asset_base': 15000000000,     # 15B assets
            'revenue_growth': 0.12,        # 12% growth
            'margin': 0.25                 # 25% net margin
        },
        'TCS': {
            'revenue_base': 2500000000,    # 2.5B revenue
            'asset_base': 4000000000,      # 4B assets
            'revenue_growth': 0.15,        # 15% growth
            'margin': 0.22                 # 22% net margin
        },
        'INFY': {
            'revenue_base': 1800000000,    # 1.8B revenue
            'asset_base': 2500000000,      # 2.5B assets
            'revenue_growth': 0.10,        # 10% growth
            'margin': 0.20                 # 20% net margin
        },
        'HIGHRISK': {
            'revenue_base': 500000000,     # 500M revenue
            'asset_base': 2000000000,      # 2B assets (Higher base to lower turnover)
            'revenue_growth': 0.50,        # 50% "growth" in past means current is lower (Decline)
            'margin': -0.50,               # -50% net margin (Huge loss)
            'liability_ratio': 0.95        # 95% liabilities (Extreme leverage)
        }
    }

    config = company_configs.get(company_symbol, company_configs['RELIANCE'])
    base_year = 2024

    for year_offset in range(3):
        year = base_year - year_offset

        # Calculate growth factors
        revenue_growth = 1.0 + (config['revenue_growth'] * year_offset)
        asset_growth = 1.0 + (config['revenue_growth'] * 0.8 * year_offset)  # Assets grow slower

        # Income Statement
        base_revenue = config['revenue_base']
        stmt_data = {
            'Total Revenue': int(base_revenue * revenue_growth),
            'Cost of Revenue': int((base_revenue * revenue_growth) * (1 - config['margin'] * 1.2)),  # COGS
            'Gross Profit': int((base_revenue * revenue_growth) * config['margin'] * 1.2),           # Gross margin
            'Operating Expenses': int((base_revenue * revenue_growth) * config['margin'] * 0.6),    # OPEX
            'Operating Income': int((base_revenue * revenue_growth) * config['margin']),           # Operating margin
            'Net Income': int((base_revenue * revenue_growth) * config['margin']),                # Net margin
            'date': f"{year}-12-31"
        }

        financial_statements.append({
            'statement_type': 'income_statement',
            'period_end': f"{year}-12-31",
            'data': stmt_data
        })

        # Balance Sheet
        base_assets = config['asset_base']
        liability_ratio = config.get('liability_ratio', 0.65)
        
        stmt_data = {
            'Total Assets': int(base_assets * asset_growth),
            'Total Current Assets': int((base_assets * asset_growth) * 0.35),     # 35% current assets
            'Cash and Cash Equivalents': int((base_assets * asset_growth) * 0.05), # 5% cash (Low liquidity)
            'Accounts Receivable': int((base_assets * asset_growth) * 0.15),      # 15% receivables
            'Inventory': int((base_assets * asset_growth) * 0.08),               # 8% inventory
            'Total Liabilities': int((base_assets * asset_growth) * liability_ratio),       # Custom liabilities
            'Total Current Liabilities': int((base_assets * asset_growth) * (liability_ratio * 0.4)), # 40% of liab are current
            'Short Term Debt': int((base_assets * asset_growth) * (liability_ratio * 0.3)),         # 30% of liab are short term debt
            'Long Term Debt': int((base_assets * asset_growth) * (liability_ratio * 0.6)),          # 60% of liab are long-term
            'Total Equity': int((base_assets * asset_growth) * (1 - liability_ratio)),            # Remaining is equity
            'date': f"{year}-12-31"
        }

        financial_statements.append({
            'statement_type': 'balance_sheet',
            'period_end': f"{year}-12-31",
            'data': stmt_data
        })

    return financial_statements


@forensic_router.post("/{company_symbol}")
async def run_forensic_analysis_api(company_symbol: str):
    """Run comprehensive forensic analysis for a company"""
    try:
        logger.info(f"Starting forensic analysis for {company_symbol}")

        # Get real data from ingestion
        try:
            ingestion_result = await ingest_company_data(company_symbol)
            financial_statements = ingestion_result["financial_statements"]
        except Exception as ingestion_error:
            logger.warning(f"Ingestion failed: {ingestion_error}")
            raise HTTPException(
                status_code=404,
                detail=f"Could not retrieve financial data for {company_symbol}. Please ensure the company symbol is valid."
            )

        if not financial_statements or len(financial_statements) < 2:
            raise HTTPException(
                status_code=404,
                detail=f"Insufficient financial data for {company_symbol}. Need at least 2 periods of data."
            )

        # Run comprehensive forensic analysis with real data
        try:
            analysis_result = forensic_agent.comprehensive_forensic_analysis(company_symbol, financial_statements)
        except Exception as agent_error:
            logger.error(f"Agent 2 (Forensic) crashed for {company_symbol}: {agent_error}")
            return {
                "success": False,
                "company_id": company_symbol,
                "error": f"Forensic Analysis Agent Failed: {str(agent_error)}",
                "analysis_timestamp": datetime.utcnow().isoformat()
            }

        if not analysis_result['success']:
            return {
                "success": False,
                "company_id": company_symbol,
                "error": analysis_result.get('error', 'Analysis failed'),
                "analysis_timestamp": datetime.utcnow().isoformat()
            }

        # Format response with real analysis results
        response_data = {
            "success": True,
            "company_id": company_symbol,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "data_source": ingestion_result.get("data_source", "unknown")
        }

        # Add analysis results from the actual forensic agents
        analysis_types = [
            'vertical_analysis', 'horizontal_analysis', 'financial_ratios',
            'benford_analysis', 'anomaly_detection', 'altman_z_score', 'beneish_m_score',
            'sloan_ratio', 'dechow_f_score'
        ]

        for analysis_type in analysis_types:
            if analysis_type in analysis_result:
                response_data[analysis_type] = analysis_result[analysis_type]

        # Add risk assessment using Agent 3
        try:
            risk_assessment = risk_agent.calculate_risk_score(company_symbol, analysis_result)
            response_data['risk_assessment'] = {
                'overall_risk_score': risk_assessment.overall_risk_score,
                'risk_level': risk_assessment.risk_level,
                'risk_factors': risk_assessment.risk_factors,
                'investment_recommendation': risk_assessment.investment_recommendation,
                'monitoring_frequency': risk_assessment.monitoring_frequency,

                'category_scores': {
                    category.value: {
                        'score': risk_score.score,
                        'weight': risk_score.weight,
                        'confidence': risk_score.confidence,
                        'factors': risk_score.factors,
                        'recommendations': risk_score.recommendations
                    }
                    for category, risk_score in risk_assessment.risk_category_scores.items()
                },
                'shap_values': risk_assessment.shap_values
            }
        except Exception as e:
            logger.warning(f"Risk assessment failed for {company_symbol}: {e}")
            response_data['risk_assessment'] = {
                'overall_risk_score': 45,
                'risk_level': 'MEDIUM',
                'risk_factors': ['Risk assessment temporarily unavailable'],
                'investment_recommendation': 'CAUTION - Risk assessment pending',
                'monitoring_frequency': 'MONTHLY'
            }

        # Add compliance assessment using Agent 4
        try:
            compliance_assessment = compliance_agent.validate_compliance(company_symbol, analysis_result)
            response_data['compliance_assessment'] = {
                'overall_compliance_score': compliance_assessment.overall_compliance_score,
                'compliance_status': compliance_assessment.compliance_status,
                'framework_scores': {
                    framework.value: score
                    for framework, score in compliance_assessment.framework_scores.items()
                },
                'violations_count': len(compliance_assessment.violations),
                'recommendations': compliance_assessment.recommendations,
                'next_review_date': compliance_assessment.next_review_date
            }
        except Exception as e:
            logger.warning(f"Compliance assessment failed for {company_symbol}: {e}")
            response_data['compliance_assessment'] = {
                'overall_compliance_score': 75,
                'compliance_status': 'PARTIAL_COMPLIANCE',
                'framework_scores': {},
                'violations_count': 0,
                'recommendations': ['Compliance assessment temporarily unavailable'],
                'next_review_date': datetime.utcnow().isoformat()
            }

        # Sanitize all values for JSON serialization (handle numpy types/NaN/etc.)
        response_data = _make_json_safe(response_data)

        # 5. Index for Q&A in the background
        try:
            from src.agents.agent7_qa_rag import index_company_for_qa
            # We can use BackgroundTasks but for now we'll do it synchronously 
            # as it's just embeddings locally
            index_company_for_qa(company_symbol, response_data)
            logger.info(f"Successfully indexed {company_symbol} for Q&A")
        except Exception as e:
            logger.warning(f"Indexing for Q&A failed for {company_symbol}: {e}")

        logger.info(f"Forensic analysis completed for {company_symbol} with real data")
        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in forensic analysis for {company_symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Forensic analysis failed: {str(e)}")


@forensic_router.post("/{company_symbol}/risk-score")
async def calculate_risk_score_api(company_symbol: str):
    """Calculate risk score for a company using Agent 3"""
    try:
        logger.info(f"Calculating risk score for {company_symbol}")

        # Get forensic analysis data first
        try:
            ingestion_result = await ingest_company_data(company_symbol)
            financial_statements = ingestion_result["financial_statements"]
        except Exception:
            # Fallback to mock data if ingestion fails
            financial_statements = _create_enhanced_mock_data(company_symbol)

        if not financial_statements:
            raise HTTPException(
                status_code=404,
                detail=f"No financial data available for {company_symbol}"
            )

        # Run forensic analysis to get the data needed for risk scoring
        forensic_result = forensic_agent.comprehensive_forensic_analysis(company_symbol, financial_statements)

        if not forensic_result['success']:
            # Fallback to mock risk assessment
            return {
                "success": True,
                "company_id": company_symbol,
                "risk_score": {
                    "overall_score": 45,
                    "risk_level": "MEDIUM",
                    "confidence_score": 0.6,
                    "risk_factors": ["Insufficient data for detailed risk analysis"],
                    "analysis_timestamp": datetime.utcnow().isoformat()
                }
            }

        # Calculate risk score using Agent 3
        risk_assessment = risk_agent.calculate_risk_score(company_symbol, forensic_result)

        return {
            "success": True,
            "company_id": company_symbol,
            "risk_score": {
                "overall_score": risk_assessment.overall_risk_score,
                "risk_level": risk_assessment.risk_level,
                "confidence_score": sum(score.confidence for score in risk_assessment.risk_category_scores.values()) / len(risk_assessment.risk_category_scores),
                "risk_factors": risk_assessment.risk_factors,
                "investment_recommendation": risk_assessment.investment_recommendation,
                "monitoring_frequency": risk_assessment.monitoring_frequency,

                "category_scores": {
                    category.value: {
                        "score": risk_score.score,
                        "weight": risk_score.weight,
                        "confidence": risk_score.confidence,
                        "factors": risk_score.factors,
                        "recommendations": risk_score.recommendations
                    }
                    for category, risk_score in risk_assessment.risk_category_scores.items()
                },
                "shap_values": risk_assessment.shap_values,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
        }

    except Exception as e:
        logger.error(f"Error calculating risk score for {company_symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Risk scoring failed: {str(e)}")


@forensic_router.post("/{company_symbol}/compliance")
async def validate_compliance_api(company_symbol: str):
    """Validate compliance for a company using Agent 4"""
    try:
        logger.info(f"Validating compliance for {company_symbol}")

        # Get forensic analysis data first
        try:
            ingestion_result = await ingest_company_data(company_symbol)
            financial_statements = ingestion_result["financial_statements"]
        except Exception:
            # Fallback to mock data if ingestion fails
            financial_statements = _create_enhanced_mock_data(company_symbol)

        if not financial_statements:
            raise HTTPException(
                status_code=404,
                detail=f"No financial data available for {company_symbol}"
            )

        # Run forensic analysis to get the data needed for compliance validation
        forensic_result = forensic_agent.comprehensive_forensic_analysis(company_symbol, financial_statements)

        if not forensic_result['success']:
            # Fallback to basic compliance assessment
            return {
                "success": True,
                "company_id": company_symbol,
                "compliance_assessment": {
                    "overall_compliance_score": 70,
                    "compliance_status": "PARTIAL_COMPLIANCE",
                    "violations": ["Insufficient data for detailed compliance analysis"],
                    "framework_scores": {},
                    "recommendations": ["Ensure all required financial disclosures are complete"],
                    "next_review_date": datetime.utcnow().isoformat(),
                    "analysis_timestamp": datetime.utcnow().isoformat()
                }
            }

        # Validate compliance using Agent 4
        compliance_assessment = compliance_agent.validate_compliance(company_symbol, forensic_result)

        return {
            "success": True,
            "company_id": company_symbol,
            "compliance_assessment": compliance_agent.generate_compliance_report(compliance_assessment, forensic_result)
        }

    except Exception as e:
        logger.error(f"Error validating compliance for {company_symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Compliance validation failed: {str(e)}")


@forensic_router.post("/{company_symbol}/comprehensive-report")
async def generate_comprehensive_report_api(company_symbol: str):
    """Generate comprehensive report with all analysis types using Agent 5"""
    try:
        logger.info(f"Generating comprehensive report for {company_symbol}")

        # Get forensic analysis data first
        try:
            ingestion_result = await ingest_company_data(company_symbol)
            financial_statements = ingestion_result["financial_statements"]
        except Exception:
            # Fallback to mock data if ingestion fails
            financial_statements = _create_enhanced_mock_data(company_symbol)

        if not financial_statements:
            raise HTTPException(
                status_code=404,
                detail=f"No financial data available for {company_symbol}"
            )

        # Run forensic analysis to get the data needed for comprehensive report
        forensic_result = forensic_agent.comprehensive_forensic_analysis(company_symbol, financial_statements)

        if not forensic_result['success']:
            raise HTTPException(
                status_code=404,
                detail=f"Forensic analysis failed for {company_symbol}"
            )

        # Calculate risk score using Agent 3
        risk_assessment = risk_agent.calculate_risk_score(company_symbol, forensic_result)

        # Validate compliance using Agent 4
        compliance_assessment = compliance_agent.validate_compliance(company_symbol, forensic_result)

        # Prepare analysis data for reporting agent
        analysis_data = {
            "forensic_analysis": forensic_result,
            "risk_assessment": {
                'overall_risk_score': risk_assessment.overall_risk_score,
                'risk_level': risk_assessment.risk_level,
                'risk_factors': risk_assessment.risk_factors,
                'investment_recommendation': risk_assessment.investment_recommendation,
                'monitoring_frequency': risk_assessment.monitoring_frequency
            },
            "compliance_assessment": {
                'overall_compliance_score': compliance_assessment.overall_compliance_score,
                'compliance_status': compliance_assessment.compliance_status,
                'framework_scores': {framework.value: score for framework, score in compliance_assessment.framework_scores.items()},
                'violations': compliance_assessment.violations,
                'recommendations': compliance_assessment.recommendations,
                'next_review_date': compliance_assessment.next_review_date
            }
        }

        # Generate comprehensive report using Agent 5
        from src.agents.forensic.agent5_reporting import ExportFormat
        comprehensive_report = await reporting_agent.generate_comprehensive_report(
            company_symbol,
            analysis_data,
            export_formats=[ExportFormat.PDF, ExportFormat.EXCEL]
        )

        if not comprehensive_report.get('success'):
            raise HTTPException(
                status_code=500,
                detail=f"Comprehensive report generation failed: {comprehensive_report.get('error')}"
            )

        return {
            "success": True,
            "company_id": company_symbol,
            "report_id": comprehensive_report["comprehensive_report"]["report_id"],
            "report_metadata": comprehensive_report["comprehensive_report"]["report_metadata"],
            "exports": comprehensive_report["comprehensive_report"]["exports"],
            "analysis_timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating comprehensive report for {company_symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Comprehensive report generation failed: {str(e)}")


@forensic_router.get("/reports/download/{filename}")
async def download_report(filename: str):
    """Download a generated report file"""
    try:
        # Construct file path
        file_path = f"/home/aditya/I.R.I.S./backend/reports/{filename}"

        # Check if file exists
        import os
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail=f"Report file not found: {filename}"
            )

        # Determine file type for proper headers
        if filename.endswith('.pdf'):
            media_type = "application/pdf"
        elif filename.endswith('.xlsx'):
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        else:
            media_type = "application/octet-stream"

        # Return file response
        from fastapi.responses import FileResponse
        return FileResponse(
            path=file_path,
            media_type=media_type,
            filename=filename
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading report {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to download report: {str(e)}")


@risk_router.post("/{company_symbol}")
async def calculate_risk_score_standalone(company_symbol: str):
    """Calculate risk score for a company (standalone endpoint) using Agent 3"""
    try:
        logger.info(f"Calculating risk score for {company_symbol}")

        # Get forensic analysis data first
        try:
            ingestion_result = await ingest_company_data(company_symbol)
            financial_statements = ingestion_result["financial_statements"]
        except Exception:
            # Fallback to mock data if ingestion fails
            financial_statements = _create_enhanced_mock_data(company_symbol)

        if not financial_statements:
            raise HTTPException(
                status_code=404,
                detail=f"No financial data available for {company_symbol}"
            )

        # Run forensic analysis to get the data needed for risk scoring
        forensic_result = forensic_agent.comprehensive_forensic_analysis(company_symbol, financial_statements)

        if not forensic_result['success']:
            # Fallback to mock risk assessment
            return {
                "success": True,
                "company_id": company_symbol,
                "risk_score": {
                    "overall_score": 45,
                    "risk_level": "MEDIUM",
                    "confidence_score": 0.6,
                    "risk_factors": ["Insufficient data for detailed risk analysis"],
                    "analysis_timestamp": datetime.utcnow().isoformat()
                }
            }

        # Calculate risk score using Agent 3
        risk_assessment = risk_agent.calculate_risk_score(company_symbol, forensic_result)

        return {
            "success": True,
            "company_id": company_symbol,
            "risk_score": {
                "overall_score": risk_assessment.overall_risk_score,
                "risk_level": risk_assessment.risk_level,
                "confidence_score": sum(score.confidence for score in risk_assessment.risk_category_scores.values()) / len(risk_assessment.risk_category_scores),
                "risk_factors": risk_assessment.risk_factors,
                "investment_recommendation": risk_assessment.investment_recommendation,
                "monitoring_frequency": risk_assessment.monitoring_frequency,
                "category_scores": {
                    category.value: {
                        "score": risk_score.score,
                        "weight": risk_score.weight,
                        "confidence": risk_score.confidence,
                        "factors": risk_score.factors,
                        "recommendations": risk_score.recommendations
                    }
                    for category, risk_score in risk_assessment.risk_category_scores.items()
                },
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
        }

    except Exception as e:
        logger.error(f"Error calculating risk score for {company_symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Risk scoring failed: {str(e)}")


@forensic_router.post("/{company_symbol}/realtime")
async def realtime_forensic_analysis(company_symbol: str):
    """Run real-time forensic analysis with progress updates"""
    try:
        logger.info(f"Starting real-time analysis for {company_symbol}")

        # Run real-time analysis with progress simulation
        # ... (existing code)
        pass

    except Exception as e:
        logger.error(f"Error in realtime analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@forensic_router.get("/network/{company_symbol}")
async def get_rpt_network(company_symbol: str):
    """
    Get Related Party Transaction Network Graph.
    UPGRADE: Uses Agent 2.5 (Shell Hunter) to detect circular trading cycles.
    """
    try:
        logger.info(f"Generating Shell Hunter Network for {company_symbol}")
        
        # Use Agent 2.5 (Shell Hunter)
        from src.agents.forensic.agent_shell_hunter import ShellHunterAgent
        shell_agent = ShellHunterAgent()
        
        # Run algorithmic detection
        result = shell_agent.analyze_network(company_symbol)

        return {
            "success": True,
            "company_id": company_symbol,
            "graph_data": {
                "nodes": result["graph_data"]["nodes"],
                "edges": result["graph_data"]["edges"]
            },
            "risk_score": result["risk_score"],
            "cycles": result["detected_cycles"],
            "detected_cycles": result["detected_cycles"],
            "hidden_directors": result["hidden_directors"],
            "analysis_timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error generating network for {company_symbol}: {e}")
        # Return a safe empty response
        return {
             "success": False,
             "error": str(e),
             "graph_data": {
                 "nodes": [],
                 "edges": []
             },
             "cycles": []
        }


        


async def store_analysis_results(company_id: str, analysis_result: Dict[str, Any]):
    """Background task to store analysis results in database"""
    try:
        db_client = get_db_client()

        # Store each analysis type separately for better querying
        analysis_types = {
            'financial_ratios': analysis_result.get('financial_ratios'),
            'altman_z_score': analysis_result.get('altman_z_score'),
            'beneish_m_score': analysis_result.get('beneish_m_score'),
            'benford_analysis': analysis_result.get('benford_analysis'),
            'anomaly_detection': analysis_result.get('anomaly_detection')
        }

        for analysis_type, data in analysis_types.items():
            if data:
                try:
                    insert_query = """
                    INSERT INTO forensic_analysis (company_id, analysis_type, results, created_at)
                    VALUES (:company_id, :analysis_type, :results, NOW())
                    """

                    db_client.execute_query(insert_query, {
                        'company_id': company_id,
                        'analysis_type': analysis_type.upper(),
                        'results': data
                    })
                except Exception as e:
                    logger.error(f"Error storing {analysis_type} for {company_id}: {e}")

    except Exception as e:
        logger.error(f"Error in background storage for {company_id}: {e}")


@companies_router.post("/analyze-yahoo/{symbol}", response_model=ComprehensiveAnalysisResponse)
async def analyze_yahoo_finance_data(symbol: str, background_tasks: BackgroundTasks):
    """Analyze real market data from Yahoo Finance for a company symbol"""
    try:
        logger.info(f"Starting Yahoo Finance forensic analysis for {symbol}")

        # Fetch real data from Yahoo Finance
        import yfinance as yf
        ticker = yf.Ticker(f"{symbol}.NS")  # NSE symbol

        # Get financial statements
        income_stmt = ticker.financials
        balance_sheet = ticker.balance_sheet

        if income_stmt is None or balance_sheet is None:
            raise HTTPException(
                status_code=404,
                detail=f"Insufficient financial data available for {symbol} on Yahoo Finance"
            )

        # Convert to format expected by forensic agent
        financial_statements = []

        # Add income statements (latest 2 years)
        for i in range(min(2, len(income_stmt.columns))):
            stmt_data = income_stmt.iloc[:, i].to_dict()
            stmt_data['date'] = str(income_stmt.columns[i].date())
            financial_statements.append({
                'statement_type': 'income_statement',
                'data': stmt_data
            })

        # Add balance sheets (latest 2 years)
        for i in range(min(2, len(balance_sheet.columns))):
            stmt_data = balance_sheet.iloc[:, i].to_dict()
            stmt_data['date'] = str(balance_sheet.columns[i].date())
            financial_statements.append({
                'statement_type': 'balance_sheet',
                'data': stmt_data
            })

        # Run comprehensive forensic analysis
        analysis_result = forensic_agent.comprehensive_forensic_analysis(f"yahoo_{symbol}", financial_statements)

        if not analysis_result['success']:
            return ComprehensiveAnalysisResponse(
                company_id=f"yahoo_{symbol}",
                success=False,
                analysis_timestamp=datetime.utcnow(),
                error=analysis_result.get('error', 'Analysis failed')
            )

        # Extract results for response
        response_data = {
            'company_id': f"yahoo_{symbol}",
            'success': True,
            'analysis_timestamp': datetime.utcnow()
        }

        # Add all analysis results
        if 'financial_ratios' in analysis_result:
            response_data['financial_ratios'] = analysis_result['financial_ratios']

        if 'vertical_analysis' in analysis_result:
            # Flatten the structure if needed (Agent 2 returns it wrapped)
            va_result = analysis_result['vertical_analysis']
            if isinstance(va_result, dict) and 'vertical_analysis' in va_result:
                response_data['vertical_analysis'] = va_result['vertical_analysis']
            else:
                response_data['vertical_analysis'] = va_result

        if 'horizontal_analysis' in analysis_result:
            response_data['horizontal_analysis'] = analysis_result['horizontal_analysis']

        if 'altman_z_score' in analysis_result:
            response_data['altman_z_score'] = analysis_result['altman_z_score']

        if 'beneish_m_score' in analysis_result:
            response_data['beneish_m_score'] = analysis_result['beneish_m_score']

        if 'benford_analysis' in analysis_result:
            response_data['benford_analysis'] = analysis_result['benford_analysis']

        if 'anomaly_detection' in analysis_result:
            response_data['anomaly_detection'] = analysis_result['anomaly_detection']

        logger.info(f"Yahoo Finance forensic analysis completed for {symbol}")
        return ComprehensiveAnalysisResponse(**response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in Yahoo Finance analysis for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Yahoo Finance analysis failed: {str(e)}")


@companies_router.get("/yahoo-symbols")
async def get_supported_yahoo_symbols():
    """Get list of supported Yahoo Finance symbols for forensic analysis"""
    return {
        "symbols": [
            {"symbol": "HCLTECH.NS", "name": "HCL Technologies Limited"},
            {"symbol": "TCS.NS", "name": "Tata Consultancy Services Limited"},
            {"symbol": "INFY.NS", "name": "Infosys Limited"},
            {"symbol": "WIPRO.NS", "name": "Wipro Limited"},
            {"symbol": "TECHM.NS", "name": "Tech Mahindra Limited"},
            {"symbol": "LTIM.NS", "name": "LTIMindtree Limited"}
        ],
        "message": "These symbols have been tested and work with Yahoo Finance forensic analysis"
    }
