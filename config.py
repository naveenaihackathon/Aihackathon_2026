"""
RepSense AI - Configuration and Constants
Centralized configuration for all thresholds and business rules
"""

# ============================================================================
# BUSINESS RULE THRESHOLDS (CONFIGURABLE)
# ============================================================================
# These thresholds are DEMO VALUES and should be adjusted based on actual business logic

THRESHOLDS = {
    'sales_decline': {
        'warning': -15,      # -15% = warning
        'major': -30,        # -30% = major
        'critical': -40,     # -40% = critical
    },
    'crm_activity': {
        'warning': 80,       # Below 80% = warning
        'major': 60,         # Below 60% = major
        'critical': 50,      # Below 50% = critical
    },
    'hcp_coverage': {
        'warning': 85,       # Below 85% = warning
        'major': 70,         # Below 70% = major
        'critical': 50,      # Below 50% = critical
    },
    'vacancy': {
        'warning_days': 30,      # 30+ days = warning
        'major_days': 60,        # 60+ days = major
        'critical_days': 90,     # 90+ days = critical
    },
}

# ============================================================================
# ANOMALY DETECTION CONFIGURATION
# ============================================================================

ANOMALY_CONFIG = {
    'isolation_forest': {
        'contamination': 0.05,  # 5% of records are expected anomalies
        'random_state': 42,
        'weight': 0.60,  # 60% weight in ensemble
    },
    'lof': {
        'n_neighbors': 20,
        'contamination': 0.05,
        'random_state': 42,
        'weight': 0.40,  # 40% weight in ensemble
    }
}

# ============================================================================
# RISK SCORING WEIGHTS
# ============================================================================
# How to combine different risk factors

RISK_WEIGHTS = {
    'ml_risk': 0.35,              # Anomaly detection score
    'sales_risk': 0.25,           # Sales decline risk
    'crm_risk': 0.15,             # CRM activity risk
    'hcp_coverage_risk': 0.10,    # HCP coverage risk
    'vacancy_risk': 0.10,         # Vacancy risk
    'long_vacancy_risk': 0.05,    # Long duration vacancy risk
}

# Severity mapping
SEVERITY_RANGES = {
    'Critical': (70, 100),   # 70-100 = Critical
    'Major': (40, 70),       # 40-70 = Major
    'Minor': (0, 40),        # 0-40 = Minor
}

# ============================================================================
# DATA GENERATION CONFIGURATION
# ============================================================================

SYNTHETIC_DATA_SEED = 42  # For reproducible synthetic data

# Territories to create (demo)
TERRITORIES = [
    'TERR_01', 'TERR_02', 'TERR_03', 'TERR_04', 'TERR_05',
    'TERR_06', 'TERR_07', 'TERR_08'
]

# CRM activity variation ranges
CRM_ACTIVITY_RANGE = (50, 100)  # 50%-100%
HCP_COVERAGE_RANGE = (40, 100)  # 40%-100%

# ============================================================================
# APP CONFIGURATION
# ============================================================================

STREAMLIT_CONFIG = {
    'page_title': 'RepSense AI - Sales Rep Management Platform',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded',
}

# Display formats
NUMBER_FORMAT = '{:,.0f}'
PERCENT_FORMAT = '{:.1f}%'
DECIMAL_FORMAT = '{:.2f}'
