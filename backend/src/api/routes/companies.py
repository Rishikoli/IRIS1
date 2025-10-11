"""
Project IRIS - Company Management API Routes
CRUD operations for company data
"""

import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime

from src.database.connection import get_db_client
from src.api.schemas.models import (
    CompanyCreate, CompanyResponse, FinancialStatementResponse,
    SuccessResponse, ErrorResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/companies",
    tags=["companies"],
    responses={404: {"model": ErrorResponse}}
)


@router.post("", response_model=SuccessResponse)
async def create_company(company: CompanyCreate):
    """Create a new company"""
    try:
        db_client = get_db_client()

        # Check if company already exists
        existing = db_client.execute_query(
            "SELECT company_id FROM companies WHERE company_id = :company_id",
            {"company_id": company.company_id}
        )

        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Company {company.company_id} already exists"
            )

        # Insert new company
        insert_query = """
        INSERT INTO companies (company_id, name, symbol, exchange, isin, sector, industry)
        VALUES (:company_id, :name, :symbol, :exchange, :isin, :sector, :industry)
        """

        db_client.execute_query(insert_query, company.dict())

        return SuccessResponse(
            success=True,
            message=f"Company {company.company_id} created successfully",
            data={"company_id": company.company_id}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating company: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create company: {str(e)}")


@router.get("", response_model=List[CompanyResponse])
async def list_companies(
    exchange: Optional[str] = Query(None, description="Filter by exchange (NSE, BSE, BOTH)"),
    sector: Optional[str] = Query(None, description="Filter by sector"),
    limit: int = Query(100, ge=1, le=1000, description="Number of companies to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """List companies with optional filtering"""
    try:
        db_client = get_db_client()

        # Build query with filters
        where_conditions = []
        params = {"limit": limit, "offset": offset}

        if exchange:
            where_conditions.append("exchange = :exchange")
            params["exchange"] = exchange

        if sector:
            where_conditions.append("sector ILIKE :sector")
            params["sector"] = f"%{sector}%"

        where_clause = " AND ".join(where_conditions)
        if where_clause:
            where_clause = f"WHERE {where_clause}"

        query = f"""
        SELECT company_id, name, symbol, exchange, isin, sector, industry,
               market_cap, fiscal_year_end, currency, website, description,
               created_at, updated_at
        FROM companies
        {where_clause}
        ORDER BY name
        LIMIT :limit OFFSET :offset
        """

        companies = db_client.execute_query(query, params)

        return [
            CompanyResponse(
                company_id=company["company_id"],
                name=company["name"],
                symbol=company["symbol"],
                exchange=company["exchange"],
                isin=company["isin"],
                sector=company["sector"],
                industry=company["industry"],
                market_cap=company.get("market_cap"),
                fiscal_year_end=company.get("fiscal_year_end"),
                currency=company.get("currency", "INR"),
                website=company.get("website"),
                description=company.get("description"),
                created_at=company["created_at"],
                updated_at=company["updated_at"]
            )
            for company in companies
        ]

    except Exception as e:
        logger.error(f"Error listing companies: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list companies: {str(e)}")


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(company_id: str):
    """Get company details by ID"""
    try:
        db_client = get_db_client()

        query = """
        SELECT company_id, name, symbol, exchange, isin, sector, industry,
               market_cap, fiscal_year_end, currency, website, description,
               created_at, updated_at
        FROM companies
        WHERE company_id = :company_id
        """

        company = db_client.execute_query(query, {"company_id": company_id})

        if not company:
            raise HTTPException(status_code=404, detail=f"Company {company_id} not found")

        company = company[0]
        return CompanyResponse(
            company_id=company["company_id"],
            name=company["name"],
            symbol=company["symbol"],
            exchange=company["exchange"],
            isin=company["isin"],
            sector=company["sector"],
            industry=company["industry"],
            market_cap=company.get("market_cap"),
            fiscal_year_end=company.get("fiscal_year_end"),
            currency=company.get("currency", "INR"),
            website=company.get("website"),
            description=company.get("description"),
            created_at=company["created_at"],
            updated_at=company["updated_at"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting company {company_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get company: {str(e)}")


@router.get("/{company_id}/financials", response_model=List[FinancialStatementResponse])
async def get_company_financials(
    company_id: str,
    statement_type: Optional[str] = Query(None, description="Filter by statement type"),
    limit: int = Query(10, ge=1, le=100, description="Number of statements to return")
):
    """Get financial statements for a company"""
    try:
        db_client = get_db_client()

        # Build query with filters
        where_conditions = ["company_id = :company_id"]
        params = {"company_id": company_id, "limit": limit}

        if statement_type:
            where_conditions.append("statement_type = :statement_type")
            params["statement_type"] = statement_type

        where_clause = " AND ".join(where_conditions)

        query = f"""
        SELECT id, company_id, period, statement_type, fiscal_year, period_type,
               currency, data, source, filing_url, filing_date, created_at, updated_at
        FROM financial_statements
        WHERE {where_clause}
        ORDER BY period DESC
        LIMIT :limit
        """

        statements = db_client.execute_query(query, params)

        return [
            FinancialStatementResponse(
                id=stmt["id"],
                company_id=stmt["company_id"],
                period=stmt["period"],
                statement_type=stmt["statement_type"],
                fiscal_year=stmt.get("fiscal_year"),
                period_type=stmt.get("period_type"),
                currency=stmt.get("currency", "INR"),
                data=stmt["data"],
                source=stmt.get("source", "FMP_API"),
                filing_url=stmt.get("filing_url"),
                filing_date=stmt.get("filing_date"),
                created_at=stmt["created_at"],
                updated_at=stmt["updated_at"]
            )
            for stmt in statements
        ]

    except Exception as e:
        logger.error(f"Error getting financials for {company_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get financial statements: {str(e)}")


@router.post("/{company_id}/financials", response_model=SuccessResponse)
async def add_financial_statement(company_id: str, statement: FinancialStatementResponse):
    """Add a financial statement for a company"""
    try:
        db_client = get_db_client()

        # Verify company exists
        company_check = db_client.execute_query(
            "SELECT company_id FROM companies WHERE company_id = :company_id",
            {"company_id": company_id}
        )

        if not company_check:
            raise HTTPException(status_code=404, detail=f"Company {company_id} not found")

        # Insert financial statement
        insert_query = """
        INSERT INTO financial_statements
        (company_id, period, statement_type, fiscal_year, period_type, currency, data, source, filing_url, filing_date)
        VALUES (:company_id, :period, :statement_type, :fiscal_year, :period_type, :currency, :data, :source, :filing_url, :filing_date)
        """

        db_client.execute_query(insert_query, {
            **statement.dict(),
            "company_id": company_id
        })

        return SuccessResponse(
            success=True,
            message=f"Financial statement added for {company_id}",
            data={"company_id": company_id, "period": statement.period.isoformat()}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding financial statement for {company_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add financial statement: {str(e)}")
