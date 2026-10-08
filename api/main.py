import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
import pandas as pd
from sqlalchemy import text
from db.connection import get_db_engine
from run_pipeline import run_pipeline

app = FastAPI(
    title="Marketing Analytics & Customer Data API",
    description="REST API to query marketing campaign KPIs, customer conversions, and channel performance metrics.",
    version="1.0.0"
)

class CampaignMetricSchema(BaseModel):
    campaign_id: str
    campaign_name: str
    channel: str
    spend: float
    impressions: int
    clicks: int
    conversions: int
    ctr: float = Field(..., description="Click-through rate percentage")
    conversion_rate: float = Field(..., description="Conversion rate percentage")
    cpa: float = Field(..., description="Cost per acquisition in USD")
    total_revenue: float = Field(..., description="Total revenue generated in USD")
    roas: float = Field(..., description="Return on ad spend (Revenue / Spend)")

class CustomerSchema(BaseModel):
    customer_id: str
    campaign_id: Optional[str]
    name: str
    email: str
    signup_date: str
    converted: bool
    order_value: float

class ExecutiveSummarySchema(BaseModel):
    total_campaigns: int
    total_customers: int
    total_spend: float
    total_revenue: float
    overall_roas: float
    overall_conversion_rate: float
    top_performing_channel: str

class ChannelPerformanceSchema(BaseModel):
    channel: str
    total_campaigns: int
    total_spend: float
    total_impressions: int
    total_clicks: int
    total_conversions: int
    total_revenue: float
    avg_ctr: float
    avg_conversion_rate: float
    channel_roas: float

def query_db(query_str: str, params: dict = None) -> pd.DataFrame:
    engine = get_db_engine()
    try:
        with engine.connect() as conn:
            return pd.read_sql(text(query_str), con=conn, params=params or {})
    except Exception as e:
        print(f"[API DB NOTICE] Table missing or query error: {e}. Executing ETL pipeline...")
        run_pipeline()
        with engine.connect() as conn:
            return pd.read_sql(text(query_str), con=conn, params=params or {})

@app.get("/", tags=["Health"])
def root():
    return {
        "status": "online",
        "service": "Marketing Analytics & Customer Data Pipeline API",
        "version": "1.0.0",
        "documentation": "/docs"
    }

@app.get("/api/metrics/summary", response_model=ExecutiveSummarySchema, tags=["Analytics"])
def get_executive_summary():
    """Retrieve high-level marketing analytics and overall pipeline KPIs."""
    df_metrics = query_db("SELECT * FROM campaign_metrics")
    df_cust = query_db("SELECT * FROM customers")
    
    if df_metrics.empty:
        raise HTTPException(status_code=444, detail="No metric data available in database.")
        
    total_campaigns = int(len(df_metrics))
    total_customers = int(len(df_cust))
    total_spend = float(round(df_metrics['spend'].sum(), 2))
    total_revenue = float(round(df_metrics['total_revenue'].sum(), 2))
    
    overall_roas = float(round(total_revenue / total_spend, 2)) if total_spend > 0 else 0.0
    
    total_clicks = df_metrics['clicks'].sum()
    total_conversions = df_metrics['conversions'].sum()
    overall_conv_rate = float(round((total_conversions / total_clicks) * 100, 2)) if total_clicks > 0 else 0.0
    
    channel_rev = df_metrics.groupby('channel')['total_revenue'].sum()
    top_channel = channel_rev.idxmax() if not channel_rev.empty else "N/A"
    
    return ExecutiveSummarySchema(
        total_campaigns=total_campaigns,
        total_customers=total_customers,
        total_spend=total_spend,
        total_revenue=total_revenue,
        overall_roas=overall_roas,
        overall_conversion_rate=overall_conv_rate,
        top_performing_channel=top_channel
    )

@app.get("/api/campaigns", response_model=List[CampaignMetricSchema], tags=["Campaigns"])
def get_campaigns(channel: Optional[str] = Query(None, description="Filter campaigns by marketing channel (e.g. Meta, Google Ads)")):
    """Retrieve all campaign performance metrics with optional channel filter."""
    if channel:
        df = query_db("SELECT * FROM campaign_metrics WHERE LOWER(channel) = LOWER(:channel)", {"channel": channel})
    else:
        df = query_db("SELECT * FROM campaign_metrics")
        
    return df.to_dict(orient="records")

@app.get("/api/campaigns/{campaign_id}", response_model=CampaignMetricSchema, tags=["Campaigns"])
def get_campaign_by_id(campaign_id: str):
    """Retrieve specific campaign metrics by ID."""
    df = query_db("SELECT * FROM campaign_metrics WHERE LOWER(campaign_id) = LOWER(:cid)", {"cid": campaign_id})
    if df.empty:
        raise HTTPException(status_code=404, detail=f"Campaign with ID '{campaign_id}' not found.")
    return df.iloc[0].to_dict()

@app.get("/api/customers", response_model=List[CustomerSchema], tags=["Customers"])
def get_customers(
    converted: Optional[bool] = Query(None, description="Filter customers by conversion status (true/false)"),
    limit: int = Query(20, ge=1, le=100, description="Page size limit"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """Retrieve customer list with optional conversion filter and pagination."""
    query = "SELECT * FROM customers"
    params = {}
    
    if converted is not None:
        query += " WHERE converted = :converted"
        params["converted"] = converted
        
    query += " LIMIT :limit OFFSET :offset"
    params["limit"] = limit
    params["offset"] = offset
    
    df = query_db(query, params)
    return df.to_dict(orient="records")

@app.get("/api/channels", response_model=List[ChannelPerformanceSchema], tags=["Analytics"])
def get_channel_performance():
    """Retrieve aggregated performance broken down by marketing channel."""
    df_metrics = query_db("SELECT * FROM campaign_metrics")
    if df_metrics.empty:
        return []
        
    grouped = df_metrics.groupby('channel').agg(
        total_campaigns=('campaign_id', 'count'),
        total_spend=('spend', 'sum'),
        total_impressions=('impressions', 'sum'),
        total_clicks=('clicks', 'sum'),
        total_conversions=('conversions', 'sum'),
        total_revenue=('total_revenue', 'sum'),
        avg_ctr=('ctr', 'mean'),
        avg_conversion_rate=('conversion_rate', 'mean')
    ).reset_index()
    
    grouped['channel_roas'] = (grouped['total_revenue'] / grouped['total_spend']).round(2)
    grouped['total_spend'] = grouped['total_spend'].round(2)
    grouped['total_revenue'] = grouped['total_revenue'].round(2)
    grouped['avg_ctr'] = grouped['avg_ctr'].round(2)
    grouped['avg_conversion_rate'] = grouped['avg_conversion_rate'].round(2)
    
    return grouped.to_dict(orient="records")
