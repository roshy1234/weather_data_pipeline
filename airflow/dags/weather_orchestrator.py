# ruff: noqa: I001

from datetime import datetime, timedelta

from airflow import DAG  # type: ignore[import-not-found]
from airflow.operators.bash import BashOperator  # type: ignore[import-not-found]

default_args = {
    'owner': 'roshy1234',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='weather_pipeline_orchestrator',
    default_args=default_args,
    description='Extract, Load, and Transform weather data',
    schedule_interval='0 6 * * *', # Your exact cron schedule!
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['weather'],
) as dag:

    # This string mimics your bash script's environment setup and path navigation
    env_setup = "cd /opt/airflow/project_root && set -a && source .env && set +a && "

    # 1. Extract
    extract_data = BashOperator(
        task_id='extract_weather_api',
        bash_command=f'{env_setup} python -m src.weather_pipeline.ingestion',
    )

    # 2. Load
    load_data = BashOperator(
        task_id='load_to_clickhouse',
        bash_command=f'{env_setup} python -m src.weather_pipeline.loader',
    )

    # 3. Transform & Test
    dbt_transform = BashOperator(
        task_id='dbt_run_and_test',
        bash_command=f'{env_setup} cd weather_transform && dbt run && dbt test',
    )

    # Define the execution order (Airflow's core superpower)
    extract_data >> load_data >> dbt_transform