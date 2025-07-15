import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENCHARGEMAP_API_KEY")

def is_in_san_francisco(lat, lon):
    # Round bounding box around SF
    return 37.58 <= lat <= 37.98 and -122.62 <= lon <= -122.25

def fetch_ev_stations_sf():
    url = "https://api.openchargemap.io/v3/poi/"
    params = {
        "output": "json",
        "countrycode": "US",
        "maxresults": 100,
        "latitud": 37.7749,
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

        sf_data = []
        for item in raw_data:
            try:
                lat = item["AddressInfo"]["Latitude"]
                lon = item["AddressInfo"]["Longitude"]
                if is_in_san_francisco(lat, lon):
                    sf_data.append(item)
            except (KeyError, TypeError):
                continue

        print(f"Filtered to {len(sf_data)} SF stations.")

        os.makedirs("data", exist_ok=True)
        with open("data/ev_api_results.json", "w") as f:
            json.dump(sf_data, f, indent=2)
        print("Saved filtered data to data/ev_api_results.json")
    else:
        print("Failed to fetch data:", response.status_code)
        
if __name__ == "__main__":
    fetch_ev_stations_sf()