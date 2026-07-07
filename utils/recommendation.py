import streamlit as st
import pandas as pd

def generate_recommendation(perf, eng, res, alert, week, high_risk_pct, top_feature):
    recs = []

    if week <= 4:
        if perf < 60 and eng < 0.6:
            recs.append("⚠️ Performa dan keterlibatan sama-sama rendah di awal semester — segera lakukan sesi penguatan materi dasar.")
        elif perf < 70 and eng >= 0.6:
            recs.append("📚 Mahasiswa aktif mengakses materi, tapi nilai masih di bawah 70 — fokus pada pemahaman konsep, bukan hanya hadir.")
        elif perf >= 70 and eng < 0.6:
            recs.append("👀 Nilai awal cukup baik, tapi engagement rendah — pantau apakah mahasiswa hanya mengandalkan kemampuan sebelumnya tanpa belajar aktif.")
        else:
            recs.append("✅ Kelas berjalan baik di awal semester. Pertahankan ritme belajar ini.")

        if high_risk_pct > 0.3:
            recs.append(f"🚨 {high_risk_pct*100:.0f}% mahasiswa terdeteksi high-risk — pertimbangkan sesi konsultasi individual untuk mahasiswa tersebut.")

    elif week <= 10:
        if high_risk_pct > 0.4:
            recs.append(f"🚨 Lebih dari {high_risk_pct*100:.0f}% mahasiswa masuk kategori high-risk — intervensi segera diperlukan sebelum UAS.")
        elif high_risk_pct > 0.2:
            recs.append(f"⚠️ Sekitar {high_risk_pct*100:.0f}% mahasiswa berisiko — fokus pada kelompok ini sebelum pertengahan semester berakhir.")

        if perf < 60:
            recs.append("📉 Rata-rata performa kelas di bawah 60 — pertimbangkan review materi atau tambahan latihan soal terstruktur.")
        elif perf < 75:
            recs.append("📊 Performa kelas sedang — dorong mahasiswa untuk mengerjakan latihan mandiri lebih konsisten.")

        if res < 0.5:
            recs.append("📂 Penggunaan resource (PPT, LN, VBL) masih rendah — ingatkan mahasiswa untuk memanfaatkan semua materi yang tersedia.")

        recs.append(f"🔍 Faktor paling berpengaruh pada prediksi risiko saat ini: **{top_feature}** — pertimbangkan untuk memperkuat aspek ini.")

    else:  # week >= 11
        recs.append("📋 Mendekati akhir semester — evaluasi menyeluruh terhadap metode pembelajaran dan kesiapan UAS diperlukan.")

        if high_risk_pct > 0.3:
            recs.append(f"🚨 Masih ada {high_risk_pct*100:.0f}% mahasiswa high-risk menjelang akhir — koordinasi dengan wali dosen atau academic advisor disarankan.")

        if perf < 65:
            recs.append("📉 Performa keseluruhan masih rendah — pertimbangkan sesi review intensif atau remedial sebelum ujian akhir.")

        if eng < 0.5:
            recs.append("👻 Keterlibatan mahasiswa sangat rendah di akhir semester — cek apakah ada mahasiswa yang sudah tidak aktif sama sekali.")

    if not recs:
        recs.append("✅ Kondisi kelas dalam batas normal. Tidak ada tindakan mendesak yang diperlukan.")

    return recs


def render_at_risk_students(df_kelas, feature_cols, model, session_label,
                             tp_cols, tk_cols, vc_cols, fd_cols, ppt_cols, ln_cols, vbl_cols):
    """
    Tampilkan daftar mahasiswa berisiko beserta nilai-nilai yang menjadi penyebab risiko.
    Hanya menampilkan kolom yang relevan untuk session tersebut.
    """

    at_risk = df_kelas[df_kelas['risk_label'] == 1].copy()

    st.subheader(f"👥 Daftar Mahasiswa Berisiko — {session_label}")

    if at_risk.empty:
        st.markdown("""
        <div class="no-risk-box">
            ✅ Tidak ada mahasiswa yang terdeteksi berisiko pada session ini.
        </div>
        """, unsafe_allow_html=True)
        return

    # Kolom relevan untuk session ini
    relevant_cols = tp_cols + tk_cols + vc_cols + fd_cols + ppt_cols + ln_cols + vbl_cols
    relevant_cols = [c for c in relevant_cols if c in at_risk.columns]

    # Ambil feature importance dari model untuk ranking alasan
    importances = dict(zip(feature_cols, model.feature_importances_))

    # Mapping nama fitur teknis → label yang lebih mudah dibaca
    label_map = {
        'TP1': 'Tugas Personal 1',     'TP2': 'Tugas Personal 2',
        'TK1': 'Tugas Kelompok 1',    'TK2': 'Tugas Kelompok 2',
        'TK3': 'Tugas Kelompok 3',    'TK4': 'Tugas Kelompok 4',
        'VC1': 'Video Content 1',     'VC2': 'Video Content 2',
        'VC3': 'Video Content 3',     'VC4': 'Video Content 4',
        'VC5': 'Video Content 5',     'VC6': 'Video Content 6',
        'VC7': 'Video Content 7',     'VC8': 'Video Content 8',
        'VC9': 'Video Content 9',     'VC10': 'Video Content 10',
        'FD1': 'File Download 1',     'FD2': 'File Download 2',
        'FD3': 'File Download 3',     'FD4': 'File Download 4',
        'FD5': 'File Download 5',     'FD6': 'File Download 6',
        'FD7': 'File Download 7',     'FD8': 'File Download 8',
        'FD9': 'File Download 9',     'FD10': 'File Download 10',
        'PPT1': 'PPT 1',  'PPT2': 'PPT 2',  'PPT3': 'PPT 3',  'PPT4': 'PPT 4',
        'PPT5': 'PPT 5',  'PPT6': 'PPT 6',  'PPT7': 'PPT 7',  'PPT8': 'PPT 8',
        'PPT9': 'PPT 9',  'PPT10': 'PPT 10',
        'LN1': 'Learning Note 1',  'LN2': 'Learning Note 2',  'LN3': 'Learning Note 3',
        'LN4': 'Learning Note 4',  'LN5': 'Learning Note 5',  'LN6': 'Learning Note 6',
        'LN7': 'Learning Note 7',  'LN8': 'Learning Note 8',  'LN9': 'Learning Note 9',
        'LN10': 'Learning Note 10',
        'VBL1': 'VBL 1',  'VBL2': 'VBL 2',  'VBL3': 'VBL 3',  'VBL4': 'VBL 4',
        'VBL5': 'VBL 5',  'VBL6': 'VBL 6',  'VBL7': 'VBL 7',  'VBL8': 'VBL 8',
        'VBL9': 'VBL 9',  'VBL10': 'VBL 10',
    }

    # Pisah high vs medium risk
    high_risk_df   = at_risk[at_risk['risk_prob'] >= 0.7].sort_values('risk_prob', ascending=False)
    medium_risk_df = at_risk[(at_risk['risk_prob'] >= 0.4) & (at_risk['risk_prob'] < 0.7)].sort_values('risk_prob', ascending=False)

    # Summary badge
    n_high   = len(high_risk_df)
    n_medium = len(medium_risk_df)
    st.markdown(f"""
    <div style="display:flex; gap:0.75rem; margin-bottom:1rem; flex-wrap:wrap;">
        <span style="background:#FEE2E2;color:#E53935;border:1px solid #FECACA;
                     padding:4px 14px;border-radius:20px;font-size:0.8rem;font-weight:600;">
            🚨 High Risk: {n_high} mahasiswa
        </span>
        <span style="background:#FEF3E2;color:#F68B1E;border:1px solid #FDE68A;
                     padding:4px 14px;border-radius:20px;font-size:0.8rem;font-weight:600;">
            ⚠️ Medium Risk: {n_medium} mahasiswa
        </span>
    </div>
    """, unsafe_allow_html=True)

    def render_student_cards(subset, card_class, prob_color):
        if subset.empty:
            return

        cols_per_row = 2
        rows_list    = list(subset.iterrows())

        for i in range(0, len(rows_list), cols_per_row):
            st_cols = st.columns(cols_per_row)
            for j, (_, row) in enumerate(rows_list[i:i + cols_per_row]):
                nim  = int(row['NIM']) if pd.notna(row['NIM']) else 'N/A'
                prob = row['risk_prob']

                factors = []
                for col in relevant_cols:
                    if col not in row.index or pd.isna(row[col]):
                        continue
                    val = row[col]
                    if col.startswith(('TP', 'TK')):
                        status = 'danger' if val < 60 else ('warning' if val < 70 else 'ok')
                        pct    = min(val / 100, 1.0) * 100
                    else:
                        status = 'danger' if val == 0 else 'ok'
                        pct    = val * 100
                    label = label_map.get(col, col)
                    factors.append((label, val, status, pct, col))

                factors.sort(key=lambda x: (0 if x[2] == 'danger' else (1 if x[2] == 'warning' else 2)))
                display_factors = factors[:6]

                border_color = '#E53935' if card_class == 'card-high' else '#F68B1E'

                with st_cols[j]:
                    # Header card
                    st.markdown(
                        f'<div style="background:#FFFFFF;border:1px solid #D1DCE8;'
                        f'border-left:3px solid {border_color};border-radius:12px;'
                        f'padding:1rem 1.25rem;margin-bottom:0.75rem;">'
                        f'<div style="font-family:\'DM Serif Display\',serif;font-size:1rem;'
                        f'color:#1A2332;font-weight:600;margin-bottom:0.2rem;">NIM {nim}</div>'
                        f'<div style="font-size:0.78rem;color:{prob_color};margin-bottom:0.75rem;">'
                        f'Probabilitas Risiko: <strong>{prob:.1%}</strong></div>',
                        unsafe_allow_html=True
                    )

                    # Render setiap faktor sebagai baris terpisah
                    for label, val, status, pct, col in display_factors:
                        val_str    = f"{val:.0f}" if col.startswith(('TP', 'TK')) else ("✓" if val == 1 else "✗")
                        bar_color  = '#E53935' if status == 'danger' else ('#F68B1E' if status == 'warning' else '#0096DA')
                        val_color  = '#E53935' if status == 'danger' else ('#F68B1E' if status == 'warning' else '#0096DA')
                        st.markdown(
                            f'<div style="display:flex;align-items:center;justify-content:space-between;'
                            f'padding:3px 0;border-bottom:1px solid #23293a;font-size:0.78rem;">'
                            f'<span style="color:#374151;flex:1;">{label}</span>'
                            f'<span style="color:{val_color};font-weight:600;min-width:36px;text-align:right;margin-right:8px;">{val_str}</span>'
                            f'<div style="width:60px;height:5px;background:#E5E7EB;border-radius:3px;overflow:hidden;">'
                            f'<div style="width:{pct:.0f}%;height:100%;background:{bar_color};border-radius:3px;"></div>'
                            f'</div></div>',
                            unsafe_allow_html=True
                        )

                    # Tutup div card
                    st.markdown('</div>', unsafe_allow_html=True)

    if n_high > 0:
        st.markdown("**🚨 High Risk**")
        render_student_cards(high_risk_df, "card-high", "#E53935")

    if n_medium > 0:
        st.markdown("**⚠️ Medium Risk**")
        render_student_cards(medium_risk_df, "card-medium", "#F68B1E")

    # Tombol download daftar berisiko
    export_cols = ['NIM', 'risk_prob', 'risk_label'] + relevant_cols
    export_cols = [c for c in export_cols if c in at_risk.columns]
    export_df   = at_risk[export_cols].copy()
    export_df['risk_prob'] = export_df['risk_prob'].round(4)
    csv = export_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        f"⬇ Download daftar mahasiswa berisiko ({session_label})",
        data=csv,
        file_name=f"at_risk_{session_label.lower().replace(' ','_')}.csv",
        mime="text/csv",
        key=f"dl_{session_label}"
    )