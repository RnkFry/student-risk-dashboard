import streamlit as st

def render():
    # Ambil data dari session_state
    risk_df = st.session_state.risk_df

    # Render UI Halaman Risk Table
    st.markdown('<p class="section-header">Tabel Lengkap Risk Level Mahasiswa</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    filter_level = col1.selectbox("Filter Risk Level:", ["Semua", "High Risk", "Medium Risk", "Low Risk"])
    sort_by      = col2.selectbox("Urutkan berdasarkan:", ["Probability (Tinggi → Rendah)", "Probability (Rendah → Tinggi)", "Index"])
    show_n       = col3.selectbox("Tampilkan:", [50, 100, 200, "Semua"])

    display_df = risk_df.copy()
    if filter_level != "Semua":
        display_df = display_df[display_df['Risk_Level'] == filter_level]

    if sort_by == "Probability (Tinggi → Rendah)":
        display_df = display_df.sort_values('Probability', ascending=False)
    elif sort_by == "Probability (Rendah → Tinggi)":
        display_df = display_df.sort_values('Probability', ascending=True)

    if show_n != "Semua":
        display_df = display_df.head(show_n)

    display_df['Probability'] = display_df['Probability'].round(4)
    display_df['Actual']      = display_df['Actual'].map({1: 'Risk', 0: 'Tidak Risk'})
    display_df['Predicted']   = display_df['Predicted'].map({1: 'Risk', 0: 'Tidak Risk'})

    st.dataframe(
        display_df[['Index', 'Probability', 'Actual', 'Predicted', 'Risk_Level']],
        use_container_width=True,
        hide_index=True
    )

    st.markdown(f"*Menampilkan {len(display_df)} dari {len(risk_df)} mahasiswa*")

    csv = display_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "⬇ Download sebagai CSV",
        data=csv,
        file_name="student_risk_prediction.csv",
        mime="text/csv"
    )