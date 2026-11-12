import clickhouse_connect
import streamlit as st  # type: ignore[import-not-found]

st.title("🌤️ Weather Analytics Hub")

@st.cache_data(ttl=300) # Cache the data for 5 minutes
def load_data():
    # Use Docker's internal DNS to hit the database container
    client = clickhouse_connect.get_client(host='clickhouse', port=8123)
    # Query your final dbt analytics table
    query = "SELECT * FROM default.fact_weather ORDER BY forecast_time DESC LIMIT 100"
    return client.query_df(query)

try:
    df = load_data()
    st.success("Successfully connected to ClickHouse!")
    st.dataframe(df)
except Exception as e:  # noqa: BLE001
    st.error(f"Failed to connect: {e}")