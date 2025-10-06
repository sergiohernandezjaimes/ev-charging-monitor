# simulate_sessions.py
# Generate mock EV charging session logs based on stations in ev_api_results.json

import pandas as pd
import random
from datetime import datetime, timedelta
import json 
import os

# Load station metadeta 
with open("data/ev_api_results.json", "r") as f:
    stations = json.load(f)

station_ids = []
for s in stations:
    sid = (
         s.get("station_id") 
         or s.get("id")
         or ("station_id") or s.get("id")
    )
    if sid:
        station_ids.append(str(sid))

# How many sessions to simulate
def generate_sessions(n=50):
    sessions = []
    now = datetime.now()

    for i in range(n):
        station_id = random.choice(station_ids)
        start_time = now - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
        duration_min = random.randint(20, 120)
        energy_kwh = round(duration_min * random.uniform(0.2, 0.4), 2)
        cost_usd = round(energy_kwh * random.uniform(0.15, 0.30), 2)

        sessions.append({
            "session_id": f"S{i+1:03}",
            "station_id": station_id,
            "start_time": start_time,
            "duration_min": duration_min,
            "energy_kwh": energy_kwh,
            "cost_usd": cost_usd,
            "charger_level": random.choice([1,2,3]),
            "availability": random.choice(["Available", "In Use", "Offline"])
        })
    return sessions

sessions = generate_sessions(50)    

# Save to CSV
df = pd.DataFrame(sessions)
df.to_csv("data/charging_log.csv", index=False)
print(f"Generated 50 sessions -> data/charging_log.csv")