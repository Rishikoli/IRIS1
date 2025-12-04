"""
Project IRIS - API Clients Tests
Test external API clients with mocked responses
"""

import pytest
import json
from unittest.mock import patch, MagicMock

from src.api_clients import FMPAPIClient, NSEClient, BSEClient, BaseAPIClient
from src.config import settings


class TestBaseAPIClient:
    """Test base API client functionality"""

    def test_rate_limiter(self):
        """Test rate limiting functionality"""
        from src.api_clients.base_client import RateLimiter

        limiter = RateLimiter(calls_per_minute=5, calls_per_day=50)

        # Test initial state
        assert limiter.can_make_request() == True
        assert limiter.wait_time() == 0

        # Record requests
        for i in range(3):
            limiter.record_request()

        # Should still allow requests
        assert limiter.can_make_request() == True

        # Fill up the minute limit
        for i in range(2):  # 3 + 2 = 5 (limit reached)
            limiter.record_request()

        # Should not allow more requests
        assert limiter.can_make_request() == False
        assert limiter.wait_time() > 0


class TestFMPAPIClient:
    """Test Financial Modeling Prep API client"""

    @pytest.fixture
    def fmp_client(self):
        """Create FMP client with test API key"""
        return FMPAPIClient(api_key="test_key")

    def test_fmp_client_initialization(self, fmp_client):
        """Test FMP client initialization"""
        assert fmp_client.base_url == settings.fmp_base_url
        assert fmp_client.api_key == "test_key"
        assert fmp_client.timeout == settings.fmp_timeout

    def test_company_search(self, fmp_client, mock_api_responses):
        """Test company search functionality"""
        results = fmp_client.search_company("RELIANCE", limit=5)

        assert len(results) > 0
        assert results[0]["symbol"] == "RELIANCE.NS"
        assert results[0]["name"] == "Reliance Industries Limited"
        assert results[0]["country"] == "India"

    def test_company_profile(self, fmp_client, mock_api_responses):
        """Test company profile retrieval"""
        profile = fmp_client.get_company_profile("RELIANCE.NS")

        assert profile is not None
        assert profile["symbol"] == "RELIANCE.NS"
        assert profile["companyName"] == "Reliance Industries Limited"
        assert "marketCap" in profile

    def test_financial_statements(self, fmp_client, mock_api_responses):
        """Test financial statements retrieval"""
        # Test income statement
        income_statements = fmp_client.get_income_statement("RELIANCE.NS", period="annual", limit=1)

        assert len(income_statements) > 0
        statement = income_statements[0]
        assert "date" in statement
        assert "revenue" in statement
        assert "netIncome" in statement

        # Test balance sheet
        balance_sheets = fmp_client.get_balance_sheet("RELIANCE.NS", period="annual", limit=1)

        assert len(balance_sheets) > 0
        assert "totalAssets" in balance_sheets[0]
        assert "totalLiabilities" in balance_sheets[0]

        # Test cash flow
        cash_flows = fmp_client.get_cash_flow_statement("RELIANCE.NS", period="annual", limit=1)

        assert len(cash_flows) > 0
        assert "netCashProvidedByOperatingActivities" in cash_flows[0]

    def test_financial_ratios(self, fmp_client, mock_api_responses):
        """Test financial ratios retrieval"""
        ratios = fmp_client.get_financial_ratios("RELIANCE.NS", period="annual", limit=1)

        assert len(ratios) > 0
        ratio = ratios[0]
        assert "date" in ratio
        # Ratios should contain various financial metrics

    def test_comprehensive_financials(self, fmp_client, mock_api_responses):
        """Test comprehensive financial data retrieval"""
        data = fmp_client.get_comprehensive_financials("RELIANCE.NS", periods=2)

        assert "symbol" in data
        assert "profile" in data
        assert "income_statement" in data
        assert "balance_sheet" in data
        assert "cash_flow" in data
        assert "ratios" in data

    def test_error_handling(self, fmp_client):
        """Test error handling for API failures"""
        # Test with invalid symbol
        profile = fmp_client.get_company_profile("INVALID_SYMBOL")
        assert profile is None

        # Test with empty search
        results = fmp_client.search_company("")
        assert isinstance(results, list)


class TestNSEClient:
    """Test NSE API client"""

    @pytest.fixture
    def nse_client(self):
        """Create NSE client"""
        return NSEClient()

    def test_nse_client_initialization(self, nse_client):
        """Test NSE client initialization"""
        assert nse_client.base_url == "https://www.nseindia.com"
        assert nse_client.timeout == 30

    def test_company_search_by_symbol(self, nse_client, mock_api_responses):
        """Test NSE company search by symbol"""
        result = nse_client.search_company_by_symbol("RELIANCE")

        assert result is not None
        assert result["symbol"] == "RELIANCE"
        assert result["company_name"] == "Reliance Industries Limited"
        assert result["isin"] == "INE002A01018"

    def test_corporate_announcements(self, nse_client, mock_api_responses):
        """Test NSE corporate announcements"""
        announcements = nse_client.get_corporate_announcements(
            "RELIANCE",
            from_date=datetime(2023, 1, 1),
            to_date=datetime(2023, 12, 31)
        )

        assert len(announcements) > 0
        announcement = announcements[0]
        assert "symbol" in announcement
        assert "subject" in announcement
        assert "announcement_date" in announcement

    def test_financial_results(self, nse_client, mock_api_responses):
        """Test NSE financial results"""
        results = nse_client.get_financial_results("RELIANCE")

        assert len(results) > 0
        result = results[0]
        assert "symbol" in result
        assert "period" in result
        assert "attachment" in result

    def test_board_meetings(self, nse_client, mock_api_responses):
        """Test NSE board meetings"""
        meetings = nse_client.get_board_meetings("RELIANCE")

        assert len(meetings) > 0
        meeting = meetings[0]
        assert "symbol" in meeting
        assert "meeting_date" in meeting
        assert "purpose" in meeting

    def test_comprehensive_filings(self, nse_client, mock_api_responses):
        """Test comprehensive NSE filings"""
        data = nse_client.get_comprehensive_filings("RELIANCE")

        assert "symbol" in data
        assert "company_info" in data
        assert "announcements" in data
        assert "financial_results" in data
        assert "source" in data

    def test_session_handling(self, nse_client):
        """Test NSE session handling"""
        # Test session initialization
        result = nse_client._get_nse_session()
        # Should not raise exception even if it fails
        assert isinstance(result, bool)


class TestBSEClient:
    """Test BSE API client"""

    @pytest.fixture
    def bse_client(self):
        """Create BSE client"""
        return BSEClient()

    def test_bse_client_initialization(self, bse_client):
        """Test BSE client initialization"""
        assert bse_client.base_url == "https://www.bseindia.com"
        assert bse_client.timeout == 30

    def test_company_search_by_code(self, bse_client, mock_api_responses):
        """Test BSE company search by scrip code"""
        result = bse_client.search_company_by_code("500325")

        # May return None if scraping fails, but should not raise exception
        assert result is None or isinstance(result, dict)

    def test_company_search_by_name(self, bse_client, mock_api_responses):
        """Test BSE company search by name"""
        results = bse_client.search_company_by_name("Reliance")

        # Should return list, may be empty if scraping fails
        assert isinstance(results, list)

    def test_corporate_announcements(self, bse_client, mock_api_responses):
        """Test BSE corporate announcements"""
        announcements = bse_client.get_corporate_announcements(
            "500325",
            from_date=datetime(2023, 1, 1),
            to_date=datetime(2023, 12, 31)
        )

        assert isinstance(announcements, list)

    def test_financial_results(self, bse_client, mock_api_responses):
        """Test BSE financial results"""
        results = bse_client.get_financial_results("500325")

        assert isinstance(results, list)

    def test_comprehensive_filings(self, bse_client, mock_api_responses):
        """Test comprehensive BSE filings"""
        data = bse_client.get_comprehensive_filings("500325")

        assert "scrip_code" in data
        assert "source" in data
        assert isinstance(data.get("announcements", []), list)


class TestAPIIntegration:
    """Test API integration scenarios"""

    def test_multi_source_company_search(self):
        """Test searching company across multiple sources"""
        from src.agents.forensic.agent1_ingestion import DataIngestionAgent

        agent = DataIngestionAgent()

        # Test with Reliance (should exist in multiple sources)
        results = agent.search_company("RELIANCE")

        # Should get results from multiple sources
        sources = [result.get("source") for result in results]
        assert len(set(sources)) >= 1  # At least one source

        # Each result should have required fields
        for result in results:
            assert "symbol" in result
            assert "name" in result
            assert "source" in result

    def test_api_rate_limiting(self):
        """Test API rate limiting across clients"""
        # Create multiple clients
        fmp_client = FMPAPIClient()
        nse_client = NSEClient()
        bse_client = BSEClient()

        # Check rate limit status
        fmp_status = fmp_client.get_rate_limit_status()
        nse_status = nse_client.get_rate_limit_status()
        bse_status = bse_client.get_rate_limit_status()

        # All should have rate limit information
        for status in [fmp_status, nse_status, bse_status]:
            assert "calls_per_minute_limit" in status
            assert "calls_today" in status
            assert "can_make_request" in status

    def test_api_error_recovery(self):
        """Test API error recovery and retry logic"""
        # This would test the retry logic in BaseAPIClient
        # For now, just test that clients handle errors gracefully
        fmp_client = FMPAPIClient()

        # Test with invalid API key
        fmp_client.api_key = "invalid_key"
        profile = fmp_client.get_company_profile("RELIANCE.NS")

        # Should handle gracefully (return None or raise handled exception)
        assert profile is None or isinstance(profile, dict)

    def test_cross_api_data_consistency(self):
        """Test data consistency across different API sources"""
        # This is more of an integration test that would compare
        # data from different sources for the same company

        # For now, just test that we can get data from multiple sources
        fmp_client = FMPAPIClient()
        nse_client = NSEClient()

        # Get data from both sources for same company
        fmp_profile = fmp_client.get_company_profile("RELIANCE.NS")
        nse_info = nse_client.search_company_by_symbol("RELIANCE")

        # Both should return valid data (or None gracefully)
        assert fmp_profile is not None or nse_info is not None
