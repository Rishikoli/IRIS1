
import asyncio
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set mock environment variables BEFORE importing anything that uses Settings
os.environ["FMP_API_KEY"] = "mock_key"
os.environ["GEMINI_API_KEY"] = "mock_key"
os.environ["SUPABASE_URL"] = "https://mock.supabase.co"
os.environ["SUPABASE_KEY"] = "mock_key"
os.environ["SUPABASE_DB_PASSWORD"] = "mock_pass"

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mocking modules to avoid connection attempts
from unittest.mock import MagicMock
sys.modules['src.database.connection'] = MagicMock()
# We don't verify src.config here because we set env vars, but we can mock it too if needed.


# Now import the agent
from src.agents.forensic.agent2_forensic_analysis import ForensicAnalysisAgent

async def debug_z_score():
    print("--- Debugging IDEA.NS Z-Score ---")
    
    # We need to fetch real data or mock it precisely as the app does.
    # Since we can't easily fetch real data without the full stack or API keys (if needed),
    # we will rely on what the user's system likely has.
    # However, to be effective, I'll try to use yfinance directly if available, 
    # as that's likely what the backend uses (or similar).
    
    try:
        import yfinance as yf
        ticker = yf.Ticker("IDEA.NS")
        bs = ticker.balance_sheet
        financials = ticker.financials
        
        print(f"Data fetched for IDEA.NS")
        
        # Convert to dictionary format expected by Agent 2
        # yfinance returns DataFrame, Agent expects Dict
        
        # We'll just define the agent and manually feed it data we extract/mock
        # to test the FORMULA logic first given the inputs.
        
        agent = ForensicAnalysisAgent()
        
        # Let's inspect what yfinance returns for IDEA.NS latest period
        if not bs.empty:
            latest_date = bs.columns[0]
            print(f"Latest Period: {latest_date}")
            
            # Map yfinance keys to what Agent 2 expects
            # Agent 2 keys: totalAssets, totalCurrentAssets, totalCurrentLiabilities,
            # retainedEarnings, totalStockholdersEquity, totalLiabilities
            
            def get_val(df, key):
                try:
                    return float(df.loc[key, latest_date])
                except KeyError:
                    return 0.0

            # Direct extracting from yfinance dataframe (checking common keys)
            # YFinance keys often differ: 'Total Assets', 'Current Assets', etc.
            
            bs_dict = {
                "totalAssets": get_val(bs, "Total Assets"),
                "totalCurrentAssets": get_val(bs, "Current Assets"),
                "totalCurrentLiabilities": get_val(bs, "Current Liabilities"),
                "retainedEarnings": get_val(bs, "Retained Earnings"),
                "totalStockholdersEquity": get_val(bs, "Stockholders Equity") or get_val(bs, "Total Stockholder Equity"),
                "totalLiabilities": get_val(bs, "Total Liabilities Net Minority Interest"),
                # "totalLiabilities": 0 # SIMULATE MISSING DATA REMOVED
            }
            
            is_dict = {
                "totalRevenue": get_val(financials, "Total Revenue"),
                "operatingIncome": get_val(financials, "Operating Income") or get_val(financials, "EBIT")
            }
            
            print("\nExtracted Inputs:")
            for k, v in bs_dict.items():
                print(f"  {k}: {v:,.2f}")
            for k, v in is_dict.items():
                print(f"  {k}: {v:,.2f}")
                
            # Run Calculation
            result = agent.calculate_altman_z_score(bs_dict, is_dict)
            
            print("\nCalculation Result (Agent Fixed):")
            import json
            print(json.dumps(result, indent=2))
            
            # Manual Check of D-Score (Equity / Debt)
            equity = bs_dict["totalStockholdersEquity"]
            debt = bs_dict["totalLiabilities"]
            print(f"\nManual D-Score Check: {equity:,.2f} / {debt:,.2f} = {equity/debt if debt else 'inf'}")
            
        else:
            print("Failed to fetch Balance Sheet data via yfinance")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_z_score())
