-- PostgreSQL Schema for Real-time News Monitoring
-- Created: 2026-01-22

-- Drop existing tables if recreating
DROP TABLE IF EXISTS sentiment_alerts CASCADE;
DROP TABLE IF EXISTS news_sentiment CASCADE;
DROP TABLE IF EXISTS news_articles CASCADE;

-- News Articles Table
CREATE TABLE news_articles (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    source VARCHAR(50) NOT NULL, -- 'economictimes', 'moneycontrol', 'livemint'
    published_date TIMESTAMP,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    company VARCHAR(100), -- Optional: extracted company name
    sector VARCHAR(50),   -- Optional: sector classification
    
    -- Indexes for faster queries
    CONSTRAINT unique_article UNIQUE(url)
);

-- Sentiment Analysis Results Table
CREATE TABLE news_sentiment (
    id SERIAL PRIMARY KEY,
    article_id INTEGER NOT NULL REFERENCES news_articles(id) ON DELETE CASCADE,
    
    -- Sentiment results
    sentiment VARCHAR(20) NOT NULL, -- 'positive', 'negative', 'neutral'
    confidence FLOAT NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    
    -- FinBERT scores
    positive_score FLOAT,
    negative_score FLOAT,
    neutral_score FLOAT,
    
    -- Metadata
    model_version VARCHAR(50) DEFAULT 'ProsusAI/finbert',
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_article_sentiment UNIQUE(article_id)
);

-- Sentiment Alerts Table
CREATE TABLE sentiment_alerts (
    id SERIAL PRIMARY KEY,
    article_id INTEGER NOT NULL REFERENCES news_articles(id) ON DELETE CASCADE,
    
    -- Alert details
    alert_type VARCHAR(50) NOT NULL, -- 'major_negative', 'major_positive', 'high_volatility'
    severity VARCHAR(20) NOT NULL, -- 'low', 'medium', 'high', 'critical'
    message TEXT NOT NULL,
    
    -- Metadata
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_at TIMESTAMP,
    acknowledged_by VARCHAR(100)
);

-- Indexes for better query performance
CREATE INDEX idx_news_source ON news_articles(source);
CREATE INDEX idx_news_published ON news_articles(published_date DESC);
CREATE INDEX idx_news_scraped ON news_articles(scraped_at DESC);
CREATE INDEX idx_news_company ON news_articles(company);

CREATE INDEX idx_sentiment_article ON news_sentiment(article_id);
CREATE INDEX idx_sentiment_type ON news_sentiment(sentiment);
CREATE INDEX idx_sentiment_analyzed ON news_sentiment(analyzed_at DESC);

CREATE INDEX idx_alerts_triggered ON sentiment_alerts(triggered_at DESC);
CREATE INDEX idx_alerts_unack ON sentiment_alerts(acknowledged) WHERE acknowledged = FALSE;

-- View: Latest News with Sentiment
CREATE VIEW latest_news_with_sentiment AS
SELECT 
    na.id,
    na.title,
    na.content,
    na.url,
    na.source,
    na.company,
    na.published_date,
    na.scraped_at,
    ns.sentiment,
    ns.confidence,
    ns.positive_score,
    ns.negative_score,
    ns.neutral_score
FROM news_articles na
LEFT JOIN news_sentiment ns ON na.id = ns.article_id
ORDER BY na.scraped_at DESC;

-- View: Recent Alerts
CREATE VIEW unacknowledged_alerts AS
SELECT 
    sa.id,
    sa.alert_type,
    sa.severity,
    sa.message,
    sa.triggered_at,
    na.title AS article_title,
    na.source,
    ns.sentiment,
    ns.confidence
FROM sentiment_alerts sa
JOIN news_articles na ON sa.article_id = na.id
LEFT JOIN news_sentiment ns ON na.id = ns.article_id
WHERE sa.acknowledged = FALSE
ORDER BY sa.triggered_at DESC;

-- Function: Get sentiment trend for a company
CREATE OR REPLACE FUNCTION get_company_sentiment_trend(
    company_name VARCHAR(100),
    days_back INTEGER DEFAULT 7
)
RETURNS TABLE (
    date DATE,
    avg_sentiment_score FLOAT,
    article_count BIGINT,
    positive_count BIGINT,
    negative_count BIGINT,
    neutral_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        DATE(na.published_date) as date,
        AVG(
            CASE 
                WHEN ns.sentiment = 'positive' THEN 1.0
                WHEN ns.sentiment = 'negative' THEN -1.0
                ELSE 0.0
            END
        ) as avg_sentiment_score,
        COUNT(*) as article_count,
        SUM(CASE WHEN ns.sentiment = 'positive' THEN 1 ELSE 0 END) as positive_count,
        SUM(CASE WHEN ns.sentiment = 'negative' THEN 1 ELSE 0 END) as negative_count,
        SUM(CASE WHEN ns.sentiment = 'neutral' THEN 1 ELSE 0 END) as neutral_count
    FROM news_articles na
    JOIN news_sentiment ns ON na.id = ns.article_id
    WHERE na.company = company_name
      AND na.published_date >= CURRENT_DATE - days_back
    GROUP BY DATE(na.published_date)
    ORDER BY date DESC;
END;
$$ LANGUAGE plpgsql;

-- Sample queries for testing:
-- SELECT * FROM latest_news_with_sentiment LIMIT 10;
-- SELECT * FROM unacknowledged_alerts;
-- SELECT * FROM get_company_sentiment_trend('Reliance', 30);
