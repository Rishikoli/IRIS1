
import sys
import os
import asyncio
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add backend to path
sys.path.append('/home/aditya/Downloads/IRIS/backend')

from src.agents.forensic.agent2_forensic_analysis import ForensicAnalysisAgent
from src.agents.forensic.agent4_compliance import ComplianceValidationAgent

def _create_enhanced_mock_data(company_symbol: str) -> list:
    """Create enhanced mock financial data (Copied from forensic.py to avoid imports)"""
    financial_statements = []
    
    # Company-specific base values
    company_configs = {
        'RELIANCE': {
            'revenue_base': 8000000000,
            'asset_base': 15000000000,
            'revenue_growth': 0.12,
            'margin': 0.25
        }
    }
    
    config = company_configs.get(company_symbol, company_configs['RELIANCE'])
    base_year = 2024
    
    for year_offset in range(3):
        year = base_year - year_offset
        revenue_growth = 1.0 + (config['revenue_growth'] * year_offset)
        asset_growth = 1.0 + (config['revenue_growth'] * 0.8 * year_offset)
        
        # Income Statement
        base_revenue = config['revenue_base']
        stmt_data = {
            'Total Revenue': int(base_revenue * revenue_growth),
            'Cost of Revenue': int((base_revenue * revenue_growth) * (1 - config['margin'] * 1.2)),
            'Gross Profit': int((base_revenue * revenue_growth) * config['margin'] * 1.2),
            'Operating Expenses': int((base_revenue * revenue_growth) * config['margin'] * 0.6),
            'Operating Income': int((base_revenue * revenue_growth) * config['margin']),
            'Net Income': int((base_revenue * revenue_growth) * config['margin']),
            'date': f"{year}-12-31"
        }
        
        financial_statements.append({
            'statement_type': 'income_statement',
            'period_end': f"{year}-12-31",
            'data': stmt_data
        })
        
        # Balance Sheet
        base_assets = config['asset_base']
        stmt_data = {
            'Total Assets': int(base_assets * asset_growth),
            'Total Current Assets': int((base_assets * asset_growth) * 0.35),
            'Cash and Cash Equivalents': int((base_assets * asset_growth) * 0.12),
            'Accounts Receivable': int((base_assets * asset_growth) * 0.15),
            'Inventory': int((base_assets * asset_growth) * 0.08),
            'Total Liabilities': int((base_assets * asset_growth) * 0.65),
            'Total Current Liabilities': int((base_assets * asset_growth) * 0.25),
            'Long Term Debt': int((base_assets * asset_growth) * 0.40),
            'Total Equity': int((base_assets * asset_growth) * 0.35),
            'date': f"{year}-12-31"
        }
        
        financial_statements.append({
            'statement_type': 'balance_sheet',
            'period_end': f"{year}-12-31",
            'data': stmt_data
        })
        
    return financial_statements

async def reproduce_compliance_issue():
    company_symbol = "RELIANCE"
    
    print(f"--- Reproducing Compliance Issue for {company_symbol} ---")
    
    # 1. Create Mock Data
    print("\n1. Generating Mock Data...")
    financial_statements = _create_enhanced_mock_data(company_symbol)
    print(f"Generated {len(financial_statements)} statements")
    
    # 2. Run Forensic Analysis
    print("\n2. Running Forensic Analysis (Agent 2)...")
    forensic_agent = ForensicAnalysisAgent()
    forensic_result = forensic_agent.comprehensive_forensic_analysis(company_symbol, financial_statements)
    
    if not forensic_result['success']:
        print("Forensic Analysis Failed!")
        return
        
    print("Forensic Analysis Successful")
    print(f"Keys in result: {list(forensic_result.keys())}")
    
    # 3. Run Compliance Validation (Agent 4)
    print("\n3. Running Compliance Validation (Agent 4)...")
    compliance_agent = ComplianceValidationAgent()
    compliance_assessment = compliance_agent.validate_compliance(company_symbol, forensic_result)
    
    # 4. Inspect Results
    print("\n--- Compliance Assessment Results ---")
    print(f"Overall Score: {compliance_assessment.overall_compliance_score}")
    print(f"Status: {compliance_assessment.compliance_status}")
    print("Framework Scores:")
    for fw, score in compliance_assessment.framework_scores.items():
        print(f"  {fw.value}: {score}")
        
    if compliance_assessment.overall_compliance_score == 0:
        print("\n[FAIL] Reproduced 0% score issue!")
    else:
        print("\n[SUCCESS] Could not reproduce 0% score issue (Scores are non-zero).")

if __name__ == "__main__":
    asyncio.run(reproduce_compliance_issue())
