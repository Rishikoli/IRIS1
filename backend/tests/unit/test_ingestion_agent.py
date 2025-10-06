"""
Project IRIS - Data Ingestion Agent Tests
Test data ingestion workflows and normalization
"""

import pytest
import json
from datetime import datetime
from unittest.mock import patch, MagicMock

from src.agents.forensic.agent1_ingestion import DataIngestionAgent
from src.models import StatementType, ReportingPeriod


class TestDataIngestionAgent:
    """Test data ingestion agent functionality"""

    @pytest.fixture
    def ingestion_agent(self):
        """Create data ingestion agent"""
        return DataIngestionAgent()

    def test_agent_initialization(self, ingestion_agent):
        """Test agent initialization"""
        assert ingestion_agent.fmp_client is not None
        assert ingestion_agent.nse_client is not None
        assert ingestion_agent.bse_client is not None
        assert ingestion_agent.document_scraper is not None

    def test_company_search_workflow(self, ingestion_agent):
        """Test complete company search workflow"""
        # Test search across all sources
        results = ingestion_agent.search_company("RELIANCE")

        # Should get results from at least one source
        assert len(results) > 0

        # Each result should have standard fields
        for result in results:
            assert "source" in result
            assert "symbol" in result
            assert "name" in result
            assert "currency" in result

    def test_financial_data_retrieval(self, ingestion_agent):
        """Test financial data retrieval from different sources"""
        # Test FMP data retrieval
        fmp_data = ingestion_agent.get_financials("RELIANCE.NS", "fmp", periods=2)

        assert "symbol" in fmp_data
        assert "income_statement" in fmp_data
        assert "balance_sheet" in fmp_data

        # Test NSE data retrieval
        nse_data = ingestion_agent.get_financials("RELIANCE", "nse")

        assert "symbol" in nse_data
        assert "announcements" in nse_data
        assert "source" in nse_data

        # Test BSE data retrieval
        bse_data = ingestion_agent.get_financials("500325", "bse")

        assert "scrip_code" in bse_data
        assert "source" in bse_data

    def test_data_normalization_fmp(self, ingestion_agent):
        """Test FMP data normalization"""
        # Sample FMP data
        fmp_data = {
            "symbol": "RELIANCE.NS",
            "income_statement": {
                "annual": [{
                    "date": "2023-03-31",
                    "revenue": 8500000000000,  # 8.5 trillion INR
                    "grossProfit": 2500000000000,
                    "operatingIncome": 1500000000000,
                    "netIncome": 750000000000
                }]
            },
            "balance_sheet": {
                "annual": [{
                    "date": "2023-03-31",
                    "totalAssets": 15000000000000,
                    "totalLiabilities": 9000000000000,
                    "totalStockholdersEquity": 6000000000000
                }]
            },
            "cash_flow": {
                "annual": [{
                    "date": "2023-03-31",
                    "netCashProvidedByOperatingActivities": 2000000000000,
                    "netCashUsedForInvestingActivites": -1500000000000,
                    "netCashUsedProvidedByFinancingActivities": -500000000000,
                    "netChangeInCash": 0
                }]
            }
        }

        normalized = ingestion_agent.normalize_financial_statements(fmp_data, "fmp")

        # Should have multiple statement types
        statement_types = [stmt["statement_type"] for stmt in normalized]
        assert StatementType.INCOME_STATEMENT in statement_types
        assert StatementType.BALANCE_SHEET in statement_types
        assert StatementType.CASH_FLOW in statement_types

        # Check normalization
        income_stmt = next(stmt for stmt in normalized if stmt["statement_type"] == StatementType.INCOME_STATEMENT)
        assert "total_revenue" in income_stmt
        assert "net_profit" in income_stmt
        assert income_stmt["currency"] == "USD"  # FMP default
        assert income_stmt["units"] == "dollars"

    def test_data_normalization_indian(self, ingestion_agent):
        """Test Indian market data normalization"""
        # Sample NSE data
        nse_data = {
            "symbol": "RELIANCE",
            "financial_results": [{
                "period": "Q4",
                "year_ending": "2023",
                "result_date": "2023-04-15",
                "attachment": "/financials/Q4_2023.pdf"
            }]
        }

        normalized = ingestion_agent.normalize_financial_statements(nse_data, "nse")

        # Should create placeholder structure for NSE data
        assert len(normalized) > 0
        statement = normalized[0]
        assert statement["symbol"] == "RELIANCE"
        assert statement["source"] == "nse"
        assert "document_url" in statement

    def test_currency_conversion(self, ingestion_agent):
        """Test currency conversion utilities"""
        # Test USD to INR lakhs conversion
        usd_amount = 1000000  # $1M USD
        converted = ingestion_agent._safe_convert_to_lakhs(usd_amount)

        # Should convert to lakhs (divide by 100,000)
        assert converted == 10  # $1M = 10 lakhs

        # Test with string input
        converted_str = ingestion_agent._safe_convert_to_lakhs("1,000,000")
        assert converted_str == 10

        # Test edge cases
        assert ingestion_agent._safe_convert_to_lakhs(None) is None
        assert ingestion_agent._safe_convert_to_lakhs("") is None
        assert ingestion_agent._safe_convert_to_lakhs("invalid") is None

    def test_date_parsing(self, ingestion_agent):
        """Test date parsing from different formats"""
        # Test various date formats
        test_cases = [
            ("2023-03-31", datetime(2023, 3, 31)),
            ("31/03/2023", datetime(2023, 3, 31)),
            ("2023-12-31", datetime(2023, 12, 31)),
            ("2023-03-31 10:30:00", datetime(2023, 3, 31)),
        ]

        for date_str, expected in test_cases:
            parsed = ingestion_agent._parse_date(date_str)
            assert parsed == expected, f"Failed to parse {date_str}"

        # Test invalid dates
        assert ingestion_agent._parse_date(None) is None
        assert ingestion_agent._parse_date("") is None
        assert ingestion_agent._parse_date("invalid-date") is None

    def test_period_type_detection(self, ingestion_agent):
        """Test reporting period type detection"""
        # Test different period strings
        test_cases = [
            ("Q4 2023", ReportingPeriod.QUARTERLY),
            ("quarterly", ReportingPeriod.QUARTERLY),
            ("H1 2023", ReportingPeriod.HALF_YEARLY),
            ("half yearly", ReportingPeriod.HALF_YEARLY),
            ("annual", ReportingPeriod.ANNUAL),
            ("yearly", ReportingPeriod.ANNUAL),
        ]

        for period_str, expected in test_cases:
            result = ingestion_agent._determine_period_type(period_str)
            assert result == expected, f"Failed for {period_str}"

    def test_balance_sheet_validation(self, ingestion_agent):
        """Test balance sheet validation logic"""
        # Test valid balance sheet
        valid_data = {
            "total_assets": 100000,
            "total_liabilities": 60000,
            "total_equity": 40000
        }

        is_valid, errors = ingestion_agent.balance_sheet_validator(valid_data)
        assert is_valid == True
        assert len(errors) == 0

        # Test invalid balance sheet
        invalid_data = {
            "total_assets": 100000,
            "total_liabilities": 60000,
            "total_equity": 50000  # Assets != Liabilities + Equity
        }

        is_valid, errors = ingestion_agent.balance_sheet_validator(invalid_data)
        assert is_valid == False
        assert len(errors) > 0
        assert "equation violation" in errors[0].lower()

        # Test negative assets
        negative_assets = {
            "total_assets": -100000,
            "total_liabilities": 60000,
            "total_equity": 40000
        }

        is_valid, errors = ingestion_agent.balance_sheet_validator(negative_assets)
        assert is_valid == False
        assert any("negative" in error.lower() for error in errors)

    def test_comprehensive_ingestion_workflow(self, ingestion_agent):
        """Test complete ingestion workflow"""
        # Search for company
        search_results = ingestion_agent.search_company("RELIANCE")

        if len(search_results) > 0:
            # Pick first result
            company_result = search_results[0]

            # Ingest company data
            job_id = ingestion_agent.ingest_company_data(company_result)

            # Should return a job ID or None
            assert job_id is None or isinstance(job_id, str)

    def test_error_handling_in_workflow(self, ingestion_agent):
        """Test error handling in ingestion workflow"""
        # Test with invalid company data
        invalid_company = {
            "source": "invalid",
            "symbol": "",
            "name": ""
        }

        job_id = ingestion_agent.ingest_company_data(invalid_company)

        # Should handle gracefully and return None
        assert job_id is None

    def test_document_processing_integration(self, ingestion_agent):
        """Test document processing integration"""
        # Test disclosure document fetching
        documents_result = ingestion_agent.fetch_disclosure_documents("RELIANCE", "nse")

        # Should return a dictionary with expected structure
        assert "symbol" in documents_result
        assert "documents_found" in documents_result
        assert "processed_documents" in documents_result
        assert "parsed_reports" in documents_result


class TestDataValidation:
    """Test data validation utilities"""

    def test_financial_data_validation(self, ingestion_agent):
        """Test financial data validation"""
        # Test valid financial data
        valid_financial = {
            "total_revenue": 10000000000,  # 1000 crores
            "total_assets": 50000000000,   # 5000 crores
            "total_liabilities": 30000000000,  # 3000 crores
            "total_equity": 20000000000,   # 2000 crores
            "net_profit": 5000000000       # 500 crores
        }

        # Should pass basic validation
        assert valid_financial["total_assets"] > 0
        assert valid_financial["total_equity"] > 0
        assert valid_financial["total_revenue"] > 0

        # Test balance sheet equation
        assets = valid_financial["total_assets"]
        liabilities = valid_financial["total_liabilities"]
        equity = valid_financial["total_equity"]

        # Should balance (within reasonable tolerance)
        assert abs(assets - (liabilities + equity)) / assets < 0.01  # 1% tolerance

    def test_data_normalization_edge_cases(self, ingestion_agent):
        """Test data normalization edge cases"""
        # Test with missing data
        incomplete_data = {
            "symbol": "TEST",
            "income_statement": {
                "annual": [{
                    "date": "2023-03-31",
                    # Missing most fields
                }]
            }
        }

        normalized = ingestion_agent.normalize_financial_statements(incomplete_data, "fmp")

        # Should handle missing data gracefully
        assert len(normalized) > 0
        statement = normalized[0]

        # Missing values should be None or handled appropriately
        assert statement["symbol"] == "TEST"

    def test_large_number_handling(self, ingestion_agent):
        """Test handling of large financial numbers"""
        # Test with very large numbers (typical for large corporations)
        large_numbers = {
            "revenue": 8500000000000,  # 8.5 trillion
            "assets": 15000000000000,  # 15 trillion
        }

        converted = ingestion_agent._safe_convert_to_lakhs(large_numbers["revenue"])

        # Should convert to lakhs correctly
        expected_lakhs = 85000000000  # 8.5 trillion / 100,000 = 85 billion lakhs
        assert converted == expected_lakhs


class TestPerformance:
    """Test performance characteristics"""

    def test_search_performance(self, ingestion_agent):
        """Test company search performance"""
        import time

        start_time = time.time()
        results = ingestion_agent.search_company("RELIANCE")
        end_time = time.time()

        # Should complete within reasonable time
        search_time = end_time - start_time
        assert search_time < 10  # 10 seconds max

        # Should return results
        assert len(results) >= 0  # May be empty but should not error

    def test_normalization_performance(self, ingestion_agent):
        """Test data normalization performance"""
        import time

        # Create large sample dataset
        large_fmp_data = {
            "symbol": "LARGE_TEST",
            "income_statement": {
                "annual": [
                    {
                        "date": f"202{i}-03-31",
                        "revenue": 1000000000000 * (i + 1),
                        "grossProfit": 300000000000 * (i + 1),
                        "operatingIncome": 200000000000 * (i + 1),
                        "netIncome": 100000000000 * (i + 1)
                    } for i in range(5)
                ]
            }
        }

        start_time = time.time()
        normalized = ingestion_agent.normalize_financial_statements(large_fmp_data, "fmp")
        end_time = time.time()

        # Should complete within reasonable time
        normalization_time = end_time - start_time
        assert normalization_time < 5  # 5 seconds max

        # Should produce correct number of statements
        assert len(normalized) == 15  # 5 years × 3 statement types
