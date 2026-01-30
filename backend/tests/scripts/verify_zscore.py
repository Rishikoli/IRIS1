
import sys
import os
import json
from datetime import datetime

# Mock Env Vars for Settings
os.environ["FMP_API_KEY"] = "test"
os.environ["GEMINI_API_KEY"] = "test"
from datetime import datetime, timedelta

# Set mock environment variables BEFORE importing anything that uses Settings
os.environ["FMP_API_KEY"] = "mock_key"
os.environ["GEMINI_API_KEY"] = "mock_key"
os.environ["SUPABASE_URL"] = "https://mock.supabase.co"
os.environ["SUPABASE_KEY"] = "mock_key"
os.environ["SUPABASE_DB_PASSWORD"] = "mock_pass"

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mocking settings and database
from unittest.mock import MagicMock
sys.modules['src.database.connection'] = MagicMock()

# Import the agent
from src.agents.forensic.agent2_forensic_analysis import ForensicAnalysisAgent

def verify_zscore_history():
    print("🔍 Starting Altman Z-Score Verification...")
    
    agent = ForensicAnalysisAgent()
    
    # Mock Financial Data (2 Periods)
    financial_statements = [
        # Period 1 (Old)
        {
            "statement_type": "balance_sheet",
            "period_end": "2023-01-01",
            "data": {
                "total_assets": 100000,
                "current_assets": 50000,
                "current_liabilities": 30000, # WC = 20k
                "retained_earnings": 20000,
                "total_equity": 60000,
                "total_liabilities": 40000
            }
        },
        {
            "statement_type": "income_statement",
            "period_end": "2023-01-01",
            "data": {
                "total_revenue": 100000,
                "operating_income": 15000, # EBIT
                "interest_expense": 5000,
                "tax_expense": 3000,
                "net_profit": 7000
            }
        },
        # Period 2 (New)
        {
            "statement_type": "balance_sheet",
            "period_end": "2023-04-01",
            "data": {
                "total_assets": 120000,
                "current_assets": 60000,
                "current_liabilities": 40000, # WC = 20k
                "retained_earnings": 25000,
                "total_equity": 70000,
                "total_liabilities": 50000
            }
        },
        {
            "statement_type": "income_statement",
            "period_end": "2023-04-01",
            "data": {
                "total_revenue": 110000,
                "operating_income": 18000, # EBIT
                "interest_expense": 5000,
                "tax_expense": 4000,
                "net_profit": 9000
            }
        }
    ]
    
    print(f"📊 Analyzing {len(financial_statements)//2} periods of financial data...")
    
    # Run Analysis
    results = agent.comprehensive_forensic_analysis("TEST_MOCK", financial_statements)
    
    # Verify Results
    z_score_data = results.get("altman_z_score")
    
    if not z_score_data:
        print("❌ FAIL: No Altman Z-Score data returned")
        return
        
    print(f"✅ Main Z-Score found: {z_score_data.get('z_score')}")
    # --- M-Score Verification ---
    print("\n--- Verifying Beneish M-Score ---")
    if "beneish_m_score" in results and results["beneish_m_score"].get("success"):
        m_data = results["beneish_m_score"]["beneish_m_score"]
        print(f"Current M-Score: {m_data.get('m_score')}")
        
        hist_m = m_data.get("historical_m_scores", [])
        print(f"Historical M-Scores Found: {len(hist_m)}")
        
        if len(hist_m) > 0:
            print("✅ Historical M-Score array present")
            for h in hist_m:
                 print(f"  Period: {h.get('period')} -> M-Score: {h.get('m_score')}")
        else:
            print("❌ Historical M-Score array MISSING or EMPTY")
            
        # Verify variables
        params = m_data.get("variables", {})
        print(f"M-Score Variables Present: {list(params.keys())}")
        if "DSRI" in params and "GMI" in params:
             print("✅ Key variables (DSRI, GMI) present")
        else:
             print("❌ Key variables missing")

    else:
        print("❌ Beneish M-Score section missing or failed")
    
    print("\nVerification Complete")
        
    history = z_score_data.get("historical_z_scores")
    if not history:
        print("❌ FAIL: No historical_z_scores found")
        return
        
    print(f"✅ History found: {len(history)} entries")
    
    if len(history) != 2:
        print(f"❌ FAIL: Expected 2 history entries, found {len(history)}")
        return
        
    for item in history:
        print(f"   - Period: {item.get('period')}, Z-Score: {item.get('z_score')}, Classification: {item.get('classification')}")
        
    print("✅ SUCCESS: Historical Z-Score calculation verified!")

if __name__ == "__main__":
    verify_zscore_history()
