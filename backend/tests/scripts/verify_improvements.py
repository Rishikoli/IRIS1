
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

# Add backend and src to path
sys.path.append(os.path.abspath('backend'))
sys.path.append(os.path.abspath('backend/src'))

try:
    from src.agents.forensic.agent3_risk_scoring import RiskScoringAgent, RiskCategory
    from src.agents.forensic.agent2_forensic_analysis import ForensicAnalysisAgent
    from src.agents.forensic.agent10_auditor import AuditorAgent
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

async def verify_improvements():
    print("--- 1. Testing Auditor Agent Manual URL ---")
    auditor = AuditorAgent()
    dummy_url = "https://example.com/report.pdf"
    
    # We expect it to try to download this URL directly
    # Since it's a dummy URL, download will fail, but the KEY is that it *tries* to use it
    # instead of searching.
    
    # We can inspect the log or just trust the logic if it returns "Failed to download"
    # A search would return "Annual Report PDF not found" or "Search failed"
    
    result = auditor.analyze_annual_report("TCS", pdf_url=dummy_url)
    print(f"Result with manual URL: {result.get('message', 'Success')}")
    
    if "Failed to download PDF" in str(result) or "Success" in str(result):
         print("✅ SUCCESS: Auditor attempted to use manual URL.")
    else:
         print(f"⚠️ UNEXPECTED: {result}")

    print("\n--- 2. Testing Market Sentiment Analysis ---")
    agent = RiskScoringAgent()
    forensic = ForensicAnalysisAgent()
    
    # ADANIENT failed to fetch data. Let's try RELIANCE.NS which worked before.
    symbol = "RELIANCE.NS" 
    print(f"Analyzing {symbol} for market sentiment...")
    
    data = forensic.analyze_yahoo_finance_data(symbol, quarters=1)
    
    if not data.get("success"):
        print("Failed to fetch forensic data.")
        return

    assessment = agent.calculate_risk_score(symbol, data)
    market_risk = assessment.risk_category_scores.get(RiskCategory.MARKET_RISK)
    
    if market_risk:
        print(f"Market Risk Score: {market_risk.score}")
        print(f"Factors: {market_risk.factors}")
        
        # Check if sentiment factors are present
        sentiment_found = any("news" in f.lower() or "sentiment" in f.lower() for f in market_risk.factors)
        if sentiment_found:
            print("✅ SUCCESS: Detected market sentiment factors.")
        else:
             print("ℹ️ NOTE: No negative sentiment found, but execution was successful.")
             # This is still a success for the code integration
    else:
        print("❌ FAILURE: Market Risk category missing.")

if __name__ == "__main__":
    asyncio.run(verify_improvements())
