
import sys
import os
import asyncio
import json

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Mock Env Vars to bypass Pydantic validation
os.environ["FMP_API_KEY"] = "mock"
os.environ["GEMINI_API_KEY"] = "mock"
os.environ["SUPABASE_URL"] = "https://mock.supabase.co"
os.environ["SUPABASE_KEY"] = "mock"
os.environ["SUPABASE_DB_PASSWORD"] = "mock"

from src.agents.forensic.agent2_forensic_analysis import ForensicAnalysisAgent

async def main():
    agent = ForensicAnalysisAgent()
    print("Fetching data for OLAELEC.NS...")
    print("Starting analysis...", flush=True)
    try:
        data = agent.analyze_yahoo_finance_data("OLAELEC.NS")
        print("Analysis returned data", flush=True)
    except Exception as e:
        print(f"Analysis Failed: {e}", flush=True)
        return
    
    print("\nKeys in result:")
    print(data.keys())
    
    print("\nForeground Analysis Keys:", data.keys())
    
    va = data.get("vertical_analysis", {})
    print(f"\nVertical Analysis Raw Type: {type(va)}")
    print(f"Vertical Analysis Keys: {va.keys() if isinstance(va, dict) else 'Not a dict'}")
    if isinstance(va, dict) and "vertical_analysis" in va:
         print(f"Inner Vertical Analysis Keys: {va['vertical_analysis'].keys()}")
         # Print one entry to check content
         if va['vertical_analysis']:
             first_key = list(va['vertical_analysis'].keys())[0]
             print(f"Sample content for {first_key}: {va['vertical_analysis'][first_key].keys()}")

    ha = data.get("horizontal_analysis", {})
    print(f"\nHorizontal Analysis Raw Type: {type(ha)}")
    print(f"Horizontal Analysis Keys: {ha.keys() if isinstance(ha, dict) else 'Not a dict'}")
    if isinstance(ha, dict) and "horizontal_analysis" in ha:
         print(f"Inner Horizontal Analysis Keys: {ha['horizontal_analysis'].keys()}")
         if ha['horizontal_analysis']:
             first_key = list(ha['horizontal_analysis'].keys())[0]
             print(f"Sample content for {first_key}: {ha['horizontal_analysis'][first_key].keys()}")

    # --- Debug Z-Score Inputs ---
    print("\n--- DEBUG Z-SCORE INPUTS ---")
    # Get latest statements
    income_stmts = [s for s in data.get('financial_statements', []) if s['statement_type'] == 'income_statement']
    balance_sheets = [s for s in data.get('financial_statements', []) if s['statement_type'] == 'balance_sheet']
    
    # Sort by date
    income_stmts.sort(key=lambda x: x['period_end'], reverse=True)
    balance_sheets.sort(key=lambda x: x['period_end'], reverse=True)
    
    latest_is = income_stmts[0]['data'] if income_stmts else {}
    latest_bs = balance_sheets[0]['data'] if balance_sheets else {}
    
    print(f"Latest Income Statement Date: {income_stmts[0]['period_end'] if income_stmts else 'None'}")
    print(f"Latest Balance Sheet Date: {balance_sheets[0]['period_end'] if balance_sheets else 'None'}")
    
    z_keys = [
        "totalAssets", "Total Assets", "total_assets",
        "retainedEarnings", "Retained Earnings", "retained_earnings",
        "totalCurrentAssets", "Total Current Assets", "current_assets",
        "totalCurrentLiabilities", "Total Current Liabilities", "current_liabilities",
        "operatingIncome", "Operating Income", "operating_income",
        "totalRevenue", "Total Revenue", "total_revenue",
        "totalStockholdersEquity", "Total Stockholders Equity", "total_equity"
    ]
    
    print("Checking Z-Score keys in Balance Sheet:")
    for k in z_keys:
        if k in latest_bs:
            print(f"  BS[{k}]: {latest_bs[k]}")
            
    print("Checking Z-Score keys in Income Statement:")
    for k in z_keys:
        if k in latest_is:
            print(f"  IS[{k}]: {latest_is[k]}")

    # --- Debug Sloan Ratio Inputs ---
    print("\n--- DEBUG SLOAN RATIO INPUTS ---")
    cash_flows = [s for s in data.get('financial_statements', []) if s['statement_type'] == 'cash_flow_statement']
    cash_flows.sort(key=lambda x: x['period_end'], reverse=True)
    latest_cf = cash_flows[0]['data'] if cash_flows else {}
    
    print(f"Latest Cash Flow Date: {cash_flows[0]['period_end'] if cash_flows else 'None'}")
    
    sloan_keys = [
        "net_income", "Net Income", "NetIncome",
        "operating_cash_flow", "Operating Cash Flow",
        "total_assets", "Total Assets"
    ]
    
    print("Checking Sloan keys in Income Statement:")
    for k in sloan_keys:
        if k in latest_is:
            print(f"  IS[{k}]: {latest_is[k]}")
            
    print("Checking Sloan keys in Cash Flow Statement:")
    for k in sloan_keys:
        if k in latest_cf:
            print(f"  CF[{k}]: {latest_cf[k]}")
            
    # Check if Sloan Ratio result exists
    print("\nSloan Result in Data:", data.get('sloan_ratio'))

    if "financial_ratios" in data:
        print("\nFinancial Ratios:")
        ratios_wrapper = data["financial_ratios"]
        print(json.dumps(ratios_wrapper, indent=2))
        
        inner_ratios = ratios_wrapper.get("financial_ratios", {})
        print(f"\nNumber of periods with ratios: {len(inner_ratios)}")
    
    if "error" in data:
        print(f"\nError: {data['error']}")
        
    # Check what statements were found
    # accessing protected member just for debugging if needed, but the agent prints to stdout too

if __name__ == "__main__":
    asyncio.run(main())
