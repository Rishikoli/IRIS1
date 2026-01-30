import sys
import os

# Add backend root to path
sys.path.insert(0, os.getcwd())

from src.agents.agent8_market_sentiment import market_sentiment_agent
import json

def test_sentiment():
    symbol = "RELIANCE.NS"
    print(f"Testing sentiment analysis for {symbol}...")
    try:
        result = market_sentiment_agent.get_sentiment_analysis(symbol)
        print("Result:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"CRASHED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sentiment()
