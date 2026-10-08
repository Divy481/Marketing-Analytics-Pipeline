import pytest
import pandas as pd
from etl.transform import clean_campaigns, clean_customers, calculate_campaign_metrics

def test_clean_campaigns():
    raw_data = pd.DataFrame([
        {
            "campaign_id": " C100 ",
            "campaign_name": "Test Meta Ad",
            "channel": " meta ",
            "spend": "500.00",
            "impressions": "10000",
            "clicks": "500",
            "start_date": "2026-06-01",
            "end_date": "2026-06-10"
        },
        # Duplicate entry
        {
            "campaign_id": "C100",
            "campaign_name": "Test Meta Ad",
            "channel": "meta",
            "spend": "500.00",
            "impressions": "10000",
            "clicks": "500",
            "start_date": "2026-06-01",
            "end_date": "2026-06-10"
        }
    ])
    
    cleaned = clean_campaigns(raw_data)
    
    # Verify duplicates removed
    assert len(cleaned) == 1
    # Verify channel standardized
    assert cleaned.iloc[0]['channel'] == "Meta"
    # Verify whitespace stripped
    assert cleaned.iloc[0]['campaign_id'] == "C100"
    # Verify numeric cast
    assert cleaned.iloc[0]['spend'] == 500.0
    assert cleaned.iloc[0]['clicks'] == 500

def test_clean_customers():
    raw_data = pd.DataFrame([
        {
            "customer_id": "U001",
            "campaign_id": "C100",
            "name": " John Doe ",
            "email": "john@example.com ",
            "signup_date": "2026-06-02",
            "converted": "TRUE",
            "order_value": "150.00"
        }
    ])
    
    cleaned = clean_customers(raw_data)
    assert len(cleaned) == 1
    assert cleaned.iloc[0]['name'] == "John Doe"
    assert cleaned.iloc[0]['email'] == "john@example.com"
    assert bool(cleaned.iloc[0]['converted']) is True
    assert cleaned.iloc[0]['order_value'] == 150.00

def test_calculate_campaign_metrics():
    campaigns = pd.DataFrame([
        {
            "campaign_id": "C100",
            "campaign_name": "Summer Promo",
            "channel": "Meta",
            "spend": 1000.00,
            "impressions": 50000,
            "clicks": 2000,
            "start_date": "2026-06-01",
            "end_date": "2026-06-15"
        }
    ])
    
    customers = pd.DataFrame([
        {
            "customer_id": "U001",
            "campaign_id": "C100",
            "name": "Alice",
            "email": "alice@example.com",
            "signup_date": "2026-06-02",
            "converted": True,
            "order_value": 200.00
        },
        {
            "customer_id": "U002",
            "campaign_id": "C100",
            "name": "Bob",
            "email": "bob@example.com",
            "signup_date": "2026-06-03",
            "converted": True,
            "order_value": 300.00
        },
        {
            "customer_id": "U003",
            "campaign_id": "C100",
            "name": "Charlie",
            "email": "charlie@example.com",
            "signup_date": "2026-06-04",
            "converted": False,
            "order_value": 0.00
        }
    ])
    
    metrics = calculate_campaign_metrics(campaigns, customers)
    row = metrics.iloc[0]
    
    # CTR = (2000 / 50000) * 100 = 4.0%
    assert row['ctr'] == 4.0
    # Conversions = 2
    assert row['conversions'] == 2
    # Conversion Rate = (2 / 2000) * 100 = 0.1%
    assert row['conversion_rate'] == 0.1
    # CPA = 1000 / 2 = 500.0
    assert row['cpa'] == 500.0
    # Total revenue = 200 + 300 = 500.00
    assert row['total_revenue'] == 500.00
    # ROAS = 500 / 1000 = 0.5
    assert row['roas'] == 0.5
