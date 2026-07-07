import streamlit as st
import pandas as pd
import joblib
import shap
import warnings
from config.database import get_db_connection
from etl.config import RAW_TABLE, PROCESSED_TABLE

warnings.filterwarnings('ignore')


FEATURE_COLS = [
    'Avg_days_before_deadline', 'pct_submission_H_minus_1', 'pct_late_submission',
    'FD_ratio', 'Download_ratio', 'VBL_ratio',
    'Avg_TLE', 'Count_TLE_below_3', 'Avg_TP_awal', 'Avg_TK_awal',
    'Quiz1_score', 'Avg_LO1_awal', 'Trend_TP', 'Trend_TK', 'Early_academic_score'
]

# Load Database
@st.cache_resource
def load_model():
    """Load pre-trained model"""
    return joblib.load("models/model.pkl")


@st.cache_data
def load_processed_data():
    """
    Load processed data dari PostgreSQL (bukan Excel).
    Query dari risk_data.processed_student_data table.
    """
    try:
        conn = get_db_connection()
        query = "SELECT * FROM processed_student_data"
        df = pd.read_sql(query, conn)
        conn.close()
        
        # Convert columns ke format yang diharapkan
        df['Probability'] = df['risk_probability']
        df['Risk_Level'] = df['risk_label'].map({
            1: 'High Risk',
            0: 'Low Risk'
        })
        df['Predicted'] = df['risk_label']
        df['Actual'] = df['risk_label']  # Karena processed_data sudah hasil prediksi
        df['Index'] = range(len(df))
        
        return df
        
    except Exception as e:
        st.error(f"❌ Error loading data from PostgreSQL: {e}")
        return pd.DataFrame()


@st.cache_data
def load_raw_data():
    """Load raw data dari PostgreSQL untuk SHAP analysis"""
    try:
        conn = get_db_connection()
        query = f"SELECT * FROM {RAW_TABLE}"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"❌ Error loading raw data: {e}")
        return pd.DataFrame()


@st.cache_data
def prepare_shap_data(_df_raw):
    """Prepare data untuk SHAP analysis"""
    try:
        model = load_model()
        
        # Uppercase kolom sesuai training
        X = _df_raw[FEATURE_COLS].fillna(0).copy()
        X.columns = X.columns.str.upper()
        
        # Compute SHAP
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X)
        shap_vals_risk = shap_values[:, :, 1]
        
        return explainer, shap_vals_risk, X
        
    except Exception as e:
        st.error(f"❌ Error preparing SHAP data: {e}")
        return None, None, None
    
@st.cache_data(ttl=10)
def load_alert_data():
    """
    Load alert data dari Google Sheets (untuk Class Alert page).
    """
    try:
        sheet_url = "https://docs.google.com/spreadsheets/d/1UEA7rwDWgWDHUDtBQJ-D-CjZsLPp_UESO8IhZvmmpEU/export?format=csv"
        df = pd.read_csv(sheet_url)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"❌ Error loading alert data: {e}")
        return pd.DataFrame()