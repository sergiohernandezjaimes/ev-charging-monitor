# app.py
# Streamlit dashboard for visualizing EV charging session log

import streamlit as st
st.set_page_config(page_title="EV Charging Monitor", layout="wide")

from geopy.distance import geodesic
from charging_map import render_station_map, user_location, load_real_stations
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim
from typing import cast
from geopy.location import Location
import pandas as pd
import os
import json
import streamlit.components.v1 as components

st.title("EV Charging Monitor - San Francisco")



# ----------------------------
# Load station data
# ----------------------------
with open("data/ev_api_results.json") as f:
    station_data = json.load(f)

# Extract unique charger levels
all_levels = sorted(set(
    level for station in station_data
    for level in station.get("charger_levels", [])
))
level_map = {1: "Level 1", 2: "Level 2", 3: "Level 3"}
level_options = [level_map.get(lvl, f"Level {lvl}") for lvl in all_levels]



# ----------------------------
# Load session data
# ----------------------------
def load_data(csv_path="data/charging_log.csv"):
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path, parse_dates=["start_time"]) # use the function arg
        return df
    else:
        st.warning("No session data found. Run the simulator first")
        return pd.DataFrame()
    
data = load_data()

if not data.empty:
    min_date = data["start_time"].min().date()
    max_date = data["start_time"].max().date()
else:
    min_date = max_date = None

# ----------------------------
#  Initialize session sate defaults BEFORE creating widgets
#  ----------------------------
if "search_query" not in st.session_state:
    st.session_state.search_query = ""
if "selected_levels_label" not in st.session_state:
    st.session_state.selected_levels_label = level_options[:]
if "date_range" not in st.session_state:
    if min_date and max_date:
        st.session_state.date_range = (min_date, max_date) 
    else:
         st.session_state.date_range = (None, None)
if "selected_station" not in st.session_state:
    st.session_state.selected_station = "ALL"
if "sort_option" not in st.session_state:
    st.session_state.sort_option = "Distance"

# ----------------------------
# Sidebar Filters
# ----------------------------
def reset_filters():
    # Remove keys so defaults above re-apply cleanly on rerun
    for k in ("search_query", "selected_levels_label", "date_range", "selected_station", "sort_option"):
        if k in st.session_state:
            del st.session_state[k]

with st.sidebar:
    st.header("Filter Options")
    st.sidebar.subheader("Charging Stations")

    # Sort option
    sort_option = st.sidebar.radio(
        "Sort stations by:",
        ("Distance", "Availability", "Charger Level"),
        key="sort_option",
    )    

    # Search box (let the key drive the value; don't set default/value here)
    search_query = st.text_input("Search Station", key="search_query")

    # Charger level filter (no explicit defaults; value comes from session_state)
    st.multiselect(
        "Filter by Charger Levels",
        level_options,
        key="selected_levels_label",
    )

    # Date range filter (value comes from session_state via key)
    if min_date and max_date:
        st.date_input(
            "Filter by Date Range",
            min_value=min_date, 
            max_value=max_date,
            key="date_range",
        )

    # Default location (Mission Dolores Park)
    default_location = "Mission Dolores Park, San Francisco"
    geolocator = Nominatim(user_agent="ev-charging-monitor")

    user_location = st.sidebar.text_input(
        "Enter your location (address or landmark):", default_location
    )

    try:
        location = cast(Location, geolocator.geocode(user_location))
        if location:
            user_coords = (float(location.latitude), float(location.longitude))
        else:
            st.sidebar.warning("Could not find that location. Using default.")
            location = cast(Location, geolocator.geocode(default_location))
            user_coords = (float(location.latitude), float(location.longitude))
    except Exception as e:
        st.sidebar.error(f"Location lookup failed: {e}")
        location = cast(Location, geolocator.geocode(default_location))
        user_coords = (float(location.latitude), float(location.longitude))    

    st.markdown("---")

    # Reset button: use callback to clear keys (avoid modifying widget after instantiation)
    st.button("Reset Filters", on_click=reset_filters)

    for station in sorted(station_data, key=lambda x: x.get("distance_miles", float("inf"))):
        name = station.get("station_name", "Unknown Station")
        distance = station.get("distance_miles", float("inf"))
        if distance != float("inf"):
            st.sidebar.write(f"{name} - {distance:.2f} mi")
        else:
            st.sidebar.write(name)
    
# ----------------------------
# Apply Date Filter (only when both dates selected and valid)
# ----------------------------
if st.session_state.date_range and isinstance(st.session_state.date_range, tuple) and len(st.session_state.date_range) == 2:
    start_date, end_date = st.session_state.date_range
    if start_date and end_date:
        filtered_data = data[
            (data["start_time"].dt.date >= start_date) &
            (data["start_time"].dt.date <= end_date)
        ]
else:
    st.info("Please select both a start date and end date.")

# ----------------------------
# Map selected level labels back to numeric codes
# ----------------------------
labels = st.session_state.get("selected_levels_label", [])
selected_levels = [num for num, label in level_map.items() if label in labels]

# ----------------------------
# Apply Search Filter to stations
# ----------------------------
filtered_station_data = station_data
search_query = st.session_state.get("search_query", "").strip()

if search_query:
    filtered_station_data = [
        station for station in station_data 
        if search_query.lower() in station.get("title", "").lower()
    ]
if not filtered_station_data:
    st.warning(f"No stations found matching '{search_query}'.")

# ----------------------------
# Compute distance in miles for popups & sorting
# ----------------------------
for station in filtered_station_data:
    coords = (station.get("latitude"), station.get("longitude"))
    if coords[0] is not None and coords[1] is not None:
        try:
            station["distance_miles"] = round(geodesic(user_coords, coords).miles, 2)
        except Exception:
            station["distance_miles"] = float("inf")
    else:
        station["distance_miles"] = float("inf")         
    
# ----------------------------
# Visual Layout (Map)
# ----------------------------
st.subheader("Charging Station Map (San Francisco)")
map_ = render_station_map(
    filtered_station_data, 
    charger_level_filter=selected_levels, 
    sort_by=st.session_state.get("sort_option", "Distance"),
)
folium_static(map_, width=900, height=700)

# Apply search filter to the table data table as well
if search_query:
    data = data[data["station_id"].apply(
        lambda sid: any(
            search_query.lower() in station.get("title", "").lower()
            for station in station_data if station.get("station_id") == sid
        )
    )]

# ----------------------------
# Charging Session Log Table
# ----------------------------
if "date_range" in st.session_state and len(st.session_state.date_range) == 2:
    start_date, end_date = st.session_state.date_range
else:
    start_date, end_date = None, None

# Get station ID from filtered_station_data
filtered_station_ids = {station.get("station_id") for station in filtered_station_data}
filtered_data = data[data["station_id"].isin(filtered_station_ids)]

# Apply date range filters only if both dates selected
if filtered_data.empty:
    st.warning("No matching sessions for the selected stations/filters. Please try adjusting your filters (date, availability, charger level).")
else:
    # Apply same sort as the map
    sort_choice = st.session_state.get("sort_option", "Distance")
    if sort_choice == "Distance":
        station_distance_map = {
            s["station_id"]: s.get("distance_miles", float("inf"))
            for s in filtered_station_data
        }
        filtered_data["distance_miles"] = filtered_data["station_id"].map(station_distance_map)
        filtered_data = filtered_data.sort_values("distance_miles")
    elif sort_choice == "Availability":
        # Sort by status if available in CSV
        if "availability" in filtered_data.columns:
            filtered_data = filtered_data.sort_values("availability")
    elif sort_choice == "Charger Level":
        if "charger_level" in filtered_data.columns:
            filtered_data = filtered_data.sort_values("charger_level")
    
    # Display session log
    st.subheader("Charging Session Log")
    st.dataframe(filtered_data.drop(columns=["distance_miles"], errors="ignore"))

    # Download filtered data
    csv = filtered_data.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="charging_sessions_filtered.csv",
        mime="text/csv",
    )

    # Summary stats
    st.subheader("Charging Stats")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Sessions", len(filtered_data))
    col2.metric("Total Energy (kWh)", f"{filtered_data['energy_kwh'].sum():.2f}")
    col3.metric("Total Cost (USD)", f"${filtered_data['cost_usd'].sum():.2f}")

    # Charts
    st.subheader("Energy Usage per Session")
    st.bar_chart(filtered_data.set_index("session_id")["energy_kwh"])

    st.subheader("Session Duration (minutes)")
    st.bar_chart(filtered_data.set_index("session_id")["duration_min"])

    st.subheader("Cost per Session (USD)")
    st.bar_chart(filtered_data.set_index("session_id")["cost_usd"])

# ----------------------------
# Coming Soon: Route Planner
# ----------------------------
st.markdown("---")
st.subheader("Coming Soon: Route Planner")
st.markdown(
    """"
    Imagine entering your destination and getting:
    - Nearby charging stations along your route
    - Estimated cost and time to charge
    - Smart recommendations based on battery % and station availability

    Actively building this next - stay tuned!
    """
)