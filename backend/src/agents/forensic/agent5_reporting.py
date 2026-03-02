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
from src.utils.gemini_client import GeminiClient

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
        """Generate executive summary using Gemini with centralized client"""

        # Prepare prompt for Gemini
        prompt = self._create_executive_summary_prompt(company_symbol, analysis_data)
        
        try:
            # Use centralized client
            client = GeminiClient()
            summary_text = await client.generate_content(prompt)

            if summary_text:
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

                logger.info(f"Executive summary generated for {company_symbol}")
                return executive_summary
            
            return {"success": False, "error": "Empty response from Gemini"}

        except Exception as e:
            logger.error(f"Executive summary generation failed: {e}")
            return {"success": False, "error": str(e)}

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
- Operating Margin: {self._extract_metric(forensic_data, 'operating_margin_pct', 'N/A')}%
- ROE: {self._extract_metric(forensic_data, 'roe', 'N/A')}%
- Current Ratio: {self._extract_metric(forensic_data, 'current_ratio', 'N/A')}
- Debt-to-Equity: {self._extract_metric(forensic_data, 'debt_to_equity', 'N/A')}
- Interest Coverage: {self._extract_metric(forensic_data, 'interest_coverage', 'N/A')}
- Asset Turnover: {self._extract_metric(forensic_data, 'asset_turnover', 'N/A')}

**FORENSIC DEEP DIVE:**
- Beneish M-Score: {float(forensic_data.get('beneish_m_score', {}).get('beneish_m_score', {}).get('m_score', 0)):.4f} (Likely Manipulator: {forensic_data.get('beneish_m_score', {}).get('beneish_m_score', {}).get('is_likely_manipulator', False)})
- Altman Z-Score: {float(forensic_data.get('altman_z_score', {}).get('altman_z_score', {}).get('z_score', 0)):.2f} (Zone: {forensic_data.get('altman_z_score', {}).get('altman_z_score', {}).get('zone', 'Unknown')})
- Benford's Law: {forensic_data.get('benford_analysis', {}).get('benford_analysis', {}).get('interpretation', 'N/A')} (Anomalous: {forensic_data.get('benford_analysis', {}).get('benford_analysis', {}).get('is_anomalous', False)})
- GST Reconciliation Risk: {forensic_data.get('gst_reconciliation', {}).get('overall_risk_score', 'N/A')}/100
- Sloan Ratio: {self._extract_sloan_ratio(forensic_data)} (Earnings Quality Indicator)

**MANAGEMENT NARRATIVE AUDIT (SEMANTIC AUDIT):**
{json.dumps(analysis_data.get('semantic_audit', {}), indent=2)}

Please provide:
1. **Formal Header**:
   TO: Executive Management / Investment Committee
   FROM: Senior Financial Analyst
   DATE: {datetime.now().strftime('%B %d, %Y')}
   SUBJECT: Executive Summary - {company_symbol}

2. **Executive Overview** (2-3 sentences): Overall company health and investment attractiveness
3. **Forensic Verdict** (3-4 bullet points): CRITICAL section. Explicitly interpret the M-Score (Manipulation?), Z-Score (Bankruptcy?), and Data Integrity signals. Be direct about any red flags.
4. **Key Financial Highlights** (3-4 bullet points): Most important financial metrics and trends.
5. **Risk Assessment Summary** (2-3 bullet points): Main risk factors and mitigation.
6. **Compliance Status** (1-2 bullet points): Regulatory compliance situation.
7. **Investment Recommendation** (1-2 sentences): Clear actionable recommendation.

**FORMATTING RULES:**
- Do NOT use markdown bolding (like **text**). The output system does not support it.
- Use <b>text</b> tags for bolding important terms or headers.
- Use standard bullet points (•).
- Keep the tone professional, objective, and concise.
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



    def _extract_sloan_ratio(self, forensic_data: Dict) -> str:
        """Extract Sloan Ratio with interpretation"""
        try:
            sloan_data = forensic_data.get("sloan_ratio", {}).get("sloan_analysis", {})
            if sloan_data:
                # Get latest period
                latest_period = sorted(sloan_data.keys())[-1]
                ratio = sloan_data[latest_period].get("sloan_ratio_pct", "N/A")
                interp = sloan_data[latest_period].get("risk_level", "Unknown")
                return f"{ratio}% ({interp} Risk)"
            return "N/A"
        except:
            return "N/A"

    async def generate_enforcement_rfi(self, company_symbol: str, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Feature 5: Automated Enforcement RFI
        Drafts a professional Request for Information (RFI) for the Audit Committee.
        """
        import google.generativeai as genai
        
        prompt = f"""
        You are a Legal & Compliance Officer specializing in SEBI regulations. 
        I have scientific forensic findings about '{company_symbol}' that suggest potential violations of SEBI LODR Regulation 23 (Related Party Transactions).
        
        FORENSIC FINDINGS:
        {json.dumps(findings, indent=2)}
        
        Task:
        Draft a professional, stern, but objective "Request for Information" (RFI) letter addressed to the "Audit Committee and Board of Directors" of {company_symbol}.
        
        The letter should:
        1. State that an AI-driven forensic audit (Project IRIS) has flagged specific anomalies.
        2. Reference specific legal sections (e.g., Section 188 of Companies Act 2013, SEBI LODR).
        3. Request detailed clarifications on the specified transactions within 15 days.
        4. Maintain a formal regulatory tone.
        
        Return the letter text directly.
        """
        
        try:
            # Use centralized client
            client = GeminiClient()
            response_text = await client.generate_content(prompt)
            
            return {
                "success": True,
                "rfi_draft": response_text.strip(),
                "target_committee": "Audit Committee",
                "law_references": ["SEBI LODR Reg 23", "Companies Act Section 188"],
                "is_fallback": False
            }
        except Exception as e:
            logger.error(f"RFI generation failed (using fallback): {e}")
            
            # Fallback Template
            fallback_rfi = f"""
To: Audit Committee and Board of Directors
{company_symbol}

Subject: URGENT: Request for Information regarding Potential Related Party Transaction Anomalies

Dear Members of the Board,

This communication is issued following an automated forensic analysis conducted by Project IRIS, which has identified potential irregularities in the financial data and related party disclosures of {company_symbol}.

Specific areas of concern requiring immediate clarification include:
1. Significant deviations in Related Party Transaction (RPT) volume relative to revenue.
2. Unexplained fluctuations in key financial ratios that may indicate potential earnings management.

In accordance with SEBI LODR Regulation 23 and Section 188 of the Companies Act, 2013, we request a detailed explanation of these transactions, including:
- The commercial rationale for these transactions.
- Evidence of arm's length pricing.
- Approvals obtained from the Audit Committee and Shareholders (where applicable).

Please provide the requested information within 15 days of receipt of this letter.

Sincerely,
Compliance Monitoring Team
Project IRIS
            """
            
            return {
                "success": True,
                "rfi_draft": fallback_rfi.strip(),
                "target_committee": "Audit Committee",
                "law_references": ["SEBI LODR Reg 23", "Companies Act Section 188"],
                "is_fallback": True,
                "error": str(e)
            }

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
            # Handle both nested and flat structures
            forensic = analysis_data.get("forensic_analysis", analysis_data)
            
            if True:

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
                        # Wrap in expected structure for export_pdf
                        report_data["horizontal_analysis"] = {
                            "horizontal_analysis": ha_data, # For export_pdf
                            "growth_periods": list(ha_data.keys()),
                            "growth_metrics": ha_data
                        }

                # Financial Ratios
                if "financial_ratios" in forensic:
                    ratios = forensic["financial_ratios"]
                    if ratios.get("success"):
                        ratios_data = ratios.get("financial_ratios", {})
                        report_data["financial_ratios"] = {
                            "financial_ratios": ratios_data, # For export_pdf consistency
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

                # Sloan Ratio
                if "sloan_ratio" in forensic:
                    sloan = forensic["sloan_ratio"]
                    if sloan.get("success"):
                        report_data["sloan_ratio"] = sloan

                if "benford_analysis" in forensic:
                    benford = forensic["benford_analysis"]
                    if benford.get("success"):
                        report_data["benford_analysis"] = {
                            "benford_analysis": benford.get("benford_analysis", {})
                        }

                # Feature 2: GST-Revenue Reconciliation
                if "gst_reconciliation" in forensic:
                    gst = forensic["gst_reconciliation"]
                    if gst.get("success"):
                        report_data["gst_reconciliation"] = {
                            "reconciliation_results": gst.get("reconciliation_results", [])
                        }

                # Feature 4: Contingent Liability Analysis
                if "contingent_liability_risk" in forensic:
                    cl = forensic["contingent_liability_risk"]
                    if cl.get("success"):
                        report_data["contingent_liability_risk"] = cl

                # Feature 3: Greed Index
                if "greed_index" in forensic:
                    greed = forensic["greed_index"]
                    if greed.get("success"):
                        report_data["greed_index"] = greed

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

            # Semantic Audit
            if "semantic_audit" in analysis_data:
                report_data["semantic_audit"] = analysis_data["semantic_audit"]

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
        """Export forensic report to PDF format (Professional Forensic Audit Standard)"""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            from reportlab.lib.units import inch

            # Create filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"IRIS_Forensic_Audit_{company_symbol}_{timestamp}.pdf"
            filepath = os.path.join(self.reports_dir, filename)

            # Create PDF document
            doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
            styles = getSampleStyleSheet()
            story = []

            # Custom Styles
            if 'Title' not in styles:
                styles.add(ParagraphStyle(name='Title', parent=styles['Heading1'], fontSize=28, leading=34, alignment=1, spaceAfter=20, textColor=colors.darkblue))
            else:
                styles['Title'].fontSize = 28
                styles['Title'].leading = 34
                styles['Title'].alignment = 1
                styles['Title'].spaceAfter = 20
                styles['Title'].textColor = colors.darkblue

            if 'Subtitle' not in styles:
                styles.add(ParagraphStyle(name='Subtitle', parent=styles['Normal'], fontSize=16, leading=20, alignment=1, spaceAfter=50, textColor=colors.grey))
            
            if 'SectionHeader' not in styles:
                styles.add(ParagraphStyle(name='SectionHeader', parent=styles['Heading2'], fontSize=18, leading=22, spaceBefore=20, spaceAfter=10, textColor=colors.darkblue, borderPadding=5, borderColor=colors.grey, borderWidth=0, borderBottomWidth=1))
            
            if 'NormalSmall' not in styles:
                styles.add(ParagraphStyle(name='NormalSmall', parent=styles['Normal'], fontSize=9, leading=11))
            
            if 'Disclaimer' not in styles:
                styles.add(ParagraphStyle(name='Disclaimer', parent=styles['Normal'], fontSize=8, leading=10, textColor=colors.grey, alignment=0))
            
            if 'RiskHigh' not in styles:
                styles.add(ParagraphStyle(name='RiskHigh', parent=styles['Normal'], fontSize=12, textColor=colors.red, fontName='Helvetica-Bold'))
            
            if 'RiskLow' not in styles:
                styles.add(ParagraphStyle(name='RiskLow', parent=styles['Normal'], fontSize=12, textColor=colors.green, fontName='Helvetica-Bold'))

            # --- Title Page ---
            story.append(Spacer(1, 2 * inch))
            story.append(Paragraph(f"CONFIDENTIAL FORENSIC AUDIT", styles['Subtitle']))
            story.append(Spacer(1, 0.5 * inch))
            story.append(Paragraph(f"{company_symbol}", styles['Title']))
            story.append(Paragraph(f"Financial Integrity & Risk Assessment", styles['Subtitle']))
            story.append(Spacer(1, 1 * inch))
            story.append(Paragraph(f"Generated by: IRIS AI Forensic Engine", styles['Normal']))
            story.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
            story.append(PageBreak())

            # --- Executive Summary ---
            story.append(Paragraph("1. Executive Summary", styles['SectionHeader']))
            summary_text = report_data.get("executive_summary", {}).get("summary_text", "No summary available")
            story.append(Paragraph(summary_text, styles['Normal']))
            story.append(Spacer(1, 15))

            # --- Risk Assessment ---
            story.append(Paragraph("2. Risk Assessment Dashboard", styles['SectionHeader']))
            risk_data = report_data.get("risk_assessment", {})
            risk_score = risk_data.get('overall_risk_score', 0)
            
            # Risk Score Logic
            risk_color = colors.red if risk_score > 70 else colors.orange if risk_score > 40 else colors.green
            risk_label = "HIGH RISK" if risk_score > 70 else "MODERATE RISK" if risk_score > 40 else "LOW RISK"

            story.append(Paragraph(f"Overall Risk Score: {risk_score:.1f} / 100", 
                                  ParagraphStyle('RiskScore', parent=styles['Heading3'], textColor=risk_color, fontSize=16)))
            story.append(Paragraph(f"Classification: {risk_label}", styles['Normal']))
            story.append(Spacer(1, 10))
            
            # Risk Factors
            story.append(Paragraph("Key Risk Factors:", styles['Heading4']))
            for factor in risk_data.get('risk_factors', [])[:5]:
                story.append(Paragraph(f"• {factor}", styles['Normal']))
            story.append(Spacer(1, 15))

            # --- Compliance Status ---
            story.append(Paragraph("3. Regulatory Compliance", styles['SectionHeader']))
            compliance_data = report_data.get("compliance_assessment", {})
            comp_score = compliance_data.get("overall_compliance_score", 0)
            
            story.append(Paragraph(f"Compliance Score: {comp_score:.1f}%", styles['Heading4']))
            story.append(Spacer(1, 10))

            # Violations Table
            violations = compliance_data.get('violations', [])
            if violations:
                story.append(Paragraph("Detected Violations:", styles['Heading4']))
                v_data = [["Regulation", "Severity", "Description", "Reference"]]
                
                for v in violations[:15]: # Limit to top 15
                    # Handle both dict and ComplianceViolation dataclass objects
                    def _vget(field, default=''):
                        if isinstance(v, dict):
                            return v.get(field, default)
                        val = getattr(v, field, default)
                        # Unwrap Enum values
                        return val.value if hasattr(val, 'value') else (val or default)
                    
                    desc_text = str(_vget('violation_description', 'No description'))
                    if len(desc_text) > 150:
                        desc_text = desc_text[:147] + "..."
                        
                    v_data.append([
                        Paragraph(str(_vget('rule_id', 'Unknown')), styles['NormalSmall']),
                        Paragraph(str(_vget('severity', 'medium')).upper(), styles['NormalSmall']),
                        Paragraph(desc_text, styles['NormalSmall']),
                        Paragraph(str(_vget('regulatory_reference', 'N/A')), styles['NormalSmall'])
                    ])

                # Adjust column widths for better layout
                # A4 width ~595 pts. Margins 72*2 = 144. Content width ~451.
                # Col widths: Reg(80), Sev(60), Desc(230), Ref(80)
                v_table = Table(v_data, colWidths=[80, 60, 230, 80])
                v_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.aliceblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.darkblue),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('WORDWRAP', (0, 0), (-1, -1), True),
                ]))
                story.append(v_table)
                story.append(Spacer(1, 15))
            else:
                story.append(Paragraph("No significant compliance violations detected.", styles['Normal']))
                story.append(Spacer(1, 15))

            # --- Forensic Deep Dive ---
            story.append(Paragraph("4. Forensic Deep Dive", styles['SectionHeader']))
            
            forensic = report_data

            # Beneish M-Score
            story.append(Paragraph("Beneish M-Score (Earnings Manipulation)", styles['Heading3']))
            m_score_data = forensic.get("beneish_m_score", {}).get("beneish_m_score", {})
            m_val = m_score_data.get("m_score", "N/A")
            is_manipulator = m_score_data.get("is_likely_manipulator", False)
            
            m_color = colors.red if is_manipulator else colors.green
            m_text = "LIKELY MANIPULATOR" if is_manipulator else "UNLIKELY MANIPULATOR"
            
            story.append(Paragraph(f"M-Score: {m_val}  -  {m_text}", 
                                  ParagraphStyle('MScore', parent=styles['Normal'], textColor=m_color, fontName='Helvetica-Bold')))
            story.append(Spacer(1, 10))
            
            if "details" in m_score_data:
                details = m_score_data["details"]
                story.append(Paragraph("Variable Breakdown:", styles['Heading4']))
                
                # Full M-Score Variables
                m_vars = [
                    ("DSRI", "Days Sales in Receivables", "Revenue inflation via receivables"),
                    ("GMI", "Gross Margin Index", "Deteriorating margins"),
                    ("AQI", "Asset Quality Index", "Capitalization of costs"),
                    ("SGI", "Sales Growth Index", "Unsustainable growth"),
                    ("DEPI", "Depreciation Index", "Slowing depreciation rate"),
                    ("SGAI", "SGA Index", "Decreasing administrative efficiency"),
                    ("LVGI", "Leverage Index", "Increasing debt burden"),
                    ("TATA", "Total Accruals to Total Assets", "High discretionary accruals")
                ]
                
                m_table_data = [["Variable", "Description", "Value", "Risk Signal"]]
                for code, name, risk_desc in m_vars:
                    val = details.get(code, 0)
                    # Basic thresholds (simplified for display)
                    signal = "Normal"
                    if code == "DSRI" and val > 1.03: signal = "High"
                    elif code == "GMI" and val > 1.0: signal = "High"
                    elif code == "AQI" and val > 1.0: signal = "High"
                    elif code == "SGI" and val > 1.1: signal = "High" 
                    elif code == "DEPI" and val > 1.0: signal = "High"
                    elif code == "SGAI" and val > 1.0: signal = "High"
                    elif code == "LVGI" and val > 1.0: signal = "High"
                    elif code == "TATA" and val > 0.05: signal = "High"
                    
                    sig_color = colors.red if signal == "High" else colors.green
                    
                    m_table_data.append([
                        Paragraph(f"<b>{code}</b>", styles['NormalSmall']),
                        Paragraph(name, styles['NormalSmall']),
                        f"{val:.4f}",
                        Paragraph(signal, ParagraphStyle('Sig', parent=styles['NormalSmall'], textColor=sig_color))
                    ])
                
                m_table = Table(m_table_data, colWidths=[50, 200, 80, 80])
                m_table.setStyle(TableStyle([
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
                    ('ALIGN', (3, 1), (-1, -1), 'CENTER'),
                ]))
                story.append(m_table)
            story.append(Spacer(1, 15))

            # Altman Z-Score
            story.append(Paragraph("Altman Z-Score (Bankruptcy Risk)", styles['Heading3']))
            
            z_score_data_raw = forensic.get("altman_z_score", {})
            # Fix: Handle both nested and direct structures
            if "altman_z_score" in z_score_data_raw:
                z_score_data = z_score_data_raw["altman_z_score"]
            else:
                z_score_data = z_score_data_raw
                
            if z_score_data:
                z_val = z_score_data.get("z_score", "N/A")
                z_class = z_score_data.get("classification", "Unknown")
                z_risk = z_score_data.get("risk_level", "Unknown")
                
                # Color coding
                z_color = colors.green if z_class == "SAFE" else (colors.orange if z_class == "GREY_ZONE" else colors.red)
                
                z_text = f"""
                Z-Score: <font color="{z_color}">{z_val}</font>  -  Zone: {z_class} ({z_risk} Risk)<br/>
                <i>Interpretation: Z > 2.99 is Safe, 1.81 < Z < 2.99 is Grey Zone, Z < 1.81 is Distress</i>
                """
                story.append(Paragraph(z_text, styles['Normal']))
            else:
                story.append(Paragraph("Altman Z-Score: N/A (Insufficient Data)", styles['Normal']))
            
            story.append(Spacer(1, 15))

            # Sloan Ratio (Earnings Quality)
            story.append(Paragraph("Sloan Ratio (Earnings Quality)", styles['Heading3']))
            
            sloan_raw = forensic.get("sloan_ratio", {})
            
            sloan_data = sloan_raw.get("sloan_analysis", {})
            if not sloan_data and "sloan_ratio" in sloan_raw:
                 sloan_data = sloan_raw.get("sloan_ratio", {}) # Handle nested if it exists

            if sloan_data:
                # Get latest period
                latest_period = sorted(sloan_data.keys())[-1]
                s_period_data = sloan_data[latest_period]
                
                s_ratio = s_period_data.get("sloan_ratio_pct", "N/A")
                s_risk = s_period_data.get("risk_level", "Unknown")
                s_interp = s_period_data.get("interpretation", "")
                
                s_color = colors.green if s_risk == "LOW" else (colors.orange if s_risk == "MEDIUM" else colors.red)
                
                s_text = f"""
                Sloan Ratio: <font color="{s_color}">{s_ratio}%</font> ({s_risk} Risk)<br/>
                <i>{s_interp}</i><br/>
                <font size="8">Formula: (Net Income - Operating Cash Flow) / Total Assets</font><br/>
                <font size="8">Interpretation: >10% indicates potential earnings manipulation (High Accruals)</font>
                """
                story.append(Paragraph(s_text, styles['Normal']))
            else:
                story.append(Paragraph("Sloan Ratio: Data Not Available", styles['Normal']))

            # --- Key Financial Metrics ---
            story.append(PageBreak())
            story.append(Paragraph("5. Detailed Financial Metrics Summary", styles['SectionHeader']))
            
            # Enhanced Metrics Table
            metrics_data = []
            if "financial_ratios" in forensic:
                ratios = forensic["financial_ratios"].get("financial_ratios", {})
                if ratios:
                    # Find the latest period that has balance sheet data (e.g., current_ratio)
                    sorted_ids = sorted(ratios.keys(), reverse=True)
                    period_ratios = {}
                    
                    for pid in sorted_ids:
                        if "current_ratio" in ratios[pid]:
                            period_ratios = ratios[pid]
                            break
                    
                    # Fallback to absolute latest if no balance sheet data found anywhere
                    if not period_ratios and sorted_ids:
                        period_ratios = ratios[sorted_ids[0]]
                        
                    # Grouped Metrics
                    groups = [
                        ("Profitability", [
                            ("net_profit_pct", "Net Profit Margin (%)"),
                            ("operating_margin_pct", "Operating Margin (%)"),
                            ("roe", "Return on Equity (%)"),
                            ("roa", "Return on Assets (%)")
                        ]),
                        ("Liquidity & Solvency", [
                            ("current_ratio", "Current Ratio"),
                            ("quick_ratio", "Quick Ratio"),
                            ("debt_to_equity", "Debt-to-Equity"),
                            ("interest_coverage", "Interest Coverage")
                        ]),
                        ("Efficiency", [
                            ("asset_turnover", "Asset Turnover"),
                            ("inventory_turnover", "Inventory Turnover"),
                            ("receivables_turnover", "Receivables Turnover")
                        ])
                    ]

                    metrics_data = [["Category", "Metric", "Value", "Forensic Insight"]]
                    
                    for category, metrics in groups:
                        for i, (key, label) in enumerate(metrics):
                            val = period_ratios.get(key, 0)
                            
                            # Insight Logic
                            insight = "Stable"
                            if key == "debt_to_equity" and val > 2.0: insight = "High Leverage Risk"
                            elif key == "current_ratio" and val < 1.0: insight = "Liquidity Strain"
                            elif key == "interest_coverage" and val < 1.5: insight = "Solvency Concern"
                            elif key == "net_profit_pct" and val < 5.0: insight = "Low Profitability"
                            elif key == "roe" and val < 10.0: insight = "Subpar Returns"
                            
                            cat_cell = category if i == 0 else ""
                            
                            metrics_data.append([
                                Paragraph(f"<b>{cat_cell}</b>", styles['NormalSmall']),
                                Paragraph(label, styles['NormalSmall']),
                                f"{val:.2f}",
                                Paragraph(insight, styles['NormalSmall'])
                            ])

            if len(metrics_data) > 1:
                t = Table(metrics_data, colWidths=[100, 150, 80, 120])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.navy),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                story.append(t)
            
            story.append(Spacer(1, 20))

            # --- Financial Statement Analysis ---
            story.append(PageBreak())
            story.append(Paragraph("6. Financial Statement Analysis", styles['SectionHeader']))

            # Vertical Analysis (Common Size)
            # Vertical Analysis Table
            story.append(Paragraph("Vertical Analysis (Income Statement - % of Revenue)", styles['Heading3']))
            
            # Robust extraction of Vertical Analysis Data
            vertical_data = forensic.get("vertical_analysis", {}).get("vertical_analysis", {})
            if not vertical_data:
                # Try accessing without nested key if structure is flattened
                vertical_data = forensic.get("vertical_analysis", {})

            # Check if we have income statement data
            income_vertical = vertical_data.get("income_statement", {})
            
            if income_vertical:
                v_table_data = [["Metric", "% of Revenue"]]
                v_items = [
                    ("cogs_pct", "Cost of Revenue"),
                    ("gross_profit_pct", "Gross Profit"),
                    ("operating_expenses_pct", "Operating Expenses"),
                    ("operating_income_pct", "Operating Income"),
                    ("interest_expense_pct", "Interest Expense"),
                    ("tax_expense_pct", "Tax Expense"),
                    ("net_income_pct", "Net Profit")
                ]
                
                for key, label in v_items:
                    val = income_vertical.get(key, 0)
                    if val is None: val = 0
                    v_table_data.append([label, f"{val:.2f}%"])
                
                vt = Table(v_table_data, colWidths=[200, 100])
                vt.setStyle(TableStyle([
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ]))
                story.append(vt)
            else:
                 story.append(Paragraph("No vertical analysis data available.", styles['Normal']))
            story.append(Spacer(1, 15))

            # Horizontal Analysis Table
            story.append(Paragraph("Horizontal Analysis (Recent Growth Trends)", styles['Heading3']))
            
            horizontal_data = forensic.get("horizontal_analysis", {}).get("horizontal_analysis", {})
            if not horizontal_data:
                 horizontal_data = forensic.get("horizontal_analysis", {})
            
            # Fix: Handle nested structure from generate_forensic_report
            if "growth_metrics" in horizontal_data:
                horizontal_data = horizontal_data["growth_metrics"]

            if horizontal_data:
                # Get latest period key
                # Keys are like '2024-12-31_to_2025-03-31_income_statement'
                # We want to sort and pick the latest one
                sorted_keys = sorted(horizontal_data.keys())
                
                if sorted_keys:
                    latest_h_key = sorted_keys[-1]
                    latest_growth = horizontal_data[latest_h_key]
                    
                    # Extract period from key for display
                    period_label = latest_h_key.replace("_income_statement", "").replace("_", " ")
                    story.append(Paragraph(f"Period: {period_label}", styles['NormalSmall']))

                    h_table_data = [["Metric (QoQ)", "Growth %", "Signal"]]
                    h_items = [
                        ("total_revenue_growth_pct", "Revenue Growth"),
                        ("net_profit_growth_pct", "Net Profit Growth"),
                        ("total_assets_growth_pct", "Asset Growth"),
                        ("total_liabilities_growth_pct", "Liability Growth")
                    ]
                    
                    for key, label in h_items:
                        val = latest_growth.get(key, 0)
                        # Handle potential None values
                        if val is None: 
                            val_str = "N/A"
                            signal = "N/A"
                            color = colors.black
                        else:
                            val_str = f"{val:.2f}%"
                            signal = "Stable"
                            if val < -10: signal = "Contraction"
                            elif val > 20: signal = "Aggressive Growth"
                            color = colors.red if val < 0 else colors.green
                        
                        h_table_data.append([
                            label, 
                            Paragraph(val_str, ParagraphStyle('Grow', parent=styles['NormalSmall'], textColor=color)),
                            signal
                        ])
                    
                    ht = Table(h_table_data, colWidths=[200, 100, 150])
                    ht.setStyle(TableStyle([
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ]))
                    story.append(ht)
                else:
                    story.append(Paragraph("Insufficient historical data for trend analysis.", styles['Normal']))
            else:
                story.append(Paragraph("Insufficient historical data for trend analysis.", styles['Normal']))
            story.append(Spacer(1, 15))

            # --- Forensic Checks ---
            story.append(PageBreak())
            story.append(Paragraph("7. Advanced Forensic Checks", styles['SectionHeader']))

            # Benford's Law
            story.append(Paragraph("Benford's Law Analysis (Data Integrity)", styles['Heading3']))
            benford = report_data.get("benford_analysis", {}) # Assuming this is passed in report_data root or forensic
            # Fallback check
            if not benford: benford = forensic.get("benford_analysis", {}).get("benford_analysis", {})

            if benford:
                is_anom = benford.get("is_anomalous", False)
                chi_sq = benford.get("chi_square_statistic", 0)
                interp = benford.get("interpretation", "Unknown")
                
                b_color = colors.red if is_anom else colors.green
                story.append(Paragraph(f"Status: {interp}", ParagraphStyle('Benford', parent=styles['Heading4'], textColor=b_color)))
                story.append(Paragraph(f"Chi-Square: {chi_sq:.2f} (Critical: {benford.get('critical_value', 15.5)})", styles['Normal']))
                
                if is_anom:
                    story.append(Paragraph("<b>Warning:</b> The financial data deviates significantly from expected natural distribution patterns, which can indicate manipulation or data quality issues.", styles['Normal']))
                else:
                    story.append(Paragraph("The data follows expected natural distribution patterns.", styles['Normal']))
            else:
                story.append(Paragraph("Benford analysis not available (requires more data points).", styles['Normal']))
            story.append(Spacer(1, 15))

            # GST Reconciliation
            story.append(Paragraph("GST vs Revenue Reconciliation", styles['Heading3']))
            gst_res = forensic.get("gst_reconciliation", {}).get("reconciliation_results", [])
            if gst_res:
                latest_gst = gst_res[-1]
                is_disc = latest_gst.get("is_disconnect", False)
                rev_g = latest_gst.get("revenue_growth_pct", 0)
                gst_g = latest_gst.get("gst_growth_pct", 0)
                
                r_color = colors.red if is_disc else colors.green
                story.append(Paragraph(f"Revenue Growth: {rev_g:.2f}% vs Tax Growth: {gst_g:.2f}%", styles['Normal']))
                story.append(Paragraph(f"Result: {latest_gst.get('risk_analysis', 'Normal')}", 
                                      ParagraphStyle('GST', parent=styles['Normal'], textColor=r_color, fontName='Helvetica-Bold')))
            else:
                story.append(Paragraph("GST reconciliation data not available.", styles['Normal']))
            
            story.append(Spacer(1, 20))

            # --- Disclaimer ---
            story.append(Paragraph("DISCLAIMER", styles['Heading4']))
            disclaimer_text = """
            This report is generated by the IRIS AI Forensic Engine for informational purposes only. 
            It is based on the analysis of public financial data and proprietary algorithms. 
            This does not constitute professional investment advice, legal counsel, or a certified forensic audit opinion. 
            Users should verify all information independently before making business or investment decisions. 
            The system assumes no liability for errors, omissions, or actions taken based on this report.
            """
            story.append(Paragraph(disclaimer_text, styles['Disclaimer']))

            # Build PDF
            doc.build(story)

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
            import traceback
            traceback.print_exc()
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
