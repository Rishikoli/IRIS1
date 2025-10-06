<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Complete Project IRIS Structure with Updated Tasks

## Complete Directory Structure

```
iris-backend/
│
├── .kiro/
│   └── specs/
│       └── project-iris-forensic/
│           ├── requirements.md          # ✅ Created (10 requirements)
│           ├── design.md                # ✅ Created (complete design)
│           └── tasks.md                 # ✅ Created (18 tasks with subtasks)
│
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   └── forensic/                   # Forensic analysis agents
│   │       ├── __init__.py
│   │       ├── agent1_ingestion.py     # Data ingestion from APIs
│   │       ├── agent2_forensic_analysis.py  # Benford, Z-Score, M-Score
│   │       ├── agent3_risk_scoring.py  # Composite risk calculation
│   │       ├── agent4_compliance.py    # Ind AS, SEBI LODR validation
│   │       ├── agent5_reporting.py     # Gemini 2.0 report generation
│   │       ├── agent6_orchestrator.py  # Pipeline coordinator
│   │       ├── agent7_qa.py            # RAG-based Q&A
│   │       ├── agent8_sentiment.py     # Google Trends, news sentiment
│   │       ├── agent9_peer_benchmarking.py  # Peer comparison
│   │       └── agent10_regulatory.py   # SEBI enforcement monitoring
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py                     # FastAPI app with Swagger
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── company.py              # Request/response models
│   │   │   ├── forensic_analysis.py
│   │   │   ├── chat.py
│   │   │   └── job.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── company_routes.py       # Company search endpoints
│   │       ├── forensic_routes.py      # Forensic analysis endpoints
│   │       └── chat_routes.py          # Q&A chat endpoints
│   │
│   ├── api_clients/
│   │   ├── __init__.py
│   │   ├── indian_api_client.py        # IndianAPI wrapper
│   │   ├── nse_client.py               # NSE portal scraper
│   │   └── bse_client.py               # BSE portal scraper
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── company.py                  # SQLAlchemy ORM models
│   │   ├── financial_statements.py
│   │   ├── forensic_analysis.py
│   │   ├── risk_scores.py
│   │   ├── compliance.py
│   │   ├── jobs.py
│   │   ├── chat.py
│   │   └── regulatory.py
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py               # PostgreSQL connection manager
│   │   └── migrations/
│   │       └── create_tables.sql       # Database schema initialization
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py                   # Structured logging
│   │   ├── ocr_processor.py            # OpenVINO OCR
│   │   └── validators.py               # Data validation helpers
│   │
│   ├── metrics/
│   │   ├── __init__.py
│   │   └── prometheus.py               # Prometheus metrics
│   │
│   ├── celery_app.py                   # Celery task configuration
│   └── config.py                       # Environment configuration
│
├── tests/
│   ├── __init__.py
│   ├── fixtures/
│   │   ├── __init__.py
│   │   ├── sample_companies.py
│   │   └── sample_financials.py
│   │
│   ├── unit/
│   │   ├── __init__.py
│   │   └── forensic/
│   │       ├── __init__.py
│   │       ├── test_agent1_ingestion.py
│   │       ├── test_agent2_forensic_analysis.py
│   │       ├── test_agent3_risk_scoring.py
│   │       ├── test_agent4_compliance.py
│   │       ├── test_agent5_reporting.py
│   │       ├── test_agent7_qa.py
│   │       ├── test_agent8_sentiment.py
│   │       ├── test_agent9_benchmarking.py
│   │       └── test_agent10_regulatory.py
│   │
│   ├── integration/
│   │   ├── __init__.py
│   │   └── forensic/
│   │       ├── __init__.py
│   │       ├── test_full_pipeline.py
│   │       └── test_qa_retrieval.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── test_company_endpoints.py
│   │   └── forensic/
│   │       ├── __init__.py
│   │       ├── test_analysis_endpoints.py
│   │       └── test_chat_endpoints.py
│   │
│   └── e2e/
│       ├── __init__.py
│       └── forensic/
│           ├── __init__.py
│           └── test_complete_workflow.py
│
├── scripts/
│   ├── init_db.sh                      # Database initialization
│   ├── run_tests.sh                    # CI/CD test runner
│   └── start_celery.sh                 # Celery worker startup
│
├── config/
│   ├── logging.yaml                    # Logging configuration
│   └── grafana_dashboard.json          # Grafana dashboard template
│
├── docs/
│   ├── api_documentation.md            # API usage guide
│   ├── architecture.md                 # System architecture
│   └── agent_details.md                # Agent implementation details
│
├── .env.template                       # Environment variables template
├── .dockerignore
├── .gitignore
├── Dockerfile                          # FastAPI application container
├── docker-compose.yml                  # Multi-service orchestration
├── requirements.txt                    # Python dependencies
├── pytest.ini                          # Pytest configuration
├── README.md                           # Setup and usage instructions
└── LICENSE
```


## Updated tasks.md

```markdown
# Implementation Plan - Project IRIS (Backend Only - Forensic Focus)

- [x] 1. Set up project infrastructure and base configuration
  - Create Python project structure: src/agents/forensic/, src/models, src/database, src/api directories
  - Create agents directory structure: src/agents/forensic/ for financial forensics agents (allows future src/agents/fraud_detection/, src/agents/credit_analysis/, etc.)
  - Write requirements.txt with dependencies: fastapi, uvicorn, sqlalchemy, psycopg2-binary, chromadb, google-generativeai, sentence-transformers, celery, redis, pytrends, beautifulsoup4, requests, pytest, pytest-cov, pydantic
  - Create .env.template with API keys placeholders (GEMINI_API_KEY, INDIAN_API_KEY, NSE_API_KEY, BSE_API_KEY)
  - Write PostgreSQL database initialization script (create_tables.sql) with all schema tables from design
  - Create docker-compose.yml for PostgreSQL, Redis, ChromaDB services
  - _Requirements: 1.1, 2.1, 3.1, 4.1, 5.1, 6.1, 7.1, 8.1, 9.1, 10.1_

- [x] 2. Implement database models and connection utilities
  - [x] 2.1 Create SQLAlchemy ORM models for all PostgreSQL tables
    - Write models/company.py with Company model
    - Write models/financial_statements.py with FinancialStatement model
    - Write models/forensic_analysis.py with ForensicAnalysis model
    - Write models/risk_scores.py, models/compliance.py, models/jobs.py, models/chat.py
    - Implement JSONB field serialization/deserialization helpers
    - _Requirements: 1.2, 1.3, 2.2, 3.2, 4.2, 5.2, 6.2, 7.2_
  - [x] 2.2 Implement database connection manager
    - Write database/connection.py with PostgreSQLClient class
    - Implement connection pooling with SQLAlchemy engine
    - Write execute() method for raw SQL queries with error handling
    - Create unit tests for connection management and query execution
    - _Requirements: 1.6, 6.1_

- [x] 3. Implement Agent 1: Data Ingestion Agent (Forensic)
  - [x] 3.1 Create API client wrappers for external data sources
    - Write api_clients/indian_api_client.py with IndianAPIClient class
    - Implement search_company(), get_financials() methods with rate limiting
    - Write api_clients/nse_client.py with NSEClient for corporate filings
    - Write api_clients/bse_client.py with BSEClient for announcements
    - Implement retry logic with exponential backoff for rate limit errors
    - Create unit tests mocking API responses
    - _Requirements: 1.1, 1.2_
  - [x] 3.2 Implement financial data normalization
    - Write agents/forensic/agent1_ingestion.py with DataIngestionAgent class
    - Implement normalize_financial_statements() to convert XBRL/JSON to standard schema
    - Write balance_sheet_validator() to check Assets = Liabilities + Equity equation
    - Create unit tests with sample XBRL data and validation edge cases
    - _Requirements: 1.3, 1.6_
  - [x] 3.3 Implement disclosure document scraping and OCR
    - Write fetch_disclosure_documents() to scrape NSE/BSE portals with BeautifulSoup
    - Implement PDF download and OpenVINO OCR extraction (ocr_processor.py)
    - Write parse_annual_report_sections() to extract MD&A, audit report, notes
    - Store extracted text in disclosure_documents table with source URLs
    - Create integration tests with sample PDFs
    - _Requirements: 1.4, 1.5_

- [ ] 4. Implement Agent 2: Forensic Analysis Agent
  - [ ] 4.1 Implement vertical and horizontal analysis functions
    - Write agents/forensic/agent2_forensic_analysis.py with ForensicAnalysisAgent class
    - Implement vertical_analysis() to calculate common-size percentages
    - Implement horizontal_analysis() for YoY and QoQ growth rates
    - Create unit tests with sample financial statements
    - _Requirements: 2.1, 2.2_
  - [ ] 4.2 Implement financial ratio calculations
    - Write calculate_liquidity_ratios() for current ratio, quick ratio, cash ratio
    - Write calculate_profitability_ratios() for ROE, ROA, net margin, gross margin
    - Write calculate_leverage_ratios() for debt-to-equity, interest coverage
    - Write calculate_efficiency_ratios() for asset turnover, receivables turnover
    - Create unit tests verifying ratio formulas with known financial data
    - _Requirements: 2.2_
  - [ ] 4.3 Implement Benford's Law test
    - Write benford_analysis() to extract first digits from line items
    - Implement chi-square statistical test comparing to expected Benford distribution
    - Flag anomalies when chi-square > 15.507 (95% confidence threshold)
    - Create unit tests with manipulated data (uniform distribution) to verify detection
    - _Requirements: 2.4_
  - [ ] 4.4 Implement Altman Z-Score calculation
    - Write calculate_z_score() with formula: Z = 1.2A + 1.4B + 3.3C + 0.6D + 1.0E
    - Implement classification logic: SAFE (>2.99), GREY (1.81-2.99), DISTRESS (<1.81)
    - Create unit tests with sample company data for each classification
    - _Requirements: 2.5_
  - [ ] 4.5 Implement Beneish M-Score calculation
    - Write calculate_m_score() with 8-variable model (DSRI, GMI, AQI, SGI, DEPI, SGAI, LVGI, TATA)
    - Calculate each variable from current and prior period financials
    - Flag manipulation risk when M-Score > -1.78
    - Create unit tests with known manipulator vs non-manipulator examples
    - _Requirements: 2.6_
  - [ ] 4.6 Implement anomaly detection rules
    - Write detect_anomalies() with rule-based checks for revenue decline, profit-cash divergence, receivables buildup
    - Implement severity classification (LOW, MEDIUM, HIGH, CRITICAL)
    - Store anomalies in forensic_analysis table with evidence JSONB
    - Create unit tests for each anomaly type with edge cases
    - _Requirements: 2.7, 2.8_

- [ ] 5. Implement Agent 3: Risk Scoring Agent (Forensic)
  - [ ] 5.1 Implement category-specific scoring functions
    - Write agents/forensic/agent3_risk_scoring.py with RiskScoringAgent class
    - Implement score_financial_health() based on Z-Score, current ratio, debt-equity
    - Implement score_earnings_quality() based on M-Score and cash flow quality
    - Implement score_disclosure_quality() based on filing timeliness and audit qualifications
    - Create unit tests for each scoring function with boundary values
    - _Requirements: 3.1, 3.2_
  - [ ] 5.2 Implement composite risk score calculation
    - Write calculate_risk_score() applying weighted aggregation across 6 categories
    - Implement classify_risk() to assign LOW/MEDIUM/HIGH/CRITICAL based on composite score
    - Store risk score breakdown in risk_scores table
    - Create unit tests verifying weight application and classification thresholds
    - _Requirements: 3.3, 3.4, 3.5_

- [ ] 6. Implement Agent 4: Compliance Validation Agent (Forensic)
  - [ ] 6.1 Implement Ind AS compliance checks
    - Write agents/forensic/agent4_compliance.py with ComplianceValidationAgent class
    - Implement check_ind_as_1() for balance sheet equation validation
    - Implement check_ind_as_7() for cash flow statement presence
    - Implement check_ind_as_24() for related party transaction disclosures
    - Create unit tests with compliant and non-compliant sample data
    - _Requirements: 4.1, 4.2_
  - [ ] 6.2 Implement SEBI LODR compliance checks
    - Write check_sebi_lodr_33() for quarterly results filing deadline (45 days)
    - Write check_sebi_lodr_31() for shareholding pattern deadline (21 days)
    - Write check_sebi_lodr_23() for RPT threshold and approval requirements
    - Store violations in compliance_validation table with regulation references
    - Create unit tests with late filings and missing approvals
    - _Requirements: 4.3, 4.4, 4.5_
  - [ ] 6.3 Implement Companies Act compliance checks
    - Write check_companies_act_143() for auditor report qualification detection
    - Flag CRITICAL severity when qualifications found in audit report text
    - Create unit tests with sample audit reports containing qualifications
    - _Requirements: 4.6, 4.7_

- [ ] 7. Implement Agent 5: Reporting Agent (Forensic)
  - [ ] 7.1 Implement Gemini 2.0 integration for executive summaries
    - Write agents/forensic/agent5_reporting.py with ReportingAgent class
    - Implement generate_executive_summary() calling Gemini API with prompt template
    - Configure Gemini model with temperature=0.1, max_output_tokens=8192
    - Write generate_recommendations() for actionable insights
    - Create integration tests with mock Gemini responses
    - _Requirements: 5.1, 5.7_
  - [ ] 7.2 Implement report data formatting functions
    - Write generate_forensic_report() compiling ratio tables, Z-Score, M-Score results
    - Write prepare_dashboard_data() formatting KPI cards, trend charts, heatmaps as JSON
    - Implement export_pdf() using ReportLab library for audit-ready reports
    - Implement export_excel() using xlsxwriter for raw data export
    - Store generated reports in reports table
    - Create unit tests verifying JSON structure for API responses
    - _Requirements: 5.2, 5.3, 5.6_

- [ ] 8. Implement Agent 6: Orchestrator Agent (Forensic)
  - [ ] 8.1 Implement job lifecycle management
    - Write agents/forensic/agent6_orchestrator.py with ForensicOrchestratorAgent class
    - Implement create_job() inserting record in analysis_jobs table with CREATED status and job_type='FORENSIC'
    - Implement update_job_status() for state transitions
    - Write handle_agent_failure() with retry logic (max 3 attempts, exponential backoff)
    - Create unit tests for job state machine transitions
    - _Requirements: 6.1, 6.3, 6.4, 6.6_
  - [ ] 8.2 Implement forensic agent pipeline execution
    - Write execute_forensic_analysis() coordinating sequential and parallel agent calls
    - Call agents in order: Agent1 → Agent2 → [Agent3 || Agent4] → Agent9 → Agent10 → Agent5 → Agent7
    - Implement error handling with job status updates on failures
    - Store pipeline results in respective tables (forensic_analysis, risk_scores, etc.)
    - Create integration tests with mock agent responses
    - _Requirements: 6.2, 6.5_

- [ ] 9. Implement Agent 7: Interactive Q&A Agent (Forensic)
  - [ ] 9.1 Implement ChromaDB vector storage integration
    - Write agents/forensic/agent7_qa.py with ForensicQAAgent class
    - Initialize ChromaDB client and create collections per company (forensic_company_{company_id})
    - Implement index_company_data() to embed financial data, disclosures, reports using FinLang model
    - Write chunking logic (max 512 tokens) for document embedding
    - Create unit tests for embedding generation and storage
    - _Requirements: 7.1, 7.2_
  - [ ] 9.2 Implement RAG-based query answering
    - Write answer_query() performing semantic search in ChromaDB (top 5 results)
    - Implement RAG prompt template with retrieved context and citation instructions
    - Call Gemini 2.0 Flash for response generation
    - Extract citations from response text using regex pattern \[source_type:source_id\]
    - Calculate confidence score from retrieval distances
    - Create integration tests with sample queries and expected citations
    - _Requirements: 7.3, 7.4, 7.5, 7.8_
  - [ ] 9.3 Implement follow-up question generation
    - Write generate_follow_ups() calling Gemini to suggest 3 relevant follow-up questions
    - Parse numbered list from Gemini response
    - Store conversation in chat_messages table with session_id and agent_type='FORENSIC'
    - Create unit tests verifying follow-up question format
    - _Requirements: 7.6, 7.7_

- [ ] 10. Implement Agent 8: Market Sentiment & Trends Agent (Forensic)
  - [ ] 10.1 Implement Google Trends scraping with pytrends
    - Write agents/forensic/agent8_sentiment.py with MarketSentimentAgent class
    - Initialize pytrends with hl='en-IN', tz=330 for India timezone
    - Implement fetch_google_trends() with keyword variations (company name, "fraud", "scam", "stock")
    - Retrieve interest_over_time, interest_by_region, related_queries
    - Implement rate limiting (2s delay between requests) and retry logic for 429 errors
    - Store trends data in google_trends_data table
    - Create integration tests with mock pytrends responses
    - _Requirements: 8.1, 8.2_
  - [ ] 10.2 Implement news sentiment analysis
    - Write scrape_financial_news() extracting articles from Economic Times, Business Standard, MoneyControl
    - Implement FinBERT sentiment classification for each article
    - Calculate aggregate sentiment score with weighted formula (news 3x, tweets 1x, Reddit 2x)
    - Create unit tests with sample articles and expected sentiment labels
    - _Requirements: 8.5, 8.6_
  - [ ] 10.3 Implement sentiment-financial divergence detection
    - Write analyze_sentiment_divergence() comparing revenue growth vs search trend change
    - Flag REVENUE_SEARCH_DIVERGENCE if revenue >15% but search <-20%
    - Flag NEGATIVE_SEARCH_SPIKE if negative keyword volume >30
    - Flag GEOGRAPHIC_MISMATCH if state search <30pp below reported revenue
    - Store anomalies in trends_anomalies table
    - Create unit tests for each divergence scenario
    - _Requirements: 8.3, 8.4, 8.7_

- [ ] 11. Implement Agent 9: Peer Benchmarking Agent (Forensic)
  - [ ] 11.1 Implement peer group identification
    - Write agents/forensic/agent9_peer_benchmarking.py with PeerBenchmarkingAgent class
    - Implement identify_peer_group() querying companies by sector and market cap (0.5x-2x)
    - Sort peers by market cap similarity and limit to top 10
    - Create unit tests with sample company database
    - _Requirements: 9.1_
  - [ ] 11.2 Implement ratio benchmarking with statistical analysis
    - Write fetch_peer_financials() retrieving ratios from IndianAPI for all peers
    - Implement benchmark_ratios() calculating median, P25, P75, mean, stddev for each ratio
    - Calculate z-scores: (company_value - peer_mean) / peer_stddev
    - Calculate percentile ranks (0-100th)
    - Flag outliers where |z-score| > 2.0
    - Store benchmarks in peer_benchmarks table
    - Create unit tests verifying z-score calculation
    - _Requirements: 9.2, 9.3, 9.4_
  - [ ] 11.3 Implement peer anomaly detection
    - Write detect_peer_anomalies() flagging ratio outliers and growth divergences
    - Flag GROWTH_DIVERGENCE if company grows >15% while peers decline <-5%
    - Flag UNDERPERFORMANCE if company declines <-10% while peers grow >10%
    - Create unit tests for divergence scenarios
    - _Requirements: 9.5, 9.6, 9.7_

- [ ] 12. Implement Agent 10: Regulatory Monitoring Agent (Forensic)
  - [ ] 12.1 Implement SEBI enforcement action scraping
    - Write agents/forensic/agent10_regulatory.py with RegulatoryMonitoringAgent class
    - Implement scrape_sebi_enforcement() with BeautifulSoup parsing SEBI website
    - Extract action date, order type, entity name, description from HTML tables
    - Filter by company name and date range (last 3 years)
    - Store actions in sebi_enforcement_actions table
    - Create integration tests with mock HTML responses
    - _Requirements: 10.1, 10.2_
  - [ ] 12.2 Implement compliance deadline calculation
    - Write calculate_compliance_deadlines() determining fiscal quarters from company fiscal_year_end
    - Calculate quarterly results deadline (45 days), annual report (21 days before AGM), shareholding pattern (21 days)
    - Flag deadlines as UPCOMING (>7 days), URGENT (≤7 days), OVERDUE (<0 days)
    - Store deadlines in compliance_deadlines table
    - Create unit tests with various fiscal year ends
    - _Requirements: 10.3, 10.4, 10.5_
  - [ ] 12.3 Implement regulatory risk scoring
    - Write generate_regulatory_risk_score() applying penalties: SCN +15, adjudication +25, debarment +40, overdue +20
    - Classify as CRITICAL (≥60), HIGH (40-59), MEDIUM (20-39), LOW (<20)
    - Store scores in regulatory_risk_scores table
    - Create unit tests verifying penalty application
    - _Requirements: 10.6, 10.7_

- [ ] 13. Implement FastAPI REST API with Swagger/OpenAPI documentation
  - [ ] 13.1 Create FastAPI app with automatic OpenAPI schema generation
    - Write api/main.py with FastAPI app initialization
    - Configure app metadata (title="IRIS Forensic API", description="Financial Forensics Analysis Platform", version="1.0.0")
    - Enable automatic Swagger UI at /docs endpoint
    - Enable ReDoc documentation at /redoc endpoint
    - Configure CORS middleware for frontend integration
    - Write health check endpoint GET /health returning {"status": "healthy", "module": "forensic"}
    - Create startup/shutdown event handlers for database connections
    - _Requirements: 6.1_
  - [ ] 13.2 Implement Pydantic request/response models with validation
    - Write api/schemas/company.py with CompanySearchRequest, CompanySearchResponse models
    - Write api/schemas/forensic_analysis.py with ForensicAnalysisRequest (company_id, start_date, end_date), ForensicAnalysisResponse models
    - Write api/schemas/chat.py with ChatRequest (company_id, query, session_id, agent_type='forensic'), ChatResponse models
    - Write api/schemas/job.py with JobStatusResponse model including job_type field
    - Add Field validators, examples, and descriptions for OpenAPI documentation
    - Create unit tests for schema validation
    - _Requirements: 1.1, 6.1, 7.1_
  - [ ] 13.3 Implement company search and lookup endpoints
    - Write GET /api/v1/companies/search endpoint with query parameter accepting company name/ticker/CIN
    - Call agent1.search_company() and return list of matching companies with metadata
    - Add OpenAPI tags: ["Companies"], summary, description for Swagger grouping
    - Write GET /api/v1/companies/{company_id} endpoint returning company details
    - Create API tests with TestClient validating response structure
    - _Requirements: 1.1_
  - [ ] 13.4 Implement forensic analysis workflow endpoints
    - Write POST /api/v1/forensic/analysis endpoint accepting ForensicAnalysisRequest body
    - Trigger orchestrator.execute_forensic_analysis() as async background task
    - Return job_id, job_type='FORENSIC', and initial status immediately (202 Accepted)
    - Write GET /api/v1/forensic/analysis/{job_id}/status endpoint returning current job state
    - Write GET /api/v1/forensic/analysis/{job_id}/results endpoint returning complete analysis results once COMPLETED
    - Add OpenAPI tags: ["Forensic Analysis"]
    - Add response models with example data for Swagger
    - Create API tests for analysis lifecycle (submit → poll status → retrieve results)
    - _Requirements: 6.1, 6.2, 6.6_
  - [ ] 13.5 Implement report export endpoints
    - Write GET /api/v1/forensic/analysis/{job_id}/reports/pdf endpoint returning PDF file as StreamingResponse
    - Write GET /api/v1/forensic/analysis/{job_id}/reports/excel endpoint returning Excel file
    - Write GET /api/v1/forensic/analysis/{job_id}/reports/json endpoint returning structured JSON report
    - Set appropriate Content-Type headers and Content-Disposition for file downloads
    - Add OpenAPI tags: ["Forensic Reports"]
    - Create API tests verifying file download functionality
    - _Requirements: 5.6_
  - [ ] 13.6 Implement Q&A chat endpoints for forensic analysis
    - Write POST /api/v1/forensic/chat endpoint accepting ChatRequest with company_id, query, session_id
    - Call agent7.answer_query() and return ChatResponse with answer, citations, confidence, follow_ups
    - Write GET /api/v1/forensic/chat/{session_id}/history endpoint returning all messages in conversation
    - Write DELETE /api/v1/forensic/chat/{session_id} endpoint clearing conversation history
    - Add OpenAPI tags: ["Forensic Q&A"]
    - Add detailed OpenAPI descriptions for citation format and confidence scoring
    - Create API tests for multi-turn conversations
    - _Requirements: 7.1, 7.3, 7.4, 7.5, 7.6, 7.7_
  - [ ] 13.7 Implement risk and compliance endpoints
    - Write GET /api/v1/forensic/analysis/{job_id}/risk-score endpoint returning risk breakdown by category
    - Write GET /api/v1/forensic/analysis/{job_id}/compliance endpoint returning violations and warnings
    - Write GET /api/v1/forensic/analysis/{job_id}/anomalies endpoint returning list of detected anomalies
    - Write GET /api/v1/forensic/analysis/{job_id}/peer-benchmark endpoint returning peer comparison data
    - Add OpenAPI tags: ["Forensic Risk & Compliance"]
    - Add OpenAPI response examples with sample risk scores and anomalies
    - Create API tests validating data structure
    - _Requirements: 3.5, 4.7, 9.7_
  - [ ] 13.8 Implement WebSocket endpoint for real-time job updates
    - Write WebSocket /api/v1/forensic/ws/{job_id} endpoint streaming job status changes
    - Emit JSON messages when orchestrator updates job status (INGESTING_DATA, ANALYZING, etc.)
    - Implement heartbeat ping/pong for connection health
    - Handle client disconnections gracefully
    - Create WebSocket client test simulating connection and message reception
    - _Requirements: 6.3_
  - [ ] 13.9 Add comprehensive OpenAPI tags and metadata
    - Tag endpoints by category: "Companies", "Forensic Analysis", "Forensic Q&A", "Forensic Reports", "Forensic Risk & Compliance"
    - Add detailed operation summaries and descriptions for each endpoint
    - Include request/response examples in schemas
    - Add authentication placeholders (API key headers) for future security implementation
    - Document error responses (400, 404, 422, 500) with example error objects
    - Verify Swagger UI displays organized, user-friendly API documentation at /docs
    - _Requirements: 6.1_

- [ ] 14. Implement Celery background task system
  - [ ] 14.1 Configure Celery with Redis broker
    - Write celery_app.py with Celery configuration (broker='redis://localhost:6379', backend='redis://localhost:6379')
    - Define task queues: default, forensic_analysis, sentiment_monitoring
    - Configure task serialization with JSON
    - Set task time limits (soft=600s, hard=900s)
    - Create celery worker startup script for forensic tasks
    - _Requirements: 6.1_
  - [ ] 14.2 Implement async forensic analysis task
    - Write @celery_app.task decorator for execute_forensic_analysis_task(company_id, date_range)
    - Call orchestrator.execute_forensic_analysis() within task
    - Update job status via database throughout execution with job_type='FORENSIC'
    - Handle task failures with retry logic (max_retries=3, retry_backoff=True)
    - Create unit tests with mock orchestrator
    - _Requirements: 6.1, 6.2_
  - [ ] 14.3 Implement scheduled sentiment monitoring task
    - Write @celery_app.task for daily_sentiment_scrape() calling agent8 for monitored companies
    - Schedule with celery beat: crontab(hour=2, minute=0) for 2 AM IST execution
    - Store results in google_trends_data and sentiment_anomalies tables
    - Send email alerts when CRITICAL sentiment anomalies detected
    - Create unit tests with mock email sending
    - _Requirements: 8.1_

- [ ] 15. Write comprehensive test suites
  - [ ] 15.1 Create unit tests for all forensic agent functions
    - Write tests/unit/forensic/test_agent1_ingestion.py for data normalization and validation
    - Write tests/unit/forensic/test_agent2_forensic_analysis.py for Benford, Z-Score, M-Score calculations
    - Write tests/unit/forensic/test_agent3_risk_scoring.py for scoring formulas and classification
    - Write tests/unit/forensic/test_agent4_compliance.py for rule-based checks
    - Write tests/unit/forensic/test_agent5_reporting.py for report formatting (mock Gemini)
    - Write tests/unit/forensic/test_agent7_qa.py for RAG retrieval and citation extraction
    - Write tests/unit/forensic/test_agent8_sentiment.py for sentiment aggregation
    - Write tests/unit/forensic/test_agent9_benchmarking.py for z-score calculations
    - Write tests/unit/forensic/test_agent10_regulatory.py for deadline calculations
    - Achieve >80% code coverage for forensic agent modules
    - _Requirements: All requirements_
  - [ ] 15.2 Create integration tests for forensic agent pipelines
    - Write tests/integration/forensic/test_full_pipeline.py executing end-to-end forensic workflow with test company data
    - Write tests/integration/forensic/test_qa_retrieval.py for RAG system with ChromaDB
    - Mock external APIs (IndianAPI, NSE, BSE, Gemini) using responses library
    - Verify database state after pipeline execution
    - Test error handling and retry mechanisms
    - _Requirements: 6.2_
  - [ ] 15.3 Create API endpoint tests
    - Write tests/api/test_company_endpoints.py for /companies/* routes
    - Write tests/api/forensic/test_analysis_endpoints.py for /forensic/analysis/* routes
    - Write tests/api/forensic/test_chat_endpoints.py for /forensic/chat/* routes
    - Use FastAPI TestClient for request/response validation
    - Test error handling (400 bad requests, 404 not found, 422 validation errors)
    - Test WebSocket connection and message streaming
    - _Requirements: 6.1_
  - [ ] 15.4 Create database test fixtures
    - Write tests/fixtures/sample_companies.py with mock company data
    - Write tests/fixtures/sample_financials.py with realistic financial statements
    - Create database setup/teardown fixtures for isolated test execution
    - Implement database migration testing
    - _Requirements: 1.1, 2.1_

- [ ] 16. Implement monitoring and logging
  - [ ] 16.1 Configure structured logging
    - Write utils/logger.py with JSON formatter for structured logs
    - Configure log levels: DEBUG for development, INFO for production
    - Add correlation IDs (job_id) and module context (agent_type='forensic') to all log messages
    - Implement log aggregation preparation (compatible with ELK/Loki)
    - Create logging middleware for FastAPI capturing request/response
    - _Requirements: 6.1_
  - [ ] 16.2 Implement Prometheus metrics
    - Add prometheus_client dependency to requirements.txt
    - Write metrics/prometheus.py exposing /metrics endpoint
    - Track metrics: forensic_jobs_total, forensic_analysis_duration_seconds, api_requests_total, forensic_agent_execution_time
    - Create Grafana dashboard JSON template for forensic module
    - _Requirements: 6.1_

- [ ] 17. Create deployment configuration
  - [ ] 17.1 Write Docker configuration
    - Create Dockerfile for FastAPI forensic application
    - Create docker-compose.yml with services: forensic_api, celery_worker_forensic, celery_beat, postgres, redis, chromadb
    - Write .dockerignore excluding tests and development files
    - Add volume mounts for persistent storage
    - _Requirements: 6.1_
  - [ ] 17.2 Write deployment scripts and documentation
    - Create scripts/init_db.sh for database initialization
    - Create scripts/run_tests.sh for CI/CD test execution
    - Write README.md with setup instructions, API documentation link (/docs), architecture diagram, future extensibility notes
    - Document directory structure: agents/forensic/ for current module, future agents/fraud_detection/, agents/credit_analysis/ for extensibility
    - Write docs/api_documentation.md with detailed API usage examples
    - Write docs/architecture.md with system design and data flow diagrams
    - Write docs/agent_details.md with implementation details for each agent
    - _Requirements: 6.1_

- [ ] 18. Integrate all components and write end-to-end tests
  - Write tests/e2e/forensic/test_complete_workflow.py simulating full API usage: search company → trigger forensic analysis → poll status → retrieve results → chat queries
  - Verify data flow through all forensic agents and storage in PostgreSQL
  - Test error recovery scenarios (API failures, database disconnections, task timeouts)
  - Validate OpenAPI schema accuracy against actual responses
  - Test concurrent forensic analysis jobs (10+ simultaneous requests)
  - Test WebSocket real-time status updates throughout pipeline
  - Verify PDF/Excel report generation and download
  - Test RAG-based Q&A with various query types and citation verification
  - _Requirements: All requirements_
```


## Key Files Location Summary

| Component | Location |
| :-- | :-- |
| **Spec Documents** | `.kiro/specs/project-iris-forensic/` |
| Requirements | `requirements.md` |
| Design | `design.md` |
| Tasks | `tasks.md` |
| **Forensic Agents** | `src/agents/forensic/` |
| Agent 1 (Ingestion) | `agent1_ingestion.py` |
| Agent 2 (Analysis) | `agent2_forensic_analysis.py` |
| Agent 3 (Risk) | `agent3_risk_scoring.py` |
| Agent 4 (Compliance) | `agent4_compliance.py` |
| Agent 5 (Reporting) | `agent5_reporting.py` |
| Agent 6 (Orchestrator) | `agent6_orchestrator.py` |
| Agent 7 (Q\&A) | `agent7_qa.py` |
| Agent 8 (Sentiment) | `agent8_sentiment.py` |
| Agent 9 (Benchmarking) | `agent9_peer_benchmarking.py` |
| Agent 10 (Regulatory) | `agent10_regulatory.py` |
| **API** | `src/api/` |
| Main App | `main.py` (Swagger at `/docs`) |
| Routes | `routes/forensic_routes.py` |
| Schemas | `schemas/forensic_analysis.py` |
| **Database** | `src/database/` |
| Connection Manager | `connection.py` |
| SQL Schema | `migrations/create_tables.sql` |
| **Tests** | `tests/` |
| Unit Tests | `unit/forensic/` |
| Integration Tests | `integration/forensic/` |
| API Tests | `api/forensic/` |
| E2E Tests | `e2e/forensic/` |

This structure is now complete with all three spec documents (requirements, design, tasks) properly organized under `.kiro/specs/project-iris-forensic/` and the entire forensic agent system under `src/agents/forensic/` for future extensibility!

