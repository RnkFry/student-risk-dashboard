import pandas as pd

def create_features(df):
    df = df.copy()
    df['FD_ratio']  = df[['FD1','FD2','FD3']].mean(axis=1)
    df['VBL_ratio'] = df[['VBL1','VBL2','VBL3']].mean(axis=1)

    # FIX #3: Kolom TK pakai nama yang benar (TK1, TK2 — bukan TK1_Total)
    df['Avg_TP_awal'] = df[['TP1']].mean(axis=1)
    df['Avg_TK_awal'] = df[['TK1','TK2']].mean(axis=1)

    df['Quiz1_score']        = df['TP1']
    df['Avg_LO1_awal']       = df['TP1']
    df['Trend_TP']           = 0
    df['Trend_TK']           = 0
    df['Early_academic_score'] = df['TP1']

    df['Avg_days_before_deadline'] = 0
    df['pct_submission_H_minus_1'] = 0
    df['pct_late_submission']      = 0
    df['Download_ratio']           = 0
    df['Avg_TLE']                  = 0
    df['Count_TLE_below_3']        = 0

    return df

def calculate_risk(df, model, feature_cols):
    X = df[feature_cols].fillna(0)
    probs = model.predict_proba(X)[:, 1]

    df = df.copy()
    df['risk_prob']  = probs
    df['risk_label'] = (probs > 0.6).astype(int)
    high_risk_pct    = df['risk_label'].mean()

    return df, high_risk_pct

def get_top_feature(model, feature_cols):
    importances = model.feature_importances_
    feat_df = pd.DataFrame({
        'Feature':    feature_cols,
        'Importance': importances
    }).sort_values(by='Importance', ascending=False)
    return feat_df.iloc[0]['Feature']

def calculate_scores(df, tp_cols, tk_cols, vc_cols, fd_cols, ppt_cols, ln_cols, vbl_cols):
    def safe_mean(columns):
        existing = [c for c in columns if c in df.columns]
        if not existing:
            return 0.0
        return df[existing].mean().mean()

    performance = safe_mean(tp_cols + tk_cols)
    engagement  = safe_mean(vc_cols + fd_cols)
    resource    = safe_mean(ppt_cols + ln_cols + vbl_cols)
    return performance, engagement, resource