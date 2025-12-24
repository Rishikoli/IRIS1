
import sys
import os
import json
import logging

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

try:
    from src.agents.forensic.agent2_forensic_analysis import ForensicAnalysisAgent
except ImportError:
    # Try adding the current directory to path if running from backend/
    sys.path.append(os.getcwd())
    from src.agents.forensic.agent2_forensic_analysis import ForensicAnalysisAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_vertical_analysis():
    print("Initializing Forensic Analysis Agent...")
    agent = ForensicAnalysisAgent()
    
    # Mock financial statements data (similar to what Yahoo Finance would return)
    # matching the structure expected by _vertical_income_statement and _vertical_balance_sheet
    mock_statements = [
        {
            "statement_type": "income_statement",
            "period_end": "2024-03-31",
            "data": {
                "total_revenue": 1000000,
                "cost_of_revenue": 600000,
                "gross_profit": 400000,
                "operating_income": 200000,
                "net_profit": 100000,
                "operating_expenses": 200000
            }
        },
        {
            "statement_type": "balance_sheet",
            "period_end": "2024-03-31",
            "data": {
                "total_assets": 5000000,
                "current_assets": 2000000,
                "fixed_assets": 3000000,
                "total_liabilities": 3000000,
                "current_liabilities": 1000000,
                "shareholders_equity": 2000000
            }
        }
    ]
    
    print("\nRunning Vertical Analysis...")
    result = agent.vertical_analysis(mock_statements)
    
    print("\n--- Result Structure ---")
    print(json.dumps(result, indent=2))
    
    # Check for the nesting issue
    if "vertical_analysis" in result and "income_statement" in result["vertical_analysis"]:
        print("\n[CONFIRMED] Data is nested inside 'vertical_analysis' key.")
        print("Frontend expects: result.income_statement")
        print("Backend provides: result.vertical_analysis.income_statement")
    else:
        print("\n[UNCLEAR] Structure is different than expected.")

if __name__ == "__main__":
    verify_vertical_analysis()
