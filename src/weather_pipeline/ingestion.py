import json
import logging
from datetime import UTC, datetime
from pathlib import Path

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

# Project configuration
API_URL = "https://api.open-meteo.com/v1/forecast"

LOCATIONS = [
    {
        "location_id": "kochi",
        "city": "Kochi",
        "latitude": 9.9312,
        "longitude": 76.2673,
    },
    {
        "location_id": "bengaluru",
        "city": "Bengaluru",
        "latitude": 12.9716,
        "longitude": 77.5946,
    },
    {
        "location_id": "delhi",
        "city": "Delhi",
        "latitude": 28.6139,
        "longitude": 77.2090,
    }
]

# 2. Updated path logic to account for moving the file into the weather_pipeline subfolder
BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"

def fetch_weather(location: dict) -> dict:
    """Fetch hourly weather forecasts for the specified location."""

    params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "hourly": [
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "wind_speed_10m",
        ],
        "forecast_days": 2,
        "timezone": "Asia/Kolkata",
    }

    logger.info("Requesting weather data for %s", location["city"])

    response = requests.get(
        API_URL,
        params=params,
        timeout=20,
    )

    # Raise an exception if the API returns an HTTP error.
    response.raise_for_status()
    payload = response.json()

    # Check that the response contains the expected structure.
    hourly_data = payload.get("hourly", {})

    if not hourly_data or "time" not in hourly_data:
        raise ValueError("API response does not contain expected hourly data")

    logger.info(
        "Successfully retrieved %s hourly records",
        len(hourly_data["time"]),
    )

    return payload


def save_raw_batch(payload: dict, location: dict) -> Path:
    """Save the raw API response together with batch metadata."""

    # Use UTC for batch identification and ingestion timestamps.
    ingested_at = datetime.now(UTC)
# Inject the city ID into the filename so they don't overwrite each other
    batch_id = f"{location['location_id']}_{ingested_at.strftime('%Y%m%dT%H%M%S%fZ')}"
    batch = {
        "batch_id": batch_id,
        "ingested_at_utc": ingested_at.isoformat(),
        "source": "Open-Meteo",
        "attribution": "Weather data provided by Open-Meteo",
        "location": location,
        "response": payload,
    }

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    output_file = RAW_DATA_DIR / f"weather_batch_{batch_id}.json"

    output_file.write_text(
        json.dumps(batch, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    logger.info("Raw batch saved to %s", output_file)

    return output_file


def main() -> None:
    """Execute one batch ingestion."""

# 3. Loop through the list and process each city one by one
for location in LOCATIONS:
    try:
        # We now pass the specific 'location' dictionary into our functions
        payload = fetch_weather(location)
        output_file = save_raw_batch(payload, location)

        logger.info("Batch ingestion completed for %s\n", location["city"])

    except (requests.RequestException, ValueError, OSError):
        logger.exception("Weather ingestion failed for %s", location["city"])
        # 4. Use 'continue' instead of exiting, so if one city fails, the others still run!
        continue


if __name__ == "__main__":
    main()
    
