import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENCHARGEMAP_API_KEY")

def is_in_san_francisco(lat, lon):
    # Round bounding box around SF
    return 37.58 <= lat <= 37.98 and -122.62 <= lon <= -122.25

# Connection level logic
def parse_charger_levels(connections):
    levels = set()
    for conn in connections:
        level_id = conn.get("LevelID")
        if level_id:
            levels.add(level_id)
    return list(levels)

# Fetch information from OpenCharge API within SF
def fetch_ev_stations_sf():
    url = "https://api.openchargemap.io/v3/poi/"
    params = {
        "output": "json",
        "countrycode": "US",
        "maxresults": 100,
        "latitude": 37.7749,
        "longitude": -122.4194,
        "distance": 25,
        "distanceunit": "Miles",
        "compact": True,
        "verbose": False, 
        "key": api_key
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        raw_data = response.json()
        print(f"Fetched {len(raw_data)} stations total.")

        filtered_stations = []

# Connection station logic
        for station in raw_data:
            try:
                lat = station["AddressInfo"]["Latitude"]
                lon = station["AddressInfo"]["Longitude"]
                if is_in_san_francisco(lat,lon):
                    connections = station.get("Connections", [])
                    charger_levels = parse_charger_levels(connections)

                    station_info = {
                        "id": station["ID"],
                        "title": station["AddressInfo"]["Title"],
                        "latitude": lat,
                        "longitude": lon,
                        "charger_levels": charger_levels,
                    }
                    filtered_stations.append(station_info)
            except (KeyError, TypeError):
                continue

        print(f"Filtered to {len(filtered_stations)} SF stations.")
        os.makedirs("data", exist_ok=True)
        with open("data/ev_api_results.json", "w") as f:
            json.dump(filtered_stations, f, indent=2)
        print("Saved filtered data to data/ev_api_results.json")
    else:
        print("Failed to fetch data:", response.status_code)
        
if __name__ == "__main__":
    fetch_ev_stations_sf()