# ⚡ EV Charging Monitor Dashboard

A real-time dashboard that simulates EV charging sessions across San Francisco. Built in Python and Streamlit, it tracks energy usage, charging duration, and cost per session - with dynamic GPS filtering, station-level analytics, and downloadable CSV logs.

> 🧪 Inspired by real-world QA & validation use cases in the EV ecosystem.

---
## 🚗 Features


- ✅ Simulates live EV charging sessions across 3 SF stations
- 🗺️ Interactive map using Folium
- 📍 GPS-based distance from user to station
- 🧮 Session-level analytics: energy (kWh), duration, cost
- 📆 Date range filtering + station filter
- 📥 CSV export for QA & analysis
- 🧠 Modular Python backend with object-oriented structure
- 🌱 Designed for future expansion (e.g. route planner, pricing logic, alerts)

---

## 📸 Demo

![EV Dashboard Preview](assets/demo.gif)
*(Streamlit dashboard with map + live session stats)*

---

## 📦 Tech Stack

- `Python`
- `Streamlit`
- `Pandas`
- `Folium`
- `Geopy`
- `VS Code` + `Git`

---

## 🛣️ Feature Roadmap

| Feature                        | Status   |
|-------------------------------|----------|
| Charging session simulation   | ✅ Done   |
| Station filtering + map view | ✅ Done   |
| Distance calculator           | ✅ Done   |
| Date range + CSV export       | ✅ Done   |
| 🔜 Route planner UI           | In progress |
| 🔜 Dynamic pricing (time of day) | Planned |
| 🔜 Mobile-friendly layout     | Planned |
| 🔜 Admin upload access        | Planned  |

---

## 🌁 About Me

Hi, I’m Sergio — a QA and systems engineer passionate about building meaningful tools in clean tech.  
I created this dashboard as a way to deepen my skills in Python and data visualization while solving real problems.  
My dream is to one day work on a product like this in San Francisco.  
**Unfinished business — building toward it every day.**

🔗 [My Portfolio](https://sergiohernandezjaimes.github.io)  
🐙 [My GitHub](https://github.com/sergiohernandezjaimes)

---

## Contribute or Fork

Want to build your own city-based version?
Fork this repo and modify `stations.json` to your region.
Pull requests welcome!