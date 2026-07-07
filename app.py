import streamlit as st
import pandas as pd

# Import fungsi dari folder utils
from utils.ui import inject_css, set_plot_style, risk_level
from utils.loader import load_model, load_processed_data, load_raw_data, prepare_shap_data

# Import semua fungsi render dari folder pages
from pages.overview          import render as page_overview
from pages.shap_global       import render as page_shap
from pages.individual        import render as page_individual
from pages.risk_table        import render as page_risk_table
from pages.class_alert       import render as page_class_alert
from pages.rekomendasi_prodi import render as page_prodi

# ── CONFIG ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Student Risk Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_css()
set_plot_style()

# ── LOAD DATA — jalan sekali saja, simpan ke memory (session_state) ──
if 'model' not in st.session_state:
    with st.spinner("Loading model & data from PostgreSQL..."):
        model = load_model()
        
        # Load processed data dari PostgreSQL (untuk risk)
        risk_df_processed = load_processed_data()
        
        # Load raw data dari PostgreSQL (untuk SHAP)
        df_raw = load_raw_data()
        
        # Uppercase kolom untuk match training features
        df_raw.columns = df_raw.columns.str.upper()
        
        # Training features (aggregated)
        TRAINING_FEATURE_COLS = [
            'AVG_DAYS_BEFORE_DEADLINE',
            'PCT_SUBMISSION_H_MINUS_1',
            'PCT_LATE_SUBMISSION',
            'FD_RATIO',
            'DOWNLOAD_RATIO',
            'VBL_RATIO',
            'AVG_TLE',
            'COUNT_TLE_BELOW_3',
            'AVG_TP_AWAL',
            'AVG_TK_AWAL',
            'QUIZ1_SCORE',
            'AVG_LO1_AWAL',
            'TREND_TP',
            'TREND_TK',
            'EARLY_ACADEMIC_SCORE'
        ]
        
        X_test = df_raw[TRAINING_FEATURE_COLS].fillna(0)
        
        # SHAP
        import shap
        explainer = shap.TreeExplainer(model)
        shap_vals_risk = explainer.shap_values(X_test)[:, :, 1]
        
        # Siapkan session_state
        st.session_state.model = model
        st.session_state.risk_df = risk_df_processed
        st.session_state.X_test = X_test
        st.session_state.feature_cols = TRAINING_FEATURE_COLS
        st.session_state.explainer = explainer
        st.session_state.shap_vals_risk = shap_vals_risk
        
        # Dummy untuk pages yang expect ini
        st.session_state.y_test = risk_df_processed['risk_label'].values
        st.session_state.y_pred = (risk_df_processed['risk_probability'] >= 0.4).astype(int)
        st.session_state.threshold = 0.4

# ── SIDEBAR ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p style="font-family:\'DM Sans\',sans-serif;font-size:1.2rem;font-weight:700;color:#FFFFFF;margin:0;">🎓 Student Risk</p>', unsafe_allow_html=True)
    st.markdown('<p style="font-family:\'DM Sans\',sans-serif;font-size:0.82rem;font-weight:400;color:rgba(255,255,255,0.7);margin:0 0 0.5rem;">Interpretable ML Dashboard</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("### Navigation")
    page = st.radio("", [
        "📊 Overview",
        "🔍 SHAP Global",
        "👤 Individual Analysis",
        "📋 Risk Table",
        "🚨 Class Alert",
        "🏫 Rekomendasi Prodi"
    ], label_visibility="collapsed")

    st.markdown("---")
    st.markdown("### Settings")
    threshold = st.slider("Risk Threshold", 0.1, 0.9, 0.4, 0.05)
    st.session_state.threshold = threshold

    st.markdown("---")
    st.markdown(
        '<p style="font-size:0.75rem;color:#9CA3AF;">Model: Random Forest v2<br>Dataset: Binus Student<br>Features: 15</p>',
        unsafe_allow_html=True
    )


# Data dari PostgreSQL
# Data dari PostgreSQL, hanya kalkulasi Risk_Level berdasarkan threshold
risk_df = st.session_state.risk_df.copy()
y_pred = (risk_df['risk_probability'] >= st.session_state.threshold).astype(int)
risk_df['Predicted'] = y_pred
risk_df['Risk_Level'] = risk_df['risk_probability'].apply(risk_level)
risk_df['Probability'] = risk_df['risk_probability']
risk_df['NIM'] = risk_df['nim']
risk_df['Index'] = range(len(risk_df))
risk_df['Actual'] = risk_df['risk_label']

st.session_state.risk_df = risk_df
st.session_state.y_pred = y_pred
st.session_state.high_count = (risk_df['Risk_Level'] == 'High Risk').sum()
st.session_state.medium_count = (risk_df['Risk_Level'] == 'Medium Risk').sum()
st.session_state.low_count = (risk_df['Risk_Level'] == 'Low Risk').sum()

# ── HEADER ATAS ──────────────────────────────────────────────
st.markdown("""
<div class="dashboard-header">
    <p class="dashboard-title">Student Risk Prediction Dashboard</p>
    <p class="dashboard-subtitle">Interpretable Machine Learning · Random Forest · SHAP Analysis</p>
</div>
""", unsafe_allow_html=True)

# ── ROUTING HALAMAN ──────────────────────────────────────────
if   page == "📊 Overview":            page_overview()
elif page == "🔍 SHAP Global":         page_shap()
elif page == "👤 Individual Analysis": page_individual()
elif page == "📋 Risk Table":          page_risk_table()
elif page == "🚨 Class Alert":         page_class_alert()
elif page == "🏫 Rekomendasi Prodi":   page_prodi()