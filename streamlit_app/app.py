import clickhouse_connect
import streamlit as st  # type: ignore[import-not-found]

st.title("🌤️ Weather Analytics Hub")

@st.cache_data(ttl=300)
def load_data():
    client = clickhouse_connect.get_client(host='clickhouse', port=8123)
    
    # Join fact and dim tables to get the human-readable city_name
    query = """
        SELECT 
            d.city_name,
            f.forecast_time,
            f.temperature_celsius,
            d.latitude,
            d.longitude
        FROM weather_warehouse_analytics.fact_weather f
        JOIN weather_warehouse_analytics.dim_location d
          ON f.location_id = d.location_id
        ORDER BY f.forecast_time DESC
        LIMIT 100
    """
    return client.query_df(query)

try:
    df = load_data()
    st.success("Successfully connected to ClickHouse!")
    st.dataframe(df)
except Exception as e:  # noqa: BLE001
    st.error(f"Failed to connect: {e}")