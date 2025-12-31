# IRIS / Nexus Ray Project Documentation

## 1. Project Overview
IRIS (also referred to as Nexus Ray) is an advanced AI-powered forensic and risk analysis platform. It leverages a multi-agent architecture to analyze financial data, market sentiment, and corporate compliance. The system uses a modern web stack with a Python FastAPI backend and a Next.js frontend, integrating powerful AI models like Google's Gemini and local LLMs (Qwen/OpenVINO) for real-time insights.

## 2. Technology Stack

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12)
- **Database**: 
    - PostgreSQL (Relational Data)
    - [ChromaDB](https://www.trychroma.com/) (Vector Database for RAG)
    - Redis (Caching/Task Broker)
- **Asynchronous Tasks**: [Celery](https://docs.celeryq.dev/)
- **Event Streaming**: Apache Kafka (via `confluent-kafka`)
- **AI & ML**:
    - **LLMs**: Google Generative AI (Gemini 2.0 Flash Exp), Hugging Face Transformers
    - **Inference**: PyTorch
    - **Embeddings**: Sentence Transformers
- **Financial Data**: `yfinance`, `pytrends`
- **Utility**: `pydantic` for validation, `sqlalchemy` for ORM.

### Frontend
- **Framework**: [Next.js 15](https://nextjs.org/) (React 19)
- **Styling**: TailwindCSS v4
- **Visualization**: 
    - `recharts`, `d3` for charts
    - `react-globe.gl` for 3D geospatial visualization
    - `reactflow` for node/agent graphs
- **Three.js**: `three`, `ogl` for 3D elements

## 3. Architecture Overview

The system operates on a **micro-agent architecture**, where specialized agents perform distinct tasks:

- **Forensic Agents (`backend/src/agents/forensic`)**:
    - **Agent 1 (Ingestion)**: Handles data ingestion from various sources.
    - **Agent 2 (Forensic Analysis)**: Core analysis engine for financial reports.
    - **Agent 2.5 (Shell Hunter)**: Specialized in detecting circular ownership, money laundering loops, and interlocking directorates.
    - **Agent 3 (Risk Scoring)**: Calculates comprehensive risk scores based on multiple factors.
    - **Agent 4 (Compliance)**: Checks adherence to regulatory measures and compliance standards.
    - **Agent 5 (Reporting)**: Aggregates findings into structured reports.
    - **Agent 6 (Orchestrator)**: Coordinates communication and task flow between agents.
    - **Agent 9 (Network Analysis)**: Builds RPT networks and detects suspicious cycles.
    - **Agent 10 (Auditor)**: Analyzes annual reports and financial statements.
    - **Agent 11 (Exchange)**: Fetches official shareholding patterns.
    - **Agent 11 (Report Generator)**: Generates PDF forensic investigation reports.
    - **Agent 12 (Cartographer)**: Provides geo-spatial intelligence and tax haven detection.
    - **Agent 13 (Time Traveler)**: Performs predictive forensics and future performance analysis.
- **QA RAG Agent (`backend/src/agents/agent7_qa_rag.py`)**: Answer questions based on retrieved documents.
- **Market Sentiment Agent (`backend/src/agents/agent8_market_sentiment.py`)**: Analyze market trends and news.
- **Orchestration**: Agents communicate and coordinate via Kafka topics and Celery tasks.

## 4. Setup Instructions

### Prerequisites
- Python 3.12+
- Node.js 18+
- Docker (for Kafka, Redis, Postgres services)
- Google Gemini API Key

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python3.12 -m venv iris_venv
   source iris_venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the development server:
   ```bash
   uvicorn src.main:app --reload
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Configure Environment:
   Refer to `ENV_SETUP.md` for setting up your `.env.local` file with the strictly required `GEMINI_API_KEY`.
4. Run the development server:
   ```bash
   npm run dev
   ```

### Documentation
- **Environment Setup**: See `frontend/ENV_SETUP.md` for detailed API key configuration.
