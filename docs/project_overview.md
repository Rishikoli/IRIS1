# IRIS: Project Overview

**Investigative Risk Intelligence System (IRIS)** is an advanced, autonomic multi-agent AI platform designed for real-time financial forensic analysis, fraud detection, and risk assessment. It moves beyond traditional static auditing by using a swarm of specialized AI agents to continuously monitor, analyze, and visualize corporate financial health.

## 🏗️ System Architecture

The project follows a modern microservices-like architecture:

| Layer | Technologies | Description |
|-------|--------------|-------------|
| **Frontend** | Next.js, React, Tailwind CSS, TypeScript | Interactive dashboard with real-time charts (Recharts), network graphs (React Flow), and 3D geospatial elements. |
| **Backend** | Python, FastAPI, Uvicorn | High-performance API layer managing agent orchestration and data processing. |
| **AI Core** | Google Gemini (2.5 Flash), LangChain | The "brains" of the system. All agents utilize Gemini-2.5-flash for reasoning and generation. |
| **Data** | ChromaDB, Redis, NetworkX | Vector storage for RAG, caching for performance, and graph algorithms for network analysis. |

## 🤖 The Agentic Framework

IRIS is driven by a specialized "Council of Agents," each an expert in a specific forensic domain:

*   **Agent 2 (Forensic Analyst)**: The core engine. Calculates 29+ metrics including Altman Z-Score, Beneish M-Score, and Benford's Law adherence.
*   **Agent 3 (Risk Scorer)**: Synthesizes data into a single "Risk Score" (0-100) and provides SHAP-based explainability for *why* a company is risky.
*   **Agent 2.5 (Shell Hunter)**: A graph-theory specialist that detects circular trading, hidden shell companies, and interlocking directorates (The "Shadow Economy").
*   **Agent 5 (Reporter)**: Generates comprehensive, executive-grade PDF/Excel forensic reports.
*   **Agent 7 (QA RAG)**: A "Chat with your Data" system allowing users to ask natural language questions about financial documents.
*   **Agent 8 (Market Sentiment)**: Monitors news and social signals to gauge market perception.
*   **Agent 9 (Network Analysis)**: The backend logic powering the RPT (Related Party Transaction) graph.

## 🌟 Key Features

1.  **"Shell Hunter" Network Graph**: Visually explodes the web of related parties to reveal hidden money laundering cycles.
2.  **Live Risk Scoring**: Real-time updates to company risk profiles based on market moves and new filings.
3.  **Forensic Deep-Dive**: Tabs for Vertical/Horizontal analysis, Ratios, and Fraud Models (M-Score/Z-Score).
4.  **Generative Reporting**: One-click generation of detailed audit reports.
5.  **Interactive 3D Globe**: Visualizing cross-border financial flows (Forensic Cartographer).

## 🚀 Current State

*   **Model Status**: All agents successfully migrated to **Gemini 2.5 Flash**.
*   **Stability**: Core endpoints (Forensic, Network, Risk) are fully operational.
*   **UI**: Enhanced with "Glassmorphism" design and interactive feedback.
