# I.R.I.S. (Investigative Risk Intelligence System)

**I.R.I.S.** is an advanced, autonomic multi-agent AI platform designed for real-time financial forensic analysis, fraud detection, and risk assessment. It moves beyond traditional static auditing by using a swarm of specialized AI agents to continuously monitor, analyze, and visualize corporate financial health.

![Next JS](https://img.shields.io/badge/Next-black?style=for-the-badge&logo=next.js&logoColor=white)
![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=google&logoColor=white)
![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)

---

## The "Council of Agents"

IRIS is powered by a coordinated swarm of specialized AI agents, each an expert in a specific domain of financial forensics.

| Agent | Name | Role | Core Function |
| :--- | :--- | :--- | :--- |
| **Agent 1** | **Forensic Analyst** | *The Auditor* | Ingests detailed PL/BS data to calculate 29+ forensic ratios (Beneish M-Score, Altman Z-Score) to detect accounting anomalies. |
| **Agent 2** | **Shell Hunter** | *The Detective* | Utilizes Graph Theory (NetworkX) to visualize and detect circular trading rings, hidden related parties, and potential shell companies. |
| **Agent 3** | **Risk Scorer** | *The Judge* | Synthesizes outputs from all agents into a unified Risk Score (0-100) with SHAP-based explainability for transparent decision-making. |
| **Agent 4** | **Compliance Agent** | *The Enforcer* | Validates compliance with SEBI LODR, Ind AS, and Companies Act 2013 regulations. |
| **Agent 5** | **Report Generator** | *The Scribe* | Compiles complex findings into executive-grade PDF and Excel audit reports, ready for regulatory submission. |
| **Agent 6** | **Orchestrator** | *The Manager* | Coordinates tasks between agents via Kafka/Celery. |
| **Agent 7** | **QA RAG System** | *The Librarian* | Vector-based "Chat with Data" system allowing analysts to query thousands of pages of annual reports instantly. |
| **Agent 8** | **Market Sentinel** | *The Watcher* | Continuously monitors news and search trends using FinBERT to gauge market sentiment and detect pump-and-dump schemes. |
| **Agent 9** | **Network Analysis** | *Back-end Logic* | Powers the RPT graph construction and cycle detection algorithms. |
| **Agent 10** | **Auditor** | *The Reviewer* | Deep analyzes text in annual reports for governance red flags. |
| **Agent 12** | **Cartographer** | *The Mapper* | Provides geospatial intelligence to track cross-border financial flows and highlight jurisdictional risks. |

---

## Key Features

### 1. Unified Risk Dashboard
A "Bento Box" style command center that aggregates data from all agents. View live risk scores, stock performance, and critical alerts in a single pane of glass.

### 2. Deep Forensic Analysis
Go beyond surface-level numbers. IRIS performs:
*   **Vertical & Horizontal Analysis**: Multi-year trend detection.
*   **Fraud Models**: Automated Probit/Logit models for probability of default.
*   **Manipulation Flags**: Instant red flags for aggressive revenue recognition or capitalization of expenses.

### 3. Automated Enforcement RFI
Automatically drafts professional "Request for Information" (RFI) letters addressed to Audit Committees when anomalies are detected, referencing specific legal sections (e.g., SEBI LODR, Companies Act) to expedite regulatory inquiries.

### 4. SEBI Regulatory Compliance
Dedicated module for Indian markets:
*   **Regulatory Breach Flag Panel**: Auto-checks against SEBI LODR regulations.
*   **Insider Trading Alerts**: Correlates price movements with insider disclosures.

### 5. Automated Reporting
One-click generation of:
*   **Due Diligence Reports**: For pre-investment analysis.
*   **Forensic Audit Reports**: For deep-dive investigations.
*   **Early Warning Memos**: For rapid internal alerts.

---

## System Architecture

![System Architecture](assets/Architecture_iris1.svg)


IRIS implements a **Micro-Agent Architecture** to ensure scalability and fault tolerance.

### Frontend Layer
*   **Framework**: Next.js 14 (App Router)
*   **Styling**: Tailwind CSS + Shadcn UI
*   **Visualization**: Recharts (Financial data), React Flow (Network Graphs)

### Backend Layer
*   **API**: FastAPI (High-performance async Python)
*   **Orchestration**: Custom agent loop with shared state management
*   **AI Engine**: Google Gemini 2.5 Flash via LangChain

### Data Layer
*   **Vector Store**: ChromaDB (for RAG and Document Search)
*   **Cache**: Redis (for Agent State and Rate Limiting)
*   **Database**: PostgreSQL (for persistent transactional data)

---

## Prerequisites

Before you begin, ensure you have the following installed:

*   **Node.js**: v18.0.0 or higher
*   **Python**: v3.10 or higher
*   **Git**: For version control

## Installation Guide

### 1. Clone the Repository
```bash
git clone https://github.com/Rishikoli/IRIS1.git
cd IRIS1
```

### 2. Backend Setup
Set up the Python environment and install dependencies.

```bash
cd backend
python -m venv iris_venv

# Activate Virtual Environment
# Windows:
iris_venv\Scripts\activate
# Mac/Linux:
source iris_venv/bin/activate

# Install Dependencies
pip install -r requirements.txt
```

**Configuration**: Create a `.env` file in `backend/` with your keys:
```env
GEMINI_API_KEY=your_gemini_key
SERPAPI_API_KEY=your_serpapi_key
DATABASE_URL=postgresql://user:password@localhost/iris_db
```

### 3. Frontend Setup
Install the Node.js dependencies.

```bash
cd ../frontend
npm install
# or
yarn install
```

**Configuration**: Create a `.env.local` file in `frontend/`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
GEMINI_API_KEY=your_gemini_key
```

---

## Usage

### Starting the System

1.  **Launch Backend**:
    ```bash
    # In one terminal
    cd backend
    uvicorn src.main:app --reload
    ```

2.  **Launch Frontend**:
    ```bash
    # In another terminal
    cd frontend
    npm run dev
    ```

3.  **Access IRIS**:
    Open your browser and navigate to `http://localhost:3000`.

### Common Workflows
*   **Analyze a Company**: Enter the ticker symbol (e.g., `RELIANCE`) in the search bar.
*   **Check Relationships**: Switch to the "Network" tab to see related party graphs.
*   **Ask Questions**: Use the "Guardian AI" chat widget to ask questions like *"What is the debt-to-equity ratio trend?"*

---

## Documentation

*   [System Design Architecture](docs/SYSTEM_DESIGN.md)
*   [Agent Reference Guide](docs/REFERENCE_AGENTS.md)
*   [API Documentation](docs/SDK_API_REFERENCE.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
