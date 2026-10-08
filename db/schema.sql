-- Marketing Analytics & Customer Data Pipeline Schema

DROP VIEW IF EXISTS view_channel_performance CASCADE;
DROP VIEW IF EXISTS view_executive_summary CASCADE;
DROP TABLE IF EXISTS campaign_metrics CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS campaigns CASCADE;

-- Base Table: Campaigns
CREATE TABLE campaigns (
    campaign_id VARCHAR(50) PRIMARY KEY,
    campaign_name VARCHAR(150) NOT NULL,
    channel VARCHAR(50) NOT NULL,
    spend NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    impressions INT NOT NULL DEFAULT 0,
    clicks INT NOT NULL DEFAULT 0,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Base Table: Customers
CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    campaign_id VARCHAR(50) REFERENCES campaigns(campaign_id) ON DELETE SET NULL,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL,
    signup_date DATE NOT NULL,
    converted BOOLEAN NOT NULL DEFAULT FALSE,
    order_value NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Derived Table: Campaign Metrics & Performance
CREATE TABLE campaign_metrics (
    campaign_id VARCHAR(50) PRIMARY KEY REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    campaign_name VARCHAR(150) NOT NULL,
    channel VARCHAR(50) NOT NULL,
    spend NUMERIC(12, 2) NOT NULL,
    impressions INT NOT NULL,
    clicks INT NOT NULL,
    conversions INT NOT NULL DEFAULT 0,
    ctr NUMERIC(6, 2) NOT NULL DEFAULT 0.00,             -- (clicks / impressions) * 100
    conversion_rate NUMERIC(6, 2) NOT NULL DEFAULT 0.00, -- (conversions / clicks) * 100
    cpa NUMERIC(12, 2) NOT NULL DEFAULT 0.00,             -- spend / conversions
    total_revenue NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    roas NUMERIC(8, 2) NOT NULL DEFAULT 0.00,             -- total_revenue / spend
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- View: Aggregated Channel Performance
CREATE VIEW view_channel_performance AS
SELECT 
    channel,
    COUNT(campaign_id) AS total_campaigns,
    SUM(spend) AS total_spend,
    SUM(impressions) AS total_impressions,
    SUM(clicks) AS total_clicks,
    SUM(conversions) AS total_conversions,
    SUM(total_revenue) AS total_revenue,
    ROUND(AVG(ctr), 2) AS avg_ctr,
    ROUND(AVG(conversion_rate), 2) AS avg_conversion_rate,
    CASE 
        WHEN SUM(spend) > 0 THEN ROUND(SUM(total_revenue) / SUM(spend), 2)
        ELSE 0.00
    END AS channel_roas
FROM campaign_metrics
GROUP BY channel;
