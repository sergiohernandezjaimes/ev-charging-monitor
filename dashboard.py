# dashboard.py
# Streamlit dashboard for visualizing EV charging session log

from charging_map import render_station_map
from streamlit_folium import folium_static
import streamlit as st
import pandas as pd
import os

# ----------------------------
# Visual Layout (Map)
# ----------------------------
st.set_page_config(page_title="EV Charging Monitor", layout="wide")
st.title("EV Charging Session Monitor")
st.subheader("Charging Station Map (San Francisco)")
folium_static(render_station_map(), width=800, height=600)

# ----------------------------
# Load session data
# ----------------------------
def load_data(csv_path="data/charging_log.csv"):
    if os.path.exists(csv_path):
        df = pd.read_csv("data/charging_log.csv", parse_dates=["start_time"])
        return df
    else:
        st.warning("No session data found. Run the simulator first")
        return pd.DataFrame()
    
data = load_data()

# ----------------------------
# Filter Sidebar
# ----------------------------
with st.sidebar:
    st.header("Filter Options")
    station_ids = ["ALL"] + sorted(data["station_id"].unique())

    if "selected_station" not in st.session_state:
        st.session_state.selected_station = "ALL"

    if st.button("Reset Filter"):
        st.session_state.selected_station = "ALL"

    selected_station = st.selectbox(
        "Select Station",
        station_ids,
        index=station_ids.index(st.session_state.selected_station),
        key="selected_station"
    )
# ----------------------------
# Date Filter
# ----------------------------
if not data.empty:
    min_date = data["start_time"].min().date()
    max_date = data["start_time"].max().date()

    date_range = st.sidebar.date_input(
        "Filter by Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # Handle single-date or invalid selections
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        if start_date > end_date:
            st.warning("Start date is after end date. Please adjust.")
        else:
            data = data[(data["start_time"].dt.date >= start_date) & (data["start_time"].dt.date <= end_date)]
    else:
        st.info("Please select both a start date and end date.")

st.sidebar.markdown("---")

# ----------------------------
# Data Table
# ----------------------------
if selected_station != "ALL":
    data = data[data["station_id"] == selected_station]
if not data.empty:
    st.subheader("Charging Session Log")
    st.dataframe(data)

# ----------------------------
# Download filtered data
# ----------------------------
    csv = data.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="charging_sessions_filtered.csv",
        mime="text/csv"
)

# ----------------------------
# Summary stats
# ----------------------------
    st.subheader("Charging Stats")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Sessions", len(data))
    col2.metric("Total Energy (kWh)", f"{data['energy_kwh'].sum():.2f}")
    col3.metric("Total Cost (USD)", f"${data['cost_usd'].sum():.2f}")

# ----------------------------
# Charts
# ----------------------------
    st.subheader("Energy Usage per Session")
    st.bar_chart(data.set_index("session_id")["energy_kwh"])

    st.subheader("Session Duration (minutes)")
    st.bar_chart(data.set_index("session_id")["duration_min"])

    st.subheader("Cost per Session (USD)")
    st.bar_chart(data.set_index("session_id")["cost_usd"])
    
else:
    st.info("No data to display.")