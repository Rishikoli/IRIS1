"""Tests for Financial Ratios module."""
import pytest
from src.analysis.forensic.ratios import FinancialRatios, RatioCategory

def test_financial_ratios_initialization():
    """Test FinancialRatios class initialization."""
    ratios = FinancialRatios(currency='USD')
    assert ratios.currency == 'USD'
    
    # Default currency should be INR
    default_ratios = FinancialRatios()
    assert default_ratios.currency == 'INR'

def test_calculate_all_ratios():
    """Test calculation of all ratios."""
    ratios = FinancialRatios()
    
    # Sample financial data for a healthy company
    financials = {
        # Liquidity
        'current_assets': 150000,
        'current_liabilities': 100000,
        'inventory': 40000,
        'cash': 30000,
        'marketable_securities': 20000,
        
        # Profitability
        'net_income': 50000,
        'revenue': 1000000,
        'total_assets': 500000,
        'total_equity': 300000,
        'ebit': 75000,
        'interest_expense': 10000,
        'tax_expense': 15000,
        'ebitda': 90000,
        
        # Efficiency
        'cogs': 600000,
        'accounts_receivable': 50000,
        'accounts_payable': 40000,
        'fixed_assets': 350000,
        
        # Valuation
        'market_cap': 600000,
        'book_value': 300000,
        'eps': 5.0,
        'pe_ratio': 12.0,
        
        # Cash Flow
        'operating_cash_flow': 80000,
        'capital_expenditures': 20000,
        'total_debt': 200000
    }
    
    # Calculate all ratios
    all_ratios = ratios.calculate_all_ratios(financials)
    
    # Check that all categories are present
    assert set(all_ratios.keys()) == {
        RatioCategory.LIQUIDITY,
        RatioCategory.PROFITABILITY,
        RatioCategory.LEVERAGE,
        RatioCategory.EFFICIENCY,
        RatioCategory.VALUATION,
        RatioCategory.CASH_FLOW
    }
    
    # Check that each category has ratios
    for category, ratio_list in all_ratios.items():
        assert isinstance(ratio_list, list)
        assert len(ratio_list) > 0
        for ratio in ratio_list:
            assert 'name' in ratio
            assert 'value' in ratio
            assert 'formula' in ratio
            assert 'category' in ratio
            assert 'interpretation' in ratio

def test_liquidity_ratios():
    """Test liquidity ratio calculations."""
    ratios = FinancialRatios()
    
    # Calculate liquidity ratios
    liquidity_ratios = ratios.calculate_liquidity_ratios(
        current_assets=150000,
        current_liabilities=100000,
        inventory=40000,
        cash=30000,
        marketable_securities=20000
    )
    
    # Should return 3 ratios: current, quick, and cash
    assert len(liquidity_ratios) == 3
    
    # Check current ratio
    current_ratio = next(r for r in liquidity_ratios if r.name == "Current Ratio")
    assert abs(current_ratio.value - 1.5) < 0.01  # 150,000 / 100,000 = 1.5
    
    # Check quick ratio
    quick_ratio = next(r for r in liquidity_ratios if "Quick Ratio" in r.name)
    assert abs(quick_ratio.value - 1.1) < 0.01  # (150,000 - 40,000) / 100,000 = 1.1
    
    # Check cash ratio
    cash_ratio = next(r for r in liquidity_ratios if r.name == "Cash Ratio")
    assert abs(cash_ratio.value - 0.5) < 0.01  # (30,000 + 20,000) / 100,000 = 0.5

def test_profitability_ratios():
    """Test profitability ratio calculations."""
    ratios = FinancialRatios()
    
    # Calculate profitability ratios
    profitability_ratios = ratios.calculate_profitability_ratios(
        net_income=50000,
        revenue=1000000,
        total_assets=500000,
        total_equity=300000,
        ebit=75000,
        interest_expense=10000,
        tax_expense=15000
    )
    
    # Should return 4 ratios: net margin, roa, roe, ebit margin, interest coverage
    assert len(profitability_ratios) == 5
    
    # Check net margin
    net_margin = next(r for r in profitability_ratios if "Net Profit Margin" in r.name)
    assert abs(net_margin.value - 5.0) < 0.01  # (50,000 / 1,000,000) * 100 = 5.0%
    
    # Check ROA
    roa = next(r for r in profitability_ratios if "Return on Assets" in r.name)
    assert abs(roa.value - 10.0) < 0.01  # (50,000 / 500,000) * 100 = 10.0%
    
    # Check ROE
    roe = next(r for r in profitability_ratios if "Return on Equity" in r.name)
    assert abs(roe.value - 16.6667) < 0.1  # (50,000 / 300,000) * 100 ≈ 16.67%
    
    # Check EBIT margin
    ebit_margin = next(r for r in profitability_ratios if "EBIT Margin" in r.name)
    assert abs(ebit_margin.value - 7.5) < 0.01  # (75,000 / 1,000,000) * 100 = 7.5%
    
    # Check interest coverage
    interest_coverage = next(r for r in profitability_ratios if "Interest Coverage" in r.name)
    assert abs(interest_coverage.value - 7.5) < 0.01  # 75,000 / 10,000 = 7.5

def test_leverage_ratios():
    """Test leverage ratio calculations."""
    ratios = FinancialRatios()
    
    # Calculate leverage ratios
    leverage_ratios = ratios.calculate_leverage_ratios(
        total_debt=200000,
        total_equity=300000,
        total_assets=500000,
        ebitda=100000,
        interest_expense=10000
    )
    
    # Should return 3 ratios: debt-to-equity, debt-to-assets, debt-to-ebitda
    assert len(leverage_ratios) == 3
    
    # Check debt-to-equity
    d_e = next(r for r in leverage_ratios if "Debt-to-Equity" in r.name)
    assert abs(d_e.value - 0.6667) < 0.01  # 200,000 / 300,000 ≈ 0.6667
    
    # Check debt-to-assets
    d_a = next(r for r in leverage_ratios if "Debt-to-Assets" in r.name)
    assert abs(d_a.value - 0.4) < 0.01  # 200,000 / 500,000 = 0.4
    
    # Check debt-to-ebitda
    d_ebitda = next(r for r in leverage_ratios if "Debt-to-EBITDA" in r.name)
    assert abs(d_ebitda.value - 2.0) < 0.01  # 200,000 / 100,000 = 2.0

def test_efficiency_ratios():
    """Test efficiency ratio calculations."""
    ratios = FinancialRatios()
    
    # Calculate efficiency ratios
    efficiency_ratios = ratios.calculate_efficiency_ratios(
        revenue=1000000,
        cogs=600000,
        inventory=100000,
        accounts_receivable=50000,
        accounts_payable=40000,
        total_assets=500000,
        fixed_assets=300000
    )
    
    # Should return 4 ratios: inventory turnover, dso, asset turnover, fixed asset turnover
    assert len(efficiency_ratios) == 4
    
    # Check inventory turnover
    inv_turnover = next(r for r in efficiency_ratios if "Inventory Turnover" in r.name)
    assert abs(inv_turnover.value - 6.0) < 0.01  # 600,000 / 100,000 = 6.0
    
    # Check days sales outstanding
    dso = next(r for r in efficiency_ratios if "Days Sales Outstanding" in r.name)
    assert abs(dso.value - 18.25) < 0.1  # (50,000 / 1,000,000) * 365 ≈ 18.25
    
    # Check asset turnover
    asset_turnover = next(r for r in efficiency_ratios if "Asset Turnover" in r.name)
    assert abs(asset_turnover.value - 2.0) < 0.01  # 1,000,000 / 500,000 = 2.0
    
    # Check fixed asset turnover
    fixed_asset_turnover = next(r for r in efficiency_ratios if "Fixed Asset Turnover" in r.name)
    assert abs(fixed_asset_turnover.value - 3.3333) < 0.1  # 1,000,000 / 300,000 ≈ 3.333

def test_valuation_ratios():
    """Test valuation ratio calculations."""
    ratios = FinancialRatios()
    
    # Calculate valuation ratios
    valuation_ratios = ratios.calculate_valuation_ratios(
        market_cap=600000,
        revenue=1000000,
        net_income=100000,
        book_value=400000,
        eps=5.0,
        pe_ratio=12.0
    )
    
    # Should return 4 ratios: P/S, P/B, P/E, Earnings Yield
    assert len(valuation_ratios) == 4
    
    # Check price-to-sales
    ps_ratio = next(r for r in valuation_ratios if "Price-to-Sales" in r.name)
    assert abs(ps_ratio.value - 0.6) < 0.01  # 600,000 / 1,000,000 = 0.6
    
    # Check price-to-book
    pb_ratio = next(r for r in valuation_ratios if "Price-to-Book" in r.name)
    assert abs(pb_ratio.value - 1.5) < 0.01  # 600,000 / 400,000 = 1.5
    
    # Check P/E ratio (provided)
    pe_ratio = next(r for r in valuation_ratios if "Price-to-Earnings" in r.name)
    assert abs(pe_ratio.value - 12.0) < 0.01  # Provided as 12.0
    
    # Check earnings yield
    earnings_yield = next(r for r in valuation_ratios if "Earnings Yield" in r.name)
    assert abs(earnings_yield.value - 8.3333) < 0.1  # (1 / 12) * 100 ≈ 8.33%

def test_cash_flow_ratios():
    """Test cash flow ratio calculations."""
    ratios = FinancialRatios()
    
    # Calculate cash flow ratios
    cash_flow_ratios = ratios.calculate_cash_flow_ratios(
        operating_cash_flow=120000,
        capital_expenditures=40000,
        current_liabilities=100000,
        total_debt=200000,
        revenue=1000000
    )
    
    # Should return 4 ratios: FCF, OCF ratio, CF to debt, OCF margin
    assert len(cash_flow_ratios) == 4
    
    # Check free cash flow
    fcf = next(r for r in cash_flow_ratios if "Free Cash Flow" in r.name)
    assert abs(fcf.value - 80000) < 0.01  # 120,000 - 40,000 = 80,000
    
    # Check operating cash flow ratio
    ocf_ratio = next(r for r in cash_flow_ratios if "Operating Cash Flow Ratio" in r.name)
    assert abs(ocf_ratio.value - 1.2) < 0.01  # 120,000 / 100,000 = 1.2
    
    # Check cash flow to debt ratio
    cf_debt = next(r for r in cash_flow_ratios if "Cash Flow to Debt Ratio" in r.name)
    assert abs(cf_debt.value - 0.6) < 0.01  # 120,000 / 200,000 = 0.6
    
    # Check operating cash flow margin
    ocf_margin = next(r for r in cash_flow_ratios if "Operating Cash Flow Margin" in r.name)
    assert abs(ocf_margin.value - 12.0) < 0.01  # (120,000 / 1,000,000) * 100 = 12.0%
