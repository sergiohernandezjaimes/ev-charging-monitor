# charging_map.py
# Creates a Folium map with mock charging station markers in San Francisco

import json
import os
from geopy.distance import geodesic
import folium
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

def render_station_map():
    stations = load_real_stations() # Now using real stations!
    # Base map centered on SF
    sf_center = [37.7749, -122.4194]
    m = folium.Map(location=sf_center, zoom_start=13)

    for station in stations:
        popup_text = f"{station['name']}<br>{station['address']}"
        folium.Marker(
            location=[station["lat"], station["lon"]],
            popup=popup_text,
            tooltip=station["name"],
            icon=folium.Icon(color="green", icon="bolt", prefix="fa")
        ).add_to(m)
          
    return m

# For standalone testing
if __name__ == "__main__":
    m = render_station_map()
    m.save("sf_charging_map.html")
    print("Map saved as sf_charging_map.html")