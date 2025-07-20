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
            data = json.load(f)

        stations = []
        for item in data:
            if item.get("AddressInfo") and item["AddressInfo"].get("Latitude") and item["AddressInfo"].get("Longitude"):
                stations.append({
                    "id": item.get("ID"),
                    "name": item["AddressInfo"].get("Title", "Unnamed Station"),
                    "lat": item["AddressInfo"]["Latitude"],
                    "lon": item["AddressInfo"]["Longitude"],
                    "address": item["AddressInfo"].get("AddressLine1", "No Address")
                })
        return stations
    else:
        return []
# Simulated user location (e.g. user's home)
user_location = (37.7680, -122.4313) # Near Mission Dolores Park

def render_station_map(station_data, charger_level_filter=None):
    # Base map centered on SF
    m = folium.Map(location=[37.7749, -122.4194], zoom_start=12)
    marker_cluster = MarkerCluster().add_to(m)

    for station in station_data:
        levels = station.get("charger_levels", [])
        if charger_level_filter is not None and charger_level_filter not in levels:
            continue # Skip if station doesn't have selected level

        popup_info = f"{station['title']}<br>Charger Levels: {levels}"
        folium.Marker(
            location=[station["latitude"], station["longitude"]],
            popup=popup_info,
            icon=folium.Icon(color="green", icon="bolt", prefix="fa")
        ).add_to(marker_cluster)
          
    return m

# For standalone testing
if __name__ == "__main__":
    stations = load_real_stations() # Load from JSON
    m = render_station_map(stations) # pass loaded data
    m.save("sf_charging_map.html")
    print("Map saved as sf_charging_map.html")