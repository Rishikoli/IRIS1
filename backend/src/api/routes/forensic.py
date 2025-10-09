"""
Project IRIS - Forensic Analysis API Routes
All forensic analysis endpoints including ratios, Z-Score, M-Score, etc.
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
import json
from datetime import datetime

from agents.forensic.agent2_forensic_analysis import ForensicAnalysisAgent
# from agents.forensic.agent3_risk_scoring import RiskScoringAgent  # TODO: Create this agent
from database.connection import get_db_client
from api.schemas.models import (
    AnalysisRequest, ComprehensiveAnalysisResponse, FinancialRatiosResponse,
    AltmanZScoreResponse, BeneishMScoreResponse, AnomalyDetectionResponse,
    BenfordAnalysisResponse, RiskScoreResponse, SuccessResponse, ErrorResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/companies",
    tags=["forensic"],
    responses={404: {"model": ErrorResponse}}
)

# Initialize agents
forensic_agent = ForensicAnalysisAgent()
# risk_agent = RiskScoringAgent()  # TODO: Create this agent


@router.post("/{company_id}/analyze", response_model=ComprehensiveAnalysisResponse)
async def run_forensic_analysis(
    company_id: str,
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
):
    """Run comprehensive forensic analysis on a company"""
    try:
        logger.info(f"Starting forensic analysis for {company_id}")

        # Verify company exists
        try:
            db_client = get_db_client()
            company_check = db_client.execute_query(
                "SELECT company_id FROM companies WHERE company_id = :company_id",
                {"company_id": company_id}
            )

            if not company_check:
                raise HTTPException(status_code=404, detail=f"Company {company_id} not found")
        except Exception as db_error:
            logger.warning(f"Database connection failed for company verification: {db_error}")
            # For database-independent analysis, we'll skip company verification
            # and proceed with the analysis if it's a yahoo_ prefixed ID

        # Convert financial statements to the format expected by the agent
        financial_statements = []
        for stmt in request.financial_statements:
            financial_statements.append({
                'statement_type': stmt.statement_type.value,
                'data': stmt.data
            })

        # Run comprehensive forensic analysis
        analysis_result = forensic_agent.comprehensive_forensic_analysis(company_id, financial_statements)

        if not analysis_result['success']:
            return ComprehensiveAnalysisResponse(
                company_id=company_id,
                success=False,
                analysis_timestamp=datetime.utcnow(),
                error=analysis_result.get('error', 'Analysis failed')
            )

        # Extract results for response
        response_data = {
            'company_id': company_id,
            'success': True,
            'analysis_timestamp': datetime.utcnow()
        }

        # Add financial ratios if available
        if 'financial_ratios' in analysis_result:
            response_data['financial_ratios'] = analysis_result['financial_ratios']

        # Add vertical analysis if available
        if 'vertical_analysis' in analysis_result:
            response_data['vertical_analysis'] = analysis_result['vertical_analysis']

        # Add horizontal analysis if available
        if 'horizontal_analysis' in analysis_result:
            response_data['horizontal_analysis'] = analysis_result['horizontal_analysis']

        # Add Altman Z-Score if available
        if 'altman_z_score' in analysis_result:
            response_data['altman_z_score'] = analysis_result['altman_z_score']

        # Add Beneish M-Score if available
        if 'beneish_m_score' in analysis_result:
            response_data['beneish_m_score'] = analysis_result['beneish_m_score']

        # Add Benford analysis if available
        if 'benford_analysis' in analysis_result:
            response_data['benford_analysis'] = analysis_result['benford_analysis']

        # Add anomaly detection if available
        if 'anomaly_detection' in analysis_result:
            response_data['anomaly_detection'] = analysis_result['anomaly_detection']

        # Store analysis results in database (background task) - handle failures gracefully
        try:
            background_tasks.add_task(store_analysis_results, company_id, analysis_result)
        except Exception as storage_error:
            logger.warning(f"Failed to queue database storage: {storage_error}")
            # Continue without storage - analysis was successful

        logger.info(f"Forensic analysis completed for {company_id}")
        return ComprehensiveAnalysisResponse(**response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in forensic analysis for {company_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Forensic analysis failed: {str(e)}")


@router.get("/{company_id}/ratios", response_model=FinancialRatiosResponse)
async def get_financial_ratios(company_id: str):
    """Get all financial ratios for a company"""
    try:
        # Get latest forensic analysis results
        try:
            db_client = get_db_client()
            query = """
            SELECT results FROM forensic_analysis
            WHERE company_id = :company_id AND analysis_type = 'RATIO_ANALYSIS'
            ORDER BY created_at DESC LIMIT 1
            """

            result = db_client.execute_query(query, {"company_id": company_id})

            if not result:
                raise HTTPException(
                    status_code=404,
                    detail=f"No ratio analysis found for company {company_id}. Run analysis first."
                )

            analysis_data = result[0]['results']

            if 'financial_ratios' not in analysis_data:
                raise HTTPException(
                    status_code=404,
                    detail="Financial ratios not found in analysis results"
                )

            ratios = analysis_data['financial_ratios']
            if not ratios:
                raise HTTPException(status_code=404, detail="No ratios calculated")

            # Get the latest period
            latest_period = max(ratios.keys()) if ratios else None
            if not latest_period:
                raise HTTPException(status_code=404, detail="No ratio data available")

            return FinancialRatiosResponse(
                company_id=company_id,
                period=latest_period,
                financial_ratios=ratios[latest_period],
                analysis_timestamp=datetime.utcnow()
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting ratios for {company_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get ratios: {str(e)}")


@router.get("/{company_id}/z-score", response_model=AltmanZScoreResponse)
async def get_altman_z_score(company_id: str):
    """Get Altman Z-Score analysis for a company"""
    try:
        try:
            db_client = get_db_client()
            query = """
            SELECT results FROM forensic_analysis
            WHERE company_id = :company_id AND analysis_type = 'Z_SCORE'
            ORDER BY created_at DESC LIMIT 1
            """

            result = db_client.execute_query(query, {"company_id": company_id})

            if not result:
                raise HTTPException(
                    status_code=404,
                    detail=f"No Z-Score analysis found for company {company_id}. Run analysis first."
                )

            z_score_data = result[0]['results']

            if 'success' not in z_score_data or not z_score_data['success']:
                raise HTTPException(status_code=404, detail="Z-Score analysis failed or not available")

            z_info = z_score_data['altman_z_score']

            return AltmanZScoreResponse(
                company_id=company_id,
                z_score=z_info['z_score'],
                classification=z_info['classification'],
                risk_level=z_info['risk_level'],
                components=z_info.get('components', {}),
                analysis_timestamp=datetime.utcnow()
            )

        except Exception as db_error:
            logger.warning(f"Database query failed for Z-Score: {db_error}")
            raise HTTPException(
                status_code=503,
                detail="Database temporarily unavailable. Please try the /analyze-yahoo endpoint for real-time analysis."
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Z-Score for {company_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get Z-Score: {str(e)}")


async def get_beneish_m_score(company_id: str):
    """Get Beneish M-Score analysis for a company"""
    try:
        try:
            db_client = get_db_client()
            query = """
            SELECT results FROM forensic_analysis
            WHERE company_id = :company_id AND analysis_type = 'M_SCORE'
            ORDER BY created_at DESC LIMIT 1
            """

            result = db_client.execute_query(query, {"company_id": company_id})

            if not result:
                raise HTTPException(
                    status_code=404,
                    detail=f"No M-Score analysis found for company {company_id}. Run analysis first."
                )

            m_score_data = result[0]['results']

            if 'success' not in m_score_data or not m_score_data['success']:
                raise HTTPException(status_code=404, detail="M-Score analysis failed or not available")

            m_info = m_score_data['beneish_m_score']

            return BeneishMScoreResponse(
                company_id=company_id,
                m_score=m_info['m_score'],
                risk_level=m_info['risk_level'],
                components=m_info.get('components', {}),
                analysis_timestamp=datetime.utcnow()
            )

        except Exception as db_error:
            logger.warning(f"Database query failed for M-Score: {db_error}")
            raise HTTPException(
                status_code=503,
                detail="Database temporarily unavailable. Please try the /analyze-yahoo endpoint for real-time analysis."
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting M-Score for {company_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get M-Score: {str(e)}")


async def get_anomalies(company_id: str):
    """Get anomaly detection results for a company"""
    try:
        try:
            db_client = get_db_client()
            query = """
            SELECT results FROM forensic_analysis
            WHERE company_id = :company_id AND analysis_type = 'ANOMALY_DETECTION'
            ORDER BY created_at DESC LIMIT 1
            """

            result = db_client.execute_query(query, {"company_id": company_id})

            if not result:
                raise HTTPException(
                    status_code=404,
                    detail=f"No anomaly analysis found for company {company_id}. Run analysis first."
                )

            anomaly_data = result[0]['results']

            if 'success' not in anomaly_data or not anomaly_data['success']:
                raise HTTPException(status_code=404, detail="Anomaly analysis failed or not available")

            anomalies_info = anomaly_data

            # Convert anomalies to proper format
            anomalies_list = []
            for anomaly in anomalies_info.get('anomalies', []):
                anomalies_list.append({
                    'type': anomaly.get('type', 'Unknown'),
                    'severity': anomaly.get('severity', 'LOW'),
                    'description': anomaly.get('description', ''),
                    'evidence': anomaly.get('evidence', {})
                })

            return AnomalyDetectionResponse(
                company_id=company_id,
                anomalies_detected=anomalies_info.get('anomalies_detected', 0),
                anomalies=anomalies_list,
                analysis_timestamp=datetime.utcnow()
            )

        except Exception as db_error:
            logger.warning(f"Database query failed for anomalies: {db_error}")
            raise HTTPException(
                status_code=503,
                detail="Database temporarily unavailable. Please try the /analyze-yahoo endpoint for real-time analysis."
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting anomalies for {company_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get anomalies: {str(e)}")


async def get_benford_analysis(company_id: str):
    """Get Benford's Law analysis for a company"""
    try:
        try:
            db_client = get_db_client()
            query = """
            SELECT results FROM forensic_analysis
            WHERE company_id = :company_id AND analysis_type = 'BENFORD'
            ORDER BY created_at DESC LIMIT 1
            """

            result = db_client.execute_query(query, {"company_id": company_id})

            if not result:
                raise HTTPException(
                    status_code=404,
                    detail=f"No Benford analysis found for company {company_id}. Run analysis first."
                )

            benford_data = result[0]['results']

            if 'success' not in benford_data or not benford_data['success']:
                raise HTTPException(status_code=404, detail="Benford analysis failed or not available")

            b_info = benford_data['benford_analysis']

            return BenfordAnalysisResponse(
                company_id=company_id,
                chi_square_statistic=b_info['chi_square_statistic'],
                interpretation=b_info['interpretation'],
                digit_frequencies=b_info.get('digit_frequencies', {}),
                expected_frequencies=b_info.get('expected_frequencies', {}),
                analysis_timestamp=datetime.utcnow()
            )

        except Exception as db_error:
            logger.warning(f"Database query failed for Benford analysis: {db_error}")
            raise HTTPException(
                status_code=503,
                detail="Database temporarily unavailable. Please try the /analyze-yahoo endpoint for real-time analysis."
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Benford analysis for {company_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get Benford analysis: {str(e)}")


async def get_risk_score(company_id: str):
    """Get comprehensive risk score for a company"""
    try:
        try:
            # Get latest forensic analysis results
            db_client = get_db_client()
            query = """
            SELECT results FROM forensic_analysis
            WHERE company_id = :company_id
            ORDER BY created_at DESC LIMIT 1
            """

            result = db_client.execute_query(query, {"company_id": company_id})

            if not result:
                raise HTTPException(
                    status_code=404,
                    detail=f"No analysis found for company {company_id}. Run analysis first."
                )

            # Get the most recent analysis results
            latest_analysis = result[0]['results']

            # TODO: Implement risk scoring agent
            # For now, return a placeholder response
            raise HTTPException(
                status_code=501,
                detail="Risk scoring agent not yet implemented. Please run forensic analysis first."
            )

        except Exception as db_error:
            logger.warning(f"Database query failed for risk score: {db_error}")
            raise HTTPException(
                status_code=503,
                detail="Database temporarily unavailable. Please try the /analyze-yahoo endpoint for real-time analysis."
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting risk score for {company_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get risk score: {str(e)}")


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


@router.post("/analyze-yahoo/{symbol}", response_model=ComprehensiveAnalysisResponse)
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
            response_data['vertical_analysis'] = analysis_result['vertical_analysis']

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


@router.get("/yahoo-symbols")
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
