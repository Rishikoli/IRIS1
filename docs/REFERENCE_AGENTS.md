# Reference Agents: The Council

IRIS is powered by a swarm of specialized agents, each acting as an expert in a specific forensic domain.

| Agent ID | Name | Role | Core Function |
| :--- | :--- | :--- | :--- |
| **Agent 1** | **Forensic Analyst** | The Auditor | Ingests PL/BS data. Calculates 29+ forensic ratios (Z-Score, M-Score, Beneish). |
| **Agent 2** | **Shell Hunter** | The Detective | Uses Graph Theory (NetworkX) to detect circular trading rings and hidden shell companies. |
| **Agent 3** | **Risk Scorer** | The Judge | Synthesizes all agent outputs into a final Risk Score (0-100) with SHAP explainability. |
| **Agent 4** | **Report Generator** | The Scribe | Compiles findings into executive-grade PDF/Excel audit reports. |
| **Agent 5** | **QA RAG** | The Librarian | Vector-based "Chat with Data" system for querying annual reports effectively. |
| **Agent 6** | **Orchestrator** | The Manager | Coordinates tasks between agents via Kafka/Celery. |
| **Agent 8** | **Market Sentinel** | The Watcher | Analyzes news and search trends using FinBERT to gauge market mood. |
| **Agent 9** | **Network Analysis** | Back-end Logic | Powers the RPT graph construction and cycle detection algorithms. |
| **Agent 10** | **Auditor** | The Reviewer | Deep analyzes text in annual reports for governance red flags. |
| **Agent 12** | **Cartographer** | The Mapper | Geospatial intelligence for tracking cross-border financial flows. |

## Technical Implementation
*   **Model**: All agents utilize **Google Gemini 2.5 Flash** for reasoning.
*   **Orchestration**: Agents communicate via shared state in Redis and tasks in Celery.
*   **Memory**: Short-term context in Redis, long-term knowledge in ChromaDB.
