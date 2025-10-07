"""
Project IRIS - Financial Modeling Prep API Client
Client for accessing financial data from FMP API
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import pandas as pd

from .base_client import BaseAPIClient
from config import settings

logger = logging.getLogger(__name__)


class FMPAPIClient(BaseAPIClient):
    """Financial Modeling Prep API client"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            base_url=settings.fmp_base_url,
            api_key=api_key or settings.fmp_api_key,
            rate_limit_per_minute=settings.fmp_rate_limit_per_minute,
            rate_limit_per_day=settings.fmp_rate_limit_per_day,
            timeout=settings.fmp_timeout
        )
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for FMP API"""
        return {}  # FMP uses API key in query params
    
    def _add_api_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add API key to request parameters"""
        if params is None:
            params = {}
        params['apikey'] = self.api_key
        return params
    
    def test_connection(self) -> bool:
        """Test FMP API connection"""
        try:
            response = self.get("/stock/list", params=self._add_api_key({"limit": 1}))
            return isinstance(response, list) and len(response) > 0
        except Exception as e:
            logger.error(f"FMP connection test failed: {e}")
            return False
    
    def search_company(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for companies by name or symbol"""
        try:
            params = self._add_api_key({
                "query": query,
                "limit": limit
            })
            
            response = self.get("/search", params=params)
            
            if isinstance(response, list):
                return response
            else:
                logger.warning(f"Unexpected response format for company search: {type(response)}")
                return []
                
        except Exception as e:
            logger.error(f"Company search failed for query '{query}': {e}")
            return []
    
    def get_company_profile(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get company profile information"""
        try:
            params = self._add_api_key({})
            response = self.get(f"/profile/{symbol}", params=params)
            
            if isinstance(response, list) and len(response) > 0:
                return response[0]
            elif isinstance(response, dict):
                return response
            else:
                logger.warning(f"No profile found for symbol: {symbol}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get company profile for {symbol}: {e}")
            return None
    
    def get_financial_statements(self, symbol: str, statement_type: str = "income-statement",
                                period: str = "annual", limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get financial statements
        
        Args:
            symbol: Stock symbol
            statement_type: "income-statement", "balance-sheet-statement", "cash-flow-statement"
            period: "annual" or "quarter"
            limit: Number of periods to retrieve
        """
        try:
            params = self._add_api_key({
                "limit": limit,
                "period": period
            })
            
            response = self.get(f"/{statement_type}/{symbol}", params=params)
            
            if isinstance(response, list):
                return response
            else:
                logger.warning(f"Unexpected response format for financial statements: {type(response)}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to get {statement_type} for {symbol}: {e}")
            return []
    
    def get_income_statement(self, symbol: str, period: str = "annual", limit: int = 5) -> List[Dict[str, Any]]:
        """Get income statement data"""
        return self.get_financial_statements(symbol, "income-statement", period, limit)
    
    def get_balance_sheet(self, symbol: str, period: str = "annual", limit: int = 5) -> List[Dict[str, Any]]:
        """Get balance sheet data"""
        return self.get_financial_statements(symbol, "balance-sheet-statement", period, limit)
    
    def get_cash_flow_statement(self, symbol: str, period: str = "annual", limit: int = 5) -> List[Dict[str, Any]]:
        """Get cash flow statement data"""
        return self.get_financial_statements(symbol, "cash-flow-statement", period, limit)
    
    def get_financial_ratios(self, symbol: str, period: str = "annual", limit: int = 5) -> List[Dict[str, Any]]:
        """Get financial ratios"""
        try:
            params = self._add_api_key({
                "limit": limit,
                "period": period
            })
            
            response = self.get(f"/ratios/{symbol}", params=params)
            
            if isinstance(response, list):
                return response
            else:
                logger.warning(f"Unexpected response format for ratios: {type(response)}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to get ratios for {symbol}: {e}")
            return []
    
    def get_key_metrics(self, symbol: str, period: str = "annual", limit: int = 5) -> List[Dict[str, Any]]:
        """Get key financial metrics"""
        try:
            params = self._add_api_key({
                "limit": limit,
                "period": period
            })
            
            response = self.get(f"/key-metrics/{symbol}", params=params)
            
            if isinstance(response, list):
                return response
            else:
                logger.warning(f"Unexpected response format for key metrics: {type(response)}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to get key metrics for {symbol}: {e}")
            return []
    
    def get_enterprise_values(self, symbol: str, period: str = "annual", limit: int = 5) -> List[Dict[str, Any]]:
        """Get enterprise value data"""
        try:
            params = self._add_api_key({
                "limit": limit,
                "period": period
            })
            
            response = self.get(f"/enterprise-values/{symbol}", params=params)
            
            if isinstance(response, list):
                return response
            else:
                logger.warning(f"Unexpected response format for enterprise values: {type(response)}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to get enterprise values for {symbol}: {e}")
            return []
    
    def get_financial_growth(self, symbol: str, period: str = "annual", limit: int = 5) -> List[Dict[str, Any]]:
        """Get financial growth metrics"""
        try:
            params = self._add_api_key({
                "limit": limit,
                "period": period
            })
            
            response = self.get(f"/financial-growth/{symbol}", params=params)
            
            if isinstance(response, list):
                return response
            else:
                logger.warning(f"Unexpected response format for financial growth: {type(response)}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to get financial growth for {symbol}: {e}")
            return []
    
    def get_comprehensive_financials(self, symbol: str, periods: int = 5) -> Dict[str, Any]:
        """Get comprehensive financial data for a company"""
        try:
            logger.info(f"Fetching comprehensive financial data for {symbol}")
            
            # Get all financial statements and metrics
            profile = self.get_company_profile(symbol)
            income_annual = self.get_income_statement(symbol, "annual", periods)
            income_quarterly = self.get_income_statement(symbol, "quarter", periods * 4)
            balance_annual = self.get_balance_sheet(symbol, "annual", periods)
            balance_quarterly = self.get_balance_sheet(symbol, "quarter", periods * 4)
            cashflow_annual = self.get_cash_flow_statement(symbol, "annual", periods)
            cashflow_quarterly = self.get_cash_flow_statement(symbol, "quarter", periods * 4)
            ratios = self.get_financial_ratios(symbol, "annual", periods)
            key_metrics = self.get_key_metrics(symbol, "annual", periods)
            growth = self.get_financial_growth(symbol, "annual", periods)
            
            return {
                "symbol": symbol,
                "profile": profile,
                "income_statement": {
                    "annual": income_annual,
                    "quarterly": income_quarterly
                },
                "balance_sheet": {
                    "annual": balance_annual,
                    "quarterly": balance_quarterly
                },
                "cash_flow": {
                    "annual": cashflow_annual,
                    "quarterly": cashflow_quarterly
                },
                "ratios": ratios,
                "key_metrics": key_metrics,
                "growth_metrics": growth,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get comprehensive financials for {symbol}: {e}")
            return {"symbol": symbol, "error": str(e)}
    
    def get_stock_list(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get list of available stocks"""
        try:
            params = self._add_api_key({"limit": limit})
            response = self.get("/stock/list", params=params)
            
            if isinstance(response, list):
                return response
            else:
                logger.warning(f"Unexpected response format for stock list: {type(response)}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to get stock list: {e}")
            return []
