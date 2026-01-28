"""
Simple test script for sentiment analysis without database

Tests FinBERT sentiment analysis on sample financial news.
"""

import sys
print("Loading FinBERT model (this may take a moment)...")

from sentiment_analyzer import get_analyzer

def main():
    print("\n" + "="*70)
    print("FINBERT SENTIMENT ANALYSIS TEST")
    print("="*70 + "\n")
    
    # Initialize analyzer
    try:
        analyzer = get_analyzer()
        print("✓ FinBERT model loaded successfully!\n")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return 1
    
    # Test cases - Indian market news
    test_cases = [
        {
            'text': "Reliance Industries reported a 25% year-on-year growth in Q4 earnings, beating market estimates.",
            'expected': 'positive'
        },
        {
            'text': "SEBI imposed a penalty on the company for accounting irregularities. Stock crashed 15% in early trading.",
            'expected': 'negative'
        },
        {
            'text': "The market remained stable today with modest gains across major indices. Nifty closed at 22,000.",
            'expected': 'neutral'
        },
        {
            'text': "Infosys announces mega buyback program worth Rs 9,000 crore, shares surge on strong quarterly results.",
            'expected': 'positive'
        },
        {
            'text': "HDFC Bank facing regulatory scrutiny over lending practices. RBI orders detailed audit.",
            'expected': 'negative'
        },
    ]
    
    correct = 0
    total = len(test_cases)
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}/{total}")
        print(f"Text: {test['text'][:80]}...")
        
        # Analyze
        result = analyzer.get_detailed_scores(test['text'])
        
        # Display results
        print(f"  Predicted: {result['sentiment'].upper()} ({result['confidence']:.1%} confidence)")
        print(f"  Expected: {test['expected'].upper()}")
        print(f"  Scores: Positive={result['positive_score']:.2f}, "
              f"Negative={result['negative_score']:.2f}, "
              f"Neutral={result['neutral_score']:.2f}")
        
        # Check accuracy
        if result['sentiment'] == test['expected']:
            print("  ✓ Correct")
            correct += 1
        else:
            print("  ✗ Incorrect")
        
        print()
    
    # Final score
    accuracy = (correct / total) * 100
    print("="*70)
    print(f"RESULTS: {correct}/{total} correct ({accuracy:.1f}% accuracy)")
    print("="*70)
    
    if accuracy >= 80:
        print("\n🎉 FinBERT is working excellently!")
    elif accuracy >= 60:
        print("\n✓ FinBERT is working well (some ambiguous cases)")
    else:
        print("\n⚠️  Results vary - this is normal for financial text")
    
    print("\nNext step: Set up PostgreSQL and run full monitoring system")
    print("Run: python3 news_monitor.py")
    
    return 0


if __name__ == "__main__":
    exit(main())
