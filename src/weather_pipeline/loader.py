import json
import logging
import os
from datetime import datetime
from pathlib import Path

import clickhouse_connect
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)

# Directory configuration
BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
ARCHIVE_DIR = BASE_DIR / "data" / "processed"

def get_db_client():
    """Establish a connection to the local ClickHouse instance."""
    return clickhouse_connect.get_client(
        host="localhost",
        port=8123,
        username=os.getenv("CLICKHOUSE_USER"),
        password=os.getenv("CLICKHOUSE_PASSWORD"),
        database="weather_raw"
    )

def process_and_load_files() -> None:
    """Read all JSON files in the raw directory and load them into ClickHouse."""
    
    if not RAW_DATA_DIR.exists():
        logger.warning("Raw data directory does not exist. Run ingestion first.")
        return

    # Find all JSON files
    json_files = list(RAW_DATA_DIR.glob("*.json"))
    
    if not json_files:
        logger.info("No new JSON files found to process.")
        return

    # Ensure archive directory exists
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    
    client = get_db_client()

    for file_path in json_files:
        logger.info("Processing %s", file_path.name)
        
        with file_path.open("r", encoding="utf-8") as f:
            payload = json.load(f)

        # Extract metadata
        batch_id = payload["batch_id"]
        ingested_at = datetime.fromisoformat(payload["ingested_at_utc"])
        location_id = payload["location"]["location_id"]
        
        # Extract hourly forecast arrays
        hourly = payload["response"]["hourly"]
        times = hourly["time"]
        temps = hourly["temperature_2m"]
        humidity = hourly["relative_humidity_2m"]
        precip = hourly["precipitation"]
        wind = hourly["wind_speed_10m"]

        # Zip the columnar arrays into row-based tuples for ClickHouse
        rows_to_insert = []
        for i in range(len(times)):
            row = (
                batch_id,
                ingested_at,
                location_id,
                datetime.fromisoformat(times[i]),
                temps[i],
                humidity[i],
                precip[i],
                wind[i]
            )
            rows_to_insert.append(row)

        # Perform the bulk insert
        client.insert(
            table="raw_weather_forecasts",
            data=rows_to_insert,
            column_names=[
                "batch_id", 
                "ingested_at", 
                "location_id", 
                "forecast_time", 
                "temperature_2m", 
                "relative_humidity_2m", 
                "precipitation", 
                "wind_speed_10m"
            ]
        )
        
        logger.info("Inserted %d rows for batch %s", len(rows_to_insert), batch_id)

        # Move file to processed directory to prevent double-loading
        file_path.rename(ARCHIVE_DIR / file_path.name)
        logger.info("Archived %s", file_path.name)

if __name__ == "__main__":
    try:
        process_and_load_files()
        logger.info("Database loading completed successfully.")
    except Exception:
        logger.exception("Failed to load data into ClickHouse")
        raise SystemExit(1)