#!/bin/bash
set -euo pipefail

# Redirect all output to a log file (useful for cron)
exec >> ~/de_projects/weather-data-pipeline/logs/pipeline.log 2>&1
echo "--- Pipeline started: $(date) ---"

# 1. Load environment variables (crucial for cron)
set -a; source ~/de_projects/weather-data-pipeline/.env; set +a

# 2. Navigate to the project root
cd ~/de_projects/weather-data-pipeline

# 3. Activate the Python virtual environment
source venv/bin/activate

# 4. Extract: Fetch weather data from API -> save as JSON
python -m src.weather_pipeline.ingestion

# 5. Load: Read JSON files -> insert into ClickHouse
python -m src.weather_pipeline.loader

# 6. Transform & Test: Run dbt models and data quality checks
cd weather_transform
dbt run && dbt test

echo "--- Pipeline finished: $(date) ---"


