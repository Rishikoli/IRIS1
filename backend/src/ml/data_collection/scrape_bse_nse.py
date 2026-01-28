"""
BSE/NSE Data Scraper

Scrapes corporate announcements, financial results, and company filings
from Bombay Stock Exchange (BSE) and National Stock Exchange (NSE).
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict
import time
import logging
from pathlib import Path
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BSENSEScraper:
    """Scraper for BSE and NSE corporate announcements"""
    
    BSE_BASE_URL = "https://www.bseindia.com"
    NSE_BASE_URL = "https://www.nseindia.com"
    
    def __init__(self, output_dir: str = "data/raw/exchanges"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # NSE requires specific headers to avoid blocking
        self.nse_session = requests.Session()
        self.nse_session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.nseindia.com/'
        })
        
        self.bse_session = requests.Session()
        self.bse_session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_bse_announcements(self, days: int = 30, max_records: int = 1000) -> pd.DataFrame:
        """
        Scrape BSE corporate announcements
        
        Args:
            days: Number of days to look back
            max_records: Maximum number of records to scrape
            
        Returns:
            DataFrame with announcement data
        """
        logger.info(f"Scraping BSE announcements for last {days} days...")
        
        announcements = []
        
        # BSE API endpoint for announcements
        api_url = f"{self.BSE_BASE_URL}/corporates/ann.html"
        
        try:
            # First, get the main page to establish session
            response = self.bse_session.get(api_url, timeout=10)
            response.raise_for_status()
            
            # Try to find announcements table
            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find('table', class_='announcement-table') or soup.find('table')
            
            if table:
                rows = table.find_all('tr')[1:]  # Skip header
                
                for row in rows[:max_records]:
                    try:
                        cols = row.find_all('td')
                        if len(cols) >= 4:
                            announcement = self._parse_bse_row(cols)
                            if announcement:
                                announcements.append(announcement)
                    except Exception as e:
                        logger.warning(f"Failed to parse BSE row: {e}")
                        continue
                    
                logger.info(f"Scraped {len(announcements)} BSE announcements")
            else:
                logger.warning("Could not find BSE announcements table")
                
        except Exception as e:
            logger.error(f"Error scraping BSE: {e}")
        
        df = pd.DataFrame(announcements)
        
        if not df.empty:
            output_file = self.output_dir / f"bse_announcements_{datetime.now().strftime('%Y%m%d')}.csv"
            df.to_csv(output_file, index=False)
            logger.info(f"Saved to {output_file}")
        
        return df
    
    def _parse_bse_row(self, cols) -> Dict:
        """Parse BSE announcement table row"""
        try:
            company = cols[0].get_text(strip=True)
            category = cols[1].get_text(strip=True)
            subject = cols[2].get_text(strip=True)
            date = cols[3].get_text(strip=True)
            
            # Determine sentiment based on keywords
            label = self._classify_announcement(subject, category)
            
            return {
                'company': company,
                'category': category,
                'text': subject,
                'title': subject,
                'date': date,
                'label': label,
                'source': 'BSE',
                'url': self.BSE_BASE_URL
            }
        except Exception as e:
            logger.warning(f"Error parsing BSE row: {e}")
            return None
    
    def scrape_nse_announcements(self, days: int = 30, max_records: int = 1000) -> pd.DataFrame:
        """
        Scrape NSE corporate announcements using their API
        
        Args:
            days: Number of days to look back
            max_records: Maximum number of records
            
        Returns:
            DataFrame with announcement data
        """
        logger.info(f"Scraping NSE announcements for last {days} days...")
        
        announcements = []
        
        try:
            # NSE API endpoint for corporate announcements
            # Note: NSE requires cookies from homepage first
            homepage = self.nse_session.get(self.NSE_BASE_URL, timeout=10)
            time.sleep(1)
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # API URL (adjust based on actual NSE API structure)
            api_url = f"{self.NSE_BASE_URL}/api/corporates-announcements"
            params = {
                'from_date': start_date.strftime('%d-%m-%Y'),
                'to_date': end_date.strftime('%d-%m-%Y'),
                'index': 'equities'
            }
            
            response = self.nse_session.get(api_url, params=params, timeout=15)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Parse JSON response (adjust keys based on actual API)
                    if isinstance(data, list):
                        items = data[:max_records]
                    elif isinstance(data, dict) and 'data' in data:
                        items = data['data'][:max_records]
                    else:
                        items = []
                    
                    for item in items:
                        announcement = self._parse_nse_item(item)
                        if announcement:
                            announcements.append(announcement)
                    
                    logger.info(f"Scraped {len(announcements)} NSE announcements")
                    
                except json.JSONDecodeError:
                    logger.warning("NSE API returned non-JSON response, trying HTML parsing...")
                    announcements = self._scrape_nse_html()
            else:
                logger.warning(f"NSE API returned status code {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error scraping NSE: {e}")
        
        df = pd.DataFrame(announcements)
        
        if not df.empty:
            output_file = self.output_dir / f"nse_announcements_{datetime.now().strftime('%Y%m%d')}.csv"
            df.to_csv(output_file, index=False)
            logger.info(f"Saved to {output_file}")
        
        return df
    
    def _parse_nse_item(self, item: Dict) -> Dict:
        """Parse NSE announcement JSON item"""
        try:
            # Adjust field names based on actual NSE API response
            company = item.get('symbol', item.get('company', 'Unknown'))
            subject = item.get('subject', item.get('sm_name', ''))
            date = item.get('an_dt', item.get('date', ''))
            category = item.get('sm_name', item.get('category', ''))
            
            label = self._classify_announcement(subject, category)
            
            return {
                'company': company,
                'category': category,
                'text': subject,
                'title': subject,
                'date': date,
                'label': label,
                'source': 'NSE',
                'url': self.NSE_BASE_URL
            }
        except Exception as e:
            logger.warning(f"Error parsing NSE item: {e}")
            return None
    
    def _scrape_nse_html(self) -> List[Dict]:
        """Fallback HTML scraping for NSE"""
        announcements = []
        
        try:
            url = f"{self.NSE_BASE_URL}/companies-listing/corporate-filings-announcements"
            response = self.nse_session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            table = soup.find('table')
            if table:
                rows = table.find_all('tr')[1:]
                
                for row in rows[:100]:
                    cols = row.find_all('td')
                    if len(cols) >= 3:
                        announcement = {
                            'company': cols[0].get_text(strip=True),
                            'text': cols[1].get_text(strip=True),
                            'date': cols[2].get_text(strip=True) if len(cols) > 2 else '',
                            'category': 'General',
                            'label': 'neutral',
                            'source': 'NSE',
                            'url': self.NSE_BASE_URL
                        }
                        announcements.append(announcement)
                        
        except Exception as e:
            logger.error(f"HTML fallback failed: {e}")
        
        return announcements
    
    def _classify_announcement(self, text: str, category: str = '') -> str:
        """
        Classify announcement sentiment based on keywords
        
        Returns: 'positive', 'negative', or 'neutral'
        """
        text_lower = text.lower()
        category_lower = category.lower()
        
        # Positive indicators
        positive_keywords = [
            'profit', 'growth', 'increase', 'dividend', 'approval', 
            'expansion', 'acquisition', 'record', 'strong', 'exceed',
            'upgrade', 'bonus', 'award', 'partnership', 'launch'
        ]
        
        # Negative indicators
        negative_keywords = [
            'loss', 'decline', 'penalty', 'fraud', 'default', 'delay',
            'litigation', 'suspension', 'resign', 'impairment', 'write-off',
            'downgrade', 'withdrawal', 'closure', 'investigation'
        ]
        
        positive_score = sum(1 for kw in positive_keywords if kw in text_lower)
        negative_score = sum(1 for kw in negative_keywords if kw in text_lower)
        
        if positive_score > negative_score:
            return 'positive'
        elif negative_score > positive_score:
            return 'negative'
        else:
            return 'neutral'
    
    def scrape_all(self, days: int = 30, max_records: int = 1000) -> pd.DataFrame:
        """Scrape both BSE and NSE announcements"""
        logger.info("Starting comprehensive BSE/NSE scraping...")
        
        bse_df = self.scrape_bse_announcements(days, max_records)
        time.sleep(3)  # Respectful delay between sources
        
        nse_df = self.scrape_nse_announcements(days, max_records)
        
        if not bse_df.empty and not nse_df.empty:
            combined_df = pd.concat([bse_df, nse_df], ignore_index=True)
        elif not bse_df.empty:
            combined_df = bse_df
        elif not nse_df.empty:
            combined_df = nse_df
        else:
            logger.warning("No data scraped from either exchange")
            return pd.DataFrame()
        
        # Remove duplicates
        combined_df = combined_df.drop_duplicates(subset=['text', 'date'])
        
        # Save combined dataset
        output_file = self.output_dir / f"exchanges_combined_{datetime.now().strftime('%Y%m%d')}.csv"
        combined_df.to_csv(output_file, index=False)
        logger.info(f"Combined dataset saved to {output_file}")
        
        return combined_df


if __name__ == "__main__":
    # Example usage
    scraper = BSENSEScraper()
    df = scraper.scrape_all(days=7, max_records=500)
    
    if not df.empty:
        print(f"\nScraped {len(df)} exchange announcements")
        print("\nSample data:")
        print(df.head())
        print(f"\nLabel distribution:\n{df['label'].value_counts()}")
        print(f"\nSource distribution:\n{df['source'].value_counts()}")
