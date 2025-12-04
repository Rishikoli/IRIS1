"""
Project IRIS - Test Configuration
Testing configuration and fixtures
"""

import os
import pytest
import tempfile
from pathlib import Path
from typing import Dict, Any, Generator

# Test database configuration
TEST_DATABASE_URL = "postgresql://test_user:test_password@localhost:5433/iris_test"

# Test directories
TEST_DATA_DIR = Path(__file__).parent / "data"
TEST_FIXTURES_DIR = TEST_DATA_DIR / "fixtures"
TEST_MOCKS_DIR = TEST_DATA_DIR / "mocks"
TEST_OUTPUTS_DIR = TEST_DATA_DIR / "outputs"

# Create test directories
for directory in [TEST_DATA_DIR, TEST_FIXTURES_DIR, TEST_MOCKS_DIR, TEST_OUTPUTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Test configuration
@pytest.fixture(scope="session")
def test_config() -> Dict[str, Any]:
    """Test configuration"""
    return {
        "database_url": TEST_DATABASE_URL,
        "test_data_dir": str(TEST_DATA_DIR),
        "mock_api_responses": True,
        "enable_ocr_tests": True,
        "enable_integration_tests": True,
        "test_timeout": 30
    }

# Test database fixture (simplified for basic testing)
@pytest.fixture(scope="session")
def test_database():
    """Create test database for testing"""
    # For now, just return a mock since we don't have docker available
    # In a real environment, this would use Docker to spin up a test database

    # Create in-memory SQLite for basic testing
    from sqlalchemy import create_engine
    engine = create_engine("sqlite:///:memory:", echo=False)

    # Create all tables
    from src.models import Base
    Base.metadata.create_all(bind=engine)

    yield engine

    # Cleanup
    Base.metadata.drop_all(bind=engine)

# Test session fixture
@pytest.fixture
def db_session(test_database) -> Generator:
    """Create a database session for testing"""
    from sqlalchemy.orm import sessionmaker

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_database)

    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# Mock API responses fixture
@pytest.fixture
def mock_api_responses():
    """Mock external API responses for testing"""
    try:
        import requests_mock
        with requests_mock.Mocker() as m:
            # Mock FMP API responses
            _setup_fmp_mocks(m)
            # Mock NSE API responses
            _setup_nse_mocks(m)
            # Mock BSE API responses
            _setup_bse_mocks(m)

            yield m
    except ImportError:
        # If requests_mock not available, yield a dummy object
        class DummyMocker:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
        yield DummyMocker()

def _setup_fmp_mocks(m):
    """Set up FMP API mocks"""
    try:
        # Company search mock
        m.get(
            "https://financialmodelingprep.com/api/v3/search?query=RELIANCE&limit=5&apikey=test_key",
            json=[
                {
                    "symbol": "RELIANCE.NS",
                    "name": "Reliance Industries Limited",
                    "currency": "INR",
                    "exchange": "NSE",
                    "country": "India",
                    "sector": "Energy",
                    "industry": "Oil & Gas Refining & Marketing"
                }
            ]
        )

        # Company profile mock
        m.get(
            "https://financialmodelingprep.com/api/v3/profile/RELIANCE.NS?apikey=test_key",
            json=[{
                "symbol": "RELIANCE.NS",
                "companyName": "Reliance Industries Limited",
                "marketCap": 15000000000000,
                "sector": "Energy",
                "industry": "Oil & Gas Refining & Marketing",
                "currency": "INR"
            }]
        )

        # Financial statements mock
        m.get(
            "https://financialmodelingprep.com/api/v3/income-statement/RELIANCE.NS?limit=5&period=annual&apikey=test_key",
            json=[
                {
                    "date": "2023-03-31",
                    "revenue": 8500000000000,
                    "grossProfit": 2500000000000,
                    "operatingIncome": 1500000000000,
                    "netIncome": 750000000000
                }
            ]
        )
    except Exception:
        # Silently fail if mocking setup fails
        pass

def _setup_nse_mocks(m):
    """Set up NSE API mocks"""
    try:
        # NSE company info mock
        m.get(
            "https://www.nseindia.com/api/quote-equity?symbol=RELIANCE",
            json={
                "info": {
                    "symbol": "RELIANCE",
                    "companyName": "Reliance Industries Limited",
                    "industry": "Refineries",
                    "sector": "Oil, Gas & Consumable Fuels",
                    "isin": "INE002A01018"
                }
            }
        )
    except Exception:
        pass

def _setup_bse_mocks(m):
    """Set up BSE API mocks"""
    try:
        # BSE company info mock
        m.get(
            "https://www.bseindia.com/stock-share-price/stock-quote/500325",
            text="<html><body><title>Reliance Industries Ltd Share Price</title></body></html>",
            status_code=200
        )
    except Exception:
        pass

# Test data fixtures
@pytest.fixture
def sample_company_data():
    """Sample company data for testing"""
    return {
        "cin": "L99999MH1994PLC123456",
        "name": "Test Company Limited",
        "sector": "Technology",
        "industry": "Software",
        "nse_symbol": "TEST",
        "bse_symbol": "500123",
        "isin": "INE123A01012"
    }

@pytest.fixture
def sample_financial_data():
    """Sample financial statement data for testing"""
    return {
        "total_revenue": 10000000000,
        "total_assets": 50000000000,
        "total_liabilities": 30000000000,
        "total_equity": 20000000000,
        "net_profit": 5000000000,
        "currency": "INR",
        "units": "lakhs"
    }

@pytest.fixture
def sample_ocr_text():
    """Sample OCR extracted text for testing"""
    return """
    RELIANCE INDUSTRIES LIMITED
    ANNUAL REPORT 2023

    MANAGEMENT DISCUSSION AND ANALYSIS

    During the year under review, your Company achieved significant milestones...

    FINANCIAL HIGHLIGHTS

    Total Revenue: ₹8,50,000 crores
    Net Profit: ₹75,000 crores
    Total Assets: ₹15,00,000 crores

    AUDITOR'S REPORT

    We have audited the accompanying financial statements...
    """

# Test utilities
class TestUtils:
    """Utility functions for testing"""

    @staticmethod
    def create_test_pdf(content: str = "Test PDF Content") -> str:
        """Create a test PDF file"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter

            pdf_path = TEST_OUTPUTS_DIR / "test_document.pdf"
            c = canvas.Canvas(str(pdf_path), pagesize=letter)
            c.drawString(100, 750, content)
            c.save()

            return str(pdf_path)
        except ImportError:
            # If reportlab not available, create a dummy file
            pdf_path = TEST_OUTPUTS_DIR / "test_document.pdf"
            with open(pdf_path, 'w') as f:
                f.write(content)
            return str(pdf_path)

    @staticmethod
    def cleanup_test_files():
        """Clean up test-generated files"""
        import shutil
        if TEST_OUTPUTS_DIR.exists():
            shutil.rmtree(TEST_OUTPUTS_DIR)
            TEST_OUTPUTS_DIR.mkdir()

# Pytest configuration
def pytest_configure(config):
    """Configure pytest"""
    # Add custom markers
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "ocr: marks tests as OCR-related tests")
    config.addinivalue_line("markers", "api: marks tests as API-related tests")

def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    # Add markers to tests based on file path
    for item in items:
        if "test_integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "test_ocr" in str(item.fspath):
            item.add_marker(pytest.mark.ocr)
        elif "test_api" in str(item.fspath):
            item.add_marker(pytest.mark.api)
