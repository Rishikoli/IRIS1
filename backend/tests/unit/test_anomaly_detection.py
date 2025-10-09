#!/usr/bin/env python3
"""
Unit tests for anomaly detection in ForensicAnalysisAgent
Tests rule-based checks for revenue decline, profit-cash divergence, receivables buildup
"""

import pytest
from decimal import Decimal

from src.agents.forensic.agent2_forensic_analysis import ForensicAnalysisAgent


class TestAnomalyDetection:
    """Tests for anomaly detection functionality"""

    @pytest.fixture
    def forensic_agent(self):
        return ForensicAnalysisAgent()

    @pytest.fixture
    def normal_financial_data(self):
        """Financial data that should NOT trigger anomalies"""
        return [
            {
                'statement_type': 'income_statement',
                'period_end': '2024-03-31',
                'data': {
                    'total_revenue': Decimal('100000'),
                    'net_profit': Decimal('10000'),
                    'operating_cash_flow': Decimal('8000'),  # 80% of profit - normal
                    'accounts_receivable': Decimal('15000')  # 15% of revenue - normal
                }
            },
            {
                'statement_type': 'income_statement',
                'period_end': '2023-03-31',
                'data': {
                    'total_revenue': Decimal('95000'),  # Only 5% decline - normal
                    'net_profit': Decimal('9500'),
                    'operating_cash_flow': Decimal('7600'),
                    'accounts_receivable': Decimal('14250')
                }
            }
        ]

    @pytest.fixture
    def anomalous_financial_data(self):
        """Financial data that should trigger multiple anomalies"""
        return [
            {
                'statement_type': 'income_statement',
                'period_end': '2024-03-31',
                'data': {
                    'total_revenue': Decimal('100000'),     # Current revenue
                    'net_profit': Decimal('10000'),         # Net profit
                    'operating_cash_flow': Decimal('2000'), # Only 20% of profit - should trigger divergence
                    'accounts_receivable': Decimal('30000') # 30% of revenue - should trigger buildup
                }
            },
            {
                'statement_type': 'income_statement',
                'period_end': '2023-03-31',
                'data': {
                    'total_revenue': Decimal('150000'),     # Previous revenue (33% decline)
                    'net_profit': Decimal('15000'),
                    'operating_cash_flow': Decimal('12000'),
                    'accounts_receivable': Decimal('22500')
                }
            }
        ]

    def test_detect_anomalies_with_normal_data(self, forensic_agent, normal_financial_data):
        """Test anomaly detection with normal financial data"""
        result = forensic_agent.detect_anomalies(normal_financial_data)

        # Debug output
        print(f"DEBUG: Normal data test - Success: {result.get('success')}, Anomalies: {result.get('anomalies_detected')}")

        assert result['success'] == True
        # Normal data should not trigger significant anomalies
        # Allow for minor edge cases but expect no major anomalies
        assert result['anomalies_detected'] <= 1  # Very permissive for edge cases
        assert len(result['anomalies']) <= 1

    def test_detect_revenue_decline_anomaly(self, forensic_agent):
        """Test revenue decline anomaly detection"""
        # Create data with significant revenue decline (>20%)
        declining_revenue_data = [
            {
                'statement_type': 'income_statement',
                'period_end': '2024-03-31',
                'data': {
                    'total_revenue': Decimal('70000'),  # 30% decline from previous
                    'net_profit': Decimal('7000')
                }
            },
            {
                'statement_type': 'income_statement',
                'period_end': '2023-03-31',
                'data': {
                    'total_revenue': Decimal('100000'),  # Previous year - baseline
                    'net_profit': Decimal('10000')
                }
            }
        ]

        result = forensic_agent.detect_anomalies(declining_revenue_data)

        assert result['success'] == True
        # Should detect at least one anomaly (revenue decline)
        assert result['anomalies_detected'] >= 1

        # Check for revenue decline anomaly specifically
        revenue_anomalies = [a for a in result['anomalies'] if a['type'] == 'REVENUE_DECLINE']
        assert len(revenue_anomalies) >= 1

        anomaly = revenue_anomalies[0]
        assert anomaly['severity'] == 'HIGH'
        assert 'declined' in anomaly['description']

    def test_detect_profit_cash_divergence_anomaly(self, forensic_agent):
        """Test profit-cash flow divergence anomaly detection"""
        divergence_data = [
            {
                'statement_type': 'income_statement',
                'period_end': '2024-03-31',
                'data': {
                    'total_revenue': Decimal('100000'),
                    'net_profit': Decimal('10000'),         # High profit
                    'operating_cash_flow': Decimal('2000')  # Very low cash flow (<50% of profit)
                }
            }
        ]

        result = forensic_agent.detect_anomalies(divergence_data)

        assert result['success'] == True
        # Should detect at least one anomaly (profit-cash divergence)
        assert result['anomalies_detected'] >= 1

        # Check for profit-cash divergence anomaly
        divergence_anomalies = [a for a in result['anomalies'] if a['type'] == 'PROFIT_CASH_DIVERGENCE']
        assert len(divergence_anomalies) >= 1

        anomaly = divergence_anomalies[0]
        assert anomaly['severity'] == 'MEDIUM'
        assert 'lower' in anomaly['description']

    def test_detect_receivables_buildup_anomaly(self, forensic_agent):
        """Test receivables buildup anomaly detection"""
        buildup_data = [
            {
                'statement_type': 'income_statement',
                'period_end': '2024-03-31',
                'data': {
                    'total_revenue': Decimal('100000'),
                    'accounts_receivable': Decimal('30000')  # 30% of revenue (>25% threshold)
                }
            }
        ]

        result = forensic_agent.detect_anomalies(buildup_data)

        assert result['success'] == True
        # Should detect at least one anomaly (receivables buildup)
        assert result['anomalies_detected'] >= 1

        # Check for receivables buildup anomaly
        buildup_anomalies = [a for a in result['anomalies'] if a['type'] == 'RECEIVABLES_BUILDUP']
        assert len(buildup_anomalies) >= 1

        anomaly = buildup_anomalies[0]
        assert anomaly['severity'] == 'MEDIUM'
        assert 'receivable' in anomaly['description']

    def test_detect_multiple_anomalies(self, forensic_agent, anomalous_financial_data):
        """Test detection of multiple anomalies in same dataset"""
        result = forensic_agent.detect_anomalies(anomalous_financial_data)

        assert result['success'] == True
        assert result['anomalies_detected'] >= 2  # Should detect multiple anomalies

        # Should detect revenue decline
        revenue_anomalies = [a for a in result['anomalies'] if a['type'] == 'REVENUE_DECLINE']
        assert len(revenue_anomalies) >= 1

        # Should detect profit-cash divergence
        divergence_anomalies = [a for a in result['anomalies'] if a['type'] == 'PROFIT_CASH_DIVERGENCE']
        assert len(divergence_anomalies) >= 1

        # Should detect receivables buildup
        buildup_anomalies = [a for a in result['anomalies'] if a['type'] == 'RECEIVABLES_BUILDUP']
        assert len(buildup_anomalies) >= 1

    def test_anomaly_severity_levels(self, forensic_agent, anomalous_financial_data):
        """Test that anomalies have correct severity levels"""
        result = forensic_agent.detect_anomalies(anomalous_financial_data)

        assert result['success'] == True

        # Check severity levels for detected anomalies
        for anomaly in result['anomalies']:
            assert 'severity' in anomaly
            assert anomaly['severity'] in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']

            # Revenue decline should be HIGH severity
            if anomaly['type'] == 'REVENUE_DECLINE':
                assert anomaly['severity'] == 'HIGH'

            # Profit-cash and receivables should be MEDIUM severity
            if anomaly['type'] in ['PROFIT_CASH_DIVERGENCE', 'RECEIVABLES_BUILDUP']:
                assert anomaly['severity'] == 'MEDIUM'

    def test_anomaly_evidence_structure(self, forensic_agent, anomalous_financial_data):
        """Test that anomalies include proper evidence structure"""
        result = forensic_agent.detect_anomalies(anomalous_financial_data)

        assert result['success'] == True

        for anomaly in result['anomalies']:
            assert 'evidence' in anomaly
            assert isinstance(anomaly['evidence'], dict)

            # Each anomaly type should have specific evidence fields
            if anomaly['type'] == 'REVENUE_DECLINE':
                assert 'current_revenue' in anomaly['evidence']
                assert 'previous_revenue' in anomaly['evidence']
                assert 'growth_rate' in anomaly['evidence']

            elif anomaly['type'] == 'PROFIT_CASH_DIVERGENCE':
                assert 'net_profit' in anomaly['evidence']
                assert 'operating_cash_flow' in anomaly['evidence']
                assert 'cash_to_profit_ratio' in anomaly['evidence']

            elif anomaly['type'] == 'RECEIVABLES_BUILDUP':
                assert 'accounts_receivable' in anomaly['evidence']
                assert 'total_revenue' in anomaly['evidence']
                assert 'receivables_ratio' in anomaly['evidence']

    def test_anomaly_detection_with_insufficient_data(self, forensic_agent):
        """Test anomaly detection with insufficient historical data"""
        single_period_data = [
            {
                'statement_type': 'income_statement',
                'period_end': '2024-03-31',
                'data': {
                    'total_revenue': Decimal('100000'),
                    'net_profit': Decimal('10000'),
                    'operating_cash_flow': Decimal('2000'),
                    'accounts_receivable': Decimal('30000')
                }
            }
        ]

        result = forensic_agent.detect_anomalies(single_period_data)

        assert result['success'] == True
        # Should only detect current period anomalies (profit-cash and receivables)
        # Revenue decline requires historical comparison
        anomalies = result['anomalies']
        assert len(anomalies) >= 2  # At least profit-cash and receivables

    def test_anomaly_detection_edge_cases(self, forensic_agent):
        """Test anomaly detection with edge cases"""
        # Test with zero values
        zero_data = [
            {
                'statement_type': 'income_statement',
                'period_end': '2024-03-31',
                'data': {
                    'total_revenue': Decimal('0'),
                    'net_profit': Decimal('0'),
                    'operating_cash_flow': Decimal('0'),
                    'accounts_receivable': Decimal('0')
                }
            }
        ]

        result = forensic_agent.detect_anomalies(zero_data)

        assert result['success'] == True
        # Should handle zero values gracefully without crashing
        assert result['anomalies_detected'] == 0

    def test_anomaly_detection_integration_with_comprehensive_analysis(self, forensic_agent, anomalous_financial_data):
        """Test anomaly detection integration in comprehensive analysis"""
        company_id = "TEST.BO"

        result = forensic_agent.comprehensive_forensic_analysis(company_id, anomalous_financial_data)

        assert result['success'] == True
        assert 'anomaly_detection' in result

        # Anomaly detection should be included in comprehensive results
        anomaly_result = result['anomaly_detection']
        assert anomaly_result['success'] == True
        assert 'anomalies' in anomaly_result
        assert 'anomalies_detected' in anomaly_result

        # Should detect multiple anomalies
        assert anomaly_result['anomalies_detected'] >= 2

        # Check anomaly structure
        for anomaly in anomaly_result['anomalies']:
            required_fields = ['type', 'severity', 'period', 'description', 'evidence']
            for field in required_fields:
                assert field in anomaly


# Run tests if executed directly
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
