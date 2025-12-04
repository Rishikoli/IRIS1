"""
Project IRIS - Database Tests
Test database models, connections, and operations
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.models import (
    Company, CompanyAlias, FinancialStatement, FinancialRatio,
    StatementType, ReportingPeriod, AnalysisJob, ForensicAnalysis,
    RiskScore, RiskFactor, ComplianceValidation, ChatSession,
    get_db, create_tables
)
from src.database.connection import PostgreSQLClient


class TestDatabaseModels:
    """Test database models and relationships"""

    def test_company_creation(self, db_session: Session, sample_company_data):
        """Test company model creation"""
        # Create company
        company = Company(**sample_company_data)
        db_session.add(company)
        db_session.commit()
        db_session.refresh(company)

        # Verify creation
        assert company.id is not None
        assert company.name == sample_company_data["name"]
        assert company.cin == sample_company_data["cin"]
        assert company.created_at is not None

    def test_company_alias_creation(self, db_session: Session, sample_company_data):
        """Test company alias model"""
        # Create company first
        company = Company(**sample_company_data)
        db_session.add(company)
        db_session.commit()

        # Create alias
        alias = CompanyAlias(
            company_id=company.id,
            alias_type="old_name",
            alias_value="Previous Company Name Ltd",
            is_primary=False
        )
        db_session.add(alias)
        db_session.commit()

        # Verify relationship
        assert len(company.aliases) == 1
        assert company.aliases[0].alias_value == "Previous Company Name Ltd"

    def test_financial_statement_creation(self, db_session: Session, sample_company_data, sample_financial_data):
        """Test financial statement model"""
        # Create company
        company = Company(**sample_company_data)
        db_session.add(company)
        db_session.commit()

        # Create financial statement
        statement = FinancialStatement(
            company_id=company.id,
            statement_type=StatementType.BALANCE_SHEET,
            period_type=ReportingPeriod.ANNUAL,
            fiscal_year=2023,
            period_start=datetime(2023, 4, 1),
            period_end=datetime(2024, 3, 31),
            **sample_financial_data
        )
        db_session.add(statement)
        db_session.commit()

        # Verify creation
        assert statement.id is not None
        assert statement.company_id == company.id
        assert statement.total_assets == sample_financial_data["total_assets"]

    def test_financial_ratios_creation(self, db_session: Session, sample_company_data):
        """Test financial ratio model"""
        # Create company and statement
        company = Company(**sample_company_data)
        db_session.add(company)
        db_session.commit()

        statement = FinancialStatement(
            company_id=company.id,
            statement_type=StatementType.BALANCE_SHEET,
            period_type=ReportingPeriod.ANNUAL,
            fiscal_year=2023,
            period_end=datetime(2024, 3, 31),
            total_assets=100000,
            total_liabilities=60000,
            total_equity=40000
        )
        db_session.add(statement)
        db_session.commit()

        # Create financial ratio
        ratio = FinancialRatio(
            financial_statement_id=statement.id,
            company_id=company.id,
            ratio_category="liquidity",
            ratio_name="current_ratio",
            ratio_value=1.67,  # 100000/60000
            calculation_formula="total_assets/total_liabilities"
        )
        db_session.add(ratio)
        db_session.commit()

        # Verify
        assert ratio.id is not None
        assert ratio.ratio_value == 1.67

    def test_analysis_job_creation(self, db_session: Session, sample_company_data):
        """Test analysis job model"""
        # Create company
        company = Company(**sample_company_data)
        db_session.add(company)
        db_session.commit()

        # Create analysis job
        job = AnalysisJob(
            job_id="test-job-123",
            job_type="FORENSIC",
            company_id=company.id,
            period_start=datetime(2023, 1, 1),
            period_end=datetime(2023, 12, 31),
            analysis_type="comprehensive"
        )
        db_session.add(job)
        db_session.commit()

        # Verify
        assert job.id is not None
        assert job.status.value == "created"
        assert job.job_id == "test-job-123"

    def test_forensic_analysis_creation(self, db_session: Session, sample_company_data):
        """Test forensic analysis model"""
        # Create company and job
        company = Company(**sample_company_data)
        db_session.add(company)
        db_session.commit()

        job = AnalysisJob(
            job_id="forensic-job-456",
            job_type="FORENSIC",
            company_id=company.id,
            period_start=datetime(2023, 1, 1),
            period_end=datetime(2023, 12, 31)
        )
        db_session.add(job)
        db_session.commit()

        # Create forensic analysis
        analysis = ForensicAnalysis(
            job_id=job.id,
            company_id=company.id,
            analysis_start_date=datetime(2023, 1, 1),
            analysis_end_date=datetime(2023, 12, 31),
            overall_risk_score=75.5,
            manipulation_probability=0.3,
            financial_health_grade="B+"
        )
        db_session.add(analysis)
        db_session.commit()

        # Verify
        assert analysis.id is not None
        assert analysis.overall_risk_score == 75.5

    def test_risk_score_creation(self, db_session: Session, sample_company_data):
        """Test risk score model"""
        # Create company
        company = Company(**sample_company_data)
        db_session.add(company)
        db_session.commit()

        # Create risk score
        risk_score = RiskScore(
            company_id=company.id,
            scoring_date=datetime.now(),
            period_start=datetime(2023, 1, 1),
            period_end=datetime(2023, 12, 31),
            overall_score=80.5,
            overall_level="MEDIUM",
            financial_health_score=85.0,
            earnings_quality_score=75.0,
            governance_score=82.0
        )
        db_session.add(risk_score)
        db_session.commit()

        # Verify
        assert risk_score.id is not None
        assert risk_score.overall_score == 80.5

    def test_chat_session_creation(self, db_session: Session, sample_company_data):
        """Test chat session model"""
        # Create company
        company = Company(**sample_company_data)
        db_session.add(company)
        db_session.commit()

        # Create chat session
        session = ChatSession(
            session_id="chat-123",
            company_id=company.id,
            agent_type="FORENSIC",
            session_title="Risk Analysis Discussion",
            user_id="test_user_123"
        )
        db_session.add(session)
        db_session.commit()

        # Verify
        assert session.id is not None
        assert session.agent_type.value == "forensic"


class TestDatabaseConnection:
    """Test database connection and operations"""

    def test_database_connection(self, test_database):
        """Test database connectivity"""
        # Test basic connection
        from sqlalchemy import text

        with test_database.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.scalar() == 1

    def test_connection_pooling(self):
        """Test connection pooling configuration"""
        client = PostgreSQLClient()
        conn_info = client.get_connection_info()

        assert "pool_size" in conn_info
        assert "checked_in" in conn_info
        assert "checked_out" in conn_info

    def test_transaction_rollback(self, db_session: Session):
        """Test transaction rollback on error"""
        # Create company
        company = Company(
            cin="L99999MH1994PLC000001",
            name="Test Company Ltd",
            sector="Technology"
        )

        # Simulate error condition
        db_session.add(company)

        # Force rollback by raising exception
        try:
            raise ValueError("Test error")
        except ValueError:
            db_session.rollback()
            raise

        # Verify rollback - company should not exist
        result = db_session.query(Company).filter_by(cin="L99999MH1994PLC000001").first()
        assert result is None

    def test_bulk_operations(self, db_session: Session):
        """Test bulk insert operations"""
        # Create multiple companies
        companies_data = [
            {"cin": f"L99999MH1994PLC{i"06d"}", "name": f"Company {i}", "sector": "Tech"}
            for i in range(1, 11)
        ]

        companies = [Company(**data) for data in companies_data]
        db_session.add_all(companies)
        db_session.commit()

        # Verify bulk insert
        count = db_session.query(Company).count()
        assert count >= 10  # At least our test companies

    def test_query_performance(self, db_session: Session):
        """Test query performance with indexes"""
        import time

        # Create test data
        company = Company(
            cin="L99999MH1994PLC999999",
            name="Performance Test Company",
            sector="Technology",
            industry="Software"
        )
        db_session.add(company)
        db_session.commit()

        # Test indexed query performance
        start_time = time.time()
        result = db_session.query(Company).filter_by(sector="Technology").first()
        query_time = time.time() - start_time

        assert result is not None
        assert query_time < 0.1  # Should be fast due to index

    def test_jsonb_operations(self, db_session: Session):
        """Test JSONB field operations"""
        # Create company with JSONB data
        company = Company(
            cin="L99999MH1994PLC888888",
            name="JSONB Test Company",
            sector="Technology",
            api_response={"test": "data", "numbers": [1, 2, 3]}
        )
        db_session.add(company)
        db_session.commit()

        # Query JSONB field
        result = db_session.query(Company).filter_by(cin="L99999MH1994PLC888888").first()
        assert result.api_response["test"] == "data"
        assert result.api_response["numbers"] == [1, 2, 3]


class TestDataValidation:
    """Test data validation and constraints"""

    def test_balance_sheet_validation(self, db_session: Session, sample_company_data):
        """Test balance sheet equation validation"""
        # Create company
        company = Company(**sample_company_data)
        db_session.add(company)
        db_session.commit()

        # Create valid balance sheet
        statement = FinancialStatement(
            company_id=company.id,
            statement_type=StatementType.BALANCE_SHEET,
            period_type=ReportingPeriod.ANNUAL,
            fiscal_year=2023,
            period_end=datetime(2024, 3, 31),
            total_assets=100000,
            total_liabilities=60000,
            total_equity=40000  # Assets = Liabilities + Equity ✓
        )
        db_session.add(statement)
        db_session.commit()

        # Test validation logic (would be in the agent)
        from src.agents.forensic.agent1_ingestion import DataIngestionAgent
        agent = DataIngestionAgent()

        is_valid, errors = agent.balance_sheet_validator({
            "total_assets": 100000,
            "total_liabilities": 60000,
            "total_equity": 40000
        })

        assert is_valid == True
        assert len(errors) == 0

    def test_invalid_balance_sheet(self, db_session: Session, sample_company_data):
        """Test invalid balance sheet detection"""
        from src.agents.forensic.agent1_ingestion import DataIngestionAgent
        agent = DataIngestionAgent()

        # Test invalid balance sheet
        is_valid, errors = agent.balance_sheet_validator({
            "total_assets": 100000,
            "total_liabilities": 60000,
            "total_equity": 50000  # Assets != Liabilities + Equity ✗
        })

        assert is_valid == False
        assert len(errors) > 0
        assert "equation violation" in errors[0].lower()

    def test_date_parsing(self, db_session: Session, sample_company_data):
        """Test date parsing utilities"""
        from src.agents.forensic.agent1_ingestion import DataIngestionAgent
        agent = DataIngestionAgent()

        # Test various date formats
        test_dates = [
            ("2023-03-31", datetime(2023, 3, 31)),
            ("31/03/2023", datetime(2023, 3, 31)),
            ("2023-12-31", datetime(2023, 12, 31))
        ]

        for date_str, expected in test_dates:
            parsed = agent._parse_date(date_str)
            assert parsed == expected

    def test_currency_conversion(self, db_session: Session, sample_company_data):
        """Test currency conversion utilities"""
        from src.agents.forensic.agent1_ingestion import DataIngestionAgent
        agent = DataIngestionAgent()

        # Test conversion to lakhs
        assert agent._safe_convert_to_lakhs(100000000) == 1000  # 10 crores = 1000 lakhs
        assert agent._safe_convert_to_lakhs("100,000,000") == 1000
        assert agent._safe_convert_to_lakhs(None) is None
        assert agent._safe_convert_to_lakhs("invalid") is None
