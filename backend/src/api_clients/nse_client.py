"""
Project IRIS - NSE (National Stock Exchange) Client
Web scraping client for NSE corporate filings and announcements
"""

import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin, urlparse
import re

from .base_client import BaseAPIClient

logger = logging.getLogger(__name__)


class NSEClient(BaseAPIClient):
    """NSE web scraping client for corporate filings"""
    
    def __init__(self):
        super().__init__(
            base_url="https://www.nseindia.com",
            rate_limit_per_minute=30,  # Conservative rate limiting
            rate_limit_per_day=1000,
            timeout=30
        )
        
        # NSE-specific headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """NSE doesn't require authentication headers"""
        return {}
    
    def test_connection(self) -> bool:
        """Test NSE connection"""
        try:
            response = self.session.get(f"{self.base_url}/", timeout=self.timeout)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"NSE connection test failed: {e}")
            return False
    
    def _get_nse_session(self):
        """Initialize NSE session with required cookies"""
        try:
            # Get main page to establish session
            response = self.session.get(f"{self.base_url}/")
            response.raise_for_status()
            
            # Get additional cookies from API endpoint
            api_response = self.session.get(f"{self.base_url}/api/option-chain-indices?symbol=NIFTY")
            
            return True
        except Exception as e:
            logger.error(f"Failed to initialize NSE session: {e}")
            return False
    
    def search_company_by_symbol(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Search for company information by NSE symbol"""
        try:
            if not self._get_nse_session():
                return None
            
            # Get company info from NSE API
            url = f"{self.base_url}/api/quote-equity?symbol={symbol.upper()}"
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                if 'info' in data:
                    return {
                        'symbol': symbol.upper(),
                        'company_name': data['info'].get('companyName', ''),
                        'industry': data['info'].get('industry', ''),
                        'sector': data['info'].get('sector', ''),
                        'isin': data['info'].get('isin', ''),
                        'listing_date': data['info'].get('listingDate', ''),
                        'market_cap': data.get('priceInfo', {}).get('marketCap', 0),
                        'face_value': data['info'].get('faceValue', 0),
                        'source': 'nse'
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to search company by symbol {symbol}: {e}")
            return None
    
    def get_corporate_announcements(self, symbol: str, from_date: Optional[datetime] = None, 
                                  to_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get corporate announcements for a company"""
        try:
            if not from_date:
                from_date = datetime.now() - timedelta(days=365)
            if not to_date:
                to_date = datetime.now()
            
            # Format dates for NSE API
            from_date_str = from_date.strftime("%d-%m-%Y")
            to_date_str = to_date.strftime("%d-%m-%Y")
            
            if not self._get_nse_session():
                return []
            
            # Get announcements from NSE
            url = f"{self.base_url}/api/corporates-announcements"
            params = {
                'index': 'equities',
                'symbol': symbol.upper(),
                'from_date': from_date_str,
                'to_date': to_date_str
            }
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                announcements = []
                
                for item in data:
                    announcements.append({
                        'symbol': item.get('symbol', ''),
                        'company_name': item.get('company', ''),
                        'announcement_date': item.get('an_dt', ''),
                        'subject': item.get('subject', ''),
                        'attachment': item.get('attchmntFile', ''),
                        'attachment_text': item.get('attchmntText', ''),
                        'source': 'nse_announcements'
                    })
                
                return announcements
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get corporate announcements for {symbol}: {e}")
            return []
    
    def get_financial_results(self, symbol: str, period: str = "annual") -> List[Dict[str, Any]]:
        """Get financial results from NSE"""
        try:
            if not self._get_nse_session():
                return []
            
            # Get financial results
            url = f"{self.base_url}/api/corporates-financial-results"
            params = {
                'index': 'equities',
                'symbol': symbol.upper(),
                'period': period
            }
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for item in data:
                    results.append({
                        'symbol': item.get('symbol', ''),
                        'company_name': item.get('company', ''),
                        'period': item.get('period', ''),
                        'year_ending': item.get('yearEnding', ''),
                        'result_date': item.get('resultDate', ''),
                        'result_type': item.get('resultType', ''),
                        'attachment': item.get('attchmntFile', ''),
                        'source': 'nse_financial_results'
                    })
                
                return results
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get financial results for {symbol}: {e}")
            return []
    
    def get_shareholding_pattern(self, symbol: str) -> List[Dict[str, Any]]:
        """Get shareholding pattern data"""
        try:
            if not self._get_nse_session():
                return []
            
            url = f"{self.base_url}/api/corporates-shareholding"
            params = {
                'index': 'equities',
                'symbol': symbol.upper()
            }
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                patterns = []
                
                for item in data:
                    patterns.append({
                        'symbol': item.get('symbol', ''),
                        'company_name': item.get('company', ''),
                        'period': item.get('period', ''),
                        'year_ending': item.get('yearEnding', ''),
                        'attachment': item.get('attchmntFile', ''),
                        'source': 'nse_shareholding'
                    })
                
                return patterns
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get shareholding pattern for {symbol}: {e}")
            return []
    
    def download_document(self, attachment_url: str, symbol: str, doc_type: str) -> Optional[str]:
        """Download document from NSE"""
        try:
            if not attachment_url:
                return None
            
            # Construct full URL
            if attachment_url.startswith('/'):
                full_url = urljoin(self.base_url, attachment_url)
            else:
                full_url = attachment_url
            
            response = self.session.get(full_url, timeout=60)  # Longer timeout for downloads
            response.raise_for_status()
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{symbol}_{doc_type}_{timestamp}.pdf"
            filepath = f"./data/pdfs/{filename}"
            
            # Save file
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Downloaded document: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to download document {attachment_url}: {e}")
            return None
    
    def get_board_meetings(self, symbol: str) -> List[Dict[str, Any]]:
        """Get board meeting announcements"""
        try:
            if not self._get_nse_session():
                return []
            
            url = f"{self.base_url}/api/corporates-board-meetings"
            params = {
                'index': 'equities',
                'symbol': symbol.upper()
            }
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                meetings = []
                
                for item in data:
                    meetings.append({
                        'symbol': item.get('symbol', ''),
                        'company_name': item.get('company', ''),
                        'meeting_date': item.get('meetingDate', ''),
                        'meeting_time': item.get('meetingTime', ''),
                        'purpose': item.get('purpose', ''),
                        'attachment': item.get('attchmntFile', ''),
                        'source': 'nse_board_meetings'
                    })
                
                return meetings
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get board meetings for {symbol}: {e}")
            return []
    
    def get_comprehensive_filings(self, symbol: str, days_back: int = 365) -> Dict[str, Any]:
        """Get comprehensive corporate filings for a company"""
        try:
            logger.info(f"Fetching comprehensive NSE filings for {symbol}")
            
            from_date = datetime.now() - timedelta(days=days_back)
            to_date = datetime.now()
            
            # Get all types of filings
            company_info = self.search_company_by_symbol(symbol)
            announcements = self.get_corporate_announcements(symbol, from_date, to_date)
            financial_results = self.get_financial_results(symbol)
            shareholding = self.get_shareholding_pattern(symbol)
            board_meetings = self.get_board_meetings(symbol)
            
            return {
                "symbol": symbol,
                "company_info": company_info,
                "announcements": announcements,
                "financial_results": financial_results,
                "shareholding_pattern": shareholding,
                "board_meetings": board_meetings,
                "last_updated": datetime.utcnow().isoformat(),
                "source": "nse"
            }
            
        except Exception as e:
            logger.error(f"Failed to get comprehensive NSE filings for {symbol}: {e}")
            return {"symbol": symbol, "error": str(e), "source": "nse"}
