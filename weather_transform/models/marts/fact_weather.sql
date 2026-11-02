SELECT 
    -- Generate a unique Surrogate Key
    lower(hex(MD5(concat(location_id, toString(forecast_time))))) AS weather_fact_id,
    
    location_id,
    forecast_time,
    temperature_celsius,
    humidity_percentage,
    precipitation_mm,
    wind_speed_kmh
FROM {{ ref('stg_hourly_weather') }}