# charging_map.py
# Creates a Folium map with mock charging station markers in San Francisco

import json
import os
from geopy.distance import geodesic
import folium
from streamlit_folium import folium_static

# Loads stations from JSON file
def load_station_data():
    filepath = os.path.join("stations.json")
    try:
        with open(filepath,"r") as f:
            stations = json.load(f)
            return stations
    except Exception as e:
        print(f"Failed to load statin data: {e}")
        return []

# Simulated user location (e.g. user's home)
user_location = (37.7680, -122.4313) # Near Mission Dolores Park

def render_station_map():
    stations = load_station_data()
    # Base map centered on SF
    sf_center = [37.7749, -122.4194]
    m = folium.Map(location=sf_center, zoom_start=13)

    # Markers for each station & calculates distance from user
    for station in stations:
        station_coords = (station["lat"], station["lon"])
        distance_km = geodesic(user_location, station_coords).km
        distance_text = f"{distance_km:.2f} km away"

        folium.Marker(
            location=station_coords,
            popup=f"{station['name']} ({station['id']})<br>{distance_text}",
            tooltip=f"{station['name']} - {distance_text}",
            icon=folium.Icon(color="green", icon="bolt", prefix="fa")
        ).add_to(m)
          
    return m

# For standalone testing
if __name__ == "__main__":
    m = render_station_map()
    m.save("sf_charging_map.html")
    print("Map saved as sf_charging_map.html")