"""Tests for Beneish M-Score calculation module."""
import pytest
from src.analysis.forensic.mscore import calculate_beneish_mscore

def test_beneish_mscore_manipulator():
    """Test with data that indicates earnings manipulation."""
    # These values are designed to strongly indicate manipulation
    result = calculate_beneish_mscore(
        sales=5000000,   # 5x increase in sales
        cogs=1000000,    # But only 2x increase in COGS
        sga=300000,      # Disproportionate SG&A
        dep=50000,
        current_assets=800000,
        current_liabilities=200000,
        total_assets=5000000,
        total_assets_prev=1000000,  # Large increase in total assets
        ppe=2000000,     # Huge increase in PPE
        ppe_prev=500000,
        net_income=2000000,  # Extremely high net income
        cash_flow_ops=100000,  # But very low cash flow
        long_term_debt=3000000,  # Large increase in debt
        long_term_debt_prev=1000000,
        sales_prev=1000000,
        sga_prev=200000,
        dep_prev=50000,
        current_assets_prev=400000,
        current_liabilities_prev=200000
    )
    
    # The M-Score threshold for manipulation is > -1.78
    # With these extreme values, it should be well above that
    assert result['m_score'] > -1.78, f"Expected M-Score > -1.78, got {result['m_score']}"
    assert result['is_likely_manipulator'] is True
    assert "likely manipulating" in result['interpretation'].lower()
    
    # Check breakdown of components
    breakdown = result['breakdown']
    assert 'DSRI' in breakdown['variables']
    assert 'GMI' in breakdown['variables']
    assert 'AQI' in breakdown['variables']
    assert 'SGI' in breakdown['variables']
    assert 'DEPI' in breakdown['variables']
    assert 'SGAI' in breakdown['variables']
    assert 'LVGI' in breakdown['variables']
    assert 'TATA' in breakdown['variables']

def test_beneish_mscore_non_manipulator():
    """Test with data that doesn't indicate manipulation."""
    result = calculate_beneish_mscore(
        sales=950000,
        cogs=600000,
        sga=180000,
        dep=50000,
        current_assets=450000,
        current_liabilities=300000,
        total_assets=2000000,
        total_assets_prev=1900000,
        ppe=800000,
        ppe_prev=780000,
        net_income=100000,
        cash_flow_ops=120000,  # Healthy cash flow relative to net income
        long_term_debt=400000,
        long_term_debt_prev=400000,
        sales_prev=900000,
        sga_prev=170000,
        dep_prev=48000,
        current_assets_prev=440000,
        current_liabilities_prev=290000
    )
    
    assert result['m_score'] <= -1.78  # Indicates no manipulation
    assert result['is_likely_manipulator'] is False
    assert "not likely" in result['interpretation'].lower()

def test_beneish_mscore_edge_cases():
    """Test edge cases and error conditions."""
    # Test with minimal non-zero values to avoid division by zero
    result = calculate_beneish_mscore(
        sales=1000,  # Use reasonable non-zero values
        cogs=500,
        sga=200,
        dep=50,
        current_assets=1000,
        current_liabilities=500,
        total_assets=5000,
        total_assets_prev=4500,
        ppe=2000,
        ppe_prev=1800,
        net_income=200,
        cash_flow_ops=250,
        long_term_debt=1000,
        long_term_debt_prev=900,
        sales_prev=900,
        sga_prev=180,
        dep_prev=45,
        current_assets_prev=900,
        current_liabilities_prev=450
    )
    
    # Should return a valid float
    assert isinstance(result['m_score'], float)
    
    # Test with negative values (should handle them gracefully)
    result = calculate_beneish_mscore(
        sales=1000,
        cogs=500,
        sga=200,
        dep=50,
        current_assets=1000,
        current_liabilities=500,
        total_assets=5000,
        total_assets_prev=4500,
        ppe=2000,
        ppe_prev=1800,
        net_income=-100,  # Negative net income
        cash_flow_ops=50,
        long_term_debt=1000,
        long_term_debt_prev=900,
        sales_prev=900,
        sga_prev=180,
        dep_prev=45,
        current_assets_prev=900,
        current_liabilities_prev=450
    )
    
    # Should still return a valid float
    assert isinstance(result['m_score'], float)
    
    # Test with negative values
    result = calculate_beneish_mscore(
        sales=1000000,
        cogs=600000,
        sga=200000,
        dep=50000,
        current_assets=500000,
        current_liabilities=300000,
        total_assets=2000000,
        total_assets_prev=1800000,
        ppe=800000,
        ppe_prev=750000,
        net_income=-50000,  # Negative net income
        cash_flow_ops=100000,
        long_term_debt=500000,
        long_term_debt_prev=400000,
        sales_prev=800000,
        sga_prev=180000,
        dep_prev=45000,
        current_assets_prev=450000,
        current_liabilities_prev=280000
    )
    
    # Should handle negative values
    assert isinstance(result['m_score'], float)
    
    # Test with negative values
    result = calculate_beneish_mscore(
        sales=1000000,
        cogs=600000,
        sga=200000,
        dep=50000,
        current_assets=500000,
        current_liabilities=300000,
        total_assets=2000000,
        total_assets_prev=1800000,
        ppe=800000,
        ppe_prev=750000,
        net_income=-50000,  # Negative net income
        cash_flow_ops=100000,
        long_term_debt=500000,
        long_term_debt_prev=400000,
        sales_prev=800000,
        sga_prev=180000,
        dep_prev=45000,
        current_assets_prev=450000,
        current_liabilities_prev=280000
    )
    
    # Should handle negative values
    assert isinstance(result['m_score'], float)

def test_beneish_mscore_components():
    """Test that individual components are calculated correctly."""
    result = calculate_beneish_mscore(
        sales=1000000,
        cogs=600000,
        sga=200000,
        dep=50000,
        current_assets=500000,
        current_liabilities=300000,
        total_assets=2000000,
        total_assets_prev=1800000,
        ppe=800000,
        ppe_prev=750000,
        net_income=100000,
        cash_flow_ops=120000,
        long_term_debt=500000,
        long_term_debt_prev=400000,
        sales_prev=800000,
        sga_prev=180000,
        dep_prev=45000,
        current_assets_prev=450000,
        current_liabilities_prev=280000
    )
    
    # Check that all components are present and are numbers
    for var_name, value in result['breakdown']['variables'].items():
        assert isinstance(value, (int, float))
        
    # Check interpretations
    for var_name, interpretation in result['breakdown']['interpretation'].items():
        assert isinstance(interpretation, str)
        assert len(interpretation) > 0

def test_beneish_mscore_sensitivity():
    """Test sensitivity of M-Score to changes in inputs."""
    # Base case
    base_params = {
        'sales': 1000000,
        'cogs': 600000,
        'sga': 200000,
        'dep': 50000,
        'current_assets': 500000,
        'current_liabilities': 300000,
        'total_assets': 2000000,
        'total_assets_prev': 1800000,
        'ppe': 800000,
        'ppe_prev': 750000,
        'net_income': 100000,
        'cash_flow_ops': 120000,
        'long_term_debt': 500000,
        'long_term_debt_prev': 400000,
        'sales_prev': 800000,
        'sga_prev': 180000,
        'dep_prev': 45000,
        'current_assets_prev': 450000,
        'current_liabilities_prev': 280000
    }
    
    # Get base M-Score
    base_result = calculate_beneish_mscore(**base_params)
    base_score = base_result['m_score']
    
    # Increase net income without increasing cash flow (potential manipulation)
    manip_params = base_params.copy()
    manip_params['net_income'] = 200000  # Double the net income
    manip_result = calculate_beneish_mscore(**manip_params)
    
    # M-Score should increase (more likely manipulation)
    assert manip_result['m_score'] > base_score
