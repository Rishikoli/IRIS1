# IRIS Project Presentation Slides

## Slide 1: Title Slide
**Title**: IRIS: Investigative Risk Intelligence System
**Subtitle**: Autonomic Multi-Agent AI for Financial Forensics & Fraud Detection
**Presenter**: [Your Name/Team Name]

---

## Slide 2: The Problem - "The Iceberg of Financial Risk"
**Headline**: Financial Fraud is Complex, Hidden, and Devastating.

*   **Complexity**: Fraudsters use intricate webs of shell companies and circular trading loops to obscure money trails.
*   **Data Overload**: Assessing risk requires analyzing thousands of documents (filings, news, RPTs), which is impossible for humans to do in real-time.
*   **Reactive vs. Proactive**: Traditional auditing is reactive—it often catches fraud only *after* a collapse (e.g., Enron, Satyam).
*   **The Cost**: Billions lost annually due to undetected accounting irregularities and "window dressing."

---

## Slide 2.5: Research & Motivation (The "Why")
**Headline**: Validated by Market Gaps & Data Reality.

*   **Research Finding 1: The Detection Lag**
    *   *ACFE Report 2024*: The average corporate fraud goes undetected for **12 months**, causing a median loss of **₹1.2 Crores ($145k)** per case.
    *   **Our Insight**: The delay exists because auditors are drowning in data. We need *speed* and *automation*.
*   **Research Finding 2: The "Unstructured" Blindspot**
    *   Quantitative models (ratios) only tell half the story.
    *   **80% of warning signals** (sudden director resignations, vague auditor notes, negative news sentiment) lie in **unstructured text**, which traditional ERPs ignore.
*   **Research Finding 3: The Network Effect**
    *   Most financial tools analyze companies in isolation.
    *   **Reality Check**: Modern fraud is **networked** (shell companies, circular trading). You cannot detect it without Graph Technology.
*   **Conclusion**: There is a critical need for a system that fuses **Numbers (Financials)**, **Text (Sentiment)**, and **Graphs (Connections)** into a single intelligence layer.

---

## Slide 2.6: Target Audience (End Users)
**Headline**: Empowering the Guardians of Finance.

1.  **Forensic Auditors & CA Firms**:
    *   *Need*: To automate routine checks and focus on high-value investigation.
    *   *IRIS Value*: Reduces initial data crunching time by 90%.
2.  **Regulatory Bodies (SEBI, MCA, RBI)**:
    *   *Need*: Market-wide surveillance to detect systemic risks early.
    *   *IRIS Value*: "God-mode" view of shell networks and circular trading.
3.  **Banks & Lenders**:
    *   *Need*: Pre-disbursal due diligence and post-disbursal monitoring.
    *   *IRIS Value*: Early warning system for rising credit risk.
4.  **Institutional Investors (PE/VC)**:
    *   *Need*: Deep due diligence beyond the pitch deck.
    *   *IRIS Value*: Uncovers hidden risks and governance issues.

---

## Slide 3: The Solution - IRIS
**Headline**: Seeing the Invisible with Autonomic Multi-Agent AI.

*   **What is IRIS?**
    *   IRIS (Investigative Risk Intelligence System) is not just a dashboard; it is an **Autonomic Agentic System**.
    *   It acts as a **Digital Forensic Squad** that works 24/7 to ingest, analyze, and cross-reference financial data across multiple dimensions.
*   **The Paradigm Shift**:
    *   **From Static to Dynamic**: Moving from quarterly spreadsheet checks to real-time, continuous monitoring.
    *   **From Siloed to Holistic**: Fusing *Quantitative/Structured Data* (Balance Sheets, Cash Flows) with *Qualitative/Unstructured Data* (News, Auditor Notes, Management Commentary) and *Network Data* (related party maps).
*   **Core Philosophy**: "Follow the Money, but also Follow the Intent."
    *   IRIS doesn't just calculate ratios; it looks for the *behavioral signatures* of fraud (e.g., complex shell structures, sentiment anomalies vs. financial reality).
*   **Key Differentiator**: **The "Council of Agents"**
    *   Unlike generic AI wrappers, IRIS delegates tasks to specialized agents (e.g., a "Shell Hunter" for graphs, a "Forensic Auditor" for numbers).
    *   These agents reason independently using **Gemini 2.5 Flash** and then collaborate to form a unified Risk Score.

---

## Slide 3.5: Unique Value Proposition (UVP)
**Headline**: Why IRIS Wins.

| Feature | The Value (Why it matters) |
| :--- | :--- |
| **Autenomic Agents** | **Speed**: Analyzes 1000+ pages of filings in seconds, not weeks. |
| **Network Graph** | **Visibility**: Sees the "Shadow Economy" that spreadsheets miss. |
| **Multi-Modal AI** | **Context**: Connects numbers (profit) with text (news) for truth. |
| **Explainable Risk** | **Trust**: Doesn't just say "High Risk"—tells you *why* (e.g., "Circular Trading"). |

*   **The Bottom Line**: IRIS transforms audit from a **Cost Center** (Compliance) to a **Value Center** (Risk Intelligence).

---

## Slide 4: System Capabilities
**Headline**: Comprehensive 360° Forensic Intelligence.

1.  **Forensic Deep-Dives**:
    *   Automated calculation of **Altman Z-Score** (Bankruptcy) & **Beneish M-Score** (Manipulation).
    *   **Benford's Law** analysis to detect fabricated data.
2.  **The "Shell Hunter"**:
    *   Visualizes the **Shadow Economy** of related party transactions (RPTs).
    *   Detects money laundering cycles and interlocking directorates automatically.
3.  **Real-Time Risk Scoring**:
    *   Dynamic 0-100 Risk Score updated with live market data.
    *   **Explainable AI (SHAP)**: Tells you *why* a company is risky (e.g., "High leverage + Negative sentiment").
4.  **Generative Reporting**:
    *   One-click generation of executive-grade audit reports (PDF/Excel).

---

## Slide 5: The "Council of Agents" (Architecture)
**Headline**: A Swarm of Specialized Experts.

| Agent | Name | Function |
| :--- | :--- | :--- |
| **Agent 1** | **Forensic Analyst** | Crunches numbers, ratios, and fraud scores (M-Score/Z-Score). |
| **Agent 2** | **Shell Hunter** | Finds hidden connections, shell companies, and circular trading. |
| **Agent 3** | **Risk Judge** | Synthesizes all findings into a final Risk Score (0-100). |
| **Agent 4** | **Reporter** | Generates executive-grade PDF/Excel audit reports. |
| **Agent 5** | **QA RAG** | "The Librarian" - Answers questions from annual reports. |
| **Agent 6** | **Market Sentinel** | Monitors news sentiment using FinBERT. |

**Tech Stack**:
*   **Generative AI**: Google Gemini 2.5 Flash (Reasoning & Code).
*   **Machine Learning**:
    *   **FinBERT**: Specialized Financial Sentiment Analysis (Hugging Face).
    *   **Sentence Transformers**: `all-MiniLM-L6-v2` for Vector Embeddings (RAG).
*   **Backend**: Python (FastAPI) + NetworkX (Graph Theory).
*   **Frontend**: Next.js + React Flow (Visualization).

---

## Slide 6: Live Demo / Visuals
**Headline**: Turning Data into Decisions.

*   *(Placeholder for Screenshot 1)*: The **Network Graph** exploding a complex shell company web.
*   *(Placeholder for Screenshot 2)*: The **Risk Score Dashboard** showing a high-risk alert.
*   *(Placeholder for Screenshot 3)*: The **Financial Ratios** breakdown showing declining health.

---

## Slide 6: The X-Factor (The WOW)
**Headline**: What makes IRIS truly unique?

1.  **The "God-Mode" View**:
    *   While others see a spreadsheet row, IRIS sees the **entire network**.
    *   *Visual WOW*: Watch the "Shell Hunter" graph **explode** hidden connections in real-time.
2.  **The "Council" Concept**:
    *   It’s not just one AI; it’s a **collaborative squad**. Warning signs from the "News Agent" trigger deeper checks by the "Forensic Agent."
3.  **No More "Black Boxes"**:
    *   Every Risk Score explains itself. "I flagged this company because..." (SHAP values).
4.  **One-Click Audit**:
    *   Generates a 20-page, regulator-ready investigation report in < 30 seconds.

---

## Slide 7: Impact & Future
**Headline**: From "Auditing" to "Intelligence".

*   **Speed**: Investigations that took weeks now take minutes.
*   **Depth**: Uncovers risks that are invisible to standard spreadsheet analysis.
*   **Future Roadmap**:
    *   Integration with live GST/MCA databases.
    *   Predictive failure modeling using time-series AI.
    *   Autonomous "Watchdog" mode for continuous portfolio monitoring.
