"""
Project IRIS - Agent 1: Data Ingestion Agent (Forensic)
Handles data ingestion from multiple sources with normalization and validation
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import json
import asyncio
from decimal import Decimal, InvalidOperation
import re

from api_clients import FMPAPIClient, NSEClient, BSEClient
from models import Company, FinancialStatement, StatementType, ReportingPeriod
from database.connection import get_db_client
from config import settings

logger = logging.getLogger(__name__)


class DataIngestionAgent:
    """Agent 1: Data ingestion from external APIs with normalization"""
    
    def __init__(self):
        self.fmp_client = FMPAPIClient()
        self.nse_client = NSEClient()
        self.bse_client = BSEClient()
        self.db_client = get_db_client()
        
    def search_company(self, query: str) -> List[Dict[str, Any]]:
        """Search for companies across multiple data sources"""
        try:
            logger.info(f"Searching for company: {query}")
            results = []
            
            # Search in FMP (international/US markets)
            try:
                fmp_results = self.fmp_client.search_company(query, limit=5)
                for result in fmp_results:
                    results.append({
                        "source": "fmp",
                        "symbol": result.get("symbol", ""),
                        "name": result.get("name", ""),
                        "exchange": result.get("exchangeShortName", ""),
                        "currency": result.get("currency", "USD"),
                        "country": result.get("country", ""),
                        "sector": result.get("sector", ""),
                        "industry": result.get("industry", ""),
                        "market_cap": result.get("marketCap", 0),
                        "raw_data": result
                    })
            except Exception as e:
                logger.error(f"FMP search failed: {e}")
            
            # Search in NSE (Indian market)
            try:
                # Try as NSE symbol
                nse_result = self.nse_client.search_company_by_symbol(query)
                if nse_result:
                    results.append({
                        "source": "nse",
                        "symbol": nse_result.get("symbol", ""),
                        "name": nse_result.get("company_name", ""),
                        "exchange": "NSE",
                        "currency": "INR",
                        "country": "India",
                        "sector": nse_result.get("sector", ""),
                        "industry": nse_result.get("industry", ""),
                        "isin": nse_result.get("isin", ""),
                        "market_cap": nse_result.get("market_cap", 0),
                        "raw_data": nse_result
                    })
            except Exception as e:
                logger.error(f"NSE search failed: {e}")
            
            # Search in BSE (Indian market)
            try:
                # Try as BSE scrip code or search by name
                if query.isdigit():
                    bse_result = self.bse_client.search_company_by_code(query)
                    if bse_result:
                        results.append({
                            "source": "bse",
                            "symbol": bse_result.get("scrip_code", ""),
                            "name": bse_result.get("company_name", ""),
                            "exchange": "BSE",
                            "currency": "INR",
                            "country": "India",
                            "industry": bse_result.get("industry", ""),
                            "raw_data": bse_result
                        })
                else:
                    bse_results = self.bse_client.search_company_by_name(query)
                    for result in bse_results[:3]:  # Limit to top 3
                        results.append({
                            "source": "bse",
                            "symbol": result.get("scrip_code", ""),
                            "name": result.get("company_name", ""),
                            "exchange": "BSE",
                            "currency": "INR",
                            "country": "India",
                            "group": result.get("group", ""),
                            "raw_data": result
                        })
            except Exception as e:
                logger.error(f"BSE search failed: {e}")
            
            logger.info(f"Found {len(results)} companies for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Company search failed for query '{query}': {e}")
            return []
    
    def get_financials(self, company_id: str, source: str, periods: int = 5) -> Dict[str, Any]:
        """Get financial data from specified source"""
        try:
            logger.info(f"Fetching financials for company {company_id} from {source}")
            
            if source == "fmp":
                return self.fmp_client.get_comprehensive_financials(company_id, periods)
            elif source == "nse":
                return self.nse_client.get_comprehensive_filings(company_id)
            elif source == "bse":
                return self.bse_client.get_comprehensive_filings(company_id)
            else:
                raise ValueError(f"Unsupported data source: {source}")
                
        except Exception as e:
            logger.error(f"Failed to get financials for {company_id} from {source}: {e}")
            return {"error": str(e), "company_id": company_id, "source": source}
    
    def normalize_financial_statements(self, raw_data: Dict[str, Any], source: str) -> List[Dict[str, Any]]:
        """Normalize financial statements from different sources to standard schema"""
        try:
            logger.info(f"Normalizing financial statements from {source}")
            normalized_statements = []
            
            if source == "fmp":
                normalized_statements.extend(self._normalize_fmp_statements(raw_data))
            elif source in ["nse", "bse"]:
                normalized_statements.extend(self._normalize_indian_statements(raw_data, source))
            
            logger.info(f"Normalized {len(normalized_statements)} financial statements")
            return normalized_statements
            
        except Exception as e:
            logger.error(f"Failed to normalize financial statements from {source}: {e}")
            return []
    
    def _normalize_fmp_statements(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Normalize FMP financial statements"""
        statements = []
        
        try:
            symbol = data.get("symbol", "")
            
            # Normalize income statements
            for period_type in ["annual", "quarterly"]:
                income_data = data.get("income_statement", {}).get(period_type, [])
                for statement in income_data:
                    normalized = {
                        "symbol": symbol,
                        "statement_type": StatementType.INCOME_STATEMENT,
                        "period_type": ReportingPeriod.ANNUAL if period_type == "annual" else ReportingPeriod.QUARTERLY,
                        "period_end": self._parse_date(statement.get("date")),
                        "currency": "USD",
                        "units": "dollars",
                        
                        # Income statement items (convert to lakhs for consistency)
                        "total_revenue": self._safe_convert_to_lakhs(statement.get("revenue")),
                        "operating_revenue": self._safe_convert_to_lakhs(statement.get("revenue")),
                        "cost_of_goods_sold": self._safe_convert_to_lakhs(statement.get("costOfRevenue")),
                        "gross_profit": self._safe_convert_to_lakhs(statement.get("grossProfit")),
                        "operating_expenses": self._safe_convert_to_lakhs(statement.get("operatingExpenses")),
                        "operating_profit": self._safe_convert_to_lakhs(statement.get("operatingIncome")),
                        "ebitda": self._safe_convert_to_lakhs(statement.get("ebitda")),
                        "ebit": self._safe_convert_to_lakhs(statement.get("ebit")),
                        "interest_expense": self._safe_convert_to_lakhs(statement.get("interestExpense")),
                        "profit_before_tax": self._safe_convert_to_lakhs(statement.get("incomeBeforeTax")),
                        "tax_expense": self._safe_convert_to_lakhs(statement.get("incomeTaxExpense")),
                        "net_profit": self._safe_convert_to_lakhs(statement.get("netIncome")),
                        "earnings_per_share": statement.get("eps"),
                        
                        # Metadata
                        "source": "fmp",
                        "raw_data": statement
                    }
                    statements.append(normalized)
            
            # Normalize balance sheets
            for period_type in ["annual", "quarterly"]:
                balance_data = data.get("balance_sheet", {}).get(period_type, [])
                for statement in balance_data:
                    normalized = {
                        "symbol": symbol,
                        "statement_type": StatementType.BALANCE_SHEET,
                        "period_type": ReportingPeriod.ANNUAL if period_type == "annual" else ReportingPeriod.QUARTERLY,
                        "period_end": self._parse_date(statement.get("date")),
                        "currency": "USD",
                        "units": "dollars",
                        
                        # Balance sheet items
                        "total_assets": self._safe_convert_to_lakhs(statement.get("totalAssets")),
                        "current_assets": self._safe_convert_to_lakhs(statement.get("totalCurrentAssets")),
                        "non_current_assets": self._safe_convert_to_lakhs(statement.get("totalNonCurrentAssets")),
                        "cash_and_equivalents": self._safe_convert_to_lakhs(statement.get("cashAndCashEquivalents")),
                        "inventory": self._safe_convert_to_lakhs(statement.get("inventory")),
                        "trade_receivables": self._safe_convert_to_lakhs(statement.get("netReceivables")),
                        
                        "total_liabilities": self._safe_convert_to_lakhs(statement.get("totalLiabilities")),
                        "current_liabilities": self._safe_convert_to_lakhs(statement.get("totalCurrentLiabilities")),
                        "non_current_liabilities": self._safe_convert_to_lakhs(statement.get("totalNonCurrentLiabilities")),
                        "total_debt": self._safe_convert_to_lakhs(statement.get("totalDebt")),
                        "short_term_debt": self._safe_convert_to_lakhs(statement.get("shortTermDebt")),
                        "long_term_debt": self._safe_convert_to_lakhs(statement.get("longTermDebt")),
                        
                        "total_equity": self._safe_convert_to_lakhs(statement.get("totalStockholdersEquity")),
                        "share_capital": self._safe_convert_to_lakhs(statement.get("commonStock")),
                        "reserves_surplus": self._safe_convert_to_lakhs(statement.get("retainedEarnings")),
                        
                        # Metadata
                        "source": "fmp",
                        "raw_data": statement
                    }
                    statements.append(normalized)
            
            # Normalize cash flow statements
            for period_type in ["annual", "quarterly"]:
                cashflow_data = data.get("cash_flow", {}).get(period_type, [])
                for statement in cashflow_data:
                    normalized = {
                        "symbol": symbol,
                        "statement_type": StatementType.CASH_FLOW,
                        "period_type": ReportingPeriod.ANNUAL if period_type == "annual" else ReportingPeriod.QUARTERLY,
                        "period_end": self._parse_date(statement.get("date")),
                        "currency": "USD",
                        "units": "dollars",
                        
                        # Cash flow items
                        "operating_cash_flow": self._safe_convert_to_lakhs(statement.get("netCashProvidedByOperatingActivities")),
                        "investing_cash_flow": self._safe_convert_to_lakhs(statement.get("netCashUsedForInvestingActivites")),
                        "financing_cash_flow": self._safe_convert_to_lakhs(statement.get("netCashUsedProvidedByFinancingActivities")),
                        "net_cash_flow": self._safe_convert_to_lakhs(statement.get("netChangeInCash")),
                        "free_cash_flow": self._safe_convert_to_lakhs(statement.get("freeCashFlow")),
                        
                        # Metadata
                        "source": "fmp",
                        "raw_data": statement
                    }
                    statements.append(normalized)
            
        except Exception as e:
            logger.error(f"Error normalizing FMP statements: {e}")
        
        return statements
    
    def _normalize_indian_statements(self, data: Dict[str, Any], source: str) -> List[Dict[str, Any]]:
        """Normalize Indian market statements (NSE/BSE)"""
        statements = []
        
        try:
            symbol = data.get("symbol", "") if source == "nse" else data.get("scrip_code", "")
            
            # Process financial results
            financial_results = data.get("financial_results", [])
            for result in financial_results:
                # This would need to be enhanced based on actual NSE/BSE data format
                # For now, create placeholder structure
                normalized = {
                    "symbol": symbol,
                    "statement_type": StatementType.INCOME_STATEMENT,  # Assume income statement
                    "period_type": self._determine_period_type(result.get("period", "")),
                    "period_end": self._parse_date(result.get("result_date")),
                    "currency": "INR",
                    "units": "lakhs",
                    "filing_date": self._parse_date(result.get("result_date")),
                    "document_url": result.get("attachment", ""),
                    "source": source,
                    "raw_data": result
                }
                statements.append(normalized)
        
        except Exception as e:
            logger.error(f"Error normalizing {source} statements: {e}")
        
        return statements
    
    def _safe_convert_to_lakhs(self, value: Any) -> Optional[int]:
        """Safely convert financial values to lakhs (Indian numbering system)"""
        try:
            if value is None or value == "":
                return None
            
            # Convert to float first
            if isinstance(value, str):
                # Remove commas and other formatting
                clean_value = re.sub(r'[,$%]', '', value)
                if clean_value == "" or clean_value == "-":
                    return None
                value = float(clean_value)
            
            # Convert to lakhs (divide by 100,000)
            lakhs_value = int(value / 100000) if value != 0 else 0
            return lakhs_value
            
        except (ValueError, TypeError, InvalidOperation):
            return None
    
    def _parse_date(self, date_str: Any) -> Optional[datetime]:
        """Parse date string to datetime object"""
        if not date_str:
            return None
        
        try:
            if isinstance(date_str, datetime):
                return date_str
            
            # Try different date formats
            date_formats = [
                "%Y-%m-%d",
                "%d/%m/%Y",
                "%m/%d/%Y",
                "%Y-%m-%d %H:%M:%S",
                "%d-%m-%Y"
            ]
            
            for fmt in date_formats:
                try:
                    return datetime.strptime(str(date_str), fmt)
                except ValueError:
                    continue
            
            logger.warning(f"Could not parse date: {date_str}")
            return None
            
        except Exception as e:
            logger.error(f"Error parsing date {date_str}: {e}")
            return None
    
    def _determine_period_type(self, period_str: str) -> ReportingPeriod:
        """Determine reporting period type from string"""
        period_lower = str(period_str).lower()
        
        if "quarter" in period_lower or "q1" in period_lower or "q2" in period_lower or "q3" in period_lower or "q4" in period_lower:
            return ReportingPeriod.QUARTERLY
        elif "half" in period_lower or "h1" in period_lower or "h2" in period_lower:
            return ReportingPeriod.HALF_YEARLY
        else:
            return ReportingPeriod.ANNUAL
    
    def balance_sheet_validator(self, statement: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate balance sheet equation: Assets = Liabilities + Equity"""
        errors = []
        
        try:
            total_assets = statement.get("total_assets", 0) or 0
            total_liabilities = statement.get("total_liabilities", 0) or 0
            total_equity = statement.get("total_equity", 0) or 0
            
            liabilities_plus_equity = total_liabilities + total_equity
            
            # Allow for small rounding differences (1% tolerance)
            tolerance = max(abs(total_assets * 0.01), 1)  # 1% or minimum 1 lakh
            
            if abs(total_assets - liabilities_plus_equity) > tolerance:
                errors.append(
                    f"Balance sheet equation violation: Assets ({total_assets}) != "
                    f"Liabilities ({total_liabilities}) + Equity ({total_equity}) = {liabilities_plus_equity}. "
                    f"Difference: {abs(total_assets - liabilities_plus_equity)}"
                )
            
            # Additional validations
            if total_assets < 0:
                errors.append("Total assets cannot be negative")
            
            if total_equity < 0:
                errors.append("Total equity is negative - company may be insolvent")
            
            current_assets = statement.get("current_assets", 0) or 0
            non_current_assets = statement.get("non_current_assets", 0) or 0
            
            if abs((current_assets + non_current_assets) - total_assets) > tolerance:
                errors.append("Current + Non-current assets do not equal total assets")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"Error validating balance sheet: {e}")
            return False, errors
    
    def ingest_company_data(self, company_search_result: Dict[str, Any]) -> Optional[str]:
        """Ingest and store company data in database"""
        try:
            logger.info(f"Ingesting company data: {company_search_result.get('name', 'Unknown')}")
            
            # Get comprehensive financial data
            source = company_search_result.get("source")
            symbol = company_search_result.get("symbol")
            
            if not source or not symbol:
                logger.error("Missing source or symbol in company data")
                return None
            
            # Fetch financial data
            financial_data = self.get_financials(symbol, source)
            
            if "error" in financial_data:
                logger.error(f"Failed to fetch financial data: {financial_data['error']}")
                return None
            
            # Normalize financial statements
            normalized_statements = self.normalize_financial_statements(financial_data, source)
            
            # Store in database (this would be implemented based on your database models)
            # For now, return a placeholder job ID
            job_id = f"job_{symbol}_{int(datetime.now().timestamp())}"
            
            logger.info(f"Successfully ingested data for {symbol}, job_id: {job_id}")
            return job_id
            
        except Exception as e:
            logger.error(f"Failed to ingest company data: {e}")
            return None
