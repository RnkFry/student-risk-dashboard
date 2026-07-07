import streamlit as st
import matplotlib.pyplot as plt

def risk_level(prob):
    if prob >= 0.7:   return 'High Risk'
    elif prob >= 0.4: return 'Medium Risk'
    else:             return 'Low Risk'

def risk_color(level):
    return {'High Risk': '#E53935', 'Medium Risk': '#F68B1E', 'Low Risk': '#0096DA'}[level]

def set_plot_style():
    plt.rcParams.update({
        'figure.facecolor':  '#FFFFFF',
        'axes.facecolor':    '#FFFFFF',
        'axes.edgecolor':    '#D1DCE8',
        'axes.labelcolor':   '#374151',
        'xtick.color':       '#6B7280',
        'ytick.color':       '#6B7280',
        'grid.color':        '#EEF4FA',
        'text.color':        '#1A2332',
        'axes.titlecolor':   '#1A2332',
        'axes.titlesize':    12,
        'axes.labelsize':    10,
        'xtick.labelsize':   9,
        'ytick.labelsize':   9,
    })

def inject_css():
    st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {
            display: none !important;
        }
        /* ── BINUS COLOR PALETTE ──────────────────────────────────
           Biru  : #0096DA   Orange: #F68B1E   Abu  : #6B7280
           Light : #F0F4F8   Border: #D1DCE8   Text : #1A2332
        ─────────────────────────────────────────────────────────── */
        @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'DM Sans', sans-serif;
            color: #1A2332;
        }

        .main { background-color: #F7F9FC; }

        .stApp {
            background: linear-gradient(150deg, #FFFFFF 0%, #EEF4FA 60%, #E6F2FA 100%);
        }

        /* ── SIDEBAR ─────────────────────────────────────────── */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0096DA 0%, #0078B5 100%);
            border-right: none;
        }

        section[data-testid="stSidebar"] * {
            color: #FFFFFF !important;
        }

        section[data-testid="stSidebar"] .stMarkdown h2 {
            color: #FFFFFF !important;
            font-family: 'DM Serif Display', serif;
            font-size: 1.1rem;
        }

        section[data-testid="stSidebar"] hr {
            border-color: rgba(255,255,255,0.25) !important;
        }

        section[data-testid="stSidebar"] [data-testid="stRadio"] label {
            color: rgba(255,255,255,0.85) !important;
            font-size: 0.9rem;
        }

        section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
            color: #FFFFFF !important;
        }

        section[data-testid="stSidebar"] [aria-checked="true"] + div label,
        section[data-testid="stSidebar"] [data-testid="stRadio"] [aria-checked="true"] ~ div {
            color: #F68B1E !important;
            font-weight: 600 !important;
        }

        /* ── HEADER ──────────────────────────────────────────── */
        .dashboard-header {
            background: linear-gradient(135deg, #0096DA 0%, #0078B5 100%);
            border: none;
            border-radius: 16px;
            padding: 2rem 2.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 20px rgba(0,150,218,0.25);
        }

        .dashboard-title {
            font-family: 'DM Sans', sans-serif;
            font-size: 1.6rem;
            font-weight: 700;
            color: #FFFFFF;
            margin: 0;
            letter-spacing: -0.3px;
        }

        .dashboard-subtitle {
            color: rgba(255,255,255,0.75);
            font-size: 0.9rem;
            margin: 0.3rem 0 0;
            font-weight: 300;
        }

        /* ── METRIC CARDS ────────────────────────────────────── */
        .metric-row {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1rem;
            margin-bottom: 1.5rem;
        }

        .metric-card {
            background: #FFFFFF;
            border: 1px solid #D1DCE8;
            border-radius: 12px;
            padding: 1.25rem 1.5rem;
            position: relative;
            overflow: hidden;
            box-shadow: 0 1px 6px rgba(0,0,0,0.06);
        }

        .metric-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0;
            width: 3px; height: 100%;
            border-radius: 12px 0 0 12px;
        }

        .metric-card.high::before   { background: #E53935; }
        .metric-card.medium::before { background: #F68B1E; }
        .metric-card.low::before    { background: #0096DA; }
        .metric-card.total::before  { background: #6B7280; }

        .metric-label {
            font-size: 0.72rem;
            color: #6B7280;
            text-transform: uppercase;
            letter-spacing: 0.09em;
            font-weight: 600;
            margin-bottom: 0.4rem;
        }

        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: #1A2332;
            line-height: 1;
            font-family: 'DM Serif Display', serif;
        }

        .metric-value.high   { color: #E53935; }
        .metric-value.medium { color: #F68B1E; }
        .metric-value.low    { color: #0096DA; }

        .metric-sub {
            font-size: 0.72rem;
            color: #9CA3AF;
            margin-top: 0.3rem;
        }

        /* ── SECTION HEADER ──────────────────────────────────── */
        .section-header {
            font-family: 'DM Serif Display', serif;
            font-size: 1.25rem;
            color: #1A2332;
            margin: 1.5rem 0 0.75rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #0096DA;
        }

        /* ── RISK BADGES ─────────────────────────────────────── */
        .risk-badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        .badge-high   { background: #FEE2E2; color: #E53935; border: 1px solid #FECACA; }
        .badge-medium { background: #FEF3E2; color: #F68B1E; border: 1px solid #FDE68A; }
        .badge-low    { background: #E0F2FE; color: #0096DA; border: 1px solid #BAE6FD; }

        /* ── CONTAINERS ──────────────────────────────────────── */
        .plot-container {
            background: #FFFFFF;
            border: 1px solid #D1DCE8;
            border-radius: 12px;
            padding: 1.25rem;
            box-shadow: 0 1px 6px rgba(0,0,0,0.05);
        }

        .student-card {
            background: #FFFFFF;
            border: 1px solid #D1DCE8;
            border-radius: 12px;
            padding: 1.25rem 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 1px 6px rgba(0,0,0,0.05);
        }

        .student-card .label {
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #9CA3AF;
            margin-bottom: 2px;
        }

        .student-card .value {
            font-size: 1rem;
            color: #1A2332;
            font-weight: 500;
        }

        /* ── STREAMLIT OVERRIDES ─────────────────────────────── */
        .stDataFrame {
            border-radius: 12px !important;
            overflow: hidden !important;
        }

        .stSelectbox > div > div,
        .stSlider > div > div {
            background: #FFFFFF !important;
            border-color: #D1DCE8 !important;
            color: #1A2332 !important;
        }

        .stTabs [data-baseweb="tab-list"] {
            background: #EEF4FA;
            border-radius: 10px;
            gap: 8px;
            padding: 6px 8px;
            border: 1px solid #D1DCE8;
        }

        .stTabs [data-baseweb="tab"] {
            color: #6B7280;
            font-size: 0.85rem;
            font-weight: 500;
            padding: 8px 20px !important;
            border-radius: 7px !important;
        }

        .stTabs [aria-selected="true"] {
            background: #0096DA !important;
            color: #FFFFFF !important;
            border-radius: 7px !important;
            padding: 8px 20px !important;
        }

        /* ── SLIDER (sidebar) ────────────────────────────────── */
        section[data-testid="stSidebar"] [data-testid="stSlider"] > div > div > div {
            background: rgba(255,255,255,0.25) !important;
        }

        section[data-testid="stSidebar"] [data-testid="stSlider"] [role="slider"] {
            background: #F68B1E !important;
            border: 2px solid #FFFFFF !important;
            box-shadow: 0 0 6px rgba(0,0,0,0.2) !important;
        }

        section[data-testid="stSidebar"] [data-testid="stSlider"] div[data-baseweb="slider"] > div:first-child {
            background: rgba(255,255,255,0.2) !important;
        }

        section[data-testid="stSidebar"] [data-testid="stSlider"] div[data-baseweb="slider"] > div:first-child > div:first-child {
            background: #F68B1E !important;
        }

        section[data-testid="stSidebar"] [data-testid="stSlider"] p {
            color: rgba(255,255,255,0.85) !important;
            font-size: 0.82rem !important;
        }
        .insight-box {
            background: #EEF4FA;
            border: 1px solid #BAE6FD;
            border-left: 3px solid #0096DA;
            border-radius: 0 8px 8px 0;
            padding: 0.875rem 1.125rem;
            margin: 0.75rem 0;
            font-size: 0.85rem;
            color: #374151;
            line-height: 1.6;
        }

        .insight-box strong { color: #1A2332; }

        /* ── TYPOGRAPHY ──────────────────────────────────────── */
        h1, h2, h3 { color: #1A2332 !important; }
        p, li { color: #374151; }

        #MainMenu, footer, header { visibility: hidden; }
        .block-container { padding-top: 1.5rem; }

        /* ── AT-RISK STUDENT CARDS ───────────────────────────── */
        .risk-student-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
            gap: 0.75rem;
            margin-top: 0.75rem;
        }

        .risk-student-card {
            background: #FFFFFF;
            border: 1px solid #D1DCE8;
            border-radius: 12px;
            padding: 1rem 1.25rem;
            position: relative;
            overflow: hidden;
            box-shadow: 0 1px 6px rgba(0,0,0,0.05);
        }

        .risk-student-card.card-high   { border-left: 3px solid #E53935; }
        .risk-student-card.card-medium { border-left: 3px solid #F68B1E; }

        .risk-student-nim {
            font-family: 'DM Serif Display', serif;
            font-size: 1rem;
            color: #1A2332;
            font-weight: 600;
            margin-bottom: 0.25rem;
        }

        .risk-student-prob { font-size: 0.78rem; margin-bottom: 0.6rem; }

        .risk-factor-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 3px 0;
            border-bottom: 1px solid #EEF4FA;
            font-size: 0.78rem;
        }

        .risk-factor-row:last-child { border-bottom: none; }
        .risk-factor-name  { color: #6B7280; flex: 1; }

        .risk-factor-val {
            color: #1A2332;
            font-weight: 500;
            min-width: 48px;
            text-align: right;
            margin-right: 8px;
        }

        .risk-factor-bar-wrap {
            width: 70px; height: 5px;
            background: #E5E7EB;
            border-radius: 3px;
            overflow: hidden;
        }

        .risk-factor-bar-fill { height: 100%; border-radius: 3px; }

        .bar-danger  { background: #E53935; }
        .bar-warning { background: #F68B1E; }
        .bar-ok      { background: #0096DA; }

        .no-risk-box {
            background: #E0F2FE;
            border: 1px solid #BAE6FD;
            border-radius: 12px;
            padding: 1.25rem 1.5rem;
            color: #0078B5;
            font-weight: 500;
            font-size: 0.9rem;
            margin-top: 0.75rem;
        }
    </style>
    """, unsafe_allow_html=True)