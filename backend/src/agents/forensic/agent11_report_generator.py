
import logging
import io
from typing import Dict, Any, List, Optional
from datetime import datetime

# Try importing reportlab, handle if missing
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

logger = logging.getLogger(__name__)

class ReportGeneratorAgent:
    """
    Agent 11: Responsible for generating comprehensive forensic investigation reports in PDF format.
    Aggregates data from Risk Scoring, Compliance, and Forensic Analysis agents.
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet() if REPORTLAB_AVAILABLE else None
        if REPORTLAB_AVAILABLE:
            self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Define custom paragraph styles for the report"""
        self.styles.add(ParagraphStyle(
            name='Header1',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=12,
            textColor=colors.HexColor('#1a237e') # Dark Blue
        ))
        self.styles.add(ParagraphStyle(
            name='Header2',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceBefore=12,
            spaceAfter=6,
            textColor=colors.HexColor('#283593')
        ))
        self.styles.add(ParagraphStyle(
            name='RiskHigh',
            parent=self.styles['Normal'],
            textColor=colors.red
        ))
        self.styles.add(ParagraphStyle(
            name='RiskMedium',
            parent=self.styles['Normal'],
            textColor=colors.orange
        ))
        self.styles.add(ParagraphStyle(
            name='RiskLow',
            parent=self.styles['Normal'],
            textColor=colors.green
        ))

    def generate_report(self, company_symbol: str, assessment_data: Dict[str, Any]) -> Optional[bytes]:
        """
        Generate a PDF report for the given company assessment data.
        Returns PDF bytes or None if generation fails.
        """
        if not REPORTLAB_AVAILABLE:
            logger.error("ReportLab library not installed. Cannot generate PDF.")
            return None

        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
            story = []

            # 1. Header
            self._create_header(story, company_symbol)
            
            # 2. Executive Summary (Risk Score)
            self._create_executive_summary(story, assessment_data)
            
            # 3. Risk Breakdown
            self._create_risk_breakdown(story, assessment_data)
            
            # 4. Compliance Section
            self._create_compliance_section(story, assessment_data)
            
            # 5. Financial Highlights
            self._create_financial_section(story, assessment_data)
            
            # 6. Market Sentiment
            self._create_sentiment_section(story, assessment_data)

            # Build PDF
            doc.build(story)
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            logger.info(f"Generated PDF report for {company_symbol} ({len(pdf_bytes)} bytes)")
            return pdf_bytes

        except Exception as e:
            logger.error(f"Failed to generate report for {company_symbol}: {e}", exc_info=True)
            return None

    def _create_header(self, story: List, company_symbol: str):
        title = Paragraph(f"Forensic Investigation Report: {company_symbol}", self.styles['Title'])
        date = Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", self.styles['Normal'])
        story.append(title)
        story.append(date)
        story.append(Spacer(1, 0.5 * inch))

    def _create_executive_summary(self, story: List, data: Dict):
        story.append(Paragraph("Executive Summary", self.styles['Header1']))
        
        # Risk Score Display
        risk_score = data.get("overall_risk_score", 0)
        risk_level = data.get("risk_level", "UNKNOWN")
        
        score_text = f"Overall Risk Score: {risk_score:.1f} / 100 ({risk_level})"
        
        # Color coding
        style = self.styles['Normal']
        if risk_level in ["CRITICAL", "HIGH"]:
            style = self.styles['RiskHigh']
        elif risk_level == "MEDIUM":
            style = self.styles['RiskMedium']
        else:
            style = self.styles['RiskLow']
            
        story.append(Paragraph(score_text, style))
        
        # Recommendation
        rec = data.get("investment_recommendation", "No recommendation available")
        story.append(Paragraph(f"<b>Recommendation:</b> {rec}", self.styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))

    def _create_risk_breakdown(self, story: List, data: Dict):
        story.append(Paragraph("Risk Breakdown", self.styles['Header2']))
        
        breakdown = data.get("category_breakdown", {})
        if not breakdown:
            story.append(Paragraph("No breakdown data available.", self.styles['Normal']))
            return

        table_data = [['Category', 'Score', 'Details']]
        
        for category, details in breakdown.items():
            cat_name = category.replace('_', ' ').title()
            score = f"{details.get('score', 0):.1f}"
            
            # Get top factor
            factors = details.get('factors', [])
            factor_text = factors[0] if factors else "No specific factors identified"
            if len(factors) > 1:
                factor_text += f" (+{len(factors)-1} more)"
                
            table_data.append([cat_name, score, Paragraph(factor_text, self.styles['Normal'])])

        t = Table(table_data, colWidths=[2*inch, 1*inch, 3.5*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.2 * inch))

    def _create_compliance_section(self, story: List, data: Dict):
        story.append(Paragraph("Compliance & Regulatory", self.styles['Header2']))
        
        # Try to find specific compliance data in breakdown or separate key
        # Assuming integration put it in 'category_breakdown' -> 'compliance_risk'
        comp_data = data.get("category_breakdown", {}).get("compliance_risk", {})
        
        if comp_data:
            score = comp_data.get('score', 0)
            # Reverse engineer the compliance score if needed, or just report risk
            compliance_score = 100 - score # Since Risk = 100 - Compliance
            story.append(Paragraph(f"Estimated Compliance Score: {compliance_score:.1f}/100", self.styles['Normal']))
            
            factors = comp_data.get('factors', [])
            if factors:
                story.append(Paragraph("<b>Violations / Issues:</b>", self.styles['Normal']))
                for f in factors:
                    bullet = f"• {f}"
                    story.append(Paragraph(bullet, self.styles['Normal']))
            else:
                story.append(Paragraph("No major compliance violations detected.", self.styles['Normal']))
        else:
            story.append(Paragraph("Compliance data not found.", self.styles['Normal']))
            
        story.append(Spacer(1, 0.2 * inch))

    def _create_financial_section(self, story: List, data: Dict):
        # This part depends on if we pass raw financial data or just the risk assessment
        # The prompt implies we aggregate data. 
        # For this v1, we might only have what's in the risk assessment unless we change call signature.
        # Let's check if 'financial_stability' in breakdown has info.
        story.append(Paragraph("Financial Stability Factors", self.styles['Header2']))
        
        fin_data = data.get("category_breakdown", {}).get("financial_stability", {})
        factors = fin_data.get("factors", [])
        
        if factors:
            for f in factors:
                story.append(Paragraph(f"• {f}", self.styles['Normal']))
        else:
             story.append(Paragraph("No specific financial flags identified.", self.styles['Normal']))

        story.append(Spacer(1, 0.2 * inch))

    def _create_sentiment_section(self, story: List, data: Dict):
        story.append(Paragraph("Market Sentiment Analysis", self.styles['Header2']))
        
        market_data = data.get("category_breakdown", {}).get("market_risk", {})
        factors = market_data.get("factors", [])
        
        sentiment_factors = [f for f in factors if "sentiment" in f.lower() or "news" in f.lower()]
        
        if sentiment_factors:
            story.append(Paragraph("<b>Negative Sentiment Detected:</b>", self.styles['RiskMedium']))
            for f in sentiment_factors:
                story.append(Paragraph(f"• {f}", self.styles['Normal']))
        else:
            story.append(Paragraph("No significant negative market sentiment detected in recent news.", self.styles['Normal']))
