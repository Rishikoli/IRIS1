"""
Altman Z-Score Calculation

This module implements the Altman Z-Score, a financial model for predicting the probability
of a company going bankrupt within two years.
"""
from typing import Dict, Optional, Union
from enum import Enum

class ZScoreRiskCategory(str, Enum):
    SAFE = "SAFE"
    GREY = "GREY"
    DISTRESS = "DISTRESS"

class ZScoreModel(str, Enum):
    ORIGINAL = "original"
    EMERGING_MARKET = "emerging_market"
    PRIVATE = "private"

def calculate_altman_zscore(
    working_capital: float,
    total_assets: float,
    retained_earnings: float,
    ebit: float,
    market_value_equity: float,
    total_liabilities: float,
    sales: float,
    model: ZScoreModel = ZScoreModel.ORIGINAL,
) -> Dict[str, Union[float, str, ZScoreRiskCategory]]:
    """
    Calculate the Altman Z-Score for a company.
    
    The Z-Score is a financial model for predicting the probability of a company 
    going bankrupt within two years.
    
    Args:
        working_capital: Working capital (current assets - current liabilities)
        total_assets: Total assets
        retained_earnings: Retained earnings
        ebit: Earnings Before Interest and Taxes
        market_value_equity: Market value of equity
        total_liabilities: Total liabilities
        sales: Total sales/revenue
        model: Z-Score model to use (original, emerging_market, or private)
        
    Returns:
        Dictionary containing:
        - z_score: The calculated Z-Score
        - risk_category: SAFE (>2.99), GREY (1.81-2.99), or DISTRESS (<1.81)
        - model_used: The model used for calculation
    """
    if total_assets == 0:
        raise ValueError("Total assets cannot be zero")
    
    # Calculate the components
    x1 = working_capital / total_assets
    x2 = retained_earnings / total_assets
    x3 = ebit / total_assets
    x4 = market_value_equity / total_liabilities if total_liabilities != 0 else 0
    x5 = sales / total_assets
    
    # Calculate Z-Score based on the selected model
    if model == ZScoreModel.ORIGINAL:
        # Original Z-Score (for public manufacturing companies)
        z_score = 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 1.0 * x5
        
        # Risk categories for original model
        if z_score > 2.99:
            risk_category = ZScoreRiskCategory.SAFE
        elif z_score > 1.81:
            risk_category = ZScoreRiskCategory.GREY
        else:
            risk_category = ZScoreRiskCategory.DISTRESS
            
    elif model == ZScoreModel.EMERGING_MARKET:
        # Emerging Market Z-Score (for emerging market companies)
        z_score = 6.56 * x1 + 3.26 * x2 + 6.72 * x3 + 1.05 * x4
        
        # Risk categories for emerging markets
        if z_score > 2.6:
            risk_category = ZScoreRiskCategory.SAFE
        elif z_score > 1.1:
            risk_category = ZScoreRiskCategory.GREY
        else:
            risk_category = ZScoreRiskCategory.DISTRESS
            
    elif model == ZScoreModel.PRIVATE:
        # Private Company Z-Score (for private companies)
        z_score = 0.717 * x1 + 0.847 * x2 + 3.107 * x3 + 0.42 * x4 + 0.998 * x5
        
        # Risk categories for private companies
        if z_score > 2.9:
            risk_category = ZScoreRiskCategory.SAFE
        elif z_score > 1.23:
            risk_category = ZScoreRiskCategory.GREY
        else:
            risk_category = ZScoreRiskCategory.DISTRESS
    else:
        raise ValueError(f"Unknown Z-Score model: {model}")
    
    return {
        'z_score': round(z_score, 4),
        'risk_category': risk_category,
        'model_used': model,
        'components': {
            'working_capital_assets_ratio': round(x1, 4),
            'retained_earnings_assets_ratio': round(x2, 4),
            'ebit_assets_ratio': round(x3, 4),
            'market_equity_liabilities_ratio': round(x4, 4),
            'sales_assets_ratio': round(x5, 4)
        },
        'interpretation': {
            ZScoreRiskCategory.SAFE: "The company is in good financial health with a low risk of bankruptcy.",
            ZScoreRiskCategory.GREY: "The company is in a grey zone with moderate risk of financial distress.",
            ZScoreRiskCategory.DISTRESS: "The company is in financial distress with a high risk of bankruptcy."
        }[risk_category]
    }
