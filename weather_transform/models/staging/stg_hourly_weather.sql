{{ config(
    order_by=['location_id', 'forecast_time']
) }}

WITH deduplicated AS (
    SELECT 
        location_id,
        forecast_time,
        temperature_2m,
        relative_humidity_2m,
        precipitation,
        wind_speed_10m,
        batch_id,
        -- Assign a row number to overlapping forecasts, prioritizing the newest batch
        row_number() OVER (
            PARTITION BY location_id, forecast_time 
            ORDER BY batch_id DESC
        ) as rn
    FROM {{ source('raw_weather', 'raw_weather_forecasts') }}
)

SELECT 
    location_id,
    forecast_time,
    temperature_2m AS temperature_celsius,
    relative_humidity_2m AS humidity_percentage,
    precipitation AS precipitation_mm,
    wind_speed_10m AS wind_speed_kmh,
    batch_id
FROM deduplicated
WHERE rn = 1