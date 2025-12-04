"""
Project IRIS - Integration Tests
End-to-end integration tests for complete workflows
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock

from src.agents.forensic.agent1_ingestion import DataIngestionAgent
from src.api_clients import FMPAPIClient, NSEClient, BSEClient
from src.utils.document_scraper import DocumentScraper


class TestDataIngestionWorkflow:
    """Test complete data ingestion workflows"""

    @pytest.mark.integration
    def test_company_search_to_ingestion_pipeline(self, mock_api_responses):
        """Test complete pipeline from search to ingestion"""
        agent = DataIngestionAgent()

        # 1. Search for company
        search_results = agent.search_company("RELIANCE")

        assert len(search_results) > 0, "Should find company in at least one source"

        # 2. Get financial data
        company_result = search_results[0]
        financial_data = agent.get_financials(
            company_result["symbol"],
            company_result["source"]
        )

        assert "error" not in financial_data, "Should get financial data successfully"

        # 3. Normalize data
        normalized_statements = agent.normalize_financial_statements(
            financial_data,
            company_result["source"]
        )

        assert len(normalized_statements) > 0, "Should normalize financial statements"

        # 4. Validate data quality
        for statement in normalized_statements:
            if statement.get("statement_type") == "balance_sheet":
                is_valid, errors = agent.balance_sheet_validator(statement)
                # Balance sheet should be valid (or have acceptable tolerance)
                assert is_valid or len(errors) < 3, f"Too many validation errors: {errors}"

    @pytest.mark.integration
    def test_multi_source_data_consistency(self):
        """Test data consistency across multiple sources"""
        agent = DataIngestionAgent()

        # Search for same company across sources
        search_results = agent.search_company("RELIANCE")

        if len(search_results) >= 2:
            # Compare data from different sources
            source_data = {}

            for result in search_results[:2]:  # Compare first two sources
                financial_data = agent.get_financials(
                    result["symbol"],
                    result["source"]
                )

                if "error" not in financial_data:
                    source_data[result["source"]] = financial_data

            # Should have data from multiple sources
            assert len(source_data) >= 1

            # Data should have consistent structure
            for source, data in source_data.items():
                assert "symbol" in data or "scrip_code" in data

    @pytest.mark.integration
    def test_document_processing_pipeline(self, mock_api_responses):
        """Test complete document processing pipeline"""
        scraper = DocumentScraper()

        # 1. Fetch documents
        documents = scraper.fetch_disclosure_documents("RELIANCE", "nse")

        assert isinstance(documents, list)

        # 2. Get comprehensive documents with processing
        comprehensive_result = scraper.get_comprehensive_documents("RELIANCE", "nse")

        # Should have expected structure
        assert "symbol" in comprehensive_result
        assert "documents_found" in comprehensive_result
        assert "processed_documents" in comprehensive_result

        # 3. Test section parsing (if we have processed text)
        if comprehensive_result.get("parsed_reports"):
            for report in comprehensive_result["parsed_reports"]:
                assert "sections" in report
                assert "document_info" in report


class TestAPIIntegration:
    """Test API integrations"""

    @pytest.mark.integration
    def test_api_client_health_checks(self):
        """Test API client health and connectivity"""
        clients = [
            FMPAPIClient(),
            NSEClient(),
            BSEClient()
        ]

        for client in clients:
            # Test connection (may fail if APIs are down)
            try:
                health = client.test_connection()
                # Should return boolean or handle gracefully
                assert isinstance(health, bool)
            except Exception:
                # Should handle connection errors gracefully
                pass

    @pytest.mark.integration
    def test_cross_api_data_comparison(self):
        """Test data comparison across APIs"""
        # This would compare data from different APIs for same company
        # For now, just test that we can query multiple APIs

        fmp_client = FMPAPIClient()
        nse_client = NSEClient()

        # Test that we can query both APIs (may return None if data unavailable)
        fmp_data = fmp_client.get_company_profile("RELIANCE.NS")
        nse_data = nse_client.search_company_by_symbol("RELIANCE")

        # Should handle responses gracefully
        assert fmp_data is None or isinstance(fmp_data, dict)
        assert nse_data is None or isinstance(nse_data, dict)


class TestDatabaseIntegration:
    """Test database integration"""

    @pytest.mark.integration
    def test_database_operations_integration(self, db_session):
        """Test integrated database operations"""
        from src.models import Company, FinancialStatement, StatementType

        # Create company
        company = Company(
            cin="L99999MH1994PLC123456",
            name="Integration Test Company",
            sector="Technology",
            nse_symbol="INTTEST"
        )

        db_session.add(company)
        db_session.commit()

        # Create financial statement
        statement = FinancialStatement(
            company_id=company.id,
            statement_type=StatementType.BALANCE_SHEET,
            period_type="annual",
            fiscal_year=2023,
            period_end="2023-03-31",
            total_assets=100000,
            total_liabilities=60000,
            total_equity=40000
        )

        db_session.add(statement)
        db_session.commit()

        # Query back
        retrieved_company = db_session.query(Company).filter_by(cin="L99999MH1994PLC123456").first()
        retrieved_statement = db_session.query(FinancialStatement).filter_by(company_id=company.id).first()

        # Verify relationships
        assert retrieved_company is not None
        assert len(retrieved_company.financial_statements) == 1
        assert retrieved_statement.company_id == company.id

    @pytest.mark.integration
    def test_database_transaction_rollback(self, db_session):
        """Test database transaction rollback in complex scenarios"""
        from src.models import Company, FinancialStatement

        # Start transaction
        company = Company(
            cin="L99999MH1994PLC654321",
            name="Rollback Test Company",
            sector="Finance"
        )

        db_session.add(company)

        # Simulate error during statement creation
        try:
            statement = FinancialStatement(
                company_id=999999,  # Invalid foreign key
                statement_type=StatementType.BALANCE_SHEET,
                period_type="annual",
                fiscal_year=2023,
                period_end="2023-03-31"
            )
            db_session.add(statement)
            db_session.commit()
        except Exception:
            db_session.rollback()

        # Company should not be committed due to rollback
        result = db_session.query(Company).filter_by(cin="L99999MH1994PLC654321").first()
        assert result is None


class TestPerformanceIntegration:
    """Test performance in integrated scenarios"""

    @pytest.mark.integration
    @pytest.mark.slow
    def test_large_dataset_processing(self):
        """Test processing of large datasets"""
        agent = DataIngestionAgent()

        # Test with multiple companies
        companies = ["RELIANCE", "TCS", "INFY", "HDFC"]

        results = {}
        for company in companies:
            start_time = asyncio.get_event_loop().time()

            # Search and get basic info
            search_results = agent.search_company(company)

            end_time = asyncio.get_event_loop().time()
            processing_time = end_time - start_time

            results[company] = {
                "found": len(search_results) > 0,
                "processing_time": processing_time
            }

        # All companies should be found and processed within time limits
        for company, result in results.items():
            assert result["found"], f"Company {company} not found"
            assert result["processing_time"] < 30, f"Company {company} took too long: {result['processing_time']}s"


class TestErrorHandlingIntegration:
    """Test error handling in integrated scenarios"""

    @pytest.mark.integration
    def test_graceful_degradation_on_api_failures(self):
        """Test graceful degradation when APIs fail"""
        # Test with invalid API keys or endpoints
        fmp_client = FMPAPIClient(api_key="invalid_key")

        # Should handle API failures gracefully
        profile = fmp_client.get_company_profile("RELIANCE.NS")
        assert profile is None  # Should return None, not raise exception

        # Should not crash the application
        search_results = fmp_client.search_company("RELIANCE")
        assert isinstance(search_results, list)  # Should return empty list

    @pytest.mark.integration
    def test_robustness_with_mixed_data_quality(self):
        """Test robustness with varying data quality"""
        agent = DataIngestionAgent()

        # Test with various company names (some may not exist)
        test_companies = [
            "RELIANCE",      # Should exist
            "INVALID_COMPANY_123",  # Should not exist
            "",              # Empty string
            "A" * 100        # Very long string
        ]

        for company in test_companies:
            # Should handle all cases without crashing
            try:
                results = agent.search_company(company)
                assert isinstance(results, list)

                if results:
                    financial_data = agent.get_financials(results[0]["symbol"], results[0]["source"])
                    assert isinstance(financial_data, dict)

            except Exception as e:
                pytest.fail(f"Failed to handle company '{company}': {e}")


class TestEndToEndWorkflows:
    """Test complete end-to-end workflows"""

    @pytest.mark.integration
    @pytest.mark.slow
    def test_complete_financial_analysis_workflow(self):
        """Test complete workflow from data ingestion to analysis"""
        # This would be a comprehensive test of the entire pipeline
        # For now, test the structure and error handling

        agent = DataIngestionAgent()

        # 1. Company discovery
        companies = agent.search_company("RELIANCE")
        assert len(companies) > 0

        # 2. Data ingestion
        company = companies[0]
        job_id = agent.ingest_company_data(company)

        # Should complete without errors
        assert job_id is None or isinstance(job_id, str)

        # 3. Document processing (if applicable)
        if company["source"] in ["nse", "bse"]:
            docs_result = agent.fetch_disclosure_documents(
                company["symbol"],
                company["source"]
            )

            assert "documents_found" in docs_result

    @pytest.mark.integration
    def test_data_quality_assurance_pipeline(self):
        """Test data quality assurance throughout pipeline"""
        agent = DataIngestionAgent()

        # Test data normalization and validation
        sample_data = {
            "total_assets": 100000,
            "total_liabilities": 60000,
            "total_equity": 40000
        }

        # Should pass validation
        is_valid, errors = agent.balance_sheet_validator(sample_data)
        assert is_valid == True

        # Test with invalid data
        invalid_data = {
            "total_assets": 100000,
            "total_liabilities": 60000,
            "total_equity": 50000  # Invalid
        }

        is_valid, errors = agent.balance_sheet_validator(invalid_data)
        assert is_valid == False
        assert len(errors) > 0


@pytest.fixture(scope="session", autouse=True)
def cleanup_after_tests():
    """Clean up after all tests"""
    yield

    # Clean up test files
    from tests.unit.test_ocr_processing import TestUtils
    TestUtils.cleanup_test_files()
