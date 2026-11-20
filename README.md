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
- **Authentication, Role-Based Access Control (RBAC) & Administration (Phase 9):**
  - Cryptographically salted PBKDF2-HMAC-SHA256 password hashing (100,000 iterations) with constant-time verification.
  - Three distinct user roles: **Student / Campus User**, **Field Staff**, and **Administrator**.
  - Service-layer backend RBAC enforcement preventing unauthorized barrier verification or user privilege escalation.
  - Dynamic role-aware navigation and sidebar session management.
  - One-time initial setup mechanism for bootstrapping the primary Administrator account.
  - Comprehensive Administrative Management Console with user directory, role/status assignment, and obstacle verification queue.
  - Immutable administrative audit logging for all critical operations and obstacle status transitions.
  - Duplicate obstacle detection warnings alerting users when existing reports already affect selected pathways.

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

### SQLite Database Schema

```sql
-- Obstacle & Barrier Reports
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

-- Registered User Accounts
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    full_name TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('Student', 'Field Staff', 'Administrator')),
    account_status TEXT NOT NULL CHECK(account_status IN ('Active', 'Inactive')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Administrative & Operational Audit Trail
CREATE TABLE IF NOT EXISTS administrative_audit_log (
    audit_id TEXT PRIMARY KEY,
    actor_user_id TEXT NOT NULL,
    action TEXT NOT NULL,
    target_type TEXT NOT NULL CHECK(target_type IN ('obstacle_report', 'user_account', 'system')),
    target_id TEXT NOT NULL,
    previous_status TEXT,
    new_status TEXT,
    timestamp TEXT NOT NULL,
    notes TEXT
);

-- Brute-Force Rate Limiting & Account Lockout
CREATE TABLE IF NOT EXISTS login_rate_limits (
    username TEXT NOT NULL,
    attempt_time REAL NOT NULL
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_obstacle_status ON obstacle_reports (status);
CREATE INDEX IF NOT EXISTS idx_obstacle_location ON obstacle_reports (location_id);
CREATE INDEX IF NOT EXISTS idx_obstacle_pathway ON obstacle_reports (source_location_id, destination_location_id);
CREATE INDEX IF NOT EXISTS idx_obstacle_reported_at ON obstacle_reports (reported_at);
CREATE INDEX IF NOT EXISTS idx_users_username ON users (username);
CREATE INDEX IF NOT EXISTS idx_users_role ON users (role);
CREATE INDEX IF NOT EXISTS idx_users_status ON users (account_status);
CREATE INDEX IF NOT EXISTS idx_audit_actor ON administrative_audit_log (actor_user_id);
CREATE INDEX IF NOT EXISTS idx_audit_action ON administrative_audit_log (action);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON administrative_audit_log (timestamp);
CREATE INDEX IF NOT EXISTS idx_rate_limit_user ON login_rate_limits (username, attempt_time);
```

### Report Verification Workflow & Lifecycle

1. **Submission (`Pending`):**
   - User submits an obstacle report. Initial status is `Pending`. Pending reports **do not automatically block pathways**.
   - The engine checks for duplicate or concurrent reports affecting the same location or connection and displays a warning notice.
2. **Field Staff / Administrator Verification (`Verified`):**
   - Authorized personnel review the pending queue and confirm the report. Status transitions to `Verified`.
   - `ObstacleManager` applies a temporary `blocked` status to the affected live graph edge/node.
   - Dijkstra and BFS automatically detour around the blocked segment.
   - The map dynamically highlights the connection in dashed red (`#e63946`).
   - Every verification records an audit trail record in `administrative_audit_log`.
3. **Resolution (`Resolved`):**
   - Field staff log mandatory resolution notes detailing maintenance.
   - Pathway is restored to original operational status (`open`).
4. **Rejection (`Rejected`):**
   - Unsubstantiated reports are marked `Rejected` with a documented reason without affecting pathway availability.

---

## 🔒 Authentication, Roles & RBAC Architecture

The application enforces a multi-tier Role-Based Access Control (RBAC) model implemented with backend service-layer validation and cryptographically salted password hashing.

### User Roles & Permissions Matrix

| Capability / Action | Student / Campus User | Field Staff | Administrator |
|:---|:---:|:---:|:---:|
| **Browse Dashboard & Campus Map** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Calculate Accessible Routes (Dijkstra/BFS)** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Inspect Accessibility Classifications** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Submit Obstacle & Hazard Reports** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Track Report Status & View Own Reports** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Inspect Field Staff Verification Queue** | ❌ No | ✅ Yes | ✅ Yes |
| **Verify Reports & Block Routes** | ❌ No | ✅ Yes | ✅ Yes |
| **Reject Reports with Documented Reason** | ❌ No | ✅ Yes | ✅ Yes |
| **Resolve Verified Obstacles (Mandatory Notes)** | ❌ No | ✅ Yes | ✅ Yes |
| **Access Administrative Console** | ❌ No | ❌ No | ✅ Yes |
| **Provision Field Staff / Admin Accounts** | ❌ No | ❌ No | ✅ Yes |
| **Modify User Roles & Activate/Deactivate** | ❌ No | ❌ No | ✅ Yes |
| **Inspect Administrative Audit Log** | ❌ No | ❌ No | ✅ Yes |

### Password Security & Cryptography

- **Algorithm:** PBKDF2 with HMAC-SHA256 (`hashlib.pbkdf2_hmac`).
- **Work Factor & Iterations:** **600,000 hashing rounds** conforming to modern OWASP Password Storage Guidelines (upgraded from 100,000).
- **Progressive Zero-Downtime Upgrade:** Existing accounts stored with legacy iterations are automatically verified and progressively upgraded to 600,000 rounds upon their next successful sign-in.
- **Salting:** Cryptographically secure 16-byte random salt generated per user via `secrets.token_hex(16)`, stored in modern `<iterations>$<salt_hex>` format.
- **Verification:** Constant-time hash comparison (`hmac.compare_digest`) preventing timing side-channel attacks.
- **Brute-Force Rate Limiting:** Consecutive failed login attempts are tracked per account. Exceeding 5 failed attempts activates an automated 5-minute (300-second) lockout window, logging a `SECURITY_LOCKOUT` audit event. Successful authentication automatically resets the lockout counter.
- **Password Complexity Policy:** Passwords must be at least 8 characters long and contain both alphabetic characters and numerical digits.
- **Session Cleanup:** The `logout_user()` mechanism completely purges authentication state and removes any transient session cache keys.
- **Sanitization:** Password hashes and salts are completely stripped from query results before reaching UI components or session state.
- **Append-Only Audit Immutability:** The administrative audit log is strictly append-only; no application methods or interface actions permit altering or deleting historical audit records.

### One-Time Initial Administrator Setup

To eliminate insecure hardcoded credentials, the system features a one-time bootstrap mechanism:
1. **Interactive Bootstrap UI:** If the database contains zero active Administrator accounts, navigating to the **Account & Sign In** page presents the **Primary Administrator Initialization** prompt to establish the lead administrator.
2. **Environment Variable Bootstrap:** Alternatively, administrators can define `CAMPUS_ADMIN_USERNAME` and `CAMPUS_ADMIN_PASSWORD` in the execution environment, allowing headless automated provisioning during initial setup.
3. Once initialized, self-registration of Administrator accounts is permanently disabled.

### Backend Defense-in-Depth Enforcement

UI navigation restrictions and button hiding are accompanied by mandatory validation in backend domain managers (`ObstacleManager`, `DatabaseManager`):
- Attempting to verify, reject, or resolve obstacle reports without `Field Staff` or `Administrator` authority raises `PermissionError`.
- Attempting to update user roles or account activation without `Administrator` authority raises `PermissionError`.
- Self-demotion safeguards prevent the last remaining active Administrator from demoting or deactivating their own account.

> [!NOTE]
> **Security Notice:** This prototype demonstrates robust application-level access controls and PBKDF2 password hashing. It is designed for educational, research, and campus-scale prototype deployment. Enterprise deployment would benefit from additional network-level TLS enforcement and multi-factor authentication (MFA).

---

## 🛠️ Technology Stack

- **Core Programming Language:** Python 3.14
- **Web Interface:** Streamlit (v1.67.0)
- **Graph & Network Algorithms:** NetworkX, Custom Dijkstra & BFS implementations
- **Mapping & Geospatial Visualization:** Plotly, Folium, streamlit-folium
- **Data Processing & Manipulation:** Pandas
- **Database & Storage:** SQLite3, JSON Data Schemas
- **Security & Authentication:** Standard Library `hashlib`, `hmac`, `secrets` (Zero external dependencies)

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
│   ├── obstacle_manager.py     # Obstacle lifecycle, RBAC checks & dynamic detour management
│   ├── indoor_map.py           # Indoor map engine, floor filters & visualizer
│   └── ui_theme.py             # Shared styling, session services & user authentication
│
├── database/                   # Persistent data management
│   ├── __init__.py
│   └── db_manager.py           # SQLite connection, RBAC user schemas, audit log & parameterized queries
│
├── data/                       # Static graph & spatial datasets
│   └── campus_map.json         # Campus nodes, edges, coordinates, and attributes
│
├── pages/                      # Streamlit multi-page interface views
│   ├── dashboard.py            # Overview & statistics dashboard
│   ├── navigation.py           # Route query & turn-by-turn guidance page
│   ├── campus_map.py           # Interactive indoor campus map & route visualizer
│   ├── accessibility.py        # Accessibility profiles & amenity directory
│   ├── obstacle_reports.py     # Hazard reporting, duplicate warnings & field staff queue
│   ├── login.py                # User authentication, registration & admin bootstrap
│   └── admin_management.py     # Administrative console: users, roles, queue & audit logs
│
├── assets/                     # Media, icons, and styling stylesheets
│   └── .gitkeep
│
├── scripts/                    # Demonstration & operational utilities
│   └── demo_setup.py           # Idempotent demo credentials initialization script
│
├── tests/                      # Automated unit & integration test suites
│   ├── __init__.py
│   ├── test_campus_map.py      # Campus map parsing and data validation tests
│   ├── test_bfs.py             # BFS routing and hop-count optimality tests
│   ├── test_dijkstra.py        # Dijkstra distance/time optimization tests
│   ├── test_route_finder.py    # Multi-modal routing & alternative route tests
│   ├── test_accessibility.py   # Accessibility engine & heuristic scoring tests
│   ├── test_obstacle_manager.py# Obstacle lifecycle, SQLite, and detour tests
│   ├── test_indoor_map.py      # Floor filtering, cross-floor transit & visualizer tests
│   ├── test_auth_rbac.py       # Authentication, PBKDF2 hashing, RBAC & audit tests
│   ├── test_security_audit.py  # Security audit, progressive re-hash, lockout & end-to-end integration tests
│   └── test_demo_workflow.py   # 8-step complete academic demonstration workflow verification
```

---

## 🧪 Running Automated Tests

All test suites use isolated in-memory or temporary databases to prevent altering the application database. The full regression suite consists of **82 automated tests** across 10 test suites:

```powershell
& ".venv\Scripts\python.exe" -m unittest discover tests -v
```

To run individual test suites:
```powershell
& ".venv\Scripts\python.exe" -m unittest tests/test_demo_workflow.py -v
& ".venv\Scripts\python.exe" -m unittest tests/test_security_audit.py -v
& ".venv\Scripts\python.exe" -m unittest tests/test_auth_rbac.py -v
& ".venv\Scripts\python.exe" -m unittest tests/test_indoor_map.py -v
& ".venv\Scripts\python.exe" -m unittest tests/test_obstacle_manager.py -v
& ".venv\Scripts\python.exe" -m unittest tests/test_route_finder.py -v
```

---

## 🎓 Academic Demonstration Guide (8-Step Live Walkthrough)

To support seamless project presentations and live academic evaluation, the system includes pre-configured, labeled demonstration credentials and an end-to-end operational script.

### Pre-Configured Demonstration Accounts

Run the idempotent setup script to ensure all demonstration credentials exist with active status:
```powershell
& ".venv\Scripts\python.exe" scripts/demo_setup.py
```

| Role | Username | Password | Intended Workflow |
|:---|:---|:---|:---|
| **Student / Campus User** | `demo_student` | `DemoStudent2026!` | Explore map, calculate routes, submit field obstacle reports. |
| **Field Staff** | `demo_staff` | `DemoStaff2026!` | Review pending report queue, verify hazards (auto-block), resolve with notes. |
| **Administrator** | `demo_admin` | `DemoAdmin2026!` | User management, role elevation/demotion, inspect immutable audit trail. |

---

### Step-by-Step Live Demonstration Script

1. **Step 1: Campus Dashboard & Metric Overview**
   - Navigate to **Dashboard**. Observe real-time KPI cards reflecting actual graph nodes (15), connections (17), and current database obstacle metrics.
   - Point out the Plotly charts showcasing pathway classifications and current obstacle status.

2. **Step 2: Cross-Floor Accessible Route Planning**
   - Navigate to **Find Accessible Route**.
   - Select Origin: `LOC_01 (Main Campus Entrance, Floor 0)` and Destination: `LOC_14 (Faculty Office Suite, Floor 1)`.
   - Select **Dijkstra** algorithm optimized for **Distance**, with **Wheelchair Accessible** enabled.
   - Point out how the route avoids vertical stairs (`LOC_05 -> LOC_11`) and safely routes via the elevator (`LOC_04 -> LOC_10`), achieving a *Fully Accessible* classification score.

3. **Step 3: Multi-Floor Interactive Campus Map Exploration**
   - Navigate to **Campus Map**.
   - Toggle between **Ground Floor (Floor 0)**, **First Floor (Floor 1)**, and **All Floors (Architectural Overview)**.
   - Show how the planned route overlays in gold with start pin, destination flag, and automated elevator transfer instructions.

4. **Step 4: Field Obstacle Reporting (as Student)**
   - Sign in via **Account & Sign In** using `demo_student` / `DemoStudent2026!`.
   - Navigate to **Obstacle Reports**.
   - Expand **Report an Obstacle or Accessibility Issue**.
   - Report a barrier on pathway `Main Campus Entrance (LOC_01)` to `Central Reception & Info Desk (LOC_02)`, category `Blocked pathway`, severity `High`.
   - Submit report. Confirm initial status is `Pending` and pathway remains open on the graph until verified.

5. **Step 5: Inspection & Verification (as Field Staff)**
   - Sign out and sign in using `demo_staff` / `DemoStaff2026!`.
   - Navigate to **Obstacle Reports**. Observe the newly visible **Field Staff Verification Queue**.
   - Click **Verify & Block Route**. The report transitions to `Verified`, and the edge is dynamically blocked in the live navigation graph.

6. **Step 6: Dynamic Route Avoidance Verification**
   - Navigate back to **Find Accessible Route**.
   - Attempt routing between `LOC_01` and `LOC_02`.
   - Observe that the navigation engine detects the active obstruction and avoids the blocked corridor.

7. **Step 7: Maintenance Resolution & Route Restoration**
   - Return to **Obstacle Reports** as Field Staff.
   - Enter mandatory resolution notes: *"Barricades removed; flooring cleared for pedestrian use."*
   - Click **Resolve & Clear Obstacle**.
   - Confirm status transitions to `Resolved` and the pathway immediately returns to `open` status.

8. **Step 8: Administrative Governance & Audit Trail Verification**
   - Sign out and sign in using `demo_admin` / `DemoAdmin2026!`.
   - Open the **Admin Console** (accessible exclusively to administrators).
   - Review user account statuses, role assignments, and the immutable **Administrative Audit Log** documenting every user creation, verification, and resolution event.

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

3. **Seed Demonstration Accounts:**
   ```powershell
   & ".venv\Scripts\python.exe" scripts/demo_setup.py
   ```

4. **Launch the Streamlit Web Application:**
   ```powershell
   & ".venv\Scripts\python.exe" -m streamlit run main.py
   ```
   Open your browser to [http://localhost:8501](http://localhost:8501) to explore the interface.
