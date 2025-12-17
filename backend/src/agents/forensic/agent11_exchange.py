import logging
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
from duckduckgo_search import DDGS
import json
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExchangeAgent:
    """Agent 11: The Exchange - Fetches Official Shareholding Patterns"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    def get_shareholding_pattern(self, company_symbol: str) -> Dict[str, Any]:
        """
        Fetches the latest shareholding pattern for a company.
        Prioritizes Screener.in as it provides clean, authoritative data mirrored from exchanges.
        """
        try:
            # Clean symbol (remove .NS, .BO)
            symbol = company_symbol.split('.')[0]
            
            logger.info(f"Fetching shareholding pattern for {symbol}...")
            
            # 1. Try Screener.in (Very reliable for Indian stocks)
            data = self._scrape_screener(symbol)
            if data:
                return {"status": "success", "source": "Screener.in", "data": data}
            
            # 2. Fallback to BSE/NSE Search & Scrape (Implementation placeholder)
            # direct scraping of nseindia.com often requires complex session handling
            
            return {"status": "error", "message": "Could not fetch shareholding pattern"}

        except Exception as e:
            logger.error(f"Exchange Agent failed: {e}")
            return {"status": "error", "message": str(e)}

    def _scrape_screener(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Scrape shareholding data from Screener.in"""
        try:
            url = f"https://www.screener.in/company/{symbol}/consolidated/"
            logger.info(f"Requesting {url}")
            
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                # Try standalone URL if consolidated fails
                url = f"https://www.screener.in/company/{symbol}/"
                response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"Screener returned {response.status_code}")
                return None

            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find Shareholding Section
            shareholding_section = soup.find('section', id='shareholding')
            if not shareholding_section:
                logger.warning("No shareholding section found")
                return None

            # Parse the table
            table = shareholding_section.find('table')
            if not table:
                return None

            # Extract latest quarter data
            # The table has headers (Quarters) and rows (Promoters, FIIs, etc.)
            # We want the last column (Latest Quarter)
            
            headers = [th.text.strip() for th in table.find_all('th')]
            latest_quarter = headers[-1] if headers else "Latest"
            
            shareholding = {
                "period": latest_quarter,
                "promoters": 0.0,
                "fii": 0.0,
                "dii": 0.0,
                "public": 0.0,
                "others": 0.0
            }
            
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if not cols:
                    continue
                
                category = row.find('td', class_='text').text.strip().lower()
                value_str = cols[-1].text.strip().replace('%', '')
                
                try:
                    value = float(value_str) if value_str else 0.0
                except ValueError:
                    continue

                if 'promoters' in category:
                    shareholding['promoters'] = value
                elif 'fii' in category or 'foreign' in category:
                    shareholding['fii'] = value
                elif 'dii' in category or 'domestic' in category:
                    shareholding['dii'] = value
                elif 'public' in category:
                    shareholding['public'] = value
                elif 'govt' in category or 'other' in category:
                    shareholding['others'] += value # Add to others

            logger.info(f"Extracted Shareholding: {shareholding}")
            return shareholding

        except Exception as e:
            logger.error(f"Screener scrape failed: {e}")
            return None
