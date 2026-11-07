import subprocess

from prefect import flow, task


@task(retries=1, retry_delay_seconds=10)
def run_python_ingestion():
    print("1. Triggering extraction script...")
    subprocess.run(
        ["python", "-m", "src.weather_pipeline.ingestion"], 
        check=True
    )
    print("Extraction complete!")

@task(retries=1, retry_delay_seconds=10)
def run_python_loader():
    print("2. Triggering loader script...")
    # Update this path if your loader script has a different name
    subprocess.run(
        ["python", "-m", "src.weather_pipeline.loader"], 
        check=True
    )
    print("Loading complete!")

@task
def run_dbt_transformations():
    print("3. Triggering dbt transformations...")
    subprocess.run(
        ["dbt", "run", "--project-dir", "weather_transform"], 
        check=True
    )
    print("dbt transformations complete!")

@flow(name="Decoupled Weather ELT Pipeline", log_prints=True)
def main_orchestrator():
    print("Starting ELT orchestrator...")
    
    # 1. Extract (Save to JSON)
    run_python_ingestion()
    
    # 2. Load (Push JSON to ClickHouse)
    run_python_loader()
    
    # 3. Transform (Run SQL via dbt)
    run_dbt_transformations()
    
    print("Pipeline finished successfully!")

if __name__ == "__main__":
    main_orchestrator.serve(
        name="daily-weather-elt",
        cron="0 12 * * *",
        tags=["production", "weather"]
    )