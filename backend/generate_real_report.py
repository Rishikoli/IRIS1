
import asyncio
import logging
import sys
import os
from datetime import datetime

# Add src to python path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
sys.path.append(os.path.dirname(__file__))

from src.agents.forensic.agent2_forensic_analysis import ForensicAnalysisAgent
from src.agents.forensic.agent3_risk_scoring import RiskScoringAgent
from src.agents.forensic.agent4_compliance import ComplianceValidationAgent
from src.agents.forensic.agent5_reporting import ReportingAgent, ExportFormat
import yfinance as yf

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fetch_yahoo_data(company_symbol):
    print(f"Fetching data for {company_symbol}...")
    try:
        ticker = yf.Ticker(company_symbol)
        income_stmt = ticker.financials
        balance_sheet = ticker.balance_sheet
        cash_flow = ticker.cashflow
        
        financial_statements = []
        
        # Process income statements
        if income_stmt is not None:
            for i in range(min(3, len(income_stmt.columns))):
                stmt_data = income_stmt.iloc[:, i].to_dict()
                # Convert timestamps to string keys for JSON serialization
                stmt_data = {str(k): v for k, v in stmt_data.items()}
                financial_statements.append({
                    'statement_type': 'income_statement',
                    'period_end': str(income_stmt.columns[i].date()),
                    'data': stmt_data
                })
        
        # Process balance sheets
        if balance_sheet is not None:
             for i in range(min(3, len(balance_sheet.columns))):
                stmt_data = balance_sheet.iloc[:, i].to_dict()
                stmt_data = {str(k): v for k, v in stmt_data.items()}
                financial_statements.append({
                    'statement_type': 'balance_sheet',
                    'period_end': str(balance_sheet.columns[i].date()),
                    'data': stmt_data
                })
                
        return financial_statements
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

async def main():
    company_symbol = "RCOM.NS"
    
    # Initialize agents
    forensic_agent = ForensicAnalysisAgent()
    risk_agent = RiskScoringAgent()
    compliance_agent = ComplianceValidationAgent()
    reporting_agent = ReportingAgent()
    
    # 1. Fetch Data
    financial_statements = await fetch_yahoo_data(company_symbol)
    if not financial_statements:
        print("Failed to fetch financial statements")
        return

    print(f"Fetched {len(financial_statements)} statements")

    # 2. Run Forensic Analysis
    print("Running Forensic Analysis...")
    forensic_result = forensic_agent.comprehensive_forensic_analysis(company_symbol, financial_statements)
    
    if not forensic_result['success']:
        print(f"Forensic Analysis Failed: {forensic_result.get('error')}")
        return
    
    print(f"DEBUG: Forensic Result Keys: {forensic_result.keys()}")
    if "sloan_ratio" in forensic_result:
        print(f"DEBUG: Sloan Ratio in Forensic Result: {forensic_result['sloan_ratio']}")
    else:
        print("DEBUG: Sloan Ratio MISSING from Forensic Result")

    if "altman_z_score" in forensic_result:
        print(f"DEBUG: Altman Z-Score Result: {forensic_result['altman_z_score']}")
    else:
        print("DEBUG: Altman Z-Score MISSING from Forensic Result")

    # 3. Assessment
    print("Running Risk & Compliance Assessment...")
    risk_assessment = risk_agent.calculate_risk_score(company_symbol, forensic_result)
    compliance_assessment = compliance_agent.validate_compliance(company_symbol, forensic_result)

    # Helper to serialize compliance violations
    def serialize_violation(v):
        return {
            "framework": v.framework.value if hasattr(v.framework, "value") else str(v.framework),
            "rule_id": v.rule_id,
            "rule_description": v.rule_description,
            "severity": v.severity.value if hasattr(v.severity, "value") else str(v.severity),
            "violation_description": v.violation_description,
            "evidence": v.evidence,
            "remediation_steps": v.remediation_steps,
            "regulatory_reference": v.regulatory_reference,
            "financial_impact": v.financial_impact
        }

    # 4. Prepare Data
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
            'violations': [serialize_violation(v) for v in compliance_assessment.violations],
        }
    }

    # 5. Generate Report
    print("Generating Comprehensive Report...")
    result = await reporting_agent.generate_comprehensive_report(
        company_symbol, 
        analysis_data,
        export_formats=[ExportFormat.PDF]
    )
    
    if result['success']:
        print("\nReport Generation SUCCESS!")
        print(f"Report ID: {result['comprehensive_report']['report_id']}")
        for key, val in result['comprehensive_report']['exports'].items():
            print(f"Exported: {val['export_info']['filepath']}")
    else:
        print(f"Report Generation Failed: {result.get('error')}")

if __name__ == "__main__":
    asyncio.run(main())
