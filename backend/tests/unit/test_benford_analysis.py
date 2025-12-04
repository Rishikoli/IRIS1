#!/usr/bin/env python3
"""
Unit tests for Benford's Law analysis in ForensicAnalysisAgent
Tests anomaly detection with manipulated data (uniform distribution)
"""

import pytest
import numpy as np
from decimal import Decimal

from src.agents.forensic.agent2_forensic_analysis import ForensicAnalysisAgent


class TestBenfordAnalysis:
    """Tests for Benford's Law analysis functionality"""

    @pytest.fixture
    def forensic_agent(self):
        return ForensicAnalysisAgent()

    @pytest.fixture
    def normal_financial_data(self):
        """Financial data that should follow Benford's Law"""
        return [
            {
                'statement_type': 'income_statement',
                'period_end': '2024-03-31',
                'data': {
                    'total_revenue': Decimal('1000000'),      # 1
                    'cost_of_revenue': Decimal('650000'),    # 6
                    'gross_profit': Decimal('350000'),       # 3
                    'operating_income': Decimal('200000'),   # 2
                    'net_profit': Decimal('150000'),         # 1
                    'interest_expense': Decimal('25000'),    # 2
                    'tax_expense': Decimal('30000')          # 3
                }
            },
            {
                'statement_type': 'balance_sheet',
                'period_end': '2024-03-31',
                'data': {
                    'total_assets': Decimal('2000000'),      # 2
                    'current_assets': Decimal('800000'),     # 8
                    'current_liabilities': Decimal('500000'), # 5
                    'total_equity': Decimal('1200000'),      # 1
                    'total_liabilities': Decimal('800000'),  # 8
                    'accounts_receivable': Decimal('300000'), # 3
                    'inventory': Decimal('400000'),          # 4
                    'cash_and_equivalents': Decimal('100000') # 1
                }
            }
        ]

    @pytest.fixture
    def manipulated_financial_data(self):
        """Manipulated data with uniform distribution (should trigger anomaly)"""
        return [
            {
                'statement_type': 'income_statement',
                'period_end': '2024-03-31',
                'data': {
                    'total_revenue': Decimal('500000'),      # 5
                    'cost_of_revenue': Decimal('600000'),    # 6
                    'gross_profit': Decimal('700000'),       # 7
                    'operating_income': Decimal('800000'),   # 8
                    'net_profit': Decimal('900000'),         # 9
                    'interest_expense': Decimal('550000'),   # 5
                    'tax_expense': Decimal('660000')         # 6
                }
            },
            {
                'statement_type': 'balance_sheet',
                'period_end': '2024-03-31',
                'data': {
                    'total_assets': Decimal('200000'),       # 2
                    'current_assets': Decimal('300000'),     # 3
                    'current_liabilities': Decimal('400000'), # 4
                    'total_equity': Decimal('500000'),       # 5
                    'total_liabilities': Decimal('600000'),  # 6
                    'accounts_receivable': Decimal('700000'), # 7
                    'inventory': Decimal('800000'),          # 8
                    'cash_and_equivalents': Decimal('900000') # 9
                }
            }
        ]

    def test_benford_analysis_with_normal_data(self, forensic_agent, normal_financial_data):
        """Test Benford's Law analysis with normal financial data"""
        result = forensic_agent.benford_analysis(normal_financial_data)

        assert result['success'] == True
        benford = result['benford_analysis']

        # Should analyze sufficient data points
        assert benford['total_numbers_analyzed'] >= 15

        # Should have expected structure
        assert 'observed_frequencies' in benford
        assert 'expected_frequencies' in benford
        assert 'chi_square_statistic' in benford
        assert 'critical_value' in benford
        assert 'is_anomalous' in benford

        # Critical value should be 15.507 for 95% confidence
        assert abs(benford['critical_value'] - 15.507) < 0.01

        # Should have 9 observed and expected frequencies (digits 1-9)
        assert len(benford['observed_frequencies']) == 9
        assert len(benford['expected_frequencies']) == 9

        # Expected frequencies should match Benford's Law
        expected_benford = [30.1, 17.6, 12.5, 9.7, 7.9, 6.7, 5.8, 5.1, 4.6]
        for i, expected in enumerate(expected_benford):
            assert abs(benford['expected_frequencies'][i] - expected) < 0.1

    def test_benford_analysis_with_manipulated_data(self, forensic_agent, manipulated_financial_data):
        """Test Benford's Law anomaly detection with manipulated data"""
        result = forensic_agent.benford_analysis(manipulated_financial_data)

        assert result['success'] == True
        benford = result['benford_analysis']

        # Should detect anomaly (uniform distribution doesn't follow Benford's Law)
        assert benford['is_anomalous'] == True
        assert benford['interpretation'] == "ANOMALOUS"

        # Chi-square should exceed critical value
        assert benford['chi_square_statistic'] > benford['critical_value']

    def test_benford_analysis_insufficient_data(self, forensic_agent):
        """Test Benford's Law with insufficient data points"""
        insufficient_data = [
            {
                'statement_type': 'income_statement',
                'data': {
                    'total_revenue': Decimal('1000'),
                    'net_profit': Decimal('100')
                }
            }
        ]

        result = forensic_agent.benford_analysis(insufficient_data)

        assert result['success'] == False
        assert 'Insufficient data points' in result['error']
        assert 'minimum 10' in result['error']

    def test_benford_analysis_first_digit_extraction(self, forensic_agent):
        """Test that first digits are correctly extracted"""
        test_data = [
            {
                'statement_type': 'income_statement',
                'data': {
                    'total_revenue': Decimal('123456'),    # First digit: 1
                    'cost_of_revenue': Decimal('234567'),  # First digit: 2
                    'gross_profit': Decimal('345678'),     # First digit: 3
                    'operating_income': Decimal('456789'), # First digit: 4
                    'net_profit': Decimal('567890'),       # First digit: 5
                    'interest_expense': Decimal('678901'), # First digit: 6
                    'tax_expense': Decimal('789012'),      # First digit: 7
                    'other_income': Decimal('890123'),     # First digit: 8
                    'extra_expense': Decimal('901234')     # First digit: 9
                }
            }
        ]

        result = forensic_agent.benford_analysis(test_data)
        assert result['success'] == True

        benford = result['benford_analysis']
        observed = benford['observed_frequencies']

        # Should analyze all 9 numbers
        assert benford['total_numbers_analyzed'] == 9

        # Each number should contribute to exactly one digit count
        total_observed = sum(observed)
        assert abs(total_observed - 100.0) < 0.1  # Should be 100% total

        # Check that we have exactly one observation for each digit 1-9
        for i, freq in enumerate(observed):
            assert freq == 100.0 / 9  # Each digit should have equal frequency (11.11%)

    def test_benford_analysis_edge_cases(self, forensic_agent):
        """Test Benford's Law with edge cases"""
        # Test with zero values (should be ignored)
        edge_case_data = [
            {
                'statement_type': 'income_statement',
                'data': {
                    'total_revenue': Decimal('100000'),   # First digit: 1
                    'cost_of_revenue': Decimal('0'),     # Zero value - should be ignored
                    'gross_profit': Decimal('50000'),     # First digit: 5
                    'net_profit': Decimal('10000')        # First digit: 1
                }
            }
        ]

        result = forensic_agent.benford_analysis(edge_case_data)
        assert result['success'] == True

        # Should analyze 3 positive non-zero values (ignoring the zero)
        benford = result['benford_analysis']
        assert benford['total_numbers_analyzed'] == 3

        # Check that zero values are properly ignored
        observed = benford['observed_frequencies']
        # Digit 1 should appear twice (100000 and 10000), digit 5 should appear once (50000)
        assert observed[0] == 200.0 / 3  # 66.67% for digit 1
        assert observed[4] == 100.0 / 3  # 33.33% for digit 5

    def test_benford_analysis_chi_square_calculation(self, forensic_agent):
        """Test chi-square calculation accuracy"""
        # Create data with digits that deviate significantly from Benford's Law
        # This should produce a high chi-square value and be flagged as anomalous
        manipulated_data = [
            {
                'statement_type': 'income_statement',
                'data': {
                    'total_revenue': Decimal('800000'),    # 8 - should be rare in Benford's Law
                    'cost_of_revenue': Decimal('900000'),  # 9 - should be rare in Benford's Law
                    'gross_profit': Decimal('700000'),     # 7 - should be rare in Benford's Law
                    'operating_income': Decimal('600000'), # 6 - should be rare in Benford's Law
                    'net_profit': Decimal('500000'),       # 5 - should be rare in Benford's Law
                    'interest_expense': Decimal('400000'), # 4 - should be rare in Benford's Law
                    'tax_expense': Decimal('300000'),      # 3 - should be rare in Benford's Law
                    'other_income': Decimal('200000'),     # 2 - should be rare in Benford's Law
                    'extra_expense': Decimal('100000')     # 1 - should be common in Benford's Law
                }
            }
        ]

        result = forensic_agent.benford_analysis(manipulated_data)
        assert result['success'] == True

        benford = result['benford_analysis']

        # Chi-square should be calculated correctly
        assert benford['chi_square_statistic'] > 0
        assert benford['critical_value'] == 15.507

        # This data should be flagged as anomalous due to deviation from Benford's Law
        # The high digits (7,8,9) are much more frequent than expected
        assert benford['is_anomalous'] == True
        assert benford['interpretation'] == "ANOMALOUS"

        # Chi-square should be significantly above the critical value
        assert benford['chi_square_statistic'] > 20  # Much higher than 15.507

    def test_benford_analysis_integration_with_comprehensive_analysis(self, forensic_agent, normal_financial_data):
        """Test Benford's Law integration in comprehensive analysis"""
        company_id = "TEST.BO"

        result = forensic_agent.comprehensive_forensic_analysis(company_id, normal_financial_data)

        assert result['success'] == True
        assert 'benford_analysis' in result

        # Benford's Law should be included in comprehensive results
        benford_result = result['benford_analysis']
        assert benford_result['success'] == True
        assert 'benford_analysis' in benford_result

        # Should have all required fields
        benford = benford_result['benford_analysis']
        required_fields = [
            'total_numbers_analyzed', 'observed_frequencies',
            'expected_frequencies', 'chi_square_statistic',
            'critical_value', 'is_anomalous', 'interpretation'
        ]

        for field in required_fields:
            assert field in benford


# Run tests if executed directly
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
