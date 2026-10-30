import json
import logging
from datetime import datetime, timezone
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

LOCATION = {
    "location_id": "kochi",
    "city": "Kochi",
    "latitude": 9.9312,
    "longitude": 76.2673,
}

RAW_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def fetch_weather() -> dict:
    """Fetch hourly weather forecasts for Kochi."""

    params = {
        "latitude": LOCATION["latitude"],
        "longitude": LOCATION["longitude"],
        "hourly": [
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "wind_speed_10m",
        ],
        "forecast_days": 2,
        "timezone": "Asia/Kolkata",
    }

    logger.info("Requesting weather data for %s", LOCATION["city"])

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


def save_raw_batch(payload: dict) -> Path:
    """Save the raw API response together with batch metadata."""

    # Use UTC for batch identification and ingestion timestamps.
    ingested_at = datetime.now(timezone.utc)

    batch_id = ingested_at.strftime("%Y%m%dT%H%M%S%fZ")

    batch = {
        "batch_id": batch_id,
        "ingested_at_utc": ingested_at.isoformat(),
        "source": "Open-Meteo",
        "attribution": "Weather data provided by Open-Meteo",
        "location": LOCATION,
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

    try:
        payload = fetch_weather()
        output_file = save_raw_batch(payload)

        logger.info("Batch ingestion completed: %s", output_file.name)

    except (requests.RequestException, ValueError, OSError):
        logger.exception("Weather ingestion failed")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
