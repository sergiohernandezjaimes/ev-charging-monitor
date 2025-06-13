# ⚡ EV Charging Session Monitor

This project simulates EV charging station activity across San Francisco using real-time generated data, GPS mapping, and interactive dashboard. The tool provides insights into session logs, energy usage, and cost - with filter options by station ID and date range, plus CSV export functionality.

It's designed as a diagnostic and analytics dashboard for electric vehicle infrastructure monitoring, and showcases full-stack development using Python and Streamlit.

---
## ✨ Features


- 📍 GPS-based station map (San Francisco view)
- 📊 Charging session log table with station ID, energy, duration, and cost
- 📆 Date and station filters with reset support
- 📈 Energy, duration, and cost charts
- 📥 Export filtered sessions as CSV
- 🧠 Random session generation via simulation script

---

## 🛠️ Tech Stack

- **Python 3.10+**
- [Streamlit](https://streamlit.io/) – web app framework
- [Folium](https://python-visualization.github.io/folium/) – map rendering
- [Pandas](https://pandas.pydata.org/) – data manipulation
- [geopy](https://github.com/geopy/geopy) – distance calculation
- [streamlit-folium](https://github.com/randyzwitch/streamlit-folium) – map embed wrapper

---

## 🚀 Live Demo

Check out the deployed dashboard:  
👉 [ev-charging-monitor.streamlit.app](https://ev-charging-monitor.streamlit.app/)

---

## 🛠️ Run Locally

Clone the repo:

```bash
git clone https://github.com/sergiohernandezjaimes/ev-charging-monitor.git
cd ev-charging-monitor
pip install -r requirements.txt
streamlit run dashboard.py
```
---

## ✍️ Author

**Sergio Hernandez**  
GitHub: [@sergiohernandezjaimes](https://github.com/sergiohernandezjaimes.com/)
LinkedIn: [LinkedIn Profile](https://www.linkedin.com/in/sergio-hernandez-1948b0159.com/)
