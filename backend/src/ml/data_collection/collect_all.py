"""
Master Data Collection Orchestrator

Runs all data collection scrapers and combines the results into a unified dataset
for FinBERT fine-tuning.
"""

import pandas as pd
from pathlib import Path
import logging
from datetime import datetime
import argparse

from scrape_sebi import SEBIScraper
from scrape_bse_nse import BSENSEScraper
from scrape_news import FinancialNewsScraper
from scrape_news_archive import NewsArchiveScraper
from download_datasets import FinancialDatasetDownloader
from process_pdfs import PDFProcessor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataCollectionOrchestrator:
    """Orchestrate all data collection processes"""
    
    def __init__(self, output_dir: str = "data/processed"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def collect_all_data(
        self,
        sebi_pages: int = 20,
        exchange_days: int = 60,
        exchange_max: int = 2000,
        news_per_source: int = 500,
        news_archive_per_source: int = 2000,
        process_pdfs: bool = True,
        download_external: bool = True
    ) -> pd.DataFrame:
        """
        Run all data collection processes
        
        Args:
            sebi_pages: Number of pages to scrape from SEBI
            exchange_days: Days to look back for exchange announcements
            exchange_max: Max exchange announcements per source
            news_per_source: Max news articles per source (RSS)
            news_archive_per_source: Max archive articles per source (deep scrape)
            process_pdfs: Whether to process PDFs
            download_external: Whether to download external datasets
            
        Returns:
            Combined DataFrame with all collected data
        """
        logger.info("="*50)
        logger.info("Starting comprehensive data collection...")
        logger.info("="*50)
        
        all_datasets = []
        
        # 1. Collect SEBI data
        logger.info("\n[1/4] Collecting SEBI data...")
        try:
            sebi_scraper = SEBIScraper()
            sebi_df = sebi_scraper.scrape_all(max_pages=sebi_pages)
            if not sebi_df.empty:
                all_datasets.append(sebi_df)
                logger.info(f"✓ Collected {len(sebi_df)} SEBI records")
        except Exception as e:
            logger.error(f"✗ SEBI collection failed: {e}")
        
        # 2. Collect BSE/NSE data
        logger.info("\n[2/4] Collecting BSE/NSE announcements...")
        try:
            exchange_scraper = BSENSEScraper()
            exchange_df = exchange_scraper.scrape_all(days=exchange_days, max_records=exchange_max)
            if not exchange_df.empty:
                all_datasets.append(exchange_df)
                logger.info(f"✓ Collected {len(exchange_df)} exchange announcements")
        except Exception as e:
            logger.error(f"✗ Exchange collection failed: {e}")
        
        # 3. Collect financial news
        logger.info("\n[3/4] Collecting financial news...")
        try:
            news_scraper = FinancialNewsScraper()
            news_df = news_scraper.scrape_all_sources(max_articles_per_source=news_per_source)
            if not news_df.empty:
                all_datasets.append(news_df)
                logger.info(f"✓ Collected {len(news_df)} news articles")
        except Exception as e:
            logger.error(f"✗ News collection failed: {e}")
        
        # 4. Collect news from archives (deep scraping)
        logger.info("\n[4/6] Collecting news from archives (deep scraping)...")
        try:
            archive_scraper = NewsArchiveScraper()
            archive_df = archive_scraper.scrape_all_archives(max_per_source=news_archive_per_source)
            if not archive_df.empty:
                all_datasets.append(archive_df)
                logger.info(f"✓ Collected {len(archive_df)} articles from news archives")
        except Exception as e:
            logger.error(f"✗ News archive collection failed: {e}")
        
        # 5. Process PDFs
        if process_pdfs:
            logger.info("\n[5/6] Processing annual report PDFs...")
            try:
                pdf_processor = PDFProcessor()
                pdf_df = pdf_processor.process_directory()
                if not pdf_df.empty:
                    all_datasets.append(pdf_df)
                    logger.info(f"✓ Extracted {len(pdf_df)} sentences from PDFs")
            except Exception as e:
                logger.error(f"✗ PDF processing failed: {e}")
        
        # 6. Download external datasets
        if download_external:
            logger.info("\n[6/6] Downloading existing financial sentiment datasets...")
            try:
                dataset_downloader = FinancialDatasetDownloader()
                external_df = dataset_downloader.download_all_datasets()
                if not external_df.empty:
                    all_datasets.append(external_df)
                    logger.info(f"✓ Downloaded {len(external_df)} labeled examples from external sources")
            except Exception as e:
                logger.error(f"✗ External dataset download failed: {e}")
        
        # Combine all datasets
        if not all_datasets:
            logger.error("No data collected from any source!")
            return pd.DataFrame()
        
        logger.info("\nCombining all datasets...")
        combined_df = pd.concat(all_datasets, ignore_index=True)
        
        # Standardize columns
        required_cols = ['text', 'label', 'source']
        for col in required_cols:
            if col not in combined_df.columns:
                combined_df[col] = ''
        
        # Remove duplicates
        initial_count = len(combined_df)
        combined_df = combined_df.drop_duplicates(subset=['text'])
        logger.info(f"Removed {initial_count - len(combined_df)} duplicate entries")
        
        # Filter by text length
        combined_df = combined_df[combined_df['text'].str.len() >= 20]
        
        # Save combined dataset
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_dir / f"finbert_training_data_{timestamp}.csv"
        combined_df.to_csv(output_file, index=False)
        
        logger.info("\n" + "="*50)
        logger.info(f"✓ Collection complete!")
        logger.info(f"Total records: {len(combined_df)}")
        logger.info(f"Saved to: {output_file}")
        logger.info("="*50)
        
        # Print statistics
        self._print_statistics(combined_df)
        
        return combined_df
    
    def _print_statistics(self, df: pd.DataFrame):
        """Print dataset statistics"""
        print("\n" + "="*50)
        print("DATASET STATISTICS")
        print("="*50)
        
        print(f"\nTotal records: {len(df):,}")
        print(f"Unique texts: {df['text'].nunique():,}")
        
        if 'source' in df.columns:
            print("\nSource distribution:")
            print(df['source'].value_counts().to_string())
        
        if 'label' in df.columns:
            print("\nLabel distribution:")
            print(df['label'].value_counts().to_string())
        
        print(f"\nText length statistics:")
        print(f"  Min: {df['text'].str.len().min()}")
        print(f"  Max: {df['text'].str.len().max()}")
        print(f"  Mean: {df['text'].str.len().mean():.1f}")
        print(f"  Median: {df['text'].str.len().median():.1f}")
        
        print("\n" + "="*50)


def main():
    parser = argparse.ArgumentParser(description='Collect financial data for FinBERT fine-tuning')
    parser.add_argument('--sebi-pages', type=int, default=10, help='SEBI pages to scrape')
    parser.add_argument('--exchange-days', type=int, default=30, help='Days of exchange data')
    parser.add_argument('--exchange-max', type=int, default=1000, help='Max exchange records')
    parser.add_argument('--news-per-source', type=int, default=100, help='News articles per source')
    parser.add_argument('--skip-pdfs', action='store_true', help='Skip PDF processing')
    parser.add_argument('--output-dir', type=str, default='data/processed', help='Output directory')
    
    args = parser.parse_args()
    
    orchestrator = DataCollectionOrchestrator(output_dir=args.output_dir)
    
    df = orchestrator.collect_all_data(
        sebi_pages=args.sebi_pages,
        exchange_days=args.exchange_days,
        exchange_max=args.exchange_max,
        news_per_source=args.news_per_source,
        process_pdfs=not args.skip_pdfs
    )
    
    if not df.empty:
        print("\n✓ Data collection successful!")
        print(f"Next step: Label the data in: {orchestrator.output_dir}")
    else:
        print("\n✗ Data collection failed!")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
