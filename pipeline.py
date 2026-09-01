"""
RepSense AI - Complete Pipeline
Orchestrates entire workflow: data cleaning → feature engineering → anomaly detection → risk scoring
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

from config import THRESHOLDS, ANOMALY_CONFIG, RISK_WEIGHTS, SEVERITY_RANGES, SYNTHETIC_DATA_SEED
from preprocessing import clean_pharma_data, create_monthly_territory_summary

def generate_synthetic_hr_data(cleaned_df):
    """
    Generate or validate synthetic HR/rep master data
    Uses actual reps from sales data for consistency
    """
    reps = cleaned_df['name_of_sales_rep'].unique()
    
    np.random.seed(SYNTHETIC_DATA_SEED)
    hr_data = []
    
    for i, rep_name in enumerate(sorted(reps)):
        manager = cleaned_df[cleaned_df['name_of_sales_rep'] == rep_name]['manager'].iloc[0]
        sales_team = cleaned_df[cleaned_df['name_of_sales_rep'] == rep_name]['sales_team'].iloc[0]
        primary_territory = cleaned_df[cleaned_df['name_of_sales_rep'] == rep_name]['territory_id'].iloc[0]
        
        # Randomly assign employment status (mostly active)
        status = np.random.choice(['Active', 'Vacant', 'Exit'], p=[0.75, 0.15, 0.10])
        
        # If vacant, assign random vacancy days
        vacancy_days = np.random.randint(0, 150) if status == 'Vacant' else 0
        
        hr_data.append({
            'rep_id': f"REP_{i+1:03d}",
            'name_of_sales_rep': rep_name,
            'manager': manager,
            'sales_team': sales_team,
            'primary_territory': primary_territory,
            'employment_status': status,
            'vacancy_flag': 1 if status == 'Vacant' else 0,
            'vacancy_days': vacancy_days,
        })
    
    hr_df = pd.DataFrame(hr_data)
    
    # Add territory summary from the HR assignments, counting active reps only.
    territories = cleaned_df[['territory_id']].drop_duplicates()
    active_reps = hr_df[hr_df['employment_status'] == 'Active']
    territory_stats = territories.merge(
        active_reps.groupby('primary_territory').size().rename('current_reps'),
        left_on='territory_id',
        right_index=True,
        how='left',
    )
    territory_stats['current_reps'] = territory_stats['current_reps'].fillna(0).astype(int)
    territory_stats['required_reps'] = 2  # Demo: assume 2 reps per territory
    territory_stats['vacancies'] = (
        territory_stats['required_reps'] - territory_stats['current_reps']
    ).clip(lower=0)
    
    return hr_df, territory_stats


def generate_synthetic_crm_data(cleaned_df, date_range):
    """
    Generate synthetic CRM activity data - MONTHLY aggregated for efficiency
    Consistent with sales reps and dates
    """
    np.random.seed(SYNTHETIC_DATA_SEED)
    
    reps = cleaned_df[['rep_id', 'name_of_sales_rep', 'territory_id']].drop_duplicates()
    hcps = cleaned_df[['hcp_id', 'customer_name']].drop_duplicates()
    
    crm_records = []
    
    # Generate monthly data for efficiency (not daily)
    for date in pd.date_range(start=date_range[0], end=date_range[1], freq='MS'):
        for _, rep_row in reps.iterrows():
            rep_id = rep_row['rep_id']
            rep_name = rep_row['name_of_sales_rep']
            territory = rep_row['territory_id']
            
            # Vary activity by rep (some are more active than others)
            rep_activity_level = np.random.uniform(0.5, 1.0)
            
            # Planned calls/visits
            planned_calls = int(np.random.normal(150, 20) * rep_activity_level)
            planned_visits = int(np.random.normal(80, 15) * rep_activity_level)
            
            # Actual completion (typically 70-95% completion)
            completion_rate = np.random.uniform(0.7, 0.95)
            actual_calls = int(planned_calls * completion_rate)
            actual_visits = int(planned_visits * completion_rate)
            
            # HCP coverage (unique customers visited)
            hcp_coverage_count = int(np.random.normal(8, 2))
            hcp_coverage_pct = min(100, (hcp_coverage_count / max(len(hcps), 1)) * 100)
            
            crm_records.append({
                'date': date,
                'rep_id': rep_id,
                'name_of_sales_rep': rep_name,
                'territory_id': territory,
                'planned_calls': planned_calls,
                'actual_calls': actual_calls,
                'planned_visits': planned_visits,
                'actual_visits': actual_visits,
                'call_completion_pct': (actual_calls / max(planned_calls, 1)) * 100,
                'visit_completion_pct': (actual_visits / max(planned_visits, 1)) * 100,
                'hcp_coverage_count': hcp_coverage_count,
                'hcp_coverage_pct': hcp_coverage_pct,
            })
    
    crm_monthly = pd.DataFrame(crm_records)
    
    return crm_monthly, crm_monthly  # Return same twice since already monthly


def generate_synthetic_promotion_data(cleaned_df, date_range):
    """
    Generate synthetic promotional activity data
    """
    np.random.seed(SYNTHETIC_DATA_SEED)
    
    promo_types = ['Product Presentation', 'HCP Meeting', 'Product Demonstration', 
                   'Educational Session', 'Campaign']
    
    reps = cleaned_df[['rep_id', 'name_of_sales_rep', 'territory_id']].drop_duplicates()
    products = cleaned_df[['product_name', 'product_class']].drop_duplicates()
    hcps = cleaned_df['hcp_id'].unique()
    
    promo_records = []
    
    # Generate ~20-30 promotions per month
    n_promos = int(len(date_range) * 25)
    
    for _ in range(n_promos):
        date = pd.Timestamp(np.random.choice(pd.date_range(date_range[0], date_range[1])))
        rep = reps.sample(1).iloc[0]
        product = products.sample(1).iloc[0]
        hcp = np.random.choice(hcps)
        
        # Sales before promotion
        sales_before = np.random.exponential(scale=10000)
        
        # Promotion uplift (typically 5-40%)
        uplift_pct = np.random.uniform(5, 40)
        sales_after = sales_before * (1 + uplift_pct / 100)
        
        # Impact classification
        if uplift_pct >= 20:
            impact = 'High Impact'
        elif uplift_pct >= 10:
            impact = 'Medium Impact'
        else:
            impact = 'Low Impact'
        
        promo_records.append({
            'date': date,
            'rep_id': rep['rep_id'],
            'name_of_sales_rep': rep['name_of_sales_rep'],
            'territory_id': rep['territory_id'],
            'hcp_id': hcp,
            'product_name': product['product_name'],
            'product_class': product['product_class'],
            'promotion_type': np.random.choice(promo_types),
            'sales_before': sales_before,
            'sales_after': sales_after,
            'sales_uplift_%': uplift_pct,
            'promotion_impact': impact,
        })
    
    promo_df = pd.DataFrame(promo_records)
    
    return promo_df


def engineer_features(territory_monthly, crm_monthly, promo_data, hr_territories):
    """
    Create comprehensive feature table for anomaly detection
    """
    features = territory_monthly.copy()
    
    # Merge CRM data
    crm_agg = crm_monthly.groupby(['date', 'territory_id']).agg({
        'planned_calls': 'sum',
        'actual_calls': 'sum',
        'planned_visits': 'sum',
        'actual_visits': 'sum',
        'call_completion_pct': 'mean',
        'visit_completion_pct': 'mean',
        'hcp_coverage_pct': 'mean',
    }).reset_index()
    
    features = features.merge(crm_agg, on=['date', 'territory_id'], how='left')
    
    # Calculate CRM activity composite
    features['avg_activity'] = features[[col for col in features.columns if 'completion' in col]].mean(axis=1)
    features['avg_hcp_coverage'] = features['hcp_coverage_pct'].fillna(75)
    
    # Calculate activity change
    features = features.sort_values(['territory_id', 'date'])
    features['prev_month_activity'] = features.groupby('territory_id')['avg_activity'].shift(1)
    features['activity_change_pct'] = (
        (features['avg_activity'] - features['prev_month_activity']) /
        features['prev_month_activity'] * 100
    ).replace([np.inf, -np.inf], np.nan).fillna(0)
    
    # Merge HR/vacancy data
    features = features.merge(hr_territories, left_on='territory_id', right_on='territory_id', how='left')
    
    # Add promotional data
    promo_monthly = promo_data.groupby(['date', 'territory_id']).agg({
        'sales_uplift_%': 'mean',
        'name_of_sales_rep': 'count',
    }).reset_index()
    promo_monthly.columns = ['date', 'territory_id', 'avg_promotion_uplift', 'promotion_count']
    promo_monthly['date'] = pd.to_datetime(promo_monthly['date']).dt.to_period('M').dt.to_timestamp()
    
    features = features.merge(promo_monthly, on=['date', 'territory_id'], how='left')
    features['promotion_count'] = features['promotion_count'].fillna(0)
    features['avg_promotion_uplift'] = features['avg_promotion_uplift'].fillna(0)
    
    # Fill missing vacancy data
    features['current_reps'] = features['current_reps'].fillna(1)
    features['vacancies'] = features['vacancies'].fillna(0)
    
    return features


def detect_anomalies(features_df):
    """
    Perform anomaly detection using Isolation Forest and LOF
    """
    # Select numeric features for anomaly detection
    feature_cols = [
        'sales', 'rolling_3m_sales', 'sales_change_pct',
        'avg_activity', 'activity_change_pct', 'avg_hcp_coverage',
        'vacancies', 'actual_calls', 'actual_visits', 'promotion_count'
    ]
    
    X = features_df[feature_cols].copy()
    
    # Handle missing values
    X = X.fillna(X.mean())
    # Replace inf values with column mean
    for col in X.columns:
        X[col] = X[col].replace([np.inf, -np.inf], X[col].mean())
    
    # Standardize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Isolation Forest
    if_model = IsolationForest(
        contamination=ANOMALY_CONFIG['isolation_forest']['contamination'],
        random_state=ANOMALY_CONFIG['isolation_forest']['random_state'],
        n_estimators=100
    )
    if_predictions = if_model.fit_predict(X_scaled)
    if_scores = -if_model.score_samples(X_scaled)  # Negative so higher = more anomalous
    
    # Normalize IF scores to 0-100
    if_scores_norm = ((if_scores - if_scores.min()) / (if_scores.max() - if_scores.min())) * 100
    
    # LOF
    lof_model = LocalOutlierFactor(
        n_neighbors=ANOMALY_CONFIG['lof']['n_neighbors'],
        contamination=ANOMALY_CONFIG['lof']['contamination']
    )
    lof_predictions = lof_model.fit_predict(X_scaled)
    lof_scores = -lof_model.negative_outlier_factor_  # Negative so higher = more anomalous
    
    # Normalize LOF scores to 0-100
    lof_scores_norm = ((lof_scores - lof_scores.min()) / (lof_scores.max() - lof_scores.min())) * 100
    
    # Ensemble score
    ensemble_score = (
        if_scores_norm * ANOMALY_CONFIG['isolation_forest']['weight'] +
        lof_scores_norm * ANOMALY_CONFIG['lof']['weight']
    )
    
    # Add to dataframe
    features_df['isolation_forest_score'] = if_scores_norm
    features_df['lof_score'] = lof_scores_norm
    features_df['ensemble_anomaly_score'] = ensemble_score
    features_df['if_anomaly'] = (if_predictions == -1).astype(int)
    features_df['lof_anomaly'] = (lof_predictions == -1).astype(int)
    
    return features_df


def compute_risk_scores(features_df):
    """
    Compute comprehensive risk scores combining ML and business rules
    """
    df = features_df.copy()
    
    # ===== BUSINESS RULE SCORES (0-100) =====
    
    # Sales Risk
    df['sales_risk_score'] = 0.0
    df.loc[df['sales_change_pct'] <= THRESHOLDS['sales_decline']['warning'], 'sales_risk_score'] = 25
    df.loc[df['sales_change_pct'] <= THRESHOLDS['sales_decline']['major'], 'sales_risk_score'] = 50
    df.loc[df['sales_change_pct'] <= THRESHOLDS['sales_decline']['critical'], 'sales_risk_score'] = 100
    
    # CRM Risk
    df['crm_risk_score'] = 0.0
    df.loc[df['avg_activity'] < THRESHOLDS['crm_activity']['critical'], 'crm_risk_score'] = 100
    df.loc[df['avg_activity'] < THRESHOLDS['crm_activity']['major'], 'crm_risk_score'] = 50
    df.loc[df['avg_activity'] < THRESHOLDS['crm_activity']['warning'], 'crm_risk_score'] = 25
    
    # HCP Coverage Risk
    df['hcp_coverage_risk_score'] = 0.0
    df.loc[df['avg_hcp_coverage'] < THRESHOLDS['hcp_coverage']['critical'], 'hcp_coverage_risk_score'] = 100
    df.loc[df['avg_hcp_coverage'] < THRESHOLDS['hcp_coverage']['major'], 'hcp_coverage_risk_score'] = 50
    df.loc[df['avg_hcp_coverage'] < THRESHOLDS['hcp_coverage']['warning'], 'hcp_coverage_risk_score'] = 25
    
    # Vacancy Risk
    df['vacancy_risk_score'] = 0.0
    df.loc[df['vacancies'] >= 1, 'vacancy_risk_score'] = 25
    df.loc[df['vacancies'] >= 2, 'vacancy_risk_score'] = 60
    
    # Long Vacancy Risk (MAX_VACANCY_DAYS not in our features, so we estimate)
    df['long_vacancy_risk'] = 0.0
    # This would normally come from HR data
    
    # ===== COMBINE SCORES =====
    
    # ML Risk (already 0-100 from ensemble)
    df['ml_risk_score'] = df['ensemble_anomaly_score'].fillna(0)
    
    # Business Risk Score (normalize all to 0-100 then average)
    business_scores = df[[
        'sales_risk_score', 'crm_risk_score', 'hcp_coverage_risk_score',
        'vacancy_risk_score', 'long_vacancy_risk'
    ]]
    df['business_risk_score'] = business_scores.mean(axis=1)
    
    # Final Risk Score (weighted combination)
    df['final_risk_score'] = (
        df['ml_risk_score'] * RISK_WEIGHTS['ml_risk'] +
        df['sales_risk_score'] * RISK_WEIGHTS['sales_risk'] +
        df['crm_risk_score'] * RISK_WEIGHTS['crm_risk'] +
        df['hcp_coverage_risk_score'] * RISK_WEIGHTS['hcp_coverage_risk'] +
        df['vacancy_risk_score'] * RISK_WEIGHTS['vacancy_risk'] +
        df['long_vacancy_risk'] * RISK_WEIGHTS['long_vacancy_risk']
    )
    
    # Ensure scores are 0-100
    df['final_risk_score'] = df['final_risk_score'].clip(0, 100)
    
    # ===== SEVERITY CLASSIFICATION =====
    def get_severity(score):
        for severity, (low, high) in SEVERITY_RANGES.items():
            if low <= score < high:
                return severity
        return 'Critical' if score >= SEVERITY_RANGES['Critical'][0] else 'Minor'
    
    df['severity'] = df['final_risk_score'].apply(get_severity)
    
    return df


def generate_explanations(risk_df):
    """
    Generate business-friendly explanations for risk scores
    """
    explanations = []
    
    for _, row in risk_df.iterrows():
        reasons = []
        
        # Sales decline
        if row['sales_change_pct'] < THRESHOLDS['sales_decline']['warning']:
            pct_change = row['sales_change_pct']
            reasons.append(f"Sales declined {abs(pct_change):.1f}% vs previous month")
        
        # Vacancies
        if row['vacancies'] > 0:
            reasons.append(f"{int(row['vacancies'])} rep vacancy/vacancies")
        
        # Low CRM activity
        if row['avg_activity'] < THRESHOLDS['crm_activity']['warning']:
            reasons.append(f"CRM activity at {row['avg_activity']:.0f}% (below {THRESHOLDS['crm_activity']['warning']}%)")
        
        # Low HCP coverage
        if row['avg_hcp_coverage'] < THRESHOLDS['hcp_coverage']['warning']:
            reasons.append(f"HCP coverage {row['avg_hcp_coverage']:.0f}% (below {THRESHOLDS['hcp_coverage']['warning']}%)")
        
        # Anomaly detection
        if row['if_anomaly'] == 1:
            reasons.append(f"Isolation Forest detected unusual pattern (score: {row['isolation_forest_score']:.0f})")
        if row['lof_anomaly'] == 1:
            reasons.append(f"Local outlier pattern identified (score: {row['lof_score']:.0f})")
        
        if reasons:
            risk_reasons = "; ".join(reasons)
        else:
            risk_reasons = "Normal territory performance"
        
        explanations.append(risk_reasons)
    
    risk_df['risk_reasons'] = explanations
    
    # Generate recommendations
    recommendations = []
    for _, row in risk_df.iterrows():
        if row['severity'] == 'Critical':
            rec = "Immediate management intervention required. Review sales, staffing, and CRM engagement urgently."
        elif row['severity'] == 'Major':
            rec = "Conduct detailed territory review. Address key risk factors: sales, coverage, or staffing."
        else:
            rec = "Continue routine monitoring. Minor risks detected; no urgent action needed."
        
        recommendations.append(rec)
    
    risk_df['ai_recommendation'] = recommendations
    
    return risk_df


def run_complete_pipeline():
    """
    Run the entire pipeline from raw data to final risk output
    """
    print("\n" + "="*80)
    print("REPSENSE AI - COMPLETE PIPELINE")
    print("="*80)
    
    # Step 1: Load and clean pharma data
    print("\n[1/7] Loading and cleaning pharma sales data...")
    raw_df = pd.read_csv('pharma-data.csv')
    cleaned_df = clean_pharma_data(raw_df)
    print(f"     ✓ Cleaned data: {cleaned_df.shape[0]:,} rows, {cleaned_df.shape[1]} columns")
    cleaned_df.to_csv('pharma_sales_cleaned.csv', index=False)
    
    # Step 2: Generate synthetic HR data
    print("\n[2/7] Generating synthetic HR/vacancy data...")
    hr_df, hr_territories = generate_synthetic_hr_data(cleaned_df)
    print(f"     ✓ HR master: {len(hr_df)} reps")
    print(f"     ✓ Territory stats: {len(hr_territories)} territories")
    hr_df.to_csv('rep_master_hr.csv', index=False)
    
    # Step 3: Generate monthly features from sales data
    print("\n[3/7] Creating monthly territory analysis...")
    territory_monthly = create_monthly_territory_summary(cleaned_df)
    print(f"     ✓ Territory-monthly records: {len(territory_monthly)}")
    
    # Use the actual date range from sales data for consistency
    date_range = (territory_monthly['date'].min(), territory_monthly['date'].max())
    print(f"     ✓ Date range: {date_range[0]} to {date_range[1]}")
    
    # Step 4: Generate CRM data
    print("\n[4/7] Generating synthetic CRM activity data...")
    crm_daily, crm_monthly = generate_synthetic_crm_data(cleaned_df, date_range)
    print(f"     ✓ CRM monthly: {len(crm_monthly):,} records")
    crm_daily.to_csv('crm_activity_detail.csv', index=False)
    
    # Step 5: Generate promotion data
    print("\n[5/7] Generating synthetic promotional activity data...")
    promo_df = generate_synthetic_promotion_data(cleaned_df, date_range)
    print(f"     ✓ Promotions: {len(promo_df):,} records")
    promo_df.to_csv('promotional_activity.csv', index=False)
    
    # Step 6: Engineer features
    print("\n[6/7] Engineering comprehensive features...")
    features = engineer_features(territory_monthly, crm_monthly, promo_df, hr_territories)
    print(f"     ✓ Feature table: {features.shape[0]} territory-months, {features.shape[1]} features")
    
    # Step 7: Anomaly detection
    print("\n[7/7] Performing anomaly detection (Isolation Forest + LOF)...")
    features = detect_anomalies(features)
    print(f"     ✓ IF scores range: {features['isolation_forest_score'].min():.1f}-{features['isolation_forest_score'].max():.1f}")
    print(f"     ✓ LOF scores range: {features['lof_score'].min():.1f}-{features['lof_score'].max():.1f}")
    print(f"     ✓ Ensemble scores range: {features['ensemble_anomaly_score'].min():.1f}-{features['ensemble_anomaly_score'].max():.1f}")
    
    # Step 8: Risk scoring and explanations
    print("\n[8/8] Computing risk scores and generating explanations...")
    output_df = compute_risk_scores(features)
    output_df = generate_explanations(output_df)
    
    # Print severity distribution
    print("\n     Severity Distribution:")
    for sev, count in output_df['severity'].value_counts().items():
        print(f"       - {sev}: {count} ({100*count/len(output_df):.1f}%)")
    
    # Save outputs
    output_df.to_csv('AI_rep_management_output.csv', index=False)
    print(f"\n     ✓ Saved: AI_rep_management_output.csv ({len(output_df):,} rows)")
    
    # Create critical territories list
    critical_df = output_df[output_df['severity'] == 'Critical'].copy()
    critical_df.to_csv('critical_territories.csv', index=False)
    print(f"     ✓ Saved: critical_territories.csv ({len(critical_df)} critical territories)")
    
    # Create major territories list
    major_df = output_df[output_df['severity'] == 'Major'].copy()
    print(f"     ✓ Major territories: {len(major_df)}")
    
    # Create executive summary
    exec_summary = output_df.groupby('date').agg({
        'sales': 'sum',
        'territory_id': 'count',
        'final_risk_score': 'mean',
        'vacancies': 'sum',
        'severity': lambda x: (x == 'Critical').sum(),
    }).reset_index()
    exec_summary.columns = ['date', 'total_sales', 'territory_count', 'avg_risk_score', 'total_vacancies', 'critical_count']
    exec_summary.to_csv('executive_dashboard.csv', index=False)
    print(f"     ✓ Saved: executive_dashboard.csv ({len(exec_summary)} dates)")
    
    print("\n" + "="*80)
    print("PIPELINE COMPLETE ✓")
    print("="*80)
    
    return output_df


if __name__ == '__main__':
    output_df = run_complete_pipeline()
