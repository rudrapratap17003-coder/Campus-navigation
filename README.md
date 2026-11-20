# Accessible Campus Navigator

A Python-based college campus accessibility and navigation system designed to empower students, staff, and visitors—especially individuals with mobility challenges—to navigate campus environments efficiently, safely, and independently.

---

## 🎯 Objectives

- **Inclusive Navigation:** Provide customized routing options catering to diverse accessibility requirements (e.g., wheelchair ramps, elevators, step-free access, tactile paths).
- **Dynamic Obstacle Awareness:** Enable real-time reporting and avoidance of temporary barriers (construction, broken elevators, maintenance work, crowded routes).
- **Interactive Campus Exploration:** Deliver rich, multi-layered visual representations of campus buildings, facilities, pathways, and accessibility infrastructure.
- **Data-Driven Insights:** Track route metrics, obstacle frequency, and pathway usage to assist campus administration in identifying accessibility bottlenecks and infrastructure improvements.

---

## ✨ Proposed Features

- **Multi-Modal Route Planning:**
  - Standard shortest path calculation using Dijkstra's and Breadth-First Search (BFS) graph algorithms.
  - Accessible routing preferences prioritizing elevators, ramps, wide corridors, and automated doors while avoiding stairs, steep slopes, and uneven surfaces.
- **Interactive Mapping:**
  - Geospatial and interactive map interfaces built with Folium and Plotly.
  - Layer toggles for accessible entrances, emergency points, rest zones, and transport stops.
- **Dynamic Obstacle & Hazard Reporting:**
  - Community-driven and administrative hazard logging stored via SQLite.
  - Real-time rerouting around active obstacles.
- **Analytics & Admin Dashboard:**
  - Overview of campus navigation flows, active barrier reports, accessibility coverage scores, and report statuses.
- **Modular Multi-Page Interface:**
  - Streamlit-powered responsive web interface organized into structured functional modules.

---

## 🛠️ Technology Stack

- **Core Programming Language:** Python 3.14
- **Web Interface:** Streamlit, Streamlit-Folium
- **Graph & Network Algorithms:** NetworkX, Custom Dijkstra & BFS implementations
- **Mapping & Geospatial Visualization:** Folium, Plotly
- **Data Processing & Manipulation:** Pandas
- **Database & Storage:** SQLite3, JSON Data Schemas

---

## 📁 Project Structure

```text
Campus navigation/
│
├── main.py                     # Primary Streamlit application entry point
├── requirements.txt            # Project dependencies and pinned package versions
├── README.md                   # Project documentation and architectural overview
├── .gitignore                  # Git exclusions for environments, databases, and caches
│
├── algorithms/                 # Graph search & pathfinding algorithms
│   ├── __init__.py
│   ├── bfs.py                  # Breadth-First Search implementation
│   └── dijkstra.py             # Dijkstra's shortest-path algorithm
│
├── modules/                    # Domain logic & business services
│   ├── __init__.py
│   ├── campus_map.py           # Campus network representation & graph loader
│   ├── accessibility.py        # Accessibility filters, penalty functions & constraints
│   ├── route_finder.py         # Route calculation engine & path optimization
│   └── obstacle_manager.py     # Obstacle lifecycle & active barrier avoidance
│
├── database/                   # Persistent data management
│   ├── __init__.py
│   └── db_manager.py           # SQLite connection, schemas, and query handlers
│
├── data/                       # Static graph & spatial datasets
│   └── campus_map.json         # Campus nodes, edges, coordinates, and attributes
│
├── pages/                      # Streamlit multi-page interface views
│   ├── dashboard.py            # Overview & statistics dashboard
│   ├── navigation.py           # Route query & turn-by-turn guidance page
│   ├── campus_map.py           # Interactive campus exploration map
│   ├── accessibility.py        # Accessibility profiles & amenity directory
│   └── obstacle_reports.py     # Hazard reporting & resolution interface
│
└── assets/                     # Media, icons, and styling stylesheets
```

---

## 🚀 Getting Started

1. **Activate Virtual Environment:**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

2. **Verify Dependencies:**
   ```powershell
   & ".venv\Scripts\python.exe" -m pip install -r requirements.txt
   ```

3. **Launch the Application:**
   ```powershell
   & ".venv\Scripts\python.exe" -m streamlit run main.py
   ```
