"""
Forensic Analysis Module

This module provides financial forensic analysis tools including:
- Benford's Law analysis
- Altman Z-Score calculation
- Beneish M-Score calculation
- Financial ratio analysis
"""

from .benfords_law import benfords_law_analysis
from .zscore import calculate_altman_zscore
from .mscore import calculate_beneish_mscore
from .ratios import FinancialRatios

__all__ = [
    'benfords_law_analysis',
    'calculate_altman_zscore',
    'calculate_beneish_mscore',
    'FinancialRatios'
]
