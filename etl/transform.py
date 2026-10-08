import pandas as pd
import numpy as np

def clean_campaigns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans raw campaign DataFrame:
    - Strips whitespace from column names & text values
    - Standardizes channel names
    - Drops duplicates based on campaign_id
    - Formats dates & casts numerical types
    """
    df = df.copy()
    
    # Strip whitespaces from column names
    df.columns = df.columns.str.strip()
    
    # Strip string columns
    str_cols = ['campaign_id', 'campaign_name', 'channel']
    for col in str_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            
    # Standardize channel names (title case or specific mappings)
    channel_map = {
        'meta': 'Meta',
        'google ads': 'Google Ads',
        'email': 'Email',
        'influencer': 'Influencer',
        'tiktok': 'TikTok',
        'youtube': 'YouTube'
    }
    df['channel'] = df['channel'].apply(lambda x: channel_map.get(x.lower(), x.title()))
    
    # Remove duplicates based on campaign_id
    df = df.drop_duplicates(subset=['campaign_id'], keep='first')
    
    # Cast numerical columns
    df['spend'] = pd.to_numeric(df['spend'], errors='coerce').fillna(0.0)
    df['impressions'] = pd.to_numeric(df['impressions'], errors='coerce').fillna(0).astype(int)
    df['clicks'] = pd.to_numeric(df['clicks'], errors='coerce').fillna(0).astype(int)
    
    # Ensure dates are valid strings YYYY-MM-DD
    df['start_date'] = pd.to_datetime(df['start_date']).dt.strftime('%Y-%m-%d')
    df['end_date'] = pd.to_datetime(df['end_date']).dt.strftime('%Y-%m-%d')
    
    return df

def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans raw customer interaction DataFrame:
    - Strips whitespace from string fields
    - Converts 'converted' to boolean
    - Fills missing order values with 0.0
    - Drops duplicate customer_id rows
    """
    df = df.copy()
    
    df.columns = df.columns.str.strip()
    
    str_cols = ['customer_id', 'campaign_id', 'name', 'email']
    for col in str_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            
    # Standardize boolean conversion status
    if 'converted' in df.columns:
        df['converted'] = df['converted'].astype(str).str.strip().str.upper().map({'TRUE': True, '1': True, 'FALSE': False, '0': False}).fillna(False)
        
    # Cast numeric order_value
    df['order_value'] = pd.to_numeric(df['order_value'], errors='coerce').fillna(0.0)
    
    # Drop duplicates by customer_id
    df = df.drop_duplicates(subset=['customer_id'], keep='first')
    
    # Ensure date format
    df['signup_date'] = pd.to_datetime(df['signup_date']).dt.strftime('%Y-%m-%d')
    
    return df

def calculate_campaign_metrics(campaigns_df: pd.DataFrame, customers_df: pd.DataFrame) -> pd.DataFrame:
    """
    Joins cleaned campaign & customer data to compute performance metrics:
    - conversions count
    - total_revenue generated
    - CTR (%)
    - Conversion Rate (%)
    - CPA ($)
    - ROAS (Revenue / Spend)
    """
    # Filter converted customers to compute revenue and conversion count
    conversions_summary = customers_df[customers_df['converted'] == True].groupby('campaign_id').agg(
        conversions=('customer_id', 'count'),
        total_revenue=('order_value', 'sum')
    ).reset_index()
    
    # Merge with campaigns
    metrics_df = pd.merge(campaigns_df, conversions_summary, on='campaign_id', how='left')
    
    # Fill missing conversions and revenue with 0
    metrics_df['conversions'] = metrics_df['conversions'].fillna(0).astype(int)
    metrics_df['total_revenue'] = metrics_df['total_revenue'].fillna(0.0).round(2)
    
    # Calculate CTR (%): (clicks / impressions) * 100
    metrics_df['ctr'] = np.where(
        metrics_df['impressions'] > 0,
        (metrics_df['clicks'] / metrics_df['impressions']) * 100.0,
        0.0
    ).round(2)
    
    # Calculate Conversion Rate (%): (conversions / clicks) * 100
    metrics_df['conversion_rate'] = np.where(
        metrics_df['clicks'] > 0,
        (metrics_df['conversions'] / metrics_df['clicks']) * 100.0,
        0.0
    ).round(2)
    
    # Calculate CPA ($): spend / conversions
    metrics_df['cpa'] = np.where(
        metrics_df['conversions'] > 0,
        metrics_df['spend'] / metrics_df['conversions'],
        0.0
    ).round(2)
    
    # Calculate ROAS: total_revenue / spend
    metrics_df['roas'] = np.where(
        metrics_df['spend'] > 0,
        metrics_df['total_revenue'] / metrics_df['spend'],
        0.0
    ).round(2)
    
    # Select columns matching database campaign_metrics table
    cols = [
        'campaign_id', 'campaign_name', 'channel', 'spend', 'impressions',
        'clicks', 'conversions', 'ctr', 'conversion_rate', 'cpa',
        'total_revenue', 'roas'
    ]
    return metrics_df[cols]
