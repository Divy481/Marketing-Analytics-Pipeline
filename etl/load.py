import pandas as pd
from sqlalchemy import text

def load_data_to_db(campaigns_df: pd.DataFrame, customers_df: pd.DataFrame, metrics_df: pd.DataFrame, engine):
    """
    Loads transformed data into database tables:
    1. campaigns
    2. customers
    3. campaign_metrics
    """
    print("[LOAD] Inserting clean records into database...")
    
    with engine.begin() as conn:
        campaigns_df.to_sql("campaigns", con=conn, if_exists="replace", index=False)
        print(f"[LOAD] Loaded {len(campaigns_df)} rows into 'campaigns' table.")
        
        customers_df.to_sql("customers", con=conn, if_exists="replace", index=False)
        print(f"[LOAD] Loaded {len(customers_df)} rows into 'customers' table.")
        
        metrics_df.to_sql("campaign_metrics", con=conn, if_exists="replace", index=False)
        print(f"[LOAD] Loaded {len(metrics_df)} rows into 'campaign_metrics' table.")
        
    print("[LOAD] Database load completed successfully.")
