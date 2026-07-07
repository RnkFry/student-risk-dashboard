import streamlit as st
from utils.loader import load_alert_data
from utils.features import create_features, calculate_risk, get_top_feature, calculate_scores
from utils.recommendation import generate_recommendation, render_at_risk_students

def render():
    # Ambil model dan fitur dari session_state
    model        = st.session_state.model
    feature_cols = st.session_state.feature_cols

    # Render UI Halaman Class Alert
    st.markdown('<p class="section-header">🚨 Class Alert System</p>', unsafe_allow_html=True)

    df_alert = load_alert_data()
    df_alert.columns = df_alert.columns.str.upper()

    if df_alert.empty:
        st.warning("Belum ada data atau gagal memuat Google Sheets.")
        st.stop()

    if 'Current_Week' not in df_alert.columns:
        st.error("Kolom 'Current_Week' belum ada di dataset!")
        st.stop()

    if 'Kode Kelas' not in df_alert.columns:
        st.error("Kolom 'Kode Kelas' tidak ditemukan di data alert.")
        st.stop()

    current_week = int(df_alert['Current_Week'].max())

    st.metric("Current Week", current_week)
    st.progress(current_week / 14)

    kelas_list     = df_alert['Kode Kelas'].dropna().unique()
    selected_kelas = st.selectbox("Pilih Kelas:", kelas_list)
    df_kelas       = df_alert[df_alert['Kode Kelas'] == selected_kelas].copy()

    # Eksekusi fungsi pengolahan fitur & perhitungan risiko
    df_kelas              = create_features(df_kelas)
    df_kelas.columns = df_kelas.columns.str.upper()
    df_kelas, high_risk_pct = calculate_risk(df_kelas, model, feature_cols)
    top_feature           = get_top_feature(model, feature_cols)

    if current_week < 4:
        st.info("⏳ Data belum mencapai Week 4. Alert belum tersedia.")
        st.stop()

    # ALERT SESSION 4
    if current_week >= 4:
        perf, eng, res = calculate_scores(
            df_kelas,
            tp_cols  = ['TP1'],
            tk_cols  = ['TK1', 'TK2'],
            vc_cols  = ['VC1','VC2','VC3'],
            fd_cols  = ['FD1','FD2','FD3'],
            ppt_cols = ['PPT1','PPT2','PPT3','PPT4'],
            ln_cols  = ['LN1','LN2','LN3'],
            vbl_cols = ['VBL1','VBL2','VBL3']
        )

        if perf < 60 and eng < 0.6:
            alert = "HIGH ALERT 🚨"
        elif perf < 70:
            alert = "MEDIUM ALERT ⚠️"
        else:
            alert = "SAFE ✅"

        st.subheader("📍 Alert Session 4")
        st.write(f"**Status:** {alert}")

        col1, col2, col3 = st.columns(3)
        col1.metric("Performance",    f"{perf:.2f}")
        col2.metric("Engagement",     f"{eng:.2f}")
        col3.metric("Resource Usage", f"{res:.2f}")

        st.subheader("🤖 ML Insight")
        st.metric("High Risk (%)", f"{high_risk_pct*100:.1f}%")
        st.write(f"Top Factor: **{top_feature}**")

        recs = generate_recommendation(perf, eng, res, alert, current_week, high_risk_pct, top_feature)

        st.subheader("💡 Recommendation")
        for r in recs:
            st.write(f"- {r}")

        st.markdown("---")
        render_at_risk_students(
            df_kelas, feature_cols, model,
            session_label = "Session 4",
            tp_cols  = ['TP1'],
            tk_cols  = ['TK1', 'TK2'],
            vc_cols  = [],
            fd_cols  = ['FD1','FD2','FD3'],
            ppt_cols = ['PPT1','PPT2','PPT3','PPT4'],
            ln_cols  = ['LN1','LN2','LN3'],
            vbl_cols = ['VBL1','VBL2','VBL3']
        )

    # ALERT SESSION 10
    if current_week >= 10:
        perf, eng, res = calculate_scores(
            df_kelas,
            tp_cols  = ['TP2'],
            tk_cols  = ['TK3', 'TK4'],
            vc_cols  = ['VC4','VC5','VC6','VC7'],
            fd_cols  = ['FD4','FD5','FD6','FD7'],
            ppt_cols = ['PPT5','PPT6','PPT7'],
            ln_cols  = ['LN4','LN5','LN6','LN7'],
            vbl_cols = ['VBL4','VBL5','VBL6']
        )

        if perf < 60 and eng < 0.6:
            alert = "HIGH ALERT 🚨"
        elif perf < 70:
            alert = "MEDIUM ALERT ⚠️"
        else:
            alert = "SAFE ✅"

        st.subheader("📍 Alert Session 10")
        st.write(f"**Status:** {alert}")

        col1, col2, col3 = st.columns(3)
        col1.metric("Performance",    f"{perf:.2f}")
        col2.metric("Engagement",     f"{eng:.2f}")
        col3.metric("Resource Usage", f"{res:.2f}")

        st.subheader("🤖 ML Insight")
        st.metric("High Risk (%)", f"{high_risk_pct*100:.1f}%")
        st.write(f"Top Factor: **{top_feature}**")

        recs = generate_recommendation(perf, eng, res, alert, current_week, high_risk_pct, top_feature)
        st.subheader("💡 Recommendation")
        for r in recs:
            st.write(f"- {r}")

        st.markdown("---")
        render_at_risk_students(
            df_kelas, feature_cols, model,
            session_label = "Session 10",
            tp_cols  = ['TP2'],
            tk_cols  = ['TK3', 'TK4'],
            vc_cols  = ['VC4','VC5','VC6','VC7'],
            fd_cols  = ['FD4','FD5','FD6','FD7'],
            ppt_cols = ['PPT5','PPT6','PPT7'],
            ln_cols  = ['LN4','LN5','LN6','LN7'],
            vbl_cols = ['VBL4','VBL5','VBL6']
        )

    # ALERT SESSION 14
    if current_week >= 14:
        perf, eng, res = calculate_scores(
            df_kelas,
            tp_cols  = [],
            tk_cols  = ['TK3', 'TK4'],
            vc_cols  = ['VC8','VC9','VC10'],
            fd_cols  = ['FD8','FD9','FD10'],
            ppt_cols = ['PPT8','PPT9','PPT10'],
            ln_cols  = ['LN8','LN9','LN10'],
            vbl_cols = ['VBL7','VBL8','VBL9','VBL10']
        )

        if perf < 60 and eng < 0.6:
            alert = "HIGH ALERT 🚨"
        elif perf < 70:
            alert = "MEDIUM ALERT ⚠️"
        else:
            alert = "SAFE ✅"

        st.subheader("📍 Alert Session 14")
        st.write(f"**Status:** {alert}")

        col1, col2, col3 = st.columns(3)
        col1.metric("Performance",    f"{perf:.2f}")
        col2.metric("Engagement",     f"{eng:.2f}")
        col3.metric("Resource Usage", f"{res:.2f}")

        st.subheader("🤖 ML Insight")
        st.metric("High Risk (%)", f"{high_risk_pct*100:.1f}%")
        st.write(f"Top Factor: **{top_feature}**")

        recs = generate_recommendation(perf, eng, res, alert, current_week, high_risk_pct, top_feature)
        st.subheader("💡 Recommendation")
        for r in recs:
            st.write(f"- {r}")

        st.markdown("---")
        render_at_risk_students(
            df_kelas, feature_cols, model,
            session_label = "Session 14",
            tp_cols  = [],
            tk_cols  = ['TK3', 'TK4'],
            vc_cols  = ['VC8','VC9','VC10'],
            fd_cols  = ['FD8','FD9','FD10'],
            ppt_cols = ['PPT8','PPT9','PPT10'],
            ln_cols  = ['LN8','LN9','LN10'],
            vbl_cols = ['VBL7','VBL8','VBL9','VBL10']
        )