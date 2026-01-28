"""
Download and integrate existing financial sentiment datasets

This script downloads publicly available financial sentiment datasets
to augment our Indian market-specific data.
"""

import pandas as pd
import requests
from pathlib import Path
import logging
from typing import List, Dict
import zipfile
import io

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FinancialDatasetDownloader:
    """Download existing financial sentiment datasets"""
    
    def __init__(self, output_dir: str = "data/external"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def download_financial_phrasebank(self) -> pd.DataFrame:
        """
        Download Financial PhraseBank dataset
        Contains 4,840 sentences from financial news categorized by sentiment
        
        Source: https://huggingface.co/datasets/financial_phrasebank
        """
        logger.info("Downloading Financial PhraseBank...")
        
        try:
            from datasets import load_dataset
            
            # Load from Hugging Face
            dataset = load_dataset("financial_phrasebank", "sentences_allagree", trust_remote_code=True)
            
            # Convert to DataFrame
            df = pd.DataFrame(dataset['train'])
            
            # Standardize columns
            df = df.rename(columns={'sentence': 'text'})
            
            # Map labels (0=negative, 1=neutral, 2=positive)
            label_map = {0: 'negative', 1: 'neutral', 2: 'positive'}
            df['label'] = df['label'].map(label_map)
            
            df['source'] = 'FinancialPhraseBank'
            df['title'] = df['text'].str[:100]
            
            # Save
            output_file = self.output_dir / "financial_phrasebank.csv"
            df.to_csv(output_file, index=False)
            logger.info(f"✓ Downloaded {len(df)} sentences from Financial PhraseBank")
            logger.info(f"Saved to {output_file}")
            
            return df
        
        except Exception as e:
            logger.error(f"Failed to download Financial PhraseBank: {e}")
            logger.info("Install datasets library: pip install datasets")
            return pd.DataFrame()
    
    def download_twitter_financial_news(self) -> pd.DataFrame:
        """
        Download Twitter Financial News Sentiment dataset
        Contains ~11,000+ tweets about financial topics
        
        Source: https://huggingface.co/datasets/zeroshot/twitter-financial-news-sentiment
        """
        logger.info("Downloading Twitter Financial News Sentiment...")
        
        try:
            from datasets import load_dataset
            
            dataset = load_dataset("zeroshot/twitter-financial-news-sentiment")
            
            # Convert to DataFrame
            df = pd.DataFrame(dataset['train'])
            
            # Standardize columns
            if 'text' not in df.columns and 'sentence' in df.columns:
                df = df.rename(columns={'sentence': 'text'})
            
            # Map labels if needed
            if 'label' in df.columns and df['label'].dtype in ['int64', 'int32']:
                label_map = {0: 'negative', 1: 'neutral', 2: 'positive'}
                df['label'] = df['label'].map(label_map)
            
            df['source'] = 'TwitterFinancialNews'
            df['title'] = df['text'].str[:100]
            
            # Save
            output_file = self.output_dir / "twitter_financial_news.csv"
            df.to_csv(output_file, index=False)
            logger.info(f"✓ Downloaded {len(df)} tweets from Twitter Financial News")
            logger.info(f"Saved to {output_file}")
            
            return df
        
        except Exception as e:
            logger.error(f"Failed to download Twitter Financial News: {e}")
            return pd.DataFrame()
    
    def download_sentiment140(self) -> pd.DataFrame:
        """
        Download Sentiment140 dataset (subset of financial tweets)
        Note: This is a large dataset, we'll take a sample
        """
        logger.info("Downloading sample from Sentiment140...")
        
        try:
            from datasets import load_dataset
            
            # Load small subset
            dataset = load_dataset("sentiment140", split="train[:5000]")
            
            df = pd.DataFrame(dataset)
            
            # Filter for financial keywords
            financial_keywords = [
                'stock', 'market', 'shares', 'trading', 'profit', 
                'revenue', 'earnings', 'dividend', 'invest', 'portfolio'
            ]
            
            keyword_pattern = '|'.join(financial_keywords)
            df = df[df['text'].str.contains(keyword_pattern, case=False, na=False)]
            
            # Map labels
            label_map = {0: 'negative', 2: 'neutral', 4: 'positive'}
            df['label'] = df['sentiment'].map(label_map)
            
            df['source'] = 'Sentiment140'
            df['title'] = df['text'].str[:100]
            
            # Keep only needed columns
            df = df[['text', 'label', 'source', 'title']]
            
            output_file = self.output_dir / "sentiment140_financial.csv"
            df.to_csv(output_file, index=False)
            logger.info(f"✓ Downloaded {len(df)} financial tweets from Sentiment140")
            
            return df
        
        except Exception as e:
            logger.error(f"Failed to download Sentiment140: {e}")
            return pd.DataFrame()
    
    def download_all_datasets(self) -> pd.DataFrame:
        """Download all available datasets"""
        logger.info("="*50)
        logger.info("Downloading existing financial sentiment datasets...")
        logger.info("="*50)
        
        all_datasets = []
        
        # Financial PhraseBank
        fpb_df = self.download_financial_phrasebank()
        if not fpb_df.empty:
            all_datasets.append(fpb_df)
        
        # Twitter Financial News
        tfn_df = self.download_twitter_financial_news()
        if not tfn_df.empty:
            all_datasets.append(tfn_df)
        
        # Sentiment140 subset
        s140_df = self.download_sentiment140()
        if not s140_df.empty:
            all_datasets.append(s140_df)
        
        if all_datasets:
            combined_df = pd.concat(all_datasets, ignore_index=True)
            
            # Standardize columns
            required_cols = ['text', 'label', 'source']
            for col in required_cols:
                if col not in combined_df.columns:
                    combined_df[col] = ''
            
            # Clean and deduplicate
            combined_df = combined_df[combined_df['text'].str.len() >= 20]
            combined_df = combined_df.drop_duplicates(subset=['text'])
            
            # Save combined
            output_file = self.output_dir / "external_datasets_combined.csv"
            combined_df.to_csv(output_file, index=False)
            
            logger.info("\n" + "="*50)
            logger.info(f"✓ Downloaded total: {len(combined_df)} labeled examples")
            logger.info(f"Saved to: {output_file}")
            logger.info("="*50)
            
            self._print_stats(combined_df)
            
            return combined_df
        else:
            logger.warning("No datasets downloaded successfully")
            return pd.DataFrame()
    
    def _print_stats(self, df: pd.DataFrame):
        """Print dataset statistics"""
        print("\nDataset Statistics:")
        print(f"Total examples: {len(df):,}")
        
        if 'source' in df.columns:
            print("\nSource distribution:")
            print(df['source'].value_counts().to_string())
        
        if 'label' in df.columns:
            print("\nLabel distribution:")
            print(df['label'].value_counts().to_string())
        
        print(f"\nText length stats:")
        print(f"  Mean: {df['text'].str.len().mean():.1f}")
        print(f"  Median: {df['text'].str.len().median():.1f}")


def main():
    """Main function"""
    downloader = FinancialDatasetDownloader()
    df = downloader.download_all_datasets()
    
    if not df.empty:
        print("\n✓ External datasets downloaded successfully!")
        print("These will be combined with Indian market data during training.")
        return 0
    else:
        print("\n✗ Failed to download datasets")
        print("Make sure you have 'datasets' library installed:")
        print("  pip install datasets")
        return 1


if __name__ == "__main__":
    exit(main())
