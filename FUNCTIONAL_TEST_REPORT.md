# FUNCTIONAL TEST REPORT
## Accessible Campus Navigator — Automated Suite, Live Health Probe & UI/Browser Verification

**Verification Date:** 2026-11-25  
**Target Environment:** Local Streamlit (`http://localhost:8501`, Python `3.14.0`, SQLite `schema_version = 3`)  
**Evidence Folder:** `COMPLETE_WEBSITE_SCREENSHOTS_AFTER_FIXES/` (`39` unique PNGs, `0` duplicate hashes)

---

## 1. Automated Verification Summary

| Check | Command | Result | Details |
|---|---|---|---|
| Full Test Suite | `.venv\Scripts\python.exe -m unittest discover -s tests -v` | **PASS** | **217 / 217 tests passed** in `80.378s` (`0` failures, `0` errors, `0` skipped) |
| CLI System Health | `.venv\Scripts\python.exe -m modules.health` | **PASS** | `status = HEALTHY`, `total_latency_ms = 51.81`, DB `schema_version = 3`, JAIN (`79`/`106`), Benchmark (`15`/`17`), `issues = []` |
| HTTP Health Endpoint | `GET http://localhost:8501/_stcore/health` | **PASS** | Returned `ok` (`10_Validation_Evidence/final_application_health.png`) |
| Screenshot Uniqueness Audit | `scripts/collect_after_fixes_screenshots.py` | **PASS** | `39` screenshots captured, `39` unique MD5 hashes, `0` duplicates |

---

## 2. Feature & Functional Test Matrix

| Area / Feature | Expected Behavior | Status | Observed Evidence |
|---|---|---|---|
| **Dashboard KPIs & Verification Clarity** | Clearly separates physical verification (`1.3%`) from attribute gaps (`0 / 78`) and renders real analytics charts | **PASS** | `01_Dashboard/dashboard_overview.png`, `01_Dashboard/dashboard_analytics.png`, `01_Dashboard/dashboard_full_page.png` |
| **Route Planner (Default & Config)** | Renders controls inside native bordered cards without empty placeholder HTML containers | **PASS** | `02_Route_Planner/route_default.png` |
| **Wheelchair Cross-Floor Routing (JAIN)** | Routes step-free via ramps and elevators, displaying total breakdown, time estimate, ramp guidance, and transition steps | **PASS** | `02_Route_Planner/wheelchair_route.png`, `02_Route_Planner/cross_floor_route.png`; `test_master_fixes_and_validation.py` |
| **Standard Pedestrian Routing (Stairs)** | Permits stairways in normal mode while clearly flagging staircase warnings and accessibility score caps | **PASS** | `02_Route_Planner/normal_route.png` |
| **2D Floor Plans (Levels G–4 & All)** | Renders clean Plotly floor schematics across all 5 FET levels + outdoor campus with pan/zoom and non-overlapping floor headers | **PASS** | `03_Campus_2D_Map/ground_floor.png` .. `fourth_floor.png`, `map_overview.png` |
| **2D Map Route Overlay & Inspector** | Synchronizes `AccessibilityEngine` to active JAIN graph without missing-edge warnings; shows score and links in Inspector | **PASS** | `03_Campus_2D_Map/route_overlay.png` (`Imported Accessible`, `100.0 / 100`), `location_inspector.png` |
| **3D Digital Twin (Default / Top / Exploded / 2F / Route)** | Interactive Three.js WebGL campus model responds cleanly to camera and floor isolation controls (`btn-cam-top`, `btn-fl-exploded`, `btn-fl-2`, `btn-fl-all`) | **PASS** | `04_Campus_3D_Map/default_view.png`, `top_down_view.png`, `exploded_view.png`, `individual_floor.png`, `route_visualization.png` |
| **3D Live Navigation HUD & KPI Cards** | Displays active navigation step banner and synchronized route KPI cards without raw HTML issues | **PASS** | `04_Campus_3D_Map/navigation_hud.png` |
| **Graph Integrity Validation Panel** | Displays automated `validate_campus_graph()` report (`79/106` & `15/17`, `0` invalid edges, connected=True) | **PASS** | `10_Validation_Evidence/graph_validation.png`, `05_Accessibility/accessibility_overview.png` |
| **Accessibility Inventory & Inspector** | Lists all `106` JAIN pathways and classifies individual locations with provenance badges (`IMAGE_DERIVED` / `VERIFIED`) | **PASS** | `05_Accessibility/accessibility_details.png`, `05_Accessibility/classification_details.png` |
| **Obstacle Reporting & Multi-Map Sync** | Lists `8` DB incident logs (`4 Pending`, `4 Resolved`), exposes report creation for both datasets, and syncs active blockages across graphs | **PASS** | `06_Obstacle_Management/obstacle_dashboard.png`, `obstacle_list.png`, `report_submission.png`; `test_multi_map_obstacle_sync_and_rerouting` |
| **Authentication Setup & Validation** | Enforces Administrator Bootstrap Setup Wizard on fresh/revoked DB (`demo_*` revoked) and validates missing credentials | **PASS** | `07_Authentication/login.png`, `07_Authentication/login_validation.png`; `test_auth_rbac.py` |
| **Unauthenticated Admin Route Gate** | Excludes `/admin_management` from `st.navigation()` for unauthenticated visitors (`Page not found`, fallback to main page) | **PASS** | `08_Administration/admin_access_denied.png` (also accounts for the 1 expected Streamlit navigation error during unauthorized direct URL probe) |
| **Authenticated Admin Console Tabs** | Live browser capture of Admin Landing, User Management, Obstacle Moderation, Audit Logs, and System Config | **BLOCKED** | Blocked by active RBAC security controls: `data/campus_navigation.db` intentionally has no active Administrator account (`demo_*` revoked), and security constraints forbid creating unauthorized DB credentials or bypassing login. Verified instead at unit/integration level via `tests/test_auth_rbac.py` and `tests/test_security_audit.py`. |
| **Post-Bootstrap Registration & Logout UI** | Standard Registration tab and authenticated Logout view after Admin bootstrap | **BLOCKED** | Blocked in live browser by same non-bypassable Admin Bootstrap prerequisite; covered by `tests/test_auth_rbac.py` and `tests/test_security_audit.py`. |
| **Responsive Layout (Desktop / Tablet / Mobile)** | Clean layout reflow across `1366x768`, `768x1024`, `390x844`, and `360x800` viewports including collapsed mobile drawer on 2D Map | **PASS** | `09_Responsive/dashboard_laptop.png`, `dashboard_tablet.png`, `dashboard_mobile.png`, `dashboard_small_mobile.png`, `planner_tablet.png`, `planner_mobile.png`, `map_mobile.png` |

---

## 3. Notes on Console & Security Behavior
- During the automated browser pass of 39 states, the **only** console/page error (`1` total) occurred cleanly when intentionally probing the protected route `http://localhost:8501/admin_management` while unauthenticated, confirming that Streamlit's role-filtered `st.navigation()` refuses to expose privileged pages to guests.
- No production database records or user credentials in `data/campus_navigation.db` were modified during testing.
