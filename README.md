# I.R.I.S. (Investigative Risk Intelligence System)

**I.R.I.S.** is an advanced, autonomic multi-agent AI platform designed for real-time financial forensic analysis, fraud detection, and risk assessment. It moves beyond traditional static auditing by using a swarm of specialized AI agents to continuously monitor, analyze, and visualize corporate financial health.

## Key Features

*   **Forensic Deep-Dive**: Automated calculation of Beneish M-Score, Altman Z-Score, and other key forensic ratios to detect earnings manipulation and financial distress.
*   **Shell Hunter Agent**: Advanced network graph analysis to identify circular trading, hidden related party transactions, and potential shell companies.
*   **Market Sentinel**: Real-time monitoring of news and social signals using FinBERT to detect pump-and-dump schemes and sentiment anomalies.
*   **SEBI Regulatory Compliance**: dedicated "Regulatory Breach Flag Panel" to automatically flag non-compliant activities based on SEBI guidelines.
*   **AI-Powered Reporting**: Generates comprehensive audit reports and executive summaries using Google Gemini models.
*   **Interactive Dashboard**: A modern, responsive React-based interface featuring real-time charts, network graphs, and risk heatmaps.

## System Architecture

The system utilizes a modern microservices-like architecture powered by a "Council of Agents":

![Next JS](https://img.shields.io/badge/Next-black?style=for-the-badge&logo=next.js&logoColor=white)
![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=google&logoColor=white)
![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)


*   **Frontend**: Next.js 14, React, Tailwind CSS, Recharts, React Flow
*   **Backend**: Python, FastAPI, Uvicorn
*   **AI Core**: Google Gemini (via LangChain)
*   **Data & Analysis**: ChromaDB (Vector Store), Redis (Caching), NetworkX (Graph Analysis)

## Prerequisites

*   **Node.js** (v18 or higher)
*   **Python** (v3.10 or higher)
*   **PostgreSQL** (optional, for persistent monitoring storage)

## Installation

### Backend Setup

1.  Navigate to the backend directory:
    ```bash
    cd backend
    ```

2.  Create and activate a virtual environment:
    ```bash
    python -m venv iris_venv
    
    # On Linux/macOS
    source iris_venv/bin/activate
    
    # On Windows
    # .\iris_venv\Scripts\activate
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4.  Configure Environment Variables:
    Create a `.env` file in the `backend` directory (or specific subdirectories as needed) with necessary API keys (e.g., `GEMINI_API_KEY`, `SERPAPI_API_KEY`).

### Frontend Setup

1.  Navigate to the frontend directory:
    ```bash
    cd frontend
    ```

2.  Install dependencies:
    ```bash
    npm install
    # or
    yarn install
    ```

3.  Configure Environment Variables:
    Create a `.env.local` file in the `frontend` directory:
    ```env
    GEMINI_API_KEY=your_gemini_api_key_here
    NEXT_PUBLIC_API_URL=http://localhost:8000
    ```

## Running the Application

### Start the Backend Server
From the `backend` directory with your virtual environment activated:

```bash
uvicorn src.main:app --reload
```
The API will be available at `http://localhost:8000`.

### Start the Frontend Application
From the `frontend` directory:

```bash
npm run dev
```
The application will be running at `http://localhost:3000`.

## Documentation

For more detailed information, please refer to the documentation in the `docs/` directory:
*   [System Design](docs/SYSTEM_DESIGN.md)
*   [Setup Guide](docs/SETUP.md)
*   [API Reference](docs/SDK_API_REFERENCE.md)

## License

This project is licensed under the MIT License.
