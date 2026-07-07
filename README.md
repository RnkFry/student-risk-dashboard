# Student Risk Prediction Dashboard

A production-grade ML dashboard system that predicts student dropout risk and provides actionable learning outcome analysis for higher education institutions.

## Overview

The system uses a machine learning model (Random Forest) to identify at-risk students based on behavioral and academic features, with interpretable SHAP analysis and LO (Learning Outcome) breakdown for course improvement recommendations.

**Status**: Tier 1 ETL Pipeline Complete ✅

## Architecture

### Database Schema
- **PostgreSQL 17** on `student_risk_db`
- **3 core tables** in `risk_data` schema:
  - `raw_student_data` — 5725 raw records from Excel (all columns)
  - `processed_student_data` — aggregated features for dashboard + risk scores + LO breakdown
  - `etl_logs` — audit trail (job name, status, timing, error tracking)

See [Database Schema Diagram](#data-schema) below.

### ETL Pipeline (Tier 1)

**Components**:
1. **Extract** (`etl/extractor.py`) — Load from Excel + Google Sheets → PostgreSQL raw table
2. **Transform** (`etl/transformer.py`) — Aggregate scores, calculate LO, compute risk probability
3. **Load** (`etl/loader.py`) — Combined pipeline runner
4. **Scheduler** (`etl/scheduler.py`) — APScheduler runs daily at 2:00 AM

**Data Flow**:

### Data Flow

```text
Excel (5725 rows)
        │
        ▼
[Extract] → raw_student_data (PostgreSQL)
        │
        ▼
[Transform] → Aggregate + LO Calculation + Risk Scoring
        │
        ▼
[Load] → processed_student_data (PostgreSQL)
        │
        ▼
Streamlit Dashboard (Real-time Query)
```

**Performance**: ~12 seconds end-to-end (5725 records)

### Dashboard (Streamlit)

**Pages**:
- **📊 Overview** — Risk distribution, metric cards, model performance
- **🔍 SHAP Global** — Summary Plot, Bar Plot, Dependence Plot (feature importance)
- **👤 Individual Analysis** — Per-student SHAP Waterfall explanation
- **📋 Risk Table** — Filterable risk data with CSV export
- **🚨 Class Alert** — Real-time monitoring by class & session
- **🏫 Rekomendasi Prodi** — L1–L4 classification + LO breakdown per course

## Installation

### Prerequisites
- Python 3.11+
- PostgreSQL 17+
- pip

### Setup

1. **Clone repository**
```bash
   git clone https://github.com/YOUR_USERNAME/student-risk-dashboard.git
   cd Student-Risk-Dashboard
```

2. **Create virtual environment**
```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
   pip install -r requirements.txt
```

4. **Setup PostgreSQL**
   - Create database: `student_risk_db`
   - Run schema setup (SQL script in docs/schema.sql)

5. **Configure environment**
   - Create `.env` file in root:
    ```env
    DB_HOST=localhost
    DB_PORT=5432
    DB_NAME=student_risk_db
    DB_USER=postgres
    DB_PASSWORD=your_password
    ```

6. **Run ETL once**
```bash
   python -m etl.loader
```

7. **Start dashboard**
```bash
   streamlit run app.py
```

   Open http://localhost:8501

## Project Structure

```text
Student-Risk-Dashboard/
├── config/
│   └── database.py
├── etl/
│   ├── config.py
│   ├── extractor.py
│   ├── transformer.py
│   ├── loader.py
│   └── scheduler.py
├── models/
│   ├── model.pkl
│   └── scaler_logistik_v4.pkl
├── pages/
│   ├── overview.py
│   ├── shap_global.py
│   ├── individual.py
│   ├── risk_table.py
│   ├── class_alert.py
│   └── rekomendasi_prodi.py
├── utils/
│   ├── ui.py
│   ├── loader.py
│   ├── features.py
│   ├── recommendation.py
│   └── __init__.py
├── data/
│   └── data.xlsx
├── logs/
│   └── etl_pipeline.log
├── .env
├── .gitignore
├── .python-version
├── app.py
├── requirements.txt
└── README.md
```


## Features

### Machine Learning
- **Model**: Random Forest (pre-trained on 5725 students)
- **14 Features**: Academic scores, engagement metrics, behavioral patterns
- **Risk Threshold**: 0.6 probability → High Risk
- **Interpretability**: SHAP (TreeExplainer) for local + global explanations

### Learning Outcome Analysis
- **3 LOs** tracked per course (LO1, LO2, LO3)
- **Weighted scoring** from assessments (TP, TK, Quiz, Final Exam)
- **Target**: ≥65% achievement per LO
- **Breakdown**: Individual task contribution + radar chart visualization

### Data Quality
- **Extraction**: Type validation, NaN handling, deduplication by `kode_gabungan`
- **Transformation**: Null filling (0), feature scaling, risk label binary conversion
- **Loading**: Atomic TRUNCATE + INSERT, batch operation (page_size=1000)
- **Logging**: Every job tracked with timestamp, status, record counts, error messages

## Usage

### Run ETL Manually
```bash
# Extract + Transform + Load in one command
python -m etl.loader

# Output:
# ============================================================
# 🚀 STARTING COMPLETE ETL PIPELINE
# ...
# ✅ ETL PIPELINE COMPLETED SUCCESSFULLY
# ⏱️  Total duration: 12.45 seconds
# ============================================================
```

### Start Dashboard
```bash
streamlit run app.py
```

Navigate to the 6 pages via sidebar. Adjust Risk Threshold slider in Settings.

### Check ETL Logs
```sql
-- PostgreSQL
SELECT * FROM risk_data.etl_logs ORDER BY started_at DESC LIMIT 5;
```

## Data Sources

| Source | Frequency | Format | Records |
|--------|-----------|--------|---------|
| `data.xlsx` | Manual upload | Excel workbook | 5725 students |
| Google Sheets (Alert) | Real-time | CSV export | Per class |
| Model | Pre-trained | joblib .pkl | Random Forest |

## Database Tables

### raw_student_data (5725 rows)
- **PK**: `id`
- **Key cols**: `nim`, `kode_kelas`, `kode_periode`, `kode_gabungan`
- **Assessment**: `tp1_total`, `tp2_total`, `tk1_total`...`tk4_total`, `quiz1_total`, `quiz2_total`, `final_exam_total`
- **Engagement**: `fd1`...`fd10`, `ln1`...`ln10`, `ppt1`...`ppt10`, `vbl1`...`vbl10`
- **Behavioral**: `avg_days_before_deadline`, `pct_late_submission`, `tle_p1`...`tle_p9`
- **Computed**: `avg_tp_awal`, `avg_tk_awal`, `trend_tp`, `trend_tk`, `early_academic_score`

### processed_student_data (5725 rows)
- **PK**: `id`
- **UK**: `kode_gabungan` (unique per student-semester)
- **Identifiers**: `nim`, `kode_kelas`, `kode_periode`
- **Features**: `avg_tp`, `avg_tk`
- **Predictions**: `risk_probability` (0.0–1.0), `risk_label` (0/1)
- **LO Scores**: `lo1_score`, `lo2_score`, `lo3_score` (0.0–100.0)

### etl_logs
- `job_name`: "extract_and_load" | "transform_and_load"
- `status`: "SUCCESS" | "FAILED"
- `records_processed`: integer
- `records_failed`: integer
- `error_message`: text (if failed)
- `started_at`, `ended_at`: timestamps

## Roadmap

### Tier 1 (Complete ✅)
- [x] Extract from Excel + Google Sheets
- [x] Transform: aggregation, LO calculation, risk scoring
- [x] Load to PostgreSQL with logging
- [x] APScheduler daily execution
- [x] Streamlit dashboard integration

### Tier 2 (Planned)
- [ ] Migrate to Apache Airflow for enterprise orchestration
- [ ] Add Grafana monitoring dashboard
- [ ] Implement data versioning (dbt + Git)
- [ ] Add incremental loading (only new/updated records)
- [ ] Unit tests + data quality assertions

### Tier 3 (Future)
- [ ] Model retraining pipeline
- [ ] API endpoint for risk predictions
- [ ] Integration with university SIS

## Deployment

### Local Development
```bash
python -m etl.loader  # Manual ETL
streamlit run app.py  # Dashboard
```

### Streamlit Cloud
1. Push to GitHub (with `.python-version` file forcing Python 3.11)
2. Connect repo to Streamlit Cloud
3. Set secrets in dashboard (DB credentials)
4. Auto-deploys on git push

**Note**: Scheduler runs locally only. For cloud scheduling, use GitHub Actions or Streamlit's beta task scheduler.

## Performance

| Operation | Time | Records | Throughput |
|-----------|------|---------|-----------|
| Extract | ~3s | 5725 | 1,908/sec |
| Transform | ~5s | 5725 | 1,145/sec |
| Load | ~2s | 5725 | 2,862/sec |
| **Total** | **~12s** | **5725** | **477/sec** |

Dashboard queries: <500ms (processed_student_data, indexed by nim & kode_kelas)

## Contributing

1. Fork repository
2. Create feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature/your-feature`
5. Submit pull request

## License

MIT License — See LICENSE file for details

## Authors

- **Adhit** — Lead Data Engineer & ML Engineer
- Binus University Student Risk Prediction System

## Contact

- GitHub Issues: [Report bugs or request features](https://github.com/YOUR_USERNAME/student-risk-dashboard/issues)
- Email: alifadhitya13@gmail.com

---

## Database Schema

```text
PostgreSQL
└── Database: student_risk_db
    └── Schema: risk_data
        ├── raw_student_data
        │   └── Raw data imported from Excel (5725 rows)
        │
        ├── processed_student_data
        │   └── Aggregated features, risk scores, and LO breakdown
        │
        └── etl_logs
            └── ETL execution history and audit logs
```

## ETL Pipeline

```text
data.xlsx
    │
    ▼
Extract
    │
    ▼
raw_student_data
    │
    ▼
Transform
    ├── Feature Engineering
    ├── Learning Outcome Calculation
    └── Risk Prediction
    │
    ▼
processed_student_data
    │
    ▼
Streamlit Dashboard
    │
    ▼
APScheduler (Daily 02:00 AM)
```

**Built with**: Python 3.11 | PostgreSQL 17 | Streamlit | scikit-learn | SHAP | joblib