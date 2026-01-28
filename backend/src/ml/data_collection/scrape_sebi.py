"""
SEBI Data Scraper

Scrapes enforcement orders, press releases, and regulatory announcements
from the Securities and Exchange Board of India (SEBI) website.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from typing import List, Dict
import time
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SEBIScraper:
    """Scraper for SEBI enforcement orders and announcements"""
    
    BASE_URL = "https://www.sebi.gov.in"
    # Correct URLs found from browser inspection
    ORDERS_AO_URL = f"{BASE_URL}/sebiweb/home/HomeAction.do?doListing=yes&sid=2&ssid=9&smid=6"
    PRESS_RELEASES_URL = f"{BASE_URL}/sebiweb/home/HomeAction.do?doListing=yes&sid=6&ssid=23&smid=0"
    
    def __init__(self, output_dir: str = "data/raw/sebi"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.sebi.gov.in/'
        })
    
    def scrape_enforcement_orders(self, max_pages: int = 20) -> pd.DataFrame:
        """
        Scrape SEBI enforcement orders (typically negative sentiment)
        Uses correct URL: /sebiweb/home/HomeAction.do
        
        Args:
            max_pages: Maximum number of pages to scrape
            
        Returns:
            DataFrame with columns: title, text, date, url, label
        """
        logger.info(f"Scraping SEBI enforcement orders (max {max_pages} pages)...")
        
        orders = []
        
        for page in range(1, max_pages + 1):
            try:
                # SEBI uses POST for pagination, but first page can be GET
                if page == 1:
                    response = self.session.get(self.ORDERS_AO_URL, timeout=15)
                else:
                    # For subsequent pages, send POST with page number
                    payload = {'pageno': str(page)}
                    response = self.session.post(self.ORDERS_AO_URL, data=payload, timeout=15)
                
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find the main table containing orders
                # Table has rows with Date, Title columns
                rows = soup.find_all('tr')
                
                page_orders = 0
                for row in rows:
                    try:
                        cols = row.find_all('td')
                        if len(cols) >= 2:
                            # First column: date
                            # Second column: title with link (class='points')
                            date_td = cols[0]
                            title_td = cols[1]
                            
                            date_str = date_td.get_text(strip=True)
                            link_elem = title_td.find('a', class_='points')
                            
                            if link_elem:
                                title = link_elem.get_text(strip=True)
                                href = link_elem.get('href', '')
                                
                                # Construct full URL
                                if href and not href.startswith('http'):
                                    url = f"{self.BASE_URL}{href}" if href.startswith('/') else f"{self.BASE_URL}/{href}"
                                else:
                                    url = href
                                
                                # Skip if title is too short or is a header
                                if len(title) < 20 or 'Title' in title:
                                    continue
                                
                                orders.append({
                                    'title': title,
                                    'text': title,  # Use title as text initially
                                    'date': date_str,
                                    'url': url,
                                    'label': 'negative',  # Enforcement orders are negative
                                    'source': 'SEBI'
                                })
                                page_orders += 1
                    
                    except Exception as e:
                        continue
                
                logger.info(f"Scraped page {page}, found {page_orders} orders")
                
                # If no orders found on this page, likely reached the end
                if page_orders == 0:
                    logger.info(f"No orders on page {page}, stopping pagination")
                    break
                
                time.sleep(2)  # Be respectful
                
            except Exception as e:
                logger.error(f"Error scraping page {page}: {e}")
                continue
        
        df = pd.DataFrame(orders)
        logger.info(f"Total orders scraped: {len(df)}")
        
        # Save to CSV
        output_file = self.output_dir / f"sebi_orders_{datetime.now().strftime('%Y%m%d')}.csv"
        df.to_csv(output_file, index=False)
        logger.info(f"Saved to {output_file}")
        
        return df
    
    def _parse_order_item(self, item) -> Dict:
        """Parse individual order entry"""
        try:
            # Adjust these selectors based on actual SEBI website structure
            title_elem = item.find('a') or item.find('td', class_='title')
            date_elem = item.find('span', class_='date') or item.find('td', class_='date')
            
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            url = title_elem.get('href', '')
            if url and not url.startswith('http'):
                url = self.BASE_URL + url
            
            date_str = date_elem.get_text(strip=True) if date_elem else ''
            
            # Extract full text from linked page (optional, slower)
            full_text = self._extract_order_text(url) if url else title
            
            return {
                'title': title,
                'text': full_text[:1000],  # Limit text length
                'date': date_str,
                'url': url,
                'label': 'negative',  # Enforcement orders are typically negative
                'source': 'SEBI'
            }
        except Exception as e:
            logger.warning(f"Error parsing order: {e}")
            return None
    
    def _extract_order_text(self, url: str) -> str:
        """Extract full text from order detail page"""
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find main content area (adjust selector as needed)
            content = soup.find('div', class_='content') or soup.find('article')
            
            if content:
                # Extract text from paragraphs
                paragraphs = content.find_all('p')
                text = ' '.join([p.get_text(strip=True) for p in paragraphs])
                return text
            
            return soup.get_text(strip=True)[:2000]
            
        except Exception as e:
            logger.warning(f"Failed to extract text from {url}: {e}")
            return ""
    
    def scrape_press_releases(self, max_pages: int = 20) -> pd.DataFrame:
        """
        Scrape SEBI press releases (mixed sentiment)
        Uses correct URL: /sebiweb/home/HomeAction.do
        
        Args:
            max_pages: Maximum number of pages to scrape
            
        Returns:
            DataFrame with press release data
        """
        logger.info(f"Scraping SEBI press releases (max {max_pages} pages)...")
        
        releases = []
        
        for page in range(1, max_pages + 1):
            try:
                if page == 1:
                    response = self.session.get(self.PRESS_RELEASES_URL, timeout=15)
                else:
                    payload = {'pageno': str(page)}
                    response = self.session.post(self.PRESS_RELEASES_URL, data=payload, timeout=15)
                
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                rows = soup.find_all('tr')
                
                page_releases = 0
                for row in rows:
                    try:
                        cols = row.find_all('td')
                        if len(cols) >= 3:
                            # Date, PR No, Title structure
                            date_str = cols[0].get_text(strip=True)
                            pr_no = cols[1].get_text(strip=True)
                            link_elem = cols[2].find('a', class_='points')
                            
                            if link_elem:
                                title = link_elem.get_text(strip=True)
                                href = link_elem.get('href', '')
                                
                                if href and not href.startswith('http'):
                                    url = f"{self.BASE_URL}{href}" if href.startswith('/') else f"{self.BASE_URL}/{href}"
                                else:
                                    url = href
                                
                                if len(title) < 20 or 'PR No' in title:
                                    continue
                                
                                releases.append({
                                    'title': title,
                                    'text': title,
                                    'date': date_str,
                                    'url': url,
                                    'label': 'neutral',  # Press releases need manual labeling
                                    'source': 'SEBI',
                                    'pr_no': pr_no
                                })
                                page_releases += 1
                    
                    except Exception as e:
                        continue
                
                logger.info(f"Scraped page {page}, found {page_releases} releases")
                
                if page_releases == 0:
                    logger.info(f"No releases on page {page}, stopping pagination")
                    break
                
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error scraping press releases page {page}: {e}")
                continue
        
        df = pd.DataFrame(releases)
        logger.info(f"Total press releases scraped: {len(df)}")
        
        output_file = self.output_dir / f"sebi_press_releases_{datetime.now().strftime('%Y%m%d')}.csv"
        df.to_csv(output_file, index=False)
        logger.info(f"Saved to {output_file}")
        
        return df
    
    def _parse_press_release(self, item) -> Dict:
        """Parse individual press release"""
        try:
            title_elem = item.find('a') or item.find('td')
            date_elem = item.find('span', class_='date') or item.find('td', class_='date')
            
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            url = title_elem.get('href', '')
            if url and not url.startswith('http'):
                url = self.BASE_URL + url
            
            date_str = date_elem.get_text(strip=True) if date_elem else ''
            
            return {
                'title': title,
                'text': title,  # Use title as text initially
                'date': date_str,
                'url': url,
                'label': 'neutral',  # Press releases need manual labeling
                'source': 'SEBI'
            }
        except Exception as e:
            logger.warning(f"Error parsing press release: {e}")
            return None
    
    def scrape_all(self, max_pages: int = 10) -> pd.DataFrame:
        """Scrape all SEBI sources and combine"""
        logger.info("Starting comprehensive SEBI scraping...")
        
        orders_df = self.scrape_enforcement_orders(max_pages)
        releases_df = self.scrape_press_releases(max_pages)
        
        combined_df = pd.concat([orders_df, releases_df], ignore_index=True)
        
        # Save combined dataset
        output_file = self.output_dir / f"sebi_combined_{datetime.now().strftime('%Y%m%d')}.csv"
        combined_df.to_csv(output_file, index=False)
        logger.info(f"Combined dataset saved to {output_file}")
        
        return combined_df


if __name__ == "__main__":
    # Example usage
    scraper = SEBIScraper()
    df = scraper.scrape_all(max_pages=5)
    print(f"\nScraped {len(df)} SEBI documents")
    print("\nSample data:")
    print(df.head())
    print(f"\nLabel distribution:\n{df['label'].value_counts()}")
