import requests
import json

def fetch_ev_stations_sf():
    url = "https://api.openchargemap.io/v3/poi/"
    params = {
        "output": "json",
        "countrycode": "US",
        "maxresults": 10,
        "latitud": 37.7749,
        "longitude": -122.4194,
        "distance": 10,
        "distanceunit": "Miles",
    }
    headers = {
        "X-API-Key": "a6092917-0057-4768-8cf9-ca86725e6310", # This is a public test key
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        with open("data/ev_api_results.json", "w") as f:
            json.dump(data, f, indent=2)
        print("Data fetched and saved!")
    else:
        print("Failed to fetch data:", response.status_code, response.text)
        
if __name__ == "__main__":
    fetch_ev_stations_sf()