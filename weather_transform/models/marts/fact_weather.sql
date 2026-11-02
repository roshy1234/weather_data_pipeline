SELECT 
    location_id,
    forecast_time,
    temperature_celsius,
    humidity_percentage,
    precipitation_mm,
    wind_speed_kmh
FROM {{ ref('stg_hourly_weather') }}