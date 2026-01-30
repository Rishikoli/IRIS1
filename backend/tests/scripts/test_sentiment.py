
import sys
import os
import logging

# Configure logging to show up in stdout
logging.basicConfig(level=logging.INFO)

# Add backend to path
sys.path.append('/home/aditya/Downloads/IRIS/backend')

from src.agents.agent8_market_sentiment import market_sentiment_agent

# Dummy headlines
headlines = [
    {"title": "Market hits all time high as tech stocks rally", "link": "http://example.com", "pubDate": "2024-01-01"},
    {"title": "Inflation concerns persist despite good jobs data", "link": "http://example.com", "pubDate": "2024-01-01"},
    {"title": "Company X reports record earnings", "link": "http://example.com", "pubDate": "2024-01-01"}
]

print("Starting sentiment analysis test...")
result = market_sentiment_agent._analyze_headlines_with_gemini(headlines)
print("\nResult:")
print(result)
