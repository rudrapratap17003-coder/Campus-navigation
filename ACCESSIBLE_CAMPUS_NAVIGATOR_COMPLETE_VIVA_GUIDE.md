# ACCESSIBLE CAMPUS NAVIGATOR
## COMPLETE TECHNICAL VIVA VOCE DEFENSE & EXAMINER INTERVIEW GUIDE

**Student Name:** Rudra Pratap  
**University Seat Number (USN):** 25BTRCL214  
**Degree Program:** Bachelor of Technology (B.Tech)  
**Branch:** Artificial Intelligence and Machine Learning (Section D)  
**Department:** School of Computer Science and Engineering  
**Faculty:** Faculty of Engineering and Technology (FET)  
**Institution:** JAIN (Deemed-to-be University), Bangalore, India  
**Project Title:** Accessible Campus Navigator  
**Repository:** https://github.com/rudrapratap17003-coder/Campus-navigation  
**Verified Automated Tests:** 190 Passing Tests across 20 Test Suites (0 Failures, 0 Errors, 32.1s runtime)  
**Production Stack:** Python 3.11/3.14, NetworkX, Three.js, Streamlit, SQLite 3 (WAL), Docker, Nginx

---

## TABLE OF CONTENTS

1. [SPECIAL SECTION 1: How to Explain This Project in 2 Minutes](#special-section-1-how-to-explain-this-project-in-2-minutes)
2. [SECTION A: Project Understanding & Architecture (Q1 – Q10)](#section-a-project-understanding--architecture)
3. [SECTION B: Python & Software Engineering (Q11 – Q20)](#section-b-python--software-engineering)
4. [SECTION C: Data Structures & Graph Algorithms (Q21 – Q33)](#section-c-data-structures--graph-algorithms)
5. [SECTION D: Accessibility Standards & Disability Inclusion (Q34 – Q43)](#section-d-accessibility-standards--disability-inclusion)
6. [SECTION E: Database Design, Storage & Persistence (Q44 – Q53)](#section-e-database-design-storage--persistence)
7. [SECTION F: Cybersecurity, Authentication & Access Control (Q54 – Q63)](#section-f-cybersecurity-authentication--access-control)
8. [SECTION G: 3D Visualization, WebGL & Three.js (Q64 – Q73)](#section-g-3d-visualization-webgl--threejs)
9. [SECTION H: Deployment, Docker & DevOps (Q74 – Q83)](#section-h-deployment-docker--devops)
10. [SPECIAL SECTION 2: Questions Faculty Ask About Limitations](#special-section-2-questions-faculty-ask-about-limitations)
11. [SPECIAL SECTION 3: Questions Faculty Ask About Algorithm Selection](#special-section-3-questions-faculty-ask-about-algorithm-selection)
12. [SPECIAL SECTION 4: Questions Faculty Ask About Real-World Deployment](#special-section-4-questions-faculty-ask-about-real-world-deployment)

---

## SPECIAL SECTION 1: HOW TO EXPLAIN THIS PROJECT IN 2 MINUTES

### The "Elevator Pitch" for Examiners

> *"Respected examiners, commercial navigation systems like Google Maps excel on road networks but fail completely inside campus complexes: they stop at external parking lots, lack floor-by-floor vertical awareness, and are oblivious to wheelchair barriers such as sudden staircases or broken elevators.*
>
> *To solve this, I designed and developed the **Accessible Campus Navigator** for JAIN Global Campus and its five-floor Faculty of Engineering and Technology complex.*
>
> *The application integrates three primary engineering layers:*
> *1. **A Mathematical Campus Graph** built in NetworkX consisting of 79 verified spatial vertices and 106 bidirectional edges, accurately capturing external walkways, building portals, 5 floors of corridors, and vertical cores (2 elevators and 2 staircases).*
> *2. **Dual-Algorithm Routing & Accessibility Engine** providing Dijkstra's algorithm for globally shortest physical distance and Breadth-First Search for minimum-turn routes. When Wheelchair Mode is enabled, the graph dynamically prunes all non-compliant edges, eliminating all stairs, prioritizing 1:12 slope ramps, and guaranteeing 100% step-free routing under India's RPwD Act 2016.*
> *3. **An Interactive Three.js 3D Digital Twin** providing full spatial awareness with floor switching, exploded views, turn-by-turn guidance, and real-time obstacle reporting where verified corridor hazards trigger automated dynamic detours.*
>
> *The system is hardened with cryptographic password hashing, role-based access control, SQLite Write-Ahead Logging, and Docker containerization, verified by 190 automated unit and regression tests with zero failures."*

---

## SECTION A: PROJECT UNDERSTANDING & ARCHITECTURE

#### Q1: What is the core problem that the Accessible Campus Navigator solves?
**Answer:** The Accessible Campus Navigator addresses the "last-hundred-meters" spatial accessibility and wayfinding problem within large university environments. Traditional GPS and satellite navigation systems cannot resolve indoor elevations, indoor corridors, or room-level destinations. Crucially, they lack awareness of physical accessibility barriers—such as stairs, narrow doorways, steep curbs, or temporary hazards—which disproportionately impact persons with disabilities, first-year students, and campus visitors.

#### Q2: What are the three primary architectural layers of this system?
**Answer:**
1. **Presentation & Visualization Layer:** Browser-based Streamlit interface integrated with an interactive Three.js WebGL canvas rendering outdoor terrain and the five-floor FET building digital twin with responsive viewports (360px to 1920px+).
2. **Application & Routing Service Layer:** Python modules encapsulating graph traversal (`modules/route_finder.py`), accessibility validation (`modules/accessibility_engine.py`), obstacle lifecycle management (`modules/obstacle_manager.py`), and authentication (`modules/security_manager.py`).
3. **Data Persistence Layer:** SQLite 3 database operating in Write-Ahead Logging (WAL) mode for users, obstacles, favorites, and audit trails, synchronized with an in-memory NetworkX spatial graph of 79 nodes and 106 edges.

#### Q3: Why is the campus represented as a mathematical graph?
**Answer:** A graph $G = (V, E)$ is the optimal discrete mathematical structure for spatial networks. Vertices ($V$) represent decision points, entrances, rooms, elevator doors, and intersections. Edges ($E$) represent navigable pathways, sidewalks, ramps, stairs, and elevator shafts. Each edge contains rich metadata attributes: `distance` (meters), `wheelchair_accessible` (boolean), `floor_level` (integer), and `surface_type` (paved, tiled, grass).

#### Q4: How does the system handle multi-floor transitions within the FET building?
**Answer:** Vertical movement between Ground Floor (Floor 0) and Floor 4 is modeled using dedicated vertical core nodes: `FET_ELEVATOR_1`, `FET_ELEVATOR_2`, `FET_STAIR_A`, and `FET_STAIR_B`. Vertical edges connect these nodes across floors with calibrated transition penalties. In the 3D twin, when navigation reaches an elevator or staircase, the UI presents an interactive Floor Transition Modal and smoothly animates the camera to the target floor.

#### Q5: How is bi-directional communication established between Streamlit and Three.js?
**Answer:** Streamlit renders server-side Python components, whereas Three.js executes client-side WebGL in an iframe. Communication is achieved via `streamlit.components.v1.html` using a structured JSON state bridge. Active route coordinates, highlighted floors, camera target presets, and user interaction events are serialized and dispatched across the iframe boundary.

#### Q6: What roles exist within the Role-Based Access Control (RBAC) system?
**Answer:**
- **Student:** View 3D digital twin, search facilities, calculate routes, follow turn-by-turn navigation, save favorites, and submit obstacle reports in `pending` status.
- **Staff (Faculty/Officials):** All student permissions, plus priority obstacle submissions and departmental occupancy/facility status views.
- **Administrator:** Full governance: review and verify pending obstacles, resolve hazards, unlock user accounts, inspect security audit logs, trigger automated database backups, and export PostgreSQL schemas.

#### Q7: How does the system guarantee that wheelchair users never encounter stairs?
**Answer:** In `modules/accessibility_engine.py`, the routing pipeline constructs an accessible subgraph $G_{acc} \subset G$. Any edge marked `wheelchair_accessible = False` or identified as a staircase vertex (`FET_STAIR_*`) is pruned before path computation. The computed itinerary is then verified by an automated invariant checker ensuring `stair_count == 0` before presenting it to the user.

#### Q8: What is dynamic rerouting and how is it triggered?
**Answer:** When an obstacle (e.g., water leak, floor waxing, elevator outage) is reported and marked `verified` by an administrator, the `ObstacleManager` flags the affected graph edge. The routing engine applies a punitive weight penalty ($+10,000$ meters) or removes the edge entirely. If a user has an active navigation session traversing that segment, the system detects the conflict, sounds an alert, flashes the 3D zone in red, and recalculates an alternative route in real time.

#### Q9: What accessibility guidelines does this project follow?
**Answer:** The project complies with:
1. **Rights of Persons with Disabilities (RPwD) Act 2016 (India)** — Mandatory non-discriminatory physical access.
2. **CPWD Guidelines for Harmonized Built Environment (2021)** — 1:12 ramp gradients, 900 mm corridor clearances.
3. **WCAG 2.1 Level AA** — Digital interface contrast ratios ($\ge 4.5:1$), keyboard navigability, text resizing, and screen reader semantic attributes.

#### Q10: How many automated tests exist and what do they validate?
**Answer:** The repository contains **190 automated unit and regression tests** across 20 modules in `tests/`. They validate graph connectivity, Dijkstra vs. BFS path equality, wheelchair step-free invariants, obstacle penalty injection, password hashing and salt verification, brute-force rate limiting, SQLite WAL concurrency, and responsive CSS breakpoints.

---

## SECTION B: PYTHON & SOFTWARE ENGINEERING

#### Q11: What software design patterns are utilized in this project?
**Answer:**
1. **Singleton Pattern:** Used for database connection management (`DatabaseManager`) to ensure a single shared pool under SQLite WAL mode.
2. **Strategy Pattern:** Implemented in `modules/route_finder.py`, allowing runtime switching between Dijkstra and BFS routing strategies.
3. **Observer/Listener Pattern:** State updates between dynamic obstacle verification and active wayfinding sessions.
4. **Factory Pattern:** Node and edge creation helper functions in `modules/campus_data.py`.
5. **Data Transfer Object (DTO):** Typed dictionaries and dataclasses for route result payloads and obstacle records.

#### Q12: Why was Python selected as the primary backend language?
**Answer:** Python provides native support for high-performance discrete mathematics via `NetworkX`, clean database abstraction via built-in `sqlite3`, rapid interactive web delivery via `Streamlit`, and rich scientific libraries. Furthermore, Python's readable syntax and strong typing annotations ensure maintainability for academic evaluation and future expansion.

#### Q13: How does the project enforce code quality and modularity?
**Answer:** All core logic is decomposed into single-responsibility modules inside `modules/`:
- `campus_data.py`: Raw graph geometry and node coordinates.
- `route_finder.py`: Pure algorithmic traversal logic.
- `accessibility_engine.py`: Domain-specific compliance rules.
- `obstacle_manager.py`: CRUD operations for hazards.
- `security_manager.py`: Cryptographic primitives and RBAC.
- `database.py`: Thread-safe database transactions.
Every module is paired with dedicated unit tests in `tests/`.

#### Q14: How are circular imports avoided in the application?
**Answer:** Circular dependencies are prevented by enforcing a strict layered dependency hierarchy:
`campus_data` $\rightarrow$ `database` $\rightarrow$ `security_manager` $\rightarrow$ `obstacle_manager` $\rightarrow$ `route_finder` $\rightarrow$ `ui_theme` $\rightarrow$ `main.py` / `pages/`. No lower-level module ever imports a presentation or orchestrator module.

#### Q15: How does the application handle exceptions during route calculation?
**Answer:** Route queries are wrapped in defensive `try...except` blocks. If an invalid or disconnected node is requested, `NetworkXNoPath` or custom `NavigationError` exceptions are caught. The engine returns a structured error response with graceful user messages and logs the event without crashing the Streamlit session.

#### Q16: What is the significance of type annotations in this project?
**Answer:** Functions across `modules/` utilize Python standard typing (`List`, `Dict`, `Tuple`, `Optional`, `Union`, `Any`). This enables static analysis, prevents `NoneType` attribute errors, provides self-documenting APIs for collaborating developers, and facilitates automated test assertions.

#### Q17: How is session state managed in Streamlit across reruns?
**Answer:** Streamlit reruns the script top-to-bottom on every user interaction. Persistent state is preserved using `st.session_state`. Key state variables include: `authenticated`, `current_user`, `user_role`, `active_route`, `navigation_step`, `selected_floor`, `high_contrast_mode`, and `language_preference`.

#### Q18: What is the role of virtual environment isolation (`.venv`)?
**Answer:** Virtual environments prevent package version collisions between the project dependencies (`streamlit`, `networkx`, `pillow`, `reportlab`, `python-docx`, `python-pptx`) and global system Python packages. It guarantees repeatable builds across developer machines and Docker containers.

#### Q19: How are automated tests structured and executed?
**Answer:** Tests use `pytest` and Python's `unittest` framework. They are organized into 20 granular files: `test_route_finder.py`, `test_accessibility_engine.py`, `test_security.py`, `test_obstacles.py`, etc. Executed via:
```bash
.venv\Scripts\python.exe -m pytest tests/ -v
```
Producing 190 passed tests in ~32 seconds.

#### Q20: How are memory leaks prevented in a continuous Streamlit session?
**Answer:** Large datasets (like the 3D geometry JSON) are loaded into memory once and cached using `@st.cache_data`. Database connections use context managers (`with sqlite3.connect(...) as conn:`) ensuring file descriptors are immediately closed.

---

## SECTION C: DATA STRUCTURES & GRAPH ALGORITHMS

#### Q21: What is the exact graph topology of the campus network?
**Answer:**
- Total Vertices ($|V|$): **79 nodes** (24 outdoor locations, 55 indoor locations across 5 floors of FET).
- Total Edges ($|E|$): **106 bidirectional pathways** (total 212 directed arcs).
- Vertex Attributes: `id`, `name`, `floor`, `x`, `y`, `z`, `type`, `wheelchair_accessible`.
- Edge Attributes: `distance` (meters), `wheelchair_accessible` (boolean), `is_staircase`, `is_elevator`, `slope`.

#### Q22: Explain Dijkstra's algorithm and its implementation in this project.
**Answer:** Dijkstra's algorithm solves the single-source shortest path problem on weighted graphs with non-negative edge weights.
1. Initialize distance table: $d[start] = 0$, $d[v] = \infty$ for all other $v \in V$.
2. Maintain a min-heap priority queue storing tuples `(current_distance, node)`.
3. In each iteration, pop node $u$ with minimum distance.
4. For every neighbor $v$ connected by edge $(u, v)$ with weight $w$:
   $$\text{If } d[u] + w < d[v] \implies d[v] = d[u] + w, \quad \text{parent}[v] = u$$
   Push `(d[v], v)` into the priority queue.
5. Reconstruct the shortest path by backtracking from destination to origin via `parent`.

#### Q23: What is the time and space complexity of Dijkstra's algorithm with a min-heap?
**Answer:**
- **Time Complexity:** $O((|E| + |V|) \log |V|)$. Each vertex is extracted from the min-heap once ($O(|V| \log |V|)$), and each edge relaxation may push an updated distance ($O(|E| \log |V|)$). For $|V|=79$ and $|E|=106$, execution completes in under 2 milliseconds.
- **Space Complexity:** $O(|V|)$ to store the distance dictionary, visited set, priority queue, and predecessor parent mapping.

#### Q24: How does Breadth-First Search (BFS) differ from Dijkstra in your application?
**Answer:** BFS treats all edges as having uniform unweighted cost (weight = 1). It explores neighbors level-by-level using a FIFO queue.
- **Dijkstra:** Guarantees minimum *physical distance in meters* (e.g., 280 m).
- **BFS:** Guarantees minimum *number of decision points / intermediate turns* (e.g., 5 hallway segments), which is often easier for cognitive wayfinding even if physical distance is slightly longer.

#### Q25: What is the time and space complexity of Breadth-First Search?
**Answer:**
- **Time Complexity:** $O(|V| + |E|)$. Every vertex is enqueued and dequeued at most once, and all incident edges are examined.
- **Space Complexity:** $O(|V|)$ for the FIFO queue and visited set.

#### Q26: Can Dijkstra's algorithm handle negative edge weights? Does your campus have negative weights?
**Answer:** No, standard Dijkstra cannot handle negative edge weights (which could cause infinite loops or incorrect greedy choices, requiring Bellman-Ford). However, in physical spatial navigation, all distances, slopes, and times are strictly non-negative ($w \ge 0$), making Dijkstra mathematically guaranteed to find the global optimum.

#### Q27: How is the penalty mechanism applied to active obstacles in Dijkstra?
**Answer:** When an obstacle is marked `verified` with severity 'Medium', the edge weight is incremented by an obstacle penalty constant $P = 10,000$ meters:
$$w'(u, v) = w(u, v) + 10000$$
This ensures the min-heap will prioritize any viable alternative detour, while still preserving graph reachability if no alternate path exists. If severity is 'High' (total blockage), the edge is completely omitted from the graph.

#### Q28: How does the system compare multiple routes side-by-side?
**Answer:** In `modules/route_finder.py`, function `compare_routes()` computes:
1. Shortest Distance Route (Dijkstra)
2. Minimum Hop Route (BFS)
3. Step-Free Route (Accessibility Filtered Dijkstra)
It aggregates metrics: total distance (m), estimated walking time (min, based on 1.2 m/s standard gait or 0.8 m/s wheelchair speed), turn count, and stair count.

#### Q29: What data structure is used to represent the graph in memory?
**Answer:** `networkx.Graph`, which internally utilizes a Python dictionary-of-dictionaries-of-dictionaries:
```python
# G[u][v] contains the attribute dictionary for edge (u, v)
adj = {
    'OUTDOOR_GATE_MAIN': {
        'OUTDOOR_SECURITY_1': {'distance': 35.0, 'wheelchair_accessible': True}
    }
}
```
This grants $O(1)$ average time complexity for neighbor lookups and edge attribute retrieval.

#### Q30: How are spatial coordinates mapped from 2D floor plans into 3D space?
**Answer:** Each node contains $(x, y, z)$ coordinates:
- $x$: East-West horizontal offset across the campus footprint.
- $z$: North-South horizontal offset across the campus footprint.
- $y$: Vertical elevation: $y = \text{floor\_number} \times 4.5\text{ meters}$, where Ground Floor is $y = 0.0\text{ m}$ and Floor 4 is $y = 18.0\text{ m}$.

#### Q31: How does the application detect disconnected subgraphs or isolated nodes?
**Answer:** Graph connectivity is verified during initialization and in automated tests (`test_graph_connectivity.py`) using `networkx.is_connected(G)` and `networkx.connected_components(G)`. In the primary campus graph, all 79 nodes form a single connected component.

#### Q32: What heuristic would be used if upgrading from Dijkstra to A* search?
**Answer:** A* uses $f(n) = g(n) + h(n)$, where $g(n)$ is the exact cost from start to $n$, and $h(n)$ is an admissible heuristic estimate to the goal. For this 3D campus, the optimal admissible heuristic is the 3D Euclidean distance:
$$h(n) = \sqrt{(x_n - x_{goal})^2 + (y_n - y_{goal})^2 + (z_n - z_{goal})^2}$$
Because straight-line distance is always $\le$ actual walking distance along hallways, $h(n)$ never overestimates, guaranteeing $A^*$ optimality.

#### Q33: How does the system calculate estimated walking time?
**Answer:**
$$\text{Time (seconds)} = \sum \frac{\text{edge\_distance}}{\text{speed\_profile}} + \sum \text{vertical\_delay}$$
- Standard walking speed: $1.2\text{ m/s}$ (approx. $4.3\text{ km/h}$).
- Wheelchair navigation speed: $0.8\text{ m/s}$ (approx. $2.9\text{ km/h}$).
- Elevator wait and travel time: fixed $45\text{ seconds}$ per vertical transition.
- Staircase ascent: $+15\text{ seconds}$ per floor climb.

---

## SECTION D: ACCESSIBILITY STANDARDS & DISABILITY INCLUSION

#### Q34: What constitutes a "barrier-free" university campus according to Indian law?
**Answer:** Under Section 40 and 46 of the Rights of Persons with Disabilities (RPwD) Act 2016, all public educational institutions must ensure accessible physical environments. This requires:
- Tactile paths and level entrances.
- Ramps with maximum slope of 1:12 (8.33%) equipped with double handrails.
- Accessible elevators with audio announcements, braille buttons, and minimum door clear width of 800 mm.
- Step-free access to all classrooms, libraries, laboratories, and restrooms.

#### Q35: How does the system model wheelchair ramps vs. staircases?
**Answer:** In `campus_data.py`:
- Ramps (`RAMP_WEST`, `RAMP_EAST`) have `wheelchair_accessible: True`, `slope: 0.083`, and `is_staircase: False`.
- Staircases (`FET_STAIR_A`, `FET_STAIR_B`) have `wheelchair_accessible: False`, `step_count: 24`, and `is_staircase: True`.
When wheelchair mode is engaged, all nodes and edges with `wheelchair_accessible: False` are excluded from the candidate path search.

#### Q36: What visual accessibility features are implemented in the UI?
**Answer:**
1. **High Contrast Mode:** Switches the UI to dark obsidian background (`#0B1512`) with bright emerald (`#10B981`) and electric cyan (`#38BDF8`) text, achieving a contrast ratio $> 7:1$ (exceeding WCAG AAA).
2. **Text Scaling:** Responsive CSS font scaling supporting up to 200% enlargement without text clipping.
3. **Reduced Motion Mode:** CSS media query `@media (prefers-reduced-motion: reduce)` disabling 3D camera fly-to animations for users with vestibular or motion sensitivity.

#### Q37: How does the system support visually impaired students?
**Answer:**
1. Text-to-Speech (TTS) turn-by-turn auditory cues (e.g., *"In 20 meters, turn right into West Corridor"*).
2. Semantic HTML markup with ARIA roles and labels for screen readers (NVDA, JAWS).
3. Sound effect cues for arrival at decision points, elevators, and destinations.

#### Q38: What languages are supported and why is multilingual capability critical?
**Answer:** The interface supports **English, Kannada (ಕನ್ನಡ), and Hindi (हिन्दी)**.
- **Kannada:** Essential for local campus staff, maintenance personnel, and regional students in Karnataka.
- **Hindi:** Facilitates accessibility for students from northern and central India.
All UI labels, obstacle categories, and navigation directives are localized in `modules/i18n.py`.

#### Q39: What is the significance of the "Stair Count = 0" metric in route evaluation?
**Answer:** Even a single step (e.g., a 15 cm entrance curb) makes a pathway physically impassable for an unaccompanied manual or motorized wheelchair user. Therefore, our validation invariant checks that the total stair count along the step-free route equals exactly zero.

#### Q40: How does the system assist individuals with cognitive or neurodiverse conditions?
**Answer:**
- BFS route option reduces cognitive load by minimizing intermediate turns.
- Visual landmarks (water fountain, library foyer, cafeteria) are highlighted as reference beacons along the path.
- Step-by-step sequential guidance prevents navigational anxiety in large, unfamiliar buildings.

#### Q41: How do you verify compliance with WCAG 2.1 Level AA?
**Answer:**
1. Color contrast verified using WebAIM color contrast analyzer ($\ge 4.5:1$ for body text, $\ge 3:1$ for large text and UI cards).
2. Full keyboard navigation operable via `Tab`, `Enter`, and arrow keys without keyboard traps.
3. Form fields include explicit associated labels and error feedback banners.

#### Q42: What physical obstacles are categorized in the reporting system?
**Answer:**
- Slippery floor / water leakage.
- Elevator out of service.
- Construction / corridor maintenance scaffolding.
- Temporary furniture / event blockade.
- Narrowed path / ramp obstruction.

#### Q43: What happens if an elevator breaks down in a multi-floor building?
**Answer:** An obstacle report is submitted for `FET_ELEVATOR_1`. Once verified, the elevator edges are severed. If `FET_ELEVATOR_2` is operational, the wheelchair algorithm automatically reroutes via Elevator 2. If *both* elevators are obstructed, the system gracefully alerts the user that no wheelchair-accessible path exists to upper floors and suggests contacting campus disability assistance.

---

## SECTION E: DATABASE DESIGN, STORAGE & PERSISTENCE

#### Q44: What database engine is used and why was it chosen over alternatives?
**Answer:** **SQLite 3** is the primary database. It was chosen because:
- Zero-configuration, serverless, self-contained single-file architecture.
- Exceptional read throughput and sub-millisecond query latency.
- Native integration with Python's standard library (`import sqlite3`).
- Fully transactional (ACID compliant).
- Ideal for embedded campus kiosks and containerized desktop deployments.

#### Q45: What is Write-Ahead Logging (WAL) mode and why is it enabled?
**Answer:** By default, SQLite uses a rollback journal which locks the entire database file during writes, blocking concurrent readers. Enabling WAL mode (`PRAGMA journal_mode=WAL;`):
1. Allows readers to read while a writer is writing (concurrent non-blocking reads).
2. Dramatically increases write transaction performance by appending changes sequentially to a `-wal` file.
3. Enhances crash resilience and prevents database corruption.

#### Q46: Detail the database schema and its primary tables.
**Answer:**
1. `users`: `id` (PK), `username` (UNIQUE), `password_hash`, `salt`, `role`, `failed_attempts`, `locked_until`, `created_at`.
2. `obstacles`: `id` (PK), `location_id`, `description`, `severity`, `status`, `reporter_name`, `reported_at`, `verified_by`, `verified_at`.
3. `user_favorites`: `id` (PK), `user_id` (FK $\rightarrow$ `users.id`), `origin_id`, `destination_id`, `created_at`.
4. `navigation_logs`: `id` (PK), `session_id`, `origin`, `destination`, `distance`, `route_type`, `timestamp`.
5. `audit_logs`: `id` (PK), `user_id`, `action`, `target`, `details` (JSON), `timestamp`.

#### Q47: How are SQL injection attacks prevented?
**Answer:** All database operations strictly utilize parameterized queries with placeholders (`?`):
```python
cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
```
String concatenation or f-strings are never used to compose SQL statements, ensuring user inputs are treated exclusively as literal data values by the query planner.

#### Q48: How is database migration to PostgreSQL implemented?
**Answer:** The project includes `modules/database_exporter.py`, which generates standard PostgreSQL-compliant DDL scripts (`schema.sql`) and DML inserts (`data.sql`). Data types are mapped appropriately (e.g., SQLite `INTEGER PRIMARY KEY` $\rightarrow$ PostgreSQL `SERIAL PRIMARY KEY`, `TIMESTAMP` $\rightarrow$ `TIMESTAMPTZ`).

#### Q49: How does the backup subsystem operate?
**Answer:** In `modules/database.py`, the `backup_database()` routine uses SQLite's Online Backup API:
```python
with sqlite3.connect("campus_navigation.db") as src:
    with sqlite3.connect(f"backups/backup_{timestamp}.db") as dst:
        src.backup(dst)
```
This produces a bit-for-bit consistent snapshot without locking ongoing client operations.

#### Q50: How are database transactions managed to ensure ACID compliance?
**Answer:** Operations are wrapped in Python context managers:
```python
with self.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(...)
    # Automatic conn.commit() upon normal exit
    # Automatic conn.rollback() if an exception is raised
```

#### Q51: How are foreign key constraints enforced in SQLite?
**Answer:** By default, SQLite disables foreign key enforcement for backward compatibility. In this application, every connection initializes with:
```sql
PRAGMA foreign_keys = ON;
```
Ensuring relational integrity (e.g., deleting a user cascades or prevents orphan records in `user_favorites`).

#### Q52: What indexing strategy is applied for query optimization?
**Answer:**
- Unique B-tree index on `users(username)`.
- Index on `obstacles(status, severity)` for rapid sub-millisecond filtering of active hazards.
- Index on `user_favorites(user_id)` for quick profile loading.
- Index on `navigation_logs(timestamp)` for telemetry time-series analytics.

#### Q53: How is database concurrency handled in a multi-threaded Streamlit environment?
**Answer:** SQLite requires that each thread create its own connection object. The `DatabaseManager` implements a thread-safe connection factory using `check_same_thread=False` and a busy timeout:
```sql
PRAGMA busy_timeout = 10000; -- Wait up to 10 seconds on lock contention
```

---

## SECTION F: CYBERSECURITY, AUTHENTICATION & ACCESS CONTROL

#### Q54: How are passwords stored securely in the database?
**Answer:** Passwords are never stored in plaintext. The system uses a cryptographic hash algorithm combining SHA-256 with a unique, cryptographically secure 16-byte random salt generated via `secrets.token_hex(16)`:
$$\text{Hash} = \text{SHA-256}(\text{salt} \parallel \text{password})$$
Each user has a distinct salt stored in the database. When validating, the stored salt is concatenated with the incoming password attempt, hashed, and compared using `hmac.compare_digest()` to eliminate timing attack vulnerabilities.

#### Q55: Why is a salt necessary in password hashing?
**Answer:** A salt thwarts rainbow table attacks (precomputed tables of password hashes) and dictionary attacks. Even if two users choose the identical password (e.g., `Password123!`), their unique random salts ensure that their resulting database hashes are completely different.

#### Q56: How does the brute-force protection rate limiter work?
**Answer:** In `modules/security_manager.py`:
1. Every failed login attempt increments `failed_attempts` in the `users` table.
2. If `failed_attempts >= 5`, the account is automatically locked:
   $$\text{locked\_until} = \text{current\_timestamp} + 15\text{ minutes}$$
3. Any subsequent login attempts during the lockout window are immediately rejected with an HTTP 429-equivalent user alert.
4. Successful login resets `failed_attempts = 0`.
5. An administrator can manually unlock accounts via the Governance Console.

#### Q57: What is the purpose of the audit log?
**Answer:** The `audit_logs` table provides an immutable, chronological security audit trail. It records every security-critical event: `LOGIN_SUCCESS`, `LOGIN_FAILED`, `ACCOUNT_LOCKED`, `OBSTACLE_SUBMITTED`, `OBSTACLE_VERIFIED`, `DATABASE_BACKUP`, and `USER_UNLOCKED`, recording user ID, action, target resource, timestamp, and metadata.

#### Q58: How does the application prevent session hijacking?
**Answer:** Streamlit sessions are bound to unique server-side session IDs. User credentials are not stored in client-side cookies or localStorage. Upon logout, `st.session_state.clear()` purges all authentication tokens, roles, and user identifiers from server memory.

#### Q59: How does the system defend against Cross-Site Scripting (XSS)?
**Answer:** All user-supplied text (such as obstacle descriptions or room search queries) is sanitized and HTML-escaped before being rendered. In the Three.js iframe bridge, data is exchanged strictly as parsed JSON objects, preventing execution of injected script tags.

#### Q60: What password complexity policies are enforced?
**Answer:** The registration and password change modules require:
- Minimum length: 8 characters.
- At least one uppercase letter ($[A-Z]$).
- At least one lowercase letter ($[a-z]$).
- At least one numeric digit ($[0-9]$).
- At least one special symbol ($[!@\#\$\%\^\&\*]$).

#### Q61: What is the principle of least privilege and how is it applied?
**Answer:** Users are granted only the minimum permissions necessary for their academic role:
- Students cannot alter obstacle verification states or access system analytics.
- Staff can flag priority hazards but cannot modify database credentials.
- Only verified administrators possess write privileges for system settings, user unlocking, and database management.

#### Q62: How are environmental variables and secrets handled?
**Answer:** Database encryption keys, admin bootstrap passwords, and deployment configurations are loaded from environment variables (`.env`) using `os.getenv()`. No private production secrets are hardcoded in the public Git repository.

#### Q63: What security headers are configured in the Nginx reverse proxy?
**Answer:** The production `nginx.conf` injects:
- `X-Frame-Options: SAMEORIGIN` (prevents clickjacking)
- `X-Content-Type-Options: nosniff` (prevents MIME-type sniffing)
- `X-XSS-Protection: 1; mode=block`
- `Content-Security-Policy` restricting script and media execution origins.

---

## SECTION G: 3D VISUALIZATION, WEBGL & THREE.JS

#### Q64: Why was Three.js chosen for 3D visualization?
**Answer:** Three.js is the industry-standard JavaScript WebGL library. It enables hardware-accelerated 3D graphics rendering directly inside all modern web browsers without requiring browser plugins, third-party software installations, or specialized client hardware.

#### Q65: What are the primary 3D visual environments in the project?
**Answer:**
1. **Outdoor JAIN Global Campus:** Digital reconstruction of the campus perimeter, entrance gates, security kiosks, central water fountain, paved avenues, sports arena, and academic greens.
2. **Five-Floor FET Building:** Detailed architectural digital twin of the Faculty of Engineering and Technology complex featuring the circular central rotunda, entrance ramp, classrooms, advanced labs, faculty cabins, elevators, and staircases.

#### Q66: Explain how camera controls (OrbitControls) are configured.
**Answer:** `THREE.OrbitControls` manages user camera movement:
- **Left Mouse Click + Drag:** Orbits/rotates around the central target.
- **Right Mouse Click + Drag:** Pans across the horizontal and vertical plane.
- **Scroll Wheel:** Zooms in and out with clamped minimum (5m) and maximum (350m) distance limits to prevent camera clipping through building walls or flying into deep space.

#### Q67: What lighting model is used to achieve realistic architectural rendering?
**Answer:** The scene utilizes a multi-light composition:
- **Ambient Light (`0xffffff`, intensity 0.5):** Provides soft uniform base illumination to prevent pitch-black shadows.
- **Directional Sunlight (`0xfffaed`, intensity 1.0):** Positioned at $(100, 150, 80)$ casting realistic directional shadows across building facades.
- **Hemisphere Light:** Simulates natural atmospheric sky-to-ground color gradients (soft blue sky to muted warm earth).

#### Q68: How does the "Exploded Building View" work mathematically?
**Answer:** In the exploded building view, each floor group $i \in \{0, 1, 2, 3, 4\}$ has its vertical position offset proportionally:
$$y_i = \text{base\_elevation}_i + (i \times \text{explosion\_factor})$$
Where $\text{explosion\_factor} = 15.0\text{ meters}$. This vertically separates the floors like architectural layers, allowing users to view interior room layouts simultaneously without occlusion.

#### Q69: How is the active navigation path rendered in 3D?
**Answer:** The path is constructed as a continuous 3D tube or luminous polyline:
1. Node coordinate sequence is converted into an array of `THREE.Vector3(x, y + 0.3, z)`.
2. A `THREE.CatmullRomCurve3` or `THREE.LineCurve3` generates smooth interpolated splines.
3. Rendered with `THREE.TubeGeometry` using an emissive neon-green material (`#10B981`) with glowing pulsation to ensure visibility from any camera angle.

#### Q70: How does the 3D twin switch between different floors?
**Answer:** Each floor's architectural meshes, walls, and furnishings are assigned to a distinct `THREE.Group` (`floorGroups[0]` through `floorGroups[4]`). When a user selects a floor:
1. Target floor group has `visible = true` and `opacity = 1.0`.
2. Non-selected floors are either set to `visible = false` or converted into translucent ghost wireframes (`opacity = 0.15`).
3. The camera target smoothly tweens via linear interpolation (`lerp`) to center on the selected floor's bounding box.

#### Q71: How does the 3D canvas maintain high framerates (60 FPS)?
**Answer:**
- **Geometry Instancing:** Repeated objects (chairs, desks, corridor lights) use `THREE.InstancedMesh`, reducing draw calls from hundreds to one.
- **Frustum Culling:** Three.js automatically skips rendering objects outside the active camera viewing frustum.
- **Low-Polygon Modeling:** Building volumes use clean box and cylinder primitives rather than bloated high-polygon CAD imports.

#### Q72: How are room click events captured in the 3D scene?
**Answer:** Through **Raycasting** (`THREE.Raycaster`):
1. Mouse click $(x, y)$ screen coordinates are normalized to $[-1, +1]$ NDC space.
2. A ray is projected from the camera through the mouse coordinates into the 3D world.
3. `raycaster.intersectObjects(selectableRooms)` detects intersected meshes.
4. The clicked room's ID is extracted from mesh metadata and dispatched to the Streamlit parent window.

#### Q73: What is the purpose of the 3D compass and orientation HUD?
**Answer:** A canvas-based Heads-Up Display (HUD) overlay shows an interactive 3D compass rosette in the upper-right corner. It dynamically rotates with the camera's azimuth angle, providing instant cardinal orientation (North, South, East, West) to prevent spatial disorientation.

---

## SECTION H: DEPLOYMENT, DOCKER & DEVOPS

#### Q74: Why is containerization using Docker advantageous for this project?
**Answer:** Docker packages the application code, Python runtime, system libraries, configuration files, and assets into an immutable container image. This guarantees that the software runs identically across development laptops, university presentation machines, Linux servers, and cloud instances ("works on my machine" is completely eliminated).

#### Q75: Explain the multi-container Docker Compose topology.
**Answer:** `docker-compose.yml` orchestrates two coordinated services on a private bridge network (`campus_net`):
1. `app`: Streamlit Python application executing on internal port 8501.
2. `nginx`: Nginx reverse proxy listening on external ports 80/443, handling client traffic, SSL termination, and proxying requests to `app:8501`.
3. Persistent volume `campus_data_vol`: Mounts the SQLite database file and backup directory outside the container filesystem.

#### Q76: What is the role of the Nginx reverse proxy?
**Answer:**
- **Security:** Hides backend server topology and prevents direct exposure of the application server.
- **SSL/TLS Termination:** Offloads cryptographic encryption from Python.
- **WebSocket Proxying:** Maintains stable persistent bidirectional WebSocket connections required by Streamlit (`Upgrade $http_upgrade;`).
- **Static File Caching & Gzip Compression:** Compresses Three.js 3D assets and scripts, reducing initial page load times by up to 60%.

#### Q77: What instructions exist in the Dockerfile?
**Answer:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
HEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost:8501/_stcore/health || exit 1
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### Q78: Why is Docker volume mounting essential for the SQLite database?
**Answer:** Docker container filesystems are ephemeral: any data written inside a container is lost when the container stops or restarts. Mounting a persistent named volume (`campus_data_vol:/app/data`) maps the SQLite database to the host storage, ensuring users, obstacles, and audit records persist indefinitely across container upgrades.

#### Q79: How is the application health-checked?
**Answer:** Streamlit provides a dedicated internal health endpoint: `/_stcore/health`. The Docker container runs an automated healthcheck every 30 seconds. If the application server hangs or experiences an unrecoverable failure, Docker marks the container unhealthy and can automatically restart it.

#### Q80: How would you scale this application to serve 25,000 concurrent students?
**Answer:**
1. Migrate database from SQLite to a distributed PostgreSQL cluster with read-replicas.
2. Decouple the Streamlit frontend across multiple container replicas behind a load balancer (AWS ALB or Nginx round-robin).
3. Implement Redis for centralized session state and caching of precomputed shortest path pairs.
4. Host static 3D digital twin assets on a Global Content Delivery Network (CDN) like Cloudflare or AWS CloudFront.

#### Q81: What is the deployment script `deploy_campus_navigator.sh`?
**Answer:** An automated shell script that:
1. Validates prerequisites (Docker, Docker Compose, Git).
2. Pulls the latest commit from GitHub repository.
3. Executes automated test suite before deployment.
4. Backs up the live database.
5. Builds and launches the updated containers with zero downtime.

#### Q82: How does the application handle port collisions on localhost?
**Answer:** The startup script detects if port 8501 is occupied using socket probing. If busy, it prompts the operator or automatically binds to alternative port 8502 or 8503, updating the Nginx upstream proxy configuration dynamically.

#### Q83: What CI/CD pipeline would you configure for this repository?
**Answer:** A GitHub Actions workflow (`.github/workflows/ci.yml`) triggering on every push and pull request:
1. Spin up Ubuntu runner with Python 3.11.
2. Install dependencies via `pip install -r requirements.txt`.
3. Run `flake8` / `black` linting.
4. Execute full test suite: `pytest tests/`.
5. Build Docker image and verify healthcheck.

---

## SPECIAL SECTION 2: QUESTIONS FACULTY ASK ABOUT LIMITATIONS

#### Q84: "Does your system provide live real-time GPS tracking inside the building?"
**Answer (Honest Academic Response):**
> *"No, sir/ma'am. The current version does not feature real-time live indoor GPS positioning. Satellite GPS signals cannot penetrate multi-story concrete and steel reinforced buildings, resulting in location inaccuracies of 15 to 30 meters indoors.*
>
> *Instead, our system provides **deterministic algorithmic wayfinding**: users select their verified origin and destination, and the platform delivers sequential turn-by-turn guidance and 3D visual progress.*
>
> *In our future scope, real-time indoor positioning will be achieved using Bluetooth Low Energy (BLE) beacons or Wi-Fi RSSI fingerprinting mapped to our existing graph vertices."*

#### Q85: "What happens if a user's mobile device has no internet connectivity?"
**Answer:**
> *"Because the 3D twin runs in modern web browsers, once the page is initially loaded, the Three.js assets and client-side route geometries are cached in browser memory. However, dynamic obstacle synchronization and user authentication require network connectivity.*
>
> *As detailed in Chapter 13 of our project report, transitioning the frontend into a Progressive Web App (PWA) with Service Workers and an offline SQLite WebAssembly (Wasm) engine is our planned solution for complete offline campus autonomy."*

#### Q86: "Can a user forge or spam false obstacle reports to disrupt campus navigation?"
**Answer:**
> *"We specifically anticipated this vulnerability. Community obstacle reports do not immediately alter campus routing. When a student submits a hazard, it enters the database in a `pending` status. It has **zero effect** on Dijkstra edge weights until a campus administrator or faculty member reviews and verifies it in the Administrative Governance Panel.*
>
> *Additionally, every report logs the submitting user's ID, preventing anonymous spam and enabling administrative sanctions against abusive accounts."*

---

## SPECIAL SECTION 3: QUESTIONS FACULTY ASK ABOUT ALGORITHM SELECTION

#### Q87: "Why didn't you use the Floyd-Warshall algorithm instead of Dijkstra?"
**Answer:**
> *"Floyd-Warshall is an all-pairs shortest path algorithm with a cubic time complexity of $O(|V|^3)$ and space complexity of $O(|V|^2)$. For our 79-node graph, computing $79^3 = 493,039$ operations on every user query would be completely unnecessary and inefficient.*
>
> *Dijkstra's algorithm is a single-source shortest path algorithm that executes in $O((|E| + |V|) \log |V|)$—completing in under 2 milliseconds. Since users only request a path from one specific origin to one destination at a time, Dijkstra with a binary min-heap is vastly superior in both speed and memory efficiency."*

#### Q88: "Why did you implement BFS alongside Dijkstra? Isn't Dijkstra always better?"
**Answer:**
> *"Dijkstra is optimal for **physical distance**, but physical distance is not always the most intuitive route for humans. A route that is 10 meters shorter but involves 6 zigzag hallway turns is much more confusing to navigate than a straight corridor with only 1 turn.*
>
> *BFS treats every hallway edge uniformly, finding the route with the **minimum number of intermediate decision points (hops)**. Providing both algorithms allows the user to choose between 'Shortest Distance' and 'Simplest Route'."*

---

## SPECIAL SECTION 4: QUESTIONS FACULTY ASK ABOUT REAL-WORLD DEPLOYMENT

#### Q89: "How much would it cost to deploy this system across the entire university campus?"
**Answer:**
> *"Because our entire software stack is built on open-source technologies—Python, NetworkX, Three.js, SQLite, Linux, Docker, and Nginx—the software licensing cost is **zero rupees**.*
>
> *To deploy it for the entire student body, the university would only require:*
> *1. A standard Linux cloud VPS or on-premise university server (approx. ₹1,500 – ₹3,000 per month).*
> *2. QR code stickers placed on classroom doors and entrance pillars (costing under ₹1,000).*
> *3. Physical touch-screen kiosk tablets at main building foyers (optional, approx. ₹15,000 each).*
>
> *It represents an exceptionally high return on investment for campus infrastructure and disability compliance."*

#### Q90: "How easy is it to add a new building or modify a floor plan when the campus expands?"
**Answer:**
> *"The system is architected for modular spatial extensibility. Adding a new building or renovating a floor does not require rewriting the routing algorithms or database schemas.*
>
> *An administrator simply updates the graph definition in `campus_data.py` (or through the administrative data import wizard), defining the new node coordinates, room names, and edge connections. The routing engine, accessibility filter, and 3D digital twin automatically ingest the updated topology upon reloading."*

---

## FINAL VIVA DEFENSE TIPS FOR RUDRA PRATAP

1. **Own Your Technical Decisions:** Never say *"The library did it for me."* Say: *"I selected NetworkX because its adjacency structure allows $O(1)$ neighbor lookup, and I implemented binary min-heap relaxation to guarantee $O((E+V)\log V)$ performance."*
2. **Highlight Accessibility Social Impact:** Remind the committee that accessible navigation is not just a coding exercise—it is a legal mandate under the RPwD Act 2016 and a profound equalizer for students with physical disabilities.
3. **Reference the Verified Test Baseline:** When asked about reliability, point directly to the **190 passing automated tests** in `tests/`, proving that edge cases have been exhaustively tested.
4. **Maintain Calm, Confident Demeanor:** Speak clearly, make eye contact with all committee members, and stand proud of your comprehensive B.Tech engineering achievement.
