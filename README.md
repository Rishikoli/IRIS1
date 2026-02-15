# I.R.I.S. (Investigative Risk Intelligence System)

**I.R.I.S.** is an advanced, autonomic multi-agent AI platform designed for real-time financial forensic analysis, fraud detection, and risk assessment. It moves beyond traditional static auditing by using a swarm of specialized AI agents to continuously monitor, analyze, and visualize corporate financial health.

![Next JS](https://img.shields.io/badge/Next-black?style=for-the-badge&logo=next.js&logoColor=white)
![React](https://img.shields.io/badge/react-%235D688A.svg?style=for-the-badge&logo=react&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/tailwindcss-%23F7A5A5.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Python](https://img.shields.io/badge/python-5D688A?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-5D688A?style=for-the-badge&logo=fastapi&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-F7A5A5?style=for-the-badge&logo=google&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-FFDBB6?style=for-the-badge&logo=postgresql&logoColor=white)
![Pandas](https://img.shields.io/badge/pandas-%235D688A.svg?style=for-the-badge&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/numpy-%23F7A5A5.svg?style=for-the-badge&logo=numpy&logoColor=white)
![NetworkX](https://img.shields.io/badge/NetworkX-FFDBB6?style=for-the-badge&logo=networkx&logoColor=white)
![Shadcn/UI](https://img.shields.io/badge/shadcn%2Fui-000000?style=for-the-badge&logo=shadcnui&logoColor=white)
![Recharts](https://img.shields.io/badge/Recharts-FFDBB6?style=for-the-badge&logo=react&logoColor=white)


---

## The "Council of Agents"

IRIS is powered by a coordinated **Council** of specialized AI agents, each functioning as a domain expert in financial forensics.

![Council of Agents](assets/council_of_agents_grid.png)

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


```mermaid
graph TD
    subgraph Experience["1. Experience Layer (Frontend)"]
        NextJS["Next.js 14"]
        Tailwind["Tailwind CSS + Shadcn/UI"]
        Viz["Recharts & React Flow"]
    end

    subgraph Orchestration["2. Orchestration Layer (Backend)"]
        FastAPI["FastAPI"]
        Agents["Custom Agent Loop"]
        Pandas["Pandas & NumPy"]
    end

    subgraph Intelligence["3. Intelligence Layer (AI)"]
        Gemini["Google Gemini 2.5 Flash"]
        NetworkX["NetworkX"]
        SkLearn["Scikit-Learn"]
    end

    subgraph Data["4. Data Layer (Persistence)"]
        Postgres["PostgreSQL (Supabase)"]
        Chroma["ChromaDB"]
        Redis["Redis"]
    end

    NextJS --> FastAPI
    FastAPI --> Agents
    Agents --> Gemini
    Agents --> NetworkX
    Agents --> SkLearn
    Agents --> Postgres
    Agents --> Chroma
    Agents --> Redis
```


IRIS implements a **Micro-Agent Architecture** to ensure scalability and fault tolerance.

### Frontend Layer
*   **Framework**: Next.js 14 (App Router)
*   **Styling**: Tailwind CSS + Shadcn UI
*   **Visualization**: Recharts (Financial data), React Flow (Network Graphs)

### Backend Layer
*   **API**: FastAPI (High-performance async Python)
*   **Orchestration**: Custom agent loop with shared state management
*   **AI Engine**: Google Gemini 2.5 Flash

### Data Layer
*   **Vector Store**: ChromaDB (for RAG and Document Search)
*   **Database**: PostgreSQL (for persistent transactional data)

---

## 📂 Project Structure

A quick overview of the codebase organization:

```text
IRIS1/
├── 📂 backend/             # FastAPI Core & Agents
│   ├── 📂 src/agents/      # The "Council of Agents" logic
│   ├── 📂 src/api/         # API Routes & WebSockets
│   └── 📂 tests/           # Pytest Suites
├── 📂 frontend/            # Next.js 14 Client
│   ├── 📂 components/      # Shadcn/UI & Recharts
│   └── 📂 app/             # Application Routes
├── 📂 docs/                # Detailed Documentation & Assets
└── 📂 assets/              # Diagrams & Media
```

---

## 🗺️ Roadmap

The future of IRIS includes:

- [x] **Local LLM Support**: Added fallback to Ollama for offline/private analysis.
- [x] **Shell Hunter Graph**: 3D interactive visualization of complex fraud rings.
- [x] **Refined Reporting**: HTML-formatted risk assessments with strict output controls.
- [ ] **Blockchain Layer**: Immutable audit trails for forensic reports.
- [ ] **Mobile App**: React Native version for on-the-go risk alerts.
- [ ] **Multi-Language Support**: Localization for global financial markets.
- [ ] **Advanced OCR**: Handling non-standard/scanned PDF annual reports.

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
    # Make sure your virtual environment is activated
    source iris_venv/bin/activate
    
    # Start the server (pointing to src.api.main)
    uvicorn src.api.main:app --reload
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

## 📸 Screenshots

| Dashboard Overview | Network Graph |
|:---:|:---:|
| ![Overview](assets/ola_best_1_overview.png) | ![Network](assets/ola_best_2_network.png) |
| **Real-time Risk Intelligence** | **Related Party Circular Loops** |

| Detail View |
|:---:|
| ![Details](assets/ola_best_3_details.png) |
| **Deep Forensic Metrics** |

---

## 🔧 Troubleshooting

### "Error loading ASGI app" / ModuleNotFoundError
If you see `Could not import module "src.main"`, it means you are using the old startup command.
**Solution**: Use the correct path to the main application:
```bash
uvicorn src.api.main:app --reload
```

### "Address already in use"
If port 8000 is blocked:
```bash
lsof -i :8000
kill -9 <PID>
```

### Database Connection Failed
Ensure your PostgreSQL container or service is running and the `DATABASE_URL` in `.env` is correct.


---

## Documentation

*   [Contributing Guide](CONTRIBUTING.md)

## Team

<div align="center">
  <table>
    <tr>
      <td align="center">
        <img src="assets/profile_neel.png" width="150" alt="Neel Dhoble"><br>
        <b>Neel Dhoble</b>
      </td>
      <td align="center">
        <img src="assets/profile_indrajit.png" width="150" alt="Indrajit Kshirsagar"><br>
        <b>Indrajit Kshirsagar</b>
      </td>
      <td align="center">
        <img src="assets/profile_rishi.png" width="150" alt="Rishi Koli"><br>
        <b>Rishi Koli</b>
      </td>
    </tr>
  </table>
</div>

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
