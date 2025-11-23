"""Tests for Altman Z-Score calculation module."""
import pytest
from src.analysis.forensic.zscore import (
    calculate_altman_zscore,
    ZScoreModel,
    ZScoreRiskCategory
)

def test_altman_zscore_original_safe():
    """Test original Z-Score model with a safe company."""
    result = calculate_altman_zscore(
        working_capital=100000,
        total_assets=500000,
        retained_earnings=200000,
        ebit=75000,
        market_value_equity=400000,
        total_liabilities=100000,
        sales=1000000,
        model=ZScoreModel.ORIGINAL
    )
    
    assert result['z_score'] > 2.99
    assert result['risk_category'] == ZScoreRiskCategory.SAFE
    assert result['model_used'] == ZScoreModel.ORIGINAL
    assert "good financial health" in result['interpretation'].lower()
    assert all(key in result['components'] for key in [
        'working_capital_assets_ratio',
        'retained_earnings_assets_ratio',
        'ebit_assets_ratio',
        'market_equity_liabilities_ratio',
        'sales_assets_ratio'
    ])

def test_altman_zscore_original_distress():
    """Test original Z-Score model with a company in distress."""
    result = calculate_altman_zscore(
        working_capital=10000,
        total_assets=500000,
        retained_earnings=-100000,
        ebit=-50000,
        market_value_equity=50000,
        total_liabilities=450000,
        sales=500000,
        model=ZScoreModel.ORIGINAL
    )
    
    assert result['z_score'] < 1.81
    assert result['risk_category'] == ZScoreRiskCategory.DISTRESS
    assert "high risk of bankruptcy" in result['interpretation'].lower()

def test_altman_zscore_emerging_market():
    """Test emerging market Z-Score model."""
    result = calculate_altman_zscore(
        working_capital=150000,
        total_assets=800000,
        retained_earnings=300000,
        ebit=120000,
        market_value_equity=600000,
        total_liabilities=200000,
        sales=1500000,
        model=ZScoreModel.EMERGING_MARKET
    )
    
    assert result['z_score'] > 2.6
    assert result['risk_category'] == ZScoreRiskCategory.SAFE
    assert result['model_used'] == ZScoreModel.EMERGING_MARKET

def test_altman_zscore_private_company():
    """Test private company Z-Score model."""
    result = calculate_altman_zscore(
        working_capital=80000,
        total_assets=500000,
        retained_earnings=150000,
        ebit=60000,
        market_value_equity=300000,  # For private companies, book value is used
        total_liabilities=200000,
        sales=900000,
        model=ZScoreModel.PRIVATE
    )
    
    assert result['z_score'] > 2.9
    assert result['risk_category'] == ZScoreRiskCategory.SAFE
    assert result['model_used'] == ZScoreModel.PRIVATE

def test_altman_zscore_edge_cases():
    """Test edge cases and error conditions."""
    # Test with zero total assets
    with pytest.raises(ValueError, match="Total assets cannot be zero"):
        calculate_altman_zscore(
            working_capital=10000,
            total_assets=0,
            retained_earnings=5000,
            ebit=2000,
            market_value_equity=15000,
            total_liabilities=5000,
            sales=50000
        )
    
    # Test with zero total liabilities (for market_equity_liabilities_ratio)
    result = calculate_altman_zscore(
        working_capital=100000,
        total_assets=500000,
        retained_earnings=200000,
        ebit=75000,
        market_value_equity=400000,
        total_liabilities=0,  # Will make market_equity_liabilities_ratio infinite
        sales=1000000
    )
    assert result['components']['market_equity_liabilities_ratio'] == 0  # Should handle division by zero
    
    # Test with negative EBIT
    result = calculate_altman_zscore(
        working_capital=100000,
        total_assets=500000,
        retained_earnings=200000,
        ebit=-50000,  # Negative EBIT
        market_value_equity=400000,
        total_liabilities=100000,
        sales=1000000
    )
    assert result['components']['ebit_assets_ratio'] < 0  # Should handle negative EBIT

def test_altman_zscore_model_comparison():
    """Compare results between different Z-Score models."""
    # Same company, different models
    params = {
        'working_capital': 120000,
        'total_assets': 600000,
        'retained_earnings': 250000,
        'ebit': 90000,
        'market_value_equity': 450000,
        'total_liabilities': 150000,
        'sales': 1200000
    }
    
    original = calculate_altman_zscore(**params, model=ZScoreModel.ORIGINAL)
    emerging = calculate_altman_zscore(**params, model=ZScoreModel.EMERGING_MARKET)
    private = calculate_altman_zscore(**params, model=ZScoreModel.PRIVATE)
    
    # All models should agree on the risk category for this healthy company
    assert original['risk_category'] == ZScoreRiskCategory.SAFE
    assert emerging['risk_category'] == ZScoreRiskCategory.SAFE
    assert private['risk_category'] == ZScoreRiskCategory.SAFE
    
    # The actual Z-scores should be different between models
    assert len({original['z_score'], emerging['z_score'], private['z_score']}) == 3
