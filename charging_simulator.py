import csv
import os
from datetime import datetime, timedelta
import random

class ChargingSession:
    def __init__(self, station_id, power_kw=7.2):
        self.session_id = f"S{random.randint(1000, 9999)}"
        self.station_id = station_id
        self.power_kw = power_kw
        self.start_time = datetime.now()
        self.duration_min = random.randint(10, 60)
        self.energy_kwh = round((self.power_kw * self.duration_min) / 60, 2)
        self.cost_usd = round(self.energy_kwh * 0.25, 2)
        self.end_time = self.start_time + timedelta(minutes=self.duration_min)

        if not station_id or not isinstance(station_id, str):
            raise ValueError("Invalid station ID. Must be a non-empty string.")

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "station_id": self.station_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration_min": self.duration_min,
            "energy_kwh": self.energy_kwh,
            "cost_usd": self.cost_usd
        }
    
def log_session(session: ChargingSession, file_path="data/charging_log.csv"):
    os.makedirs("data", exist_ok=True)
    file_exists = os.path.isfile(file_path)
    try: 
        with open(file_path, mode="a", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=session.to_dict().keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(session.to_dict())
    except Exception as e:
        print(f"Failed to log session: {e}")


# Test run
def simulate_multiple_sessions(station_id, num_sessions=5):
     for _ in range(num_sessions):
          session = ChargingSession(station_id=station_id)
          print("Session:", session.to_dict())
          log_session(session)

if __name__ == "__main__":
    print("Simulating 5 sessions at SF-001...")
    simulate_multiple_sessions("SF-001", num_sessions=5)
    print("All sessions logged to data/charging_log.csv")
