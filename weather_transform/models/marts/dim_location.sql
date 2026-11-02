WITH unique_locations AS (
    SELECT DISTINCT location_id 
    FROM {{ ref('stg_hourly_weather') }}
)

SELECT 
    location_id,
    CASE 
        WHEN location_id = 'kochi' THEN 'Kochi, Kerala'
        WHEN location_id = 'bengaluru' THEN 'Bengaluru, Karnataka'
        WHEN location_id = 'delhi' THEN 'New Delhi, Delhi'
    END AS city_name,
    CASE 
        WHEN location_id = 'kochi' THEN 9.9312
        WHEN location_id = 'bengaluru' THEN 12.9716
        WHEN location_id = 'delhi' THEN 28.6139
    END AS latitude,
    CASE 
        WHEN location_id = 'kochi' THEN 76.2673
        WHEN location_id = 'bengaluru' THEN 77.5946
        WHEN location_id = 'delhi' THEN 77.2090
    END AS longitude
FROM unique_locations