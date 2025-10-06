<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Requirements Document - Project IRIS Forensic Analysis (Updated with FMP API)

## Introduction

Project IRIS is a financial forensics platform that analyzes Indian public companies for fraud detection, risk assessment, and regulatory compliance. The system ingests financial data from **Financial Modeling Prep (FMP) API** with NSE/BSE backup sources, applies forensic analysis techniques (Benford's Law, Z-Score, M-Score), validates compliance with Indian regulations (Ind AS, SEBI LODR, Companies Act 2013), and provides conversational intelligence through a RAG-based Q\&A system powered by Gemini 2.0 Flash.

The platform implements a microservices-inspired agent-based architecture where 10 specialized agents orchestrate forensic workflows, with deployment optimized for Intel Tiber Developer Cloud infrastructure.

***

## Requirements

### Requirement 1: Data Ingestion (FMP API Primary Source)

**User Story:** As a forensic analyst, I want to automatically fetch financial data from FMP API with NSE/BSE backup sources, so that I can analyze Indian companies with comprehensive 30-year historical data.

#### Acceptance Criteria

1. WHEN a user provides a company identifier (NSE symbol like "RELIANCE.NS" or BSE symbol like "RELIANCE.BO") THEN the system SHALL search FMP API and return matching companies with metadata including sector, industry, market cap, and exchange
2. WHEN financial data is requested for a date range THEN the system SHALL fetch income statements, balance sheets, and cash flow statements from FMP API with automatic period filtering (annual or quarterly)
3. WHEN FMP API returns statements THEN the system SHALL normalize data to internal schema mapping FMP fields (revenue, costOfRevenue, totalAssets, totalLiabilities) to standardized field names
4. IF balance sheet data is retrieved THEN the system SHALL validate that Assets = Liabilities + Equity within ₹1,000 tolerance using normalized field values
5. WHEN FMP API rate limit is exceeded (250 calls/day on free tier) THEN the system SHALL implement exponential backoff (2s, 4s, 8s) with maximum 3 retry attempts and log rate limit event to monitoring
6. IF FMP API returns incomplete data or is unavailable THEN the system SHALL fall back to NSE/BSE portal scraping for Indian-specific disclosures (corporate announcements, shareholding patterns, insider trades)
7. WHEN NSE/BSE corporate filings are unavailable via API THEN the system SHALL scrape portal pages and extract PDF documents using BeautifulSoup
8. WHEN PDF annual reports are downloaded THEN the system SHALL extract text using Intel OpenVINO OCR with >80% accuracy for printed financial statements
9. IF FMP API is completely unavailable THEN the system SHALL use cached data if available within 24 hours and flag response as "stale_data" with last_updated timestamp
10. WHEN FMP returns pre-calculated financial ratios THEN the system SHALL store them for validation against internally calculated ratios (acceptance tolerance ±5%)

***

### Requirement 2: Forensic Analysis

**User Story:** As a fraud investigator, I want automated forensic analysis of financial statements, so that I can identify manipulation patterns quickly.

#### Acceptance Criteria

1. WHEN financial statements are ingested THEN the system SHALL perform vertical analysis calculating each line item as percentage of base figure (total assets for balance sheet, revenue for income statement)
2. WHEN multiple periods of data exist THEN the system SHALL calculate horizontal analysis showing Year-over-Year (YoY) and Quarter-over-Quarter (QoQ) growth rates
3. WHEN financial data is available THEN the system SHALL calculate liquidity ratios (current ratio, quick ratio, cash ratio), profitability ratios (ROE, ROA, net margin, gross margin), leverage ratios (debt-to-equity, interest coverage), and efficiency ratios (asset turnover, receivables turnover)
4. WHEN FMP provides pre-calculated ratios THEN the system SHALL compare with internally calculated ratios and flag discrepancies exceeding 5% for manual review
5. WHEN revenue, expense, or asset line items are provided THEN the system SHALL apply Benford's Law test extracting first digits and performing chi-square test with critical value 15.507 at 95% confidence
6. WHEN balance sheet and income statement data are complete THEN the system SHALL calculate Altman Z-Score using formula Z = 1.2A + 1.4B + 3.3C + 0.6D + 1.0E and classify as SAFE (>2.99), GREY (1.81-2.99), or DISTRESS (<1.81)
7. WHEN current period and prior period financials exist THEN the system SHALL calculate Beneish M-Score using 8-variable model (DSRI, GMI, AQI, SGI, DEPI, SGAI, LVGI, TATA) and flag manipulation risk if M-Score > -1.78
8. WHEN forensic analysis is complete THEN the system SHALL detect anomalies including revenue decline >30% (HIGH severity), profit-cash divergence where PAT grows >20% while cash declines >10% (CRITICAL severity), and receivables growth delta >20% (MEDIUM severity)
9. IF multiple anomalies are detected THEN the system SHALL rank by severity (CRITICAL > HIGH > MEDIUM > LOW) and store evidence in JSONB format with source line items and FMP data source reference

***

### Requirement 3: Risk Scoring

**User Story:** As a risk manager, I want a composite risk score across multiple dimensions, so that I can prioritize companies for deeper investigation.

#### Acceptance Criteria

1. WHEN forensic analysis completes THEN the system SHALL calculate Financial Health score (0-100) based on Z-Score classification, current ratio health, and debt-to-equity ratio
2. WHEN M-Score and cash flow quality metrics are available THEN the system SHALL calculate Earnings Quality score (0-100) penalizing M-Score > -1.78 by 50 points and profit-cash divergence by 30 points
3. WHEN disclosure filing data exists THEN the system SHALL calculate Disclosure Quality score (0-100) based on filing timeliness (<45 days for quarterly, <21 days for shareholding) and audit report qualifications
4. WHEN all 6 category scores are computed THEN the system SHALL calculate composite risk score using weighted formula: (Financial Health × 0.20) + (Earnings Quality × 0.20) + (Disclosure Quality × 0.20) + (Market Signals × 0.15) + (Forensic Flags × 0.10) + (Market Sentiment × 0.15)
5. WHEN composite score is calculated THEN the system SHALL classify risk as LOW (80-100), MEDIUM (60-79), HIGH (40-59), or CRITICAL (0-39)
6. IF risk level is CRITICAL or HIGH THEN the system SHALL include detailed breakdown showing which categories contributed most to the score with evidence from FMP data and forensic analysis

***

### Requirement 4: Compliance Validation

**User Story:** As a compliance officer, I want automated validation against Indian regulations, so that I can identify violations without manual checklist review.

#### Acceptance Criteria

1. WHEN balance sheet is processed THEN the system SHALL validate Ind AS 1 requirement that Assets = Liabilities + Equity within tolerance using FMP-normalized data
2. WHEN financial statements are complete THEN the system SHALL check Ind AS 7 for cash flow statement presence and Ind AS 24 for related party transaction disclosures
3. WHEN quarterly results are filed THEN the system SHALL validate SEBI LODR Regulation 33 requiring filing within 45 days of quarter end by comparing FMP filing dates with quarter end dates
4. WHEN shareholding pattern is submitted THEN the system SHALL check SEBI LODR Regulation 31 requiring filing within 21 days
5. WHEN related party transactions exceed 10% of annual revenue THEN the system SHALL verify SEBI LODR Regulation 23 requirement for audit committee approval
6. WHEN audit report text is extracted THEN the system SHALL scan for qualification keywords ("subject to", "except for", "qualified opinion") and flag Companies Act Section 143 violations as CRITICAL severity
7. IF violations are detected THEN the system SHALL store regulation reference, violation description, severity level, and data source (FMP or NSE/BSE) in compliance_validation table

***

### Requirement 5: Reporting and Export

**User Story:** As an audit team lead, I want professional reports with AI-generated summaries, so that I can present findings to stakeholders.

#### Acceptance Criteria

1. WHEN forensic analysis completes THEN the system SHALL generate executive summary using Gemini 2.0 Flash API with max 150 words covering overall assessment and top 3 findings
2. WHEN all analysis results are available THEN the system SHALL compile detailed forensic report with ratio tables, Z-Score breakdown, M-Score components, and anomaly explanations
3. WHEN report generation is requested THEN the system SHALL format data as JSON for API consumers including KPI cards (risk score, Z-score, anomaly count), trend charts (5-year revenue/profit/cash flow using FMP historical data), and risk heatmaps
4. IF report export format is PDF THEN the system SHALL use ReportLab to generate audit-ready document with tables, charts, company branding, and data source attribution (FMP API)
5. IF report export format is Excel THEN the system SHALL use xlsxwriter to create workbook with separate sheets for ratios, anomalies, compliance, peer benchmarks, and raw FMP data
6. WHEN multiple reports exist for same company THEN the system SHALL store in reports table with creation timestamp, report_type classification, and data_sources array
7. IF Gemini API fails THEN the system SHALL generate template-based summary using predefined risk level descriptions

***

### Requirement 6: Orchestration and Job Management

**User Story:** As a system administrator, I want reliable pipeline execution with error recovery, so that analysis jobs complete successfully even when individual components fail.

#### Acceptance Criteria

1. WHEN analysis is triggered via API THEN the system SHALL create job record in analysis_jobs table with status CREATED, unique job_id, FMP symbol, and data_sources array, returning 202 Accepted immediately
2. WHEN job execution begins THEN the system SHALL coordinate agents in sequence: Agent1 (FMP Ingestion) → Agent2 (Forensic) → [Agent3 (Risk) || Agent4 (Compliance)] parallel → Agent9 (Peer) → Agent10 (Regulatory) → Agent5 (Reporting) → Agent7 (Q\&A Indexing)
3. WHEN each agent completes THEN the system SHALL update job status to corresponding state (INGESTING_DATA, ANALYZING, SCORING_RISK, BENCHMARKING, MONITORING, GENERATING_REPORTS, INDEXING, COMPLETED)
4. IF any agent encounters error (including FMP rate limit) THEN the system SHALL implement retry logic with exponential backoff (2s, 4s, 8s) for maximum 3 attempts before marking job as FAILED
5. WHEN job status changes THEN the system SHALL emit WebSocket message to subscribed clients with status, progress percentage, current agent name, and API call count remaining (for FMP rate limiting)
6. WHEN user requests job results THEN the system SHALL return status, risk score, reports, anomalies, and data_sources metadata if status is COMPLETED, or error details with failed_agent if status is FAILED

***

### Requirement 7: Interactive Q\&A System

**User Story:** As a financial analyst, I want to ask natural language questions about analyzed companies, so that I can explore findings conversationally without writing SQL queries.

#### Acceptance Criteria

1. WHEN forensic analysis completes THEN the system SHALL index financial statements (from FMP), disclosure documents (from NSE/BSE), and analysis reports into ChromaDB collection named forensic_company_{company_id}
2. WHEN documents are indexed THEN the system SHALL chunk text into maximum 512 tokens per chunk and generate 768-dimensional embeddings using FinLang/finance-embeddings-investopedia model
3. WHEN user submits natural language query THEN the system SHALL perform semantic search in ChromaDB retrieving top 5 most relevant document chunks by cosine similarity
4. WHEN context is retrieved THEN the system SHALL construct RAG prompt with context documents (including FMP data source references) and user query, calling Gemini 2.0 Flash for response generation
5. WHEN Gemini generates response THEN the system SHALL extract inline citations matching pattern [source_type:source_id] and validate all citations reference actual source documents (FMP, NSE, BSE, or internal analysis)
6. IF user asks follow-up question THEN the system SHALL generate 3 relevant follow-up questions using Gemini based on current conversation context
7. WHEN conversation concludes THEN the system SHALL store all messages in chat_messages table with session_id, role (user/assistant), message text, citations array, and data_sources
8. IF confidence score (based on retrieval similarity) is below 0.5 THEN the system SHALL include disclaimer: "Low confidence answer - please verify from source documents"

***

### Requirement 8: Market Sentiment and Trends

**User Story:** As a market researcher, I want to detect divergences between financial performance and public sentiment, so that I can identify potential reputation risks or stock manipulation.

#### Acceptance Criteria

1. WHEN company analysis is scheduled THEN the system SHALL scrape Google Trends data using pytrends library with keyword variations (company name, "{company} fraud", "{company} scam", "{company} stock") for timeframe 'today 5-y'
2. WHEN trends data is retrieved THEN the system SHALL extract interest_over_time, interest_by_region (Indian states), and related_queries, storing in google_trends_data table
3. IF revenue growth exceeds 15% (from FMP historical data) but search interest declines more than 20% THEN the system SHALL flag REVENUE_SEARCH_DIVERGENCE anomaly as HIGH severity
4. IF negative keyword searches ("{company} fraud") exceed volume 30 THEN the system SHALL flag NEGATIVE_SEARCH_SPIKE as CRITICAL severity
5. WHEN news articles are scraped from Economic Times, Business Standard, MoneyControl THEN the system SHALL extract article text, publish date, and source URL for last 30 days
6. WHEN articles are collected THEN the system SHALL apply FinBERT sentiment classification to each article using Intel PyTorch optimization, calculating aggregate sentiment score using weighted formula: (news_confidence × 3 + tweets_confidence × 1 + reddit_confidence × 2) / total_sources × 100
7. IF state-level search interest is 30 percentage points below reported revenue contribution for that state THEN the system SHALL flag GEOGRAPHIC_MISMATCH anomaly indicating possible revenue inflation

***

### Requirement 9: Peer Benchmarking

**User Story:** As a comparative analyst, I want to benchmark company ratios against industry peers, so that I can identify outliers indicating possible manipulation or competitive advantage.

#### Acceptance Criteria

1. WHEN peer analysis is requested THEN the system SHALL identify peer group by querying FMP API for companies with same sector classification (from company profile) and market cap between 0.5x-2x of target company
2. WHEN peer group is identified THEN the system SHALL fetch financial ratios for all peers from FMP API (using ratios endpoint) and calculate median, 25th percentile, 75th percentile, mean, and standard deviation for each ratio
3. WHEN peer statistics are computed THEN the system SHALL calculate z-score for target company using formula: (company_value - peer_mean) / peer_stddev
4. WHEN z-scores are calculated THEN the system SHALL compute percentile rank (0-100th) showing target company's position relative to peers using FMP ratio data
5. IF absolute z-score exceeds 2.0 for any ratio THEN the system SHALL flag as outlier and store in peer_benchmarks table with is_outlier=TRUE and peer_data_source='FMP'
6. IF company revenue grows more than 15% while peer median declines more than 5% (using FMP growth data) THEN the system SHALL flag GROWTH_DIVERGENCE anomaly
7. IF company revenue declines more than 10% while peer median grows more than 10% THEN the system SHALL flag UNDERPERFORMANCE anomaly

***

### Requirement 10: Regulatory Monitoring

**User Story:** As a regulatory compliance analyst, I want automated monitoring of SEBI enforcement actions, so that I can track regulatory risk for analyzed companies.

#### Acceptance Criteria

1. WHEN company is analyzed THEN the system SHALL scrape SEBI enforcement database using BeautifulSoup for company name matches in last 3 years
2. WHEN SEBI page is parsed THEN the system SHALL extract action date, order type (Show Cause Notice, Adjudication Order, Debarment Order), entity name, description, and order URL from HTML tables
3. WHEN fiscal year end is known (from FMP company profile) THEN the system SHALL calculate compliance deadlines: quarterly results (fiscal quarter end + 45 days), annual report (fiscal year end + 6 months before AGM), shareholding pattern (quarter end + 21 days)
4. WHEN current date is within 7 days of deadline THEN the system SHALL flag deadline status as URGENT
5. WHEN current date passes deadline without filing (verified against FMP filing dates) THEN the system SHALL flag deadline status as OVERDUE
6. WHEN enforcement actions are counted THEN the system SHALL calculate regulatory risk score using formula: (Show Cause Notices × 15) + (Adjudication Orders × 25) + (Debarment Orders × 40) + (Overdue Filings × 20), capped at 100
7. IF regulatory risk score exceeds 60 THEN the system SHALL classify as CRITICAL regulatory risk

***

### Requirement 11: Intel Hardware Optimization

**User Story:** As a DevOps engineer, I want to leverage Intel Tiber Developer Cloud hardware acceleration, so that the system achieves faster processing and lower operational costs.

#### Acceptance Criteria

1. WHEN OCR processing is required for PDF documents (from NSE/BSE) THEN the system SHALL use Intel OpenVINO Runtime with optimized text detection models compiled for Intel CPU/GPU
2. WHEN OpenVINO is initialized THEN the system SHALL compile models for target device (CPU, GPU, or AUTO) and utilize Intel Gaussian \& Neural Accelerator (GNA) if available
3. IF Intel GPU is available THEN the system SHALL prioritize GPU execution for OCR inference achieving minimum 6x speedup compared to CPU-only processing
4. WHEN FinBERT sentiment analysis is executed THEN the system SHALL use Intel Extension for PyTorch (ipex.optimize()) to enable automatic mixed precision (BF16) inference
5. WHEN PyTorch models are optimized THEN the system SHALL achieve minimum 2x speedup for batch sentiment analysis compared to standard PyTorch inference
6. IF Intel Gaudi AI accelerators are available THEN the system SHALL support model fine-tuning on Gaudi with Habana frameworks for future fraud detection model training
7. WHEN system is deployed on Intel Tiber Developer Cloud THEN the system SHALL expose Prometheus metrics tracking inference latency (openvino_ocr_latency_seconds, pytorch_sentiment_latency_seconds, fmp_api_call_duration_seconds) for hardware utilization monitoring
8. IF Intel hardware optimizations fail to initialize THEN the system SHALL gracefully fallback to standard CPU processing with warning log but SHALL NOT fail job execution

***

### Requirement 12: Configuration-Driven Agent Architecture

**User Story:** As a data scientist, I want to tune forensic parameters without code changes, so that I can experiment with thresholds and rules quickly.

#### Acceptance Criteria

1. WHEN each agent is initialized THEN the system SHALL load configuration from YAML file located at agents/forensic/config/{agent_name}.yaml including FMP API settings (rate limits, endpoints, symbol suffixes)
2. WHEN YAML configuration is loaded THEN the system SHALL validate schema using Pydantic models and raise ValidationError with specific field errors if configuration is malformed
3. IF environment variable ENVIRONMENT is set to 'dev', 'staging', or 'prod' THEN the system SHALL merge environment-specific overrides from {agent_name}.{env}.yaml with base configuration (e.g., different FMP API keys per environment)
4. WHEN YAML contains environment variable placeholders in format \${ENV_VAR_NAME} THEN the system SHALL replace with actual environment variable values at load time (e.g., \${FMP_API_KEY})
5. WHEN forensic thresholds are changed in YAML (e.g., z_score.safe: 3.5) THEN the system SHALL apply new thresholds without requiring code redeployment or agent class modification
6. WHEN anomaly detection rules are added to YAML THEN the system SHALL automatically detect and evaluate new rules using configured conditions and thresholds
7. IF configuration changes between job executions THEN the system SHALL store applied configuration snapshot (including FMP API version and rate limits used) in JSONB column (analysis_config) in analysis_jobs table for audit trail
8. WHEN domain expert modifies YAML configuration THEN the system SHALL validate on next agent initialization and log clear error messages if validation fails, preventing silent failures

***

## Non-Functional Requirements

### Performance

- FMP API calls SHALL complete within 3 seconds per request at 95th percentile
- OCR processing SHALL complete within 5 seconds per document page on Intel GPU
- Full forensic analysis pipeline SHALL complete within 3 minutes for standard company (8 quarters of data from FMP)
- API response time (excluding background job execution) SHALL be under 200ms for 95th percentile
- System SHALL support minimum 10 concurrent analysis jobs without exceeding FMP free tier rate limits (250 calls/day)


### Scalability

- System SHALL scale horizontally by adding Celery workers
- ChromaDB vector database SHALL support minimum 1000 companies with 100MB documents each
- PostgreSQL SHALL handle minimum 1 million financial statement records from FMP and NSE/BSE
- System SHALL handle FMP API pagination for companies with >10 years of historical data


### Security

- FMP API keys SHALL be stored in environment variables, never in code or configuration files
- PostgreSQL connections SHALL use SSL/TLS encryption
- API endpoints SHALL implement rate limiting (100 requests/minute per IP)
- FMP API calls SHALL use HTTPS with certificate validation


### Reliability

- System SHALL achieve 99.5% uptime for API layer
- Database backups SHALL be automated daily with 30-day retention
- Failed jobs SHALL be retryable without data corruption
- System SHALL cache FMP responses for 24 hours to handle API outages gracefully


### Maintainability

- All agents SHALL have minimum 80% code coverage with unit tests
- Configuration changes SHALL not require code deployment
- Logging SHALL use structured JSON format compatible with ELK/Loki aggregation
- FMP API version and schema changes SHALL be documented in changelog


### Compliance

- System SHALL log all data access with user_id, timestamp, accessed company_id, and data_source (FMP/NSE/BSE) for audit
- Financial data SHALL be retained for minimum 7 years per Indian regulations
- System SHALL support data deletion requests per DPDPA (Digital Personal Data Protection Act)
- FMP API usage SHALL comply with Financial Modeling Prep Terms of Service

***

## Data Sources and API Integration

### Primary Data Source: Financial Modeling Prep (FMP) API

**Coverage:**

- Indian stocks: NSE (suffix .NS), BSE (suffix .BO)
- 30 years of historical financial data (Premium plan)
- Pre-calculated ratios, growth metrics, key metrics
- SEC filings links (limited for Indian companies)

**Endpoints Used:**

- `/search` - Company search
- `/profile/{symbol}` - Company metadata
- `/income-statement/{symbol}` - P\&L statements
- `/balance-sheet-statement/{symbol}` - Balance sheets
- `/cash-flow-statement/{symbol}` - Cash flows
- `/ratios/{symbol}` - Pre-calculated ratios
- `/key-metrics/{symbol}` - Market metrics
- `/financial-growth/{symbol}` - Growth rates
- `/historical-price-full/{symbol}` - Price history

**Rate Limits:**

- Free tier: 250 calls/day
- Starter: 300 calls/minute
- Premium: 750 calls/minute


### Backup Data Sources: NSE/BSE Portals

**Coverage (Indian-specific):**

- Corporate announcements
- Shareholding patterns
- Insider trading data
- Board meeting outcomes
- Annual reports (PDF format)

**Usage:**

- Fallback when FMP lacks Indian regulatory data
- OCR processing for PDF annual reports
- Web scraping with BeautifulSoup + Selenium

***

## Out of Scope

The following are explicitly NOT included in this version:

- Real-time stock price alerts and trading signals
- Mobile application development
- Multi-language support (English only)
- Integration with ERP systems (SAP, Oracle)
- Automated report distribution via email/Slack
- User authentication and role-based access control (to be added in v2.0)
- Blockchain-based audit trail
- Integration with paid global financial data providers (Bloomberg Terminal, Refinitiv Eikon, FactSet)
- Options/derivatives analysis
- Cryptocurrency financial analysis
- International GAAP/IFRS compliance validation (India-specific only)

***

## Summary of Key Changes

✅ **FMP API as primary data source** for financial statements
✅ **NSE/BSE as backup** for Indian regulatory data
✅ **30-year historical data** from FMP Premium plan
✅ **Pre-calculated ratios** from FMP for validation
✅ **Rate limit handling** (250 calls/day free tier)
✅ **Symbol conventions** (.NS for NSE, .BO for BSE)
✅ **Data source tracking** in all stored records
✅ **FMP-specific endpoints** documented
✅ **Cache strategy** (24 hours) for API resilience
✅ **Configuration management** for FMP API keys per environment

This updated requirements document ensures FMP API is the backbone of financial data ingestion while maintaining NSE/BSE scrapers for Indian-specific regulatory compliance data!

