-- 1. Create a dedicated database for ingestion
CREATE DATABASE IF NOT EXISTS weather_raw;

-- 2. Create the table inside the new database
CREATE TABLE IF NOT EXISTS weather_raw.raw_weather_forecasts (
    batch_id String,
    ingested_at DateTime,
    location_id String,
    forecast_time DateTime,
    temperature_2m Float32,
    relative_humidity_2m Float32,
    precipitation Float32,
    wind_speed_10m Float32
) 
ENGINE = MergeTree()
ORDER BY (location_id, forecast_time, batch_id);