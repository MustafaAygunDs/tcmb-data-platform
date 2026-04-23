# Turkish Macroeconomic Data Platform (TCMB)

Enterprise-grade data pipeline for Turkish Central Bank (TCMB) macroeconomic data using Apache Airflow, dbt, and PostgreSQL.

## 📊 Overview

Automated daily extraction, transformation, and loading of Turkish Central Bank exchange rates (USD/TRY, EUR/TRY) and economic indicators (TÜFE - CPI) into a production PostgreSQL database. The pipeline includes a dbt transformation layer that builds a dimensional data model with automated data quality tests.

## 🎯 Project Summary

Real-time macroeconomic data processing platform leveraging live exchange rate APIs, Apache Airflow orchestration, dbt transformation, and PostgreSQL data warehousing. The system processes multiple data series with technical indicators and automated quality validation achieving 100% data integrity.

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Docker & Docker Compose
- Git

### Installation

```bash
# Clone repository
git clone https://github.com/MustafaAygunDs/tcmb-data-platform.git
cd tcmb-data-platform

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your configuration
```

### Run Pipeline

```bash
# Start PostgreSQL
docker-compose up -d postgres

# Run ETL pipeline (extract → transform → load to staging)
python src/load.py

# Run dbt transformation layer (staging → marts)
cd tcmb_dbt
dbt run
dbt test

# Or start full Airflow stack (runs everything automatically)
docker-compose up -d
# Access Airflow UI: http://localhost:8080 (admin/admin)
```

## 🏗️ Architecture

```
Exchange Rate API (exchangerate-api.com)
        │
        ▼
┌─────────────────┐
│  EXTRACT PHASE  │  fetch_tcmb_series()
│  3 series       │  USD/TRY · EUR/TRY · CPI
│  Real + fallback│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ TRANSFORM PHASE │  transform_pipeline()
│  Clean data     │
│  SMA-7          │
│  Volatility     │
│  Weekly OHLC    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   LOAD PHASE    │  load_etl_pipeline()
│  staging schema │  stg_exchange_rates
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   DBT LAYER     │  dbt run / dbt test
│  stg → marts   │
│  dim_date       │
│  dim_series     │
│  fact_exchange  │
│  17 data tests  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ VALIDATE PHASE  │  run_validation()
│  5 quality chks │
│  100% score     │
└─────────────────┘
```

## 📁 Project Structure

```
tcmb-data-platform/
├── dags/
│   └── tcmb_extract_dag.py        # Airflow orchestration
├── src/
│   ├── extract.py                 # Data extraction
│   ├── transform.py               # Data processing
│   ├── load.py                    # Database loading
│   ├── validate.py                # Quality validation
│   ├── utils.py                   # Helper functions
│   └── __init__.py
├── tcmb_dbt/                      # dbt transformation layer
│   ├── models/
│   │   ├── staging/
│   │   │   ├── sources.yml        # Source definitions
│   │   │   ├── stg_exchange_rates.sql
│   │   │   └── schema.yml
│   │   └── marts/
│   │       ├── dim_date.sql
│   │       ├── dim_series.sql
│   │       ├── fact_exchange_rates.sql
│   │       └── schema.yml
│   └── dbt_project.yml
├── data/                          # Raw data (gitignored)
├── logs/                          # Airflow logs (gitignored)
├── docker-compose.yml             # Container orchestration
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment template
├── .gitignore                     # Git rules
└── README.md                      # This file
```

## 🛠️ Tech Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Language | Python | 3.12 | Development |
| Orchestration | Apache Airflow | 2.10.3 | Task scheduling |
| Transformation | dbt-postgres | 1.10.0 | SQL modeling & testing |
| Database | PostgreSQL | 15 | Data warehouse |
| Container | Docker | 29.1.3 | Containerization |
| Processing | Pandas, NumPy | Latest | Data manipulation |
| API | exchangerate-api.com | Live | Exchange rates |
| Version Control | Git | Latest | Source control |

## 📈 Data Pipeline

### Extract Phase
- **Source:** Real exchange rate API (primary)
- **Fallback:** Mock data with realistic values
- **Series:** 3 macroeconomic indicators
  - TP.DK.USD.S (USD/TRY Exchange Rate)
  - TP.DK.EUR.S (EUR/TRY Exchange Rate)
  - TP.FG.AB09 (TÜFE - CPI Index)
- **Frequency:** Daily automated
- **Records:** 113+ daily records

### Transform Phase

**Data cleaning:**
- Remove null values
- Handle duplicates
- Validate date sequences

**Feature engineering:**
- SMA-7 (7-day moving average)
- Volatility (7-day standard deviation)
- Time-series aggregation

**Aggregation:**
- Daily to Weekly conversion
- Open, High, Low, Close (OHLC) prices
- Weekly volatility metrics

### Load Phase

**Staging Layer (Python ETL):**
- `staging.stg_exchange_rates` — raw cleaned data with SMA and volatility

### dbt Transformation Layer

Python ETL, veriyi staging'e yükledikten sonra dbt devreye girer ve staging'den boyutsal modeli inşa eder.

**Staging model** (`view`):
- `stg_exchange_rates` — sütun yeniden adlandırma, null filtresi

**Mart modelleri** (`table`):
- `marts.dim_date` — tarih boyutu (yıl, ay, gün, hafta, is_weekday)
- `marts.dim_series` — seri boyutu (USD/EUR/GBP eşleştirmeleri)
- `marts.fact_exchange_rates` — olgu tablosu (günlük değişim %, SMA-7, volatilite)

**Otomatik testler (17 adet):**
- `unique` + `not_null` — tüm birincil anahtarlar
- `relationships` — FK bütünlüğü (fact → dim)

```bash
cd tcmb_dbt
dbt run    # 4 model, ~0.3s
dbt test   # 17 test, 17/17 PASS
```

### Validate Phase

**5 Quality Checks:**
- ✅ No null dates
- ✅ No null values
- ✅ Valid range validation (1-150)
- ✅ Sequential dates verification
- ✅ Duplicate detection

**Result:** 100.0% Quality Score (5/5 checks passed)

## 🔄 Airflow DAG

```
tcmb_extract_dag
├── Schedule: @daily
├── Owner: data-engineering
└── Retries: 2 (5 min delay)

Task flow:

extract_usd_try ──┐
extract_eur_try ──┼──► transform_and_validate ──► load_to_db ──► dbt_run ──► dbt_test ──► log_completion
extract_cpi ──────┘
```

| Task | Type | Açıklama |
|------|------|----------|
| `extract_usd_try` | PythonOperator | USD/TRY verisini çeker |
| `extract_eur_try` | PythonOperator | EUR/TRY verisini çeker |
| `extract_cpi` | PythonOperator | TÜFE verisini çeker |
| `transform_and_validate` | PythonOperator | Temizler, göstergeler ekler, kalite skoru ≥90 kontrol |
| `load_to_db` | PythonOperator | `staging.stg_exchange_rates`'e yükler |
| `dbt_run` | BashOperator | 4 dbt modelini çalıştırır |
| `dbt_test` | BashOperator | 17 veri testini koşturur |
| `log_completion` | PythonOperator | Pipeline tamamlanma kaydı |

## 📊 Real-Time Data

**Current Exchange Rates (Live API):**
- USD/TRY: 44.95
- EUR/TRY: 38.34

**Data Quality Metrics:**
- Records loaded: 113
- dbt models: 4/4 OK
- dbt tests: 17/17 PASS
- Quality score: 100%

## 🔐 Security

✅ Credentials in .env (not in Git)
✅ .gitignore properly configured
✅ No API keys in repository
✅ Environment variables for secrets
✅ SQL parameterized queries
✅ Input validation

## 🚨 Error Handling

- Try-except blocks for API calls
- Automatic failover to exchangerate-api.com when primary TCMB API is unavailable
- Comprehensive logging
- Database transaction rollback
- Airflow retries (2x, 5 min delay)

## 📈 Performance

**Execution Time:**
- Extract: ~2 seconds (113 records)
- Transform: ~1 second (cleaning + indicators)
- Load: ~0.5 seconds (PostgreSQL insert)
- dbt run: ~0.3 seconds (4 models)
- dbt test: ~0.3 seconds (17 tests)
- Validate: ~0.5 seconds (5 quality checks)

**Total:** ~5 seconds (end-to-end)

## 🔧 Challenges & Solutions

**TCMB API Authentication Failure**
Initial integration with TCMB EVDS API returned empty responses, causing `JSONDecodeError: Expecting value` on `response.json()`. Root cause was an invalid API key format. Resolved by switching the primary data source to exchangerate-api.com with the TCMB API retained as a future integration target when institutional access is available.

**TÜFE Validation Range Bug**
Data quality score for the TÜFE (CPI) series was 80% despite clean data. Root cause: `validate_value_range()` had a hardcoded `max_val=100`, but current TÜFE index values are in the 110–150 range. Fixed by updating the range to `max_val=150`, restoring 100% quality score across all 3 series.

**SQLAlchemy 1.4 / pandas 2.x Incompatibility**
`df.to_sql()` failed with `AttributeError: 'Connection' object has no attribute 'cursor'` because pandas 2.x dropped support for SQLAlchemy 1.4 connection objects. Resolved by upgrading SQLAlchemy to 2.x in the local venv (Airflow runs in Docker so its dependency is unaffected) and using `engine.url.render_as_string(hide_password=False)` to pass the connection URL directly to pandas.

**PostgreSQL Role Missing After Volume Reuse**
`dbt debug` returned `FATAL: role "postgres" does not exist` because the existing `postgres_data` Docker volume had been initialized by an Airflow-managed instance that created only the `airflow` role. Resolved by connecting via the `airflow` superuser (local socket trust auth) and creating the `postgres` role and `tcmb_dev` database manually — without discarding the volume.

## 🎓 Learning Outcomes

- Real exchange rate API integration
- Apache Airflow orchestration
- PostgreSQL star schema design
- dbt dimensional modeling (staging → marts)
- dbt automated data testing (17 tests)
- Data quality framework implementation
- Docker containerization
- Git workflow and clean commits
- Technical indicators calculation
- Time-series data aggregation
- Production-ready code structure
- Professional documentation

## 🔄 Development Workflow

```bash
# Create feature branch
git checkout -b feature/new-feature

# Run ETL locally
python src/load.py

# Run dbt locally
cd tcmb_dbt && dbt run && dbt test

# Commit with meaningful message
git add .
git commit -m "feat: description of changes"

# Push to remote
git push origin feature/new-feature
```

## 🚀 Future Enhancements

- [ ] Real TCMB EVDS API integration (when access available)
- [ ] AWS RDS production deployment + S3 data lake
- [ ] Grafana/Superset dashboard connected to mart tables
- [ ] ML-based exchange rate forecasting (LSTM)
- [ ] dbt snapshots for slowly changing dimensions

## 📝 License

MIT License - See LICENSE file for details

## 👤 Author

**Mustafa Aygün**
- GitHub: [@MustafaAygunDs](https://github.com/MustafaAygunDs)
- Email: mustafaaygunds@gmail.com
- Title: Data Engineer
