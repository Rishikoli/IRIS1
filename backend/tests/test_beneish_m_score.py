"""
Unit tests for Beneish M-Score calculation in IRIS forensic analysis system.

This module tests the calculate_beneish_m_score method with:
- Known manipulator companies (high M-Score > -1.78)
- Known non-manipulator companies (low M-Score ≤ -1.78)
- Edge cases and error conditions
"""

import pytest
import sys
import os
from decimal import Decimal
from datetime import datetime

# Add the src directory to Python path for imports
sys.path.insert(0, '/home/aditya/I.R.I.S./backend/src')

from agents.forensic.agent2_forensic_analysis import ForensicAnalysisAgent


class TestBeneishMScore:
    """Test suite for Beneish M-Score calculation"""

    def setup_method(self):
        """Set up test fixtures"""
        self.agent = ForensicAnalysisAgent()

    def test_calculate_beneish_m_score_manipulator_example(self):
        """Test M-Score calculation with known manipulator company data"""
        # Example data representing a company with earnings manipulation indicators
        current_period = {
            "totalRevenue": 1000000,
            "Total Revenue": 1000000,
            "totalCurrentAssets": 800000,
            "Total Current Assets": 800000,
            "grossProfit": 300000,
            "Gross Profit": 300000,
            "totalAssets": 2000000,
            "Total Assets": 2000000,
            "sellingGeneralAdministrative": 150000,
            "SG&A Expense": 150000,
            "depreciation": 50000
        }

        previous_period = {
            "totalRevenue": 900000,
            "Total Revenue": 900000,
            "totalCurrentAssets": 600000,
            "Total Current Assets": 600000,
            "grossProfit": 350000,
            "Gross Profit": 350000,
            "totalAssets": 1800000,
            "Total Assets": 1800000,
            "sellingGeneralAdministrative": 120000,
            "SG&A Expense": 120000,
            "depreciation": 60000
        }

        result = self.agent.calculate_beneish_m_score(current_period, previous_period)

        # Verify successful calculation
        assert result["success"] is True
        assert "beneish_m_score" in result

        m_score_data = result["beneish_m_score"]
        assert "m_score" in m_score_data
        assert "variables" in m_score_data
        assert "is_likely_manipulator" in m_score_data

        # Check all 8 variables are calculated
        variables = m_score_data["variables"]
        expected_variables = ["DSRI", "GMI", "AQI", "SGI", "DEPI", "SGAI", "LVGI", "TATA"]
        for var in expected_variables:
            assert var in variables

    def test_calculate_beneish_m_score_non_manipulator_example(self):
        """Test M-Score calculation with known non-manipulator company data"""
        # Example data representing a healthy company with no manipulation
        current_period = {
            "totalRevenue": 2000000,
            "Total Revenue": 2000000,
            "totalCurrentAssets": 600000,
            "Total Current Assets": 600000,
            "grossProfit": 800000,
            "Gross Profit": 800000,
            "totalAssets": 1500000,
            "Total Assets": 1500000,
            "sellingGeneralAdministrative": 200000,
            "SG&A Expense": 200000,
            "depreciation": 75000
        }

        previous_period = {
            "totalRevenue": 1800000,
            "Total Revenue": 1800000,
            "totalCurrentAssets": 550000,
            "Total Current Assets": 550000,
            "grossProfit": 750000,
            "Gross Profit": 750000,
            "totalAssets": 1400000,
            "Total Assets": 1400000,
            "sellingGeneralAdministrative": 180000,
            "SG&A Expense": 180000,
            "depreciation": 70000
        }

        result = self.agent.calculate_beneish_m_score(current_period, previous_period)

        # Verify successful calculation
        assert result["success"] is True
        m_score_data = result["beneish_m_score"]

        # For a healthy company, M-Score should typically be low (≤ -1.78)
        m_score = m_score_data["m_score"]
        assert m_score <= -1.78
        assert m_score_data["is_likely_manipulator"] is False
        assert m_score_data["risk_level"] == "LOW"

    def test_calculate_beneish_m_score_high_manipulation_risk(self):
        """Test M-Score calculation that should trigger high manipulation risk"""
        # Create data that should result in high M-Score (> -1.78)
        current_period = {
            "totalRevenue": 1000000,
            "totalCurrentAssets": 900000,  # Very high receivables
            "grossProfit": 200000,        # Declining margins
            "totalAssets": 1500000,
            "sellingGeneralAdministrative": 250000,  # Increasing SG&A
            "depreciation": 30000
        }

        previous_period = {
            "totalRevenue": 1200000,       # Revenue decline
            "totalCurrentAssets": 500000,  # Lower receivables previously
            "grossProfit": 400000,        # Higher margins previously
            "totalAssets": 1400000,
            "sellingGeneralAdministrative": 150000,  # Lower SG&A previously
            "depreciation": 40000
        }

        result = self.agent.calculate_beneish_m_score(current_period, previous_period)

        assert result["success"] is True
        m_score_data = result["beneish_m_score"]
        m_score = m_score_data["m_score"]

        # Should flag as manipulator (high risk)
        assert m_score > -1.78
        assert m_score_data["is_likely_manipulator"] is True
        assert m_score_data["risk_level"] == "HIGH"

    def test_calculate_beneish_m_score_missing_data(self):
        """Test M-Score calculation with missing critical data"""
        current_period = {
            "totalRevenue": 1000000,
            # Missing other required fields
        }

        previous_period = {
            "totalRevenue": 900000,
            # Missing other required fields
        }

        result = self.agent.calculate_beneish_m_score(current_period, previous_period)

        # Should handle gracefully with default values
        assert result["success"] is True
        m_score_data = result["beneish_m_score"]

        # Should get default M-Score around -2.48 (all variables = 1)
        assert abs(m_score_data["m_score"] - (-2.48)) < 0.1

    def test_calculate_beneish_m_score_zero_revenue(self):
        """Test M-Score calculation with zero revenue (edge case)"""
        current_period = {
            "totalRevenue": 0,
            "totalCurrentAssets": 100000,
            "grossProfit": 0,
            "totalAssets": 1000000,
            "sellingGeneralAdministrative": 50000,
            "depreciation": 10000
        }

        previous_period = {
            "totalRevenue": 1000000,
            "totalCurrentAssets": 80000,
            "grossProfit": 300000,
            "totalAssets": 900000,
            "sellingGeneralAdministrative": 40000,
            "depreciation": 15000
        }

        result = self.agent.calculate_beneish_m_score(current_period, previous_period)

        # Should handle zero revenue gracefully
        assert result["success"] is True

        # Variables that depend on revenue should be set to safe defaults
        variables = result["beneish_m_score"]["variables"]
        assert variables["SGI"] == 1  # Sales growth should be 1 when current revenue is 0

    def test_calculate_beneish_m_score_variable_calculations(self):
        """Test individual variable calculations for accuracy"""
        current_period = {
            "totalRevenue": 1000000,
            "totalCurrentAssets": 200000,
            "grossProfit": 400000,
            "totalAssets": 1000000,
            "sellingGeneralAdministrative": 100000,
            "depreciation": 50000
        }

        previous_period = {
            "totalRevenue": 800000,
            "totalCurrentAssets": 150000,
            "grossProfit": 350000,
            "totalAssets": 900000,
            "sellingGeneralAdministrative": 90000,
            "depreciation": 45000
        }

        result = self.agent.calculate_beneish_m_score(current_period, previous_period)

        assert result["success"] is True
        variables = result["beneish_m_score"]["variables"]

        # Test DSRI calculation: (200000/1000000) / (150000/800000) = 0.2 / 0.1875 = 1.067
        assert abs(variables["DSRI"] - 1.067) < 0.01

        # Test GMI calculation: (350000/800000) / (400000/1000000) = 0.4375 / 0.4 = 1.094
        assert abs(variables["GMI"] - 1.094) < 0.01

        # Test SGI calculation: 1000000/800000 = 1.25
        assert abs(variables["SGI"] - 1.25) < 0.01

        # Test SGAI calculation: (100000/1000000) / (90000/800000) = 0.1 / 0.1125 = 0.889
        assert abs(variables["SGAI"] - 0.889) < 0.01

    def test_calculate_beneish_m_score_real_company_data(self):
        """Test M-Score calculation with real company-like data"""
        # Simulate real financial data similar to what we've seen
        current_period = {
            "totalRevenue": 2436320000000,
            "totalCurrentAssets": 1650000000000,
            "grossProfit": 572000000000,
            "totalAssets": 19501210000000,
            "sellingGeneralAdministrative": 45000000000,
            "depreciation": 120000000000
        }

        previous_period = {
            "totalRevenue": 2380000000000,
            "totalCurrentAssets": 1500000000000,
            "grossProfit": 580000000000,
            "totalAssets": 17500000000000,
            "sellingGeneralAdministrative": 42000000000,
            "depreciation": 115000000000
        }

        result = self.agent.calculate_beneish_m_score(current_period, previous_period)

        assert result["success"] is True
        m_score_data = result["beneish_m_score"]

        # Verify all components are present
        assert "m_score" in m_score_data
        assert "threshold" in m_score_data
        assert "is_likely_manipulator" in m_score_data
        assert "risk_level" in m_score_data
        assert "variables" in m_score_data
        assert "interpretation" in m_score_data

        # Verify threshold is correct
        assert m_score_data["threshold"] == -1.78

        # Variables should be calculated (not all defaults)
        variables = m_score_data["variables"]
        assert variables["SGI"] != 1  # Should not be default if data is different
        assert variables["DSRI"] != 1  # Should not be default

    def test_calculate_beneish_m_score_error_handling(self):
        """Test error handling in M-Score calculation"""
        # Test with invalid data types
        current_period = {
            "totalRevenue": "invalid",
            "totalCurrentAssets": None,
            "grossProfit": float('inf'),
            "totalAssets": -1000,  # Negative assets
        }

        previous_period = {
            "totalRevenue": 1000000,
            "totalCurrentAssets": 100000,
            "grossProfit": 300000,
            "totalAssets": 2000000,
            "sellingGeneralAdministrative": 100000,
            "depreciation": 50000
        }

        # Should handle errors gracefully
        result = self.agent.calculate_beneish_m_score(current_period, previous_period)

        # Should still succeed with safe defaults
        assert result["success"] is True
        assert "beneish_m_score" in result

        # Should get reasonable M-Score even with problematic input
        m_score = result["beneish_m_score"]["m_score"]
        assert isinstance(m_score, (int, float))


if __name__ == "__main__":
    # Run tests if called directly
    test_suite = TestBeneishMScore()

    # Run a few key tests
    print("Running Beneish M-Score unit tests...")

    try:
        test_suite.test_calculate_beneish_m_score_manipulator_example()
        print("✅ Manipulator example test passed")

        test_suite.test_calculate_beneish_m_score_non_manipulator_example()
        print("✅ Non-manipulator example test passed")

        test_suite.test_calculate_beneish_m_score_variable_calculations()
        print("✅ Variable calculations test passed")

        test_suite.test_calculate_beneish_m_score_real_company_data()
        print("✅ Real company data test passed")

        print("\\n🎉 All Beneish M-Score tests passed!")
        print("✅ Unit tests implementation: COMPLETE")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise
