import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from utils.loader import load_alert_data


# ── Helper ───────────────────────────────────────────────────
def _col_mean(df, cols):
    existing = [c for c in cols if c in df.columns]
    if not existing:
        return 0.0
    return float(df[existing].mean().mean())


def _classify_level(avg_assessment, avg_delivery, avg_dosen, avg_course):
    """
    Klasifikasi L1–L4 berdasarkan 4 dimensi.

    Skala input:
      avg_assessment : 0–100  (nilai TP & TK)
      avg_delivery   : 0–10   (FD + LN, dinormalisasi)
      avg_dosen      : 0–10   (kualifikasi dosen)
      avg_course     : 0–10   (VBL + PPT, dinormalisasi)

    Return: (level, level_name, color, focus, description)
    """
    # L4 — semua dimensi bermasalah
    if (avg_course < 7
            and avg_dosen < 4.0
            and avg_delivery < 4.0
            and avg_assessment < 75):
        return (
            "L4", "Poor", "#E53935",
            "🗂️ Fokus perbaiki Course Design",
            "Seluruh aspek pembelajaran perlu perhatian. Prioritas utama adalah memperbaiki "
            "desain kursus (VBL & PPT) karena menjadi fondasi dari dimensi lainnya."
        )

    # L3 — dosen & delivery buruk, assessment rendah
    if (avg_dosen < 4.0
            and avg_delivery < 4.0
            and avg_assessment < 75):
        return (
            "L3", "Average", "#F68B1E",
            "🎓 Fokus evaluasi Kualifikasi Dosen",
            "Performa dosen dan penyampaian materi sama-sama kurang efektif. "
            "Evaluasi dan pembinaan dosen perlu menjadi prioritas agar kualitas "
            "delivery content dapat meningkat."
        )

    # L2 — delivery rendah, assessment rendah
    if (avg_delivery < 7
            and avg_assessment < 75):
        return (
            "L2", "Good", "#F68B1E",
            "📡 Fokus tingkatkan Delivery Content",
            "Course design dan kualifikasi dosen sudah cukup baik, namun materi "
            "belum tersampaikan secara efektif. Tingkatkan kualitas dan aksesibilitas "
            "File Download & Learning Note."
        )

    # L1 — semua aman tapi nilai masih < 75
    if avg_assessment < 75:
        return (
            "L1", "Excellent", "#0096DA",
            "📝 Fokus turunkan kesulitan Assessment",
            "Semua aspek pembelajaran sudah berjalan baik — course design, dosen, "
            "dan delivery sudah solid. Namun nilai mahasiswa masih di bawah 75. "
            "Pertimbangkan untuk mereview tingkat kesulitan soal atau memperjelas rubrik penilaian."
        )

    # Aman
    return (
        "Aman", "Aman", "#10b981",
        "✅ Tidak ada intervensi mendesak",
        "Semua dimensi pembelajaran berjalan dengan baik dan nilai assessment mahasiswa "
        "sudah memenuhi target ≥ 75. Pertahankan kualitas ini."
    )


def render():
    st.markdown("""
    <div class="dashboard-header" style="margin-bottom:1rem;">
        <p class="dashboard-title">🏫 Rekomendasi untuk Program Studi</p>
        <p class="dashboard-subtitle">Evaluasi kelas berdasarkan 4 dimensi · Klasifikasi L1–L4</p>
    </div>
    """, unsafe_allow_html=True)

    df_alert = load_alert_data()

    if df_alert.empty:
        st.warning("Belum ada data atau gagal memuat Google Sheets.")
        return

    if 'Kode Kelas' not in df_alert.columns:
        st.error("Kolom 'Kode Kelas' tidak ditemukan.")
        return

    # ── Pilih kelas ──────────────────────────────────────────
    semua_kelas = sorted(df_alert['Kode Kelas'].dropna().unique().tolist())

    col_sel, col_week = st.columns([3, 1])
    with col_sel:
        selected_kelas = st.selectbox("Pilih Kelas yang Dievaluasi:", semua_kelas)
    with col_week:
        current_week = int(df_alert['Current_Week'].max()) \
            if 'Current_Week' in df_alert.columns else 4
        st.metric("Current Week", current_week)
        st.progress(current_week / 14)

    df_kelas = df_alert[df_alert['Kode Kelas'] == selected_kelas].copy()
    st.markdown(f"*Kelas **{selected_kelas}** · {len(df_kelas)} mahasiswa*")
    st.markdown("---")

    # ── Kolom data ───────────────────────────────────────────
    tp_all  = [f'TP{i}'  for i in range(1, 3)]
    tk_all  = [f'TK{i}'  for i in range(1, 5)]
    fd_all  = [f'FD{i}'  for i in range(1, 11)]
    ln_all  = [f'LN{i}'  for i in range(1, 11)]
    vbl_all = [f'VBL{i}' for i in range(1, 11)]
    ppt_all = [f'PPT{i}' for i in range(1, 11)]

    # ── Hitung 4 dimensi ─────────────────────────────────────
    avg_tp         = _col_mean(df_kelas, tp_all)
    avg_tk         = _col_mean(df_kelas, tk_all)
    avg_assessment = (avg_tp + avg_tk) / 2             # skala 0–100

    avg_fd       = _col_mean(df_kelas, fd_all)          # skala 0–1
    avg_ln       = _col_mean(df_kelas, ln_all)
    avg_delivery = ((avg_fd + avg_ln) / 2) * 10        # → skala 0–10

    avg_vbl    = _col_mean(df_kelas, vbl_all)
    avg_ppt    = _col_mean(df_kelas, ppt_all)
    avg_course = ((avg_vbl + avg_ppt) / 2) * 10        # → skala 0–10

    # Kualifikasi Dosen: gabungan nilai TP (dinorm) + engagement
    avg_dosen = (avg_tp / 10 + avg_delivery) / 2       # → skala 0–10

    # ── Klasifikasi ──────────────────────────────────────────
    level, level_name, color, focus, description = _classify_level(
        avg_assessment, avg_delivery, avg_dosen, avg_course
    )

    # ── BADGE LEVEL ──────────────────────────────────────────
    badge_bg = {
        'L4': '#FEE2E2', 'L3': '#FEF3E2',
        'L2': '#FEF9E2', 'L1': '#E0F2FE', 'Aman': '#ECFDF5'
    }
    st.markdown(f"""
    <div style="background:{badge_bg.get(level,'#F0F4F8')};
                border:2px solid {color};border-radius:16px;
                padding:1.5rem 2rem;margin-bottom:1.25rem;">
        <div style="display:flex;align-items:center;gap:1.5rem;flex-wrap:wrap;">
            <div>
                <div style="font-size:0.7rem;color:#6B7280;text-transform:uppercase;
                            letter-spacing:.1em;font-weight:600;margin-bottom:.3rem;">
                    Level Kelas
                </div>
                <div style="font-size:3rem;font-weight:800;color:{color};
                            font-family:'DM Sans',sans-serif;line-height:1;">
                    {level}
                    <span style="font-size:1rem;font-weight:400;color:#6B7280;">
                        &nbsp;{level_name}
                    </span>
                </div>
            </div>
            <div style="border-left:2px solid {color};padding-left:1.5rem;flex:1;min-width:200px;">
                <div style="font-size:1rem;font-weight:700;color:{color};margin-bottom:.4rem;">
                    {focus}
                </div>
                <div style="font-size:0.85rem;color:#374151;line-height:1.6;">
                    {description}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 4 SCORECARD ──────────────────────────────────────────
    st.markdown("#### 📊 Skor 4 Dimensi")

    c1, c2, c3, c4 = st.columns(4)
    cards = [
        (c1, "📝 Assessment",        avg_assessment, 75,  100, "Nilai TP & TK",         "Target ≥ 75"),
        (c2, "📡 Delivery Content",  avg_delivery,   7,   10,  "FD + LN (skala 0–10)",  "Target ≥ 7"),
        (c3, "🎓 Kualifikasi Dosen", avg_dosen,      4.0, 10,  "Perf + Engagement",     "Target ≥ 4"),
        (c4, "🗂️ Course Design",     avg_course,     7,   10,  "VBL + PPT (skala 0–10)","Target ≥ 7"),
    ]

    for col_w, label, val, threshold, max_val, subtitle, target_note in cards:
        c   = '#0096DA' if val >= threshold else ('#F68B1E' if val >= threshold * 0.7 else '#E53935')
        pct = min(val / max_val * 100, 100)
        ok  = "✅" if val >= threshold else "❌"
        col_w.markdown(f"""
        <div style="background:#FFFFFF;border:1px solid #D1DCE8;border-left:3px solid {c};
                    border-radius:12px;padding:1rem 1.1rem;
                    box-shadow:0 1px 6px rgba(0,0,0,0.05);margin-bottom:.5rem;">
            <div style="font-size:0.7rem;color:#6B7280;text-transform:uppercase;
                        letter-spacing:.08em;font-weight:600;">{label}</div>
            <div style="font-size:1.9rem;font-weight:700;color:{c};line-height:1.1;margin:.2rem 0;">
                {val:.1f} <span style="font-size:0.9rem;">{ok}</span>
            </div>
            <div style="width:100%;height:5px;background:#E5E7EB;border-radius:3px;margin:.4rem 0;">
                <div style="width:{pct:.0f}%;height:100%;background:{c};border-radius:3px;"></div>
            </div>
            <div style="font-size:0.68rem;color:#9CA3AF;">{subtitle}</div>
            <div style="font-size:0.68rem;color:{c};font-weight:600;">{target_note}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── RADAR BAR CHART ──────────────────────────────────────
    st.markdown("#### 🗺️ Peta Dimensi vs Target")
    fig, ax = plt.subplots(figsize=(8, 2.8))
    dim_labels  = ['Assessment (target 75)',
                   'Delivery Content (target 7)',
                   'Kualifikasi Dosen (target 4)',
                   'Course Design (target 7)']
    # Normalisasi semua ke skala 0–100 untuk chart
    dim_vals    = [avg_assessment,
                   avg_delivery * 10,
                   avg_dosen * 10,
                   avg_course * 10]
    dim_targets = [75, 70, 40, 70]
    bar_c = ['#0096DA' if v >= t else '#E53935'
             for v, t in zip(dim_vals, dim_targets)]

    bars = ax.barh(dim_labels, dim_vals, color=bar_c, height=0.45, alpha=0.85)
    for t in set(dim_targets):
        ax.axvline(t, color='#9CA3AF', linestyle=':', linewidth=1.2)
    for bar, val in zip(bars, dim_vals):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                f'{val:.1f}', va='center', color='#1A2332', fontsize=9)

    ax.set_xlabel("Skor (dinormalisasi 0–100)")
    ax.set_xlim(0, 115)
    ax.invert_yaxis()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    # ── DETAIL EXPANDABLE ────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 🔍 Detail per Dimensi")

    # Assessment
    with st.expander("📝 Assessment — Detail Nilai TP & TK",
                     expanded=(level == 'L1')):
        col_g1, col_g2 = st.columns(2)
        tp_exist = [c for c in tp_all if c in df_kelas.columns]
        tk_exist = [c for c in tk_all if c in df_kelas.columns]
        with col_g1:
            st.markdown(f"**Rata-rata TP:** `{avg_tp:.1f}` &nbsp;·&nbsp; **Rata-rata TK:** `{avg_tk:.1f}`")
            if tp_exist or tk_exist:
                fig, ax = plt.subplots(figsize=(5, 3))
                for cols, lbl in [(tp_exist, 'TP'), (tk_exist, 'TK')]:
                    if cols:
                        flat = df_kelas[cols].values.flatten()
                        flat = flat[~np.isnan(flat)]
                        ax.hist(flat, bins=12, alpha=0.7, label=lbl)
                ax.axvline(75, color='#0096DA', linestyle='--', linewidth=1.5, label='Target 75')
                ax.set_xlabel("Nilai"); ax.set_ylabel("Jumlah")
                ax.legend(fontsize=8, facecolor='#FFFFFF', edgecolor='#D1DCE8', labelcolor='#374151')
                ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
                plt.tight_layout(); st.pyplot(fig); plt.close()
        with col_g2:
            if tp_exist:
                st.markdown("**5 mahasiswa dengan nilai TP terendah**")
                low5 = df_kelas[['NIM'] + tp_exist].copy()
                low5['avg'] = low5[tp_exist].mean(axis=1)
                low5 = low5.nsmallest(5, 'avg')[['NIM', 'avg'] + tp_exist]
                low5['NIM'] = low5['NIM'].astype(int)
                st.dataframe(low5.round(1), use_container_width=True, hide_index=True)

    # Delivery Content
    with st.expander("📡 Delivery Content — Detail FD & LN",
                     expanded=(level == 'L2')):
        fd_exist = [c for c in fd_all if c in df_kelas.columns]
        ln_exist = [c for c in ln_all if c in df_kelas.columns]
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown(f"**File Download:** `{avg_fd:.0%}` &nbsp;·&nbsp; **Learning Note:** `{avg_ln:.0%}`")
            show_cols = fd_exist[:5] + ln_exist[:5]
            if show_cols:
                vals = [df_kelas[c].mean() * 100 for c in show_cols]
                fig, ax = plt.subplots(figsize=(5, 3))
                bar_c = ['#0096DA' if v >= 70 else '#E53935' for v in vals]
                ax.bar(show_cols, vals, color=bar_c, width=0.6)
                ax.axhline(70, color='#F68B1E', linestyle='--', linewidth=1, label='Target 70%')
                ax.set_ylabel("Akses (%)"); ax.set_ylim(0, 115)
                ax.tick_params(axis='x', rotation=45)
                ax.legend(fontsize=8, facecolor='#FFFFFF', edgecolor='#D1DCE8', labelcolor='#374151')
                ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
                plt.tight_layout(); st.pyplot(fig); plt.close()
        with col_g2:
            delivery_cols = fd_exist + ln_exist
            if delivery_cols:
                st.markdown("**5 mahasiswa dengan akses materi terendah**")
                low5 = df_kelas[['NIM'] + delivery_cols].copy()
                low5['avg_akses'] = low5[delivery_cols].mean(axis=1)
                low5 = low5.nsmallest(5, 'avg_akses')[['NIM', 'avg_akses']]
                low5['NIM'] = low5['NIM'].astype(int)
                low5['avg_akses'] = (low5['avg_akses'] * 100).round(1).astype(str) + '%'
                st.dataframe(low5, use_container_width=True, hide_index=True)

    # Kualifikasi Dosen
    with st.expander("🎓 Kualifikasi Dosen — Detail",
                     expanded=(level == 'L3')):
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown(f"""
**Skor Kualifikasi Dosen:** `{avg_dosen:.2f}` / 10

Komponen:
- Rata-rata nilai TP mahasiswa: `{avg_tp:.1f}` → dinormalisasi `{avg_tp/10:.2f}`
- Rata-rata engagement FD+LN: `{avg_delivery:.2f}` / 10
- **Skor akhir:** ({avg_tp/10:.2f} + {avg_delivery:.2f}) / 2 = **{avg_dosen:.2f}**
""")
        with col_g2:
            fig, ax = plt.subplots(figsize=(5, 2.5))
            lbls = ['Nilai TP\n(norm)', 'Engagement\n(norm)', 'Skor\nDosen']
            vals = [avg_tp / 10, avg_delivery, avg_dosen]
            bar_c = ['#0096DA' if v >= 4 else '#E53935' for v in vals]
            ax.barh(lbls, [v * 10 for v in vals], color=bar_c, height=0.45)
            ax.axvline(40, color='#F68B1E', linestyle='--', linewidth=1, label='Target 4.0')
            ax.set_xlabel("Skor × 10")
            ax.legend(fontsize=8, facecolor='#FFFFFF', edgecolor='#D1DCE8', labelcolor='#374151')
            ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
            plt.tight_layout(); st.pyplot(fig); plt.close()

    # Course Design
    with st.expander("🗂️ Course Design — Detail VBL & PPT",
                     expanded=(level == 'L4')):
        vbl_exist = [c for c in vbl_all if c in df_kelas.columns]
        ppt_exist = [c for c in ppt_all if c in df_kelas.columns]
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown(f"**VBL:** `{avg_vbl:.0%}` &nbsp;·&nbsp; **PPT:** `{avg_ppt:.0%}` &nbsp;·&nbsp; **Gabungan:** `{avg_course:.1f}` / 10")
            show_cols = vbl_exist[:5] + ppt_exist[:5]
            if show_cols:
                vals = [df_kelas[c].mean() * 100 for c in show_cols]
                fig, ax = plt.subplots(figsize=(5, 3))
                bar_c = ['#0096DA' if v >= 70 else '#E53935' for v in vals]
                ax.bar(show_cols, vals, color=bar_c, width=0.6)
                ax.axhline(70, color='#F68B1E', linestyle='--', linewidth=1, label='Target 70%')
                ax.set_ylabel("Akses (%)"); ax.set_ylim(0, 115)
                ax.tick_params(axis='x', rotation=45)
                ax.legend(fontsize=8, facecolor='#FFFFFF', edgecolor='#D1DCE8', labelcolor='#374151')
                ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
                plt.tight_layout(); st.pyplot(fig); plt.close()
        with col_g2:
            course_cols = vbl_exist + ppt_exist
            if course_cols:
                st.markdown("**5 mahasiswa dengan akses course material terendah**")
                low5 = df_kelas[['NIM'] + course_cols].copy()
                low5['avg_akses'] = low5[course_cols].mean(axis=1)
                low5 = low5.nsmallest(5, 'avg_akses')[['NIM', 'avg_akses']]
                low5['NIM'] = low5['NIM'].astype(int)
                low5['avg_akses'] = (low5['avg_akses'] * 100).round(1).astype(str) + '%'
                st.dataframe(low5, use_container_width=True, hide_index=True)

    # ── RINGKASAN SEMUA KELAS ────────────────────────────────
    st.markdown("---")
    with st.expander("📋 Ringkasan Level Semua Kelas", expanded=False):
        rows = []
        for kelas in semua_kelas:
            dk  = df_alert[df_alert['Kode Kelas'] == kelas]
            a   = (_col_mean(dk, tp_all) + _col_mean(dk, tk_all)) / 2
            d   = ((_col_mean(dk, fd_all) + _col_mean(dk, ln_all)) / 2) * 10
            co  = ((_col_mean(dk, vbl_all) + _col_mean(dk, ppt_all)) / 2) * 10
            do  = (_col_mean(dk, tp_all) / 10 + d) / 2
            lv, ln, _, _, _ = _classify_level(a, d, do, co)
            rows.append({
                'Kelas':      kelas,
                'Assessment': round(a, 1),
                'Delivery':   round(d, 2),
                'Dosen':      round(do, 2),
                'Course':     round(co, 2),
                'Level':      lv,
                'Keterangan': ln
            })

        df_summary = pd.DataFrame(rows)
        order = {'L4': 0, 'L3': 1, 'L2': 2, 'L1': 3, 'Aman': 4}
        df_summary = df_summary.sort_values(
            'Level', key=lambda x: x.map(order)
        ).reset_index(drop=True)

        st.dataframe(df_summary, use_container_width=True, hide_index=True)

        # Distribusi level bar chart
        level_counts = df_summary['Level'].value_counts().reindex(
            ['L4', 'L3', 'L2', 'L1', 'Aman'], fill_value=0
        )
        fig, ax = plt.subplots(figsize=(7, 2.5))
        bar_c = ['#E53935', '#F68B1E', '#F68B1E', '#0096DA', '#0096DA']
        bars = ax.barh(level_counts.index, level_counts.values,
                       color=bar_c, height=0.45)
        for bar, val in zip(bars, level_counts.values):
            if val > 0:
                ax.text(bar.get_width() + 0.1,
                        bar.get_y() + bar.get_height()/2,
                        f'{val} kelas', va='center',
                        color='#1A2332', fontsize=9)
        ax.set_xlabel("Jumlah Kelas")
        ax.invert_yaxis()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.tight_layout(); st.pyplot(fig); plt.close()

        csv = df_summary.to_csv(index=False).encode('utf-8')
        st.download_button(
            "⬇ Download Ringkasan CSV",
            data=csv,
            file_name="level_semua_kelas.csv",
            mime="text/csv"
        )