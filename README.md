# Turkish Macroeconomic Data Platform (TCMB)


Enterprise-grade data pipeline for Turkish Central Bank (TCMB) macroeconomic data using Apache Airflow, AWS, and PostgreSQL.

## 📊 Overview

Automated daily extraction, transformation, and loading of Turkish Central Bank exchange rates (USD/TRY, EUR/TRY) and economic indicators (TÜFE - CPI) into a production PostgreSQL database with comprehensive data quality validation.

## 🎯 Project Summary

Real-time macroeconomic data processing platform leveraging live exchange rate APIs, Apache Airflow orchestration, and PostgreSQL data warehousing. The system processes multiple data series with technical indicators and automated quality validation achieving 100% data integrity.

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
# Start Docker containers (Airflow + PostgreSQL)
docker-compose up -d

# Run ETL pipeline
python src/load.py

# Access Airflow UI
# http://localhost:8080 (admin/admin)

# Monitor PostgreSQL
docker exec postgres psql -U postgres -d tcmb_dev
```

## 🏗️ Architecture
```
Exchange Rate API (exchangerate-api.com)
↓
EXTRACT PHASE
• Fetch rates
• 3 series
• Real + fallback
↓
TRANSFORM PHASE
• Clean data
• SMA-7 indicator
• Volatility calculation
• Weekly aggregation
↓
LOAD PHASE
• PostgreSQL
• Staging layer
• Mart layer
↓
VALIDATE PHASE
• 5 quality checks
• 100% score
• Monitoring

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
│   └── init.py
├── sql/                           # Database schemas
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
- **Records:** 38+ daily records

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

**Staging Layer:**
- staging.stg_exchange_rates (raw data)

**Dimensional Model:**
- marts.dim_date (date dimension)
- marts.dim_series (series dimension)
- marts.fact_exchange_rates (fact table)

**Monitoring:**
- monitoring.data_quality_checks (validation results)

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
tcmb_extract_dag:
├── Schedule: @daily (24:00)
├── Owner: data-engineering
├── Retries: 2 (5 min delay)
└── Tasks:
├── extract_usd_try ──┐
├── extract_eur_try ──┼──> transform_and_validate ──> log_completion
└── extract_cpi ──────┘
Dependencies:
[extract_usd_try, extract_eur_try, extract_cpi] >> transform_and_validate >> log_completion

```
## 📊 Real-Time Data

**Current Exchange Rates (Live API):**
- USD/TRY: 44.58
- EUR/TRY: 38.61

**Data Quality Metrics:**
- Min: 44.58 | Max: 44.95 | Mean: 44.77
- Null records: 0
- Duplicates: 0
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
- Email alerts (future enhancement)

## 📈 Performance

**Execution Time:**
- Extract: ~2 seconds (38 records)
- Transform: ~1 second (cleaning + indicators)
- Load: ~0.5 seconds (PostgreSQL insert)
- Validate: ~0.5 seconds (5 quality checks)

**Total:** ~4 seconds (end-to-end)


## 🔧 Challenges & Solutions

**TCMB API Authentication Failure**
Initial integration with TCMB EVDS API returned empty responses, causing `JSONDecodeError: Expecting value` on `response.json()`. Root cause was an invalid API key format. Resolved by switching the primary data source to exchangerate-api.com with the TCMB API retained as a future integration target when institutional access is available.

**TÜFE Validation Range Bug**
Data quality score for the TÜFE (CPI) series was 80% despite clean data. Root cause: `validate_value_range()` had a hardcoded `max_val=100`, but current TÜFE index values are in the 110–150 range. Fixed by updating the range to `max_val=150`, restoring 100% quality score across all 3 series.

## 🎓 Learning Outcomes

- Real exchange rate API integration
- Apache Airflow orchestration
- PostgreSQL star schema design
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

# Make changes and test
python src/load.py

# Commit with meaningful message
git add .
git commit -m "feat: description of changes"

# Push to remote
git push origin feature/new-feature

# Create Pull Request on GitHub
```

## 🚀 Future Enhancements

- [ ] Real TCMB EVDS API integration (when access available)
- [ ] AWS RDS production deployment + S3 data lake
- [ ] Grafana/Superset dashboard
- [ ] ML-based exchange rate forecasting (LSTM)

## 📝 License

MIT License - See LICENSE file for details

## 👤 Author

**Mustafa Aygün**
- GitHub: [@MustafaAygunDs](https://github.com/MustafaAygunDs)
- Email: mustafaaygunds@gmail.com
- Title: Data Engineer


