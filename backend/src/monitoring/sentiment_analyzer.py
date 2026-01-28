"""
Sentiment Analyzer using FinBERT

Analyzes sentiment of financial news articles.
"""

from transformers import pipeline
import logging
from typing import Dict, List
import torch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """FinBERT-based sentiment analyzer for financial text"""
    
    def __init__(self, model_name: str = "ProsusAI/finbert"):
        """
        Initialize sentiment analyzer
        
        Args:
            model_name: Hugging Face model name
        """
        logger.info(f"Loading sentiment model: {model_name}...")
        
        self.model_name = model_name
        self.device = 0 if torch.cuda.is_available() else -1
        
        # Load pipeline with truncation enabled
        self.pipeline = pipeline(
            "sentiment-analysis",
            model=model_name,
            device=self.device,
            truncation=True,
            max_length=512
        )
        
        logger.info(f"✓ Model loaded on {'GPU' if self.device == 0 else 'CPU'}")
    
    def analyze(self, text: str, max_length: int = 512) -> Dict:
        """
        Analyze sentiment of text
        
        Args:
            text: Text to analyze
            max_length: Maximum text length
            
        Returns:
            Dictionary with sentiment, confidence, and scores
        """
        # Truncate if too long
        if len(text) > max_length * 4:  # Rough char estimate
            text = text[:max_length * 4]
        
        try:
            result = self.pipeline(text)[0]
            
            # FinBERT returns: {'label': 'positive/negative/neutral', 'score': confidence}
            return {
                'sentiment': result['label'].lower(),
                'confidence': result['score'],
                'model': self.model_name
            }
        
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {
                'sentiment': 'neutral',
                'confidence': 0.0,
                'model': self.model_name,
                'error': str(e)
            }
    
    def analyze_batch(self, texts: List[str], max_length: int = 512) -> List[Dict]:
        """
        Analyze sentiment of multiple texts (faster)
        
        Args:
            texts: List of texts to analyze
            max_length: Maximum text length
            
        Returns:
            List of sentiment dictionaries
        """
        # Truncate if needed
        processed_texts = [
            text[:max_length * 4] if len(text) > max_length * 4 else text
            for text in texts
        ]
        
        try:
            results = self.pipeline(processed_texts)
            
            return [
                {
                    'sentiment': r['label'].lower(),
                    'confidence': r['score'],
                    'model': self.model_name
                }
                for r in results
            ]
        
        except Exception as e:
            logger.error(f"Batch sentiment analysis failed: {e}")
            return [
                {
                    'sentiment': 'neutral',
                    'confidence': 0.0,
                    'model': self.model_name,
                    'error': str(e)
                }
                for _ in texts
            ]
    
    def get_detailed_scores(self, text: str) -> Dict:
        """
        Get detailed sentiment scores (not available in pipeline by default)
        For more detailed analysis, would need to use model directly
        
        Returns:
            Dictionary with positive, negative, neutral scores
        """
        # This is a simplified version
        # For true probabilities, we'd need to use the model directly
        result = self.analyze(text)
        
        # Approximate scores based on confidence
        sentiment = result['sentiment']
        confidence = result['confidence']
        
        scores = {
            'positive': 0.33,
            'negative': 0.33,
            'neutral': 0.34
        }
        
        # Adjust based on prediction
        if sentiment == 'positive':
            scores['positive'] = confidence
            scores['neutral'] = (1 - confidence) / 2
            scores['negative'] = (1 - confidence) / 2
        elif sentiment == 'negative':
            scores['negative'] = confidence
            scores['neutral'] = (1 - confidence) / 2
            scores['positive'] = (1 - confidence) / 2
        else:  # neutral
            scores['neutral'] = confidence
            scores['positive'] = (1 - confidence) / 2
            scores['negative'] = (1 - confidence) / 2
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'positive_score': scores['positive'],
            'negative_score': scores['negative'],
            'neutral_score': scores['neutral'],
            'model': self.model_name
        }


# Singleton instance
_analyzer_instance = None

def get_analyzer() -> SentimentAnalyzer:
    """Get sentiment analyzer instance (singleton)"""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = SentimentAnalyzer()
    return _analyzer_instance


if __name__ == "__main__":
    # Test sentiment analyzer
    analyzer = get_analyzer()
    
    # Test cases
    test_texts = [
        "Reliance Industries reported 25% growth in Q4 earnings, beating estimates.",
        "SEBI penalizes company for accounting fraud, stock crashes 15%.",
        "Market remains stable with modest gains in key indices."
    ]
    
    print("\n" + "="*50)
    print("Sentiment Analysis Test")
    print("="*50 + "\n")
    
    for text in test_texts:
        result = analyzer.get_detailed_scores(text)
        print(f"Text: {text[:60]}...")
        print(f"Sentiment: {result['sentiment'].upper()}")
        print(f"Confidence: {result['confidence']:.2%}")
        print(f"Scores: P={result['positive_score']:.2f}, "
              f"NEG={result['negative_score']:.2f}, "
              f"NEU={result['neutral_score']:.2f}")
        print()
