import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import shap
from utils.ui import risk_color

def render():
    # Ambil data dari session_state
    risk_df        = st.session_state.risk_df
    X_test         = st.session_state.X_test
    feature_cols   = st.session_state.feature_cols
    shap_vals_risk = st.session_state.shap_vals_risk
    explainer      = st.session_state.explainer

    # Render UI Halaman Individual Analysis
    st.markdown('<p class="section-header">Analisis Individual Mahasiswa</p>', unsafe_allow_html=True)

    col_sel, col_info = st.columns([1, 2])

    with col_sel:
        filter_opt = st.selectbox("Filter mahasiswa:", ["Semua", "High Risk", "Medium Risk", "Low Risk"])
        if filter_opt == "Semua":
            filtered = risk_df
        else:
            filtered = risk_df[risk_df['Risk_Level'] == filter_opt]

        student_options = filtered.index.tolist()
        selected_student = st.selectbox(
            "Pilih index mahasiswa:",
            student_options,
            format_func=lambda x: f"Index {x} - NIM {risk_df.loc[x, 'NIM']}"
        )

    X_test_reset  = X_test.reset_index(drop=True)
    risk_df_reset = risk_df.reset_index(drop=True)

    idx          = selected_student
    student_data = risk_df_reset.loc[idx]
    level        = student_data['Risk_Level']
    prob         = student_data['Probability']
    actual       = "Risk" if student_data['Actual'] == 1 else "Tidak Risk"
    predicted    = "Risk" if student_data['Predicted'] == 1 else "Tidak Risk"
    badge_class  = {'High Risk': 'badge-high', 'Medium Risk': 'badge-medium', 'Low Risk': 'badge-low'}[level]

    with col_info:
        st.markdown(f"""
        <div class="student-card">
            <div style="display:flex; gap:2rem; align-items:center; flex-wrap:wrap;">
                <div>
                    <div class="label">Mahasiswa</div>
                    <div class="value">Index #{selected_student} | NIM {student_data['NIM']}</div>
                </div>
                <div>
                    <div class="label">Probabilitas Risk</div>
                    <div class="value" style="color:{risk_color(level)}">{prob:.1%}</div>
                </div>
                <div>
                    <div class="label">Risk Level</div>
                    <div><span class="risk-badge {badge_class}">{level}</span></div>
                </div>
                <div>
                    <div class="label">Aktual</div>
                    <div class="value">{actual}</div>
                </div>
                <div>
                    <div class="label">Prediksi</div>
                    <div class="value">{predicted}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("**SHAP Waterfall Plot** — kontribusi tiap fitur untuk mahasiswa ini")
    fig, ax = plt.subplots(figsize=(9, 5))
    shap.waterfall_plot(
        shap.Explanation(
            values        = shap_vals_risk[idx],
            base_values   = explainer.expected_value[1],
            data          = X_test_reset.iloc[idx].values,
            feature_names = feature_cols
        ),
        show=False
    )
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.markdown("""
    <div class="insight-box">
        <strong>Cara membaca waterfall:</strong>
        Bar <strong style="color:#E53935">merah</strong> = fitur yang mendorong prediksi ke arah Risk (menaikkan probabilitas).
        Bar <strong style="color:#0096DA">biru</strong> = fitur yang menahan dari Risk (menurunkan probabilitas).
        Angka di ujung bar = besarnya kontribusi fitur tersebut dalam satuan log-odds.
        <strong>E[f(x)]</strong> adalah baseline (rata-rata semua mahasiswa), <strong>f(x)</strong> adalah prediksi akhir mahasiswa ini.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**Nilai fitur mahasiswa ini**")
    feat_df = pd.DataFrame({
        'Fitur':       feature_cols,
        'Nilai':       X_test_reset.iloc[idx].values.round(4),
        'SHAP Value':  shap_vals_risk[idx].round(4),
        'Pengaruh':    ['↑ Risk' if v > 0 else ('↓ Aman' if v < 0 else '—') for v in shap_vals_risk[idx]]
    }).sort_values('SHAP Value', key=abs, ascending=False)
    st.dataframe(feat_df, use_container_width=True, hide_index=True)