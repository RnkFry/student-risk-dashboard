import streamlit as st
import matplotlib.pyplot as plt
import shap

def render():
    # Ambil data dari session_state
    shap_vals_risk = st.session_state.shap_vals_risk
    X_test         = st.session_state.X_test
    explainer = st.session_state.explainer
    feature_cols   = st.session_state.feature_cols

    feature_cols_display = [f.lower() for f in feature_cols]

    # Render UI Halaman SHAP Global
    tab1, tab2, tab3 = st.tabs(["Summary Plot", "Bar Plot", "Dependence Plot"])

    with tab1:
        st.markdown('<p class="section-header">SHAP Summary Plot</p>', unsafe_allow_html=True)
        st.markdown("""
        <div class="insight-box">
            Setiap titik = satu mahasiswa. <strong>Warna merah</strong> = nilai fitur tinggi, <strong>biru</strong> = rendah.
            Posisi <strong>kanan</strong> = mendorong ke Risk, <strong>kiri</strong> = mendorong ke Aman.
            Fitur diurutkan dari yang paling berpengaruh di atas.
        </div>
        """, unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(9, 6))
        shap.summary_plot(shap_vals_risk, X_test, feature_names=feature_cols_display,
                          show=False, plot_size=(9, 6))
        st.pyplot(plt.gcf())
        plt.close('all')

    with tab2:
        st.markdown('<p class="section-header">SHAP Bar Plot — Rata-rata Kontribusi</p>', unsafe_allow_html=True)
        st.markdown("""
        <div class="insight-box">
            Menampilkan <strong>rata-rata absolut SHAP value</strong> tiap fitur.
            Semakin panjang bar, semakin besar kontribusi fitur tersebut secara keseluruhan dalam model.
        </div>
        """, unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(9, 5))
        shap.summary_plot(shap_vals_risk, X_test, feature_names=feature_cols_display,
                          plot_type='bar', show=False, plot_size=(9, 5))
        st.pyplot(plt.gcf())
        plt.close('all')

    with tab3:
        st.markdown('<p class="section-header">Dependence Plot</p>', unsafe_allow_html=True)
        st.markdown("""
        <div class="insight-box">
            Menunjukkan hubungan antara <strong>nilai fitur</strong> (sumbu X) dengan <strong>SHAP value</strong>-nya (sumbu Y).
            Dari sini terlihat di nilai berapa suatu fitur mulai mendorong mahasiswa ke arah Risk.
        </div>
        """, unsafe_allow_html=True)

        selected_feature = st.selectbox("Pilih fitur:", feature_cols_display,
                                         index=feature_cols_display.index('early_academic_score'))
        fig, ax = plt.subplots(figsize=(9, 4.5))
        shap.dependence_plot(selected_feature, shap_vals_risk, X_test,
                              feature_names=feature_cols_display, show=False, ax=ax)
        ax.axhline(0, color='#D1DCE8', linestyle='--', linewidth=1)
        st.pyplot(plt.gcf())
        plt.close('all')

        st.markdown(f"""
        <div class="insight-box">
            <strong>Cara baca:</strong> Titik di atas garis 0 → nilai {selected_feature} tersebut
            mendorong mahasiswa ke arah Risk. Titik di bawah garis 0 → mendorong ke arah Aman.
            Warna titik menunjukkan fitur lain yang paling berinteraksi.
        </div>
        """, unsafe_allow_html=True)