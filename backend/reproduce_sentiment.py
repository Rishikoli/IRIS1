import sys
import os
import asyncio
import logging

# Setup paths
current_file = os.path.abspath(__file__)
backend_root = os.path.dirname(current_file) # backend/
sys.path.insert(0, backend_root)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from src.agents.forensic.agent5_reporting import ReportingAgent

async def test_sentiment():
    try:
        agent = ReportingAgent()
        company_symbol = "RELIANCE.NS"
        findings = [{"observation": "Test Finding"}]
        
        print(f"Testing RFI generation for {company_symbol}...")
        result = await agent.generate_enforcement_rfi(company_symbol, findings)
        print("Result:", result)
        
    except Exception as e:
        print(f"Caught exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_sentiment())
