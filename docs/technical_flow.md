# IRIS Agents: Technical Flow & Serial Order

## 1. The Council of Agents (Serial Order)

| Agent ID | Name | Role | Core Function |
| :--- | :--- | :--- | :--- |
| **Agent 1** | **Forensic Analyst** | The Auditor | Ingests basic financial data (PL/BS) and calculates 29+ forensic ratios (Z-Score, M-Score). |
| **Agent 2** | **Shell Hunter** | The Detective | Uses Graph Theory to detect circular trading rings and hidden shell companies. |
| **Agent 3** | **Risk Scorer** | The Judge | Aggregates outputs from all other agents to compute the final Risk Score (0-100). |
| **Agent 4** | **Report Gen.** | The Scribe | Compiles all findings into a structured PDF/Excel audit report. |
| **Agent 5** | **QA RAG** | The Librarian | Vector-based "Chat with Data" system for querying annual reports. |
| **Agent 6** | **Market Sentiment**| The Watcher | Analyzes news and google trends using FinBERT to gauge market mood. |

---

## 2. Technical Data Flow Diagram

```mermaid
graph TD
    subgraph "Layer 1: Data Ingestion"
        Docs[Annual Reports / PDFs] --> A5[Agent 5: QA RAG]
        News[News & Social Signals] --> A6[Agent 6: Sentiment]
        FinData[Financial Statements] --> A1[Agent 1: Forensic Analyst]
        RPT[Related Party Data] --> A2[Agent 2: Shell Hunter]
    end

    subgraph "Layer 2: Analysis & Reasoning"
        A5 --> |Context & Answers| A3
        A6 --> |Sentiment Score (-100 to +100)| A3
        A1 --> |Z-Score, M-Score, Ratios| A3
        A2 --> |Graph Cycles & Red Flags| A3
    end

    subgraph "Layer 3: Synthesis & Output"
        A3[Agent 3: Risk Judge] --> |Final Integrity Score| DB[(Database)]
        A3 --> |Risk Breakdown| FE[Frontend Dashboard]
        
        DB --> A4[Agent 4: Report Generator]
        A4 --> Output[PDF/Excel Audit Report]
    end

    style A3 fill:#f9f,stroke:#333,stroke-width:4px
```
