# Deployment Guide

## Local Development Setup

### 1. PostgreSQL Setup
```bash
# Windows: Start PostgreSQL service
# macOS: brew services start postgresql

# Create database and schema
createdb -U postgres student_risk_db

# Connect and run schema
psql -U postgres -d student_risk_db -f docs/schema.sql
```

### 2. Environment Setup
```bash
# Create .env
cp .env.example .env

# Edit .env with credentials
DB_PASSWORD=your_actual_password
```

### 3. Run ETL
```bash
# First time setup
python -m etl.loader

# Check logs
tail -f logs/etl_pipeline.log
```

### 4. Start Dashboard
```bash
streamlit run app.py
```

## Streamlit Cloud Deployment

### Prerequisites
- GitHub account with repo pushed
- Streamlit Cloud account (connect GitHub)

### Steps

1. **Push to GitHub** (see Step 3 below)

2. **Setup .python-version**
   - File must exist at root: `.python-version`
   - Content: `3.11`
   - This forces Streamlit Cloud to use Python 3.11

3. **Streamlit Cloud Dashboard**
   - Go to https://share.streamlit.io/
   - Click "New app"
   - Repository: `student-risk-dashboard`
   - Branch: `main`
   - Main file path: `app.py`
   - Click Deploy

4. **Add Secrets**
   - In app settings, go to "Secrets"
   - Add:
   ```
    DB_HOST = "your-db-host"
    DB_PORT = "5432"
    DB_NAME = "student_risk_db"
    DB_USER = "postgres"
    DB_PASSWORD = "your-password"
    ```

### Limitations on Cloud
- APScheduler runs locally only (not on Streamlit servers)
- For cloud scheduling, use:
  - GitHub Actions + cron job + Python script
  - Streamlit's beta task scheduler
  - External services (e.g., AWS Lambda, Cloud Functions)

## GitHub Actions Scheduled ETL (Optional)

Create `.github/workflows/etl-schedule.yml`:

```yaml
name: Scheduled ETL

on:
  schedule:
    - cron: '0 2 * * *'  # Daily 2 AM UTC

jobs:
  etl:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python -m etl.loader
        env:
          DB_HOST: ${{ secrets.DB_HOST }}
          DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
```

---

**For detailed setup, see README.md**