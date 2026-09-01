"""
Comprehensive data validation and quality check for RepSense AI project
"""
import pandas as pd
import numpy as np
import os
from pathlib import Path

def validate_files():
    """Validate all CSV files"""
    print("\n" + "="*80)
    print("COMPREHENSIVE DATA VALIDATION REPORT")
    print("="*80)
    
    issues = []
    
    # 1. Check pharma-data.csv (main source)
    print("\n1. MAIN SALES DATA (pharma-data.csv)")
    print("-" * 50)
    df = pd.read_csv('pharma-data.csv')
    print(f"   Shape: {df.shape}")
    print(f"   Missing values per column:")
    missing = df.isnull().sum()
    for col, cnt in missing[missing > 0].items():
        print(f"     - {col}: {cnt} ({100*cnt/len(df):.1f}%)")
    
    # Check for duplicates
    dup_count = df.duplicated().sum()
    print(f"   Duplicates: {dup_count}")
    
    # Check rep names
    print(f"   Unique Sales Reps: {df['Name_of_Sales_Rep'].nunique()}")
    
    # Check date range
    df['Date'] = pd.to_datetime(df['Year'].astype(str) + '-' + df['Month'].astype(str), format='%Y-%m', errors='coerce')
    print(f"   Date range: {df['Date'].min()} to {df['Date'].max()}")
    
    # 2. Check AI output file
    print("\n2. AI OUTPUT FILE (AI_rep_management_output.csv)")
    print("-" * 50)
    ai_df = pd.read_csv('AI_rep_management_output.csv')
    print(f"   Shape: {ai_df.shape}")
    print(f"   Date range: {pd.to_datetime(ai_df['Date']).min()} to {pd.to_datetime(ai_df['Date']).max()}")
    
    # Check for null risk columns
    risk_cols = ['Final_Risk_Score', 'Severity', 'Risk_Reasons', 'AI_Recommendation']
    for col in risk_cols:
        null_cnt = ai_df[col].isnull().sum()
        if null_cnt > 0:
            print(f"   ⚠️  {col}: {null_cnt} nulls")
            issues.append(f"AI output missing {null_cnt} values in {col}")
    
    # Check risk score distribution
    risk_scores = ai_df['Final_Risk_Score'].dropna()
    print(f"   Risk Score range: {risk_scores.min():.1f} - {risk_scores.max():.1f}")
    print(f"   Severity distribution:")
    for sev, cnt in ai_df['Severity'].value_counts().items():
        print(f"     - {sev}: {cnt}")
    
    # 3. Check HR data
    print("\n3. HR MASTER DATA (rep_master_hr.csv)")
    print("-" * 50)
    hr_df = pd.read_csv('rep_master_hr.csv')
    print(f"   Shape: {hr_df.shape}")
    print(f"   Columns: {list(hr_df.columns)}")
    print(f"   Reps: {hr_df['Name_of_Sales_Rep'].tolist()}")
    
    # 4. Check CRM data
    print("\n4. CRM ACTIVITY (crm_activity_detail.csv)")
    print("-" * 50)
    crm_df = pd.read_csv('crm_activity_detail.csv')
    print(f"   Shape: {crm_df.shape}")
    print(f"   Date range: {pd.to_datetime(crm_df['Date']).min()} to {pd.to_datetime(crm_df['Date']).max()}")
    print(f"   Unique reps: {crm_df['Name_of_Sales_Rep'].nunique()}")
    print(f"   Unique territories: {crm_df['Territory_ID'].nunique()}")
    
    # 5. Check promotional data
    print("\n5. PROMOTIONAL ACTIVITY (promotional_activity.csv)")
    print("-" * 50)
    promo_df = pd.read_csv('promotional_activity.csv')
    print(f"   Shape: {promo_df.shape}")
    print(f"   Date range: {pd.to_datetime(promo_df['Date']).min()} to {pd.to_datetime(promo_df['Date']).max()}")
    print(f"   Promotion types: {promo_df['Promotion_Type'].nunique()}")
    print(f"   Avg uplift: {promo_df['Sales_Uplift_%'].mean():.1f}%")
    
    # 6. Check critical territories (should have data)
    print("\n6. CRITICAL TERRITORIES (critical_territories.csv)")
    print("-" * 50)
    crit_df = pd.read_csv('critical_territories.csv')
    print(f"   Shape: {crit_df.shape}")
    if len(crit_df) == 0:
        print("   ⚠️  FILE IS EMPTY - This should contain critical territories!")
        issues.append("critical_territories.csv is empty")
    
    # 7. Check executive dashboard
    print("\n7. EXECUTIVE DASHBOARD (executive_dashboard.csv)")
    print("-" * 50)
    exec_df = pd.read_csv('executive_dashboard.csv')
    print(f"   Shape: {exec_df.shape}")
    print(f"   Columns: {list(exec_df.columns)}")
    
    # 8. Check promotion summary
    print("\n8. PROMOTION SUMMARY (promotion_summary.csv)")
    print("-" * 50)
    promo_sum = pd.read_csv('promotion_summary.csv')
    print(f"   Shape: {promo_sum.shape}")
    if len(promo_sum) < 3:
        print(f"   ⚠️  Only {len(promo_sum)} rows - expected 3+ impact categories")
        issues.append(f"promotion_summary.csv has only {len(promo_sum)} rows")
    
    print("\n" + "="*80)
    print("SUMMARY OF ISSUES FOUND:")
    print("="*80)
    if issues:
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
    else:
        print("  ✓ No major data quality issues detected")
    
    return issues

if __name__ == '__main__':
    validate_files()
