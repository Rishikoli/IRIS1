
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
except Exception as e:
    print(f"Import Error: {e}")
    sys.exit(1)

def check_mock_risk():
    print(f"Checking mock 'HIGHRISK' company...")
    
    risk_agent = RiskScoringAgent()
    
    # Mock data is empty as the agent short-circuits on symbol name
    assessment = risk_agent.calculate_risk_score("HIGHRISK", {})
    score = assessment.overall_risk_score
    
    print(f"Company: HIGHRISK, Risk Score: {score}")
    
    if score == 75.0:
        print(f"\n*** MATCH FOUND: HIGHRISK HAS RISK SCORE 75 ***\n")
    else:
        print(f"Score is {score}, not 75.")

if __name__ == "__main__":
    check_mock_risk()
