
import sys
import os
import asyncio
import logging
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')
logging.getLogger('yfinance').setLevel(logging.CRITICAL)

# Mock Environment Variables BEFORE importing src.config
os.environ["FMP_API_KEY"] = "dummy"
os.environ["GEMINI_API_KEY"] = "dummy"
os.environ["SUPABASE_URL"] = "https://dummy.supabase.co"
os.environ["SUPABASE_KEY"] = "dummy"
os.environ["SUPABASE_DB_PASSWORD"] = "dummy"  # Added this
os.environ["SECRET_KEY"] = "dummy"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"

# Add backend to path
sys.path.append(os.path.abspath('backend'))

try:
    from src.agents.forensic.agent2_forensic_analysis import ForensicAnalysisAgent
    from src.agents.forensic.agent4_compliance import ComplianceValidationAgent
except Exception as e:
    print(f"Import Error: {e}")
    sys.exit(1)

async def check_companies():
    companies = [
        "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS",
        "BHARTIARTL.NS", "ITC.NS", "SBIN.NS", "LICI.NS", "HINDUNILVR.NS",
        "INDUSINDBK.NS", "OLAELEC.NS", "IDEA.NS", "TATAMOTORS.NS", "ADANIENT.NS",
        "WIPRO.NS", "HCLTECH.NS", "MARUTI.NS", "SUNPHARMA.NS", "TITAN.NS"]
    
    print(f"Checking {len(companies)} companies for Compliance Score 75...")
    
    forensic_agent = ForensicAnalysisAgent()
    compliance_agent = ComplianceValidationAgent()
    
    found_match = False
    
    for symbol in companies:
        try:
            # print(f"Analyzing {symbol}...")
            # Fetch data (blocking call acting as sync in this context or is it async? analyze_yahoo_finance_data is sync)
            data = forensic_agent.analyze_yahoo_finance_data(symbol, quarters=1)
            
            if not data.get("success"):
                # print(f"Failed to fetch data for {symbol}: {data.get('error')}")
                continue
            
            # Run compliance
            assessment = compliance_agent.validate_compliance(symbol, data)
            score = assessment.overall_compliance_score
            
            print(f"Company: {symbol}, Score: {score}")
            
            if score == 75.0:
                print(f"\n*** MATCH FOUND: {symbol} HAS SCORE 75 ***\n")
                found_match = True
                
        except Exception as e:
            # print(f"Error checking {symbol}: {e}")
            pass
            
    if not found_match:
        print("\nNo company with exact score 75 found in this batch.")

if __name__ == "__main__":
    asyncio.run(check_companies())
