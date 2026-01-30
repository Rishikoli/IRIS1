
import sys
import os
import asyncio
import logging
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')
logging.getLogger('yfinance').setLevel(logging.CRITICAL)

# Mock Environment Variables
os.environ["FMP_API_KEY"] = "dummy"
os.environ["GEMINI_API_KEY"] = "dummy"
os.environ["SUPABASE_URL"] = "https://dummy.supabase.co"
os.environ["SUPABASE_KEY"] = "dummy"
os.environ["SUPABASE_DB_PASSWORD"] = "dummy"
os.environ["SECRET_KEY"] = "dummy"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"

# Add backend to path
sys.path.append(os.path.abspath('backend'))

try:
    from src.agents.forensic.agent3_risk_scoring import RiskScoringAgent
    from src.agents.forensic.agent2_forensic_analysis import ForensicAnalysisAgent
except Exception as e:
    print(f"Import Error: {e}")
    sys.exit(1)

async def check_risk_details():
    companies = [
       "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS",
       "BHARTIARTL.NS", "ITC.NS", "SBIN.NS", "LICI.NS", "HINDUNILVR.NS",
       "INDUSINDBK.NS", "OLAELEC.NS", "IDEA.NS", "TATAMOTORS.NS", "ADANIENT.NS",
       "WIPRO.NS", "HCLTECH.NS", "MARUTI.NS", "SUNPHARMA.NS", "TITAN.NS"
    ]
    
    print(f"Checking {len(companies)} companies for ANY Risk Category Score 75...")
    
    forensic_agent = ForensicAnalysisAgent()
    risk_agent = RiskScoringAgent()
    
    found_match = False
    
    for symbol in companies:
        try:
            data = forensic_agent.analyze_yahoo_finance_data(symbol, quarters=1)
            if not data.get("success"):
                continue
            
            assessment = risk_agent.calculate_risk_score(symbol, data)
            
            # Check overall
            if assessment.overall_risk_score == 75.0:
                 print(f"*** MATCH OVERALL: {symbol} Score 75 ***")
                 found_match = True

            # Check categories
            for cat, score_obj in assessment.risk_category_scores.items():
                if score_obj.score == 75.0:
                    print(f"*** MATCH CATEGORY: {symbol} - {cat.value} Score 75 ***")
                    found_match = True
                    
        except Exception as e:
            pass
            
    if not found_match:
        print("\nNo company with exact Risk Score 75 (Overall or Category) found.")

if __name__ == "__main__":
    asyncio.run(check_risk_details())
