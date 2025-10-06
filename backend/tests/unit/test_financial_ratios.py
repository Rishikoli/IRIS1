
import pytest
from decimal import Decimal

from src.agents.forensic.agent2_forensic_analysis import ForensicAnalysisAgent


class TestFinancialRatios:
    """Comprehensive tests for financial ratio calculations"""

    @pytest.fixture
    def forensic_agent(self):
        return ForensicAnalysisAgent()

    @pytest.fixture
    def sample_financial_data(self):
        """Sample financial data for testing"""
        return [
            {
                'statement_type': 'balance_sheet',
                'period_end': '2024-03-31',
                'data': {
                    'total_assets': Decimal('100000'),
                    'current_assets': Decimal('30000'),
                    'current_liabilities': Decimal('20000'),
                    'total_equity': Decimal('60000'),
                    'total_liabilities': Decimal('40000'),
                    'accounts_receivable': Decimal('8000'),
                    'inventory': Decimal('12000'),
                    'cash_and_equivalents': Decimal('10000'),
                    'property_plant_equipment': Decimal('50000')
                }
            },
            {
                'statement_type': 'income_statement',
                'period_end': '2024-03-31',
                'data': {
                    'total_revenue': Decimal('50000'),
                    'gross_profit': Decimal('30000'),
                    'operating_income': Decimal('15000'),
                    'net_profit': Decimal('10000'),
                    'interest_expense': Decimal('2000'),
                    'cost_of_goods_sold': Decimal('20000')
                }
            }
        ]

    def test_calculate_liquidity_ratios(self, forensic_agent, sample_financial_data):
        """Test liquidity ratio calculations"""
        result = forensic_agent.calculate_financial_ratios(sample_financial_data)
        
        assert result['success'] == True
        ratios = result['financial_ratios']['2024-03-31']
        
        # Current Ratio: 30000/20000 = 1.5
        assert 'current_ratio' in ratios
        assert ratios['current_ratio'] == 1.5
        
        # Quick Ratio: (30000 - 12000)/20000 = 0.9
        assert 'quick_ratio' in ratios
        assert ratios['quick_ratio'] == 0.9
        
        # Cash Ratio: 10000/20000 = 0.5
        assert 'cash_ratio' in ratios
        assert ratios['cash_ratio'] == 0.5

    def test_calculate_profitability_ratios(self, forensic_agent, sample_financial_data):
        """Test profitability ratio calculations"""
        result = forensic_agent.calculate_financial_ratios(sample_financial_data)
        
        assert result['success'] == True
        ratios = result['financial_ratios']['2024-03-31']
        
        # Gross Margin: 30000/50000 * 100 = 60%
        assert 'gross_margin_pct' in ratios
        assert ratios['gross_margin_pct'] == 60.0
        
        # Net Margin: 10000/50000 * 100 = 20%
        assert 'net_margin_pct' in ratios
        assert ratios['net_margin_pct'] == 20.0
        
        # ROE: 10000/60000 * 100 ≈ 16.67%
        assert 'roe' in ratios
        assert abs(ratios['roe'] - 16.67) < 0.01
        
        # ROA: 10000/100000 * 100 = 10%
        assert 'roa' in ratios
        assert ratios['roa'] == 10.0

    def test_calculate_leverage_ratios(self, forensic_agent, sample_financial_data):
        """Test leverage ratio calculations"""
        result = forensic_agent.calculate_financial_ratios(sample_financial_data)
        
        assert result['success'] == True
        ratios = result['financial_ratios']['2024-03-31']
        
        # Debt-to-Equity: 40000/60000 ≈ 0.67
        assert 'debt_to_equity' in ratios
        assert abs(ratios['debt_to_equity'] - 0.67) < 0.01
        
        # Debt-to-Assets: 40000/100000 = 0.4
        assert 'debt_to_assets' in ratios
        assert ratios['debt_to_assets'] == 0.4
        
        # Interest Coverage: 15000/2000 = 7.5
        assert 'interest_coverage' in ratios
        assert ratios['interest_coverage'] == 7.5

    def test_calculate_efficiency_ratios(self, forensic_agent, sample_financial_data):
        """Test efficiency ratio calculations"""
        result = forensic_agent.calculate_financial_ratios(sample_financial_data)
        
        assert result['success'] == True
        ratios = result['financial_ratios']['2024-03-31']
        
        # Asset Turnover: 50000/100000 = 0.5
        assert 'asset_turnover' in ratios
        assert ratios['asset_turnover'] == 0.5
        
        # Receivables Turnover: 50000/8000 = 6.25
        assert 'receivables_turnover' in ratios
        assert ratios['receivables_turnover'] == 6.25
        
        # Inventory Turnover: 20000/12000 ≈ 1.67
        assert 'inventory_turnover' in ratios
        assert abs(ratios['inventory_turnover'] - 1.67) < 0.01
        
        # Days Sales Outstanding: (8000/50000) * 365 ≈ 58.4
        assert 'days_sales_outstanding' in ratios
        assert abs(ratios['days_sales_outstanding'] - 58.4) < 0.1

    def test_comprehensive_ratio_coverage(self, forensic_agent, sample_financial_data):
        """Test that all required ratios are calculated"""
        result = forensic_agent.calculate_financial_ratios(sample_financial_data)
        
        assert result['success'] == True
        ratios = result['financial_ratios']['2024-03-31']
        
        # Check for all required ratio categories
        required_ratios = [
            # Liquidity
            'current_ratio', 'quick_ratio', 'cash_ratio',
            # Profitability
            'gross_margin_pct', 'net_margin_pct', 'roe', 'roa',
            # Leverage
            'debt_to_equity', 'debt_to_assets', 'interest_coverage',
            # Efficiency
            'asset_turnover', 'receivables_turnover', 'inventory_turnover'
        ]
        
        found_ratios = [ratio for ratio in required_ratios if ratio in ratios]
        print(f"✅ Ratios implemented: {len(found_ratios)}/{len(required_ratios)}")
        
        for ratio in found_ratios:
            assert ratio in ratios
            assert isinstance(ratios[ratio], (int, float))
            assert not isinstance(ratios[ratio], str)  # Should be numeric
        
        # Should have at least 12 ratios
        assert len(found_ratios) >= 12

    def test_ratio_calculation_with_edge_cases(self, forensic_agent):
        """Test ratio calculations with edge cases"""
        # Zero values
        zero_data = [
            {
                'statement_type': 'balance_sheet',
                'data': {
                    'total_assets': 0,
                    'current_assets': 0,
                    'current_liabilities': 0,
                    'total_equity': 0
                }
            },
            {
                'statement_type': 'income_statement',
                'data': {
                    'total_revenue': 0,
                    'net_profit': 0
                }
            }
        ]
        
        result = forensic_agent.calculate_financial_ratios(zero_data)
        # Should handle gracefully without crashing
        assert result['success'] == True or 'error' in result

    def test_ratio_accuracy_with_known_data(self, forensic_agent):
        """Test ratio accuracy with known financial data"""
        # Apple-like financials for verification
        apple_like_data = [
            {
                'statement_type': 'balance_sheet',
                'data': {
                    'total_assets': Decimal('352755000000'),  # B
                    'current_assets': Decimal('143566000000'),
                    'current_liabilities': Decimal('105392000000'),
                    'total_equity': Decimal('63090000000'),
                    'total_liabilities': Decimal('289665000000')
                }
            },
            {
                'statement_type': 'income_statement',
                'data': {
                    'total_revenue': Decimal('394328000000'),  # B
                    'net_profit': Decimal('96995000000')      # B
                }
            }
        ]
        
        result = forensic_agent.calculate_financial_ratios(apple_like_data)
        assert result['success'] == True
        
        ratios = result['financial_ratios']
        if ratios:
            period_ratios = list(ratios.values())[0]
            
            # Current Ratio ≈ 1.36
            assert abs(period_ratios.get('current_ratio', 0) - 1.36) < 0.01
            
            # ROE ≈ 153.7%
            assert abs(period_ratios.get('roe', 0) - 153.7) < 1
            
            # ROA ≈ 27.5%
            assert abs(period_ratios.get('roa', 0) - 27.5) < 0.1

# Run tests if executed directly
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
