# Accessible Campus Navigator — Final Project Overview

**Institution:** Faculty of Engineering and Technology (FET) — JAIN (Deemed-to-be University)  
**Campus Location:** JAIN Global Campus, Jakkasandra Post, Kanakapura Road, Ramanagara District, Karnataka, India — 562112  
**Coordinates:** `12.6508° N, 77.4428° E`  
**Current Milestone:** Phase 23: Final Release Validation & Demonstration Handover  
**Repository:** [https://github.com/rudrapratap17003-coder/Campus-navigation](https://github.com/rudrapratap17003-coder/Campus-navigation)  
**Demonstration Endpoint:** `http://localhost:8501` (Local Demonstration Host)  

---

## 1. Project Abstract & Mission

The **Accessible Campus Navigator** is an enterprise-grade, accessibility-first 3D digital twin and multi-modal wayfinding system engineered for modern multi-story academic institutions. Built to address the pervasive navigation barriers experienced by persons with disabilities, mobility-impaired individuals, elderly visitors, and first-time students, the platform transforms complex 3D campus infrastructure into an intuitive, accessible, and dynamically responsive navigation experience.

The system features a high-fidelity WebGL 3D reconstruction of the 300-acre **JAIN Global Campus** and all 5 physical floors of the octagonal **Faculty of Engineering and Technology (FET)** building. Leveraging rigorous graph theory (Dijkstra and Breadth-First Search), real-time SQLite obstacle synchronization, continuous heuristic accessibility scoring (0–100), and multilingual internationalization (English, Kannada, Hindi), the platform guarantees safe, step-free transit routes that completely bypass architectural barriers.

---

## 2. Technical Stack & Architectural Overview

```
                                  ┌────────────────────────────────────────────────────────┐
                                  │            Client Presentation Layer                   │
                                  │  • Three.js WebGL (Interactive 3D Digital Twin)        │
                                  │  • Streamlit 1.67.0 UI (Dark Green Glassmorphism)      │
                                  │  • Plotly 7.1.0 (Interactive Telemetry Charts)         │
                                  │  • i18n Localization (English, Kannada, Hindi)         │
                                  └───────────────────────────┬────────────────────────────┘
                                                              │
                                                              ▼
                                  ┌────────────────────────────────────────────────────────┐
                                  │           Application & Intelligence Layer             │
                                  │  • RouteFinder: Dijkstra & BFS Algorithms              │
                                  │  • AccessibilityEngine: Heuristic Barrier Classifier   │
                                  │  • DestinationSearch: Keyword & Semantic Relevance     │
                                  │  • ObstacleManager: Dynamic Lifecycle & In-Graph Block │
                                  │  • CampusAnalytics: Operational KPI Calculations       │
                                  └───────────────────────────┬────────────────────────────┘
                                                              │
                                                              ▼
                                  ┌────────────────────────────────────────────────────────┐
                                  │              Data & Persistence Layer                  │
                                  │  • NetworkX 3.7 (79 Locations, 106 Spatial Pathways)   │
                                  │  • SQLite 3.x (WAL Mode, 5s Timeout, Point-in-Time Bak)│
                                  │  • Role-Based Access Control (PBKDF2-HMAC-SHA256)      │
                                  │  • PostgresMigration: Enterprise Database Exporter     │
                                  └────────────────────────────────────────────────────────┘
```

| Layer | Technologies Used | Primary Responsibilities |
| :--- | :--- | :--- |
| **Front-End & 3D Engine** | Three.js WebGL, Streamlit 1.67, HTML5 Canvas, CSS3 Glassmorphism | Real-time 3D canvas, orbit camera, room inspector, floor isolation, multi-page routing. |
| **Routing & Graph Core** | Python 3.11, NetworkX 3.7, Custom Dijkstra & BFS implementations | Mathematical pathfinding, step-free constraint filtering, dynamic detours, turn instructions. |
| **Database & Security** | SQLite3 (WAL mode), PBKDF2-HMAC-SHA256 (600,000 iterations) | User management, RBAC authorization, hazard reports queue, navigation telemetry, audit trails. |
| **Deployment & Ops** | Docker (python:3.11-slim, non-root `appuser`), Docker Compose, Nginx | Multi-stage containerization, persistent volume mounts, WebSocket reverse proxying. |

---

## 3. Core System Highlights

### A. 3D Digital Twin & Procedural Architecture
- **Complete Campus Outdoor Model:** 300-acre JAIN Global Campus including the octagonal FET Building Complex, Colosseum Arena with colonnade pillars, JIRS Aquatic Center with 50m Olympic pool, International Cricket Stadium with running track, SBMJCE Dining Complex, student hostels, administrative block, aerospace hangar, and arterial roads.
- **Five-Floor FET Architectural Model:** Precise multi-floor reconstruction modeling all 5 physical levels (Ground Floor L0, First Floor L1, Second Floor L2, Third Floor L3, Fourth Floor L4). Includes exterior curtain wall glazing, structural mullions, ADA west access ramp with handrails, central amphitheater, and 4 cardinal fire stairwells.
- **Mathematical Vertical Invariant Proof:** Formally verified zero horizontal displacement ($0.00\text{ m}$ shear) for the central wheelchair elevator core at $(-6.0, 18.0)$ across Floors 0, 1, 2, 3, and 4.
- **5-Floor Exploded View:** Instant separation of floor slabs along vertical guide rods for comprehensive building layout comprehension.
- **Procedural Interior Detailing:** Workstations, dual monitors, science and electronics benches with oscilloscopes, library stack rows, tiered auditorium seating, and supercomputing server clusters with pulsating activity LEDs.

### B. Inclusive Wayfinding & Accessibility Engine
- **79 Locations & 106 Pathways:** Unified campus graph connecting outdoor gateways directly to indoor research laboratories.
- **Wheelchair Invariant Guarantee:** Accessible routing mode strictly excludes all 18 staircase pathways, routing exclusively via ramps and the central elevator core.
- **Turn-by-Turn Instruction Engine:** Geometric cross-product vector calculations yielding human-readable guidance (`continue straight`, `turn left`, `turn right`, `take elevator to Floor X`).
- **Real-Time Compass Bearings:** Azimuth orientation ($0^\circ - 360^\circ$ from campus grid North) and 8-cardinal directional cues.
- **Dynamic Obstacle Avoidance:** Verified hazards in SQLite immediately update the NetworkX graph and trigger automatic in-transit rerouting.

### C. Multilingual & Universal Accessibility
- **Multilingual Support:** Instant localization across **English (`en`)**, **Kannada (`kn`)**, and **Hindi (`hi`)**.
- **WCAG AAA High-Contrast Mode:** High-contrast color scheme for visually impaired users.
- **Reduced-Motion Mode:** Disables CSS and WebGL animations for users with vestibular sensitivities.
- **Personalized Bookmarks & Routes:** Account-isolated bookmarking for saved rooms and favorite route setups.
- **Community Feedback Pipeline:** Structured incident and feedback collection with administrative resolution tracking.

### D. Security & Production Architecture
- **Cryptographic Security:** PBKDF2-HMAC-SHA256 hashing upgraded to 600,000 rounds with progressive legacy rehash.
- **Brute-Force Rate Limiting:** Automatic account lockout after 5 consecutive failed login attempts.
- **Backend RBAC:** Strict enforcement across `Student`, `Field Staff`, and `Administrator` roles.
- **Immutable Audit Logging:** Every user role update, obstacle verification, and resolution writes an immutable record.
- **Data Protection:** Parameterized SQL queries preventing SQL injection; `SensitiveDataFilter` scrubbing credentials from logs.

---

## 4. Multi-Floor FET Building Spatial Map

| Level | Elevation | Key Facilities & Specialized Wings | Connectors |
| :--- | :--- | :--- | :--- |
| **Ground Floor (L0)** | $0.0\text{ m}$ | Main Entrance Portico, Central Amphitheater, Civil Lab, Workshop, West ADA Ramp, Admin Suites | Elevator `(-6.0, 18.0)`, North/East/South/West Stairs |
| **First Floor (L1)** | $3.5\text{ m}$ | Electronics & Comm Labs, Microprocessor Lab, Smart Classrooms, Faculty Office Suites | Elevator `(-6.0, 18.0)`, North/East/South/West Stairs |
| **Second Floor (L2)** | $7.0\text{ m}$ | Computer Science & AI Labs, HPC Supercomputer Cluster, Data Science Lab, Server Room | Elevator `(-6.0, 18.0)`, North/East/South/West Stairs |
| **Third Floor (L3)** | $10.5\text{ m}$ | Mechanical CAD Lab, Robotics & Automation Wing, Mechatronics Research Centre | Elevator `(-6.0, 18.0)`, North/East/South/West Stairs |
| **Fourth Floor (L4)** | $14.0\text{ m}$ | Central Library & Stacks, Digital Learning Center, Ramanujan Conference Hall, Terrace | Elevator `(-6.0, 18.0)`, North/East/South/West Stairs |

---

## 5. Demonstration Credentials & RBAC Matrix

| Role | Username | Password | Demonstration Scope |
| :--- | :--- | :--- | :--- |
| **Student / Visitor** | `demo_student` | `DemoStudent2026!` | Explore 3D map, search rooms, plan accessible routes, bookmark places, submit obstacle reports and feedback. |
| **Field Staff** | `demo_staff` | `DemoStaff2026!` | Access staff verification queue, inspect pending hazard reports, verify obstacles (auto-block graph), resolve with notes. |
| **Administrator** | `demo_admin` | `DemoAdmin2026!` | System-wide administrative governance, user directory management, audit trail inspection, data reliability updates. |

---

## 6. Verification and Test Results

```
======================================================================
Ran 190 tests in 47.011s
OK (failures=0, errors=0, skipped=0)
======================================================================
```
- **190 Automated Tests:** 100% test pass rate across 20 test modules covering routing algorithms, graph connectivity, 3D data serialization, database migrations, security, and deployment specifications.
- **Zero Python Syntax Errors:** Bytecode compilation verified across all modules, pages, and scripts.
- **Verified Zero Shear Invariant:** Elevator core mathematically proven invariant across all 5 physical tiers.

---

## 7. Operational Notices & Compliance Disclaimers

1. **Local Demonstration Status:** The address `http://localhost:8501` is a local demonstration host and does not represent a live public deployment.
2. **Algorithmic Heuristic Advisory:** The 0–100 accessibility scoring system is a heuristic routing metric designed for comparative navigation and barrier freedom; it does not constitute an official statutory building compliance certificate.
3. **Illustrative Coordinates:** The spatial coordinates are designed for schematic topological routing and 3D digital twin visualization based on architectural evacuation drawings.
