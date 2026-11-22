# Accessible Campus Navigator — JAIN Global Campus & FET 3D Digital Twin

[![Build Status](https://img.shields.io/badge/Build-Passing-16A36A.svg)](#-test-suite-and-quality-assurance)
[![Test Suite](https://img.shields.io/badge/Tests-190%20Passed-16A36A.svg)](#-test-suite-and-quality-assurance)
[![Python Version](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.14-35D99A.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.67.0-FF4B4B.svg)](https://streamlit.io)
[![Three.js](https://img.shields.io/badge/Three.js-WebGL%203D-049EF4.svg)](https://threejs.org)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](#)

A high-performance, accessible 3D digital twin and real-time wayfinding platform for the **JAIN Global Campus** (300-acre university campus on Kanakapura Road, Karnataka, India) and its flagship **Faculty of Engineering and Technology (FET)** building.

Engineered specifically to empower students, visitors, and individuals with mobility challenges (wheelchair users, elderly visitors, and ambulatory impairments) to navigate complex multi-floor university environments safely, independently, and efficiently.

---

## 🏛️ Campus Overview & Physical Setting

- **Campus Reference:** JAIN Global Campus, Jakkasandra Post, Kanakapura Taluk, Ramanagara District, Karnataka, India — 562112
- **Coordinate Reference:** `12.6508° N, 77.4428° E` (Kanakapura Road / NH-948)
- **Topological Graph:** **79 Verified Campus Locations** and **106 Pathways**
- **Indoor Environment:** **5 Physical Floors** of the FET Building (Ground Level 0, First Level 1, Second Level 2, Third Level 3, Fourth Level 4)
- **Vertical Infrastructure:** Continuous central wheelchair-accessible elevator core and 4 cardinal fire stairwells (North, East, South, West)
- **Outdoor Environment:** Octagonal FET Complex, Central Amphitheater, Colosseum Arena, JIRS Olympic Aquatic Center, International Cricket Stadium & Running Track, Aerospace Hangars, Student Hostels, Dining Complex, and Administrative Headquarters.

---

## ✨ System Capabilities & Milestone Architecture

```
                          ┌─────────────────────────────────────┐
                          │     Streamlit 1.67.0 Web UI         │
                          │   (Dark Green Glassmorphism)        │
                          └──────────────────┬──────────────────┘
                                             │
             ┌───────────────────────────────┼───────────────────────────────┐
             ▼                               ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────┐     ┌─────────────────────────┐
│   3D Digital Twin       │     │   Navigation & Routing  │     │  Accessibility Engine   │
│   (Three.js WebGL)      │     │  (Dijkstra, BFS, Detour)│     │  (0-100 Heuristic Score)│
│ • Outdoor 300-acre map  │     │ • Multi-Route Tradeoffs │     │ • Step-free classification│
│ • 5-Floor FET Building  │     │ • Turn-by-Turn Guidance │     │ • Wheelchair invariants │
│ • Exploded & Cutaway    │     │ • Real-time avatar sync │     │ • Dynamic hazard alerts │
└────────────┬────────────┘     └────────────┬────────────┘     └────────────┬────────────┘
             │                               │                               │
             └───────────────────────────────┼───────────────────────────────┘
                                             ▼
                               ┌───────────────────────────┐
                               │     Service & Data Layer  │
                               │  (NetworkX Graph Engine)  │
                               └─────────────┬─────────────┘
                                             │
                      ┌──────────────────────┴──────────────────────┐
                      ▼                                             ▼
        ┌───────────────────────────┐                 ┌───────────────────────────┐
        │   SQLite WAL Database     │                 │   Configuration & Logs    │
        │ • Role-Based Access Control│                │ • AppConfig (.env)        │
        │ • Obstacle Reports Queue  │                 │ • SensitiveDataFilter     │
        │ • Navigation History      │                 │ • Automated Backups       │
        │ • Saved Places & Feedback │                 │ • Docker & Nginx Proxy    │
        └───────────────────────────┘                 └───────────────────────────┘
```

### 1. 3D Digital Twin & Procedural Architecture (Phases 12 & 13)
- **Three.js WebGL Rendering Engine:** Realistic 3D canvas with shadow-casting directional sunlight, ambient fill lights, fog depth, and antialiased graphics.
- **Architectural Faithfulness:** Faithful representation of the octagonal FET building complex derived from official satellite imagery and architectural floor plans.
- **Five-Floor Vertical Exploration:** Instant toggle between individual floor slices (Levels 0–4), Stacked view, and **5-Floor Exploded View** with emerald vertical alignment guide rods.
- **Procedural Interior Detailing:** Detailed computer science workstation arrays, electronics lab oscilloscopes, library stack rows, tiered auditorium desks, supercomputer server clusters with pulsating LEDs, and executive suites.
- **Interactive Facility Inspector:** Real-time HUD detailing metadata, floor, department, step-free access status, and **"🎯 Focus on Room"** camera animation.

### 2. Intelligent Routing & Wayfinding (Phases 14, 15 & 16)
- **Authoritative Graph Engine:** NetworkX-backed campus graph computing Dijkstra (Shortest Distance), Breadth-First Search (Fewest Step Turns), and Alternative Detours.
- **Strict Wheelchair Accessibility:** ♿ Wheelchair toggle strictly enforces step-free paths, excluding all 18 staircase pathways and routing via the central elevator core or ADA-compliant ramps.
- **Turn-by-Turn Instruction Engine:** Geometric cross-product analysis yielding natural instructions (`continue straight`, `turn left`, `turn right`, `take elevator to Floor X`, `enter building`, `exit building`).
- **Compass & Directional Orientation:** True compass bearings ($0^\circ - 360^\circ$) and 8 cardinal quadrants (N, NE, E, SE, S, SW, W, NW) integrated with statutory navigation disclosures.
- **Dynamic Obstacle Synchronization:** Live synchronization with SQLite hazard reports; verified obstacles display as glowing crimson red barriers and trigger automatic in-transit rerouting.

### 3. Production Architecture & Robustness (Phase 17)
- **Hierarchical Configuration (`config.py`):** Environment-driven settings with `AppConfig`, `DatabaseConfig`, `SecurityConfig`, `MapConfig`, and `LoggingConfig`.
- **Domain Exception Hierarchy (`modules/exceptions.py`):** Structured domain exceptions (`AuthenticationError`, `PermissionDeniedError`, `RouteNotFoundError`, `ObstacleConflictError`).
- **Data Protection & Masking (`modules/logging_config.py`):** Structured logging featuring `SensitiveDataFilter` to scrub passwords, salts, and secret tokens.
- **Database Hardening (`database/db_manager.py`):** SQLite WAL (Write-Ahead Logging) mode, 5000ms busy timeout, automated point-in-time snapshotting, and `user_version` schema management.
- **Enterprise Postgres Ready (`database/postgres_migration.py`):** Standalone migration pipeline with PostgreSQL DDL and JSON/CSV data export.

### 4. Inclusive UX & Intelligent Services (Phase 18)
- **Multilingual Internationalization (`modules/i18n.py`):** Native language selection supporting **English (`en`)**, **Kannada (`kn`)**, and **Hindi (`hi`)**, including dynamic translation of directional instructions.
- **High-Contrast & Reduced-Motion Modes:** Instant CSS theme injection ensuring WCAG AAA accessibility for visually impaired users and reduced animation for vestibular sensitivity.
- **Personalized Bookmarks & Routes:** Securely saves favorite campus rooms and customized transit routes per authenticated user account.
- **Community Feedback Pipeline:** User feedback collection across accessibility, routing, map clarity, and facility reports with administrative resolution workflows.

### 5. Advanced Campus Intelligence & Analytics (Phase 19)
- **Dual-Dataset Intelligence Engine (`modules/campus_analytics.py`):** High-level comparative analytics between the full JAIN Global Campus (79 nodes) and the Benchmark Model (15 nodes).
- **Executive KPI Dashboard:** Real-time metrics tracking Step-Free Accessibility Ratio, Active Obstacle Rate, Average Transit Time, and Resolution Turnaround.
- **Interactive Plotly Visualizations:** Pathway distribution donuts, floor-level hazard breakdowns, obstacle resolution efficiency gauges, and route telemetry.

### 6. Enterprise Security & Quality Assurance (Phase 20)
- **Cryptographic Password Security:** Salted PBKDF2-HMAC-SHA256 hashing upgraded to **600,000 iterations** with automatic legacy rehash on authentication.
- **Brute-Force Attack Mitigation:** Account lockout enforcement after 5 consecutive failed login attempts.
- **Role-Based Access Control (RBAC):** Backend privilege verification across `Student`, `Field Staff`, and `Administrator` roles, preventing sole-admin demotion.
- **SQL Injection Defense:** Complete parameterized SQL queries across all database operations.

### 7. Deployment & Release Engineering (Phase 21)
- **Hardened Multi-Stage Container (`Dockerfile`):** `python:3.11-slim` base running under non-root user `appuser` (UID 10001) with internal Python health checking.
- **Persistent Orchestration (`docker-compose.yml`):** Volume mounts for `./data`, `./database`, `./backups`, and `./logs` with `restart: unless-stopped`.
- **Nginx Reverse Proxy (`nginx/nginx.conf`):** WebSocket upgrade rules (`/_stcore/stream`), security headers, and 25MB body upload buffers.
- **Cross-Platform Automation:** Idempotent deployment scripts (`scripts/deploy.sh` and `scripts/deploy.ps1`) with automated pre-deploy database backups.

---

## 🏢 Multi-Floor FET Building Map Specification

The Faculty of Engineering and Technology (FET) building is modeled across 5 physical levels with mathematically verified vertical shaft alignment:

| Floor Level | Elevation ($Z$) | Primary Facilities & Departments | Vertical Connectors |
| :--- | :--- | :--- | :--- |
| **Ground Floor (L0)** | $0.0\text{ m}$ | Main Entrance Portico, Central Amphitheater, Civil Lab, Workshop, West ADA Ramp, Admin Suites | Elevator Shaft `(-6.0, 18.0)`, North/East/South/West Stairs |
| **First Floor (L1)** | $3.5\text{ m}$ | Electronics & Comm Labs, Microprocessor Lab, Smart Classrooms, Faculty Office Suites | Elevator Shaft `(-6.0, 18.0)`, North/East/South/West Stairs |
| **Second Floor (L2)** | $7.0\text{ m}$ | Computer Science & AI Labs, HPC Supercomputer Cluster, Data Science Lab, Server Room | Elevator Shaft `(-6.0, 18.0)`, North/East/South/West Stairs |
| **Third Floor (L3)** | $10.5\text{ m}$ | Mechanical CAD Lab, Robotics & Automation Wing, Mechatronics Research Centre | Elevator Shaft `(-6.0, 18.0)`, North/East/South/West Stairs |
| **Fourth Floor (L4)** | $14.0\text{ m}$ | Central Library & Stacks, Digital Learning Center, Grand Auditorium, Terrace Pavilion | Elevator Shaft `(-6.0, 18.0)`, North/East/South/West Stairs |

---

## 👥 Role-Based Access Control & Demonstration Accounts

The platform includes pre-configured demonstration accounts for evaluating each user role:

| Role | Username | Password | Permitted Operations |
| :--- | :--- | :--- | :--- |
| **Student / Visitor** | `demo_student` | `DemoStudent2026!` | Explore 3D map, calculate routes, bookmark places, submit obstacle reports and feedback. |
| **Field Staff** | `demo_staff` | `DemoStaff2026!` | Inspect pending reports queue, verify hazards (auto-block graph), resolve obstacles with notes. |
| **Administrator** | `demo_admin` | `DemoAdmin2026!` | Manage user roles/statuses, audit trails, review community feedback, update data verification tiers. |

---

## 🚀 Getting Started & Quickstart Guide

### Option 1: Local Python Environment

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/rudrapratap17003-coder/Campus-navigation.git
   cd "Campus-navigation"
   ```

2. **Activate Virtual Environment:**
   - **Windows (PowerShell):**
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   - **Linux / macOS:**
     ```bash
     source .venv/bin/activate
     ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize Database & Seed Demonstration Accounts:**
   ```bash
   python scripts/demo_setup.py
   ```

5. **Launch the Application:**
   ```bash
   streamlit run main.py
   ```
   Open [http://localhost:8501](http://localhost:8501) in your browser.

---

### Option 2: Docker & Docker Compose (Recommended for Production)

1. **Automated One-Click Deployment:**
   - **Linux / macOS:**
     ```bash
     bash scripts/deploy.sh
     ```
   - **Windows PowerShell:**
     ```powershell
     .\scripts\deploy.ps1
     ```

2. **Manual Docker Compose Launch:**
   ```bash
   docker compose up -d --build
   ```
   The application will be available at [http://localhost:8501](http://localhost:8501).

---

## 🧪 Test Suite and Quality Assurance

The codebase features a comprehensive, 100% automated regression and verification test suite:

```bash
python -m unittest discover tests -v
```

### Test Coverage Highlights:
- **`tests/test_phase16_data_accuracy.py`**: Validates 79 locations, 106 pathways, vertical alignment invariance, and destination intelligence.
- **`tests/test_phase17_production_architecture.py`**: Validates environment configs, exception hierarchies, database backups, and logging filters.
- **`tests/test_phase18_user_experience.py`**: Validates i18n translation strings, saved places, favourite routes, and community feedback pipelines.
- **`tests/test_phase19_campus_analytics.py`**: Validates dual-dataset analytics, obstacle resolution KPIs, and administrative insights.
- **`tests/test_phase20_security_and_qa.py`**: Validates SQL injection immunity, RBAC authorization boundaries, brute-force rate-limiting, and credential scrubbing.
- **`tests/test_phase21_deployment.py`**: Validates Dockerfile security, compose volume mapping, `.dockerignore` coverage, Nginx proxy rules, and deploy scripts.

**Latest Test Run Results:**
```
Ran 190 tests in 75.940s
OK (failures=0, errors=0, skipped=0)
```

---

## 📂 Repository Architecture

```
Campus-navigation/
├── .streamlit/
│   └── config.toml                  # Streamlit dark forest theme & server configuration
├── data/
│   ├── jain_global_campus.json      # Authoritative 79-location, 106-pathway campus dataset
│   └── campus_map.json              # Canonical 15-location benchmark dataset
├── database/
│   ├── db_manager.py                # SQLite WAL manager, RBAC, reports, backups, & audit logs
│   └── postgres_migration.py        # Production PostgreSQL schema migration & data exporter
├── modules/
│   ├── accessibility.py             # 0-100 heuristic scoring & barrier classification
│   ├── campus_analytics.py          # Enterprise metrics, KPIs, and operational analytics
│   ├── destination_search.py        # Search intelligence engine with colloquial synonym matching
│   ├── exceptions.py                # Structured domain exception hierarchy
│   ├── i18n.py                      # Multilingual internationalization (en, kn, hi)
│   ├── indoor_map.py                # 2D schematic multi-floor SVG/HTML renderer
│   ├── jain_digital_twin.py         # Authoritative 3D digital twin scene generator & NetworkX bridge
│   ├── logging_config.py            # Structured logging & SensitiveDataFilter
│   ├── obstacle_manager.py          # Dynamic hazard lifecycle manager
│   ├── route_finder.py              # Dijkstra, BFS, and Detour routing algorithms
│   ├── three_d_map.py               # Benchmark 3D scene builder
│   └── ui_theme.py                  # Dark green glassmorphism theme & UI helper components
├── nginx/
│   └── nginx.conf                   # Production Nginx reverse proxy with WebSocket stream support
├── pages/
│   ├── 3d_campus_map.py             # Interactive Three.js 3D Campus Digital Twin & Wayfinding
│   ├── accessibility.py             # Campus accessibility distribution & compliance audit
│   ├── admin_management.py         # Administrative console, user management & audit logs
│   ├── campus_map.py                # 2D multi-floor interactive map visualizer
│   ├── dashboard.py                 # Executive analytics dashboard & KPI telemetry
│   ├── login.py                     # Authentication, registration & account profile
│   ├── navigation.py                # Multi-modal route calculation & algorithm comparison
│   └── obstacle_reports.py          # Field hazard reporting & staff verification queue
├── scripts/
│   ├── demo_setup.py                # Seed default accounts & sample obstacle data
│   ├── deploy.sh                    # POSIX bash automated deployment script
│   └── deploy.ps1                   # Windows PowerShell automated deployment script
├── tests/                           # 190 comprehensive automated test cases across 20 modules
├── .dockerignore                    # Excludes sensitive data, venvs, and databases
├── config.py                        # Centralized configuration dataclasses & environment loader
├── docker-compose.yml               # Container orchestration & persistent volume specification
├── Dockerfile                       # Multi-stage hardened Python 3.11-slim container
├── main.py                          # Streamlit multi-page application entrypoint
├── requirements.txt                 # Exact version-pinned production dependencies
└── README.md                        # Complete project documentation & operator guide
```

---

## 📄 License & Attribution

Developed for the **Accessible Campus Navigator** initiative at **JAIN Global Campus — Faculty of Engineering and Technology (FET)**.  
Released under the **MIT License**. All rights reserved.
