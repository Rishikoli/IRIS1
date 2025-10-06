# Project IRIS - Financial Forensics Analysis Platform

**I**ntelligent **R**egulatory **I**nsight **S**ystem for Indian Public Companies

## Overview

Project IRIS is a comprehensive financial forensics platform that analyzes Indian public companies for fraud detection, risk assessment, and regulatory compliance. The system leverages AI/ML with Intel hardware acceleration to provide deep insights into financial health and potential manipulation.

## Key Features

### 🔍 Forensic Analysis
- **Benford's Law** - First-digit frequency analysis for manipulation detection
- **Altman Z-Score** - Bankruptcy prediction (SAFE/GREY/DISTRESS classification)
- **Beneish M-Score** - Earnings manipulation detection (8-variable model)
- **Ratio Analysis** - Liquidity, profitability, leverage, and efficiency ratios

### 📊 Risk Scoring
- 6-category composite risk scoring
- Weighted aggregation (Financial Health, Earnings Quality, Disclosure Quality, Market Signals, Forensic Flags, Market Sentiment)
- Risk classification: LOW (80-100), MEDIUM (60-79), HIGH (40-59), CRITICAL (0-39)

### ⚖️ Compliance Validation
- **Ind AS Standards** - Balance sheet equation, cash flow presence
- **SEBI LODR Regulations** - Filing timeliness, related party transactions
- **Companies Act 2013** - Audit qualifications, board compliance

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

### 10 Specialized Agents

```
Agent 1: Data Ingestion (FMP API + NSE/BSE)
Agent 2: Forensic Analysis (Benford, Z-Score, M-Score, Ratios)
Agent 3: Risk Scoring (6-category weighted composite)
Agent 4: Compliance Validation (Ind AS, SEBI, Companies Act)
Agent 5: Reporting (Gemini summaries, PDF/Excel)
Agent 6: Orchestrator (Pipeline coordinator, job management)
Agent 7: Q&A RAG System (ChromaDB + FinLang + Gemini)
Agent 8: Market Sentiment (Google Trends + FinBERT)
Agent 9: Peer Benchmarking (FMP peer ratios, z-scores)
Agent 10: Regulatory Monitoring (SEBI enforcement scraping)
```

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

**Data Sources:**
- FMP API (primary - 30yr history)
- NSE/BSE portals (backup)
- SEBI database
- Google Trends

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+
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

### Alternative: Manual Setup

1. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up database**
```bash
# Start PostgreSQL and create database
createdb iris_forensic

# Run migrations
psql -U iris -d iris_forensic -f src/database/migrations/create_tables.sql
```

4. **Start Redis**
```bash
redis-server
```

5. **Start ChromaDB**
```bash
chroma run --path ./data/chromadb
```

6. **Start Celery worker**
```bash
celery -A src.celery_app worker --loglevel=info -Q forensic_analysis
```

7. **Start Celery beat (scheduler)**
```bash
celery -A src.celery_app beat --loglevel=info
```

8. **Start FastAPI server**
```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

## Usage

### Example: Analyze a Company

**1. Search for company**
```bash
curl -X GET "http://localhost:8000/api/v1/companies/search?query=Reliance&exchange=NSE"
```

**2. Trigger forensic analysis**
```bash
curl -X POST "http://localhost:8000/api/v1/forensic/analysis" \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": "RELIANCE.NS",
    "start_date": "2023-01-01",
    "end_date": "2024-09-30",
    "period": "quarter"
  }'
```

**3. Check analysis status**
```bash
curl -X GET "http://localhost:8000/api/v1/forensic/analysis/{job_id}/status"
```

**4. Retrieve results**
```bash
curl -X GET "http://localhost:8000/api/v1/forensic/analysis/{job_id}/results"
```

**5. Ask questions**
```bash
curl -X POST "http://localhost:8000/api/v1/forensic/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": "RELIANCE.NS",
    "query": "What is the company'\''s Z-Score and what does it indicate?"
  }'
```

## Testing

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=src --cov-report=html
```

### Run specific test categories
```bash
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests only
pytest -m e2e              # End-to-end tests only
pytest -m forensic         # Forensic agent tests only
```

### Run without external API calls
```bash
MOCK_FMP_API=true MOCK_GEMINI_API=true pytest
```

## Configuration

### YAML-Based Agent Configuration

Configuration files are located in `src/agents/forensic/config/`

**Example: Agent 2 (Forensic Analysis)**
```yaml
# agent2_forensic_analysis.yaml
thresholds:
  z_score:
    safe: 2.99
    grey_zone_min: 1.81
  m_score:
    manipulation_threshold: -1.78

anomaly_rules:
  - name: "REVENUE_DECLINE"
    threshold: -30
    severity: "HIGH"
```

**Environment-specific overrides:**
```yaml
# agent2_forensic_analysis.prod.yaml
thresholds:
  z_score:
    safe: 3.5  # More conservative in production
```

## API Documentation

Full API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Main Endpoint Groups

- **Companies** - Search, profile retrieval
- **Forensic Analysis** - Trigger, status, results
- **Reports** - PDF, Excel, JSON downloads
- **Q&A** - Chat interface, conversation history
- **Risk & Compliance** - Risk scores, violations, anomalies

## Monitoring

### Access Monitoring Tools

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)
- **PgAdmin**: http://localhost:5050 (admin@iris.local/admin) - Start with `--profile tools`

### Key Metrics

- `forensic_jobs_total` - Total analysis jobs
- `forensic_analysis_duration_seconds` - Pipeline execution time
- `api_requests_total` - API request count
- `fmp_api_calls_remaining` - FMP API quota tracking

## Project Structure

```
iris-backend/
├── src/
│   ├── agents/forensic/          # 10 specialized agents
│   ├── api/                       # FastAPI routes & schemas
│   ├── api_clients/               # FMP, NSE, BSE clients
│   ├── models/                    # SQLAlchemy ORM
│   ├── database/                  # DB connection & migrations
│   ├── utils/                     # Utilities (logger, OCR)
│   ├── metrics/                   # Prometheus metrics
│   ├── celery_app.py             # Celery configuration
│   └── config.py                  # Application config
├── tests/                         # Test suites
├── config/                        # Logging, Prometheus configs
├── scripts/                       # Utility scripts
├── Docs/                         # Design & requirements docs
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## Development

### Code Quality

```bash
# Format code
black src tests

# Sort imports
isort src tests

# Lint
flake8 src tests

# Type checking
mypy src
```

### Database Migrations

```bash
# Generate migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Deployment

### Intel Tiber Developer Cloud

1. **Get free Intel Tiber Cloud account** (120 days free)
2. **SSH into instance**
3. **Clone repository and start services**
```bash
git clone https://github.com/your-org/iris-backend.git
cd iris-backend
docker-compose up -d
```

### Production Checklist

- [ ] Set `ENVIRONMENT=production` in `.env`
- [ ] Use strong database passwords
- [ ] Enable SSL/TLS for PostgreSQL
- [ ] Configure CORS for specific origins
- [ ] Set up log rotation
- [ ] Configure automated backups
- [ ] Monitor FMP API quota usage
- [ ] Set up alerts for CRITICAL risk scores

## Troubleshooting

### FMP API Rate Limit Exceeded
```python
# Check remaining quota
GET /api/v1/system/fmp-quota

# System uses 24hr cache for resilience
# Upgrade to FMP Starter plan for 300 calls/min
```

### Intel Hardware Not Detected
```python
# Check hardware metrics
GET /api/v1/system/hardware-status

# System automatically falls back to CPU
# Check logs for fallback events
```

### Job Stuck in ANALYZING Status
```python
# Check Celery worker logs
docker-compose logs celery-worker-forensic

# Retry job
POST /api/v1/forensic/analysis/{job_id}/retry
```

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Acknowledgments

- Financial Modeling Prep for comprehensive financial data
- Google Gemini for AI-powered analysis
- Intel for hardware acceleration support
- Open source community for excellent libraries

## Contact

- Project Lead: [Your Name]
- Email: [your.email@example.com]
- GitHub: [https://github.com/your-org/iris-backend](https://github.com/your-org/iris-backend)

---

**⚠️ Disclaimer**: This system is for educational and research purposes. Always verify findings with professional financial analysts before making investment decisions.
