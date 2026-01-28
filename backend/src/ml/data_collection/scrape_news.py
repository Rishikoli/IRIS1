"""
Financial News Scraper

Scrapes financial news from Indian sources:
- Economic Times
- Business Standard  
- Moneycontrol
- LiveMint (Market, Companies, Economy)
- Hindu Business Line (Markets, Portfolio)
- Financial Express (Market, Economy)
- Bloomberg Quint (Markets, Business)
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from typing import List, Dict
import time
import logging
from pathlib import Path
import feedparser
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FinancialNewsScraper:
    """Scraper for Indian financial news websites"""
    
    SOURCES = {
        'economictimes': {
            'url': 'https://economictimes.indiatimes.com',
            'rss': 'https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms'
        },
        'moneycontrol': {
            'url': 'https://www.moneycontrol.com',
            'rss': 'https://www.moneycontrol.com/rss/marketreports.xml'
        },
        'businessstandard': {
            'url': 'https://www.business-standard.com',
            'rss': 'https://www.business-standard.com/rss/markets-106.rss'
        },
        'livemint': {
            'url': 'https://www.livemint.com',
            'rss': 'https://www.livemint.com/rss/market'
        },
        'livemint_companies': {
            'url': 'https://www.livemint.com',
            'rss': 'https://www.livemint.com/rss/companies'
        },
        'livemint_economy': {
            'url': 'https://www.livemint.com',
            'rss': 'https://www.livemint.com/rss/economy'
        },
        'thehindubusinessline': {
            'url': 'https://www.thehindubusinessline.com',
            'rss': 'https://www.thehindubusinessline.com/markets/?service=rss'
        },
        'thehindubusinessline_portfolio': {
            'url': 'https://www.thehindubusinessline.com',
            'rss': 'https://www.thehindubusinessline.com/portfolio/?service=rss'
        },
        'financialexpress': {
            'url': 'https://www.financialexpress.com',
            'rss': 'https://www.financialexpress.com/market/feed/'
        },
        'financialexpress_economy': {
            'url': 'https://www.financialexpress.com',
            'rss': 'https://www.financialexpress.com/economy/feed/'
        },
        'bloombergquint': {
            'url': 'https://www.bloombergquint.com',
            'rss': 'https://www.bloombergquint.com/feed/markets'
        },
        'bloombergquint_business': {
            'url': 'https://www.bloombergquint.com',
            'rss': 'https://www.bloombergquint.com/feed/business'
        }
    }
    
    def __init__(self, output_dir: str = "data/raw/news"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_rss_feed(self, source_name: str, max_articles: int = 500) -> pd.DataFrame:
        """
        Scrape articles from RSS feed
        
        Args:
            source_name: Name of the source (e.g., 'economictimes')
            max_articles: Maximum number of articles to scrape
            
        Returns:
            DataFrame with article data
        """
        if source_name not in self.SOURCES:
            logger.error(f"Unknown source: {source_name}")
            return pd.DataFrame()
        
        logger.info(f"Scraping {source_name} RSS feed...")
        
        rss_url = self.SOURCES[source_name]['rss']
        articles = []
        
        try:
            feed = feedparser.parse(rss_url)
            
            for entry in feed.entries[:max_articles]:
                try:
                    article = {
                        'title': entry.get('title', ''),
                        'text': entry.get('summary', entry.get('description', '')),
                        'url': entry.get('link', ''),
                        'date': entry.get('published', ''),
                        'source': source_name,
                        'label': 'neutral'  # Will be labeled later
                    }
                    
                    # Clean HTML tags from summary
                    article['text'] = self._clean_html(article['text'])
                    
                    # Try to get full article text
                    if article['url']:
                        full_text = self._extract_article_text(article['url'], source_name)
                        if full_text:
                            article['text'] = full_text
                    
                    articles.append(article)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse RSS entry: {e}")
                    continue
                
                time.sleep(0.5)  # Be respectful
            
            logger.info(f"Scraped {len(articles)} articles from {source_name}")
            
        except Exception as e:
            logger.error(f"Error scraping RSS feed from {source_name}: {e}")
        
        df = pd.DataFrame(articles)
        
        if not df.empty:
            output_file = self.output_dir / f"{source_name}_{datetime.now().strftime('%Y%m%d')}.csv"
            df.to_csv(output_file, index=False)
            logger.info(f"Saved to {output_file}")
        
        return df
    
    def _extract_article_text(self, url: str, source_name: str) -> str:
        """Extract full article text from URL"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Different selectors for different sources
            content_selectors = {
                'economictimes': ['div.artText', 'div.artData'],
                'moneycontrol': ['div.content_wrapper', 'div.article'],
                'businessstandard': ['div.story-content', 'div.main-story'],
                'livemint': ['div.article-content', 'div.FirstEle'],
                'livemint_companies': ['div.article-content', 'div.FirstEle'],
                'livemint_economy': ['div.article-content', 'div.FirstEle'],
                'thehindubusinessline': ['div.articlebodycontent', 'div.article-text'],
                'thehindubusinessline_portfolio': ['div.articlebodycontent', 'div.article-text'],
                'financialexpress': ['div.main-story', 'div.story-content'],
                'financialexpress_economy': ['div.main-story', 'div.story-content'],
                'bloombergquint': ['div.story-content', 'div.article-body'],
                'bloombergquint_business': ['div.story-content', 'div.article-body']
            }
            
            selectors = content_selectors.get(source_name, ['article', 'div.content'])
            
            content = None
            for selector in selectors:
                content = soup.select_one(selector)
                if content:
                    break
            
            if content:
                # Extract paragraphs
                paragraphs = content.find_all('p')
                text = ' '.join([p.get_text(strip=True) for p in paragraphs])
                
                # Clean and limit length
                text = self._clean_text(text)
                return text[:2000]  # Limit to 2000 chars
            
            return ""
            
        except Exception as e:
            logger.debug(f"Failed to extract article from {url}: {e}")
            return ""
    
    def _clean_html(self, text: str) -> str:
        """Remove HTML tags from text"""
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        return text.strip()
    
    def scrape_all_sources(self, max_articles_per_source: int = 500) -> pd.DataFrame:
        """Scrape all configured news sources"""
        logger.info("Starting comprehensive news scraping...")
        
        all_articles = []
        
        for source_name in self.SOURCES.keys():
            try:
                df = self.scrape_rss_feed(source_name, max_articles_per_source)
                if not df.empty:
                    all_articles.append(df)
                
                time.sleep(2)  # Delay between sources
                
            except Exception as e:
                logger.error(f"Error scraping {source_name}: {e}")
                continue
        
        if all_articles:
            combined_df = pd.concat(all_articles, ignore_index=True)
            
            # Remove duplicates based on title
            combined_df = combined_df.drop_duplicates(subset=['title'])
            
            # Filter out very short articles
            combined_df = combined_df[combined_df['text'].str.len() > 50]
            
            # Save combined dataset
            output_file = self.output_dir / f"news_combined_{datetime.now().strftime('%Y%m%d')}.csv"
            combined_df.to_csv(output_file, index=False)
            logger.info(f"Combined news dataset saved to {output_file}")
            
            return combined_df
        else:
            logger.warning("No articles scraped from any source")
            return pd.DataFrame()
    
    def scrape_company_news(self, company_name: str, max_articles: int = 50) -> pd.DataFrame:
        """
        Scrape news articles about a specific company
        
        Args:
            company_name: Name of the company (e.g., 'Reliance', 'TCS')
            max_articles: Maximum articles to find
            
        Returns:
            DataFrame with company-specific news
        """
        logger.info(f"Searching for news about {company_name}...")
        
        # Scrape all sources and filter for company
        all_news = self.scrape_all_sources(max_articles_per_source=max_articles * 2)
        
        if all_news.empty:
            return pd.DataFrame()
        
        # Filter for company mentions
        company_news = all_news[
            all_news['title'].str.contains(company_name, case=False, na=False) |
            all_news['text'].str.contains(company_name, case=False, na=False)
        ]
        
        logger.info(f"Found {len(company_news)} articles about {company_name}")
        
        return company_news[:max_articles]


if __name__ == "__main__":
    # Example usage
    scraper = FinancialNewsScraper()
    
    # Scrape all sources
    df = scraper.scrape_all_sources(max_articles_per_source=50)
    
    if not df.empty:
        print(f"\nScraped {len(df)} news articles")
        print(f"\nSource distribution:\n{df['source'].value_counts()}")
        print("\nSample articles:")
        for _, row in df.head(3).iterrows():
            print(f"\n[{row['source']}] {row['title']}")
            print(f"Text preview: {row['text'][:200]}...")
