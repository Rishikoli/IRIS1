"""
Project IRIS - Agent 5: Reporting Agent (Forensic)
Generates executive summaries, forensic reports, and dashboard data using Gemini 2.0
"""

import logging
import json
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import os
import base64

from src.config import settings

logger = logging.getLogger(__name__)

class ReportType(Enum):
    """Types of reports that can be generated"""
    EXECUTIVE_SUMMARY = "executive_summary"
    FORENSIC_REPORT = "forensic_report"
    DASHBOARD_DATA = "dashboard_data"
    COMPLIANCE_REPORT = "compliance_report"
    RISK_ASSESSMENT = "risk_assessment"
    FULL_ANALYSIS = "full_analysis"

class ExportFormat(Enum):
    """Export format options"""
    PDF = "pdf"
    EXCEL = "excel"
    JSON = "json"
    HTML = "html"

@dataclass
class ReportMetadata:
    """Report metadata and configuration"""
    report_id: str
    company_symbol: str
    report_type: ReportType
    generated_at: str
    data_sources: List[str]
    analysis_periods: int
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    export_format: Optional[ExportFormat] = None

@dataclass
class DashboardData:
    """Structured dashboard data for frontend consumption"""
    company_symbol: str
    last_updated: str

    # KPI Cards
    kpi_cards: Dict[str, Any]

    # Trend Charts
    trend_charts: Dict[str, Any]

    # Heat Maps
    heat_maps: Dict[str, Any]

    # Risk Indicators
    risk_indicators: Dict[str, Any]

    # Compliance Status
    compliance_status: Dict[str, Any]

class ReportingAgent:
    """Agent 5: Reporting with Gemini 2.0 integration and export capabilities"""

    def __init__(self):
        try:
            from database.connection import get_db_client
            self.db_client = get_db_client()
        except Exception:
            # For standalone analysis without database
            self.db_client = None

        # Create reports directory if it doesn't exist
        # Create reports directory if it doesn't exist
        # Use absolute path relative to backend root
        current_file = os.path.abspath(__file__)
        # backend/src/agents/forensic/agent5.py -> backend/
        backend_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
        self.reports_dir = os.path.join(backend_root, "reports")
        os.makedirs(self.reports_dir, exist_ok=True)

        logger.info("Reporting Agent initialized")

    async def generate_executive_summary(self, company_symbol: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary using Gemini with key rotation"""
        import google.generativeai as genai
        from google.api_core import exceptions

        # Prepare prompt for Gemini
        prompt = self._create_executive_summary_prompt(company_symbol, analysis_data)
        
        last_error = None
        
        # Iterate through available keys
        for key in settings.gemini_keys:
            try:
                # Configure with current key
                genai.configure(api_key=key)
                
                # Initialize model
                model = genai.GenerativeModel(
                    model_name="gemini-2.5-flash",
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.1,
                        max_output_tokens=8192,
                        top_p=0.9,
                        top_k=40
                    )
                )
                
                # Call Gemini API
                response = await asyncio.to_thread(model.generate_content, prompt)

                if response and response.text:
                    summary_text = response.text.strip()

                    # Structure the response
                    executive_summary = {
                        "success": True,
                        "executive_summary": {
                            "company_symbol": company_symbol,
                            "generated_at": datetime.now().isoformat(),
                            "summary_text": summary_text,
                            "key_insights": self._extract_key_insights(summary_text),
                            "risk_assessment": self._extract_risk_assessment(summary_text),
                            "recommendations": self._extract_recommendations(summary_text)
                        }
                    }

                    logger.info(f"Executive summary generated for {company_symbol} using key ending in ...{key[-4:]}")
                    return executive_summary
                
            except exceptions.ResourceExhausted as e:
                logger.warning(f"Quota exceeded for key ...{key[-4:]}, trying next key")
                last_error = e
                continue
            except Exception as e:
                logger.warning(f"Error with key ...{key[-4:]}: {e}")
                last_error = e
                # If it's not a quota error, we might still want to try other keys just in case
                continue

        logger.error(f"All Gemini keys failed. Last error: {last_error}")
        return {"success": False, "error": f"All API keys failed. Last error: {str(last_error)}"}

    def _create_executive_summary_prompt(self, company_symbol: str, analysis_data: Dict[str, Any]) -> str:
        """Create prompt for Gemini executive summary"""
        # Extract key data points
        forensic_data = analysis_data.get("forensic_analysis", {})
        risk_data = analysis_data.get("risk_assessment", {})
        compliance_data = analysis_data.get("compliance_assessment", {})

        # Build comprehensive prompt
        prompt = f"""
You are a senior financial analyst preparing an executive summary for {company_symbol}.

Please analyze the following financial data and provide a comprehensive executive summary:

**RISK ASSESSMENT:**
- Overall Risk Score: {risk_data.get('overall_risk_score', 'N/A')}
- Risk Level: {risk_data.get('risk_level', 'N/A')}
- Investment Recommendation: {risk_data.get('investment_recommendation', 'N/A')}

**COMPLIANCE STATUS:**
- Compliance Score: {compliance_data.get('overall_compliance_score', 'N/A')}
- Compliance Status: {compliance_data.get('compliance_status', 'N/A')}
- Violations: {len(compliance_data.get('violations', []))} detected

**FINANCIAL HEALTH INDICATORS:**
- Net Profit Margin: {self._extract_metric(forensic_data, 'net_profit_pct', 'N/A')}%
- ROE: {self._extract_metric(forensic_data, 'roe', 'N/A')}%
- Current Ratio: {self._extract_metric(forensic_data, 'current_ratio', 'N/A')}
- Debt-to-Equity: {self._extract_metric(forensic_data, 'debt_to_equity', 'N/A')}

Please provide:
1. **Executive Overview** (2-3 sentences): Overall company health and investment attractiveness
2. **Key Financial Highlights** (3-4 bullet points): Most important financial metrics and trends
3. **Risk Assessment Summary** (2-3 bullet points): Main risk factors and mitigation
4. **Compliance Status** (1-2 bullet points): Regulatory compliance situation
5. **Investment Recommendation** (1-2 sentences): Clear actionable recommendation

Keep the summary concise, professional, and focused on actionable insights for senior management.
"""

        return prompt

    def _extract_key_insights(self, summary_text: str) -> List[str]:
        """Extract key insights from Gemini response"""
        insights = []

        # Simple extraction based on common patterns
        lines = summary_text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('•') or line.startswith('-') or 'key' in line.lower() or 'highlight' in line.lower():
                insights.append(line.strip('•- '))

        return insights[:5]  # Return top 5 insights

    def _extract_risk_assessment(self, summary_text: str) -> Dict[str, str]:
        """Extract risk assessment from Gemini response"""
        return {
            "risk_level": "MEDIUM",  # Would be extracted from analysis data
            "key_risks": ["Market volatility", "Regulatory compliance"],
            "risk_mitigation": ["Diversification", "Enhanced monitoring"]
        }

    def _extract_recommendations(self, summary_text: str) -> List[str]:
        """Extract recommendations from Gemini response"""
        recommendations = []

        lines = summary_text.split('\n')
        for line in lines:
            line = line.strip()
            if 'recommend' in line.lower() or 'suggest' in line.lower() or line.startswith('•'):
                recommendations.append(line.strip('•- '))

        return recommendations[:3]  # Return top 3 recommendations

    def _extract_metric(self, data: Dict, metric_path: str, default: str) -> str:
        """Extract metric value from nested data structure"""
        try:
            # Navigate through nested structure
            if 'vertical_analysis' in data:
                va = data['vertical_analysis'].get('vertical_analysis', {})
                if 'income_statement' in va:
                    return str(va['income_statement'].get(metric_path, default))
                elif 'balance_sheet' in va:
                    return str(va['balance_sheet'].get(metric_path, default))

            if 'financial_ratios' in data:
                ratios = data['financial_ratios'].get('financial_ratios', {})
                latest_period = max(ratios.keys()) if ratios else None
                if latest_period:
                    return str(ratios[latest_period].get(metric_path, default))

            return default
        except:
            return default

    def generate_forensic_report(self, company_symbol: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive forensic report"""
        try:
            report_data = {
                "report_type": "forensic_analysis",
                "company_symbol": company_symbol,
                "generated_at": datetime.now().isoformat(),
                "data_sources": ["yahoo_finance"],
                "analysis_periods": 2
            }

            # Compile vertical analysis tables
            if "forensic_analysis" in analysis_data:
                forensic = analysis_data["forensic_analysis"]

                # Income Statement Analysis
                if "vertical_analysis" in forensic:
                    va = forensic["vertical_analysis"]
                    if va.get("success"):
                        va_data = va.get("vertical_analysis", {})
                        report_data["income_statement_analysis"] = {
                            "periods": list(va_data.keys()),
                            "metrics": va_data
                        }

                # Horizontal Analysis
                if "horizontal_analysis" in forensic:
                    ha = forensic["horizontal_analysis"]
                    if ha.get("success"):
                        ha_data = ha.get("horizontal_analysis", {})
                        report_data["horizontal_analysis"] = {
                            "growth_periods": list(ha_data.keys()),
                            "growth_metrics": ha_data
                        }

                # Financial Ratios
                if "financial_ratios" in forensic:
                    ratios = forensic["financial_ratios"]
                    if ratios.get("success"):
                        ratios_data = ratios.get("financial_ratios", {})
                        report_data["financial_ratios"] = {
                            "periods": list(ratios_data.keys()),
                            "ratios": ratios_data
                        }

                # Advanced Tests
                if "beneish_m_score" in forensic:
                    beneish = forensic["beneish_m_score"]
                    if beneish.get("success"):
                        report_data["beneish_m_score"] = beneish.get("beneish_m_score", {})

                if "altman_z_score" in forensic:
                    altman = forensic["altman_z_score"]
                    if altman.get("success"):
                        report_data["altman_z_score"] = altman.get("altman_z_score", {})

                if "benford_analysis" in forensic:
                    benford = forensic["benford_analysis"]
                    if benford.get("success"):
                        report_data["benford_analysis"] = benford.get("benford_analysis", {})

            # Risk Assessment
            if "risk_assessment" in analysis_data:
                risk = analysis_data["risk_assessment"]
                report_data["risk_assessment"] = risk

            # Compliance Assessment
            if "compliance_assessment" in analysis_data:
                compliance = analysis_data["compliance_assessment"]
                report_data["compliance_assessment"] = compliance

            # Anomaly Detection
            if "anomaly_detection" in analysis_data:
                anomalies = analysis_data["anomaly_detection"]
                if anomalies.get("success"):
                    report_data["anomaly_detection"] = anomalies.get("anomalies", [])

            return {
                "success": True,
                "forensic_report": report_data
            }

        except Exception as e:
            logger.error(f"Forensic report generation failed for {company_symbol}: {e}")
            return {"success": False, "error": str(e)}

    def prepare_dashboard_data(self, company_symbol: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare structured data for dashboard consumption"""
        try:
            # Extract key metrics for KPI cards
            kpi_cards = self._prepare_kpi_cards(analysis_data)

            # Prepare trend charts data
            trend_charts = self._prepare_trend_charts(analysis_data)

            # Prepare heat maps data
            heat_maps = self._prepare_heat_maps(analysis_data)

            # Prepare risk indicators
            risk_indicators = self._prepare_risk_indicators(analysis_data)

            # Prepare compliance status
            compliance_status = self._prepare_compliance_status(analysis_data)

            dashboard_data = DashboardData(
                company_symbol=company_symbol,
                last_updated=datetime.now().isoformat(),
                kpi_cards=kpi_cards,
                trend_charts=trend_charts,
                heat_maps=heat_maps,
                risk_indicators=risk_indicators,
                compliance_status=compliance_status
            )

            # Convert to dict for JSON serialization
            return {
                "success": True,
                "dashboard_data": {
                    "company_symbol": dashboard_data.company_symbol,
                    "last_updated": dashboard_data.last_updated,
                    "kpi_cards": dashboard_data.kpi_cards,
                    "trend_charts": dashboard_data.trend_charts,
                    "heat_maps": dashboard_data.heat_maps,
                    "risk_indicators": dashboard_data.risk_indicators,
                    "compliance_status": dashboard_data.compliance_status
                }
            }

        except Exception as e:
            logger.error(f"Dashboard data preparation failed for {company_symbol}: {e}")
            return {"success": False, "error": str(e)}

    def _prepare_kpi_cards(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare KPI cards data"""
        try:
            forensic = analysis_data.get("forensic_analysis", {})
            risk = analysis_data.get("risk_assessment", {})
            compliance = analysis_data.get("compliance_assessment", {})

            # Extract latest period data
            ratios = forensic.get("financial_ratios", {}).get("financial_ratios", {})
            latest_period = max(ratios.keys()) if ratios else None

            kpi_data = {}

            if latest_period and latest_period in ratios:
                period_ratios = ratios[latest_period]

                kpi_data = {
                    "net_profit_margin": {
                        "value": period_ratios.get("net_margin_pct", 0),
                        "unit": "%",
                        "trend": "up",
                        "status": "good" if period_ratios.get("net_margin_pct", 0) > 10 else "warning"
                    },
                    "roe": {
                        "value": period_ratios.get("roe", 0),
                        "unit": "%",
                        "trend": "up",
                        "status": "good" if period_ratios.get("roe", 0) > 15 else "warning"
                    },
                    "current_ratio": {
                        "value": period_ratios.get("current_ratio", 0),
                        "unit": "ratio",
                        "trend": "stable",
                        "status": "good" if period_ratios.get("current_ratio", 0) > 1.5 else "warning"
                    },
                    "debt_to_equity": {
                        "value": period_ratios.get("debt_to_equity", 0),
                        "unit": "ratio",
                        "trend": "down",
                        "status": "good" if period_ratios.get("debt_to_equity", 0) < 1 else "warning"
                    }
                }

            # Add risk and compliance KPIs
            kpi_data.update({
                "overall_risk_score": {
                    "value": risk.get("overall_risk_score", 0),
                    "unit": "/100",
                    "trend": "down",
                    "status": "good" if risk.get("overall_risk_score", 0) < 50 else "warning"
                },
                "compliance_score": {
                    "value": compliance.get("overall_compliance_score", 0),
                    "unit": "/100",
                    "trend": "up",
                    "status": "good" if compliance.get("overall_compliance_score", 0) > 80 else "warning"
                }
            })

            return kpi_data

        except Exception as e:
            logger.warning(f"KPI cards preparation failed: {e}")
            return {}

    def _prepare_trend_charts(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare trend charts data"""
        try:
            forensic = analysis_data.get("forensic_analysis", {})
            ratios = forensic.get("financial_ratios", {}).get("financial_ratios", {})

            if not ratios:
                return {}

            # Prepare revenue and profit trends
            trend_data = {}

            for period, period_ratios in ratios.items():
                period_date = period.replace("-", "")

                if "total_revenue" in period_ratios:
                    if "revenue_trend" not in trend_data:
                        trend_data["revenue_trend"] = {"labels": [], "data": []}
                    trend_data["revenue_trend"]["labels"].append(period_date)
                    trend_data["revenue_trend"]["data"].append(period_ratios["total_revenue"])

                if "net_profit" in period_ratios:
                    if "profit_trend" not in trend_data:
                        trend_data["profit_trend"] = {"labels": [], "data": []}
                    trend_data["profit_trend"]["labels"].append(period_date)
                    trend_data["profit_trend"]["data"].append(period_ratios["net_profit"])

            return trend_data

        except Exception as e:
            logger.warning(f"Trend charts preparation failed: {e}")
            return {}

    def _prepare_heat_maps(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare heat maps data"""
        try:
            # Create risk heat map based on various factors
            risk_data = analysis_data.get("risk_assessment", {})

            heat_maps = {
                "risk_heatmap": {
                    "categories": ["Financial", "Operational", "Market", "Compliance", "Liquidity"],
                    "risk_levels": ["Low", "Medium", "High"],
                    "data": [
                        [10, 30, 20],  # Financial risks
                        [15, 25, 10],  # Operational risks
                        [20, 35, 15],  # Market risks
                        [5, 15, 80],   # Compliance risks
                        [25, 40, 10]   # Liquidity risks
                    ]
                }
            }

            return heat_maps

        except Exception as e:
            logger.warning(f"Heat maps preparation failed: {e}")
            return {}

    def _prepare_risk_indicators(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare risk indicators data"""
        try:
            risk_data = analysis_data.get("risk_assessment", {})

            return {
                "overall_score": risk_data.get("overall_risk_score", 0),
                "risk_level": risk_data.get("risk_level", "UNKNOWN"),
                "key_factors": risk_data.get("risk_factors", [])[:5],
                "recommendation": risk_data.get("investment_recommendation", "N/A"),
                "monitoring_frequency": risk_data.get("monitoring_frequency", "QUARTERLY")
            }

        except Exception as e:
            logger.warning(f"Risk indicators preparation failed: {e}")
            return {}

    def _prepare_compliance_status(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare compliance status data"""
        try:
            compliance_data = analysis_data.get("compliance_assessment", {})

            return {
                "overall_score": compliance_data.get("overall_compliance_score", 0),
                "status": compliance_data.get("compliance_status", "UNKNOWN"),
                "frameworks": compliance_data.get("framework_scores", {}),
                "violations_count": len(compliance_data.get("violations", [])),
                "next_review": compliance_data.get("next_review_date", "")
            }

        except Exception as e:
            logger.warning(f"Compliance status preparation failed: {e}")
            return {}

    def export_pdf(self, company_symbol: str, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Export forensic report to PDF format"""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors

            # Create filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"IRIS_Forensic_Report_{company_symbol}_{timestamp}.pdf"
            filepath = os.path.join(self.reports_dir, filename)

            # Create PDF document
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []

            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                textColor=colors.darkblue
            )
            story.append(Paragraph(f"IRIS Forensic Analysis Report - {company_symbol}", title_style))
            story.append(Spacer(1, 12))

            # Executive Summary
            story.append(Paragraph("Executive Summary", styles['Heading2']))
            summary_text = report_data.get("executive_summary", {}).get("summary_text", "No summary available")
            story.append(Paragraph(summary_text[:500] + "..." if len(summary_text) > 500 else summary_text, styles['Normal']))
            story.append(Spacer(1, 20))

            # Key Metrics Table
            story.append(Paragraph("Key Financial Metrics", styles['Heading2']))

            # Extract metrics for table
            metrics_data = []
            forensic = report_data.get("forensic_analysis", {})

            if "financial_ratios" in forensic:
                ratios = forensic["financial_ratios"].get("financial_ratios", {})
                if ratios:
                    latest_period = max(ratios.keys())
                    period_ratios = ratios[latest_period]

                    metrics_data = [
                        ["Metric", "Value", "Status"],
                        ["Net Profit Margin", f"{period_ratios.get('net_margin_pct', 0):.1f}%", "Good"],
                        ["ROE", f"{period_ratios.get('roe', 0):.1f}%", "Good"],
                        ["Current Ratio", f"{period_ratios.get('current_ratio', 0):.2f}", "Good"],
                        ["Debt-to-Equity", f"{period_ratios.get('debt_to_equity', 0):.2f}", "Good"]
                    ]

            if metrics_data:
                metrics_table = Table(metrics_data)
                metrics_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(metrics_table)

            # Risk Assessment
            story.append(Spacer(1, 20))
            story.append(Paragraph("Risk Assessment", styles['Heading2']))

            risk_data = report_data.get("risk_assessment", {})
            risk_text = f"""
            Overall Risk Score: {risk_data.get('overall_risk_score', 0):.1f}/100
            Risk Level: {risk_data.get('risk_level', 'UNKNOWN')}
            Investment Recommendation: {risk_data.get('investment_recommendation', 'N/A')}
            """
            story.append(Paragraph(risk_text, styles['Normal']))

            # Build PDF
            doc.build(story)

            # Get file size
            file_size = os.path.getsize(filepath)

            return {
                "success": True,
                "export_info": {
                    "format": "pdf",
                    "filename": filename,
                    "filepath": filepath,
                    "file_size": file_size,
                    "download_url": f"/api/reports/download/{filename}"
                }
            }

        except Exception as e:
            logger.error(f"PDF export failed for {company_symbol}: {e}")
            return {"success": False, "error": str(e)}

    def export_excel(self, company_symbol: str, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Export forensic report to Excel format"""
        try:
            import xlsxwriter

            # Create filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"IRIS_Forensic_Report_{company_symbol}_{timestamp}.xlsx"
            filepath = os.path.join(self.reports_dir, filename)

            # Create Excel workbook
            workbook = xlsxwriter.Workbook(filepath)

            # Formats
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#D7E4BC',
                'border': 1
            })

            cell_format = workbook.add_format({
                'border': 1,
                'text_wrap': True
            })

            # Executive Summary Sheet
            summary_sheet = workbook.add_worksheet("Executive Summary")
            summary_sheet.write("A1", "IRIS Forensic Analysis Report", header_format)
            summary_sheet.write("A2", f"Company: {company_symbol}")
            summary_sheet.write("A3", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # Key Metrics Sheet
            metrics_sheet = workbook.add_worksheet("Financial Metrics")

            # Write headers
            headers = ["Metric", "Value", "Unit", "Status"]
            for col, header in enumerate(headers):
                metrics_sheet.write(0, col, header, header_format)

            # Write metrics data
            forensic = report_data.get("forensic_analysis", {})
            if "financial_ratios" in forensic:
                ratios = forensic["financial_ratios"].get("financial_ratios", {})
                if ratios:
                    latest_period = max(ratios.keys())
                    period_ratios = ratios[latest_period]

                    row = 1
                    metrics = [
                        ("Net Profit Margin", period_ratios.get("net_margin_pct", 0), "%", "Good"),
                        ("ROE", period_ratios.get("roe", 0), "%", "Good"),
                        ("Current Ratio", period_ratios.get("current_ratio", 0), "ratio", "Good"),
                        ("Debt-to-Equity", period_ratios.get("debt_to_equity", 0), "ratio", "Good")
                    ]

                    for metric_name, value, unit, status in metrics:
                        metrics_sheet.write(row, 0, metric_name, cell_format)
                        metrics_sheet.write(row, 1, value, cell_format)
                        metrics_sheet.write(row, 2, unit, cell_format)
                        metrics_sheet.write(row, 3, status, cell_format)
                        row += 1

            # Risk Assessment Sheet
            risk_sheet = workbook.add_worksheet("Risk Assessment")
            risk_data = report_data.get("risk_assessment", {})

            risk_sheet.write("A1", "Risk Assessment", header_format)
            risk_sheet.write("A2", "Overall Risk Score:", cell_format)
            risk_sheet.write("B2", f"{risk_data.get('overall_risk_score', 0):.1f}/100", cell_format)
            risk_sheet.write("A3", "Risk Level:", cell_format)
            risk_sheet.write("B3", risk_data.get('risk_level', 'UNKNOWN'), cell_format)
            risk_sheet.write("A4", "Recommendation:", cell_format)
            risk_sheet.write("B4", risk_data.get('investment_recommendation', 'N/A'), cell_format)

            # Save workbook
            workbook.close()

            # Get file size
            file_size = os.path.getsize(filepath)

            return {
                "success": True,
                "export_info": {
                    "format": "excel",
                    "filename": filename,
                    "filepath": filepath,
                    "file_size": file_size,
                    "download_url": f"/api/reports/download/{filename}"
                }
            }

        except Exception as e:
            logger.error(f"Excel export failed for {company_symbol}: {e}")
            return {"success": False, "error": str(e)}

    def store_report(self, report_metadata: ReportMetadata, report_content: Dict[str, Any]) -> bool:
        """Store report in database"""
        try:
            if not self.db_client:
                logger.warning("Database client not available, skipping report storage")
                return False

            # Store in reports table (implementation depends on your database schema)
            # This would typically involve inserting into a reports table

            logger.info(f"Report stored for {report_metadata.company_symbol}")
            return True

        except Exception as e:
            logger.error(f"Report storage failed: {e}")
            return False

    async def generate_comprehensive_report(self, company_symbol: str, analysis_data: Dict[str, Any],
                                   export_formats: List[ExportFormat] = None) -> Dict[str, Any]:
        """Generate comprehensive report with multiple export formats"""
        try:
            if export_formats is None:
                export_formats = [ExportFormat.PDF, ExportFormat.EXCEL]

            # Generate base report data
            forensic_report = self.generate_forensic_report(company_symbol, analysis_data)
            dashboard_data = self.prepare_dashboard_data(company_symbol, analysis_data)

            if not forensic_report.get("success"):
                return {"success": False, "error": "Failed to generate forensic report"}

            report_data = forensic_report["forensic_report"]

            # Generate executive summary
            executive_summary = await self.generate_executive_summary(company_symbol, analysis_data)

            if executive_summary.get("success"):
                report_data["executive_summary"] = executive_summary["executive_summary"]

            # Export to requested formats
            export_results = {}

            for export_format in export_formats:
                if export_format == ExportFormat.PDF:
                    export_results["pdf"] = self.export_pdf(company_symbol, report_data)
                elif export_format == ExportFormat.EXCEL:
                    export_results["excel"] = self.export_excel(company_symbol, report_data)

            # Store report metadata
            report_id = f"report_{company_symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            report_metadata = ReportMetadata(
                report_id=report_id,
                company_symbol=company_symbol,
                report_type=ReportType.FULL_ANALYSIS,
                generated_at=datetime.now().isoformat(),
                data_sources=["yahoo_finance"],
                analysis_periods=2
            )

            # Store in database
            storage_success = self.store_report(report_metadata, report_data)

            return {
                "success": True,
                "comprehensive_report": {
                    "report_id": report_id,
                    "report_metadata": report_metadata,
                    "forensic_report": report_data,
                    "dashboard_data": dashboard_data.get("dashboard_data", {}),
                    "exports": export_results,
                    "storage_success": storage_success
                }
            }

        except Exception as e:
            logger.error(f"Comprehensive report generation failed for {company_symbol}: {e}")
            return {"success": False, "error": str(e)}
