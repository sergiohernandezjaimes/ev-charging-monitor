# dashboard.py
# Streamlit dashboard for visualizing EV charging session log

import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="EV Charging Monitor", layout="wide")
st.title("EV Charging Session Monitor")

# Load session data
def load_data(csv_path="data/charging_log.csv"):
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path, parse_dates=["start_time", "end_time"])
        return df
    else:
        st.warning("No session data found. Run the simulator first")
        return pd.DataFrame()
    
data = load_data()

# Display table
if not data.empty:
    st.subheader("Charging Session Log")
    st.dataframe(data)

    # Summary stats
    st.subheader("Charging Stats")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Sessions", len(data))
    col2.metric("Total Energy (kWh)", f"{data['energy_kwh'].sum():.2f}")
    col3.metric("Total Cost (USD)", f"${data['cost_usd'].sum():.2f}")

    st.subheader("Energy Usage per Session")
    st.bar_chart(data.set_index("session_id")["energy_kwh"])

    st.subheader("Session Duration (minutes)")
    st.bar_chart(data.set_index("session_id")["duration_min"])

    st.subheader("Cost per Session (USD)")
    st.bar_chart(data.set_index("session_id")["cost_usd"])
    
else:
    st.info("No data to display.")