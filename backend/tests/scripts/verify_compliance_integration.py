
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

# Add backend and src to path to handle various import styles
sys.path.append(os.path.abspath('backend'))
sys.path.append(os.path.abspath('backend/src'))

try:
    from src.agents.forensic.agent3_risk_scoring import RiskScoringAgent, RiskCategory
    from src.agents.forensic.agent2_forensic_analysis import ForensicAnalysisAgent
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

async def verify_integration():
    print("Initializing agents...")
    agent = RiskScoringAgent()
    forensic = ForensicAnalysisAgent()
    
    symbol = "HDFCBANK.NS"
    print(f"Fetching data for {symbol}...")
    
    # We expect this to fetch live/mocked yahoo data
    data = forensic.analyze_yahoo_finance_data(symbol, quarters=1)
    
    if not data.get("success"):
        print("Failed to fetch forensic data.")
        return

    print("Calculating Risk Score...")
    assessment = agent.calculate_risk_score(symbol, data)
    
    # Check Compliance Risk specifically
    # RiskCategory.COMPLIANCE_RISK
    comp_score = assessment.risk_category_scores.get(RiskCategory.COMPLIANCE_RISK)
    
    if comp_score:
        print(f"\n--- RESULTS for {symbol} ---")
        print(f"Compliance Risk Score: {comp_score.score}")
        print(f"Confidence: {comp_score.confidence}")
        print(f"Factors: {comp_score.factors}")
        
        # Validation Logic
        # HDFC Compliance Score is ~75.0 (from previous run)
        # Risk Score should be 100 - 75 = 25.0
        # Placeholder was 30.0
        
        if abs(comp_score.score - 25.0) < 5:
            print("✅ SUCCESS: Score matches expected (approx 25.0 derived from 75.0)")
        elif comp_score.score == 30.0 and "integration failed" in str(comp_score.factors):
             print("❌ FAILURE: Fallback placeholder used. Integration failed.")
        else:
             print(f"⚠️ UNEXPECTED: Score is {comp_score.score}. Check logic.")
             
    else:
        print("❌ FAILURE: Compliance Risk category missing.")

if __name__ == "__main__":
    asyncio.run(verify_integration())
