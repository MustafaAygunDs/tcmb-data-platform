"""
TCMB Data Extraction DAG
Daily scheduled ETL pipeline with dbt transformation layer
"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import sys
sys.path.insert(0, '/opt/airflow/src')

from extract import fetch_tcmb_series
from transform import transform_pipeline
from validate import run_validation
from load import load_etl_pipeline

default_args = {
    'owner': 'data-engineering',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2026, 4, 7),
}

dag = DAG(
    'tcmb_extract_dag',
    default_args=default_args,
    description='TCMB macroeconomic data ETL pipeline with dbt',
    schedule_interval='@daily',
    catchup=False,
)

DBT_DIR = '/opt/airflow/tcmb_dbt'
DBT_PROFILES_DIR = '/home/airflow/.dbt'
DBT_TARGET = 'docker'


def extract_usd_try():
    df = fetch_tcmb_series('TP.DK.USD.S', '2026-03-01')
    return df.to_dict('records')

def extract_eur_try():
    df = fetch_tcmb_series('TP.DK.EUR.S', '2026-03-01')
    return df.to_dict('records')

def extract_cpi():
    df = fetch_tcmb_series('TP.FG.AB09', '2026-01-01')
    return df.to_dict('records')

def transform_and_validate():
    df = fetch_tcmb_series('TP.DK.USD.S', '2026-03-01')
    result = transform_pipeline(df)
    validation = run_validation(result['daily'])

    if validation['score'] >= 90:
        print(f"[SUCCESS] Data quality: {validation['score']:.1f}%")
        return True
    else:
        raise Exception(f"Data quality check failed: {validation['score']:.1f}%")

def load_to_db():
    df = fetch_tcmb_series('TP.DK.USD.S', '2026-03-01')
    result = transform_pipeline(df)
    load_etl_pipeline(result['daily'])

def log_completion():
    print("[COMPLETE] TCMB ETL + dbt pipeline executed successfully")


# Tasks
task_extract_usd = PythonOperator(
    task_id='extract_usd_try',
    python_callable=extract_usd_try,
    dag=dag,
)

task_extract_eur = PythonOperator(
    task_id='extract_eur_try',
    python_callable=extract_eur_try,
    dag=dag,
)

task_extract_cpi = PythonOperator(
    task_id='extract_cpi',
    python_callable=extract_cpi,
    dag=dag,
)

task_transform = PythonOperator(
    task_id='transform_and_validate',
    python_callable=transform_and_validate,
    dag=dag,
)

task_load = PythonOperator(
    task_id='load_to_db',
    python_callable=load_to_db,
    dag=dag,
)

task_dbt_run = BashOperator(
    task_id='dbt_run',
    bash_command=(
        f"cd {DBT_DIR} && "
        f"dbt run --profiles-dir {DBT_PROFILES_DIR} --target {DBT_TARGET}"
    ),
    dag=dag,
)

task_dbt_test = BashOperator(
    task_id='dbt_test',
    bash_command=(
        f"cd {DBT_DIR} && "
        f"dbt test --profiles-dir {DBT_PROFILES_DIR} --target {DBT_TARGET}"
    ),
    dag=dag,
)

task_log = PythonOperator(
    task_id='log_completion',
    python_callable=log_completion,
    dag=dag,
)

# Dependencies
[task_extract_usd, task_extract_eur, task_extract_cpi] >> task_transform >> task_load >> task_dbt_run >> task_dbt_test >> task_log
