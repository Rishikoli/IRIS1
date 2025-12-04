"""
Project IRIS - XBRL Parsing and Validation Tests
Unit tests with sample XBRL data and validation edge cases
"""

import pytest
import xml.etree.ElementTree as ET
from decimal import Decimal
from datetime import datetime

from src.utils.xbrl_parser import XBRLParser, normalize_xbrl_to_standard_schema
from tests.fixtures.xbrl_test_data import (
    create_sample_xbrl_balance_sheet,
    create_sample_xbrl_income_statement,
    create_sample_xbrl_cash_flow,
    create_malformed_xbrl_data,
    create_xbrl_with_negative_values,
    create_xbrl_validation_edge_cases,
    create_xbrl_parsing_test_cases
)


class TestXBRLParser:
    """Test XBRL parsing functionality"""

    @pytest.fixture
    def xbrl_parser(self):
        """Create XBRL parser instance"""
        return XBRLParser()

    def test_xbrl_parser_initialization(self, xbrl_parser):
        """Test XBRL parser initialization"""
        assert xbrl_parser.namespaces is not None
        assert "xbrli" in xbrl_parser.namespaces
        assert "xbrldi" in xbrl_parser.namespaces

    def test_parse_valid_balance_sheet(self, xbrl_parser):
        """Test parsing valid XBRL balance sheet"""
        xbrl_content = create_sample_xbrl_balance_sheet()
        result = xbrl_parser.parse_xbrl_data(xbrl_content)

        # Should parse successfully
        assert result["success"] == True
        assert "entity_info" in result
        assert "contexts" in result
        assert "financial_data" in result

        # Check entity info
        entity_info = result["entity_info"]
        assert "identifier" in entity_info
        assert entity_info["identifier"] == "INE002A01018"

        # Check contexts
        contexts = result["contexts"]
        assert len(contexts) >= 2  # c1 and c2

        # Check financial data
        financial_data = result["financial_data"]
        assert "TotalAssets" in financial_data
        assert "TotalLiabilities" in financial_data
        assert "TotalEquity" in financial_data

    def test_parse_valid_income_statement(self, xbrl_parser):
        """Test parsing valid XBRL income statement"""
        xbrl_content = create_sample_xbrl_income_statement()
        result = xbrl_parser.parse_xbrl_data(xbrl_content)

        # Should parse successfully
        assert result["success"] == True

        # Check financial data
        financial_data = result["financial_data"]
        assert "TotalRevenue" in financial_data
        assert "ProfitAfterTax" in financial_data
        assert "BasicEPS" in financial_data

        # Check data points have correct structure
        revenue_data = financial_data["TotalRevenue"]
        assert len(revenue_data) > 0
        assert "value" in revenue_data[0]
        assert "context" in revenue_data[0]
        assert revenue_data[0]["value"] == Decimal("850000")

    def test_parse_valid_cash_flow(self, xbrl_parser):
        """Test parsing valid XBRL cash flow statement"""
        xbrl_content = create_sample_xbrl_cash_flow()
        result = xbrl_parser.parse_xbrl_data(xbrl_content)

        # Should parse successfully
        assert result["success"] == True

        # Check financial data
        financial_data = result["financial_data"]
        assert "NetCashFromOperatingActivities" in financial_data
        assert "NetCashFromInvestingActivities" in financial_data
        assert "NetCashFromFinancingActivities" in financial_data

    def test_parse_malformed_xbrl(self, xbrl_parser):
        """Test parsing malformed XBRL data"""
        xbrl_content = create_malformed_xbrl_data()
        result = xbrl_parser.parse_xbrl_data(xbrl_content)

        # Should fail gracefully
        assert result["success"] == False
        assert "error" in result
        assert result["error_type"] in ["parse_error", "unexpected_error"]

    def test_parse_negative_values(self, xbrl_parser):
        """Test parsing XBRL with negative values"""
        xbrl_content = create_xbrl_with_negative_values()
        result = xbrl_parser.parse_xbrl_data(xbrl_content)

        # Should parse successfully despite negative values
        assert result["success"] == True

        # Check that negative values are preserved
        financial_data = result["financial_data"]
        total_assets_data = financial_data.get("TotalAssets", [])
        if total_assets_data:
            assert total_assets_data[0]["value"] == Decimal("-100000")

    def test_safe_decimal_conversion(self, xbrl_parser):
        """Test safe decimal conversion"""
        # Test valid conversions
        assert xbrl_parser._safe_decimal("123456") == Decimal("123456")
        assert xbrl_parser._safe_decimal("-123456") == Decimal("-123456")
        assert xbrl_parser._safe_decimal("123,456") == Decimal("123456")
        assert xbrl_parser._safe_decimal("123.45") == Decimal("123.45")

        # Test invalid conversions
        assert xbrl_parser._safe_decimal("invalid") is None
        assert xbrl_parser._safe_decimal("") is None
        assert xbrl_parser._safe_decimal(None) is None

    def test_context_extraction(self, xbrl_parser):
        """Test context information extraction"""
        xbrl_content = create_sample_xbrl_balance_sheet()
        result = xbrl_parser.parse_xbrl_data(xbrl_content)

        contexts = result["contexts"]

        # Should have multiple contexts
        assert len(contexts) >= 2

        # Check context structure
        for context_id, context_info in contexts.items():
            assert "entity" in context_info
            assert "period" in context_info

            # Check entity info
            entity_info = context_info["entity"]
            assert "identifier" in entity_info

            # Check period info
            period_info = context_info["period"]
            assert "type" in period_info

    def test_unit_extraction(self, xbrl_parser):
        """Test unit information extraction"""
        xbrl_content = create_sample_xbrl_balance_sheet()
        result = xbrl_parser.parse_xbrl_data(xbrl_content)

        units = result["units"]

        # Should have units defined
        assert len(units) > 0
        assert "u1" in units

        # Check unit structure
        unit_info = units["u1"]
        assert "measure" in unit_info
        assert unit_info["measure"] == "iso4217:INR"


class TestXBRLNormalization:
    """Test XBRL to standard schema normalization"""

    def test_normalize_balance_sheet(self):
        """Test balance sheet normalization"""
        xbrl_content = create_sample_xbrl_balance_sheet()
        parser = XBRLParser()
        parsed_data = parser.parse_xbrl_data(xbrl_content)

        normalized = normalize_xbrl_to_standard_schema(parsed_data)

        # Should find balance sheet
        balance_sheets = [stmt for stmt in normalized if stmt.get("statement_type") == "balance_sheet"]
        assert len(balance_sheets) >= 1

        bs = balance_sheets[0]
        assert "data" in bs
        bs_data = bs["data"]

        # Check normalized fields
        assert "total_assets" in bs_data
        assert "total_liabilities" in bs_data
        assert "total_equity" in bs_data
        assert bs_data["currency"] == "INR"
        assert bs_data["units"] == "crores"

        # Verify balance sheet equation
        assets = bs_data["total_assets"]
        liabilities = bs_data["total_liabilities"]
        equity = bs_data["total_equity"]
        assert abs(assets - (liabilities + equity)) / assets < 0.01  # 1% tolerance

    def test_normalize_income_statement(self):
        """Test income statement normalization"""
        xbrl_content = create_sample_xbrl_income_statement()
        parser = XBRLParser()
        parsed_data = parser.parse_xbrl_data(xbrl_content)

        normalized = normalize_xbrl_to_standard_schema(parsed_data)

        # Should find income statement
        income_statements = [stmt for stmt in normalized if stmt.get("statement_type") == "income_statement"]
        assert len(income_statements) >= 1

        income_stmt = income_statements[0]
        assert "data" in income_stmt
        is_data = income_stmt["data"]

        # Check normalized fields
        assert "total_revenue" in is_data
        assert "net_profit" in is_data
        assert "currency" in is_data
        assert "units" in is_data

        # Check values
        assert is_data["total_revenue"] == 850000
        assert is_data["net_profit"] == 250000

    def test_normalize_cash_flow(self):
        """Test cash flow normalization"""
        xbrl_content = create_sample_xbrl_cash_flow()
        parser = XBRLParser()
        parsed_data = parser.parse_xbrl_data(xbrl_content)

        normalized = normalize_xbrl_to_standard_schema(parsed_data)

        # Should find cash flow statement
        cash_flows = [stmt for stmt in normalized if stmt.get("statement_type") == "cash_flow"]
        assert len(cash_flows) >= 1

        cf = cash_flows[0]
        assert "data" in cf
        cf_data = cf["data"]

        # Check normalized fields
        assert "net_cash_from_operating_activities" in cf_data
        assert "net_cash_from_investing_activities" in cf_data
        assert "net_cash_from_financing_activities" in cf_data
        assert "currency" in cf_data
        assert "units" in cf_data

    def test_normalize_malformed_data(self):
        """Test normalization with malformed XBRL data"""
        xbrl_content = create_malformed_xbrl_data()
        parser = XBRLParser()
        parsed_data = parser.parse_xbrl_data(xbrl_content)

        # Should handle gracefully
        if parsed_data["success"]:
            normalized = normalize_xbrl_to_standard_schema(parsed_data)
            # May be empty or have partial data
            assert isinstance(normalized, list)
        else:
            # Should not crash
            normalized = normalize_xbrl_to_standard_schema(parsed_data)
            assert isinstance(normalized, list)


class TestXBRLValidationEdgeCases:
    """Test XBRL validation with edge cases"""

    def test_validation_edge_cases(self):
        """Test validation with various edge cases"""
        from src.agents.forensic.agent1_ingestion import DataIngestionAgent

        agent = DataIngestionAgent()
        test_cases = create_xbrl_validation_edge_cases()

        for test_case in test_cases:
            case_name = test_case["name"]
            data = test_case["data"]
            expected_valid = test_case["expected_valid"]
            expected_errors = test_case["expected_errors"]

            # Run validation
            is_valid, errors = agent.balance_sheet_validator(data)

            # Check results
            assert is_valid == expected_valid, f"Failed for {case_name}: expected {expected_valid}, got {is_valid}"
            assert len(errors) == len(expected_errors), f"Failed for {case_name}: expected {len(expected_errors)} errors, got {len(errors)}"

            # Check error messages
            for expected_error in expected_errors:
                assert any(expected_error.lower() in error.lower() for error in errors), \
                    f"Failed for {case_name}: expected error '{expected_error}' not found in {errors}"

    def test_validation_with_large_numbers(self):
        """Test validation with very large financial numbers"""
        from src.agents.forensic.agent1_ingestion import DataIngestionAgent

        agent = DataIngestionAgent()

        # Test with Reliance-sized numbers (in crores)
        large_balance_sheet = {
            "total_assets": Decimal("1500000000000"),      # 1.5 lakh crores
            "total_liabilities": Decimal("900000000000"),   # 90k crores
            "total_equity": Decimal("600000000000")        # 60k crores
        }

        is_valid, errors = agent.balance_sheet_validator(large_balance_sheet)

        # Should be valid (equation holds)
        assert is_valid == True
        assert len(errors) == 0

    def test_validation_with_negative_values(self):
        """Test validation with negative values"""
        from src.agents.forensic.agent1_ingestion import DataIngestionAgent

        agent = DataIngestionAgent()

        # Test with negative assets (invalid)
        negative_balance_sheet = {
            "total_assets": Decimal("-100000"),
            "total_liabilities": Decimal("60000"),
            "total_equity": Decimal("40000")
        }

        is_valid, errors = agent.balance_sheet_validator(negative_balance_sheet)

        # Should be invalid due to negative assets
        assert is_valid == False
        assert len(errors) > 0
        assert any("negative" in error.lower() for error in errors)

    def test_validation_with_missing_fields(self):
        """Test validation with missing required fields"""
        from src.agents.forensic.agent1_ingestion import DataIngestionAgent

        agent = DataIngestionAgent()

        # Test with missing total_equity
        incomplete_balance_sheet = {
            "total_assets": Decimal("100000"),
            "total_liabilities": Decimal("60000")
            # Missing total_equity
        }

        is_valid, errors = agent.balance_sheet_validator(incomplete_balance_sheet)

        # Should be invalid due to missing fields
        assert is_valid == False
        assert len(errors) > 0
        assert any("missing" in error.lower() or "required" in error.lower() for error in errors)

    def test_validation_with_precision_issues(self):
        """Test validation with decimal precision issues"""
        from src.agents.forensic.agent1_ingestion import DataIngestionAgent

        agent = DataIngestionAgent()

        # Test with slight rounding differences
        precision_balance_sheet = {
            "total_assets": Decimal("100000.123"),
            "total_liabilities": Decimal("60000.456"),
            "total_equity": Decimal("39999.667")  # Slight difference due to rounding
        }

        is_valid, errors = agent.balance_sheet_validator(precision_balance_sheet)

        # Should pass validation with tolerance
        assert is_valid == True
        assert len(errors) == 0

    def test_validation_tolerance_handling(self):
        """Test validation tolerance for minor discrepancies"""
        from src.agents.forensic.agent1_ingestion import DataIngestionAgent

        agent = DataIngestionAgent()

        # Test with 0.5% discrepancy (within tolerance)
        tolerance_balance_sheet = {
            "total_assets": Decimal("100000"),
            "total_liabilities": Decimal("60000"),
            "total_equity": Decimal("40100")  # 1% difference
        }

        is_valid, errors = agent.balance_sheet_validator(tolerance_balance_sheet)

        # Should pass with tolerance
        assert is_valid == True
        assert len(errors) == 0


class TestXBRLIntegration:
    """Test XBRL integration scenarios"""

    def test_end_to_end_xbrl_processing(self):
        """Test complete XBRL processing pipeline"""
        # Parse XBRL data
        xbrl_content = create_sample_xbrl_balance_sheet()
        parser = XBRLParser()
        parsed_data = parser.parse_xbrl_data(xbrl_content)

        # Normalize to standard schema
        normalized = normalize_xbrl_to_standard_schema(parsed_data)

        # Validate normalized data
        from src.agents.forensic.agent1_ingestion import DataIngestionAgent
        agent = DataIngestionAgent()

        # Should have valid balance sheet
        balance_sheets = [stmt for stmt in normalized if stmt.get("statement_type") == "balance_sheet"]
        assert len(balance_sheets) >= 1

        bs_data = balance_sheets[0]["data"]
        is_valid, errors = agent.balance_sheet_validator(bs_data)

        # Should be valid
        assert is_valid == True
        assert len(errors) == 0

    def test_multiple_statement_types(self):
        """Test processing XBRL with multiple statement types"""
        # This would combine balance sheet, income statement, and cash flow
        # For now, test that we can handle multiple contexts

        xbrl_content = create_sample_xbrl_balance_sheet()
        parser = XBRLParser()
        parsed_data = parser.parse_xbrl_data(xbrl_content)

        # Should have multiple contexts
        contexts = parsed_data["contexts"]
        assert len(contexts) >= 2

        # Each context should have entity and period info
        for context_info in contexts.values():
            assert "entity" in context_info
            assert "period" in context_info
            assert "identifier" in context_info["entity"]

    def test_xbrl_error_recovery(self):
        """Test error recovery in XBRL processing"""
        parser = XBRLParser()

        # Test with various error conditions
        error_cases = [
            "",  # Empty string
            "<invalid>xml</invalid>",  # Invalid XML
            "<?xml version=\"1.0\"?><xbrl></xbrl>",  # Valid XML but no XBRL content
        ]

        for error_case in error_cases:
            result = parser.parse_xbrl_data(error_case)

            # Should handle gracefully without crashing
            assert "success" in result
            if not result["success"]:
                assert "error" in result
                assert "error_type" in result


class TestXBRLPerformance:
    """Test XBRL processing performance"""

    def test_xbrl_parsing_performance(self):
        """Test XBRL parsing performance"""
        import time

        xbrl_content = create_sample_xbrl_balance_sheet()
        parser = XBRLParser()

        # Measure parsing time
        start_time = time.time()
        result = parser.parse_xbrl_data(xbrl_content)
        end_time = time.time()

        parsing_time = end_time - start_time

        # Should parse within reasonable time
        assert parsing_time < 1.0  # 1 second
        assert result["success"] == True

    def test_normalization_performance(self):
        """Test XBRL normalization performance"""
        import time

        xbrl_content = create_sample_xbrl_balance_sheet()
        parser = XBRLParser()
        parsed_data = parser.parse_xbrl_data(xbrl_content)

        # Measure normalization time
        start_time = time.time()
        normalized = normalize_xbrl_to_standard_schema(parsed_data)
        end_time = time.time()

        normalization_time = end_time - start_time

        # Should normalize within reasonable time
        assert normalization_time < 0.5  # 0.5 seconds
        assert len(normalized) > 0

    def test_large_xbrl_handling(self):
        """Test handling of large XBRL documents"""
        # Create larger XBRL content (simulate multiple years)
        large_xbrl_parts = []

        # Add multiple years of data
        for year in range(2020, 2024):
            # Modify sample to different year
            xbrl_content = create_sample_xbrl_balance_sheet()
            xbrl_content = xbrl_content.replace("2024-03-31", f"{year+1}-03-31")
            xbrl_content = xbrl_content.replace("2023-03-31", f"{year}-03-31")
            large_xbrl_parts.append(xbrl_content)

        # Combine into large document
        large_xbrl = "\n".join(large_xbrl_parts)

        parser = XBRLParser()

        # Should handle large documents
        start_time = time.time()
        result = parser.parse_xbrl_data(large_xbrl)
        end_time = time.time()

        processing_time = end_time - start_time

        # Should complete within reasonable time
        assert processing_time < 2.0  # 2 seconds for large document
        # May succeed or fail gracefully, but should not hang
        assert "success" in result
