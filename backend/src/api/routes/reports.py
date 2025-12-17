"""
Project IRIS - Reports API Routes
Comprehensive report generation and download endpoints using Agent 5.
"""

import logging
import os
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException
from datetime import datetime
from src.agents.forensic.agent5_reporting import ReportingAgent, ExportFormat
from src.api.routes.forensic import ingest_company_data, _create_enhanced_mock_data
from src.agents.forensic.agent2_forensic_analysis import ForensicAnalysisAgent
from src.agents.forensic.agent3_risk_scoring import RiskScoringAgent
from src.agents.forensic.agent4_compliance import ComplianceValidationAgent

logger = logging.getLogger(__name__)

# Initialize router
reports_router = APIRouter(prefix="/api/reports", tags=["reports"])

# Initialize agents
reporting_agent = ReportingAgent()
forensic_agent = ForensicAnalysisAgent()
risk_agent = RiskScoringAgent()
compliance_agent = ComplianceValidationAgent()


@reports_router.post("/generate")
async def generate_reports_api(request: Dict[str, Any]):
    """Generate comprehensive reports for a company"""
    print(f"DEBUG: Received report request: {request}")
    try:
        company_symbol = request.get('company_symbol')
        export_formats = request.get('export_formats', ['pdf', 'excel'])
        include_summary = request.get('include_summary', True)

        if not company_symbol:
            raise HTTPException(
                status_code=400,
                detail="Company symbol is required"
            )

        logger.info(f"Generating reports for {company_symbol} with formats: {export_formats}")

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

        # Convert format strings to ExportFormat enums
        format_enums = []
        for fmt in export_formats:
            if fmt.lower() == 'pdf':
                format_enums.append(ExportFormat.PDF)
            elif fmt.lower() == 'excel':
                format_enums.append(ExportFormat.EXCEL)
            elif fmt.lower() == 'html':
                format_enums.append(ExportFormat.HTML)
            elif fmt.lower() == 'json':
                format_enums.append(ExportFormat.JSON)

        # Generate comprehensive report using Agent 5
        comprehensive_report = await reporting_agent.generate_comprehensive_report(
            company_symbol,
            analysis_data,
            export_formats=format_enums
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
        logger.error(f"Error generating reports: {e}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@reports_router.get("/download/{filename}")
async def download_report_api(filename: str):
    """Download a generated report file"""
    try:
        # Construct file path - check multiple possible locations
        # Construct file path - check multiple possible locations
        current_file = os.path.abspath(__file__)
        backend_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
        reports_dir = os.path.join(backend_root, "reports")
        
        possible_paths = [
            os.path.join(reports_dir, filename),
            f"reports/{filename}",
        ]

        file_path = None
        for path in possible_paths:
            if os.path.exists(path):
                file_path = path
                break

        if not file_path:
            raise HTTPException(
                status_code=404,
                detail=f"Report file not found: {filename}"
            )

        # Determine file type for proper headers
        if filename.endswith('.pdf'):
            media_type = "application/pdf"
        elif filename.endswith('.xlsx'):
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif filename.endswith('.html'):
            media_type = "text/html"
        elif filename.endswith('.json'):
            media_type = "application/json"
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
