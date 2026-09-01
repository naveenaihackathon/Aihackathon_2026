"""
Data Preprocessing Pipeline
Handles cleaning, standardization, and preparation of sales data
"""

import pandas as pd
import numpy as np
from datetime import datetime

def clean_pharma_data(df):
    """
    Clean and standardize pharma sales data
    
    Args:
        df: Raw pharma-data.csv DataFrame
        
    Returns:
        Cleaned DataFrame with standardized columns
    """
    df = df.copy()
    
    # 1. Standardize column names (remove spaces, make lowercase with underscores)
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    
    # 2. Strip whitespace from text columns
    text_cols = df.select_dtypes(include=['object']).columns
    for col in text_cols:
        df[col] = df[col].str.strip()
    
    # 3. Remove exact duplicates (safe removal)
    df = df.drop_duplicates(keep='first')
    
    # 4. Create standardized Date column from Year + Month
    df['date'] = pd.to_datetime(
        df['year'].astype(str) + '-' + df['month'].astype(str).str.zfill(2),
        format='%Y-%m',
        errors='coerce'
    )
    
    # If there are NaT values, fill them with a default date
    if df['date'].isna().any():
        # Use the median date or a default
        valid_dates = df[df['date'].notna()]['date']
        if len(valid_dates) > 0:
            fill_date = valid_dates.median()
        else:
            fill_date = pd.Timestamp('2017-01-01')
        df['date'] = df['date'].fillna(fill_date)
    
    # 5. Create transaction flag columns
    df['is_negative_transaction'] = df['sales'] < 0
    
    # 6. Handle negative transactions - keep them but flag
    # They represent returns or adjustments
    
    # 7. Ensure numeric types
    numeric_cols = ['quantity', 'price', 'sales', 'month', 'year']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 8. Create Rep_ID mapping for consistency
    # Use rep name as basis but create stable IDs
    rep_mapping = {
        rep_name: f"REP_{i:03d}"
        for i, rep_name in enumerate(sorted(df['name_of_sales_rep'].unique()), 1)
    }
    df['rep_id'] = df['name_of_sales_rep'].map(rep_mapping)
    
    # 9. Create Territory_ID from City (deterministic mapping)
    # Map cities to territories consistently
    territory_mapping = {}
    cities = sorted(df['city'].dropna().unique())
    for city in cities:
        # Assign cities to territories in round-robin fashion
        territory_idx = len(territory_mapping) % 8  # 8 territories
        territory_mapping[city] = f"TERR_{territory_idx + 1:02d}"
    
    df['territory_id'] = df['city'].map(territory_mapping)
    
    # 10. Create HCP_ID from Customer Name (for CRM tracking)
    hcp_mapping = {}
    customers = sorted(df['customer_name'].dropna().unique())
    for customer in customers:
        hcp_idx = len(hcp_mapping) + 1
        hcp_mapping[customer] = f"HCP_{hcp_idx:05d}"
    
    df['hcp_id'] = df['customer_name'].map(hcp_mapping)
    
    # 11. Select and order columns for output (only include columns that exist)
    available_cols = df.columns.tolist()
    output_cols = [
        'date', 'rep_id', 'name_of_sales_rep', 'manager', 'sales_team',
        'territory_id', 'hcp_id', 'customer_name', 'city', 'country',
        'latitude', 'longitude', 'channel', 'sub-channel',
        'product_name', 'product_class', 'quantity', 'price', 'sales',
        'is_negative_transaction', 'month', 'year'
    ]
    
    # Filter to only columns that exist
    output_cols = [col for col in output_cols if col in available_cols]
    
    return df[output_cols]


def create_monthly_rep_summary(df):
    """
    Create monthly summary by rep for time-series analysis
    
    Args:
        df: Cleaned sales data
        
    Returns:
        Monthly rep-level aggregated DataFrame
    """
    monthly = df.groupby(['date', 'rep_id', 'name_of_sales_rep', 'manager', 'sales_team']).agg({
        'sales': ['sum', 'count'],
        'quantity': 'sum',
        'customer_name': 'nunique',
        'product_name': 'nunique',
        'hcp_id': 'nunique',
    }).reset_index()
    
    monthly.columns = ['date', 'rep_id', 'name_of_sales_rep', 'manager', 'sales_team',
                       'sales', 'transactions', 'quantity', 'customers', 'products', 'hcps']
    
    # Calculate previous month sales for change calculation
    monthly = monthly.sort_values(['rep_id', 'date'])
    monthly['previous_month_sales'] = monthly.groupby('rep_id')['sales'].shift(1)
    monthly['sales_change_pct'] = (
        (monthly['sales'] - monthly['previous_month_sales']) / 
        monthly['previous_month_sales'] * 100
    ).replace([np.inf, -np.inf], np.nan)
    
    # Calculate rolling 3-month average
    monthly['rolling_3m_sales'] = monthly.groupby('rep_id')['sales'].transform(
        lambda x: x.rolling(window=3, min_periods=1).mean()
    )
    monthly['sales_vs_3m_avg_pct'] = (
        (monthly['sales'] - monthly['rolling_3m_sales']) /
        monthly['rolling_3m_sales'] * 100
    ).replace([np.inf, -np.inf], np.nan)
    
    return monthly.fillna(0)


def create_monthly_territory_summary(df):
    """
    Create monthly summary by territory for territorial analysis
    
    Args:
        df: Cleaned sales data
        
    Returns:
        Monthly territory-level aggregated DataFrame
    """
    monthly = df.groupby(['date', 'territory_id']).agg({
        'sales': ['sum', 'count'],
        'quantity': 'sum',
        'customer_name': 'nunique',
        'product_name': 'nunique',
        'rep_id': 'nunique',
        'hcp_id': 'nunique',
    }).reset_index()
    
    monthly.columns = ['date', 'territory_id',
                       'sales', 'transactions', 'quantity', 'customers',
                       'products', 'active_reps', 'hcps']
    
    # Calculate previous month sales for change calculation
    monthly = monthly.sort_values(['territory_id', 'date'])
    monthly['previous_month_sales'] = monthly.groupby('territory_id')['sales'].shift(1)
    monthly['sales_change_pct'] = (
        (monthly['sales'] - monthly['previous_month_sales']) /
        monthly['previous_month_sales'] * 100
    ).replace([np.inf, -np.inf], np.nan)
    
    # Calculate rolling 3-month average
    monthly['rolling_3m_sales'] = monthly.groupby('territory_id')['sales'].transform(
        lambda x: x.rolling(window=3, min_periods=1).mean()
    )
    monthly['sales_vs_3m_avg_pct'] = (
        (monthly['sales'] - monthly['rolling_3m_sales']) /
        monthly['rolling_3m_sales'] * 100
    ).replace([np.inf, -np.inf], np.nan)
    
    return monthly.fillna(0)


if __name__ == '__main__':
    # Example usage
    print("Testing preprocessing pipeline...")
    
    # Load and clean
    raw_df = pd.read_csv('pharma-data.csv')
    print(f"Raw data: {raw_df.shape}")
    
    cleaned_df = clean_pharma_data(raw_df)
    print(f"Cleaned data: {cleaned_df.shape}")
    
    # Save cleaned data
    cleaned_df.to_csv('pharma_sales_cleaned.csv', index=False)
    print("✓ Saved: pharma_sales_cleaned.csv")
    
    # Create summaries
    rep_summary = create_monthly_rep_summary(cleaned_df)
    rep_summary.to_csv('rep_monthly_analysis.csv', index=False)
    print(f"✓ Saved: rep_monthly_analysis.csv ({rep_summary.shape[0]} rows)")
    
    terr_summary = create_monthly_territory_summary(cleaned_df)
    terr_summary.to_csv('territory_monthly_analysis.csv', index=False)
    print(f"✓ Saved: territory_monthly_analysis.csv ({terr_summary.shape[0]} rows)")
