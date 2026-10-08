import os
import sys
from db.connection import get_db_engine, execute_sql_file
from etl.extract import extract_campaigns, extract_customers
from etl.transform import clean_campaigns, clean_customers, calculate_campaign_metrics
from etl.load import load_data_to_db

def run_pipeline(db_url: str = None):
    print("=" * 60)
    print("  STARTING MARKETING ANALYTICS & CUSTOMER DATA PIPELINE")
    print("=" * 60)
    
    # 1. Base Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    campaigns_csv = os.path.join(base_dir, "data", "campaigns_raw.csv")
    customers_csv = os.path.join(base_dir, "data", "customers_raw.csv")
    schema_sql = os.path.join(base_dir, "db", "schema.sql")
    
    # 2. DB Engine Setup
    engine = get_db_engine(db_url)
    
    # Run Schema SQL if connected to Postgres
    if "postgresql" in str(engine.url):
        print("[DB] Applying database schema...")
        try:
            execute_sql_file(schema_sql, engine)
        except Exception as e:
            print(f"[DB WARNING] Could not run schema script directly ({e}). Continuing with pandas load...")

    # 3. Extract Phase
    raw_campaigns = extract_campaigns(campaigns_csv)
    raw_customers = extract_customers(customers_csv)
    
    # 4. Transform Phase
    print("[TRANSFORM] Cleaning campaign & customer data...")
    clean_camp_df = clean_campaigns(raw_campaigns)
    clean_cust_df = clean_customers(raw_customers)
    
    print("[TRANSFORM] Calculating marketing metrics (CTR, Conversion Rate, CPA, ROAS)...")
    metrics_df = calculate_campaign_metrics(clean_camp_df, clean_cust_df)
    
    # 5. Load Phase
    load_data_to_db(clean_camp_df, clean_cust_df, metrics_df, engine)
    
    # 6. Summary Report
    print("=" * 60)
    print("  PIPELINE EXECUTION SUMMARY")
    print("=" * 60)
    print(f"Total Campaigns Processed : {len(clean_camp_df)}")
    print(f"Total Customers Processed : {len(clean_cust_df)}")
    print(f"Total Ad Spend           : ${clean_camp_df['spend'].sum():,.2f}")
    print(f"Total Revenue Generated   : ${metrics_df['total_revenue'].sum():,.2f}")
    
    if clean_camp_df['spend'].sum() > 0:
        overall_roas = metrics_df['total_revenue'].sum() / clean_camp_df['spend'].sum()
        print(f"Overall Pipeline ROAS    : {overall_roas:.2f}x")
        
    print("=" * 60)
    print("  ETL PIPELINE COMPLETED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    db_override = sys.argv[1] if len(sys.argv) > 1 else None
    run_pipeline(db_override)
