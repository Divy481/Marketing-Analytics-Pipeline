import os
import pandas as pd

def extract_campaigns(csv_path: str) -> pd.DataFrame:
    """Extract raw campaigns data from CSV."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Campaigns CSV file not found at: {csv_path}")
    
    print(f"[EXTRACT] Reading campaigns dataset from: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"[EXTRACT] Extracted {len(df)} campaign records.")
    return df

def extract_customers(csv_path: str) -> pd.DataFrame:
    """Extract raw customer interaction data from CSV."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Customers CSV file not found at: {csv_path}")
        
    print(f"[EXTRACT] Reading customers dataset from: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"[EXTRACT] Extracted {len(df)} customer records.")
    return df
