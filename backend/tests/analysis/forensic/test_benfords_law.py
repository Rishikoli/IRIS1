"""Tests for Benford's Law analysis module."""
import pytest
import numpy as np
from src.analysis.forensic.benfords_law import (
    benfords_law_analysis,
    get_leading_digit,
    benfords_law_expected
)

def test_get_leading_digit():
    """Test extraction of leading digits."""
    from src.analysis.forensic.benfords_law import get_leading_digit
    
    # Test with positive numbers
    assert get_leading_digit('123') == '1'
    assert get_leading_digit('5') == '5'
    assert get_leading_digit('0.00456') == '4'
    
    # Test with negative numbers (should ignore sign)
    assert get_leading_digit('-789') == '7'
    
    # Test with zero (should return '0')
    assert get_leading_digit('0') == '0'
    
    # Test with very small numbers
    assert get_leading_digit('0.000000123') == '1'

def test_benfords_law_expected():
    """Test expected Benford's Law distribution."""
    expected = benfords_law_expected()
    assert len(expected) == 9  # Digits 1-9
    assert all(1 <= d <= 9 for d in expected.keys())
    assert abs(sum(expected.values()) - 1.0) < 1e-10  # Should sum to ~1.0
    assert expected[1] > expected[9]  # 1 should be more frequent than 9

def test_benfords_law_analysis_perfect_fit():
    """Test with data that perfectly fits Benford's Law."""
    # Generate data that follows Benford's Law
    np.random.seed(42)
    benford_probs = [0.301, 0.176, 0.125, 0.097, 0.079, 0.067, 0.058, 0.051, 0.046]
    digits = list(range(1, 10))
    data = np.random.choice(digits, size=10000, p=benford_probs).tolist()
    
    # Add some magnitude variation
    data = [d * (10 ** np.random.randint(0, 6)) for d in data]
    
    # Add some decimal numbers
    data.extend([d * (10 ** -np.random.randint(1, 4)) for d in data[:1000]])
    
    # Perform analysis
    result = benfords_law_analysis(data, confidence_level=0.95)
    
    # Should not be significantly different from Benford's Law
    assert not result['significant'], \
        f"Expected data to fit Benford's Law (p={result['p_value']:.4f}, mad={result['mad']:.4f})"
    assert result['mad'] < 0.015, "MAD too high for perfect fit data"
    assert result['p_value'] > 0.10, f"p-value too low: {result['p_value']:.4f}"

def test_benfords_law_analysis_non_benford():
    """Test with data that doesn't follow Benford's Law."""
    # Uniform distribution (doesn't follow Benford's Law)
    np.random.seed(42)
    data = np.random.uniform(1, 10000, 10000).tolist()
    
    # Perform analysis
    result = benfords_law_analysis(data, confidence_level=0.99)
    
    # Should be significantly different from Benford's Law
    assert result['significant']
    assert result['mad'] > 0.015  # Should show nonconformity
    assert result['p_value'] < 0.01  # Statistically significant difference

def test_benfords_law_analysis_edge_cases():
    """Test edge cases in Benford's Law analysis."""
    from src.analysis.forensic.benfords_law import benfords_law_analysis
    
    # Test with empty list
    with pytest.raises(ValueError, match="No valid positive numbers found"):
        benfords_law_analysis([])
    
    # Test with list containing only zeros and negative numbers
    with pytest.raises(ValueError, match="No valid positive numbers found"):
        benfords_law_analysis([0, -1, -2, -3])
    
    # Test with single number (should work with a single positive number)
    result = benfords_law_analysis([42.0])  # Pass as float
    assert 'digit_distribution' in result, "Result should contain 'digit_distribution' key"
    assert float(result['digit_distribution'].get('4', 0)) > 0, "Should have digit 4 in distribution"
    
    # Test with a list containing some valid numbers and some invalid ones
    result = benfords_law_analysis([0, -1, 42.0, 100.0, -5, 3.14])
    assert 'digit_distribution' in result, "Result should contain 'digit_distribution' key"
    non_zero_counts = sum(1 for d in result['digit_distribution'].values() if float(d) > 0)
    assert non_zero_counts >= 1, f"Expected at least 1 non-zero digit count, got {non_zero_counts}"

def test_benfords_law_analysis_confidence_level():
    """Test different confidence levels."""
    # Generate some non-Benford data
    np.random.seed(42)
    data = np.random.uniform(1, 10000, 1000).tolist()
    
    # With 90% confidence (more likely to be significant)
    result_90 = benfords_law_analysis(data, confidence_level=0.90)
    
    # With 99% confidence (less likely to be significant)
    result_99 = benfords_law_analysis(data, confidence_level=0.99)
    
    # The same data might be significant at 90% but not at 99%
    if result_90['p_value'] < 0.1:  # Significant at 90%
        if result_99['p_value'] > 0.01:  # Not significant at 99%
            assert result_90['significant'] and not result_99['significant']
