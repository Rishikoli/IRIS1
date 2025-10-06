"""
Project IRIS - BSE (Bombay Stock Exchange) Client
Web scraping client for BSE corporate announcements and filings
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


class BSEClient(BaseAPIClient):
    """BSE web scraping client for corporate filings"""
    
    def __init__(self):
        super().__init__(
            base_url="https://www.bseindia.com",
            rate_limit_per_minute=20,  # Conservative rate limiting for BSE
            rate_limit_per_day=800,
            timeout=30
        )
        
        # BSE-specific headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.bseindia.com/'
        })
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """BSE doesn't require authentication headers"""
        return {}
    
    def test_connection(self) -> bool:
        """Test BSE connection"""
        try:
            response = self.session.get(f"{self.base_url}/", timeout=self.timeout)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"BSE connection test failed: {e}")
            return False
    
    def search_company_by_code(self, scrip_code: str) -> Optional[Dict[str, Any]]:
        """Search for company information by BSE scrip code"""
        try:
            # BSE stock quote URL
            url = f"{self.base_url}/stock-share-price/stock-quote/{scrip_code}"
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract company information
                company_name = ""
                industry = ""
                
                # Try to find company name
                title_elem = soup.find('title')
                if title_elem:
                    title_text = title_elem.get_text()
                    # Extract company name from title
                    match = re.search(r'(.+?)\s+Share Price', title_text)
                    if match:
                        company_name = match.group(1).strip()
                
                # Try to find industry information
                industry_elem = soup.find('span', {'class': 'industry'})
                if industry_elem:
                    industry = industry_elem.get_text().strip()
                
                return {
                    'scrip_code': scrip_code,
                    'company_name': company_name,
                    'industry': industry,
                    'source': 'bse'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to search company by scrip code {scrip_code}: {e}")
            return None
    
    def get_corporate_announcements(self, scrip_code: str, from_date: Optional[datetime] = None,
                                  to_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get corporate announcements from BSE"""
        try:
            if not from_date:
                from_date = datetime.now() - timedelta(days=365)
            if not to_date:
                to_date = datetime.now()
            
            # BSE announcements URL
            url = f"{self.base_url}/corporates/ann.aspx"
            
            # Format dates for BSE (dd/mm/yyyy)
            from_date_str = from_date.strftime("%d/%m/%Y")
            to_date_str = to_date.strftime("%d/%m/%Y")
            
            params = {
                'scripcd': scrip_code,
                'fdate': from_date_str,
                'tdate': to_date_str
            }
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                announcements = []
                
                # Find announcement table
                table = soup.find('table', {'id': 'ctl00_ContentPlaceHolder1_gvData'})
                if table:
                    rows = table.find_all('tr')[1:]  # Skip header row
                    
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 4:
                            announcement = {
                                'scrip_code': scrip_code,
                                'date': cells[0].get_text().strip(),
                                'category': cells[1].get_text().strip(),
                                'subject': cells[2].get_text().strip(),
                                'attachment': '',
                                'source': 'bse_announcements'
                            }
                            
                            # Check for attachment link
                            link = cells[3].find('a')
                            if link and link.get('href'):
                                announcement['attachment'] = urljoin(self.base_url, link.get('href'))
                            
                            announcements.append(announcement)
                
                return announcements
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get BSE announcements for {scrip_code}: {e}")
            return []
    
    def get_financial_results(self, scrip_code: str) -> List[Dict[str, Any]]:
        """Get financial results from BSE"""
        try:
            url = f"{self.base_url}/corporates/Comp_Resultsnew.aspx"
            params = {'scripcd': scrip_code}
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                results = []
                
                # Find results table
                table = soup.find('table', {'class': 'TTRow'})
                if table:
                    rows = table.find_all('tr')[1:]  # Skip header
                    
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 5:
                            result = {
                                'scrip_code': scrip_code,
                                'period': cells[0].get_text().strip(),
                                'year': cells[1].get_text().strip(),
                                'result_date': cells[2].get_text().strip(),
                                'result_type': cells[3].get_text().strip(),
                                'attachment': '',
                                'source': 'bse_financial_results'
                            }
                            
                            # Check for attachment
                            link = cells[4].find('a')
                            if link and link.get('href'):
                                result['attachment'] = urljoin(self.base_url, link.get('href'))
                            
                            results.append(result)
                
                return results
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get BSE financial results for {scrip_code}: {e}")
            return []
    
    def get_shareholding_pattern(self, scrip_code: str) -> List[Dict[str, Any]]:
        """Get shareholding pattern from BSE"""
        try:
            url = f"{self.base_url}/corporates/shpPromoterNPublic.aspx"
            params = {'scripcd': scrip_code}
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                patterns = []
                
                # Find shareholding table
                table = soup.find('table', {'class': 'TTRow'})
                if table:
                    rows = table.find_all('tr')[1:]  # Skip header
                    
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 4:
                            pattern = {
                                'scrip_code': scrip_code,
                                'quarter': cells[0].get_text().strip(),
                                'year': cells[1].get_text().strip(),
                                'submission_date': cells[2].get_text().strip(),
                                'attachment': '',
                                'source': 'bse_shareholding'
                            }
                            
                            # Check for attachment
                            link = cells[3].find('a')
                            if link and link.get('href'):
                                pattern['attachment'] = urljoin(self.base_url, link.get('href'))
                            
                            patterns.append(pattern)
                
                return patterns
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get BSE shareholding pattern for {scrip_code}: {e}")
            return []
    
    def get_board_meetings(self, scrip_code: str) -> List[Dict[str, Any]]:
        """Get board meeting information from BSE"""
        try:
            url = f"{self.base_url}/corporates/board-meeting.aspx"
            params = {'scripcd': scrip_code}
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                meetings = []
                
                # Find meetings table
                table = soup.find('table', {'class': 'TTRow'})
                if table:
                    rows = table.find_all('tr')[1:]  # Skip header
                    
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 4:
                            meeting = {
                                'scrip_code': scrip_code,
                                'meeting_date': cells[0].get_text().strip(),
                                'purpose': cells[1].get_text().strip(),
                                'announcement_date': cells[2].get_text().strip(),
                                'attachment': '',
                                'source': 'bse_board_meetings'
                            }
                            
                            # Check for attachment
                            link = cells[3].find('a')
                            if link and link.get('href'):
                                meeting['attachment'] = urljoin(self.base_url, link.get('href'))
                            
                            meetings.append(meeting)
                
                return meetings
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get BSE board meetings for {scrip_code}: {e}")
            return []
    
    def download_document(self, attachment_url: str, scrip_code: str, doc_type: str) -> Optional[str]:
        """Download document from BSE"""
        try:
            if not attachment_url:
                return None
            
            response = self.session.get(attachment_url, timeout=60)  # Longer timeout for downloads
            response.raise_for_status()
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"BSE_{scrip_code}_{doc_type}_{timestamp}.pdf"
            filepath = f"./data/pdfs/{filename}"
            
            # Save file
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Downloaded BSE document: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to download BSE document {attachment_url}: {e}")
            return None
    
    def search_company_by_name(self, company_name: str) -> List[Dict[str, Any]]:
        """Search for companies by name on BSE"""
        try:
            # BSE company search URL
            url = f"{self.base_url}/corporates/List_Scrips.aspx"
            
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                companies = []
                
                # Find company list table
                table = soup.find('table', {'class': 'TTRow'})
                if table:
                    rows = table.find_all('tr')[1:]  # Skip header
                    
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 3:
                            company_cell_name = cells[1].get_text().strip()
                            
                            # Check if company name matches search term
                            if company_name.lower() in company_cell_name.lower():
                                company = {
                                    'scrip_code': cells[0].get_text().strip(),
                                    'company_name': company_cell_name,
                                    'group': cells[2].get_text().strip() if len(cells) > 2 else '',
                                    'source': 'bse'
                                }
                                companies.append(company)
                
                return companies
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to search BSE companies by name '{company_name}': {e}")
            return []
    
    def get_comprehensive_filings(self, scrip_code: str, days_back: int = 365) -> Dict[str, Any]:
        """Get comprehensive corporate filings for a company from BSE"""
        try:
            logger.info(f"Fetching comprehensive BSE filings for scrip code {scrip_code}")
            
            from_date = datetime.now() - timedelta(days=days_back)
            to_date = datetime.now()
            
            # Get all types of filings
            company_info = self.search_company_by_code(scrip_code)
            announcements = self.get_corporate_announcements(scrip_code, from_date, to_date)
            financial_results = self.get_financial_results(scrip_code)
            shareholding = self.get_shareholding_pattern(scrip_code)
            board_meetings = self.get_board_meetings(scrip_code)
            
            return {
                "scrip_code": scrip_code,
                "company_info": company_info,
                "announcements": announcements,
                "financial_results": financial_results,
                "shareholding_pattern": shareholding,
                "board_meetings": board_meetings,
                "last_updated": datetime.utcnow().isoformat(),
                "source": "bse"
            }
            
        except Exception as e:
            logger.error(f"Failed to get comprehensive BSE filings for {scrip_code}: {e}")
            return {"scrip_code": scrip_code, "error": str(e), "source": "bse"}
