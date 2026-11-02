-- If this query returns ANY rows, it means the deduplication failed.
SELECT 
    location_id,
    forecast_time,
    count(*) as total_records
FROM {{ ref('stg_hourly_weather') }}
GROUP BY 
    location_id, 
    forecast_time
HAVING count(*) > 1