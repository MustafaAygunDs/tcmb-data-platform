"""
Load module: Database loading
"""
import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Create database connection"""
    rds_host = os.getenv('RDS_HOST', 'localhost')
    rds_user = os.getenv('RDS_USER', 'postgres')
    rds_password = os.getenv('RDS_PASSWORD', 'postgres')
    rds_port = os.getenv('RDS_PORT', '5432')
    rds_db = os.getenv('RDS_DB', 'tcmb_dev')
    
    connection_string = f"postgresql://{rds_user}:{rds_password}@{rds_host}:{rds_port}/{rds_db}"
    engine = create_engine(connection_string)
    return engine

def create_schema(engine):
    """Create database schema"""
    print("[LOAD] Creating schema...")
    
    with engine.connect() as conn:
        # Staging
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS staging.stg_exchange_rates (
                id SERIAL PRIMARY KEY,
                tarih DATE NOT NULL,
                unvan VARCHAR(50),
                deger DECIMAL(10, 4),
                sma_7 DECIMAL(10, 4),
                volatility_7 DECIMAL(10, 4),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Mart - Dimensions
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS marts.dim_date (
                date_id DATE PRIMARY KEY,
                year INT,
                month INT,
                day INT,
                week INT
            )
        """))
        
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS marts.dim_series (
                series_id SERIAL PRIMARY KEY,
                series_code VARCHAR(20) UNIQUE,
                series_name VARCHAR(100)
            )
        """))
        
        # Mart - Fact
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS marts.fact_exchange_rates (
                fact_id SERIAL PRIMARY KEY,
                date_id DATE,
                series_id INT,
                rate DECIMAL(10, 4),
                sma_7 DECIMAL(10, 4),
                volatility DECIMAL(10, 4),
                FOREIGN KEY (date_id) REFERENCES marts.dim_date(date_id),
                FOREIGN KEY (series_id) REFERENCES marts.dim_series(series_id)
            )
        """))
        
        conn.commit()
    
    print("[SUCCESS] Schema created")

def load_to_staging(engine, df: pd.DataFrame, table_name: str = "stg_exchange_rates"):
    """Load data to staging layer"""
    print(f"[LOAD] Loading {len(df)} records to staging...")
    
    try:
        df.to_sql(
            table_name,
            engine,
            schema='staging',
            if_exists='append',
            index=False
        )
        print(f"[SUCCESS] Loaded {len(df)} records")
    except Exception as e:
        print(f"[ERROR] {e}")
        raise

def load_etl_pipeline(df: pd.DataFrame):
    """Full ETL load pipeline"""
    print("[PIPELINE] Starting load phase...")
    
    engine = get_db_connection()
    
    # Create schema
    create_schema(engine)
    
    # Load to staging
    load_to_staging(engine, df)
    
    print("[COMPLETE] ETL pipeline finished")
    return True

if __name__ == "__main__":
    from extract import fetch_tcmb_series
    from transform import transform_pipeline
    
    # Test
    df = fetch_tcmb_series("TP.DK.USD.S", "2026-03-01")
    result = transform_pipeline(df)
    
    # Uncomment to test with real database
    # load_etl_pipeline(result['daily'])
