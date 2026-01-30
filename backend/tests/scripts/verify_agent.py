
import sys
import os

# Add backend to path
sys.path.append('/home/aditya/Downloads/IRIS/backend')

try:
    from src.agents.agent8_market_sentiment import MarketSentimentAgent
    print("Successfully imported MarketSentimentAgent")
except Exception as e:
    print(f"Error importing MarketSentimentAgent: {e}")
    sys.exit(1)
