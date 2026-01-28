"""
FinBERT Fine-tuning Script

Fine-tunes the pre-trained FinBERT model on Indian market-specific financial sentiment data.
"""

import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments,
    EarlyStoppingCallback
)
from datasets import load_dataset, Dataset
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
import numpy as np
import pandas as pd
from pathlib import Path
import logging
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FinBERTFineTuner:
    """Fine-tune FinBERT for financial sentiment analysis"""
    
    def __init__(self, 
                 model_name: str = "ProsusAI/finbert",
                 output_dir: str = "models/finbert_indian",
                 max_length: int = 512):
        
        self.model_name = model_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.max_length = max_length
        
        # Label mappings
        self.label2id = {'negative': 0, 'neutral': 1, 'positive': 2}
        self.id2label = {0: 'negative', 1: 'neutral', 2: 'positive'}
        
        logger.info(f"Initializing fine-tuner with model: {model_name}")
        
        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name,
            num_labels=3,
            id2label=self.id2label,
            label2id=self.label2id
        )
        
        logger.info(f"Model loaded successfully")
        logger.info(f"Device: {'cuda' if torch.cuda.is_available() else 'cpu'}")
    
    def load_data(self, train_file: str, val_file: str, test_file: str):
        """Load train/val/test datasets"""
        logger.info("Loading datasets...")
        
        dataset = load_dataset('csv', data_files={
            'train': train_file,
            'validation': val_file,
            'test': test_file
        })
        
        logger.info(f"Train: {len(dataset['train'])} examples")
        logger.info(f"Val: {len(dataset['validation'])} examples")
        logger.info(f"Test: {len(dataset['test'])} examples")
        
        return dataset
    
    def tokenize_function(self, examples):
        """Tokenize texts"""
        return self.tokenizer(
            examples['text'],
            padding='max_length',
            truncation=True,
            max_length=self.max_length
        )
    
    def preprocess_datasets(self, dataset):
        """Tokenize and prepare datasets"""
        logger.info("Tokenizing datasets...")
        
        # Tokenize
        tokenized_datasets = dataset.map(
            self.tokenize_function,
            batched=True,
            remove_columns=['text']
        )
        
        # Rename label_id to labels (required by Trainer)
        tokenized_datasets = tokenized_datasets.rename_column('label_id', 'labels')
        
        # Set format
        tokenized_datasets.set_format('torch', columns=['input_ids', 'attention_mask', 'labels'])
        
        return tokenized_datasets
    
    def compute_metrics(self, eval_pred):
        """Compute metrics for evaluation"""
        logits, labels = eval_pred
        predictions = np.argmax(logits, axis=-1)
        
        # Calculate metrics
        precision, recall, f1, _ = precision_recall_fscore_support(
            labels, predictions, average='weighted', zero_division=0
        )
        acc = accuracy_score(labels, predictions)
        
        # Per-class metrics
        precision_per_class, recall_per_class, f1_per_class, _ = precision_recall_fscore_support(
            labels, predictions, average=None, zero_division=0
        )
        
        metrics = {
            'accuracy': acc,
            'f1': f1,
            'precision': precision,
            'recall': recall,
            'f1_negative': f1_per_class[0],
            'f1_neutral': f1_per_class[1],
            'f1_positive': f1_per_class[2],
        }
        
        return metrics
    
    def train(self, tokenized_datasets, 
             learning_rate: float = 2e-5,
             batch_size: int = 16,
             num_epochs: int = 5,
             weight_decay: float = 0.01,
             warmup_steps: int = 500):
        """Fine-tune the model"""
        
        logger.info("Setting up training...")
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=str(self.output_dir),
            eval_strategy='epoch',
            save_strategy='epoch',
            learning_rate=learning_rate,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            num_train_epochs=num_epochs,
            weight_decay=weight_decay,
            load_best_model_at_end=True,
            metric_for_best_model='f1',
            greater_is_better=True,
            logging_dir=str(self.output_dir / 'logs'),
            logging_steps=100,
            save_total_limit=3,
            warmup_steps=warmup_steps,
            fp16=torch.cuda.is_available(),  # Mixed precision if GPU available
            report_to='none',  # Disable wandb/tensorboard for now
            seed=42
        )
        
        # Initialize Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_datasets['train'],
            eval_dataset=tokenized_datasets['validation'],
            compute_metrics=self.compute_metrics,
            callbacks=[EarlyStoppingCallback(early_stopping_patience=2)]
        )
        
        # Train
        logger.info("="*50)
        logger.info("Starting training...")
        logger.info("="*50)
        
        train_result = trainer.train()
        
        # Save model
        logger.info("Saving model...")
        trainer.save_model(str(self.output_dir / 'final'))
        self.tokenizer.save_pretrained(str(self.output_dir / 'final'))
        
        # Save training metrics
        metrics_file = self.output_dir / 'training_metrics.json'
        with open(metrics_file, 'w') as f:
            json.dump(train_result.metrics, f, indent=2)
        
        logger.info(f"Training complete! Model saved to {self.output_dir / 'final'}")
        
        return trainer
    
    def evaluate(self, trainer, tokenized_datasets):
        """Evaluate on test set"""
        logger.info("="*50)
        logger.info("Evaluating on test set...")
        logger.info("="*50)
        
        test_results = trainer.evaluate(tokenized_datasets['test'])
        
        logger.info("Test Results:")
        for key, value in test_results.items():
            logger.info(f"  {key}: {value:.4f}")
        
        # Save test results
        results_file = self.output_dir / 'test_results.json'
        with open(results_file, 'w') as f:
            json.dump(test_results, f, indent=2)
        
        # Get predictions for confusion matrix
        predictions_output = trainer.predict(tokenized_datasets['test'])
        predictions = np.argmax(predictions_output.predictions, axis=-1)
        labels = predictions_output.label_ids
        
        # Confusion matrix
        cm = confusion_matrix(labels, predictions)
        
        logger.info("\nConfusion Matrix:")
        logger.info("               Predicted")
        logger.info("              Neg  Neu  Pos")
        for i, row in enumerate(cm):
            label_name = self.id2label[i][:3]
            logger.info(f"Actual {label_name}  {row[0]:4d} {row[1]:4d} {row[2]:4d}")
        
        # Save confusion matrix
        cm_df = pd.DataFrame(cm, 
                            index=['Actual_Neg', 'Actual_Neu', 'Actual_Pos'],
                            columns=['Pred_Neg', 'Pred_Neu', 'Pred_Pos'])
        cm_df.to_csv(self.output_dir / 'confusion_matrix.csv')
        
        return test_results


def main():
    """Main training function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fine-tune FinBERT')
    parser.add_argument('--train-file', type=str, default='src/ml/data/splits/train.csv',
                       help='Path to training data')
    parser.add_argument('--val-file', type=str, default='src/ml/data/splits/val.csv',
                       help='Path to validation data')
    parser.add_argument('--test-file', type=str, default='src/ml/data/splits/test.csv',
                       help='Path to test data')
    parser.add_argument('--model-name', type=str, default='ProsusAI/finbert',
                       help='Pre-trained model name')
    parser.add_argument('--output-dir', type=str, default='models/finbert_indian',
                       help='Output directory for fine-tuned model')
    parser.add_argument('--learning-rate', type=float, default=2e-5,
                       help='Learning rate')
    parser.add_argument('--batch-size', type=int, default=16,
                       help='Batch size')
    parser.add_argument('--epochs', type=int, default=5,
                       help='Number of training epochs')
    
    args = parser.parse_args()
    
    # Initialize fine-tuner
    fine_tuner = FinBERTFineTuner(
        model_name=args.model_name,
        output_dir=args.output_dir
    )
    
    # Load data
    dataset = fine_tuner.load_data(args.train_file, args.val_file, args.test_file)
    
    # Preprocess
    tokenized_datasets = fine_tuner.preprocess_datasets(dataset)
    
    # Train
    trainer = fine_tuner.train(
        tokenized_datasets,
        learning_rate=args.learning_rate,
        batch_size=args.batch_size,
        num_epochs=args.epochs
    )
    
    # Evaluate
    fine_tuner.evaluate(trainer, tokenized_datasets)
    
    print("\n✓ Fine-tuning complete!")
    print(f"Model saved to: {args.output_dir}/final")


if __name__ == "__main__":
    main()
