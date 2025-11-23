"""
Beneish M-Score Calculation

This module implements the Beneish M-Score, an 8-variable model for detecting the likelihood of
earnings manipulation in financial statements.
"""
from typing import Dict, Optional, Union
import numpy as np

class MScoreResult:
    """Container for M-Score calculation results."""
    
    def __init__(self, m_score: float, is_likely_manipulator: bool):
        self.m_score = m_score
        self.is_likely_manipulator = is_likely_manipulator
        self.threshold = -1.78  # Standard threshold for manipulation detection
        
    def to_dict(self) -> Dict:
        """Convert results to dictionary format."""
        return {
            'm_score': round(self.m_score, 4),
            'is_likely_manipulator': self.is_likely_manipulator,
            'threshold': self.threshold,
            'interpretation': self._get_interpretation()
        }
        
    def _get_interpretation(self) -> str:
        """Get human-readable interpretation of the M-Score."""
        if self.m_score > -1.78:
            return "The company is likely manipulating earnings (M-Score > -1.78)."
        return "The company is not likely manipulating earnings (M-Score <= -1.78)."

def calculate_beneish_mscore(
    sales: float,
    cogs: float,
    sga: float,
    dep: float,
    current_assets: float,
    current_liabilities: float,
    total_assets: float,
    total_assets_prev: float,
    ppe: float,
    ppe_prev: float,
    net_income: float,
    cash_flow_ops: float,
    long_term_debt: float,
    long_term_debt_prev: float,
    sales_prev: float,
    sga_prev: float,
    dep_prev: float,
    current_assets_prev: float,
    current_liabilities_prev: float,
) -> Dict:
    """
    Calculate the Beneish M-Score for a company.
    
    The M-Score is a probabilistic model that identifies companies that are likely to be
    manipulating their reported earnings.
    
    Args:
        sales: Current year sales/revenue
        cogs: Current year cost of goods sold
        sga: Current year selling, general and administrative expenses
        dep: Current year depreciation and amortization
        current_assets: Current year current assets
        current_liabilities: Current year current liabilities
        total_assets: Current year total assets
        total_assets_prev: Previous year total assets
        ppe: Current year property, plant, and equipment (PPE)
        ppe_prev: Previous year PPE
        net_income: Current year net income
        cash_flow_ops: Current year cash flow from operations
        long_term_debt: Current year long-term debt
        long_term_debt_prev: Previous year long-term debt
        sales_prev: Previous year sales/revenue
        sga_prev: Previous year SG&A
        dep_prev: Previous year depreciation and amortization
        current_assets_prev: Previous year current assets
        current_liabilities_prev: Previous year current liabilities
        
    Returns:
        Dictionary containing M-Score and interpretation
    """
    # Calculate the 8 variables for the M-Score
    
    # 1. Days' Sales in Receivables Index (DSRI)
    # Add small epsilon to avoid division by zero
    epsilon = 1e-10
    
    # Calculate DSRI with input validation
    try:
        dsri = ((sales / max(current_assets - current_assets_prev + sales, epsilon)) / 
               (sales_prev / max(sales_prev, epsilon)))
    except (ZeroDivisionError, ValueError):
        dsri = 1.0  # Default to neutral value if calculation fails
    
    # 2. Gross Margin Index (GMI)
    gmi = ((sales_prev - cogs) / sales_prev) / ((sales - cogs) / sales)
    
    # 3. Asset Quality Index (AQI)
    aqi = (1 - ((current_assets + ppe) / total_assets)) / \
          (1 - ((current_assets_prev + ppe_prev) / total_assets_prev))
    
    # 4. Sales Growth Index (SGI)
    sgi = sales / sales_prev
    
    # 5. Depreciation Index (DEPI)
    depi = (dep_prev / (ppe_prev + dep_prev)) / (dep / (ppe + dep))
    
    # 6. Sales, General and Administrative Expenses Index (SGAI)
    sgai = (sga / sales) / (sga_prev / sales_prev)
    
    # 7. Leverage Index (LVGI)
    lvgi = ((current_liabilities + long_term_debt) / total_assets) / \
           ((current_liabilities_prev + long_term_debt_prev) / total_assets_prev)
    
    # 8. Total Accruals to Total Assets (TATA)
    tata = (net_income - cash_flow_ops) / total_assets
    
    # Calculate M-Score
    m_score = (-4.84 + 0.92 * dsri + 0.528 * gmi + 0.404 * aqi + 0.892 * sgi + 
               0.115 * depi - 0.172 * sgai + 4.679 * tata - 0.327 * lvgi)
    
    # Check if likely manipulator
    is_manipulator = m_score > -1.78
    
    # Create result object
    result = MScoreResult(m_score, is_manipulator)
    
    # Add detailed breakdown
    breakdown = {
        'variables': {
            'DSRI': round(dsri, 4),
            'GMI': round(gmi, 4),
            'AQI': round(aqi, 4),
            'SGI': round(sgi, 4),
            'DEPI': round(depi, 4),
            'SGAI': round(sgai, 4),
            'LVGI': round(lvgi, 4),
            'TATA': round(tata, 4)
        },
        'interpretation': {
            'DSRI': 'High values may indicate revenue inflation',
            'GMI': 'Higher values may indicate deteriorating margins',
            'AQI': 'Higher values may indicate increased risk',
            'SGI': 'Rapid growth may indicate aggressive revenue recognition',
            'DEPI': 'Lower values may indicate over-depreciation',
            'SGAI': 'Lower values may indicate expense manipulation',
            'LVGI': 'Higher values indicate increased leverage',
            'TATA': 'Higher values may indicate earnings manipulation'
        }
    }
    
    return {**result.to_dict(), 'breakdown': breakdown}
