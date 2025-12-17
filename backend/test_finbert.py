import sys
import os
import asyncio
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agents.agent7_qa_rag import qa_system

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_finbert():
    print("Testing FinBERT integration...")
    
    # Test direct sentiment analysis method
    test_text = "The company reported a significant increase in revenue and profits, exceeding market expectations."
    print(f"\nAnalyzing text: '{test_text}'")
    
    sentiment = qa_system._analyze_sentiment_with_finbert(test_text)
    print(f"Sentiment result: {sentiment}")
    
    if sentiment['label'] == 'Positive' and sentiment['score'] > 0.5:
        print("SUCCESS: Positive sentiment correctly identified.")
    else:
        print("FAILURE: Sentiment analysis result unexpected.")

    # Test negative sentiment
    test_text_neg = "The company faces severe liquidity crunch and declining market share."
    print(f"\nAnalyzing text: '{test_text_neg}'")
    sentiment_neg = qa_system._analyze_sentiment_with_finbert(test_text_neg)
    print(f"Sentiment result: {sentiment_neg}")
    
    if sentiment_neg['label'] == 'Negative':
        print("SUCCESS: Negative sentiment correctly identified.")
    else:
        print("FAILURE: Negative sentiment result unexpected.")

if __name__ == "__main__":
    asyncio.run(test_finbert())
