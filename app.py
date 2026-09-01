"""
RepSense AI - Professional Streamlit Application
Complete Pages for Territory Risk Management
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="RepSense AI - Territory Risk Management",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_col(df, *possible_names):
    """Find first matching column name (case-insensitive)"""
    for name in possible_names:
        for col in df.columns:
            if col.lower() == name.lower():
                return col
    return None

def safe_get(row, *possible_names, default=0):
    """Safely get a value from row with multiple possible column names"""
    for name in possible_names:
        if name in row.index:
            val = row[name]
            return val if pd.notna(val) else default
    return default

# ============================================================================
# DATA LOADING & CACHING
# ============================================================================

@st.cache_data
def load_all_data():
    """Load all required CSV files"""
    try:
        ai_output = pd.read_csv('AI_rep_management_output.csv')
        
        hr_master = pd.read_csv('rep_master_hr.csv')
        
        try:
            crm_analysis = pd.read_csv('crm_monthly_analysis.csv')
        except:
            crm_analysis = pd.DataFrame()
        
        try:
            promo_activity = pd.read_csv('promotional_activity.csv')
        except:
            promo_activity = pd.DataFrame()
        
        return {
            'ai_output': ai_output,
            'hr_master': hr_master,
            'crm_analysis': crm_analysis,
            'promo_activity': promo_activity,
        }
    except FileNotFoundError as e:
        st.error(f"Missing required data file: {str(e)}")
        st.stop()

# Load data
data = load_all_data()
ai_df = data['ai_output']
hr_df = data['hr_master']
crm_df = data['crm_analysis']
promo_df = data['promo_activity']

# Normalize to ensure we have standard column names
date_col = get_col(ai_df, 'date')
territory_col = get_col(ai_df, 'territory_id')
severity_col = get_col(ai_df, 'severity')
risk_col = get_col(ai_df, 'final_risk_score')
sales_col = get_col(ai_df, 'sales')

# ============================================================================
# SIDEBAR & NAVIGATION
# ============================================================================

st.sidebar.title("🎯 RepSense AI")
st.sidebar.markdown("---")

# Date filter
if date_col and len(ai_df) > 0:
    available_dates = sorted(ai_df[date_col].dropna().unique())
    if len(available_dates) > 0:
        selected_date = st.sidebar.selectbox(
            "📅 Analysis Date",
            available_dates,
            index=len(available_dates) - 1
        )
    else:
        selected_date = None
else:
    selected_date = None

# Severity filter
if severity_col:
    available_severities = sorted(ai_df[severity_col].dropna().unique().tolist())
    selected_severities = st.sidebar.multiselect(
        "⚠️ Risk Level",
        available_severities,
        default=available_severities
    )
else:
    selected_severities = []

# Get filtered data
if selected_date and date_col:
    latest_data = ai_df[ai_df[date_col] == selected_date].copy()
else:
    latest_data = ai_df.copy()

if severity_col and len(selected_severities) > 0:
    filtered_data = latest_data[latest_data[severity_col].isin(selected_severities)].copy()
else:
    filtered_data = latest_data.copy()

# ============================================================================
# PAGE SELECTION
# ============================================================================

page = st.sidebar.radio(
    "📑 Navigate",
    [
        "🏢 Executive Dashboard",
        "🤖 AI Risk Monitor",
        "🔍 Territory Deep Dive",
        "👤 Rep Management",
        "📢 Promotion Analytics",
        "💬 AI Assistant"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("RepSense AI v1.0 | Hackathon Edition")

# ============================================================================
# HEADER
# ============================================================================

st.title("📊 RepSense AI")
st.markdown("**AI-Powered Territory Risk Intelligence Platform**")

# Executive metrics
if len(latest_data) > 0:
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        sales_total = latest_data[sales_col].sum() if sales_col else 0
        st.metric("💰 Total Sales", f"${sales_total:,.0f}")
    
    with col2:
        st.metric("👥 Reps", len(hr_df))
    
    with col3:
        vac_col = get_col(latest_data, 'vacancies')
        vacancies = latest_data[vac_col].sum() if vac_col else 0
        st.metric("🔴 Vacancies", int(vacancies))
    
    with col4:
        critical_count = (latest_data[severity_col] == 'Critical').sum() if severity_col else 0
        st.metric("🚨 Critical", critical_count)
    
    with col5:
        avg_risk = latest_data[risk_col].mean() if risk_col else 0
        st.metric("📈 Avg Risk", f"{avg_risk:.0f}/100")

st.divider()

# ============================================================================
# PAGE 1: EXECUTIVE DASHBOARD
# ============================================================================

if page == "🏢 Executive Dashboard":
    st.header("Executive Dashboard")
    st.markdown("High-level KPIs, trends, and territory health overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if severity_col and len(latest_data) > 0:
            risk_dist = latest_data[severity_col].value_counts()
            fig = px.pie(
                values=risk_dist.values,
                names=risk_dist.index,
                title="Risk Distribution",
                color_discrete_map={'Critical': '#d32f2f', 'Major': '#f57c00', 'Minor': '#388e3c'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if risk_col and territory_col and len(latest_data) > 0:
            top_risk = latest_data.nlargest(10, risk_col)[[territory_col, risk_col]].copy()
            fig = px.bar(
                top_risk,
                y=territory_col,
                x=risk_col,
                orientation='h',
                title="Top 10 Risk Territories",
                color=risk_col,
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Trends
    if len(ai_df) > 1 and date_col:
        st.subheader("📈 Monthly Trends")
        trend_data = ai_df.groupby(date_col).agg({
            sales_col: 'sum' if sales_col else None,
            get_col(ai_df, 'vacancies'): 'sum',
            risk_col: 'mean'
        }).reset_index().sort_values(date_col)
        
        trend_data = trend_data.dropna(how='all', axis=1)
        
        cols = st.columns(3)
        
        if sales_col:
            with cols[0]:
                fig = px.line(trend_data, x=date_col, y=sales_col, markers=True, title="Sales Trend")
                st.plotly_chart(fig, use_container_width=True)
        
        vac_col = get_col(ai_df, 'vacancies')
        if vac_col:
            with cols[1]:
                fig = px.bar(trend_data, x=date_col, y=vac_col, title="Vacancies", color_discrete_sequence=['#d32f2f'])
                st.plotly_chart(fig, use_container_width=True)
        
        if risk_col:
            with cols[2]:
                fig = px.line(trend_data, x=date_col, y=risk_col, markers=True, title="Avg Risk Score")
                st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# PAGE 2: AI RISK MONITOR
# ============================================================================

elif page == "🤖 AI Risk Monitor":
    st.header("🤖 AI Risk Monitor")
    st.markdown("Isolation Forest + Local Outlier Factor Anomaly Detection")
    
    if len(filtered_data) > 0:
        # Data table
        display_cols = [territory_col, sales_col, 
                       get_col(filtered_data, 'sales_change_pct'),
                       get_col(filtered_data, 'vacancies'),
                       get_col(filtered_data, 'avg_activity'),
                       get_col(filtered_data, 'avg_hcp_coverage'),
                       risk_col, severity_col]
        display_cols = [c for c in display_cols if c is not None]
        
        st.subheader("Territory Risk Scores")
        if display_cols:
            st.dataframe(
                filtered_data[display_cols].sort_values(risk_col, ascending=False) if risk_col else filtered_data[display_cols],
                use_container_width=True,
                hide_index=True
            )
        
        # Critical alerts
        if severity_col:
            critical = filtered_data[filtered_data[severity_col] == 'Critical']
            if len(critical) > 0:
                st.subheader("🚨 Critical Alerts")
                for _, row in critical.iterrows():
                    with st.container(border=True):
                        terr = safe_get(row, territory_col, default='Unknown')
                        risk_score = safe_get(row, risk_col, default=0)
                        reasons = safe_get(row, 'risk_reasons', 'ai_recommendation', default='N/A')
                        rec = safe_get(row, 'ai_recommendation', default='Review immediately')
                        
                        st.markdown(f"### 🔴 {terr}")
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.markdown(f"**Risk Score:** {risk_score:.1f}/100")
                            st.markdown(f"**Reasons:** {reasons}")
                        with col2:
                            st.markdown(f"**Recommendation:**  \n{rec}")

# ============================================================================
# PAGE 3: TERRITORY DEEP DIVE
# ============================================================================

elif page == "🔍 Territory Deep Dive":
    st.header("🔍 Territory Investigation")
    
    if territory_col and len(ai_df) > 0:
        territories = sorted(ai_df[territory_col].dropna().unique())
        selected_territory = st.selectbox("Select Territory", territories)
        
        territory_data = ai_df[ai_df[territory_col] == selected_territory].copy()
        if date_col:
            territory_data = territory_data.sort_values(date_col)
        
        if len(territory_data) > 0:
            latest = territory_data.iloc[-1]
            
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                sales_val = safe_get(latest, sales_col, default=0)
                st.metric("Sales", f"${sales_val:,.0f}")
            with col2:
                sales_pct = safe_get(latest, 'sales_change_pct', default=0)
                st.metric("Sales %", f"{sales_pct:.1f}%")
            with col3:
                vac = safe_get(latest, 'vacancies', default=0)
                st.metric("Vacancies", int(vac))
            with col4:
                activity = safe_get(latest, 'avg_activity', default=0)
                st.metric("CRM %", f"{activity:.0f}%")
            with col5:
                risk = safe_get(latest, risk_col, default=0)
                st.metric("Risk Score", f"{risk:.0f}")
            
            st.divider()
            
            # Status badge
            if severity_col:
                severity = safe_get(latest, severity_col, default='Minor')
                col1, col2 = st.columns([1, 3])
                with col1:
                    severity_emoji = {'Critical': '🔴', 'Major': '🟠', 'Minor': '🟢'}
                    st.markdown(f"## {severity_emoji.get(str(severity), '🟡')} {severity}")
            
            reasons = safe_get(latest, 'risk_reasons', default='N/A')
            rec = safe_get(latest, 'ai_recommendation', default='Monitor closely')
            st.markdown(f"**Risk Reasons:**  \n{reasons}")
            st.markdown(f"**Recommendation:**  \n{rec}")
            
            st.divider()
            
            # Time series
            col1, col2 = st.columns(2)
            with col1:
                if sales_col and date_col:
                    fig = px.line(territory_data, x=date_col, y=sales_col, markers=True, title=f"Sales - {selected_territory}")
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if risk_col and date_col:
                    fig = px.line(territory_data, x=date_col, y=risk_col, markers=True, title="Risk Score", color_discrete_sequence=['#d32f2f'])
                    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# PAGE 4: REP MANAGEMENT
# ============================================================================

elif page == "👤 Rep Management":
    st.header("👤 Sales Rep Management")
    
    st.subheader("Rep Directory")
    if len(hr_df) > 0:
        st.dataframe(hr_df, use_container_width=True, hide_index=True)
    
    st.subheader("Rep Statistics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Reps", len(hr_df))
    with col2:
        emp_status_col = get_col(hr_df, 'employment_status')
        active = (hr_df[emp_status_col] == 'Active').sum() if emp_status_col else len(hr_df)
        st.metric("Active", active)
    with col3:
        vacant = (hr_df[emp_status_col] == 'Vacant').sum() if emp_status_col else 0
        st.metric("Vacancies", vacant)
    with col4:
        team_col = get_col(hr_df, 'sales_team')
        teams = hr_df[team_col].nunique() if team_col else 0
        st.metric("Teams", teams)

# ============================================================================
# PAGE 5: PROMOTION ANALYTICS
# ============================================================================

elif page == "📢 Promotion Analytics":
    st.header("📢 Promotional Activity Analytics")
    
    if len(promo_df) > 0:
        uplift_col = get_col(promo_df, 'sales_uplift', 'sales_uplift_%')
        impact_col = get_col(promo_df, 'promotion_impact')
        type_col = get_col(promo_df, 'promotion_type')
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Promotions", len(promo_df))
        with col2:
            avg_uplift = promo_df[uplift_col].mean() if uplift_col else 0
            st.metric("Avg Uplift", f"{avg_uplift:.1f}%")
        with col3:
            high = (promo_df[impact_col] == 'High Impact').sum() if impact_col else 0
            st.metric("High Impact", high)
        
        st.divider()
        
        if type_col and uplift_col:
            by_type = promo_df.groupby(type_col, as_index=False).agg(
                Avg_Uplift=(uplift_col, 'mean'),
                Count=(uplift_col, 'size'),
            )
            fig = px.bar(by_type, x=type_col, y='Avg_Uplift', title="Uplift by Type", color='Avg_Uplift', color_continuous_scale='Greens')
            st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Promotion Details")
        st.dataframe(promo_df.head(20), use_container_width=True, hide_index=True)
    else:
        st.info("No promotional data available")

# ============================================================================
# PAGE 6: AI ASSISTANT
# ============================================================================

elif page == "💬 AI Assistant":
    st.header("💬 AI Territory Assistant")
    st.markdown("Ask questions about your territory data")
    
    question = st.text_input("Your Question:", placeholder="Which territories are at highest risk?")
    
    if question:
        q = question.lower()
        
        if any(w in q for w in ['highest', 'top', 'critical', 'risk']):
            st.subheader("🔴 Highest Risk Territories")
            if risk_col and len(latest_data) > 0:
                top = latest_data.nlargest(5, risk_col)
                for _, row in top.iterrows():
                    terr = safe_get(row, territory_col, default='Unknown')
                    risk = safe_get(row, risk_col, default=0)
                    sev = safe_get(row, severity_col, default='Minor')
                    reasons = safe_get(row, 'risk_reasons', default='N/A')
                    st.warning(f"**{terr}** ({risk:.0f}/100) - {sev}\n{reasons}")
        
        elif any(w in q for w in ['vacancy', 'vacant', 'staffing']):
            st.subheader("🔴 Vacancies")
            vac_col = get_col(latest_data, 'vacancies')
            if vac_col:
                with_vac = latest_data[latest_data[vac_col] > 0].sort_values(vac_col, ascending=False)
                if len(with_vac) > 0:
                    vacancy_days_col = get_col(with_vac, 'max_vacancy_days')
                    vacancy_cols = [territory_col, vac_col]
                    if vacancy_days_col:
                        vacancy_cols.append(vacancy_days_col)
                    st.dataframe(with_vac[vacancy_cols], use_container_width=True)
                else:
                    st.success("✅ No vacancies")
        
        elif any(w in q for w in ['sales', 'decline', 'down', 'drop']):
            st.subheader("📉 Sales Declines")
            sales_change = get_col(latest_data, 'sales_change_pct')
            if sales_change:
                decline = latest_data[latest_data[sales_change] < -15].sort_values(sales_change)
                if len(decline) > 0:
                    st.dataframe(decline[[territory_col, sales_col, sales_change]].dropna(axis=1), use_container_width=True)
                else:
                    st.success("✅ No major sales declines")
        
        else:
            st.info("Try asking about: highest risk, vacancies, sales, or CRM activity")
