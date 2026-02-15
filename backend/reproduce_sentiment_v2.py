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

from src.agents.agent8_market_sentiment import market_sentiment_agent

async def test_sentiment():
    try:
        company_symbol = "RELIANCE.NS"
        print(f"Testing Sentiment Analysis for {company_symbol}...")
        result = await market_sentiment_agent.get_sentiment_analysis(company_symbol)
        print("Result:", result)
        
    except Exception as e:
        print(f"Caught exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_sentiment())
