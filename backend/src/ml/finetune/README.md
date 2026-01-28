# Fine-tuning FinBERT for Indian Markets

Complete pipeline for fine-tuning FinBERT on Indian market-specific financial sentiment data.

## 📊 Dataset Summary

- **Total examples**: 10,352
- **Training**: 7,246 (70%)
- **Validation**: 1,553 (15%)
- **Test**: 1,553 (15%)

**Label Distribution:**
- Positive: 6,129 (59%)
- Neutral: 2,756 (27%)
- Negative: 1,467 (14%)

**Data Sources:**
- Twitter Financial News: 9,486 (pre-labeled)
- Economic Times: 805
- SEBI Orders: 49
- LiveMint: 9
- Moneycontrol: 4
- BSE: 2

## 🚀 Quick Start

### 1. Data Preprocessing (Already Done ✓)

```bash
cd src/ml/finetune
python3 preprocess_data.py \
  --input ../data_collection/data/processed/finbert_training_data_20260122_005123.csv \
  --output-dir ../data/splits
```

**Output**: `src/ml/data/splits/` containing `train.csv`, `val.csv`, `test.csv`

### 2. Fine-tune FinBERT

```bash
python3 train_finbert.py \
  --train-file ../data/splits/train.csv \
  --val-file ../data/splits/val.csv \
  --test-file ../data/splits/test.csv \
  --output-dir ../../models/finbert_indian \
  --epochs 5 \
  --batch-size 16 \
  --learning-rate 2e-5
```

**Training time estimate:**
- **GPU (RTX 3060+)**: ~30-45 minutes
- **CPU**: ~3-4 hours

### 3. Evaluate Model

Automatically runs after training. Results saved to `models/finbert_indian/test_results.json`.

## 📝 Scripts

### `preprocess_data.py`
- Loads combined dataset
- Cleans and standardizes
- Creates stratified train/val/test splits
- Saves splits as CSV

### `train_finbert.py`
- Loads pre-trained FinBERT
- Fine-tunes on training data
- Evaluates on validation set
- Saves best model based on F1 score
- Generates confusion matrix
- Saves final model + metrics

## 🎯 Expected Results

Based on similar fine-tuning tasks:
- **Accuracy**: 80-85%
- **F1 Score (weighted)**: 0.78-0.83
- **Improvement over baseline**: +5-10%

## 📂 Output Structure

```
models/finbert_indian/
├── final/                      # Fine-tuned model
│   ├── pytorch_model.bin
│   ├── config.json
│   └── tokenizer files
├── logs/                       # Training logs
├── training_metrics.json       # Training metrics
├── test_results.json          # Test evaluation metrics
└── confusion_matrix.csv  # Confusion matrix
```

## 🔧 Advanced Options

### Adjust batch size (for less memory):
```bash
python3 train_finbert.py --batch-size 8
```

### More epochs:
```bash
python3 train_finbert.py --epochs 10
```

### Different base model:
```bash
python3 train_finbert.py --model-name yiyanghkust/finbert-tone
```

## 🚨 Troubleshooting

### Out of Memory Error
- Reduce `--batch-size` to 4 or 8
- Reduce `max_length` in train_finbert.py

### Training is slow
- Use GPU if available
- Reduce `--epochs`
- Use smaller batch size

## 📊 Monitoring Training

Training progress is logged in real-time:
- Loss decreases
- F1 score on validation set
- Early stopping if no improvement for 2 epochs

## 🎓 Next Steps After Training

1. **Integration**: Use fine-tuned model in Agent 8 (Market Sentiment)
2. **Testing**: Test on real Indian market news
3. **Comparison**: Compare with baseline FinBERT
4. **Deployment**: Deploy to production

---

## 📄 Files

- `preprocess_data.py` - Data preprocessing
- `train_finbert.py` - Fine-tuning script
- `README.md` - This file
