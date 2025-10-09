# Project IRIS - Enhanced Financial Forensics Analysis Platform

**I**ntelligent **R**egulatory **I**nsight **S**ystem for Indian Public Companies

## Overview

Project IRIS is a comprehensive financial forensics platform that analyzes Indian public companies for fraud detection, risk assessment, and regulatory compliance. The system leverages AI/ML with Intel hardware acceleration to provide deep insights into financial health and potential manipulation.

**🚀 ENHANCED: Both Agent 1 and Agent 2 now feature advanced Yahoo Finance integration with 29 comprehensive forensic metrics and real-time data processing.**

## Key Features

### 🔍 Enhanced Forensic Analysis
- **29 Comprehensive Metrics** - Vertical analysis, horizontal analysis, and financial ratios
- **Real-time Data Processing** - Live data from Yahoo Finance, NSE, BSE, and FMP
- **Enhanced Field Mapping** - Consistent data normalization across all sources
- **Pandas NaN Detection** - Robust null value handling and data validation
- **Multi-Quarter Support** - Configurable historical analysis periods

### 📊 Enhanced Risk Assessment
- **Vertical Analysis** - Common-size financial statements (11 metrics)
- **Horizontal Analysis** - Growth rate calculations and trend analysis (10 metrics)
- **Financial Ratios** - Liquidity, profitability, and leverage ratios (8 metrics)
- **Real-time Integration** - Live market data and financial metrics

### ⚖️ Advanced Data Integration
- **Yahoo Finance Integration** - Real-time global market data
- **Enhanced Agent Architecture** - Simultaneous operation of ingestion and analysis agents
- **Multi-Source Validation** - Cross-verification across Yahoo Finance, NSE, BSE, and FMP
- **Production-Ready Pipeline** - Seamless data flow from ingestion to analysis

### 💬 Interactive Q&A
- RAG-based system with ChromaDB vector storage
- Gemini 2.0 Flash for natural language responses
- FinLang embeddings (768-dim) for financial document search
- Citation tracking and confidence scoring

### 📈 Market Intelligence
- Google Trends analysis with divergence detection
- FinBERT sentiment analysis (news, social media)
- Peer benchmarking with z-scores and outlier detection
- SEBI enforcement action monitoring

### ⚡ Intel Hardware Optimization
- **OpenVINO** - 6-10x OCR speedup on Intel GPU
- **Intel PyTorch Extension** - 2-4x sentiment analysis speedup with BF16
- Graceful CPU fallback when hardware unavailable

## Architecture

### Enhanced 10-Agent System

```
Agent 1: Enhanced Data Ingestion (Yahoo Finance + NSE/BSE + FMP)
Agent 2: Enhanced Forensic Analysis (29 Metrics + Real-time Processing)
Agent 3: Risk Scoring (6-category weighted composite)
Agent 4: Compliance Validation (Ind AS, SEBI, Companies Act)
Agent 5: Reporting (Gemini summaries, PDF/Excel)
Agent 6: Orchestrator (Pipeline coordinator, job management)
Agent 7: Q&A RAG System (ChromaDB + FinLang + Gemini)
Agent 8: Market Sentiment (Google Trends + FinBERT)
Agent 9: Peer Benchmarking (FMP peer ratios, z-scores)
Agent 10: Regulatory Monitoring (SEBI enforcement scraping)
```

### Enhanced Agent 1 & 2 Architecture

**Agent 1 (Data Ingestion) - Enhanced:**
- **Multi-Source Integration**: Yahoo Finance, NSE, BSE, FMP
- **Real-time Data Fetching**: Live market data processing
- **Enhanced Normalization**: 29-field comprehensive mapping
- **Pandas Integration**: Robust NaN detection and validation
- **Quarterly Processing**: Multi-period historical analysis

**Agent 2 (Forensic Analysis) - Enhanced:**
- **29 Comprehensive Metrics**: All forensic analysis types
- **Real-time Processing**: Live data analysis capabilities
- **Enhanced Field Mapping**: Consistent with Agent 1
- **Multi-Quarter Analysis**: Configurable historical periods
- **Production Pipeline**: Seamless integration with Agent 1

### Technology Stack

**Backend Core:**
- FastAPI (REST + WebSocket)
- Celery + Redis (async processing)
- PostgreSQL (financial data)
- ChromaDB (vector search)
- SQLAlchemy ORM

**AI/ML:**
- Gemini 2.0 Flash
- FinLang embeddings
- FinBERT sentiment
- Intel OpenVINO
- Intel PyTorch Extension

**Enhanced Data Sources:**
- **Yahoo Finance** (primary - real-time global data)
- FMP API (backup - 30yr history)
- NSE/BSE portals (Indian markets)
- SEBI database
- Google Trends

## Enhanced Features

### 🚀 Agent 1 & 2 Enhancements

**Enhanced Yahoo Finance Integration:**
- Real-time data fetching from Yahoo Finance API
- Quarterly and annual financial statement processing
- Live market capitalization and trading data
- Global market coverage (US, India, International)

**29 Comprehensive Forensic Metrics:**
- **Vertical Analysis (11 metrics)**: Common-size financial statements
- **Horizontal Analysis (10 metrics)**: Growth rate calculations and trends
- **Financial Ratios (8 metrics)**: Liquidity, profitability, leverage analysis

**Enhanced Field Mapping:**
- Consistent field mapping across all data sources
- Standardized financial statement normalization
- Cross-source data validation and verification

**Pandas Integration:**
- Robust NaN detection using `pd.isna()`
- Data quality validation and cleaning
- Enhanced data type handling and conversion

**Real-time Processing:**
- Simultaneous operation of both agents
- Live data pipeline from ingestion to analysis
- Real-time market data integration

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+
- **Yahoo Finance API** (free - no API key required)
- FMP API Key (free tier: 250 calls/day)
- Gemini API Key (free tier available)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-org/iris-backend.git
cd iris-backend
```

2. **Create environment file**
```bash
cp .env.template .env
# Edit .env and add your API keys
```

3. **Start services with Docker Compose**
```bash
docker-compose up -d
```

4. **Verify services are running**
```bash
docker-compose ps
```

5. **Access the API**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

### Test Enhanced Agents

**Test both agents simultaneously:**
```bash
# Test complete pipeline with real Reliance data
python3 -c "
import sys, os
sys.path.insert(0, '/home/aditya/I.R.I.S./backend/src')
from agents.forensic.agent1_ingestion import DataIngestionAgent
from agents.forensic.agent2_forensic_analysis import ForensicAnalysisAgent

agent1 = DataIngestionAgent()
agent2 = ForensicAnalysisAgent()

# Real-time Reliance analysis
search_results = agent1.search_company('RELIANCE.NS')
reliance_data = agent1.get_financials('RELIANCE.NS', 'yahoo', periods=3)
normalized = agent1.normalize_financial_statements(reliance_data, 'yahoo')
analysis = agent2.analyze_yahoo_finance_data('RELIANCE.NS', quarters=3)

print('Both agents operational with real Reliance data!')
"
```

## Usage

### Example: Real-time Reliance Analysis

**1. Search for Reliance Industries**
```bash
curl -X GET "http://localhost:8000/api/v1/companies/search?query=RELIANCE.NS"
```

**2. Trigger enhanced forensic analysis**
```bash
curl -X POST "http://localhost:8000/api/v1/forensic/analysis" \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": "RELIANCE.NS",
    "data_source": "yahoo_finance",
    "periods": 3,
    "analysis_types": ["vertical", "horizontal", "ratios"]
  }'
```

**3. Check analysis status**
```bash
curl -X GET "http://localhost:8000/api/v1/forensic/analysis/{job_id}/status"
```

**4. Retrieve comprehensive results**
```bash
curl -X GET "http://localhost:8000/api/v1/forensic/analysis/{job_id}/results"
```

## Enhanced Data Sources

### Yahoo Finance Integration
- **Real-time Data**: Live market prices, volumes, and financial metrics
- **Global Coverage**: US, Indian, and international markets
- **Quarterly Data**: Historical quarterly financial statements
- **No API Key Required**: Free access to comprehensive financial data
- **Real-time Updates**: Live trading data and market information

### Multi-Source Architecture
1. **Yahoo Finance** (Primary) - Real-time global data
2. **FMP API** (Secondary) - 30-year historical data
3. **NSE Portal** (Indian) - National Stock Exchange data
4. **BSE Portal** (Indian) - Bombay Stock Exchange data

## Enhanced Analysis Pipeline

### Real-time Processing Flow
```
Real-time Data → Agent 1 (Ingestion) → Agent 2 (Analysis)
     ↓              ↓                        ↓
Yahoo Finance → Enhanced Field Mapping → 29 Forensic Metrics
Live Market   → Pandas NaN Detection  → Vertical/Horizontal/Ratios
Multi-Quarter → Cross-Agent Integration → Real-time Results
```

### 29 Comprehensive Metrics

**Vertical Analysis (11 metrics):**
- Revenue percentages, cost breakdowns, profit margins
- Asset composition, liability structure, equity analysis

**Horizontal Analysis (10 metrics):**
- Year-over-year growth rates for revenue, profits, assets
- Trend analysis and growth pattern identification

**Financial Ratios (8 metrics):**
- Liquidity ratios (current ratio, quick ratio)
- Profitability ratios (ROE, ROA, margins)
- Leverage ratios (debt-to-equity, interest coverage)

## Configuration

### Enhanced Agent Configuration

**Agent 1 (Data Ingestion) Configuration:**
```yaml
# agent1_ingestion.yaml
data_sources:
  yahoo_finance:
    enabled: true
    real_time: true
    quarterly_data: true
  fmp_api:
    enabled: true
    historical_data: true
  nse_bse:
    enabled: true
    indian_markets: true

field_mapping:
  enhanced_mode: true
  total_fields: 29
  nan_detection: pandas
```

**Agent 2 (Forensic Analysis) Configuration:**
```yaml
# agent2_forensic_analysis.yaml
analysis_types:
  vertical_analysis:
    enabled: true
    metrics_count: 11
  horizontal_analysis:
    enabled: true
    metrics_count: 10
  financial_ratios:
    enabled: true
    metrics_count: 8

real_time_processing:
  enabled: true
  live_data: true
  yahoo_integration: true
```

## Testing

### Enhanced Agent Testing

```bash
# Test both agents simultaneously with real data
python3 complete_pipeline_test.py

# Test Yahoo Finance integration specifically
python3 -c "
import sys, os
sys.path.insert(0, '/home/aditya/I.R.I.S./backend/src')
from agents.forensic.agent1_ingestion import DataIngestionAgent
from agents.forensic.agent2_forensic_analysis import ForensicAnalysisAgent

agent1 = DataIngestionAgent()
agent2 = ForensicAnalysisAgent()

# Real-time test with Reliance
search_results = agent1.search_company('RELIANCE.NS')
yahoo_data = agent1.get_financials('RELIANCE.NS', 'yahoo', periods=3)
analysis = agent2.analyze_yahoo_finance_data('RELIANCE.NS', quarters=3)

print('Real-time pipeline test: SUCCESS')
"
```

### Run all tests
```bash
pytest
```

### Run enhanced agent tests
```bash
pytest -m enhanced_agents  # Enhanced Agent 1 & 2 tests
pytest -m yahoo_integration  # Yahoo Finance integration tests
pytest -m real_time         # Real-time processing tests
```

## Enhanced API Endpoints

### Enhanced Forensic Analysis API

**Real-time Company Analysis:**
```bash
# Analyze Reliance with all enhanced features
POST /api/v1/forensic/enhanced-analysis
{
  "company_id": "RELIANCE.NS",
  "data_sources": ["yahoo_finance", "nse", "bse", "fmp"],
  "periods": 3,
  "analysis_types": ["vertical", "horizontal", "ratios"],
  "real_time": true
}
```

**Multi-Source Data Validation:**
```bash
# Cross-validate Reliance data across sources
POST /api/v1/forensic/multi-source-validation
{
  "company_id": "RELIANCE.NS",
  "sources": ["yahoo_finance", "nse", "bse", "fmp"],
  "validation_type": "cross_reference"
}
```

## Monitoring

### Enhanced Monitoring Metrics

- `enhanced_agents_active` - Both Agent 1 & 2 operational status
- `yahoo_finance_integration` - Real-time Yahoo Finance connectivity
- `real_time_processing` - Live data processing metrics
- `field_mapping_accuracy` - Enhanced field mapping validation
- `pandas_nan_detection` - Data quality metrics

## Deployment

### Enhanced Deployment Checklist

- [ ] **Yahoo Finance Integration**: Configure real-time data fetching
- [ ] **Enhanced Field Mapping**: Enable 29-metric comprehensive analysis
- [ ] **Pandas Integration**: Configure robust NaN detection
- [ ] **Multi-Source Support**: Enable Yahoo Finance, NSE, BSE, FMP
- [ ] **Real-time Processing**: Configure live data pipeline
- [ ] **Agent Synchronization**: Ensure Agent 1 & 2 simultaneous operation

### Production Enhancements

- **Real-time Data Pipeline**: Live Yahoo Finance integration
- **Enhanced Scalability**: Multi-threaded agent processing
- **Data Quality Assurance**: Advanced validation and cleaning
- **Performance Optimization**: Optimized field mapping and processing

## Troubleshooting

### Enhanced Agent Issues

**Yahoo Finance Data Fetch Issues:**
```python
# Check Yahoo Finance connectivity
GET /api/v1/system/yahoo-finance-status

# Test with different periods
POST /api/v1/forensic/test-yahoo-connection
{
  "company_id": "RELIANCE.NS",
  "test_periods": [1, 2, 3]
}
```

**Enhanced Field Mapping Issues:**
```python
# Validate field mapping
POST /api/v1/forensic/validate-field-mapping
{
  "company_id": "RELIANCE.NS",
  "source": "yahoo_finance",
  "expected_fields": 29
}
```

**Real-time Processing Issues:**
```python
# Check agent synchronization
GET /api/v1/system/agent-status

# Monitor real-time pipeline
GET /api/v1/monitoring/real-time-metrics
```

## Contributing

### Enhanced Agent Development

1. **Agent 1 Enhancements**: Yahoo Finance integration, field mapping
2. **Agent 2 Enhancements**: 29-metric analysis, real-time processing
3. **Integration Testing**: Simultaneous agent operation
4. **Documentation**: Update for enhanced features

## Recent Updates

### 🚀 Enhanced Agent 1 & 2 Integration

**Updated:** Both agents now feature:
- ✅ **Yahoo Finance Integration** - Real-time global market data
- ✅ **29 Comprehensive Metrics** - Complete forensic analysis suite
- ✅ **Enhanced Field Mapping** - Consistent across all data sources
- ✅ **Pandas NaN Detection** - Robust data quality handling
- ✅ **Real-time Processing** - Live data pipeline operation
- ✅ **Multi-Source Support** - Yahoo Finance, NSE, BSE, FMP
- ✅ **Production Ready** - Tested with real Reliance Industries data

**Status:** Both agents are now fully enhanced and operational with real-time data processing capabilities!

---

**⚠️ Disclaimer**: This system is for educational and research purposes. Always verify findings with professional financial analysts before making investment decisions.
