# charging_map.py
# Creates a Folium map with mock charging station markers in San Francisco

import json
import os
from geopy.distance import geodesic
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static

# Loads stations from JSON file
def load_real_stations(json_path="data/ev_api_results.json"):
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            return json.load(f)
    else:
        return []
    
# Simulated user location (e.g. user's home)
user_location = (37.7680, -122.4313) # Near Mission Dolores Park

def render_station_map(station_data, charger_level_filter=None):
    station_data = sorted(station_data, key=lambda s: s.get("distance_miles", float("inf")))
    # Base map centered on SF
    m = folium.Map(location=[37.7749, -122.4194], zoom_start=12)
    marker_cluster = MarkerCluster().add_to(m)

    # Icon color by availability status
    availability_colors = {
        "Available":"green",
        "In use":"orange",
        "Offline":"gray"
    }

    for station in station_data:
        levels = station.get("charger_levels", [])
        if charger_level_filter and not any(level in levels for level in charger_level_filter):
            continue # Skip if station doesn't have selected level
        
        availability = station.get("availability", "Unknown")
        icon_color = availability_colors.get(availability, "blue") # fallback = blue

        popup_info = f"""
        <b>{station['title']}</b><br>
        Charger Levels: {', '.join(str(lvl) for lvl in levels)}<br>
        Status: <b>{availability}</b><br>
        Distance: <b>{station['distance_miles']} mi</b>
        """

        folium.Marker(
            location=[station["latitude"], station["longitude"]],
            popup=popup_info,
            icon=folium.Icon(color=icon_color, icon="bolt", prefix="fa")
        ).add_to(marker_cluster)
          
    return m

# For standalone testing
if __name__ == "__main__":
    stations = load_real_stations() # Load from JSON
    m = render_station_map(stations) # pass loaded data
    m.save("sf_charging_map.html")
    print("Map saved as sf_charging_map.html")