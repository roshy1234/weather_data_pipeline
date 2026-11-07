import subprocess
from prefect import flow, task

@task(retries=1, retry_delay_seconds=10)
def run_python_ingestion():
    print("Triggering Python ingestion script...")
    # Executes your untouched script exactly as you would in the terminal
    subprocess.run(
        ["python", "-m", "src.weather_pipeline.ingestion"], 
        check=True
    )
    print("Ingestion complete!")

@task
def run_dbt_transformations():
    print("Triggering dbt transformations...")
    # Replace 'weather_transform' with your actual dbt folder name
    subprocess.run(
        ["dbt", "run", "--project-dir", "weather_transform"], 
        check=True
    )
    print("dbt transformations complete!")

@flow(name="Decoupled Weather ELT Pipeline", log_prints=True)
def main_orchestrator():
    print("Starting orchestrator...")
    
    # 1. Run the independent ingestion script
    run_python_ingestion()
    
    # 2. Run the independent dbt models
    run_dbt_transformations()
    
    print("Pipeline finished successfully!")

if __name__ == "__main__":
    main_orchestrator()