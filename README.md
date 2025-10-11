# IRIS - Investment Risk Intelligence System

**I**ntelligent **R**egulatory **I**nsight **S**ystem for Indian Public Companies

## Overview

IRIS is a comprehensive financial forensics platform that analyzes Indian public companies for fraud detection, risk assessment, and regulatory compliance. The system leverages AI/ML with Intel hardware acceleration to provide deep insights into financial health and potential manipulation.

## Architecture

IRIS consists of two main components:

### 🖥️ Frontend (`/frontend`)
Modern Next.js web application providing an intuitive interface for:
- **Risk Assessment Dashboard** - Multi-factor risk scoring with confidence levels
- **Forensic Analysis Tools** - Financial statement analysis (vertical, horizontal, ratio)
- **Anomaly Detection** - Advanced algorithms for irregularities detection
- **Interactive Visualizations** - Charts and graphs for financial data

**Tech Stack:**
- Next.js 15+ with TypeScript
- Tailwind CSS for styling
- Recharts for data visualization
- GSAP for animations
- Three.js for 3D visualizations

### ⚙️ Backend (`/backend`)
Sophisticated 10-agent system for comprehensive financial analysis:
- **Agent 1**: Enhanced Data Ingestion (Yahoo Finance + NSE/BSE + FMP)
- **Agent 2**: Enhanced Forensic Analysis (29 Metrics + Real-time Processing)
- **Agent 3**: Risk Scoring (6-category weighted composite)
- **Agent 4**: Compliance Validation (Ind AS, SEBI, Companies Act)
- **Agent 5**: Reporting (Gemini summaries, PDF/Excel)
- **Agent 6**: Orchestrator (Pipeline coordinator, job management)
- **Agent 7**: Q&A RAG System (ChromaDB + FinLang + Gemini)
- **Agent 8**: Market Sentiment (Google Trends + FinBERT)
- **Agent 9**: Peer Benchmarking (FMP peer ratios, z-scores)
- **Agent 10**: Regulatory Monitoring (SEBI enforcement scraping)

**Tech Stack:**
- FastAPI (REST + WebSocket)
- Celery + Redis (async processing)
- PostgreSQL (financial data)
- ChromaDB (vector search)
- Intel OpenVINO (hardware acceleration)

## Key Features

### 🔍 Enhanced Forensic Analysis
- **29 Comprehensive Metrics** - Vertical analysis, horizontal analysis, and financial ratios
- **Real-time Data Processing** - Live data from Yahoo Finance, NSE, BSE, and FMP
- **Multi-Quarter Support** - Configurable historical analysis periods

### 📊 Advanced Risk Assessment
- **Multi-factor Risk Scoring** - Six-category weighted composite risk assessment
- **Confidence Levels** - Detailed risk factor analysis with confidence scoring
- **Real-time Integration** - Live market data and financial metrics

### ⚖️ Comprehensive Data Integration
- **Yahoo Finance Integration** - Real-time global market data (Primary)
- **Multi-Source Validation** - Cross-verification across multiple data sources
- **Production-Ready Pipeline** - Seamless data flow from ingestion to analysis

### 💬 Interactive Q&A System
- RAG-based system with ChromaDB vector storage
- Gemini 2.0 Flash for natural language responses
- FinLang embeddings (768-dim) for financial document search

### 📈 Market Intelligence
- Google Trends analysis with divergence detection
- FinBERT sentiment analysis (news, social media)
- Peer benchmarking with z-scores and outlier detection

## Quick Start

### Prerequisites

- **Node.js 18+** (for frontend)
- **Python 3.11+** (for backend)
- **Docker & Docker Compose**
- **PostgreSQL 15+**
- **Redis 7+**
- **API Keys**: Yahoo Finance (free), FMP API (free tier), Gemini API (free tier)

### Installation & Setup

1. **Clone the repository**
```bash
git clone https://github.com/Rishikoli/IRIS1.git
cd IRIS1
```

2. **Backend Setup**
```bash
cd backend
cp .env.template .env
# Edit .env and add your API keys
docker-compose up -d
```

3. **Frontend Setup**
```bash
cd ../frontend
npm install
npm run build
```

4. **Start Development**
```bash
# Backend API
cd backend
docker-compose up

# Frontend (new terminal)
cd frontend
npm run dev
```

5. **Access the Application**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Project Structure

```
IRIS1/
├── frontend/           # Next.js web application
│   ├── src/
│   │   ├── app/       # Next.js app router
│   │   ├── components/# React components
│   │   └── lib/       # Utilities
│   ├── public/        # Static assets
│   └── package.json   # Frontend dependencies
├── backend/           # FastAPI application
│   ├── src/          # Source code
│   ├── agents/       # AI agents
│   ├── config/       # Configuration files
│   └── requirements.txt
└── README.md         # This file
```

## Usage Examples

### Risk Assessment
```bash
# Analyze a company's risk profile
curl -X POST "http://localhost:8000/api/v1/risk/assessment" \
  -H "Content-Type: application/json" \
  -d '{"company_id": "RELIANCE.NS", "periods": 3}'
```

### Forensic Analysis
```bash
# Get comprehensive forensic analysis
curl -X GET "http://localhost:8000/api/v1/forensic/analysis/RELIANCE.NS?quarters=3"
```

### Anomaly Detection
```bash
# Detect financial irregularities
curl -X POST "http://localhost:8000/api/v1/anomaly/detection" \
  -H "Content-Type: application/json" \
  -d '{"company_id": "RELIANCE.NS", "sensitivity": "high"}'
```

## Development

### Frontend Development
```bash
cd frontend
npm run dev        # Start development server
npm run build      # Build for production
npm run lint       # Run linter
```

### Backend Development
```bash
cd backend
python -m pytest              # Run tests
python src/main.py           # Run locally
docker-compose up -d         # Run with Docker
```

## Deployment

### Frontend Deployment
The frontend can be deployed to Vercel, Netlify, or any static hosting:
```bash
cd frontend
npm run build
# Deploy .next folder to your hosting provider
```

### Backend Deployment
```bash
cd backend
docker-compose -f docker-compose.prod.yml up -d
```

## API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Testing

### Frontend Tests
```bash
cd frontend
npm test
```

### Backend Tests
```bash
cd backend
pytest                           # Run all tests
pytest -m enhanced_agents       # Test enhanced agents
pytest -m yahoo_integration     # Test Yahoo Finance integration
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Recent Updates

### 🚀 Enhanced Features
- **Real-time Yahoo Finance Integration** - Live global market data
- **29 Comprehensive Forensic Metrics** - Complete analysis suite
- **Multi-factor Risk Assessment** - Advanced risk scoring algorithms
- **Interactive Dashboard** - Modern UI for data visualization
- **Intel Hardware Optimization** - OpenVINO acceleration for AI tasks

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

⚠️ **This system is for educational and research purposes only.** Always verify findings with professional financial analysts before making investment decisions. Past performance does not guarantee future results.

---

**Made with ❤️ for financial transparency and regulatory compliance**
