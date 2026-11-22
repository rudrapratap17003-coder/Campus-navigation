# FINAL PROJECT TECHNICAL EXPLANATION HANDBOOK

**Project Title:** Accessible Campus Navigator  
**Lead Developer & System Architect:** Rudra Pratap  
**USN:** 25BTRCL214  
**Department:** Artificial Intelligence and Machine Learning  
**Institution:** JAIN (Deemed-to-be University) — Faculty of Engineering and Technology (FET)  
**Target Audience:** Evaluators, Faculty Reviewers, Presenters, and Technical Auditors  

---

## 1. PROJECT INTRODUCTION
Accessible Campus Navigator is an intelligent, accessibility-aware wayfinding and digital twin platform developed specifically for JAIN Global Campus and its five-storey Faculty of Engineering and Technology (FET) facility. The system integrates mathematical graph algorithms, multi-floor indoor mapping, wheelchair constraint solving, dynamic obstacle reporting with operational lifecycles, and a hardware-accelerated 3D WebGL digital twin into a single, cohesive web application.

---

## 2. PROBLEM STATEMENT
University campuses are large, dynamic, and architecturally complex. For new students, visiting researchers, and attendees, locating specialized laboratories, seminar halls, and faculty rooms is time-consuming. Commercial wayfinding systems (e.g., Google Maps) provide outdoor road guidance but terminate abruptly at building entrances, providing zero interior guidance.

Crucially, for individuals with physical mobility impairments, temporary injuries, or heavy laboratory transport needs, standard campus navigation presents invisible barriers: sudden staircases, missing curb ramps, and unannounced elevator outages turn standard walks into impassable routes. Static signage cannot adapt to live campus disruptions.

---

## 3. MOTIVATION
The motivation for this project stems from the conviction that physical accessibility is a prerequisite for educational equity. Under UN Sustainable Development Goals (SDG 10: Reduced Inequalities and SDG 11: Sustainable Cities & Communities), educational institutions must provide inclusive infrastructure. By engineering an intelligent, software-driven navigation platform, JAIN University can empower all students to navigate campus independently, safely, and with dignity.

---

## 4. PROJECT OBJECTIVES
1. **Unified Graph Modeling:** Create an integrated mathematical graph bridging outdoor walkways and 5-storey indoor floor plans into a continuous navigational topology.
2. **Deterministic Algorithmic Routing:** Implement and contrast Breadth-First Search (BFS) and Dijkstra's algorithm, demonstrating physical distance versus transition optimization.
3. **Accessibility Equity:** Implement an automated step-free filter that strips staircases, forces certified elevator routes, and calculates heuristic accessibility confidence scores.
4. **Dynamic Obstacle Resilience:** Build a closed-loop obstacle reporting lifecycle (Pending → Verified → Resolved) with instantaneous in-memory graph edge severance.
5. **Interactive 3D Digital Twin:** Construct a lightweight, procedural Three.js WebGL model offering spatial intuition and floor isolation slicing without heavy hardware demands.
6. **Enterprise Backend Security:** Implement PBKDF2 password hashing, Role-Based Access Control (RBAC), and immutable audit trails in SQLite.

---

## 5. FUNCTIONAL REQUIREMENTS
- **FR1 (Authentication & RBAC):** Support secure user registration, login, and tiered role enforcement (`Student`, `Field Staff`, `Administrator`).
- **FR2 (Campus Exploration & Search):** Provide interactive 2D and 3D maps with autocomplete search across 79 campus landmarks.
- **FR3 (Route Calculation):** Calculate optimal point-to-point routes with turn-by-turn guidance, distance, time, and compass bearings.
- **FR4 (Wheelchair Constraint Mode):** Allow users to restrict routes to step-free paths, prioritizing ramps and passenger elevators.
- **FR5 (Algorithmic Comparison):** Provide side-by-side comparison between Dijkstra and BFS path metrics.
- **FR6 (Multi-Floor Slicing):** Enable discrete indoor floor filtering for Ground, 1st, 2nd, 3rd, and 4th floors.
- **FR7 (Obstacle Lifecycle):** Allow students to report hazards and authorized staff to verify or resolve them, triggering live rerouting.
- **FR8 (Spatial Analytics):** Display barrier distributions, resolution times, and pathway statistics using interactive Plotly charts.
- **FR9 (Multilingual Interface):** Support language switching across English, Kannada, and Hindi.

---

## 6. NON-FUNCTIONAL REQUIREMENTS
- **NFR1 (Performance):** Route calculation on the 79-node graph must execute in under 10 milliseconds; 3D rendering must maintain 60 FPS in standard browsers.
- **NFR2 (Reliability):** SQLite must operate in Write-Ahead Logging (WAL) mode with busy timeout handling to eliminate database locks.
- **NFR3 (Security):** Zero plaintext passwords; passwords hashed using PBKDF2 with 600,000 SHA-256 iterations and 32-byte salts; brute-force login rate limiting (5 attempts = 300s lockout).
- **NFR4 (Accessibility Standards):** UI must adhere to WCAG 2.1 AA contrast requirements (> 4.5:1 ratio) using dark-forest green palette (`#07130F`, `#16A36A`, `#35D99A`).
- **NFR5 (Maintainability):** Backed by 208 automated unit and regression tests with 100% pass rate.

---

## 7. SYSTEM ARCHITECTURE
The system employs a 4-tier layered architectural pattern:
```
+-------------------------------------------------------+
|                 PRESENTATION LAYER                    |
| Streamlit Multi-Page UI • WCAG 2.1 AA Dark Theme     |
| (Dashboard, Navigation, Campus Map, 3D Map, Admin)   |
+-------------------------------------------------------+
                           |
+-------------------------------------------------------+
|                   SERVICE LAYER                       |
| RouteFinder • AccessibilityEngine • ObstacleManager  |
| CampusAnalytics • TranslationService • SecurityManager|
+-------------------------------------------------------+
                           |
+-------------------------------------------------------+
|                 CORE ENGINES LAYER                    |
| NetworkX Undirected Weighted Graph (79 Nodes, 106 Edges)|
| Three.js WebGL Procedural 3D Scene Engine             |
+-------------------------------------------------------+
                           |
+-------------------------------------------------------+
|                DATA PERSISTENCE LAYER                 |
| SQLite in WAL Mode • Immutable Audit Logs            |
| Campus Spatial JSON • Automated Online Backups        |
+-------------------------------------------------------+
```

---

## 8. TECHNOLOGY STACK & SELECTION RATIONALE
- **Python 3.11+:** Robust standard library, graph algorithm support, high readability.
- **Streamlit:** Python-native reactive web interface; manages session state without REST API overhead.
- **NetworkX:** Industry-standard graph library with native priority-queue Dijkstra and BFS solvers.
- **SQLite (WAL):** Serverless, zero-configuration relational database; ACID compliant with low memory overhead.
- **Three.js & WebGL:** Hardware-accelerated 3D graphics in standard browsers without external plugins.
- **Plotly & Folium:** Geospatial coordinate plotting and interactive analytics charts.
- **python-pptx & ReportLab:** Automated generation of academic presentations and PDF artifacts.

---

## 9. DATA STRUCTURES
- **Adjacency List (Dict-of-Dicts):** NetworkX stores graph edges as nested hash maps, providing $O(1)$ edge existence checks and neighbor lookups.
- **Binary Min-Heap:** Priority queue for Dijkstra's algorithm, enabling $O(\log V)$ extraction of minimum-distance vertices.
- **FIFO Queue:** Standard queue for BFS level-by-level traversal.
- **Hash Table (Set):** Visited node sets providing $O(1)$ cycle prevention.
- **Relational Tables:** B-tree indexed relational tables in SQLite for users, reports, and audit logs.

---

## 10. ALGORITHMIC ENGINE

### 10.1 Breadth-First Search (BFS)
- **Principle:** Explores unweighted graphs level by level via FIFO queue.
- **Formula:** Minimizes edge count: $\min |E_{\text{path}}|$.
- **Complexity:** Time $O(V + E)$, Space $O(V)$.
- **Implementation:** `algorithms/bfs.py`.

### 10.2 Dijkstra's Algorithm
- **Principle:** Traverses weighted graphs with non-negative edge weights using a min-priority queue.
- **Formula:** Minimizes cumulative weight: $\min \sum_{(u, v) \in P} w(u, v)$.
- **Complexity:** Time $O((E + V) \log V)$, Space $O(V)$.
- **Implementation:** `algorithms/dijkstra.py`.

### 10.3 Comparative Analysis
On a real query (Main Gate to FET Auditorium):
- **Dijkstra:** 420 meters (7 nodes traversed) — physically shorter.
- **BFS:** 465 meters (6 nodes traversed) — fewer hops, but physically longer.
- **Conclusion:** Weighted Dijkstra is mandatory for realistic pedestrian routing.

---

## 11. ACCESSIBILITY ENGINE

### 11.1 Dynamic Subgraph Pruning
When wheelchair mode is enabled:
$$G' = (V, E \setminus E_{\text{stairs}})$$
Edges tagged with `edge_type == 'stairs'` are stripped, forcing traversal through ramps and elevators.

### 11.2 Heuristic Accessibility Scoring
$$\text{Score} = 100 - (\text{penalty}_{\text{stairs}} + \text{penalty}_{\text{slope}} + \text{penalty}_{\text{width}} + \text{penalty}_{\text{surface}})$$
If stairs are present on a route, the score is capped at 20/100.
- **Files:** `modules/accessibility.py`.
- **Limitation:** Scores are heuristic estimates based on recorded attributes, requiring physical on-ground confirmation.

---

## 12. INDOOR NAVIGATION (FIVE-FLOOR FET BUILDING)
- **What it does:** Maps all 5 storeys of the FET building with 45+ laboratories, classrooms, and facilities.
- **How it works:** Each floor is represented as a 2D Cartesian plane ($Z = \text{floor\_id} \times 4.0\text{m}$). Vertical transitions (elevators and stairwells) are modeled as inter-floor edges.
- **Files:** `modules/jain_digital_twin.py`, `pages/campus_map.py`.
- **Demonstration:** Switch floor views from Ground to 4th floor; select a multi-floor route from Main Entrance to 2nd-floor AI Lab.

---

## 13. OUTDOOR CAMPUS NAVIGATION
- **What it does:** Connects campus gates, hostel blocks, sports complexes, libraries, and food courts to academic buildings.
- **How it works:** Models major asphalt walkways and pedestrian corridors with physical length measurements and incline tags.
- **Files:** `data/jain_global_campus.json`, `pages/campus_map.py`.

---

## 14. 3D DIGITAL TWIN
- **What it does:** Renders a 3D procedural campus model in WebGL with interactive orbit controls, floor isolation, and route splines.
- **How it works:** `modules/three_d_map.py` serializes spatial metadata into JSON, injected into a Three.js canvas. CatmullRom splines draw 3D glowing route lines.
- **Files:** `modules/three_d_map.py`, `pages/3d_campus_map.py`.
- **Limitation:** Schematic model for wayfinding intuition, not a surveyed architectural BIM/CAD model.

---

## 15. DATABASE ARCHITECTURE
- **Engine:** SQLite 3 in WAL mode.
- **Tables:** `users`, `obstacle_reports`, `audit_logs`, `schema_version`.
- **Key Methods:** `create_user()`, `authenticate_user()`, `submit_obstacle_report()`, `verify_obstacle_report()`, `backup_database()`, `restore_database()`.
- **Files:** `database/db_manager.py`.

---

## 16. AUTHENTICATION & SECURITY
- **Password Security:** PBKDF2-HMAC-SHA256 with 600,000 iterations and 32-byte salts.
- **RBAC:** Three tiers (`Student`, `Field Staff`, `Administrator`) with strict privilege enforcement.
- **Brute-Force Rate Limiting:** 5 failed attempts locks user/IP for 300 seconds.
- **Audit Logging:** Immutable `audit_logs` table records every role modification and obstacle event.
- **Demo Remediation:** Default credentials deactivated; initial setup requires interactive bootstrap wizard.

---

## 17. DYNAMIC OBSTACLE REPORTING LIFECYCLE
- **Lifecycle Sequence:** `Pending` → `Verified` → `Resolved` / `Rejected`.
- **Operational Logic:**
  1. Student submits hazard report → Status: `PENDING` (graph remains open).
  2. Field Staff inspects and verifies → Status: `VERIFIED` ($w(e) = \infty$, edge severed).
  3. Staff clears hazard with notes → Status: `RESOLVED` ($w(e)$ restored).
- **Files:** `pages/obstacle_reports.py`, `modules/obstacle_manager.py`.

---

## 18. TESTING & QUALITY ASSURANCE
- **Test Suite:** 208 automated test cases in `tests/`.
- **Execution Time:** ~52 seconds with 0 failures and 0 errors.
- **Compilation:** `python -m compileall -q .` exited with code 0.
- **Coverage:** Tests cover BFS, Dijkstra, wheelchair pruning, WAL persistence, schema migrations, RBAC, and rate limiting.

---

## 19. PRODUCTION DEPLOYMENT & RELEASE ENGINEERING
- **Containerization:** Multi-stage `Dockerfile` running as non-root user.
- **Reverse Proxy:** Nginx handling HTTPS termination and WebSocket upgrades.
- **Orchestration:** `docker-compose.yml` mounting persistent volume `./data:/app/data`.
- **Cloud Readiness:** Streamlit Cloud `st.secrets` adapter implemented; Status C (Deployment Prepared, User Action Required).

---

## 20. PROJECT LIMITATIONS (HONEST DISCLOSURE)
1. **Schematic Spatial Coordinates:** Node coordinates are mapped to campus layouts rather than geodetic GPS surveys.
2. **Manual Waypoint Entry:** Real-time indoor beacon positioning (BLE/WiFi RTT) is not implemented.
3. **Heuristic Accessibility:** Accessibility scores are mathematical estimates requiring on-ground verification.
4. **Schematic 3D Geometry:** Three.js visualization is procedural and schematic, not a structural BIM model.
5. **Public Cloud Status:** Prepared and containerized; public domain activation requires owner GitHub OAuth.

---

## 21. FUTURE IMPROVEMENTS
1. **BLE Beacon Positioning:** Deploy low-cost Bluetooth beacons for live indoor blue-dot positioning.
2. **Synthetic Voice Guidance:** Text-to-speech turn-by-turn audio cues for visually impaired students.
3. **Crowdsourced Accessibility Notes:** Allow students to attach photo reviews of ramp quality and doorway conditions.
4. **University Timetable Integration:** Synchronize student class schedules to automatically route them to their next classroom.
