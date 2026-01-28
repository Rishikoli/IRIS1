"""
Data Preprocessing and Train/Val/Test Split

Prepares the collected data for FinBERT fine-tuning by:
1. Loading the combined dataset
2. Cleaning and standardizing labels
3. Splitting into train (70%), validation (15%), test (15%)
4. Saving splits in formats ready for training
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataPreprocessor:
    """Preprocess and split data for FinBERT fine-tuning"""
    
    def __init__(self, input_file: str, output_dir: str = "data/splits"):
        self.input_file = Path(input_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Label mapping
        self.label2id = {'negative': 0, 'neutral': 1, 'positive': 2}
        self.id2label = {0: 'negative', 1: 'neutral', 2: 'positive'}
    
    def load_data(self) -> pd.DataFrame:
        """Load and initial cleaning"""
        logger.info(f"Loading data from {self.input_file}...")
        
        df = pd.read_csv(self.input_file)
        initial_count = len(df)
        
        # Ensure required columns exist
        if 'text' not in df.columns or 'label' not in df.columns:
            raise ValueError("Dataset must have 'text' and 'label' columns")
        
        # Clean text
        df['text'] = df['text'].astype(str).str.strip()
        
        # Remove empty or very short texts
        df = df[df['text'].str.len() >= 20]
        
        # Standardize labels (lowercase)
        df['label'] = df['label'].str.lower().str.strip()
        
        # Keep only valid labels
        valid_labels = ['positive', 'negative', 'neutral']
        df = df[df['label'].isin(valid_labels)]
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['text'])
        
        logger.info(f"Loaded {len(df)} examples (filtered from {initial_count})")
        logger.info(f"Label distribution:\n{df['label'].value_counts()}")
        
        return df
    
    def create_splits(self, df: pd.DataFrame, train_size: float = 0.7, 
                     val_size: float = 0.15, test_size: float = 0.15, 
                     random_state: int = 42) -> tuple:
        """
        Create stratified train/val/test splits
        
        Returns:
            (train_df, val_df, test_df)
        """
        assert abs(train_size + val_size + test_size - 1.0) < 0.01, "Sizes must sum to 1.0"
        
        logger.info(f"Creating splits: train={train_size}, val={val_size}, test={test_size}")
        
        # First split: train vs (val + test)
        train_df, temp_df = train_test_split(
            df, 
            test_size=(val_size + test_size),
            stratify=df['label'],
            random_state=random_state
        )
        
        # Second split: val vs test
        val_ratio = val_size / (val_size + test_size)
        val_df, test_df = train_test_split(
            temp_df,
            test_size=(1 - val_ratio),
            stratify=temp_df['label'],
            random_state=random_state
        )
        
        logger.info(f"Train: {len(train_df)} examples")
        logger.info(f"Val: {len(val_df)} examples")
        logger.info(f"Test: {len(test_df)} examples")
        
        # Print label distributions
        for name, split_df in [('Train', train_df), ('Val', val_df), ('Test', test_df)]:
            logger.info(f"\n{name} label distribution:")
            logger.info(f"{split_df['label'].value_counts()}")
        
        return train_df, val_df, test_df
    
    def add_label_ids(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add numeric label IDs"""
        df = df.copy()
        df['label_id'] = df['label'].map(self.label2id)
        return df
    
    def save_splits(self, train_df: pd.DataFrame, val_df: pd.DataFrame, 
                   test_df: pd.DataFrame):
        """Save splits as CSV files"""
        
        # Add label IDs
        train_df = self.add_label_ids(train_df)
        val_df = self.add_label_ids(val_df)
        test_df = self.add_label_ids(test_df)
        
        # Save
        train_file = self.output_dir / "train.csv"
        val_file = self.output_dir / "val.csv"
        test_file = self.output_dir / "test.csv"
        
        train_df.to_csv(train_file, index=False)
        val_df.to_csv(val_file, index=False)
        test_df.to_csv(test_file, index=False)
        
        logger.info(f"\nSaved splits to {self.output_dir}:")
        logger.info(f"  - {train_file.name} ({len(train_df)} examples)")
        logger.info(f"  - {val_file.name} ({len(val_df)} examples)")
        logger.info(f"  - {test_file.name} ({len(test_df)} examples)")
        
        return train_file, val_file, test_file
    
    def preprocess(self):
        """Main preprocessing pipeline"""
        logger.info("="*50)
        logger.info("Starting data preprocessing...")
        logger.info("="*50)
        
        # Load data
        df = self.load_data()
        
        # Create splits
        train_df, val_df, test_df = self.create_splits(df)
        
        # Save
        train_file, val_file, test_file = self.save_splits(train_df, val_df, test_df)
        
        logger.info("\n" + "="*50)
        logger.info("✓ Preprocessing complete!")
        logger.info("="*50)
        
        return {
            'train': train_file,
            'val': val_file,
            'test': test_file,
            'train_size': len(train_df),
            'val_size': len(val_df),
            'test_size': len(test_df)
        }


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Preprocess data for FinBERT fine-tuning')
    parser.add_argument('--input', type=str, 
                       default='src/ml/data_collection/data/processed/finbert_training_data_20260122_005123.csv',
                       help='Path to combined dataset')
    parser.add_argument('--output-dir', type=str, default='src/ml/data/splits',
                       help='Output directory for splits')
    parser.add_argument('--train-size', type=float, default=0.7,
                       help='Train split size (default: 0.7)')
    parser.add_argument('--val-size', type=float, default=0.15,
                       help='Validation split size (default: 0.15)')
    parser.add_argument('--test-size', type=float, default=0.15,
                       help='Test split size (default: 0.15)')
    
    args = parser.parse_args()
    
    # Preprocess
    preprocessor = DataPreprocessor(args.input, args.output_dir)
    df = preprocessor.load_data()
    train_df, val_df, test_df = preprocessor.create_splits(
        df, args.train_size, args.val_size, args.test_size
    )
    preprocessor.save_splits(train_df, val_df, test_df)
    
    print("\n✓ Data preprocessing complete!")
    print(f"Next step: Run fine-tuning with: python train_finbert.py")


if __name__ == "__main__":
    main()
