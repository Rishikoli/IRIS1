"""
Enhanced News Scraper with Archive Crawling

Crawls news website archives to get more articles beyond RSS feed limits.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict
import time
import logging
from pathlib import Path
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewsArchiveScraper:
    """Scraper for news website archives (beyond RSS limits)"""
    
    def __init__(self, output_dir: str = "data/raw/news"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_economictimes_archive(self, days_back: int = 90, max_articles: int = 2000) -> pd.DataFrame:
        """
        Scrape Economic Times market news archive
        
        Args:
            days_back: How many days back to search
            max_articles: Maximum articles to collect
        """
        logger.info(f"Scraping Economic Times archive for last {days_back} days...")
        
        articles = []
        base_url = "https://economictimes.indiatimes.com/markets/stocks/news"
        
        try:
            # Try paginated archive URLs
            for page in range(1, 50):  # Try up to 50 pages
                try:
                    url = f"{base_url}?curpg={page}" if page > 1 else base_url
                    response = self.session.get(url, timeout=10)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Find article links
                    article_links = soup.find_all('a', class_='story-title')
                    if not article_links:
                        article_links = soup.find_all('h3')
                    
                    if not article_links:
                        logger.info(f"No more articles found at page {page}")
                        break
                    
                    for link in article_links:
                        try:
                            if isinstance(link, dict):
                                continue
                            
                            a_tag = link if link.name == 'a' else link.find('a')
                            if not a_tag:
                                continue
                            
                            title = a_tag.get_text(strip=True)
                            href = a_tag.get('href', '')
                            
                            if not href or len(title) < 20:
                                continue
                            
                            if not href.startswith('http'):
                                href = f"https://economictimes.indiatimes.com{href}"
                            
                            # Extract full article
                            article_text = self._extract_article_text(href, 'economictimes')
                            
                            articles.append({
                                'title': title,
                                'text': article_text if article_text else title,
                                'url': href,
                                'source': 'economictimes',
                                'date': datetime.now().strftime('%Y-%m-%d'),
                                'label': 'neutral'
                            })
                            
                            if len(articles) >= max_articles:
                                break
                        
                        except Exception as e:
                            continue
                    
                    logger.info(f"Page {page}: collected {len(articles)} total articles")
                    
                    if len(articles) >= max_articles:
                        break
                    
                    time.sleep(2)
                
                except Exception as e:
                    logger.error(f"Error on page {page}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Archive scraping failed: {e}")
        
        df = pd.DataFrame(articles)
        logger.info(f"Collected {len(df)} articles from ET archive")
        return df
    
    def scrape_moneycontrol_archive(self, max_articles: int = 2000) -> pd.DataFrame:
        """Scrape Moneycontrol market news archive"""
        logger.info("Scraping Moneycontrol archive...")
        
        articles = []
        base_url = "https://www.moneycontrol.com/news/business/stocks/"
        
        try:
            for page in range(1, 100):
                try:
                    url = f"{base_url}page-{page}/" if page > 1 else base_url
                    response = self.session.get(url, timeout=10)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    article_items = soup.find_all('li', class_='clearfix')
                    
                    if not article_items:
                        article_items = soup.find_all('h2')
                    
                    if not article_items:
                        break
                    
                    for item in article_items:
                        try:
                            a_tag = item.find('a')
                            if not a_tag:
                                continue
                            
                            title = a_tag.get_text(strip=True)
                            href = a_tag.get('href', '')
                            
                            if len(title) < 20 or not href:
                                continue
                            
                            article_text = self._extract_article_text(href, 'moneycontrol')
                            
                            articles.append({
                                'title': title,
                                'text': article_text if article_text else title,
                                'url': href,
                                'source': 'moneycontrol',
                                'date': datetime.now().strftime('%Y-%m-%d'),
                                'label': 'neutral'
                            })
                            
                            if len(articles) >= max_articles:
                                break
                        
                        except Exception as e:
                            continue
                    
                    logger.info(f"Page {page}: collected {len(articles)} total articles")
                    
                    if len(articles) >= max_articles:
                        break
                    
                    time.sleep(2)
                
                except Exception as e:
                    logger.error(f"Error on page {page}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Moneycontrol archive failed: {e}")
        
        df = pd.DataFrame(articles)
        logger.info(f"Collected {len(df)} articles from Moneycontrol archive")
        return df
    
    def _extract_article_text(self, url: str, source: str) -> str:
        """Extract full article text"""
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Source-specific selectors
            selectors = {
                'economictimes': ['div.artText', 'div.Normal'],
                'moneycontrol': ['div.content_wrapper p', 'div.article p'],
                'businessstandard': ['div.story-content p'],
                'livemint': ['div.  p']
            }
            
            content_selectors = selectors.get(source, ['article p', 'div.content p'])
            
            paragraphs = []
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    paragraphs = [p.get_text(strip=True) for p in elements]
                    break
            
            if not paragraphs:
                # Fallback: get all paragraphs
                paragraphs = [p.get_text(strip=True) for p in soup.find_all('p')]
            
            text = ' '.join(paragraphs)
            
            # Clean
            text = re.sub(r'\s+', ' ', text)
            return text[:2000]
        
        except Exception as e:
            return ""
    
    def scrape_all_archives(self, max_per_source: int = 2000) -> pd.DataFrame:
        """Scrape all news archives"""
        logger.info("Scraping all news archives...")
        
        all_articles = []
        
        # Economic Times
        et_df = self.scrape_economictimes_archive(days_back=90, max_articles=max_per_source)
        if not et_df.empty:
            all_articles.append(et_df)
        
        time.sleep(5)
        
        # Moneycontrol
        mc_df = self.scrape_moneycontrol_archive(max_articles=max_per_source)
        if not mc_df.empty:
            all_articles.append(mc_df)
        
        if all_articles:
            combined = pd.concat(all_articles, ignore_index=True)
            combined = combined.drop_duplicates(subset=['title'])
            
            output_file = self.output_dir / f"news_archive_{datetime.now().strftime('%Y%m%d')}.csv"
            combined.to_csv(output_file, index=False)
            logger.info(f"Saved {len(combined)} archive articles to {output_file}")
            
            return combined
        
        return pd.DataFrame()


if __name__ == "__main__":
    scraper = NewsArchiveScraper()
    df = scraper.scrape_all_archives(max_per_source=2000)
    print(f"\nScraped {len(df)} articles from archives")
