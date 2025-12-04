"""
Project IRIS - Agent 1: Data Ingestion Agent (Forensic)
Handles data ingestion from multiple sources with normalization and validation
"""

import logging
import yfinance as yf
import pandas as pd
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import json
import asyncio
from decimal import Decimal, InvalidOperation
import re
import os
import tempfile
from pathlib import Path

from src.api_clients import FMPAPIClient, NSEClient, BSEClient
from src.models import Company, FinancialStatement, StatementType, ReportingPeriod
from src.database.connection import get_db_client
from src.config import settings
from src.utils.ocr_processor import OCRProcessor
from src.utils.document_scraper import DocumentScraper

logger = logging.getLogger(__name__)


class DataIngestionAgent:
    """Agent 1: Data ingestion from external APIs with normalization"""
    
    def __init__(self):
        self.fmp_client = FMPAPIClient()
        self.nse_client = NSEClient()
        self.bse_client = BSEClient()
        self.db_client = get_db_client()
        self.ocr_processor = OCRProcessor()
        self.document_scraper = DocumentScraper()
        
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
            
            # Search in Yahoo Finance (global markets)
            try:
                # Try to get ticker data from Yahoo Finance
                ticker = yf.Ticker(query)
                info = ticker.info
                
                if info and info.get("symbol"):
                    # Convert market cap from Yahoo Finance format
                    market_cap = info.get("marketCap", 0)
                    if market_cap:
                        # Convert to appropriate format (Yahoo Finance gives raw numbers)
                        market_cap_display = self._format_market_cap(market_cap)
                    else:
                        market_cap_display = 0
                    
                    results.append({
                        "source": "yahoo",
                        "symbol": info.get("symbol", ""),
                        "name": info.get("longName", info.get("shortName", "")),
                        "exchange": info.get("exchange", ""),
                        "currency": info.get("currency", "USD"),
                        "country": info.get("country", ""),
                        "sector": info.get("sector", ""),
                        "industry": info.get("industry", ""),
                        "market_cap": market_cap_display,
                        "raw_data": info
                    })
            except Exception as e:
                logger.error(f"Yahoo Finance search failed: {e}")
            
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
            elif source == "yahoo":
                return self._get_yahoo_financials(company_id, periods)
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
            elif source == "yahoo":
                normalized_statements.extend(self._normalize_yahoo_statements(raw_data))
            
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
    
    def _get_yahoo_financials(self, symbol: str, periods: int = 5) -> Dict[str, Any]:
        """Get comprehensive financial data from Yahoo Finance"""
        try:
            logger.info(f"Fetching Yahoo Finance data for {symbol}")

            ticker = yf.Ticker(symbol)

            # Get quarterly and annual data
            quarterly_income = ticker.quarterly_financials
            quarterly_balance = ticker.quarterly_balance_sheet
            annual_income = ticker.financials
            annual_balance = ticker.balance_sheet

            # Get additional info
            info = ticker.info

            financial_data = {
                "symbol": symbol,
                "name": info.get("longName", info.get("shortName", "")) if info else "",
                "sector": info.get("sector", "") if info else "",
                "industry": info.get("industry", "") if info else "",
                "currency": info.get("currency", "USD") if info else "USD",
                "quarterly_income_statement": self._convert_yahoo_dataframe(quarterly_income, periods) if quarterly_income is not None else [],
                "quarterly_balance_sheet": self._convert_yahoo_dataframe(quarterly_balance, periods) if quarterly_balance is not None else [],
                "annual_income_statement": self._convert_yahoo_dataframe(annual_income, min(periods, 3)) if annual_income is not None else [],
                "annual_balance_sheet": self._convert_yahoo_dataframe(annual_balance, min(periods, 3)) if annual_balance is not None else [],
                "source": "yahoo"
            }

            logger.info(f"Successfully fetched Yahoo Finance data for {symbol}")
            return financial_data

        except Exception as e:
            logger.error(f"Failed to get Yahoo Finance data for {symbol}: {e}")
            return {"error": str(e), "symbol": symbol, "source": "yahoo"}

    def _convert_yahoo_dataframe(self, df: pd.DataFrame, max_periods: int) -> List[Dict[str, Any]]:
        """Convert Yahoo Finance DataFrame to list of dictionaries"""
        if df is None or df.empty:
            return []

        statements = []
        # Limit to requested periods
        columns_to_process = min(max_periods, len(df.columns))

        for i in range(columns_to_process):
            try:
                # Get column data
                col_data = df.iloc[:, i]
                col_name = str(df.columns[i].date()) if hasattr(df.columns[i], 'date') else str(df.columns[i])

                # Convert to dictionary, handling NaN values
                statement_dict = {}
                for idx, value in col_data.items():
                    if pd.isna(value) or value is None:
                        statement_dict[str(idx)] = None
                    else:
                        try:
                            # Convert to appropriate numeric format
                            if isinstance(value, (int, float)):
                                statement_dict[str(idx)] = float(value)
                            else:
                                statement_dict[str(idx)] = str(value)
                        except (ValueError, TypeError):
                            statement_dict[str(idx)] = str(value)

                statement_dict["period_end"] = col_name
                statements.append(statement_dict)

            except Exception as e:
                logger.warning(f"Error processing Yahoo Finance column {i}: {e}")
                continue

        return statements

    def _normalize_yahoo_statements(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Normalize Yahoo Finance financial statements with enhanced field mapping"""
        statements = []

        try:
            symbol = data.get("symbol", "")

            # Enhanced Yahoo Finance to Agent field mapping (from Agent 2)
            yahoo_to_agent_mapping = {
                'income_statement': {
                    # Revenue fields
                    'Total Revenue': 'total_revenue',
                    'TotalRevenue': 'total_revenue',

                    # Profit fields
                    'Net Income': 'net_profit',
                    'NetIncome': 'net_profit',
                    'Net Income From Continuing And Discontinued Operation': 'net_profit',

                    # Cost fields
                    'Cost Of Revenue': 'cost_of_revenue',
                    'CostOfRevenue': 'cost_of_revenue',

                    # Additional profit metrics
                    'Gross Profit': 'gross_profit',
                    'GrossProfit': 'gross_profit',
                    'Operating Income': 'operating_income',
                    'OperatingIncome': 'operating_income',
                    'EBITDA': 'ebitda',
                    'EBIT': 'ebit',

                    # Expense fields
                    'Interest Expense': 'interest_expense',
                    'InterestExpense': 'interest_expense',
                    'Income Tax Expense': 'tax_expense',
                    'Tax Expense': 'tax_expense',
                },
                'balance_sheet': {
                    # Asset fields
                    'Total Assets': 'total_assets',
                    'TotalAssets': 'total_assets',

                    # Liability fields
                    'Total Liabilities Net Minority Interest': 'total_liabilities',
                    'TotalLiabilitiesNetMinorityInterest': 'total_liabilities',

                    # Equity fields
                    'Stockholders Equity': 'total_equity',
                    'StockholdersEquity': 'total_equity',

                    # Current fields
                    'Current Assets': 'current_assets',
                    'CurrentAssets': 'current_assets',
                    'Current Liabilities': 'current_liabilities',
                    'CurrentLiabilities': 'current_liabilities',

                    # Cash fields
                    'Cash And Cash Equivalents': 'cash_and_equivalents',
                    'CashAndCashEquivalents': 'cash_and_equivalents',
                }
            }

            # Process quarterly income statements
            quarterly_income_data = data.get("quarterly_income_statement", [])
            for stmt_data in quarterly_income_data:
                normalized = self._normalize_yahoo_statement_data(
                    stmt_data, symbol, StatementType.INCOME_STATEMENT,
                    ReportingPeriod.QUARTERLY, yahoo_to_agent_mapping['income_statement']
                )
                if normalized:
                    statements.append(normalized)

            # Process quarterly balance sheets
            quarterly_balance_data = data.get("quarterly_balance_sheet", [])
            for stmt_data in quarterly_balance_data:
                normalized = self._normalize_yahoo_statement_data(
                    stmt_data, symbol, StatementType.BALANCE_SHEET,
                    ReportingPeriod.QUARTERLY, yahoo_to_agent_mapping['balance_sheet']
                )
                if normalized:
                    statements.append(normalized)

            # Process annual income statements
            annual_income_data = data.get("annual_income_statement", [])
            for stmt_data in annual_income_data:
                normalized = self._normalize_yahoo_statement_data(
                    stmt_data, symbol, StatementType.INCOME_STATEMENT,
                    ReportingPeriod.ANNUAL, yahoo_to_agent_mapping['income_statement']
                )
                if normalized:
                    statements.append(normalized)

            # Process annual balance sheets
            annual_balance_data = data.get("annual_balance_sheet", [])
            for stmt_data in annual_balance_data:
                normalized = self._normalize_yahoo_statement_data(
                    stmt_data, symbol, StatementType.BALANCE_SHEET,
                    ReportingPeriod.ANNUAL, yahoo_to_agent_mapping['balance_sheet']
                )
                if normalized:
                    statements.append(normalized)

        except Exception as e:
            logger.error(f"Error normalizing Yahoo Finance statements: {e}")

        return statements

    def _normalize_yahoo_statement_data(self, stmt_data: Dict[str, Any], symbol: str,
                                     statement_type: StatementType, period_type: ReportingPeriod,
                                     field_mapping: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Normalize individual Yahoo Finance statement data"""
        try:
            period_end = stmt_data.get("period_end")
            if not period_end:
                return None

            # Map Yahoo fields to agent fields with pandas NaN detection
            mapped_data = {}
            for yahoo_field, agent_field in field_mapping.items():
                if yahoo_field in stmt_data:
                    value = stmt_data[yahoo_field]
                    if value is not None and not pd.isna(value):
                        try:
                            numeric_value = float(value)
                            if numeric_value != 0:  # Include zero values for growth calculations
                                mapped_data[agent_field] = numeric_value
                        except (ValueError, TypeError):
                            continue

            if not mapped_data:
                return None

            # Determine currency and units based on symbol suffix
            currency = "INR" if symbol.endswith((".NS", ".BO")) else "USD"
            units = "lakhs" if currency == "INR" else "dollars"

            return {
                "symbol": symbol,
                "statement_type": statement_type,
                "period_type": period_type,
                "period_end": self._parse_date(period_end),
                "currency": currency,
                "units": units,
                **mapped_data,
                "source": "yahoo",
                "raw_data": stmt_data
            }

        except Exception as e:
            logger.error(f"Error normalizing Yahoo statement data: {e}")
            return None

    def _format_market_cap(self, market_cap: float) -> float:
        """Format market cap for display (convert to appropriate scale)"""
        try:
            if market_cap >= 1e12:  # Trillion
                return round(market_cap / 1e12, 2)
            elif market_cap >= 1e9:  # Billion
                return round(market_cap / 1e9, 2)
            elif market_cap >= 1e6:  # Million
                return round(market_cap / 1e6, 2)
            else:
                return round(market_cap, 2)
        except (ValueError, TypeError):
            return 0.0

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
            
    def fetch_disclosure_documents(self, company_symbol: str, source: str, document_types: List[str] = None) -> List[Dict[str, Any]]:
        """Fetch disclosure documents from NSE/BSE portals"""
        try:
            logger.info(f"Fetching disclosure documents for {company_symbol} from {source}")

            if document_types is None:
                document_types = ["annual_report", "quarterly_results", "corporate_announcements"]

            documents = []

            if source == "nse":
                # Get corporate announcements from NSE
                announcements = self.nse_client.get_corporate_announcements(company_symbol)
                for announcement in announcements:
                    doc_type = self._classify_document_type(announcement.get("subject", ""))
                    if doc_type in document_types:
                        documents.append({
                            "source": "nse",
                            "company_symbol": company_symbol,
                            "document_type": doc_type,
                            "title": announcement.get("subject", ""),
                            "date": announcement.get("disseminated_date"),
                            "attachment_url": announcement.get("attachment", ""),
                            "raw_data": announcement
                        })

            elif source == "bse":
                # Get corporate announcements from BSE
                announcements = self.bse_client.get_corporate_announcements(company_symbol)
                for announcement in announcements:
                    doc_type = self._classify_document_type(announcement.get("subject", ""))
                    if doc_type in document_types:
                        documents.append({
                            "source": "bse",
                            "company_symbol": company_symbol,
                            "document_type": doc_type,
                            "title": announcement.get("subject", ""),
                            "date": announcement.get("disseminated_date"),
                            "attachment_url": announcement.get("attachment", ""),
                            "raw_data": announcement
                        })

            logger.info(f"Found {len(documents)} disclosure documents for {company_symbol}")
            return documents

        except Exception as e:
            logger.error(f"Failed to fetch disclosure documents for {company_symbol}: {e}")
            return []

    def _classify_document_type(self, subject: str) -> str:
        """Classify document type based on subject/title"""
        subject_lower = str(subject).lower()

        if any(term in subject_lower for term in ["annual report", "annual results", "audited"]):
            return "annual_report"
        elif any(term in subject_lower for term in ["quarterly", "q1", "q2", "q3", "q4"]):
            return "quarterly_results"
        elif any(term in subject_lower for term in ["board meeting", "outcome", "proceedings"]):
            return "board_meeting"
        elif any(term in subject_lower for term in ["dividend", "bonus", "split"]):
            return "corporate_action"
        else:
            return "other"

    async def parse_annual_report_sections(self, pdf_path: str) -> Dict[str, Any]:
        """Parse annual report PDF and extract key sections"""
        try:
            logger.info(f"Parsing annual report: {pdf_path}")

            # Extract text using OCR processor
            ocr_result = await self.ocr_processor.extract_text_from_pdf(pdf_path)

            if not ocr_result.get("success"):
                logger.error(f"OCR extraction failed for {pdf_path}")
                return {"success": False, "error": "OCR extraction failed"}

            extracted_text = ocr_result.get("text", "")

            # Parse different sections
            sections = {
                "management_discussion": self._extract_section(extracted_text, ["management discussion", "md&a", "management's discussion"]),
                "audit_report": self._extract_section(extracted_text, ["auditor", "audit report", "independent auditor"]),
                "financial_statements": self._extract_section(extracted_text, ["balance sheet", "profit and loss", "income statement"]),
                "notes_to_accounts": self._extract_section(extracted_text, ["notes to", "notes on accounts", "accounting policies"]),
                "directors_report": self._extract_section(extracted_text, ["directors report", "board report", "directors' report"])
            }

            return {
                "success": True,
                "pdf_path": pdf_path,
                "total_pages": ocr_result.get("page_count", 0),
                "extraction_method": ocr_result.get("method", "unknown"),
                "sections": sections,
                "extracted_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to parse annual report {pdf_path}: {e}")
            return {"success": False, "error": str(e)}

    def _extract_section(self, text: str, keywords: List[str]) -> Optional[str]:
        """Extract section of text based on keywords"""
        try:
            text_lower = text.lower()
            lines = text.split('\n')

            # Find start of section
            start_idx = -1
            for i, line in enumerate(lines):
                line_lower = line.lower()
                if any(keyword in line_lower for keyword in keywords):
                    start_idx = i
                    break

            if start_idx == -1:
                return None

            # Find end of section (next major section or end of document)
            section_lines = []
            for i in range(start_idx, len(lines)):
                line_lower = lines[i].lower()

                # Check if this is a new major section
                if (i > start_idx and
                    any(header in line_lower for header in ["financial statements", "notes to", "directors", "auditor", "management"])):
                    break

                section_lines.append(lines[i])

            return '\n'.join(section_lines) if section_lines else None

        except Exception as e:
            logger.error(f"Error extracting section: {e}")
            return None

    async def process_disclosure_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single disclosure document (download, OCR, parse, store)"""
        try:
            attachment_url = document.get("attachment_url")
            if not attachment_url:
                return {"success": False, "error": "No attachment URL"}

            company_symbol = document.get("company_symbol")
            document_type = document.get("document_type")

            # Download document
            tmp_path = None
            try:
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
                    tmp_path = tmp_file.name

                if document.get("source") == "nse":
                    download_success = self.nse_client.download_document(
                        attachment_url, company_symbol, document_type
                    )
                elif document.get("source") == "bse":
                    download_success = self.bse_client.download_document(
                        attachment_url, company_symbol, document_type
                    )
                else:
                    return {"success": False, "error": "Unsupported source"}

                if not download_success:
                    return {"success": False, "error": "Document download failed"}

                # Parse PDF content
                parse_result = await self.parse_annual_report_sections(tmp_path)

                if not parse_result.get("success"):
                    return {"success": False, "error": "PDF parsing failed"}

                # Store in database (placeholder for now)
                document_id = f"doc_{company_symbol}_{int(datetime.now().timestamp())}"

                return {
                    "success": True,
                    "document_id": document_id,
                    "company_symbol": company_symbol,
                    "document_type": document_type,
                    "source": document.get("source"),
                    "parsed_sections": parse_result.get("sections", {}),
                    "extraction_metadata": {
                        "total_pages": parse_result.get("total_pages", 0),
                        "extraction_method": parse_result.get("extraction_method", "unknown"),
                        "extracted_at": parse_result.get("extracted_at")
                    },
                    "stored_at": datetime.now().isoformat()
                }

            finally:
                # Clean up temporary file
                if tmp_path and os.path.exists(tmp_path):
                    os.unlink(tmp_path)

        except Exception as e:
            logger.error(f"Failed to process disclosure document: {e}")
            return {"success": False, "error": str(e)}

    async def process_company_disclosure_documents(self, company_symbol: str, source: str) -> Dict[str, Any]:
        """Process all disclosure documents for a company"""
        try:
            logger.info(f"Processing disclosure documents for {company_symbol} from {source}")

            # Fetch available documents
            documents = self.fetch_disclosure_documents(company_symbol, source)

            if not documents:
                return {
                    "success": True,
                    "message": f"No disclosure documents found for {company_symbol}",
                    "processed_count": 0
                }

            # Process each document
            processed_documents = []
            failed_documents = []

            for document in documents:
                try:
                    result = await self.process_disclosure_document(document)
                    if result.get("success"):
                        processed_documents.append(result)
                    else:
                        failed_documents.append({
                            "document": document,
                            "error": result.get("error")
                        })
                except Exception as e:
                    logger.error(f"Error processing document {document.get('title')}: {e}")
                    failed_documents.append({
                        "document": document,
                        "error": str(e)
                    })

            return {
                "success": True,
                "company_symbol": company_symbol,
                "source": source,
                "total_documents": len(documents),
                "processed_count": len(processed_documents),
                "failed_count": len(failed_documents),
                "processed_documents": processed_documents,
                "failed_documents": failed_documents,
                "processed_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to process company disclosure documents: {e}")
            return {"success": False, "error": str(e)}
