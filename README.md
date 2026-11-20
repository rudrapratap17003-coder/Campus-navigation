# Accessible Campus Navigator

A Python-based college campus accessibility and navigation system designed to empower students, staff, and visitors—especially individuals with mobility challenges—to navigate campus environments efficiently, safely, and independently.

---

## 🎯 Objectives

- **Inclusive Navigation:** Provide customized routing options catering to diverse accessibility requirements (e.g., wheelchair ramps, elevators, step-free access, tactile paths).
- **Dynamic Obstacle Awareness:** Enable real-time reporting and avoidance of temporary barriers (construction, broken elevators, maintenance work, crowded routes).
- **Interactive Campus Exploration:** Deliver rich, multi-layered visual representations of campus buildings, facilities, pathways, and accessibility infrastructure.
- **Data-Driven Insights:** Track route metrics, obstacle frequency, and pathway usage to assist campus administration in identifying accessibility bottlenecks and infrastructure improvements.

---

## ✨ Implemented Core Features

- **Multi-Modal Route Planning:**
  - Standard shortest path calculation using Dijkstra's and Breadth-First Search (BFS) graph algorithms.
  - Accessible routing preferences prioritizing elevators, ramps, wide corridors, and automated doors while avoiding stairs, steep slopes, and uneven surfaces.
  - Alternative route calculation using edge-penalty detours.
- **Accessibility Intelligence Engine:**
  - Standardized pathway classification: *Fully Accessible*, *Accessible with Assistance*, *Not Wheelchair Accessible*, *Temporarily Blocked*, and *Unknown Accessibility*.
  - Heuristic continuous scoring formula (0–100) reflecting step-free status, ramps, elevators, staircase barriers, and temporary obstructions.
  - Turn-by-turn guidance and automated warning alerts.
- **Dynamic Obstacle Reporting & SQLite Database Integration:**
  - Community-driven and administrative hazard logging stored persistently in SQLite.
  - Comprehensive lifecycle management: *Pending*, *Verified*, *Resolved*, and *Rejected*.
  - Dynamic graph synchronization: verified active obstacles dynamically update live path availability without overwriting raw dataset attributes.
  - Immediate operational restoration upon report resolution.

---

## 🗄️ Database Architecture & Obstacle Management

Persistent storage is implemented via Python's built-in `sqlite3` module with foreign key enforcement and parameterized SQL queries to prevent SQL injection vulnerabilities.

### SQLite Database Schema (`obstacle_reports`)

```sql
CREATE TABLE IF NOT EXISTS obstacle_reports (
    report_id TEXT PRIMARY KEY,
    location_id TEXT,
    source_location_id TEXT,
    destination_location_id TEXT,
    target_type TEXT NOT NULL CHECK(target_type IN ('location', 'pathway')),
    obstacle_category TEXT NOT NULL,
    description TEXT NOT NULL,
    severity TEXT NOT NULL CHECK(severity IN ('Low', 'Medium', 'High', 'Critical')),
    reported_at TEXT NOT NULL,
    reporter_name TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('Pending', 'Verified', 'Resolved', 'Rejected')),
    resolution_notes TEXT,
    updated_at TEXT NOT NULL
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_obstacle_status ON obstacle_reports (status);
CREATE INDEX IF NOT EXISTS idx_obstacle_location ON obstacle_reports (location_id);
CREATE INDEX IF NOT EXISTS idx_obstacle_pathway ON obstacle_reports (source_location_id, destination_location_id);
CREATE INDEX IF NOT EXISTS idx_obstacle_reported_at ON obstacle_reports (reported_at);
```

### Report Verification Workflow & Lifecycle

1. **Submission (`Pending`):**
   - User or campus member submits an obstacle report specifying a target (location or pathway), category, severity, and description.
   - Initial status is `Pending`. **Pending reports do not automatically block pathways**, preventing false alarms from disrupting campus flow.
2. **Verification (`Verified`):**
   - Facility administrators review the submission. Once confirmed, the report transitions to `Verified`.
   - `ObstacleManager` automatically applies a temporary `blocked` operational status to the affected live graph edge/node while preserving original JSON dataset attributes.
   - Navigation engines (Dijkstra and BFS) dynamically detour around the blocked segment.
   - `AccessibilityEngine` updates pathway assessment to `Temporarily Blocked` (score: 0.0).
3. **Resolution (`Resolved`):**
   - Maintenance completes repairs and logs mandatory resolution notes.
   - If no other active verified reports affect the pathway, `ObstacleManager` automatically restores the pathway to its original operational state (`open`).
4. **Rejection (`Rejected`):**
   - Unsubstantiated or duplicate reports are marked `Rejected` with an explanation.
   - Rejected reports never alter pathway availability.

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
│   ├── accessibility.py        # Accessibility classification, heuristics & scoring
│   ├── route_finder.py         # Route calculation engine & path optimization
│   └── obstacle_manager.py     # Obstacle lifecycle & dynamic detour management
│
├── database/                   # Persistent data management
│   ├── __init__.py
│   └── db_manager.py           # SQLite connection, schemas, and parameterized queries
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
├── assets/                     # Media, icons, and styling stylesheets
│   └── .gitkeep
│
└── tests/                      # Automated unit test suite
    ├── __init__.py
    ├── test_campus_map.py      # Campus map parsing and data validation tests
    ├── test_bfs.py             # BFS routing and hop-count optimality tests
    ├── test_dijkstra.py        # Dijkstra distance/time optimization tests
    ├── test_route_finder.py    # Multi-modal routing & alternative route tests
    ├── test_accessibility.py   # Accessibility engine & heuristic scoring tests
    └── test_obstacle_manager.py# Obstacle lifecycle, SQLite, and detour tests
```

---

## 🧪 Running Automated Tests

All test suites use isolated in-memory or temporary databases to prevent altering the application database:

```powershell
& ".venv\Scripts\python.exe" -m unittest discover tests
```

To run individual test suites:
```powershell
& ".venv\Scripts\python.exe" -m unittest tests/test_obstacle_manager.py
& ".venv\Scripts\python.exe" -m unittest tests/test_accessibility.py
& ".venv\Scripts\python.exe" -m unittest tests/test_route_finder.py
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

3. **Launch Application:**
   ```powershell
   & ".venv\Scripts\python.exe" -m streamlit run main.py
   ```
