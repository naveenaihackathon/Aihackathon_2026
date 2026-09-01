"""
RepSense AI - Professional Streamlit Application
AI-Powered Sales Rep & Territory Risk Management Platform
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="RepSense AI - Territory Risk Management",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM STYLING
# ============================================================================

st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .critical-box {
        background-color: #ffebee;
        padding: 15px;
        border-left: 4px solid #d32f2f;
        border-radius: 5px;
        margin: 10px 0;
    }
    .major-box {
        background-color: #fff3e0;
        padding: 15px;
        border-left: 4px solid #f57c00;
        border-radius: 5px;
        margin: 10px 0;
    }
    .minor-box {
        background-color: #e8f5e9;
        padding: 15px;
        border-left: 4px solid #388e3c;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA LOADING & CACHING
# ============================================================================

@st.cache_data
def load_all_data():
    """Load all required CSV files"""
    try:
        # Main AI output
        ai_output = pd.read_csv('AI_rep_management_output.csv')
        ai_output['Date'] = pd.to_datetime(ai_output['Date'], errors='coerce')
        
        # HR Master
        hr_master = pd.read_csv('rep_master_hr.csv')
        
        # Territory HR Analysis
        territory_hr = pd.read_csv('territory_hr_analysis.csv')
        
        # CRM Analysis
        crm_analysis = pd.read_csv('crm_monthly_analysis.csv')
        crm_analysis['Date'] = pd.to_datetime(crm_analysis['Date'], errors='coerce')
        
        # Promotional Activity
        promo_activity = pd.read_csv('promotional_activity.csv')
        promo_activity['Date'] = pd.to_datetime(promo_activity['Date'], errors='coerce')
        
        # Executive Dashboard
        exec_dashboard = pd.read_csv('executive_dashboard.csv')
        exec_dashboard['Date'] = pd.to_datetime(exec_dashboard['Date'], errors='coerce')
        
        return {
            'ai_output': ai_output,
            'hr_master': hr_master,
            'territory_hr': territory_hr,
            'crm_analysis': crm_analysis,
            'promo_activity': promo_activity,
            'exec_dashboard': exec_dashboard
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
exec_df = data['exec_dashboard']

# ============================================================================
# SIDEBAR & FILTERS
# ============================================================================

st.sidebar.title("🎯 RepSense AI")
st.sidebar.markdown("---")

# Date filter
available_dates = sorted(ai_df['Date'].dropna().unique())
if len(available_dates) > 0:
    selected_date = st.sidebar.selectbox(
        "📅 Select Analysis Date",
        available_dates,
        index=len(available_dates) - 1 if len(available_dates) > 0 else 0
    )
else:
    selected_date = None

# Filter by severity
selected_severities = st.sidebar.multiselect(
    "⚠️ Filter by Risk Level",
    ['Critical', 'Major', 'Minor'],
    default=['Critical', 'Major', 'Minor']
)

# Get filtered data
if selected_date:
    latest_data = ai_df[ai_df['Date'] == selected_date].copy()
else:
    latest_data = ai_df.copy()

filtered_data = latest_data[latest_data['Severity'].isin(selected_severities)].copy()

# ============================================================================
# MAIN HEADER & EXECUTIVE METRICS
# ============================================================================

col1, col2, col3 = st.columns([2, 3, 1])

with col1:
    st.title("📊 RepSense AI")
    st.markdown("**AI-Powered Territory Risk Intelligence**")

with col3:
    if selected_date:
        st.metric("📅 Analysis Date", selected_date.strftime('%b %Y'))

st.markdown("---")

# Executive Overview Metrics
if len(latest_data) > 0:
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_sales = latest_data['Sales'].sum() if 'Sales' in latest_data.columns else 0
        st.metric(
            "💰 Total Sales",
            f"${total_sales:,.0f}" if total_sales > 0 else "N/A"
        )
    
    with col2:
        total_reps = len(hr_df)
        st.metric("👥 Sales Reps", total_reps)
    
    with col3:
        total_vacancies = latest_data['Vacancies'].sum() if 'Vacancies' in latest_data.columns else 0
        st.metric("🔴 Vacancies", int(total_vacancies))
    
    with col4:
        critical_count = (latest_data['Severity'] == 'Critical').sum()
        st.metric("🚨 Critical", critical_count, delta=None)
    
    with col5:
        avg_risk = latest_data['Final_Risk_Score'].mean() if 'Final_Risk_Score' in latest_data.columns else 0
        st.metric("📈 Avg Risk", f"{avg_risk:.1f}/100")

st.markdown("---")

# ============================================================================
# PAGE NAVIGATION
# ============================================================================

page = st.sidebar.radio(
    "📑 Navigate to",
    [
        "🏢 Executive Dashboard",
        "🤖 AI Risk Monitor",
        "🔍 Territory Deep Dive",
        "👤 Rep Management",
        "📢 Promotion Analytics",
        "💬 AI Assistant"
    ]
)
)

st.divider()


page = st.sidebar.radio(
    "Navigate",
    [
        "Executive Dashboard",
        "AI Risk Monitor",
        "Territory Investigation",
        "Promotion Analytics",
        "AI Assistant"
    ]
)

if page == "Executive Dashboard":

    st.header("Executive Dashboard")

    col1, col2 = st.columns(2)


    with col1:

        risk_counts = (
            latest_data["Severity"]
            .value_counts()
            .reset_index()
        )

        risk_counts.columns = [
            "Severity",
            "Count"
        ]

        fig = px.bar(
            risk_counts,
            x="Severity",
            y="Count",
            title="Territory Risk Distribution"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    with col2:

        risk_plot = latest_data.sort_values(
            "Final_Risk_Score",
            ascending=False
        )

        fig = px.bar(
            risk_plot,
            x="Territory_ID",
            y="Final_Risk_Score",
            title="AI Risk Score by Territory"
        )

        fig.update_layout(
            xaxis_tickangle=-45
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.subheader("Overall Sales Trend")

    sales_trend = (
        ai_df
        .groupby("Date")
        .agg(
            Sales=("Sales", "sum")
        )
        .reset_index()
    )

    fig = px.line(
        sales_trend,
        x="Date",
        y="Sales",
        markers=True,
        title="Monthly Sales Trend"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

  
    st.subheader("CRM Activity Trend")

    crm_trend = (
        ai_df
        .groupby("Date")
        .agg(
            CRM_Activity=("Avg_Activity", "mean")
        )
        .reset_index()
    )

    fig = px.line(
        crm_trend,
        x="Date",
        y="CRM_Activity",
        markers=True,
        title="Average CRM Activity"
    )

    fig.update_yaxes(
        title="Activity %"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

elif page == "AI Risk Monitor":

    st.header("🤖 AI Risk Monitor")

    st.markdown(
        """
        **Isolation Forest** detects unusual territory behavior.
        Business rules then add context from sales, vacancies,
        CRM activity and HCP coverage.
        """
    )

    
    display_columns = [
        "Territory_ID",
        "Sales",
        "Sales_Change_Pct",
        "Vacancies",
        "Max_Vacancy_Days",
        "Avg_Activity",
        "Avg_HCP_Coverage",
        "Anomaly_Score",
        "Final_Risk_Score",
        "Severity"
    ]

    display_df = filtered_data[
        display_columns
    ].copy()

    st.dataframe(
        display_df.sort_values(
            "Final_Risk_Score",
            ascending=False
        ),
        use_container_width=True,
        hide_index=True
    )


    st.subheader("🚨 Critical Alerts")

    critical = filtered_data[
        filtered_data["Severity"] == "Critical"
    ]

    if len(critical) == 0:

        st.success(
            "No critical territories detected for this month."
        )

    else:

        for _, row in critical.iterrows():

            st.error(
                f"""
                **{row['Territory_ID']}**

                Risk Score: {row['Final_Risk_Score']:.1f}

                {row['Risk_Reasons']}

                **Recommended Action:**
                {row['AI_Recommendation']}
                """
            )

elif page == "Territory Investigation":

    st.header("🔎 Territory Investigation")

    territories = sorted(
        ai_df["Territory_ID"]
        .dropna()
        .unique()
    )

    selected_territory = st.selectbox(
        "Select Territory",
        territories
    )

    territory_history = ai_df[
        ai_df["Territory_ID"] ==
        selected_territory
    ].sort_values("Date")

    current = territory_history[
        territory_history["Date"] ==
        selected_date
    ]

    if len(current) == 0:

        st.warning(
            "No data available for the selected month."
        )

    else:

        row = current.iloc[0]


        c1, c2, c3, c4, c5 = st.columns(5)

        c1.metric(
            "Sales",
            f"{row['Sales']:,.0f}"
        )

        c2.metric(
            "Sales Change",
            f"{row['Sales_Change_Pct']:.1f}%"
        )

        c3.metric(
            "Vacancies",
            int(row["Vacancies"])
        )

        c4.metric(
            "CRM Activity",
            f"{row['Avg_Activity']:.1f}%"
        )

        c5.metric(
            "Risk Score",
            f"{row['Final_Risk_Score']:.1f}"
        )

        st.divider()


        if row["Severity"] == "Critical":

            st.error(
                f"🔴 CRITICAL — {selected_territory}"
            )

        elif row["Severity"] == "Major":

            st.warning(
                f"🟠 MAJOR — {selected_territory}"
            )

        else:

            st.success(
                f"🟢 MINOR — {selected_territory}"
            )


        st.subheader("Why was this territory flagged?")

        st.info(
            row["Risk_Reasons"]
        )

       

        st.subheader("Recommended Action")

        st.success(
            row["AI_Recommendation"]
        )


        st.subheader("Sales Trend")

        fig = px.line(
            territory_history,
            x="Date",
            y="Sales",
            markers=True
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        

        st.subheader("CRM Activity")

        fig = px.line(
            territory_history,
            x="Date",
            y="Avg_Activity",
            markers=True
        )

        fig.update_yaxes(
            title="Activity %"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

 

        st.subheader("HCP Coverage")

        fig = px.line(
            territory_history,
            x="Date",
            y="Avg_HCP_Coverage",
            markers=True
        )

        fig.update_yaxes(
            title="Coverage %"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


elif page == "Promotion Analytics":

    st.header("📢 Promotional Activity Analytics")

    if len(promotion_df) == 0:

        st.warning(
            "No promotional data available."
        )

    else:

 
        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Promotional Activities",
            len(promotion_df)
        )

        avg_uplift = promotion_df[
            "Sales_Uplift_%"
        ].mean()

        high_impact = (
            promotion_df[
                "Promotion_Impact"
            ] == "High Impact"
        ).sum()

        c2.metric(
            "Avg Sales Uplift",
            f"{avg_uplift:.1f}%"
        )

        c3.metric(
            "High Impact Activities",
            int(high_impact)
        )

      
        promotion_type = (
            promotion_df
            .groupby("Promotion_Type")
            .agg(
                Activities=(
                    "Promotion_Type",
                    "count"
                ),
                Avg_Uplift=(
                    "Sales_Uplift_%",
                    "mean"
                )
            )
            .reset_index()
        )

        fig = px.bar(
            promotion_type,
            x="Promotion_Type",
            y="Avg_Uplift",
            title="Average Sales Uplift by Promotion Type"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

 

        product_impact = (
            promotion_df
            .groupby("Product_Name")
            .agg(
                Activities=(
                    "Product_Name",
                    "count"
                ),
                Avg_Uplift=(
                    "Sales_Uplift_%",
                    "mean"
                )
            )
            .reset_index()
            .sort_values(
                "Avg_Uplift",
                ascending=False
            )
            .head(15)
        )

        fig = px.bar(
            product_impact,
            x="Product_Name",
            y="Avg_Uplift",
            title="Top Products by Promotional Uplift"
        )

        fig.update_layout(
            xaxis_tickangle=-45
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )



        st.subheader("Promotional Activity Details")

        st.dataframe(
            promotion_df[
                [
                    "Date",
                    "Name_of_Sales_Rep",
                    "Territory_ID",
                    "HCP_ID",
                    "Product_Name",
                    "Promotion_Type",
                    "Sales_Before",
                    "Sales_After",
                    "Sales_Uplift_%",
                    "Promotion_Impact"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )


elif page == "AI Assistant":

    st.header("🤖 AI Territory Assistant")

    st.markdown(
        """
        Ask questions about the sales-force data.

        Examples:

        - Which territories are at highest risk?
        - Why is TERR_01 critical?
        - Which territories have vacancies and declining sales?
        - Which territories have low CRM activity?
        - What should the manager investigate first?
        """
    )

    question = st.text_area(
        "Ask the AI Assistant",
        placeholder="Why is this territory at risk?"
    )

    if st.button("Analyze"):

        if not question.strip():

            st.warning(
                "Please enter a question."
            )

        else:

            q = question.lower()

   

            if (
                "highest risk" in q
                or "high risk" in q
                or "critical" in q
            ):

                result = (
                    latest_data
                    .sort_values(
                        "Final_Risk_Score",
                        ascending=False
                    )
                    .head(5)
                )

                st.subheader(
                    "Highest Risk Territories"
                )

                for _, r in result.iterrows():

                    st.warning(
                        f"""
                        **{r['Territory_ID']}**
                        
                        Risk Score: {r['Final_Risk_Score']:.1f}

                        Severity: {r['Severity']}

                        {r['Risk_Reasons']}
                        """
                    )


            elif "vacancy" in q:

                result = latest_data[
                    latest_data["Vacancies"] > 0
                ].sort_values(
                    "Vacancies",
                    ascending=False
                )

                st.subheader(
                    "Territories With Vacancies"
                )

                st.dataframe(
                    result[
                        [
                            "Territory_ID",
                            "Vacancies",
                            "Max_Vacancy_Days",
                            "Sales_Change_Pct",
                            "Final_Risk_Score",
                            "Severity"
                        ]
                    ],
                    use_container_width=True,
                    hide_index=True
                )


            elif "crm" in q or "activity" in q:

                result = latest_data.sort_values(
                    "Avg_Activity"
                ).head(10)

                st.subheader(
                    "Lowest CRM Activity"
                )

                st.dataframe(
                    result[
                        [
                            "Territory_ID",
                            "Avg_Activity",
                            "Avg_HCP_Coverage",
                            "Sales_Change_Pct",
                            "Severity"
                        ]
                    ],
                    use_container_width=True,
                    hide_index=True
                )

            elif "sales" in q:

                result = latest_data.sort_values(
                    "Sales_Change_Pct"
                ).head(10)

                st.subheader(
                    "Largest Sales Declines"
                )

                st.dataframe(
                    result[
                        [
                            "Territory_ID",
                            "Sales",
                            "Sales_Change_Pct",
                            "Vacancies",
                            "Severity"
                        ]
                    ],
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.info(
                    """
                    I can currently analyze:

                    • Risk
                    • Vacancies
                    • Sales trends
                    • CRM activity
                    • HCP coverage

                    Try asking one of those questions.
                    """
                )


st.sidebar.divider()

st.sidebar.caption(
    "AI Rep Management Platform | Hackathon Prototype"
)

st.sidebar.caption(
    "Isolation Forest + Business Rules + Analytics"
)