from transformers import pipeline
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_zeroshot():
    try:
        logger.info("Loading Zero-Shot Pipeline...")
        classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        
        text = "The company is under investigation for accounting irregularities and potential embezzlement of funds."
        labels = ["Fraud", "Litigation", "Regulatory Fine", "Embezzlement", "Bribery", "Normal Business"]
        
        logger.info(f"Analyzing text: {text}")
        result = classifier(text, labels)
        
        logger.info("Result:")
        print(result)
        
    except Exception as e:
        logger.error(f"Failed: {e}")

if __name__ == "__main__":
    test_zeroshot()
