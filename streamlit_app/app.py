import os

import clickhouse_connect
import streamlit as st  # type: ignore[import-not-found]
from dotenv import load_dotenv

load_dotenv()

# Set page config for a wider layout to accommodate side-by-side graphs
st.set_page_config(page_title="Weather Analytics Hub", layout="wide")
st.title("🌤️ Weather Analytics Hub")

# 1. Safely cache the database connection to prevent memory leaks
@st.cache_resource
def get_db_client():
    return clickhouse_connect.get_client(
        host=os.getenv("CLICKHOUSE_HOST"),
        port=os.getenv("CLICKHOUSE_PORT"),
        username=os.getenv("CLICKHOUSE_USER"),
        password=os.getenv("CLICKHOUSE_PASSWORD")
    )

# 2. Cache the actual data for 5 minutes
@st.cache_data(ttl=300)
def load_data():
    client = get_db_client()
    
    # Query updated to pull all 4 metrics from the mart schema
    query = """
        SELECT 
            d.city_name,
            f.forecast_time,
            f.temperature_celsius,
            f.humidity_percentage,
            f.precipitation_mm,
            f.wind_speed_kmh
        FROM weather_warehouse_analytics.fact_weather f
        JOIN weather_warehouse_analytics.dim_location d
          ON f.location_id = d.location_id
        ORDER BY f.forecast_time DESC
        LIMIT 300
    """
    return client.query_df(query)

try:
    df = load_data()
    st.success("Successfully connected to ClickHouse!")
    
    # Hide the raw data table inside an expander to save UI space
    with st.expander("View Raw Data Table"):
        st.dataframe(df)

    # 3. Draw the 4 lightweight graphs using Streamlit columns
    # Passing color="city_name" automatically draws a separate line for each city
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Temperature (°C)")
        st.line_chart(df, x="forecast_time", y="temperature_celsius", color="city_name")
        
        st.subheader("Precipitation (mm)")
        st.line_chart(df, x="forecast_time", y="precipitation_mm", color="city_name")

    with col2:
        st.subheader("Humidity (%)")
        st.line_chart(df, x="forecast_time", y="humidity_percentage", color="city_name")
        
        st.subheader("Wind Speed (km/h)")
        st.line_chart(df, x="forecast_time", y="wind_speed_kmh", color="city_name")

except Exception as e:  # noqa: BLE001
    st.error(f"Failed to connect: {e}")