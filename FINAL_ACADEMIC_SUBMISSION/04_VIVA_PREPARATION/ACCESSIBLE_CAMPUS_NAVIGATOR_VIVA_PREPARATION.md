# Accessible Campus Navigator — Comprehensive Academic Viva Preparation Guide

**Project Title:** Accessible Campus Navigator — JAIN Global Campus & FET 3D Digital Twin  
**Target Level:** Undergraduate / Postgraduate Computer Science & Engineering Examination Defense  
**Evaluation Scope:** Algorithmics, 3D Computer Graphics, Database Systems, Web Architecture, Cybersecurity, and Software Testing  

---

## TABLE OF CONTENTS

- [PART 1 — ARCHITECTURAL & THEORETICAL FOUNDATIONS (SECTIONS 1–24)](#part-1--architectural--theoretical-foundations)
  - [1. Project Introduction](#1-project-introduction)
  - [2. Problem Statement](#2-problem-statement)
  - [3. Objectives](#3-objectives)
  - [4. Existing System Limitations](#4-existing-system-limitations)
  - [5. Proposed System](#5-proposed-system)
  - [6. System Architecture](#6-system-architecture)
  - [7. Technology Stack](#7-technology-stack)
  - [8. Database Architecture](#8-database-architecture)
  - [9. Graph Representation of the Campus](#9-graph-representation-of-the-campus)
  - [10. Dijkstra Algorithm Explanation](#10-dijkstra-algorithm-explanation)
  - [11. BFS Algorithm Explanation](#11-bfs-algorithm-explanation)
  - [12. Wheelchair-Accessible Routing Logic](#12-wheelchair-accessible-routing-logic)
  - [13. Multi-Floor Navigation](#13-multi-floor-navigation)
  - [14. 3D Digital Twin Architecture](#14-3d-digital-twin-architecture)
  - [15. Obstacle Reporting & Route Recalculation](#15-obstacle-reporting--route-recalculation)
  - [16. Authentication & RBAC](#16-authentication--rbac)
  - [17. Password Hashing & Security Hardening](#17-password-hashing--security-hardening)
  - [18. Campus Analytics & Intelligence](#18-campus-analytics--intelligence)
  - [19. Internationalization & Accessibility Standards](#19-internationalization--accessibility-standards)
  - [20. Docker & Deployment Architecture](#20-docker--deployment-architecture)
  - [21. Testing Strategy & Actual Results](#21-testing-strategy--actual-results)
  - [22. System Limitations](#22-system-limitations)
  - [23. Future Enhancements](#23-future-enhancements)
  - [24. Conclusion](#24-conclusion)
- [PART 2 — 40+ COMPREHENSIVE VIVA QUESTIONS & ANSWERS](#part-2--40-comprehensive-viva-questions--answers)

---

# PART 1 — ARCHITECTURAL & THEORETICAL FOUNDATIONS

### 1. Project Introduction
The **Accessible Campus Navigator** is an interactive 3D digital twin and accessibility-first pedestrian wayfinding system. It models the 300-acre **JAIN Global Campus** on Kanakapura Road and the 5 physical floors of the octagonal **Faculty of Engineering and Technology (FET)** building. It provides safe, reliable, and step-free navigation guidance for students, visitors, elderly guests, and persons with mobility impairments.

### 2. Problem Statement
Commercial navigation engines (e.g., Google Maps, Apple Maps) excel at outdoor vehicular routing but fail within university campuses. Specifically, they:
1. Treat multi-story academic buildings as flat, single-point coordinates without indoor room resolution.
2. Lack awareness of vertical accessibility infrastructure (elevators, stairs, ramps).
3. Do not track temporary physical barriers (maintenance work, broken lifts, construction barricades).
4. Do not offer step-free navigation guarantees for wheelchair users.

### 3. Objectives
- **Mathematically Guaranteed Accessibility:** Formulate constrained shortest-path graph algorithms that strictly eliminate physical barriers (staircases) for wheelchair users.
- **Indoor/Outdoor Unified 3D Digital Twin:** Reconstruct the complete campus and a 5-floor architectural model in Three.js WebGL with floor isolation and exploded views.
- **Dynamic Obstacle Synchronization:** Enable real-time community hazard reporting with role-based field verification that dynamically modifies active graph edges.
- **Inclusive Universal Design:** Support multilingual translation (English, Kannada, Hindi), WCAG AAA high contrast, and reduced motion.
- **Production-Ready Architecture:** Containerized deployment using Docker, Nginx reverse proxying, SQLite WAL persistence, and comprehensive automated test suites.

### 4. Existing System Limitations
- **Flat 2D Maps:** Inability to visualize multi-floor room relationships and elevator shafts.
- **Static Graph Topology:** Inability to alter path availability when a physical corridor is closed.
- **Absence of User Roles:** No segregation between anonymous user reports and authenticated facility staff verification.
- **Unverified Data:** Many academic navigation projects present hardcoded routes without dynamic path calculation or database persistence.

### 5. Proposed System
Our system represents the campus as an undirected weighted spatial graph $G = (V, E)$. Nodes $V$ represent physical rooms, entrances, and vertical junctions; edges $E$ represent walkable pathways with distance, time, and accessibility attributes. Users calculate optimal routes using Dijkstra or BFS, explore the 3D campus, view dynamic detours around verified hazards, and inspect operational analytics.

### 6. System Architecture
The application follows a 3-tier modular architecture:
1. **Presentation Layer:** Streamlit 1.67 multi-page application with dark-forest-green glassmorphism CSS, Three.js WebGL canvas, and Plotly analytics charts.
2. **Business Logic & Service Layer:** NetworkX graph algorithms, `RouteFinder`, `AccessibilityEngine`, `ObstacleManager`, and `DestinationSearch`.
3. **Data & Persistence Layer:** SQLite 3 database operating in WAL mode with connection pooling, automated snapshot backups, and structured domain error handling.

### 7. Technology Stack
- **Language:** Python 3.11 / 3.12
- **Web UI & Rendering:** Streamlit 1.67.0, Three.js (r128 WebGL), Plotly 7.1.0, HTML5/CSS3
- **Graph & Algorithms:** NetworkX 3.7 (Dijkstra, BFS, Detour generation)
- **Database & Security:** SQLite3 (WAL mode), PBKDF2-HMAC-SHA256 (600,000 rounds)
- **DevOps & Containers:** Docker (python:3.11-slim base, non-root user), Docker Compose, Nginx (WebSocket reverse proxy), POSIX Bash & PowerShell automation

### 8. Database Architecture
The SQLite database (`campus.db`) uses strict foreign keys (`PRAGMA foreign_keys = ON;`) and WAL journaling (`PRAGMA journal_mode = WAL;`). Core relational tables include:
- `users`: ID, username, password_hash, salt, role (`Student`, `Field Staff`, `Administrator`), status (`active`, `deactivated`), failed_attempts, lockout_until, hash_iterations.
- `obstacle_reports`: Report ID, category, severity, description, status (`Pending`, `Verified`, `Resolved`, `Rejected`), source_location_id, destination_location_id, reporter_name, resolution_notes.
- `administrative_audit_log`: Audit ID, user_id, action, target_type, target_id, details, timestamp.
- `navigation_history`: Session ID, user_id, start_node, destination_node, algorithm, accessible_only, distance, transit_time.
- `user_saved_places` & `user_favourite_routes`: Account-isolated bookmarking tables.
- `campus_user_feedback`: User category feedback and administrative review records.

### 9. Graph Representation of the Campus
- **Vertices ($V = 79$):** 12 outdoor facilities (Gates, Quad, Sports Arena, Dining, Hostels), 67 indoor FET facilities across Floors 0 to 4 (Classrooms, AI Labs, HPC Supercomputer, Restrooms, Elevators, Stairwells).
- **Edges ($E = 106$):** 16 outdoor pathways, 66 intra-floor corridors, 24 vertical connectors (4 elevator inter-floor segments, 20 staircase inter-floor segments).
- **Edge Attributes:** `distance` (meters), `estimated_time` (seconds), `wheelchair_accessible` (boolean), `has_stairs` (boolean), `has_ramp` (boolean), `has_elevator` (boolean), `status` (`open` or `blocked`).

### 10. Dijkstra Algorithm Explanation
Dijkstra's algorithm finds the shortest path between a source node $s$ and all other nodes in a graph with non-negative edge weights $w(u, v) \ge 0$.
- **Mechanism:** Maintains a priority queue (min-heap) of tentative distances. At each step, it extracts the node $u$ with the minimum tentative distance, inspects each outgoing edge $(u, v)$, and performs edge relaxation:
  $$\text{If } d[u] + w(u, v) < d[v] \implies d[v] = d[u] + w(u, v)$$
- **Time Complexity:** $O((|V| + |E|) \log |V|)$ using a binary min-heap.
- **Space Complexity:** $O(|V|)$ for distance array and predecessor map.
- **Optimization Metric:** In our system, Dijkstra optimizes either physical distance (meters) or transit duration (seconds).

### 11. BFS Algorithm Explanation
Breadth-First Search (BFS) traverses an unweighted graph layer by layer using a First-In-First-Out (FIFO) queue.
- **Mechanism:** Explores all immediate neighbors at depth $k$ before moving to depth $k + 1$.
- **Relevance to Navigation:** Finds the path with the **minimum number of edges / step turns**, which is ideal for visitors who prefer simpler routes with fewer turns over slightly shorter physical distances.
- **Time Complexity:** $O(|V| + |E|)$.
- **Space Complexity:** $O(|V|)$ for visited set and predecessor queue.

### 12. Wheelchair-Accessible Routing Logic
Wheelchair-accessible routing applies a strict subgraph filter prior to shortest-path search:
1. **Edge Filtering:** The graph view excludes any edge where `wheelchair_accessible == False` or `has_stairs == True` or `status != 'open'`.
2. **Staircase Elimination:** All 18 vertical staircase edges are removed from the searchable graph.
3. **Elevator & Ramp Prioritization:** Routes are constrained to traverse the central elevator core or ADA-compliant ramps (slope $\le 1:12$).
4. **Graceful Fallback:** If vertical elevator connections are disabled or blocked, the engine returns `NoPathFoundError` rather than suggesting stairs.

### 13. Multi-Floor Navigation
Pedestrian routing seamlessly crosses floor boundaries:
- Intra-floor edges connect rooms to floor circulation hubs (concourse, elevator lobby, stairwell doors).
- Inter-floor vertical edges connect identical vertical shafts between adjacent levels (e.g., `FET_0F_ELEVATOR` to `FET_1F_ELEVATOR`).
- Multi-floor journeys aggregate horizontal distance and vertical transit time (modeled as 15 seconds per elevator floor change and 25 seconds per staircase flight).

### 14. 3D Digital Twin Architecture
- **Three.js Canvas:** Renders a 3D perspective scene with ambient light, directional sunlight casting real-time soft shadows, and ground plane fog.
- **Procedural Room Generation:** Computes 3D room geometries, interior walls (1.8m height), and procedural furniture (workstations, monitors, server racks with flashing LEDs).
- **Exploded View Transformation:** In Exploded View, floor $k$ is translated along the $Y$-axis by offset:
  $$Y_{\text{exploded}}(k) = Y_{\text{base}}(k) + k \times \Delta_{\text{separation}}$$
  Emerald alignment guide rods visually anchor the vertical relationship between floor slabs.

### 15. Obstacle Reporting & Route Recalculation
- **Lifecycle:** `Pending` $\to$ `Verified` $\to$ `Resolved` (or `Rejected`).
- **Safety Rule:** Community reports start as `Pending` and do **not** block pathways immediately. Only authenticated Field Staff or Administrators can transition a report to `Verified`.
- **Dynamic In-Memory Blocking:** Once verified, `ObstacleManager` sets the edge's operational status to `'blocked'` in the NetworkX graph and records the original state.
- **Automatic Rerouting:** Active navigation sessions detecting a verified hazard along their forward path automatically invoke `RouteFinder` to compute a detour around the blocked edge.

### 16. Authentication & RBAC
- **Student / Visitor:** Route planning, 3D exploration, room bookmarking, field hazard reporting, and feedback submission.
- **Field Staff:** Access to the verification queue, power to verify hazards (auto-block pathways), and resolve hazards with mandatory resolution notes.
- **Administrator:** Complete user directory control, role assignment, data verification tier management, and access to the immutable audit trail.
- **Sole Admin Protection:** Business logic prevents the last remaining administrator from demoting themselves or deactivating their own account.

### 17. Password Hashing & Security Hardening
- **Cryptographic Hash:** Salted PBKDF2-HMAC-SHA256 with a unique 32-byte cryptographic salt (`secrets.token_bytes(32)`) and **600,000 iterations** (exceeding OWASP 2026 guidelines).
- **Legacy Migration:** Accounts with legacy 100,000 iteration hashes are transparently upgraded to 600,000 iterations upon successful login.
- **Brute-Force Lockout:** Tracks failed attempts; locks the account for 15 minutes after 5 consecutive failures.
- **SQL Injection Defense:** All SQLite queries use parameterized placeholders (`?`). No SQL strings are concatenated.
- **Log Privacy:** Structured logging incorporates `SensitiveDataFilter` to redact passwords, salts, tokens, and hashes from console and file logs.

### 18. Campus Analytics & Intelligence
- **Dual-Dataset Analysis:** Distinguishes between the full 79-location JAIN Digital Twin and the canonical 15-location Schematic Benchmark.
- **Interactive Visualizations:** 4 Plotly charts:
  1. Pathway Accessibility Classification (Donut chart)
  2. Obstacle Lifecycle Status Distribution (Bar chart)
  3. Floor-by-Floor Hazard Distribution (Stacked chart)
  4. Frequently Blocked Pathways & Resolution Turnaround (Horizontal bar chart)
- **Administrative Telemetry:** Displays step-free ratio (83.0%), total pathways (106), active obstacles, and average resolution time.

### 19. Internationalization & Accessibility Standards
- **Languages:** English (`en`), Kannada (`kn`), and Hindi (`hi`). Natural-language instructions are translated dynamically.
- **High-Contrast Mode:** Injects WCAG AAA compliant CSS (deep black `#000000`, vibrant yellow `#FFD700`, crisp borders) for visually impaired users.
- **Reduced-Motion Mode:** Disables CSS transitions, transforms, and WebGL animations for users with vestibular disorders.

### 20. Docker & Deployment Architecture
- **Base Image:** `python:3.11-slim` multi-stage build.
- **Non-Root Execution:** Runs under dedicated system user `appuser` (UID 10001) and group `appgroup`.
- **Persistent Storage:** Docker Compose maps host volumes `./data`, `./database`, `./backups`, and `./logs`.
- **Nginx Reverse Proxy:** Manages WebSocket streaming (`/_stcore/stream`), buffers request bodies (25MB), and enforces security headers (X-Frame-Options, CSP, X-Content-Type-Options).

### 21. Testing Strategy & Actual Results
- **Framework:** Python standard library `unittest`.
- **Current Baseline:** **190 tests passed in 47.0s (0 failures, 0 errors, 0 skipped)** across 20 test modules.
- **Test Categories:** Graph connectivity, multi-floor routing, wheelchair invariant proofs, database migrations, RBAC boundaries, brute-force rate-limiting, and container deployment specifications.

### 22. System Limitations
1. **Schematic Spatial Coordinates:** 2D/3D coordinates are illustrative layout values derived from architectural floor plans rather than geodetic centimeter-accurate GPS/RTK surveys.
2. **Continuous Scoring Heuristic:** The 0–100 accessibility score is an algorithmic heuristic for route optimization, not an official statutory ADA or ISO building certification.
3. **Simulated Real-Time Navigation:** Avatar traversal simulates movement based on constant walking speed; it does not interface with physical indoor Bluetooth beacons or UWB positioning hardware.
4. **Single Campus Model:** Tailored to JAIN Global Campus and FET; multi-campus switching requires importing additional GeoJSON schemas.

### 23. Future Enhancements
1. **Physical Positioning Integration:** Interface with Wi-Fi RTT (Round Trip Time) or BLE beacon trilateration for live blue-dot user tracking.
2. **Audio Turn-by-Turn Screen Reader:** Full Web Speech API synthesis for voice-guided navigation for blind pedestrians.
3. **Automated CAD Ingestion:** Automated parser to extract graph topology directly from architectural Revit or IFC BIM models.
4. **IoT Sensor Integration:** Real-time elevator telemetry directly reporting maintenance outages into SQLite via MQTT.

### 24. Conclusion
The Accessible Campus Navigator successfully demonstrates how graph theory, 3D computer graphics, cybersecurity, and universal design principles can be unified into an accessible, practical, and deployment-ready software platform.

---

# PART 2 — 40+ COMPREHENSIVE VIVA QUESTIONS & ANSWERS

### Section A: Python & Web Framework Architecture

#### Q1: Why did you choose Streamlit over frameworks like Django or React/FastAPI?
**Answer:** Streamlit enables rapid, pure-Python development with reactive state management, making it ideal for data-intensive applications. By integrating Three.js through HTML/iframe components and persisting singletons in `st.session_state`, we achieved high-performance 3D rendering and reactive routing without the overhead of maintaining a separate JavaScript front-end build pipeline.

#### Q2: How does Streamlit handle state across page reloads, and how did you prevent graph re-instantiation?
**Answer:** Streamlit re-executes the Python script from top to bottom on user interaction. To prevent reloading the heavy 79-node campus graph on every click, we implemented `get_app_services()` in `modules/ui_theme.py`, which caches `CampusMap`, `DatabaseManager`, `ObstacleManager`, and `RouteFinder` in `st.session_state` as shared singletons.

#### Q3: What is the purpose of `.streamlit/config.toml`?
**Answer:** It configures the Streamlit server daemon: sets the listening port to `8501`, disables telemetry tracking (`gatherUsageStats = false`), enforces headless execution (`headless = true`), and configures the default dark-forest-green theme palette (`primaryColor = "#16A36A"`, `backgroundColor = "#07130F"`).

---

### Section B: Graph Theory & Data Structures

#### Q4: How is the campus represented mathematically in your codebase?
**Answer:** As an undirected weighted graph $G = (V, E)$ using NetworkX. $V$ contains 79 nodes with attributes `(id, name, floor, building, category, x, y)`. $E$ contains 106 edges with attributes `(distance, estimated_time, wheelchair_accessible, has_stairs, has_ramp, has_elevator, status)`.

#### Q5: What is the difference between a directed and an undirected graph in the context of campus navigation?
**Answer:** An undirected graph allows bidirectional travel along corridors ($u \to v$ and $v \to u$ have identical weights). In our system, corridors and elevators are bidirectional. However, for specialized turnstiles or one-way emergency fire escape doors, directed edges ($u \to v$ only) would be used.

#### Q6: How do you represent edge weights, and why do you offer dual optimization (Distance vs. Time)?
**Answer:** Edges have two distinct weight attributes: `distance` (Euclidean/corridor meters) and `estimated_time` (seconds, assuming $1.2\text{ m/s}$ walking speed plus vertical penalties). Distance optimization minimizes physical meters walked; time optimization minimizes transit duration, prioritizing elevators over longer walking detours.

#### Q7: What data structure does Dijkstra's algorithm use to achieve efficient performance?
**Answer:** A binary min-heap (implemented via Python's `heapq`). The priority queue stores tuples of `(tentative_distance, node_id)`. Extracting the minimum distance node takes $O(\log |V|)$ time, yielding an overall complexity of $O((|V| + |E|) \log |V|)$.

#### Q8: Under what condition would Dijkstra's algorithm fail?
**Answer:** Dijkstra fails if the graph contains negative edge weights, because once a node is marked visited, Dijkstra assumes its shortest distance is finalized. In pedestrian physical navigation, distances and times are strictly positive ($w(e) > 0$), so Dijkstra is mathematically guaranteed to find the optimal shortest path.

#### Q9: Compare Dijkstra's algorithm with Breadth-First Search (BFS). When would a student prefer BFS over Dijkstra?
**Answer:** Dijkstra finds the path with the minimum sum of edge weights (distance). BFS finds the path with the minimum number of edges (hops/turns). A student carrying heavy project equipment might prefer a BFS route with only 2 long straight corridors over a Dijkstra route that turns through 5 zigzag hallways to save 8 meters.

---

### Section C: Accessibility & Multi-Floor Routing

#### Q10: How does the system guarantee that a wheelchair user will never be guided to a staircase?
**Answer:** In `RouteFinder.find_route()`, when `wheelchair_accessible=True`, the algorithm generates a filtered graph view:
```python
valid_edges = [
    (u, v) for u, v, d in graph.edges(data=True)
    if d.get("wheelchair_accessible", True) 
    and not d.get("has_stairs", False) 
    and d.get("status") == "open"
]
```
All 18 staircase edges are strictly stripped from the searchable graph before the pathfinding algorithm runs.

#### Q11: How is the central elevator modeled across all 5 floors?
**Answer:** Each floor has an elevator landing node (`FET_0F_ELEVATOR` through `FET_4F_ELEVATOR`). Adjacent floors are linked by vertical edges (`CONN_VERT_ELEV_L0_L1`, etc.) with `has_elevator = True`, `wheelchair_accessible = True`, and `has_stairs = False`. Planar coordinates $(X, Y) = (-6.0, 18.0)$ are invariant across all 5 tiers.

#### Q12: How are turn-by-turn navigation instructions generated?
**Answer:** In `modules/navigation_instructions.py`, for every three consecutive nodes $(A, B, C)$, we compute the 2D vectors $\vec{u} = B - A$ and $\vec{v} = C - B$. We evaluate the 2D cross-product $\vec{u} \times \vec{v} = u_x v_z - u_z v_x$ and dot-product $\vec{u} \cdot \vec{v}$. The sign and magnitude determine whether the turn is slight left, sharp left, slight right, sharp right, or straight.

#### Q13: What is the 0–100 accessibility scoring formula?
**Answer:** Evaluated by `AccessibilityEngine`:
$$\text{Score} = 100 - (\text{Staircase Penalty} \times 40) - (\text{Slope Penalty}) - (\text{Obstacle Penalty} \times 100)$$
A clean, step-free path with automatic doors scores 100 (*Fully Accessible*). A path with steep ramps scores 70 (*Accessible with Assistance*). A path requiring stairs scores 0 for wheelchairs (*Not Wheelchair Accessible*).

---

### Section D: Obstacle Management & Dynamic Rerouting

#### Q14: What is the lifecycle of an obstacle report in the database?
**Answer:** An obstacle begins in the `Pending` state upon user submission. An authenticated Field Staff or Administrator inspects the report and transitions it to `Verified` (which dynamically blocks the pathway) or `Rejected`. Once physical maintenance is completed, staff transitions it to `Resolved` with mandatory resolution notes, restoring the pathway.

#### Q15: Why don't pending obstacle reports immediately block pathways in the graph?
**Answer:** To prevent Denial-of-Service (DoS) attacks or malicious false reports by unverified users that could disrupt campus operations. Only verified reports by authorized staff can alter routing topology.

#### Q16: How does the system handle concurrent obstacles on the same pathway?
**Answer:** If multiple reports affect the same edge $(u, v)$, `ObstacleManager` tracks an active count. Resolving one report decrements the active count; the edge is only restored to `open` when all verified reports on that edge are resolved (`active_count == 0`).

#### Q17: How is dynamic in-transit rerouting implemented?
**Answer:** During real-time navigation simulation (`NavigationSession`), before advancing to the next waypoint, the system checks whether any upcoming edge in the planned route is in `obstacle_manager.get_active_blocked_edges()`. If an edge is blocked, the session transitions to `REROUTING` and recalculates an alternative detour from the user's current node to the destination.

---

### Section E: Database Systems & Persistence

#### Q18: What is SQLite WAL mode, and why did you enable it?
**Answer:** Write-Ahead Logging (WAL) writes changes to a separate `-wal` file before committing them to the database. It allows concurrent readers to read without blocking writers, and writers to commit without blocking readers, significantly improving concurrency and eliminating `database locked` errors.

#### Q19: How do you prevent data loss during deployment or server restarts?
**Answer:** 
1. Database file `campus.db` is stored on a persistent host volume mounted inside the Docker container (`./database:/app/database`).
2. Deployment scripts (`deploy.sh`, `deploy.ps1`) trigger an automated point-in-time snapshot backup to `backups/campus_backup_YYYYMMDD_HHMMSS.db` prior to container recreation.

#### Q20: How did you implement database schema migrations?
**Answer:** We utilize SQLite's `PRAGMA user_version`. On startup, `db_manager.py` checks `user_version`. If the version is less than 3, it executes non-destructive `ALTER TABLE` and `CREATE TABLE IF NOT EXISTS` statements and updates `PRAGMA user_version = 3`.

#### Q21: What is the purpose of `database/postgres_migration.py`?
**Answer:** It provides an enterprise migration pipeline. It generates PostgreSQL-compatible DDL schemas (translating SQLite types to `UUID`, `VARCHAR`, `TIMESTAMPTZ`, and `BOOLEAN`) and exports all SQLite table data as clean JSON/CSV dumps for ingestion into managed Cloud SQL or PostgreSQL instances.

---

### Section F: Cybersecurity & Cryptography

#### Q22: How are user passwords stored in your database?
**Answer:** Passwords are never stored in plaintext. They are hashed using PBKDF2 (Password-Based Key Derivation Function 2) with HMAC-SHA256, a cryptographically secure 32-byte salt (`secrets.token_bytes(32)`), and **600,000 iterations**, complying with OWASP recommendations.

#### Q23: How do you defend against brute-force password guessing?
**Answer:** `DatabaseManager` tracks `failed_login_attempts` in the `users` table. If 5 consecutive failed attempts occur, the account's `lockout_until` timestamp is set to 15 minutes in the future, and subsequent login attempts immediately raise `SecurityLockoutError`.

#### Q24: How do you defend against SQL Injection?
**Answer:** All SQL queries throughout `db_manager.py` utilize parameterized queries with `?` placeholders (e.g., `cursor.execute("SELECT * FROM users WHERE username = ?", (username,))`). User input is never concatenated or formatted directly into SQL query strings.

#### Q25: How do you prevent privilege escalation in Role-Based Access Control?
**Answer:** RBAC checks are enforced at the backend service layer in `db_manager.py`, not just in the UI. For instance, `update_user_role` requires passing `actor_user`. If `actor_user.get("role") != "Administrator"`, the method raises `PermissionError`, even if an attacker attempts to spoof the HTTP request.

#### Q26: What is sole-admin demotion prevention?
**Answer:** If an administrator attempts to change their role to `Student` or deactivate their account, `db_manager.py` queries `SELECT COUNT(*) FROM users WHERE role = 'Administrator' AND status = 'active'`. If the count is 1, it aborts the operation and raises `ValueError`, preventing the system from becoming orphaned without an admin.

#### Q27: How do you ensure sensitive data is not leaked into log files?
**Answer:** In `modules/logging_config.py`, we implemented `SensitiveDataFilter(logging.Filter)`. It intercepts log records and applies regex patterns to redact passwords, salts, API tokens, and 64-character hashes before writing to disk.

---

### Section G: 3D Graphics & Three.js WebGL

#### Q28: How does Three.js render the 3D campus inside a Streamlit web app?
**Answer:** Streamlit serves a responsive HTML iframe embedding Three.js (r128). The Python backend serializes campus nodes, pathways, and active routes into a JSON payload injected into the JavaScript template. Three.js instantiates geometries (`BoxGeometry`, `CylinderGeometry`), materials (`MeshStandardMaterial`), and attaches them to the scene graph.

#### Q29: What is an Exploded View, and how is it calculated in 3D space?
**Answer:** An exploded view separates overlapping architectural layers to reveal interior layout. For each floor $k \in \{0, 1, 2, 3, 4\}$, the mesh group's vertical position is set to $Y_k = Y_{\text{normal}} + (k \times 16.0\text{ meters})$. Emerald vertical guide rods visually link the levels.

#### Q30: How do you optimize 3D rendering performance for low-end mobile devices?
**Answer:**
1. **Low-Polygon Geometry:** Using minimal subdivision segments on cylinders and boxes.
2. **Material Reuse:** Sharing common materials across instanced elements.
3. **Selective Rendering:** Rendering trees and decorative bollards only in Outdoor view.
4. **Antialiasing Control:** Providing reduced-motion and lower shadow map resolution options.

---

### Section H: Internationalization & Inclusive UX

#### Q31: How is multilingual localization implemented?
**Answer:** Through `modules/i18n.py`. It maintains complete translation dictionaries for English (`en`), Kannada (`kn`), and Hindi (`hi`). The helper function `t(key, lang)` looks up localized text, while `translate_instruction(step, lang)` dynamically parses and translates navigation turn instructions into localized natural language.

#### Q32: What accessibility features are implemented for visually impaired users?
**Answer:** 
1. **WCAG AAA High-Contrast Mode:** Injects high-contrast CSS (pure black background, high-contrast gold/green borders, 7:1 minimum contrast ratio).
2. **Large Typography & Badges:** Clear status indicators with text labels rather than color-only signifiers.
3. **Screen Reader Accessible Tables:** Tabular representation of routes and directions.

---

### Section I: DevOps, Docker & Release Engineering

#### Q33: Why did you use a non-root user inside the Docker container?
**Answer:** Running containers as `root` is a major security vulnerability; if an attacker executes remote code, they gain root privileges on the host system. In our `Dockerfile`, we create `appuser:appgroup` (UID 10001) and switch to `USER appuser`, ensuring the principle of least privilege.

#### Q34: Why is an Nginx reverse proxy necessary in front of Streamlit?
**Answer:** Streamlit uses bidirectional WebSockets (`/_stcore/stream`) for real-time UI synchronization. Nginx terminates client HTTP/HTTPS connections, upgrades WebSocket connections (`proxy_set_header Upgrade $http_upgrade;`), manages large client upload limits (25MB), and enforces security headers (HSTS, CSP, X-Frame-Options).

#### Q35: What does the Docker container healthcheck verify?
**Answer:** It periodically executes an internal Python command:
```dockerfile
HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1
```
This probes Streamlit's internal health endpoint. If the server crashes or hangs, Docker automatically flags the container as `unhealthy` and restarts it.

---

### Section J: Software Testing & Quality Assurance

#### Q36: What is the current test baseline of the project?
**Answer:** **190 automated unit, integration, and security tests** across 20 test files, executing in **47.011 seconds with 0 failures, 0 errors, and 0 skipped tests**.

#### Q37: What is the difference between unit testing, integration testing, and regression testing in your project?
**Answer:**
- **Unit Testing:** Tests individual functions in isolation (e.g., verifying `dijkstra_shortest_path` returns correct distance on a 3-node mock graph).
- **Integration Testing:** Tests interactions between multiple components (e.g., verifying that a verified obstacle in `ObstacleManager` alters the path returned by `RouteFinder`).
- **Regression Testing:** Running all 190 tests across the entire codebase after any code modification to prove that new features did not break existing functionality.

#### Q38: Why didn't you claim 100% code coverage?
**Answer:** In academic and industrial engineering, test pass rate ($100\%$, 190/190) must never be conflated with code coverage (line/branch coverage). Standard Python in our production container does not include unpinned third-party coverage tools. We strictly report verifiable facts rather than fabricating unmeasured coverage statistics.

#### Q39: How did you test SQL injection resistance?
**Answer:** In `tests/test_phase20_security_and_qa.py`, we execute test cases passing malicious SQL payloads:
```python
malicious_payload = "admin' OR '1'='1' --"
res = db.authenticate_user(malicious_payload, "password")
self.assertIsNone(res)
```
This verifies that malicious SQL payloads fail authentication rather than bypassing credentials.

#### Q40: What was the most challenging technical bug you encountered and resolved during development?
**Answer:** The vertical shaft planar alignment invariant. Early schematic drafts placed floor landings with slight coordinate variations between levels ($X = -6.0$ on Ground, $X = -5.8$ on Floor 1). This caused the 3D elevator shaft to render sheared at an angle. We performed a complete geometric audit in Phase 16, standardizing the shaft to $(X, Y) = (-6.0, 18.0)$ across all 5 tiers and creating automated mathematical tests to guarantee zero shear.
