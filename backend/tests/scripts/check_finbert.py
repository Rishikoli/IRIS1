import logging
from transformers import pipeline
import sys

# Configure logging to show info
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_finbert():
    print("Attempting to load FinBERT model...")
    try:
        classifier = pipeline("sentiment-analysis", model="ProsusAI/finbert")
        print("Successfully loaded FinBERT model!")
        
        # Test with a sample sentence
        result = classifier("Markets are rallying today.")
        print(f"Test result: {result}")
        
    except Exception as e:
        print(f"Error loading FinBERT: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_finbert()
