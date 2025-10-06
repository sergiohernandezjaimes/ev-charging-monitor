# app.py
# Streamlit dashboard for visualizing EV charging session log

import streamlit as st
st.set_page_config(page_title="EV Charging Monitor", layout="wide")

from geopy.distance import geodesic
from charging_map import render_station_map, load_real_stations
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from typing import Optional, Tuple, cast
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

# ----------------------------
# Normalize station data for consistency across JSON versions
# ----------------------------    
def normalize_stations(stations):
    for s in stations:
        # cannonical id/title/coords keys
        s["station_id"] = (
            s.get("station_id")
            or s.get("id") 
            or s.get("stationId") 
            or s.get("station_id_str")
            or str(s.get("id", "") or "")
        )
        s["title"] = (
            s.get("title") 
            or s.get("station_name") 
            or s.get("name") 
            or s.get("title_name") 
            or "Unknown Station"
        )

        # latitude/longitude: try common variants, coerce to float or None
        lat = s.get("latitude") or s.get("lat") or s.get("y") or s.get("Latitude")
        lon = s.get("longitude") or s.get("lng") or s.get("lon") or s.get("x") or s.get("Longitude")
        try:
            s["latitude"] = float(lat) if lat not in (None, "", "NaN") else None
            s["longitude"] = float(lon) if lon not in (None, "", "NaN") else None
        except Exception:
            s["latitude"] = None
            s["longitude"] = None

    return stations

station_data = normalize_stations(station_data)    

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
        df = pd.read_csv(csv_path, parse_dates=["start_time"])
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
#  Initialize session state defaults BEFORE creating widgets
#  ----------------------------
if "search_query" not in st.session_state:
    st.session_state.search_query = ""
if "selected_levels_label" not in st.session_state:
    st.session_state.selected_levels_label = level_options[:]
#if "date_range" not in st.session_state:
#    if min_date and max_date:
#       st.session_state.date_range = (min_date, max_date) 
#     else:
#         st.session_state.date_range = (None, None)
if "selected_station" not in st.session_state:
    st.session_state.selected_station = "ALL"
if "sort_option" not in st.session_state:
    st.session_state.sort_option = "Distance"
if "distance_sort_order" not in st.session_state:
    st.session_state.distance_sort_order = "Nearest first"

# ----------------------------
# Sidebar Filters
# ----------------------------
def reset_filters():
    for k in ("search_query", "selected_levels_label", "date_range", "selected_station", "sort_option", "distance_sort_order"):
        if k in st.session_state:
            del st.session_state[k]

with st.sidebar:
    st.header("Filter Options")

    # Sort option (affects map + session table ordering)
    sort_option = st.radio(
        "Sort stations by:",
        ("Distance", "Availability", "Charger Level"),
        key="sort_option",
    )    

    # Search box
    search_query = st.text_input("Search Station", key="search_query")

    # Charger level filter (labels)
    st.multiselect(
        "Filter by Charger Levels",
        level_options,
        key="selected_levels_label",
    )

    # Date range filter (value comes from session_state via key)
    if min_date and max_date:
        st.date_input(
            "Filter by Date Range",
            value=(min_date, max_date),
            min_value=min_date, 
            max_value=max_date,
            key="date_range",
        )       

    # Sidebar: location input and safe geocode
    st.markdown("---")
    st.subheader("Location (for distance)")
    default_location = "Mission Dolores Park, San Francisco"
    geolocator = Nominatim(user_agent="ev-charging-monitor")

    user_input_location = st.text_input("Enter your location (address or landmark):", default_location)

    # cached safe geocode to avoid repeated network calls during dev
    @st.cache_data(ttl=60 * 60 * 24)
    def cache_geocode(query: str, fallback: str = default_location) -> Optional[Tuple[float, float]]:
        try:
            loc = geolocator.geocode(query)
            if loc:
                loc = cast(Location, loc)
                return (float(loc.latitude), float(loc.longitude))
        except Exception:
            pass
        try:
            loc = geolocator.geocode(fallback)
            if loc:
                loc = cast(Location, loc)
                return (float(loc.latitude), float(loc.longitude))
        except Exception:
            pass
        return None
        

    user_coords = cache_geocode(user_input_location)
    if user_coords is None:
        st.sidebar.error("Location lookup failed. (or rate-limited). Using a generic SF center.")
        user_coords = (37.7749, -122.4194)

    st.markdown("---")
    # Distance sort toggle (single widget)
    distance_sort_order = st.radio(
        "Sort by distance:",
        ("Nearest first", "Farthest first"),
        key="distance_sort_order",
    )

    # Reset button
    st.button("Reset Filters", on_click=reset_filters)

# ----------------------------
# Compute distance in miles for popups & sorting (after user_coords available)
# ----------------------------
for s in station_data:
    lat = s.get("latitude")
    lon = s.get("longitude")
    if lat is not None and lon is not None:
        try:
            s["distance_miles"] = round(geodesic(user_coords, (lat, lon)).miles, 2)
        except Exception:
            s["distance_miles"] = float("inf")
    else:
        s["distance_miles"] = float("inf")

# ----------------------------
# Show sidebar station list (sorted by distance order)
# ----------------------------
st.sidebar.subheader("Charging Stations")
reverse = distance_sort_order == "Farthest first"
sorted_stations = sorted(station_data, key=lambda x: x.get("distance_miles", float("inf")), reverse=reverse)
for s in sorted_stations:
    name = s.get("title", "Unknown Station")
    dist = s.get("distance_miles", float("inf"))
    if dist is None or dist == float("inf"):
        st.sidebar.write(f"{name}")
    else:
        st.sidebar.write(f"{name} - {dist:.2f} mi")

# ----------------------------
# Map selected level labels back to numeric codes
# ----------------------------
labels = st.session_state.get("selected_levels_label", [])
# Map label back to numeric keys in level_map
selected_levels = [num for num, label in level_map.items() if label in labels]

# ----------------------------
# Apply Search Filter to stations (for map)
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
# Visual Layout (Map)
# ----------------------------
st.subheader("Charging Station Map (San Francisco)")
map_ = render_station_map(
    filtered_station_data, 
    charger_level_filter=selected_levels, 
    sort_by=st.session_state.get("sort_option", "Distance"),
)
returned = st_folium(map_, width=900, height=700, returned_objects=["last_clicked"])

# returned last click --> find nearest station and set session_state selected_station
click = returned.get("last_clicked")
if click and click.get("lat") is not None and click.get("lng") is not None:
    clicked_lat = click["lat"]
    clicked_lng = click["lng"]

    # find nearest station to clicked coords
    def find_nearest_station_id(lat, lng, stations):
        best = None
        best_d = float("inf")
        for stn in stations:
            lat2 = stn.get("latitude")
            lon2 = stn.get("longitude")
            if lat2 is None or lon2 is None:
                continue
            try:
                d = geodesic((lat, lng), (lat2, lon2)).miles
            except Exception:
                continue
            if d < best_d:
                best = stn
                best_d = d
        return best.get("station_id") if best else None
            
    nearest_id = find_nearest_station_id(clicked_lat, clicked_lng, filtered_station_data)
    if nearest_id:
        # set session_state so the table updates
        st.session_state.selected_station = nearest_id

# ----------------------------
# Charging Session Log Table (robust pipeline)
# ----------------------------
df = data.copy()

# filter by search query station titles (if present)
search_query = st.session_state.get("search_query", "").strip()
if search_query:
    matching_ids = {s["station_id"] for s in station_data if search_query.lower() in s.get("title", "").lower()}
    df = df[df["station_id"].isin(matching_ids)]

# filter to stations currently visible on the map
visible_ids = {s["station_id"] for s in filtered_station_data}
df = df[df["station_id"].isin(visible_ids)]

# if a single station selected (map click), filter down
sel = st.session_state.get("selected_station", "ALL")
if sel != "ALL":
    df = df[df["station_id"] == sel]

# apply date filter (if both provided)
dr = st.session_state.get("date_range")
if isinstance(dr, tuple) and len(dr) == 2:
    sd, ed = dr
    if sd and ed:
        df = df[(df["start_time"].dt.date >= sd) & (df["start_time"].dt.date <= ed)]

# attach distance_miles to sessions for sorting
dist_map = {s["station_id"]: s.get("distance_miles", float("inf")) for s in station_data}
if not df.empty:
    df["distance_miles"] = df["station_id"].map(dist_map)

# session-table sorting to mirror map sort
sort_choice = st.session_state.get("sort_option", "Distance")
if sort_choice == "Distance" and "distance_miles" in df.columns:
    df = df.sort_values("distance_miles")
elif sort_choice == "Availability" and "availability" in df.columns:
    df = df.sort_values("availability")
elif sort_choice == "Charger Level" and "charger_level" in df.columns:
    df = df.sort_values("charger_level")

# Display sessions
if df.empty:
    st.warning("No matching sessions for the selected stations/filters. Please try adjusting your filters.")
else:    
    st.subheader("Charging Session Log")
    st.dataframe(df.drop(columns=["distance_miles"], errors="ignore"))

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(label="Download CSV", data=csv, file_name="charging_sessions_filtered.csv", mime="text/csv")

    # Summary stats
    st.subheader("Charging Stats")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Sessions", len(df))
    col2.metric("Total Energy (kWh)", f"{df['energy_kwh'].sum():.2f}")
    col3.metric("Total Cost (USD)", f"${df['cost_usd'].sum():.2f}")

    # Charts
    st.subheader("Energy Usage per Session")
    st.bar_chart(df.set_index("session_id")["energy_kwh"])
    st.subheader("Session Duration (minutes)")
    st.bar_chart(df.set_index("session_id")["duration_min"])
    st.subheader("Cost per Session (USD)")
    st.bar_chart(df.set_index("session_id")["cost_usd"])

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