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
- **Advanced Interactive Indoor Map & Route Visualizer (Phase 8):**
  - Floor-by-floor navigation filtering for Ground Floor (Floor 0), First Floor (Floor 1), and a side-by-side All Floors architectural overview.
  - In-map route planning with dynamic gold route overlays, origin pins, and destination flags.
  - Automated cross-floor elevator transfer detection with step instructions.
  - Live color-coded obstacle visualization reflecting active verified obstructions directly from the SQLite database.
  - Single-location inspector panel displaying room categories, accessibility classifications, amenities, and connected links.

---

## 🗺️ Indoor Campus Map System & Coordinate Clarification

### Schematic Connectivity Layout Notice

> [!WARNING]
> **Coordinate Accuracy & Architectural Blueprint Limitations:**
> The 2D coordinates $(X, Y)$ utilized by the mapping visualizer are **illustrative graph-layout coordinates** designed strictly for schematic connectivity, topological pathfinding, and navigation demonstration. They are **not geographically surveyed coordinates** and do **not** claim architectural scale, room dimensions, or blueprint precision.
>
> The visualization engine in `modules/indoor_map.py` has been architected to cleanly accept high-resolution vector floor plans (SVG/DXF), architectural CAD exports, or georeferenced indoor GIS coordinates once physical building surveys are integrated.

### Multi-Floor Visualization Architecture

1. **Floor-by-Floor Separation:**
   - Filters nodes and intra-floor edges for the selected floor level (`Floor 0` or `Floor 1`).
2. **All-Floors Side-by-Side Architectural Plate:**
   - Because physical floors overlap in 2D space, the *All Floors* overview renders Floor 0 and Floor 1 side-by-side using an automatic plate offset ($X + 65.0$), allowing vertical elevator transfers and stairways to span visibly across levels.
3. **Color-Coded Pathway Classifications:**
   - 🟢 **Solid Green:** Accessible open corridors and ramps (`#2d6a4f` / `#40916c`).
   - 🔵 **Solid Teal:** Elevator vertical transitions (`#2a9d8f`).
   - 🟠 **Dotted Orange:** Staircase connections (`#e76f51`).
   - 🔴 **Dashed Red:** Verified blocked pathways (`#e63946`).
   - ⚪ **Dash-Dot Grey:** Unknown or unverified accessibility (`#6c757d`).
   - 🟡 **Thick Amber Overlay:** Active navigation path (`#f59e0b`).

---

## 💻 Streamlit Web Application Pages

The application is structured into five cohesive pages accessible via the sidebar navigation:

1. **📊 Dashboard (`pages/dashboard.py`):**
   - High-level metric summary: Total locations (15), total pathways (17), accessible pathways (16), active verified obstacles, pending reports, and resolved issues.
   - Interactive Plotly donut and bar charts showing pathway classifications and obstacle distribution (with empty-state handling).
   - Infrastructure summary for elevators, access ramps, and stairs.
   - Recent obstacle log and quick-action navigation shortcuts.
2. **🧭 Find Accessible Route (`pages/navigation.py`):**
   - Dropdown selectors for origin and destination with floor metadata.
   - Toggle between Dijkstra's algorithm (minimizing distance or travel time) and Breadth-First Search (minimizing transitions).
   - Wheelchair-only constraint toggle enforcing step-free routes through elevators and ramps.
   - Turn-by-turn instruction sequence with directional badges and segment metrics.
   - Alternative route suggestions.
3. **🗺️ Campus Map (`pages/campus_map.py`):**
   - Interactive indoor schematic map with floor filters (*Ground Floor*, *First Floor*, *All Floors*).
   - In-map route visualization with path overlays, origin/destination pins, and elevator transfer callouts.
   - Location details panel with connected link breakdown and active obstacle alerts.
4. **♿ Accessibility Overview (`pages/accessibility.py`):**
   - Explanation of the 5 standardized accessibility classifications.
   - Comprehensive inventory of all 17 campus connections with distances, times, and facilities.
   - Single-location inspector analyzing node accessibility and special amenities.
   - Prominent disclaimer regarding the algorithmic heuristic nature of the scores.
5. **⚠️ Obstacle Reports (`pages/obstacle_reports.py`):**
   - Complete incident audit log with filters by Status, Severity, and Category.
   - In-app reporting accordion to log field obstructions directly into the SQLite database.

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
   - User submits an obstacle report. Initial status is `Pending`. Pending reports **do not automatically block pathways**.
2. **Verification (`Verified`):**
   - Administrators confirm the report. Status transitions to `Verified`.
   - `ObstacleManager` applies a temporary `blocked` status to the affected live graph edge/node.
   - Dijkstra and BFS automatically detour around the blocked segment.
   - The map dynamically highlights the connection in dashed red (`#e63946`).
3. **Resolution (`Resolved`):**
   - Maintenance logs resolution notes. Pathway is restored to original status (`open`).
4. **Rejection (`Rejected`):**
   - Unsubstantiated reports are marked `Rejected` without affecting pathway availability.

---

## 🛠️ Technology Stack

- **Core Programming Language:** Python 3.14
- **Web Interface:** Streamlit (v1.67.0)
- **Graph & Network Algorithms:** NetworkX, Custom Dijkstra & BFS implementations
- **Mapping & Geospatial Visualization:** Plotly, Folium, streamlit-folium
- **Data Processing & Manipulation:** Pandas
- **Database & Storage:** SQLite3, JSON Data Schemas

---

## 📁 Project Structure

```text
Campus navigation/
│
├── main.py                     # Primary Streamlit application entry point & router
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
│   ├── obstacle_manager.py     # Obstacle lifecycle & dynamic detour management
│   ├── indoor_map.py           # Indoor map engine, floor filters & visualizer
│   └── ui_theme.py             # Shared styling, theme injection & session services
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
│   ├── campus_map.py           # Interactive indoor campus map & route visualizer
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
    ├── test_obstacle_manager.py# Obstacle lifecycle, SQLite, and detour tests
    └── test_indoor_map.py      # Floor filtering, cross-floor transit & visualizer tests
```

---

## 🧪 Running Automated Tests

All test suites use isolated in-memory or temporary databases to prevent altering the application database:

```powershell
& ".venv\Scripts\python.exe" -m unittest discover tests
```

To run individual test suites:
```powershell
& ".venv\Scripts\python.exe" -m unittest tests/test_indoor_map.py
& ".venv\Scripts\python.exe" -m unittest tests/test_obstacle_manager.py
& ".venv\Scripts\python.exe" -m unittest tests/test_route_finder.py
```

---

## 🚀 Getting Started & Launching the Web App

1. **Activate Virtual Environment:**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

2. **Verify Dependencies:**
   ```powershell
   & ".venv\Scripts\python.exe" -m pip install -r requirements.txt
   ```

3. **Launch the Streamlit Web Application:**
   ```powershell
   & ".venv\Scripts\python.exe" -m streamlit run main.py
   ```
   Open your browser to [http://localhost:8501](http://localhost:8501) to explore the interface.
