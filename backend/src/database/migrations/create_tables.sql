-- =============================================================================
-- Project IRIS - PostgreSQL Database Schema
-- Financial Forensics Analysis for Indian Public Companies
-- =============================================================================
-- Version: 1.0.0
-- Database: PostgreSQL 15+
-- =============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- =============================================================================
-- CORE TABLES
-- =============================================================================

-- Companies Table
CREATE TABLE companies (
    company_id VARCHAR(50) PRIMARY KEY,  -- FMP symbol (e.g., RELIANCE.NS)
    name VARCHAR(255) NOT NULL,
    symbol VARCHAR(50) NOT NULL,  -- Without suffix (e.g., RELIANCE)
    exchange VARCHAR(10) CHECK (exchange IN ('NSE', 'BSE', 'BOTH')),
    isin VARCHAR(20),
    sector VARCHAR(100),
    industry VARCHAR(150),
    market_cap NUMERIC(20, 2),
    fiscal_year_end DATE,
    currency VARCHAR(10) DEFAULT 'INR',
    website VARCHAR(255),
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_companies_symbol ON companies(symbol);
CREATE INDEX idx_companies_sector ON companies(sector);
CREATE INDEX idx_companies_market_cap ON companies(market_cap DESC);
CREATE INDEX idx_companies_name_trgm ON companies USING GIN (name gin_trgm_ops);

-- =============================================================================
-- FINANCIAL DATA TABLES
-- =============================================================================

-- Financial Statements
CREATE TABLE financial_statements (
    id SERIAL PRIMARY KEY,
    company_id VARCHAR(50) REFERENCES companies(company_id) ON DELETE CASCADE,
    period DATE NOT NULL,
    statement_type VARCHAR(30) CHECK (statement_type IN ('INCOME_STATEMENT', 'BALANCE_SHEET', 'CASH_FLOW')),
    fiscal_year INTEGER,
    period_type VARCHAR(10),  -- 'FY', 'Q1', 'Q2', 'Q3', 'Q4'
    currency VARCHAR(10) DEFAULT 'INR',
    data JSONB NOT NULL,  -- Normalized financial data
    source VARCHAR(50) DEFAULT 'FMP_API',
    filing_url TEXT,
    filing_date DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (company_id, period, statement_type)
);

CREATE INDEX idx_financial_statements_company_period ON financial_statements(company_id, period DESC);
CREATE INDEX idx_financial_statements_type ON financial_statements(statement_type);
CREATE INDEX idx_financial_statements_fiscal_year ON financial_statements(fiscal_year DESC);
CREATE INDEX idx_financial_statements_data ON financial_statements USING GIN (data jsonb_path_ops);

-- Disclosure Documents
CREATE TABLE disclosure_documents (
    id SERIAL PRIMARY KEY,
    company_id VARCHAR(50) REFERENCES companies(company_id) ON DELETE CASCADE,
    filing_type VARCHAR(50),  -- 'ANNUAL_REPORT', 'QUARTERLY_RESULTS', 'CORPORATE_ACTION', etc.
    filing_date DATE NOT NULL,
    section_type VARCHAR(50),  -- 'directors_report', 'md_and_a', 'audit_report', 'notes'
    full_text TEXT,
    source_url TEXT,
    source VARCHAR(50),  -- 'NSE_PORTAL', 'BSE_PORTAL', 'FMP_API'
    ocr_method VARCHAR(50),  -- 'OPENVINO_GPU', 'CPU_FALLBACK', 'N/A'
    ocr_accuracy NUMERIC(5, 2),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_disclosure_documents_company_filing ON disclosure_documents(company_id, filing_type, filing_date DESC);
CREATE INDEX idx_disclosure_documents_filing_date ON disclosure_documents(filing_date DESC);
CREATE INDEX idx_disclosure_documents_source ON disclosure_documents(source);

-- =============================================================================
-- ANALYSIS JOB MANAGEMENT
-- =============================================================================

-- Analysis Jobs
CREATE TABLE analysis_jobs (
    job_id VARCHAR(50) PRIMARY KEY,
    company_id VARCHAR(50) REFERENCES companies(company_id) ON DELETE CASCADE,
    job_type VARCHAR(20) DEFAULT 'FORENSIC' CHECK (job_type IN ('FORENSIC', 'FRAUD', 'CREDIT')),
    status VARCHAR(30) CHECK (status IN (
        'CREATED', 'INGESTING_DATA', 'ANALYZING', 'SCORING_RISK', 
        'BENCHMARKING', 'MONITORING', 'GENERATING_REPORTS', 
        'INDEXING', 'COMPLETED', 'FAILED'
    )),
    analysis_config JSONB NOT NULL,  -- Snapshot of YAML configs used
    data_sources JSONB,  -- ['FMP_API', 'NSE_PORTAL', 'BSE_PORTAL']
    fmp_calls_used INTEGER DEFAULT 0,
    error TEXT,
    error_details JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

CREATE INDEX idx_analysis_jobs_status ON analysis_jobs(status);
CREATE INDEX idx_analysis_jobs_company ON analysis_jobs(company_id);
CREATE INDEX idx_analysis_jobs_created ON analysis_jobs(created_at DESC);
CREATE INDEX idx_analysis_jobs_job_type ON analysis_jobs(job_type);

-- =============================================================================
-- FORENSIC ANALYSIS RESULTS
-- =============================================================================

-- Forensic Analysis Results
CREATE TABLE forensic_analysis (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(50) REFERENCES analysis_jobs(job_id) ON DELETE CASCADE,
    company_id VARCHAR(50) REFERENCES companies(company_id) ON DELETE CASCADE,
    analysis_type VARCHAR(30) NOT NULL,  -- 'BENFORD', 'Z_SCORE', 'M_SCORE', 'RATIO_ANALYSIS', 'VERTICAL', 'HORIZONTAL'
    results JSONB NOT NULL,
    anomalies JSONB,
    config_used JSONB,  -- Snapshot of YAML config for this analysis
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_forensic_analysis_job ON forensic_analysis(job_id);
CREATE INDEX idx_forensic_analysis_company ON forensic_analysis(company_id);
CREATE INDEX idx_forensic_analysis_type ON forensic_analysis(analysis_type);

-- Risk Scores
CREATE TABLE risk_scores (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(50) REFERENCES analysis_jobs(job_id) ON DELETE CASCADE,
    company_id VARCHAR(50) REFERENCES companies(company_id) ON DELETE CASCADE,
    composite_score NUMERIC(5, 2) CHECK (composite_score BETWEEN 0 AND 100),
    risk_level VARCHAR(20) CHECK (risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    breakdown JSONB NOT NULL,  -- Category scores: financial_health, earnings_quality, etc.
    weights_used JSONB,  -- YAML config weights snapshot
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_risk_scores_job ON risk_scores(job_id);
CREATE INDEX idx_risk_scores_company ON risk_scores(company_id);
CREATE INDEX idx_risk_scores_level ON risk_scores(risk_level);
CREATE INDEX idx_risk_scores_composite ON risk_scores(composite_score DESC);

-- Compliance Validation
CREATE TABLE compliance_validation (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(50) REFERENCES analysis_jobs(job_id) ON DELETE CASCADE,
    company_id VARCHAR(50) REFERENCES companies(company_id) ON DELETE CASCADE,
    regulation VARCHAR(50) NOT NULL,  -- 'IND_AS_1', 'SEBI_LODR_33', 'COMPANIES_ACT_143', etc.
    violation_type VARCHAR(100),
    severity VARCHAR(20) CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    description TEXT,
    evidence JSONB,
    rule_config JSONB,  -- YAML rule used
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_compliance_validation_job ON compliance_validation(job_id);
CREATE INDEX idx_compliance_validation_company ON compliance_validation(company_id);
CREATE INDEX idx_compliance_validation_regulation ON compliance_validation(regulation);
CREATE INDEX idx_compliance_validation_severity ON compliance_validation(severity);

-- =============================================================================
-- PEER BENCHMARKING
-- =============================================================================

-- Peer Benchmarks
CREATE TABLE peer_benchmarks (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(50) REFERENCES analysis_jobs(job_id) ON DELETE CASCADE,
    company_id VARCHAR(50) REFERENCES companies(company_id) ON DELETE CASCADE,
    peer_group JSONB NOT NULL,  -- Array of peer symbols
    ratio_name VARCHAR(50) NOT NULL,
    company_value NUMERIC(20, 4),
    peer_median NUMERIC(20, 4),
    peer_mean NUMERIC(20, 4),
    peer_p25 NUMERIC(20, 4),
    peer_p75 NUMERIC(20, 4),
    peer_stddev NUMERIC(20, 4),
    z_score NUMERIC(10, 4),
    percentile_rank NUMERIC(5, 2),
    is_outlier BOOLEAN,
    data_source VARCHAR(50) DEFAULT 'FMP_API',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_peer_benchmarks_job ON peer_benchmarks(job_id);
CREATE INDEX idx_peer_benchmarks_company_ratio ON peer_benchmarks(company_id, ratio_name);
CREATE INDEX idx_peer_benchmarks_outlier ON peer_benchmarks(is_outlier) WHERE is_outlier = true;

-- =============================================================================
-- MARKET SENTIMENT & TRENDS
-- =============================================================================

-- Google Trends Data
CREATE TABLE google_trends_data (
    id SERIAL PRIMARY KEY,
    company_id VARCHAR(50) REFERENCES companies(company_id) ON DELETE CASCADE,
    keyword VARCHAR(100) NOT NULL,
    timeframe VARCHAR(50),
    geo VARCHAR(10) DEFAULT 'IN',
    interest_over_time JSONB,
    interest_by_region JSONB,
    related_queries JSONB,
    scraped_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_google_trends_company_keyword ON google_trends_data(company_id, keyword);
CREATE INDEX idx_google_trends_scraped ON google_trends_data(scraped_at DESC);

-- Sentiment Analysis Results
CREATE TABLE sentiment_analysis (
    id SERIAL PRIMARY KEY,
    company_id VARCHAR(50) REFERENCES companies(company_id) ON DELETE CASCADE,
    source_type VARCHAR(30),  -- 'NEWS_ARTICLE', 'SOCIAL_MEDIA', 'ANALYST_REPORT'
    source_url TEXT,
    publish_date DATE,
    text_snippet TEXT,
    sentiment VARCHAR(20) CHECK (sentiment IN ('POSITIVE', 'NEGATIVE', 'NEUTRAL')),
    confidence NUMERIC(5, 4),
    aggregate_score NUMERIC(6, 2),  -- -100 to +100
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_sentiment_analysis_company ON sentiment_analysis(company_id);
CREATE INDEX idx_sentiment_analysis_sentiment ON sentiment_analysis(sentiment);
CREATE INDEX idx_sentiment_analysis_publish ON sentiment_analysis(publish_date DESC);

-- Trends Anomalies
CREATE TABLE trends_anomalies (
    id SERIAL PRIMARY KEY,
    company_id VARCHAR(50) REFERENCES companies(company_id) ON DELETE CASCADE,
    anomaly_type VARCHAR(50) NOT NULL,  -- 'REVENUE_SEARCH_DIVERGENCE', 'NEGATIVE_SEARCH_SPIKE', etc.
    severity VARCHAR(20) CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    description TEXT,
    evidence JSONB,
    detected_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_trends_anomalies_company ON trends_anomalies(company_id);
CREATE INDEX idx_trends_anomalies_type ON trends_anomalies(anomaly_type);
CREATE INDEX idx_trends_anomalies_severity ON trends_anomalies(severity);

-- =============================================================================
-- REGULATORY MONITORING
-- =============================================================================

-- SEBI Enforcement Actions
CREATE TABLE sebi_enforcement_actions (
    id SERIAL PRIMARY KEY,
    company_id VARCHAR(50) REFERENCES companies(company_id) ON DELETE CASCADE,
    action_date DATE NOT NULL,
    order_type VARCHAR(50),  -- 'SHOW_CAUSE_NOTICE', 'ADJUDICATION_ORDER', 'DEBARMENT_ORDER'
    entity_name VARCHAR(255),
    description TEXT,
    order_url TEXT,
    penalty_amount NUMERIC(15, 2),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_sebi_enforcement_company_date ON sebi_enforcement_actions(company_id, action_date DESC);
CREATE INDEX idx_sebi_enforcement_order_type ON sebi_enforcement_actions(order_type);

-- Compliance Deadlines
CREATE TABLE compliance_deadlines (
    id SERIAL PRIMARY KEY,
    company_id VARCHAR(50) REFERENCES companies(company_id) ON DELETE CASCADE,
    filing_type VARCHAR(50) NOT NULL,
    deadline DATE NOT NULL,
    status VARCHAR(20) CHECK (status IN ('UPCOMING', 'URGENT', 'OVERDUE', 'COMPLETED')),
    regulation VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_compliance_deadlines_company_status ON compliance_deadlines(company_id, status, deadline);
CREATE INDEX idx_compliance_deadlines_deadline ON compliance_deadlines(deadline);

-- Regulatory Risk Scores
CREATE TABLE regulatory_risk_scores (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(50) REFERENCES analysis_jobs(job_id) ON DELETE CASCADE,
    company_id VARCHAR(50) REFERENCES companies(company_id) ON DELETE CASCADE,
    total_score INTEGER CHECK (total_score BETWEEN 0 AND 100),
    risk_level VARCHAR(20) CHECK (risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    enforcement_count INTEGER,
    overdue_count INTEGER,
    breakdown JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_regulatory_risk_scores_job ON regulatory_risk_scores(job_id);
CREATE INDEX idx_regulatory_risk_scores_company ON regulatory_risk_scores(company_id);
CREATE INDEX idx_regulatory_risk_scores_level ON regulatory_risk_scores(risk_level);

-- =============================================================================
-- REPORTING
-- =============================================================================

-- Reports
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(50) REFERENCES analysis_jobs(job_id) ON DELETE CASCADE,
    company_id VARCHAR(50) REFERENCES companies(company_id) ON DELETE CASCADE,
    report_type VARCHAR(50) CHECK (report_type IN ('EXECUTIVE_SUMMARY', 'DETAILED_FORENSIC', 'COMPLIANCE', 'PEER_BENCHMARK')),
    format VARCHAR(10) CHECK (format IN ('JSON', 'PDF', 'EXCEL')),
    content BYTEA,  -- For PDF/Excel binary data
    json_data JSONB,  -- For JSON format
    data_sources JSONB,  -- ['FMP_API', 'NSE_PORTAL', 'GEMINI']
    file_size_bytes INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_reports_job_type ON reports(job_id, report_type);
CREATE INDEX idx_reports_company ON reports(company_id);
CREATE INDEX idx_reports_format ON reports(format);

-- =============================================================================
-- Q&A SYSTEM (RAG)
-- =============================================================================

-- Chat Sessions
CREATE TABLE chat_sessions (
    session_id VARCHAR(50) PRIMARY KEY,
    company_id VARCHAR(50) REFERENCES companies(company_id) ON DELETE CASCADE,
    user_id VARCHAR(100),
    agent_type VARCHAR(20) DEFAULT 'FORENSIC',
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_chat_sessions_company_user ON chat_sessions(company_id, user_id);
CREATE INDEX idx_chat_sessions_created ON chat_sessions(created_at DESC);

-- Chat Messages
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(50) REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
    role VARCHAR(20) CHECK (role IN ('user', 'assistant')),
    message TEXT NOT NULL,
    citations JSONB,
    confidence NUMERIC(5, 4),
    follow_up_questions JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_chat_messages_session ON chat_messages(session_id, created_at);
CREATE INDEX idx_chat_messages_role ON chat_messages(role);

-- =============================================================================
-- PERFORMANCE MONITORING
-- =============================================================================

-- Hardware Metrics (Intel Optimization Tracking)
CREATE TABLE hardware_metrics (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(50) REFERENCES analysis_jobs(job_id) ON DELETE CASCADE,
    agent_name VARCHAR(50) NOT NULL,
    operation VARCHAR(100) NOT NULL,  -- 'ocr_extraction', 'sentiment_analysis', 'embedding_generation'
    hardware_used VARCHAR(50) NOT NULL,  -- 'openvino_gpu', 'intel_pytorch_bf16', 'cpu_fallback'
    execution_time_ms INTEGER NOT NULL,
    speedup_factor NUMERIC(6, 2),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_hardware_metrics_job ON hardware_metrics(job_id);
CREATE INDEX idx_hardware_metrics_hardware ON hardware_metrics(hardware_used);
CREATE INDEX idx_hardware_metrics_operation ON hardware_metrics(operation);

-- =============================================================================
-- CONFIGURATION AUDIT
-- =============================================================================

-- Configuration Audit Log
CREATE TABLE config_audit_log (
    id SERIAL PRIMARY KEY,
    agent_name VARCHAR(50) NOT NULL,
    config_file VARCHAR(100) NOT NULL,
    changed_by VARCHAR(100),
    changes JSONB NOT NULL,  -- {"field": {"old": value, "new": value}}
    change_reason TEXT,
    applied_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_config_audit_agent_time ON config_audit_log(agent_name, applied_at DESC);
CREATE INDEX idx_config_audit_changed_by ON config_audit_log(changed_by);

-- =============================================================================
-- TRIGGERS FOR AUTO-UPDATE timestamps
-- =============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_financial_statements_updated_at BEFORE UPDATE ON financial_statements
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_analysis_jobs_updated_at BEFORE UPDATE ON analysis_jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_compliance_deadlines_updated_at BEFORE UPDATE ON compliance_deadlines
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- DEFAULT DATA / SEED DATA
-- =============================================================================

-- Insert sample test company (optional - for development)
-- INSERT INTO companies (company_id, name, symbol, exchange, sector, market_cap, currency)
-- VALUES ('RELIANCE.NS', 'Reliance Industries Limited', 'RELIANCE', 'NSE', 'Energy', 1500000000000, 'INR');

-- =============================================================================
-- END OF SCHEMA
-- =============================================================================
