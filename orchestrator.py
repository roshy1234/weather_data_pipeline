import subprocess

from prefect import flow, task


def run_command(cmd: list[str], step: str) -> None:
    """Run a shell command and surface its output on failure."""
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    print(result.stdout)
    if result.returncode != 0:
        print(f"❌ {step} failed:\n{result.stderr}")
        raise subprocess.CalledProcessError(result.returncode, cmd, result.stderr)


@task(retries=1, retry_delay_seconds=10)
def run_python_ingestion():
    print("1. Triggering extraction script...")
    run_command(["python", "-m", "src.weather_pipeline.ingestion"], "Ingestion")
    print("Extraction complete!")


@task(retries=1, retry_delay_seconds=10)
def run_python_loader():
    print("2. Triggering loader script...")
    run_command(["python", "-m", "src.weather_pipeline.loader"], "Loader")
    print("Loading complete!")


@task
def run_dbt_transformations():
    print("3. Triggering dbt transformations...")
    run_command(["dbt", "run", "--project-dir", "weather_transform", "--profiles-dir", "weather_transform"], "dbt run")
    print("dbt transformations complete!")


@task
def run_dbt_tests():
    print("4. Triggering dbt data quality tests...")
    run_command(["dbt", "test", "--project-dir", "weather_transform", "--profiles-dir", "weather_transform"], "dbt test")
    print("dbt tests passed!")


@flow(name="Decoupled Weather ELT Pipeline", log_prints=True)
def main_orchestrator():
    print("Starting ELT orchestrator...")

    # 1. Extract (Save to JSON)
    run_python_ingestion()

    # 2. Load (Push JSON to ClickHouse)
    run_python_loader()

    # 3. Transform (Build tables)
    run_dbt_transformations()

    # 4. Test (Verify data quality)
    run_dbt_tests()

    print("Pipeline finished successfully!")


if __name__ == "__main__":
    main_orchestrator.serve(
        name="daily-weather-elt",
        cron="0 12 * * *",
        tags=["production", "weather"]
    )
