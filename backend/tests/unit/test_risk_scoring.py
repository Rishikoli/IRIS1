
import pytest
from decimal import Decimal
from unittest.mock import Mock, patch

from src.agents.forensic.agent3_risk_scoring import RiskScoringAgent


class TestRiskScoringAgent:
    """Comprehensive tests for Risk Scoring Agent"""

    @pytest.fixture
    def risk_agent(self):
        return RiskScoringAgent()

    @pytest.fixture
    def sample_forensic_results(self):
        """Sample forensic analysis results for testing"""
        return {
            'altman_z_score': {
                'success': True,
                'altman_z_score': {
                    'z_score': 2.5,
                    'classification': 'GREY',
                    'risk_level': 'MEDIUM'
                }
            },
            'financial_ratios': {
                '2024-03-31': {
                    'current_ratio': 1.5,
                    'net_margin_pct': 8.0,
                    'roe': 12.0,
                    'debt_to_equity': 0.5,
                    'interest_coverage': 6.0,
                    'asset_turnover': 1.2,
                    'receivables_turnover': 10.0,
                    'inventory_turnover': 6.0
                }
            },
            'beneish_m_score': {
                'success': True,
                'beneish_m_score': {
                    'm_score': -2.0,
                    'risk_level': 'LOW'
                }
            },
            'benford_analysis': {
                'success': True,
                'benford_analysis': {
                    'chi_square_statistic': 12.5,
                    'interpretation': 'Normal distribution'
                }
            },
            'anomaly_detection': {
                'success': True,
                'anomalies_detected': 2,
                'anomalies': [
                    {'type': 'revenue_decline', 'severity': 'MEDIUM'},
                    {'type': 'receivables_buildup', 'severity': 'LOW'}
                ]
            }
        }

    def test_score_financial_health_safe_company(self, risk_agent, sample_forensic_results):
        """Test financial health scoring for a safe company"""
        # Modify for SAFE Z-Score
        sample_forensic_results['altman_z_score']['altman_z_score']['z_score'] = 3.5
        sample_forensic_results['financial_ratios']['2024-03-31']['current_ratio'] = 2.5
        sample_forensic_results['financial_ratios']['2024-03-31']['net_margin_pct'] = 15.0
        sample_forensic_results['financial_ratios']['2024-03-31']['roe'] = 20.0
        
        result = risk_agent.score_financial_health(sample_forensic_results)
        
        assert result['success'] == True
        assert result['financial_health_score'] < 25  # Should be low risk
        assert 'z_score_risk' in result['components']
        assert 'liquidity_risk' in result['components']
        assert 'profitability_risk' in result['components']

    def test_score_financial_health_distressed_company(self, risk_agent, sample_forensic_results):
        """Test financial health scoring for a distressed company"""
        # Modify for DISTRESS Z-Score
        sample_forensic_results['altman_z_score']['altman_z_score']['z_score'] = 1.0
        sample_forensic_results['financial_ratios']['2024-03-31']['current_ratio'] = 0.8
        sample_forensic_results['financial_ratios']['2024-03-31']['net_margin_pct'] = -5.0
        sample_forensic_results['financial_ratios']['2024-03-31']['roe'] = -10.0
        
        result = risk_agent.score_financial_health(sample_forensic_results)
        
        assert result['success'] == True
        assert result['financial_health_score'] > 75  # Should be high risk
        assert result['components']['z_score_risk'] == 70  # DISTRESS zone

    def test_score_earnings_quality_low_risk(self, risk_agent, sample_forensic_results):
        """Test earnings quality scoring for low manipulation risk"""
        # Modify for low M-Score
        sample_forensic_results['beneish_m_score']['beneish_m_score']['m_score'] = -2.5
        sample_forensic_results['financial_ratios']['2024-03-31']['net_margin_pct'] = 18.0
        sample_forensic_results['benford_analysis']['benford_analysis']['chi_square_statistic'] = 8.0
        
        result = risk_agent.score_earnings_quality(sample_forensic_results)
        
        assert result['success'] == True
        assert result['earnings_quality_score'] < 25  # Should be low risk
        assert result['components']['manipulation_risk'] == 0  # Very low M-Score

    def test_score_earnings_quality_high_risk(self, risk_agent, sample_forensic_results):
        """Test earnings quality scoring for high manipulation risk"""
        # Modify for high M-Score
        sample_forensic_results['beneish_m_score']['beneish_m_score']['m_score'] = -0.5
        sample_forensic_results['financial_ratios']['2024-03-31']['net_margin_pct'] = -2.0
        sample_forensic_results['benford_analysis']['benford_analysis']['chi_square_statistic'] = 20.0
        
        result = risk_agent.score_earnings_quality(sample_forensic_results)
        
        assert result['success'] == True
        assert result['earnings_quality_score'] > 75  # Should be high risk
        assert result['components']['manipulation_risk'] == 90  # High M-Score

    def test_score_leverage_risk_conservative(self, risk_agent, sample_forensic_results):
        """Test leverage risk scoring for conservative company"""
        sample_forensic_results['financial_ratios']['2024-03-31']['debt_to_equity'] = 0.2
        sample_forensic_results['financial_ratios']['2024-03-31']['interest_coverage'] = 15.0
        
        result = risk_agent.score_leverage_risk(sample_forensic_results)
        
        assert result['success'] == True
        assert result['leverage_risk_score'] < 25  # Should be low risk
        assert result['components']['debt_to_equity_risk'] == 0
        assert result['components']['interest_coverage_risk'] == 0

    def test_score_leverage_risk_excessive(self, risk_agent, sample_forensic_results):
        """Test leverage risk scoring for highly leveraged company"""
        sample_forensic_results['financial_ratios']['2024-03-31']['debt_to_equity'] = 2.0
        sample_forensic_results['financial_ratios']['2024-03-31']['interest_coverage'] = 1.5
        
        result = risk_agent.score_leverage_risk(sample_forensic_results)
        
        assert result['success'] == True
        assert result['leverage_risk_score'] > 75  # Should be high risk
        assert result['components']['debt_to_equity_risk'] == 90
        assert result['components']['interest_coverage_risk'] == 85

    def test_score_operational_efficiency_excellent(self, risk_agent, sample_forensic_results):
        """Test operational efficiency scoring for excellent company"""
        sample_forensic_results['financial_ratios']['2024-03-31']['asset_turnover'] = 2.0
        sample_forensic_results['financial_ratios']['2024-03-31']['receivables_turnover'] = 15.0
        sample_forensic_results['financial_ratios']['2024-03-31']['inventory_turnover'] = 10.0
        
        result = risk_agent.score_operational_efficiency(sample_forensic_results)
        
        assert result['success'] == True
        assert result['operational_efficiency_score'] < 25  # Should be low risk
        assert result['components']['asset_efficiency'] == 0
        assert result['components']['receivables_efficiency'] == 0

    def test_score_anomaly_severity_no_anomalies(self, risk_agent, sample_forensic_results):
        """Test anomaly severity scoring with no anomalies"""
        sample_forensic_results['anomaly_detection']['anomalies_detected'] = 0
        sample_forensic_results['anomaly_detection']['anomalies'] = []
        
        result = risk_agent.score_anomaly_severity(sample_forensic_results)
        
        assert result['success'] == True
        assert result['anomaly_severity_score'] == 0  # No anomalies = no risk
        assert result['components']['anomaly_count_risk'] == 0

    def test_score_anomaly_severity_critical_anomalies(self, risk_agent, sample_forensic_results):
        """Test anomaly severity scoring with critical anomalies"""
        sample_forensic_results['anomaly_detection']['anomalies_detected'] = 6
        sample_forensic_results['anomaly_detection']['anomalies'] = [
            {'type': 'revenue_manipulation', 'severity': 'CRITICAL'},
            {'type': 'cash_flow_divergence', 'severity': 'CRITICAL'},
            {'type': 'receivables_buildup', 'severity': 'HIGH'},
            {'type': 'inventory_buildup', 'severity': 'HIGH'},
            {'type': 'expense_timing', 'severity': 'MEDIUM'},
            {'type': 'related_party', 'severity': 'MEDIUM'}
        ]
        
        result = risk_agent.score_anomaly_severity(sample_forensic_results)
        
        assert result['success'] == True
        assert result['anomaly_severity_score'] > 90  # Should be very high risk
        assert result['components']['severity_adjustment'] == 1.5  # Critical multiplier

    def test_calculate_risk_score_low_risk_company(self, risk_agent):
        """Test composite risk score for low-risk company"""
        # Create low-risk forensic results
        low_risk_results = {
            'altman_z_score': {
                'success': True,
                'altman_z_score': {'z_score': 3.5, 'classification': 'SAFE'}
            },
            'financial_ratios': {
                '2024-03-31': {
                    'current_ratio': 2.5, 'net_margin_pct': 15.0, 'roe': 20.0,
                    'debt_to_equity': 0.2, 'interest_coverage': 15.0,
                    'asset_turnover': 2.0, 'receivables_turnover': 15.0, 'inventory_turnover': 10.0
                }
            },
            'beneish_m_score': {
                'success': True,
                'beneish_m_score': {'m_score': -2.5, 'risk_level': 'LOW'}
            },
            'benford_analysis': {
                'success': True,
                'benford_analysis': {'chi_square_statistic': 8.0}
            },
            'anomaly_detection': {
                'success': True,
                'anomalies_detected': 0,
                'anomalies': []
            }
        }
        
        result = risk_agent.calculate_risk_score('LOW_RISK_COMPANY', low_risk_results)
        
        assert result['success'] == True
        assert result['composite_risk_score'] < 25  # Should be low risk
        assert result['risk_classification']['level'] == 'LOW'
        assert len(result['category_scores']) == 6  # All 6 categories

    def test_calculate_risk_score_high_risk_company(self, risk_agent):
        """Test composite risk score for high-risk company"""
        # Create high-risk forensic results
        high_risk_results = {
            'altman_z_score': {
                'success': True,
                'altman_z_score': {'z_score': 1.0, 'classification': 'DISTRESS'}
            },
            'financial_ratios': {
                '2024-03-31': {
                    'current_ratio': 0.8, 'net_margin_pct': -5.0, 'roe': -10.0,
                    'debt_to_equity': 2.0, 'interest_coverage': 1.5,
                    'asset_turnover': 0.3, 'receivables_turnover': 3.0, 'inventory_turnover': 1.5
                }
            },
            'beneish_m_score': {
                'success': True,
                'beneish_m_score': {'m_score': -0.5, 'risk_level': 'HIGH'}
            },
            'benford_analysis': {
                'success': True,
                'benford_analysis': {'chi_square_statistic': 20.0}
            },
            'anomaly_detection': {
                'success': True,
                'anomalies_detected': 8,
                'anomalies': [{'type': 'critical_issue', 'severity': 'CRITICAL'}] * 8
            }
        }
        
        result = risk_agent.calculate_risk_score('HIGH_RISK_COMPANY', high_risk_results)
        
        assert result['success'] == True
        assert result['composite_risk_score'] > 75  # Should be high risk
        assert result['risk_classification']['level'] == 'CRITICAL'

    def test_classify_risk_boundaries(self, risk_agent):
        """Test risk classification boundary conditions"""
        # Test LOW boundary
        low_classification = risk_agent.classify_risk(20.0)
        assert low_classification['level'] == 'LOW'
        
        # Test MEDIUM boundary
        medium_classification = risk_agent.classify_risk(35.0)
        assert medium_classification['level'] == 'MEDIUM'
        
        # Test HIGH boundary
        high_classification = risk_agent.classify_risk(60.0)
        assert high_classification['level'] == 'HIGH'
        
        # Test CRITICAL boundary
        critical_classification = risk_agent.classify_risk(80.0)
        assert critical_classification['level'] == 'CRITICAL'

    def test_comprehensive_risk_assessment(self, risk_agent, sample_forensic_results):
        """Test comprehensive risk assessment with detailed analysis"""
        result = risk_agent.comprehensive_risk_assessment('TEST_COMPANY', sample_forensic_results)
        
        assert result['success'] == True
        assert 'composite_risk_score' in result
        assert 'risk_classification' in result
        assert 'category_scores' in result
        assert 'detailed_analysis' in result
        
        # Check detailed analysis contains all categories
        detailed = result['detailed_analysis']
        expected_categories = [
            'financial_health', 'earnings_quality', 'leverage_risk',
            'operational_efficiency', 'anomaly_severity', 'disclosure_quality'
        ]
        
        for category in expected_categories:
            assert category in detailed
            assert detailed[category]['success'] == True

    def test_category_weights_sum_to_one(self, risk_agent):
        """Test that category weights sum to 1.0"""
        total_weight = sum(risk_agent.category_weights.values())
        assert abs(total_weight - 1.0) < 0.001  # Allow for floating point precision

    def test_error_handling_missing_data(self, risk_agent):
        """Test error handling with missing forensic data"""
        incomplete_results = {
            'altman_z_score': {'success': False, 'error': 'Missing data'}
        }
        
        result = risk_agent.score_financial_health(incomplete_results)
        # Should handle gracefully and return partial score
        assert result['success'] == True

# Run tests if executed directly
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
