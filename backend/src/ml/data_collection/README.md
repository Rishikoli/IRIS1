# Data Collection for FinBERT Fine-tuning

This module contains web scrapers and data processors to collect Indian market-specific financial text data for fine-tuning FinBERT.

## 📁 Directory Structure

```
data_collection/
├── __init__.py                   # Module exports
├── scrape_sebi.py               # SEBI enforcement orders & press releases
├── scrape_bse_nse.py            # BSE/NSE corporate announcements
├── scrape_news.py               # Financial news from ET, MC, BS, LM
├── process_pdfs.py              # Annual report PDF extraction
├── collect_all.py               # Master orchestrator script
├── requirements_data_collection.txt  # Python dependencies
└── README.md                    # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend/src/ml/data_collection
pip install -r requirements_data_collection.txt
```

### 2. Create Data Directories

```bash
mkdir -p data/raw/{sebi,exchanges,news,pdfs,reports}
mkdir -p data/processed
```

### 3. Run Data Collection

**Collect all data sources:**
```bash
python collect_all.py
```

**With custom parameters:**
```bash
python collect_all.py \
    --sebi-pages 20 \
    --exchange-days 60 \
    --news-per-source 200 \
    --output-dir data/processed
```

**Skip PDF processing:**
```bash
python collect_all.py --skip-pdfs
```

## 📊 Individual Scrapers

### SEBI Scraper

Collects enforcement orders and press releases from SEBI.

```python
from scrape_sebi import SEBIScraper

scraper = SEBIScraper(output_dir="data/raw/sebi")
df = scraper.scrape_all(max_pages=10)
print(f"Collected {len(df)} SEBI documents")
```

### BSE/NSE Scraper

Collects corporate announcements from stock exchanges.

```python
from scrape_bse_nse import BSENSEScraper

scraper = BSENSEScraper(output_dir="data/raw/exchanges")
df = scraper.scrape_all(days=30, max_records=1000)
print(f"Collected {len(df)} announcements")
```

### Financial News Scraper

Collects news from Economic Times, Moneycontrol, Business Standard, and LiveMint.

```python
from scrape_news import FinancialNewsScraper

scraper = FinancialNewsScraper(output_dir="data/raw/news")
df = scraper.scrape_all_sources(max_articles_per_source=100)
print(f"Collected {len(df)} articles")
```

### PDF Processor

Extracts text from annual report PDFs.

```python
from process_pdfs import PDFProcessor

processor = PDFProcessor(
    input_dir="data/raw/pdfs",
    output_dir="data/raw/reports"
)
df = processor.process_directory()
print(f"Extracted {len(df)} sentences")
```

## 📋 Output Format

All scrapers output CSV files with these standard columns:

| Column | Description |
|--------|-------------|
| `text` | Main text content (title, summary, or full article) |
| `title` | Document title (if available) |
| `date` | Publication/announcement date |
| `source` | Data source (SEBI, BSE, NSE, economictimes, etc.) |
| `label` | Sentiment label (positive/negative/neutral) |
| `url` | Source URL (if available) |

## 🏷️ Labeling Strategy

**Auto-labeled:**
- SEBI enforcement orders → `negative`
- BSE/NSE announcements → auto-classified by keywords
- News articles → needs manual labeling

**Keyword-based classification:**
- `positive`: profit, growth, dividend, expansion, etc.
- `negative`: loss, penalty, fraud, litigation, etc.
- `neutral`: no strong indicators

**Manual labeling required for:**
- News articles (initially labeled as `neutral`)
- Annual report sections
- Ambiguous announcements

## 📊 Expected Data Volume

| Source | Expected Records | Sentiment Distribution |
|--------|------------------|------------------------|
| SEBI | 5,000-10,000 | 80% negative, 20% neutral |
| BSE/NSE | 20,000-30,000 | Mixed (auto-classified) |
| News | 30,000-40,000 | Needs labeling |
| PDFs | 10,000-15,000 | Needs labeling |
| **Total** | **65,000-95,000** | **Balanced after labeling** |

## ⚙️ Configuration

### Rate Limiting

All scrapers include delays between requests:
- 1-2 seconds between pages
- 2-3 seconds between different sources

### User Agents

Scrapers use realistic browser user agents to avoid blocking.

### Error Handling

- Automatic retries on network errors
- Graceful fallbacks for parsing failures
- Comprehensive logging

## 🔧 Troubleshooting

**Issue: No data collected**
- Check internet connection
- Verify website structure hasn't changed
- Check logs for specific errors

**Issue: PDF extraction fails**
- Ensure PDFs are in `data/raw/pdfs/`
- Try both PyPDF2 and pdfplumber extractors
- Check PDF is not password-protected

**Issue: NSE API blocked**
- NSE has strict rate limiting
- Try using VPN or different IP
- Add longer delays between requests

## 📝 Next Steps

After data collection:

1. **Manual Labeling**: Use Label Studio or similar tool
2. **Data Cleaning**: Remove noise and duplicates
3. **Train/Val/Test Split**: 70/15/15 stratified split
4. **Fine-tune FinBERT**: Follow `implementation_plan.md`

## 🤝 Contributing

To add a new data source:

1. Create `scrape_<source>.py` following existing patterns
2. Implement scraper class with standard output format
3. Add to `collect_all.py` orchestrator
4. Update this README

## 📄 License

Part of the I.R.I.S. project. For internal use only.
