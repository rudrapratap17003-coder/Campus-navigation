# FINAL 100+ TECHNICAL VIVA QUESTIONS AND ANSWERS

**Project:** Accessible Campus Navigator — JAIN Global Campus  
**Presenter:** Rudra Pratap (USN: `25BTRCL214`)  
**Department:** Artificial Intelligence and Machine Learning  
**Institution:** JAIN (Deemed-to-be University) — Faculty of Engineering and Technology (FET)  
**Total Questions Prepared:** 120 Comprehensive Questions & Verified Answers  

---

## CATEGORY A: PROJECT FUNDAMENTALS (Q1 – Q10)

### Q1: What is the Accessible Campus Navigator?
**Answer:** Accessible Campus Navigator is a web-based spatial wayfinding and digital twin platform designed for JAIN Global Campus and its Faculty of Engineering and Technology (FET). It combines graph-theoretic pathfinding, wheelchair-accessible constraint routing, multi-storey indoor navigation, crowdsourced dynamic obstacle management, and an interactive 3D WebGL digital twin.

### Q2: What exact problem does this project address?
**Answer:** Large university campuses pose severe navigation hurdles: commercial GPS systems stop at the building perimeter, providing no indoor room guidance; multi-storey buildings disorient freshmen and visitors; students with physical disabilities or injuries face sudden staircase dead-ends; and temporary campus maintenance hazards (e.g., broken elevators, wet floors) are not reflected in static paper maps.

### Q3: Why was JAIN Global Campus chosen as the target environment?
**Answer:** JAIN Global Campus features both extensive outdoor terrain and the multi-storey FET engineering building with over 45 specialized laboratories, lecture halls, and administrative wings. It provides a real-world testing ground for integrating outdoor walkways with multi-floor vertical transitions.

### Q4: Who are the primary stakeholders and end users?
**Answer:** 
1. **Students & Visitors:** Seek efficient turn-by-turn guidance to classrooms, labs, and amenities.
2. **Mobility-Impaired Students:** Require guaranteed step-free paths utilizing elevators and ramps.
3. **Field & Facility Staff:** Need to verify on-ground obstacles, review hazard reports, and resolve campus barriers.
4. **Campus Administrators:** Require spatial analytics, user governance, and infrastructure audit trails.

### Q5: What makes this project an engineering project rather than just a UI website?
**Answer:** The project implements deterministic graph algorithms (Dijkstra and BFS) on mathematical graphs, dynamic subgraph pruning for accessibility constraints, real-time edge invalidation via SQLite triggers and state management, and custom WebGL shaders/orbit controls in Three.js, backed by 208 automated unit and regression tests.

### Q6: What are the primary objectives achieved in this project?
**Answer:** Unified campus mapping across 79 nodes and 106 edges, comparative routing between Dijkstra and BFS, automated step-free wheelchair routing, multi-floor FET indoor navigation, dynamic obstacle lifecycles, and a responsive 3D digital twin.

### Q7: Does the system guarantee 100% accessible routes in the real world?
**Answer:** No. We explicitly disclose that accessibility ratings are heuristic calculations based on mapped attributes (doorway width, ramp gradient, surface smoothness). Physical conditions on campus may vary dynamically; therefore, heuristic scores provide guidance, but physical confirmation is always recommended.

### Q8: What dataset sizes are currently supported?
**Answer:** The primary dataset covers JAIN Global Campus with 79 nodes, 106 pathways, and 5 building floors. The system also supports a 15-node, 17-edge Schematic Benchmark model for algorithmic validation and unit testing.

### Q9: How does the application handle localization and language accessibility?
**Answer:** The system includes a built-in multilingual engine (`modules/translations.py`) supporting English, Kannada (ಕನ್ನಡ), and Hindi (हिन्दी), allowing users to switch languages seamlessly across all operational pages.

### Q10: What is the current release version of the application?
**Answer:** Release version `v1.0.0`, verified with 208 automated tests, containerized with Docker, and synchronized on GitHub.

---

## CATEGORY B: PYTHON & APPLICATION ARCHITECTURE (Q11 – Q20)

### Q11: Why was Python selected as the primary programming language?
**Answer:** Python offers a rich scientific and algorithmic ecosystem (`NetworkX`, `Pandas`), built-in relational database libraries (`sqlite3`), enterprise security tooling (`hashlib`), and seamless integration with web frameworks like Streamlit.

### Q12: Why was Streamlit chosen over React or Angular?
**Answer:** Streamlit provides a stateful, reactive Python-native UI without frontend-backend serialization overhead. It enables rapid prototyping, direct binding to in-memory graph objects, and built-in support for interactive visualization libraries like Plotly and Folium.

### Q13: How is the software architecture structured?
**Answer:** It follows a 4-tier layered architecture:
1. **Presentation Layer:** Streamlit pages (`pages/`) with custom CSS themes (`modules/ui_theme.py`).
2. **Service Layer:** Singletons managing routing, accessibility heuristics, obstacle state, and analytics.
3. **Core Engine Layer:** `NetworkX` graph traversal and `Three.js` 3D scene construction.
4. **Data Persistence Layer:** SQLite relational database in WAL mode and JSON campus datasets.

### Q14: How does shared session state work across multiple Streamlit pages?
**Answer:** Via `st.session_state` and the singleton helper `get_app_services()` in `modules/ui_theme.py`. When an obstacle is verified on one page, the underlying `campus_map` object is mutated in session memory, ensuring all other pages instantly reflect the blocked edge without re-instantiation.

### Q15: What is the role of `main.py`?
**Answer:** `main.py` serves as the centralized entry point and multi-page router. It initializes global theme styles, authenticates the user, checks roles, dynamically constructs the navigation menu using `st.navigation`, and runs the selected page.

### Q16: How are environment configurations and secrets managed?
**Answer:** Through `config.py` using `get_secret(key, default)`. It prioritizes `st.secrets` (Streamlit Cloud), falls back to `os.environ` (Docker/VPS), and defaults to safe local development values.

### Q17: What design patterns are implemented in the codebase?
**Answer:**
- **Singleton Pattern:** Shared application service instances (`get_app_services()`).
- **Strategy Pattern:** Interchangeable routing algorithms (`DijkstraStrategy`, `BFSStrategy`).
- **State Machine Pattern:** Obstacle lifecycle (`Pending` → `Verified` → `Resolved`/`Rejected`).
- **Data Access Object (DAO):** `DatabaseManager` encapsulating raw SQL execution.

### Q18: What is Write-Ahead Logging (WAL) mode in SQLite?
**Answer:** In WAL mode, changes are written to a separate `.wal` file rather than directly overwriting the main database. This allows concurrent readers to access the database without being blocked by active write operations, drastically reducing database lock contention.

### Q19: How are circular imports avoided in Python modules?
**Answer:** By using `from __future__ import annotations`, type hinting with strings (`'CampusMap'`), and performing localized imports inside helper functions when runtime coupling exists.

### Q20: What happens if an unhandled exception occurs in a service?
**Answer:** Services wrap operations in structured `try...except` blocks, logging errors to `logs/campus_navigator.log` and surfacing user-friendly UI warnings (`st.error`) rather than exposing raw stack traces.

---

## CATEGORY C: DATA STRUCTURES & ALGORITHMS (Q21 – Q35)

### Q21: What mathematical structure represents the campus?
**Answer:** An undirected, weighted graph $G = (V, E)$, where $V$ is the set of physical campus landmarks and $E$ is the set of walkable pathway connections.

### Q22: What data structure does NetworkX use internally to store graphs?
**Answer:** NetworkX uses a dictionary of dictionaries of dictionaries (`dict-of-dicts-of-dicts`) representing an adjacency list. This provides $O(1)$ edge existence lookups and $O(1)$ neighbor iteration per vertex.

### Q23: How does Breadth-First Search (BFS) work in your application?
**Answer:** BFS traverses the unweighted campus graph level by level using a First-In, First-Out (FIFO) queue. Starting at the source node, it explores all direct neighbors before visiting second-degree neighbors. It guarantees the path with the minimum number of edge transitions.

### Q24: What is the time and space complexity of BFS?
**Answer:**
- **Time Complexity:** $O(V + E)$, where $V$ is the number of vertices and $E$ is the number of edges.
- **Space Complexity:** $O(V)$ for the visited set and FIFO queue.

### Q25: How does Dijkstra's Algorithm work in your application?
**Answer:** Dijkstra's algorithm finds the minimum-cost path on a weighted graph with non-negative edge weights. It maintains a min-priority queue (min-heap) of tentative distances. At each step, it extracts the unvisited vertex with the smallest tentative distance, relaxes its outgoing edges, and updates neighbor distances.

### Q26: What is the time and space complexity of Dijkstra's Algorithm?
**Answer:**
- **Time Complexity:** $O((E + V) \log V)$ using a binary min-heap priority queue.
- **Space Complexity:** $O(V)$ for distance arrays, priority queue, and predecessor maps.

### Q27: Why does BFS fail to find the shortest physical distance on a weighted graph?
**Answer:** BFS treats all edges as having an identical unit cost ($w=1$). If Path A has 2 long edges (each 200m, total 400m) and Path B has 3 short edges (each 50m, total 150m), BFS will choose Path A because it has fewer edge hops (2 vs 3), even though it is physically 250 meters longer.

### Q28: How do you mathematically define edge weight $w(u, v)$?
**Answer:**
$$w(u, v) = \text{distance\_meters} \times \left(1 + \frac{\text{incline\_pct}}{100}\right) + \text{surface\_penalty}$$
where surface penalties account for unpaved gravel or high-friction terrain.

### Q29: Can Dijkstra's algorithm handle negative edge weights?
**Answer:** No. Dijkstra assumes that adding an edge to a path never decreases its total cost (greedy monotonicity). If negative edge weights were present, the Bellman-Ford algorithm ($O(V \cdot E)$) would be required. Since physical distances and inclines are strictly non-negative, Dijkstra is mathematically optimal.

### Q30: What is path relaxation?
**Answer:** Given an edge $(u, v)$ with weight $w(u, v)$, relaxation checks whether the path to $v$ through $u$ is shorter than the currently recorded distance $dist[v]$:
$$\text{if } dist[u] + w(u, v) < dist[v] \implies dist[v] = dist[u] + w(u, v); \quad pred[v] = u$$

### Q31: How is the final path reconstructed from Dijkstra or BFS?
**Answer:** Starting from the destination vertex $v_{dest}$, the algorithm traces backwards through the predecessor dictionary $pred[v]$ until reaching the source vertex $v_{src}$. The resulting list is reversed to yield the forward path.

### Q32: What happens if there is no path between two selected nodes?
**Answer:** If the destination is unreachable (e.g., in a disconnected component or after obstacle severance), the priority queue empties without reaching the destination. The function catches this state and returns `None`, prompting the UI to display a clear "No route available" message.

### Q33: How do you prevent graph traversal cycles?
**Answer:** In BFS, a `visited` set tracks processed vertices; in Dijkstra, vertices extracted from the priority queue have their shortest distances finalized and are marked as settled.

### Q34: What is the difference between an adjacency matrix and an adjacency list?
**Answer:** An adjacency matrix is a $|V| \times |V|$ 2D array requiring $O(V^2)$ space, inefficient for sparse graphs like campus networks ($V=79, E=106$). An adjacency list requires $O(V + E)$ space and allows iterating only over existing neighbors.

### Q35: Could A* search be used instead of Dijkstra?
**Answer:** Yes. A* uses a heuristic $f(n) = g(n) + h(n)$, where $h(n)$ is Euclidean distance to the goal. For our 79-node campus graph, Dijkstra executes in under 2 milliseconds, making the optimization difference negligible; however, A* would be advantageous if scaling to thousands of city-wide street nodes.

---

## CATEGORY D: ACCESSIBILITY (Q36 – Q48)

### Q36: How does wheelchair-accessible routing work algorithmically?
**Answer:** When wheelchair mode is enabled, the accessibility engine creates a temporary subgraph:
$$G' = (V, E \setminus E_{\text{stairs}})$$
Edges tagged with `edge_type == 'stairs'` or `has_stairs == True` are eliminated before invoking Dijkstra's algorithm.

### Q37: How are elevators represented in the graph?
**Answer:** An elevator is modeled as a set of vertical edges connecting co-located nodes across different floors (e.g., `FET_Elevator_F0` to `FET_Elevator_F1`, `F2`, `F3`, `F4`). These edges are tagged with `is_step_free = True` and assigned a travel weight reflecting elevator transit and door-wait time (~15 seconds).

### Q38: How are ramps evaluated?
**Answer:** Ramps are mapped with their measured gradient. According to accessibility standards (ADA / CPWD), ramps with gradients $\le 1:12$ (approx 8.33%) are classified as fully independent step-free pathways. Steeper ramps are tagged as requiring assistance.

### Q39: What formula calculates the 0–100 Route Accessibility Score?
**Answer:**
$$\text{Score} = 100 - (\text{penalty}_{\text{stairs}} + \text{penalty}_{\text{gradient}} + \text{penalty}_{\text{width}} + \text{penalty}_{\text{surface}})$$
If any step contains an unresolved flight of stairs, the score is capped at a maximum of 20/100.

### Q40: What happens if all elevators in a building are marked as blocked?
**Answer:** If all vertical elevator edges are severed by verified obstacle reports, the wheelchair routing engine correctly determines that no step-free cross-floor path exists. It notifies the user that upper floors are temporarily inaccessible and suggests contacting campus support.

### Q41: What is heuristic accessibility scoring?
**Answer:** Heuristic scoring uses rule-based mathematical approximations derived from known attributes rather than live sensor readings. For instance, assuming a 120cm corridor width provides high accessibility is a heuristic rule based on standard wheelchair dimensions (75cm width requirement).

### Q42: How does the system handle doorway clearance widths?
**Answer:** Node and pathway records include a `clearance_width_cm` attribute. Pathways narrower than 90cm trigger an accessibility warning for standard motorized wheelchairs.

### Q43: What UI features support visually impaired or low-vision users?
**Answer:** High-contrast color palette (`#07130F` dark green background with `#35D99A` accent text), WCAG 2.1 AA compliant contrast ratios (> 4.5:1), responsive font scaling, and semantic HTML elements compatible with screen readers.

### Q44: What is the "Reduced Motion" accessibility toggle?
**Answer:** It disables dynamic camera fly-through animations and spinning 3D scene rotations in the Three.js viewport, accommodating users prone to vestibular motion sickness.

### Q45: How does the system guide a user through vertical transitions?
**Answer:** Turn-by-turn guidance explicitly generates elevation instructions: "Board North Passenger Elevator on Ground Floor. Ascend to Floor 2. Exit toward Computer Science Wing."

### Q46: Can standard non-disabled users still use stairs?
**Answer:** Yes. When "Wheelchair Accessible Only" is unchecked, Dijkstra calculates the shortest path regardless of edge type, frequently utilizing central staircases if they offer a shorter physical route.

### Q47: What happens if an obstacle blocks an accessible ramp?
**Answer:** Once the obstacle report is verified, the ramp edge is severed. If an alternative accessible route (e.g., an alternate ramp or building elevator) exists, the algorithm routes through it; otherwise, it reports the destination as step-free unreachable.

### Q48: Are outdoor terrain surfaces considered in accessibility?
**Answer:** Yes. Pathways mapped across unpaved lawns or rough gravel carry higher resistance multipliers ($1.5\times$), biasing the routing engine toward paved concrete footpaths.

---

## CATEGORY E: DATABASE (Q49 – Q60)

### Q49: Why was SQLite selected instead of MySQL or PostgreSQL?
**Answer:** SQLite is serverless, zero-configuration, and embedded directly into the application process. It eliminates network roundtrips, requires no external database service daemon, and stores all tables in a single file (`data/campus_navigation.db`), making it ideal for self-contained academic deployment.

### Q50: How is the database schema structured?
**Answer:** The relational schema contains four core tables:
1. `users`: Stores user credentials, roles, account status, and failed login counters.
2. `obstacle_reports`: Tracks obstacle targets, severities, verification statuses, and resolution notes.
3. `audit_logs`: Immutable security log of logins, role updates, and obstacle status changes.
4. `schema_version`: Tracks migration history (currently version 3).

### Q51: What is a primary key, and what primary keys are used?
**Answer:** A primary key is a column or set of columns uniquely identifying every row in a table. In `users`, `id` (INTEGER AUTOINCREMENT) is the PK; in `obstacle_reports`, `report_id` (INTEGER AUTOINCREMENT) is the PK.

### Q52: What is a foreign key, and where is it used?
**Answer:** A foreign key establishes a relationship between child and parent tables. In `obstacle_reports`, `reported_by_user_id` references `users(id)`, and `verified_by_user_id` references `users(id)`.

### Q53: How does the application enforce foreign key constraints in SQLite?
**Answer:** SQLite disables foreign keys by default. The `DatabaseManager` explicitly executes `PRAGMA foreign_keys = ON;` on every newly opened database connection.

### Q54: How does schema migration work across development phases?
**Answer:** When `DatabaseManager.initialize_schema()` runs, it queries `schema_version`. If the existing version is less than 3, it applies incremental `ALTER TABLE` statements (e.g., adding `account_status`, `failed_attempts`, `locked_until`) inside a transaction without wiping existing records.

### Q55: How does database backup work?
**Answer:** The `backup_database(destination_path)` method uses the native SQLite Online Backup API (`conn.backup(backup_conn)`). This copies the live database page-by-page while maintaining read-write transactions, preventing corruption.

### Q56: How is database restoration verified?
**Answer:** When `restore_database(backup_path)` is invoked, it first opens the candidate backup file, runs `PRAGMA integrity_check`, and only replaces the active database if the integrity check returns "ok".

### Q57: What is an immutable audit log?
**Answer:** An audit log where records can only be inserted, never updated or deleted (`INSERT-only`). This ensures that administrative actions, failed logins, and obstacle resolutions can never be tampered with or erased.

### Q58: Can the application be migrated to PostgreSQL?
**Answer:** Yes. In Phase 30, we authored `scripts/export_to_postgres.py` and validated PostgreSQL DDL. All SQLite queries adhere to standard ANSI SQL, allowing seamless porting to PostgreSQL.

### Q59: What is connection busy timeout?
**Answer:** In multi-threaded environments, if another thread is writing to the database, `PRAGMA busy_timeout = 5000;` tells SQLite to wait up to 5,000 milliseconds for the lock to clear before raising an `OperationalError`.

### Q60: How are database transactions handled?
**Answer:** Using Python's `with conn:` context manager. If all operations complete successfully, changes are automatically committed; if an exception is raised, the entire transaction is rolled back.

---

## CATEGORY F: INDOOR & OUTDOOR NAVIGATION (Q61 – Q72)

### Q61: How are outdoor and indoor spaces unified into one navigation model?
**Answer:** Outdoor pathways terminate at building entrance nodes (e.g., `FET_Main_Entrance`). These entrance nodes connect directly via indoor foyer edges to internal corridor nodes, creating a single continuous graph without architectural boundaries.

### Q62: How are individual building floors distinguished?
**Answer:** Every node possesses a `floor_id` attribute: `0` for Ground Floor, `1` for First Floor, `2` for Second Floor, `3` for Third Floor, and `4` for Fourth Floor. Outdoor nodes are assigned `floor_id = 0`.

### Q63: How does the 2D Campus Map display different floors?
**Answer:** In `pages/campus_map.py`, when a user selects a floor button (e.g., "Floor 2"), the plotting function filters the active node set to `node.floor_id == 2`, rendering only the classrooms, labs, and hallway connections of that specific level.

### Q64: What laboratories are mapped inside the FET Building?
**Answer:** Over 20 specialized labs, including:
- **Floor 0:** Mechanical Workshop, Fluid Mechanics Lab, Manufacturing Center.
- **Floor 1:** VLSI Design Lab, Digital Signal Processing Lab, Microcontroller Lab.
- **Floor 2:** Artificial Intelligence & Machine Learning Lab, High Performance Computing (HPC) Center, Robotics Research Lab.
- **Floor 3:** Geotechnical Engineering Lab, Structural Analysis Lab.
- **Floor 4:** Aerodynamics & Wind Tunnel Facility, Propulsion Systems Lab.

### Q65: How are vertical distances calculated in routing?
**Answer:** Moving between floors incurs a vertical distance penalty (typically 4 meters of vertical rise per floor) plus a transfer weight representing stair climbing effort or elevator wait time.

### Q66: What is the coordinate system used for nodes?
**Answer:** A normalized 2D Cartesian coordinate plane $(X, Y)$ where coordinates range from 0 to 1,000 meters across the campus bounding box, with an additional discrete $Z$ axis representing floor elevation ($Z = \text{floor\_id} \times 4.0\text{m}$).

### Q67: How does destination search autocomplete work?
**Answer:** The search input performs a case-insensitive substring match against node names, categories (e.g., "Laboratory", "Cafeteria"), and floor identifiers, returning matching destination options in real time.

### Q68: What is turn-by-turn guidance?
**Answer:** A chronological sequence of directional instructions generated by analyzing the vectors between consecutive path coordinates:
$$\theta = \text{atan2}(y_2 - y_1, x_2 - x_1)$$
Changes in angle determine "Turn left", "Turn right", "Continue straight", or "Board elevator".

### Q69: How are compass bearings calculated?
**Answer:** The direction vector between consecutive waypoints is mapped to standard 360-degree compass headings: North ($0^\circ$), East ($90^\circ$), South ($180^\circ$), and West ($270^\circ$).

### Q70: What happens if a user inputs the same node as origin and destination?
**Answer:** The routing engine detects that $v_{src} == v_{dest}$, returns a zero-length path, and informs the user: "You are already at your destination."

### Q71: How are outdoor landmarks represented?
**Answer:** Landmarks include the Main Entrance Gate, University Administrative Block, Central Library, Cricket Ground, Hostel Blocks A & B, and the Food Court.

### Q72: How are emergency exits mapped?
**Answer:** Primary and secondary emergency staircases on the East and West wings of the FET building are mapped with `is_emergency_exit = True`, allowing routing engines to prioritize them during evacuation mode.

---

## CATEGORY G: THREE.JS & VISUALIZATION (Q73 – Q84)

### Q73: Why was Three.js chosen for 3D visualization?
**Answer:** Three.js is the industry-standard JavaScript 3D library for WebGL. It runs natively in modern web browsers without plugins, provides camera controls (`OrbitControls`), and renders lighting, shadows, and materials at 60 FPS.

### Q74: What is WebGL?
**Answer:** WebGL (Web Graphics Library) is a JavaScript API for rendering interactive 2D and 3D graphics within any compatible web browser using hardware-accelerated GPU processing.

### Q75: How is the 3D scene built from Python data?
**Answer:** `modules/three_d_map.py` serializes campus node coordinates, pathway connections, and building footprints into a structured JSON payload, which is injected into a custom HTML/JavaScript template rendered via `streamlit.components.v1.html()`.

### Q76: What is procedural geometry generation?
**Answer:** Instead of loading a pre-modeled 100-megabyte 3D asset file, the JavaScript code procedurally creates Three.js `BoxGeometry` and `CylinderGeometry` meshes based on building coordinates and heights specified in the JSON data.

### Q77: How does floor isolation slicing work in the 3D model?
**Answer:** When the user clicks "Isolate Floor 2", a JavaScript function iterates through all floor mesh groups in the scene, setting `.visible = false` or increasing transparency (`material.opacity = 0.15`) for storeys above and below Floor 2.

### Q78: How is the route visualized in 3D?
**Answer:** The 3D coordinates $(x, y, z)$ of the path returned by Dijkstra are converted into a `CatmullRomCurve3` spline. Three.js then sweeps a `TubeGeometry` along this spline with an emissive glowing green material (`#35D99A`).

### Q79: How does camera rotation and zoom work?
**Answer:** Through `Three.OrbitControls`. Left-click and drag rotates the camera around the campus target center; right-click pans horizontally; and the mouse scroll wheel adjusts camera distance (zoom).

### Q80: Is the 3D digital twin a surveyed BIM or CAD model?
**Answer:** No. We explicitly clarify that the 3D model is a schematic digital twin derived from building dimensions and floor plans, designed for spatial intuition rather than architectural structural engineering.

### Q81: How is high performance (60 FPS) maintained on low-end laptops?
**Answer:** By using low polygon counts, disabling computationally expensive dynamic shadow maps, reusing shared materials, and utilizing hardware-accelerated WebGL drawing calls.

### Q82: How does the 3D view reflect active obstacles?
**Answer:** When an edge is marked as blocked in the database, the serialized JSON payload flags that pathway as `is_blocked = True`. The Three.js renderer colors the corresponding wireframe pathway glowing red instead of green.

### Q83: What lighting is configured in the Three.js scene?
**Answer:** A combination of `AmbientLight` (providing soft overall illumination) and `DirectionalLight` (simulating sunlight from the southwest), highlighting building contours and elevation depth.

### Q84: How are location pins rendered in 3D?
**Answer:** As vertical Three.js marker cones positioned directly above landmark coordinates, accompanied by HTML/CSS overlay labels displaying room names upon mouse hover.

---

## CATEGORY H: SECURITY & GOVERNANCE (Q85 – Q95)

### Q85: What authentication mechanism is implemented?
**Answer:** Form-based session authentication with passwords hashed using PBKDF2 (Password-Based Key Derivation Function 2) using HMAC-SHA256.

### Q86: Why is PBKDF2 used instead of MD5 or plain SHA-256?
**Answer:** MD5 and single-round SHA-256 are extremely fast, making them vulnerable to brute-force and rainbow-table attacks. PBKDF2 applies 600,000 iterations of HMAC-SHA256, intentionally making each hash computation computationally expensive for attackers while negligible for legitimate users.

### Q87: What is cryptographic salting?
**Answer:** Appending a unique, cryptographically random 32-byte sequence to each password before hashing:
$$\text{Hash} = \text{PBKDF2}(\text{password}, \text{salt}, \text{iterations} = 600000)$$
This ensures that two users with identical passwords have completely distinct stored hashes, defeating rainbow-table attacks.

### Q88: What are the three roles in Role-Based Access Control (RBAC)?
**Answer:**
1. **Student:** View maps, calculate routes, submit obstacle reports, customize accessibility preferences.
2. **Field Staff:** All Student privileges plus verify on-ground obstacles, sever pathways, and resolve tickets.
3. **Administrator:** All Staff privileges plus user account management, role assignment, system configuration, and audit log inspection.

### Q89: How does brute-force login rate limiting work?
**Answer:** The `users` table tracks `failed_attempts` and `locked_until`. If 5 consecutive failed login attempts occur within 15 minutes, the account is locked for 300 seconds (5 minutes), rejecting any further login attempts.

### Q90: How is session hijacking mitigated?
**Answer:** User session state is held strictly in server-side memory (`st.session_state`). Session IDs are not stored in unencrypted client URL parameters.

### Q91: What is the sole administrator demotion protection?
**Answer:** The `DatabaseManager.update_user_role()` method enforces that if only one user has the `Administrator` role, any attempt to demote that account to `Student` or `Field Staff` is strictly rejected to prevent administrative lockout.

### Q92: What information is recorded in the audit log?
**Answer:** Every security-sensitive action writes:
- Event timestamp (ISO 8601 UTC).
- Acting User ID and username.
- Action type (`LOGIN_SUCCESS`, `LOGIN_FAILED`, `ROLE_UPDATE`, `OBSTACLE_VERIFIED`, etc.).
- Target entity and contextual details.

### Q93: How was demo credential remediation handled in Phase 31?
**Answer:** All default, hardcoded demo passwords were revoked by replacing database password hashes with randomized invalid strings and setting account statuses to `Inactive`. A fresh system requires initial setup via the interactive Admin Bootstrap Wizard.

### Q94: What password complexity policy is enforced?
**Answer:** Passwords must be at least 8 characters long and contain both alphabetical letters and numeric digits.

### Q95: How are SQL injection vulnerabilities prevented?
**Answer:** 100% of database queries use parameterized SQL statements (`?` placeholders). User input is never concatenated directly into SQL query strings.

---

## CATEGORY I: TESTING & DEPLOYMENT (Q96 – Q108)

### Q96: How many automated tests exist in the project?
**Answer:** 208 automated unit and regression tests across 23 test modules in the `tests/` directory.

### Q97: What testing framework is used?
**Answer:** Python's standard `unittest` library, executed via:
```powershell
python -m unittest discover tests -v
```

### Q98: What is the execution time and pass rate of the test suite?
**Answer:** All 208 tests pass with 0 failures and 0 errors in approximately 52 seconds.

### Q99: What is regression testing?
**Answer:** Re-running existing tests after introducing code changes to ensure that new features, bug fixes, or optimizations have not broken existing functionality.

### Q100: How is code compilation verified?
**Answer:** Using Python's `compileall` utility:
```powershell
python -m compileall -q .
```
Exiting with code 0 confirms zero syntax or compilation errors across the entire codebase.

### Q101: How is the application containerized?
**Answer:** A multi-stage `Dockerfile` packages Python 3.11, installs pinned dependencies from `requirements.txt`, configures non-root user execution, and exposes port 8501.

### Q102: What is the role of Nginx in production deployment?
**Answer:** Nginx acts as a reverse proxy, handling SSL/TLS HTTPS termination, static asset caching, and WebSocket connection upgrade headers required by Streamlit's real-time communication.

### Q103: What is the purpose of `docker-compose.yml`?
**Answer:** It coordinates the multi-container environment, defining the Streamlit application container, Nginx reverse proxy, shared volume mounts for SQLite persistence (`./data:/app/data`), and restart policies.

### Q104: How does the application verify runtime health?
**Answer:** Streamlit provides a native HTTP health endpoint at `http://localhost:8501/_stcore/health`, which returns HTTP 200 "ok" in under 50 milliseconds.

### Q105: What is the memory footprint of the running application?
**Answer:** Approximately 140MB of RAM during active execution, making it extremely lightweight and cost-effective to host.

### Q106: What is the status of public cloud hosting?
**Answer:** Status C: Deployment Prepared. The repository is configured with `st.secrets` adapters for 1-click activation on Streamlit Community Cloud or Hugging Face Spaces, requiring only owner GitHub OAuth login.

### Q107: How are Python dependencies managed?
**Answer:** Pinned in `requirements.txt`, specifying exact versions for `streamlit`, `networkx`, `plotly`, `folium`, and `python-pptx` to prevent supply-chain breaking changes.

### Q108: How is database persistence maintained across container restarts?
**Answer:** Through a Docker named volume or host bind-mount linking the host's `data/` directory to `/app/data` inside the container.

---

## CATEGORY J: CRITICAL EVALUATION & FUTURE SCOPE (Q109 – Q120)

### Q109: What is the biggest technical limitation of the current system?
**Answer:** The absence of automated real-time indoor positioning (such as BLE beacons or WiFi RTT). Users must manually select their starting point rather than having it detected automatically.

### Q110: Are the campus coordinates geodetically surveyed?
**Answer:** No. Coordinates are schematic representations calibrated to campus layout maps. They are proportionally accurate for distance calculations, but not centimeter-precise geodetic survey coordinates.

### Q111: What would happen if a malicious user submitted a false obstacle report?
**Answer:** The system's operational lifecycle prevents disruption: all reports start in `PENDING` status and do not alter graph edge weights. Only authorized `Field Staff` or `Administrators` can verify a report and trigger rerouting.

### Q112: How would the system scale to a campus with 500 buildings and 10,000 nodes?
**Answer:**
1. Replace standard Dijkstra with $A^*$ or Contraction Hierarchies to maintain sub-millisecond query latency.
2. Partition the graph by building clusters using hierarchical graphs.
3. Migrate storage from SQLite to PostgreSQL with PostGIS for spatial indexing ($R$-trees).

### Q113: How could Bluetooth Low Energy (BLE) beacons be integrated?
**Answer:** Low-cost battery-powered BLE beacons installed in corridors broadcast periodic UUIDs. A mobile client measures Received Signal Strength Indicator (RSSI), applies trilateration or fingerprinting to resolve the user's $(x, y, \text{floor})$, and passes it as the origin node.

### Q114: How could the system support visually impaired students?
**Answer:** By integrating text-to-speech (TTS) voice guidance with directional audio cues (e.g., "In 10 meters, turn 90 degrees right into the AI Lab corridor") and haptic vibration prompts on mobile devices.

### Q115: How does the application prevent concurrent write locks in SQLite?
**Answer:** By activating WAL mode, setting busy timeouts to 5,000ms, and maintaining short, localized write transactions.

### Q116: How could live elevator status be integrated?
**Answer:** By connecting IoT telemetry from elevator controller APIs. If an elevator experiences a mechanical fault, an automated webhook would submit a verified obstacle report, immediately severing the vertical edge in the navigation graph.

### Q117: What was the most difficult engineering challenge encountered?
**Answer:** Harmonizing multi-storey 2D indoor coordinate planes with outdoor ground pathways into a single unified graph where Dijkstra could seamlessly transition across horizontal corridors and vertical elevator shafts.

### Q118: How does this project differ from commercial mapping apps?
**Answer:** Commercial apps stop at building entrances, lack interior room directories, do not account for step-free elevator requirements, and do not provide crowdsourced barrier verification.

### Q119: What social and academic impact does this project provide?
**Answer:** It directly supports UN Sustainable Development Goal 10 (Reduced Inequalities) and Goal 11 (Sustainable Cities & Communities) by fostering physical inclusivity and equal access to university education.

### Q120: What is your final concluding takeaway?
**Answer:** Accessible Campus Navigator proves that fundamental computer science principles—graph theory, Dijkstra's algorithm, relational databases, and WebGL graphics—can be combined to solve real accessibility challenges, making JAIN University more inclusive and accessible for everyone.
