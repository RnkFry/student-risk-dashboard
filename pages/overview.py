import streamlit as st
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, recall_score, precision_score, f1_score

def render():
    # Ambil data dari session_state
    risk_df      = st.session_state.risk_df
    threshold    = st.session_state.threshold
    high_count   = st.session_state.high_count
    medium_count = st.session_state.medium_count
    low_count    = st.session_state.low_count
    y_test       = st.session_state.y_test
    y_pred       = st.session_state.y_pred

    # Render UI Halaman Overview
    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card total">
            <div class="metric-label">Total Mahasiswa</div>
            <div class="metric-value">{len(risk_df)}</div>
            <div class="metric-sub">Data test set (20%)</div>
        </div>
        <div class="metric-card high">
            <div class="metric-label">High Risk</div>
            <div class="metric-value high">{high_count}</div>
            <div class="metric-sub">Prob ≥ 0.7 → Prioritas intervensi</div>
        </div>
        <div class="metric-card medium">
            <div class="metric-label">Medium Risk</div>
            <div class="metric-value medium">{medium_count}</div>
            <div class="metric-sub">Prob 0.4–0.7 → Perlu dipantau</div>
        </div>
        <div class="metric-card low">
            <div class="metric-label">Low Risk</div>
            <div class="metric-value low">{low_count}</div>
            <div class="metric-sub">Prob < 0.4 → Kondisi aman</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown('<p class="section-header">Distribusi Risk Level</p>', unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(6, 3.5))
        order  = ['High Risk', 'Medium Risk', 'Low Risk']
        colors = ['#E53935', '#F68B1E', '#0096DA']
        counts = [high_count, medium_count, low_count]
        bars = ax.barh(order, counts, color=colors, height=0.5)
        for bar, count in zip(bars, counts):
            ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                    f'{count}', va='center', ha='left', color='#1A2332', fontsize=10)
        ax.set_xlabel("Jumlah Mahasiswa")
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.invert_yaxis()
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col2:
        st.markdown('<p class="section-header">Distribusi Probabilitas</p>', unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(6, 3.5))
        ax.hist(risk_df[risk_df['Risk_Level'] == 'Low Risk']['Probability'],
                bins=20, color='#0096DA', alpha=0.7, label='Low Risk')
        ax.hist(risk_df[risk_df['Risk_Level'] == 'Medium Risk']['Probability'],
                bins=20, color='#F68B1E', alpha=0.7, label='Medium Risk')
        ax.hist(risk_df[risk_df['Risk_Level'] == 'High Risk']['Probability'],
                bins=20, color='#E53935', alpha=0.7, label='High Risk')
        ax.axvline(threshold, color='#1A2332', linestyle='--', linewidth=1.5,
                   label=f'Threshold ({threshold})')
        ax.set_xlabel("Probabilitas Risk")
        ax.set_ylabel("Jumlah Mahasiswa")
        ax.legend(fontsize=8, facecolor='#FFFFFF', edgecolor='#D1DCE8', labelcolor='#374151')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    st.markdown('<p class="section-header">Model Performance Summary</p>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Accuracy",  f"{accuracy_score(y_test, y_pred):.1%}")
    col2.metric("Recall",    f"{recall_score(y_test, y_pred):.1%}")
    col3.metric("Precision", f"{precision_score(y_test, y_pred):.1%}")
    col4.metric("F1-Score",  f"{f1_score(y_test, y_pred):.3f}")

    st.markdown("""
    <div class="insight-box">
        <strong>Cara membaca dashboard ini:</strong> Threshold default 0.4 berarti mahasiswa dengan probabilitas ≥ 0.4 dikategorikan Risk.
        Ubah threshold di sidebar kiri untuk melihat bagaimana jumlah deteksi berubah.
        High Risk (≥0.7) adalah mahasiswa yang paling butuh intervensi segera.
    </div>
    """, unsafe_allow_html=True)