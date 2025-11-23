"""
Benford's Law Analysis

This module implements Benford's Law analysis for detecting anomalies in numerical data.
Benford's Law predicts the frequency distribution of leading digits in many naturally occurring
collections of numbers.
"""
import numpy as np
from typing import Dict, List, Tuple, Union
from collections import defaultdict
from scipy import stats

def get_leading_digit(number: Union[str, float, int]) -> str:
    """
    Extract the first non-zero digit of a number.
    
    Args:
        number: The input number (can be string, float, or int)
        
    Returns:
        str: The first non-zero digit as a string, or '0' for zero
    """
    try:
        # Convert to string and remove any leading/trailing whitespace
        num_str = str(number).strip()
        
        # Handle negative numbers
        if num_str.startswith('-'):
            num_str = num_str[1:]
            
        # Handle decimal numbers by replacing the decimal point
        if '.' in num_str:
            num_str = num_str.replace('.', '')
        
        # Remove any leading zeros
        num_str = num_str.lstrip('0')
        
        # If we have an empty string, it was just zeros
        if not num_str:
            return '0'
            
        # Return the first non-zero digit
        return num_str[0]
    except (ValueError, TypeError, IndexError):
        return '0'  # Default to '0' for any invalid input

def benfords_law_expected() -> Dict[int, float]:
    """Return the expected distribution of first digits according to Benford's Law."""
    return {d: np.log10(1 + 1/d) for d in range(1, 10)}

def benfords_law_analysis(
    data: List[Union[int, float]],
    confidence_level: float = 0.95
) -> Dict:
    """
    Perform Benford's Law analysis on a dataset.
    
    Args:
        data: List of numerical values to analyze
        confidence_level: Confidence level for chi-square test (default: 0.95)
        
    Returns:
        Dict containing analysis results including:
        - observed_counts: Count of each leading digit (1-9)
        - expected_counts: Expected count of each digit per Benford's Law
        - chi2: Chi-square statistic
        - p_value: p-value of the chi-square test
        - significant: Whether the distribution deviates significantly from Benford's Law
        - mad: Mean Absolute Deviation
        - mad_conclusion: Interpretation of MAD value
    """
    # Filter out zeros and non-positive numbers
    filtered_data = [x for x in data if x > 0]
    
    if not filtered_data:
        raise ValueError("No valid positive numbers found in the input data")
    
    # Count leading digits
    digit_counts = defaultdict(int)
    for num in filtered_data:
        digit_str = get_leading_digit(num)
        try:
            digit = int(digit_str)
            if 1 <= digit <= 9:  # Only consider digits 1-9
                digit_counts[digit] += 1
        except (ValueError, TypeError):
            continue  # Skip invalid digits
    
    # Calculate observed and expected frequencies
    total_count = sum(digit_counts.values())
    if total_count == 0:
        raise ValueError("No valid leading digits found in the input data")
        
    expected_dist = benfords_law_expected()
    
    # Initialize observed and expected lists
    digits = list(range(1, 10))
    observed = [digit_counts.get(d, 0) for d in digits]
    expected = [expected_dist[d] * total_count for d in digits]
    
    # Calculate digit distribution (proportions)
    digit_distribution = {str(d): count/total_count for d, count in digit_counts.items()}
    
    # Perform chi-square test
    chi2, p_value = stats.chisquare(f_obs=observed, f_exp=expected)
    
    # Calculate Mean Absolute Deviation (MAD)
    mad = np.mean([abs(observed[i]/total_count - expected_dist[d]) for i, d in enumerate(digits)])
    
    # Interpret MAD (Nigrini, 2012)
    if mad < 0.006:
        mad_conclusion = "Close conformity"
    elif mad < 0.012:
        mad_conclusion = "Acceptable conformity"
    elif mad < 0.015:
        mad_conclusion = "Marginally acceptable"
    else:
        mad_conclusion = "Nonconformity"
    
    # Prepare results
    result = {
        'observed_counts': dict(zip(digits, observed)),
        'expected_counts': dict(zip(digits, expected)),
        'digit_distribution': digit_distribution,
        'chi2': chi2,
        'p_value': p_value,
        'significant': p_value < (1 - confidence_level),
        'mad': mad,
        'mad_conclusion': mad_conclusion,
        'total_count': total_count
    }
    
    return result
