# PHASE 12: COMPLETE 3D JAIN GLOBAL CAMPUS RECONSTRUCTION & INTERACTIVE NAVIGATION REPORT

## Project: Accessible Campus Navigator
**Institution:** JAIN (Deemed-to-be University) — Faculty of Engineering & Technology (FET)  
**Campus Location:** Jakkasandra Post, Kanakapura Taluk, Ramanagara District, Karnataka, India — 562112  
**Coordinates Reference:** 12.6517° N, 77.4419° E (NH-948 Kanakapura Road)  
**Date:** November 21, 2026  
**Status:** Completed & Fully Verified (106 / 106 Regression & Digital Twin Tests Passing)  

---

## EXECUTIVE SUMMARY

Phase 12 transforms the **Accessible Campus Navigator** from a schematic demonstration into a high-fidelity **Interactive 3D Digital Twin** of the **JAIN Global Campus** and its flagship **Faculty of Engineering & Technology (FET)** academic building.

The system delivers two interconnected 3D environments rendered in **Three.js / WebGL** seamlessly embedded within the Streamlit platform:
1. **Complete Outdoor Campus Environment:** Reconstructs the 300-acre JAIN Global Campus on Kanakapura Road, including the iconic circular/octagonal FET complex, the Colosseum sports arena, JIRS Aquatic Center, International Cricket Stadium, SBMJCE Dining Complex, student residence halls, administrative headquarters, aerospace research hangars, arterial roads, and pedestrian walkways.
2. **FET Five-Floor Indoor Reconstruction:** Faithfully models all five architectural levels (Ground Floor Level 0, First Floor Level 1, Second Floor Level 2, Third Floor Level 3, and Fourth Floor Level 4) based on the user-uploaded official fire escape route plans. Features include true 3D room volumes, annular octagonal corridors, the central tiered amphitheater, four cardinal fire stairwells (North, East, South, West), and a continuous wheelchair-accessible elevator core.

The 3D environment is powered entirely by the existing **Python backend**, preserving **BFS**, **Dijkstra**, the **Accessibility Intelligence Engine**, **Role-Based Access Control (RBAC)**, and **SQLite live obstacle synchronization**.

---

## PART 1 — COMPREHENSIVE REFERENCE IMAGE ANALYSIS REPORT

A rigorous analysis was conducted across all nine user-uploaded media assets extracted to `assets/floor_plans/`.

### 1.1 Four Campus Aerial Reference Images

| Image Asset | Descriptive Name | Visual Content & Spatial Observations | Data Classification |
| :--- | :--- | :--- | :--- |
| `Screenshot 2026-11-21 132059.png` | `campus_building_closeup_1` | High-resolution close aerial view of the iconic **FET Building Complex**. Displays an **octagonal annular ring** footprint surrounding an open-air central courtyard with a **semi-circular tiered amphitheater**. Reveals multi-tiered concentric steps, perimeter roadway, dedicated west accessible entrance ramp, and segmented roof planes. | **IMAGE_DERIVED** / **VERIFIED** |
| `Screenshot 2026-11-21 132358.png` | `campus_overview` | Comprehensive wide aerial view of the **JAIN Global Campus** along NH-948 (Kanakapura Road). Identifies the main campus security gateway, central quadrangle boulevard, administrative headquarters, international cricket pavilion and ground, the multi-story student residential blocks, and adjacent sports complexes. | **IMAGE_DERIVED** / **APPROXIMATE** (relative building offsets) |
| `Screenshot 2026-11-21 132418.png` | `campus_building_closeup_2` | Close aerial view showcasing the spatial synergy between the circular FET building, the adjacent dome-shaped **Colosseum sports arena**, the indoor athletics center, and the multi-story **SBMJCE Central Dining Hall**. | **IMAGE_DERIVED** / **VERIFIED** |
| `Screenshot 2026-11-21 132429.png` | `campus_other_buildings` | Overhead view of student hostel clusters, the dedicated Aerospace & Aeronautical research test hangars, internal paved walkways, shaded tree lines, and perimeter boundary parking zones. | **IMAGE_DERIVED** / **APPROXIMATE** |

---

### 1.2 Five FET Floor-Plan Reference Images

Each of the five uploaded architectural fire escape route plans was analyzed individually:

```
+-----------------------------------------------------------------------------------------+
|                                    FET BUILDING OVERVIEW                                |
|                           Annular Octagonal Floor Plate (68m x 68m)                     |
|                                                                                         |
|                                    [ North Stairwell ]                                  |
|                                             |                                           |
|                   +-------------------------+-------------------------+                 |
|                   |                   North Concourse                 |                 |
|                   |                                                   |                 |
|         [ West    |   +-------------------------------------------+   |    [ East       |
|          Stairwell]   |             Central Amphitheater          |   |     Stairwell ] |
|             |     |   |              (Concentric Tiers)           |   |         |       |
|             |     |   |                                           |   |         |       |
|             |     |   +-------------------------------------------+   |         |       |
|             |     |                   South Concourse                 |         |       |
|                   +-------------------------+-------------------------+                 |
|                                             |                                           |
|                            [ South Stairwell & Glass Elevator Bank ]                    |
+-----------------------------------------------------------------------------------------+
```

#### A. Ground Floor (Level 0) — `WhatsApp Image 2026-10-15 at 1.53.07 PM (1).jpeg`
- **Building Perimeter:** Octagonal perimeter wall, main south-facing entrance portico, and dedicated western wheelchair ramp.
- **Key Facilities Identified:**
  - `FET_G_ENTRANCE_FOYER`: Grand double-height security and visitor reception foyer.
  - `FET_G_AMPHI_STAGE`: Direct access to the central amphitheater presentation stage and seating.
  - `FET_G_MECH_LAB`: Heavy Machinery & Mechanical Engineering Laboratories (west wing, vibration-isolated slab).
  - `FET_G_CIVIL_LAB`: Structural Engineering & Concrete Testing Laboratory.
  - `FET_G_PHYSICS_LAB`: Engineering Physics & Applied Optics Laboratory.
  - `FET_G_CHEM_LAB`: Engineering Chemistry & Environmental Sciences Laboratory.
  - `FET_G_SEMINAR_01`: Executive Seminar Hall 01 with audio-visual presentation setup.
  - `FET_G_RESTROOM_ACC`: Dedicated wheelchair-accessible universal restroom.
  - `FET_G_FIRE_EXIT_EAST`: Emergency fire egress door leading to outer perimeter assembly ground.
- **Vertical Circulation:** 4 cardinal staircases (`FET_0F_STAIRS_NORTH`, `EAST`, `SOUTH`, `WEST`) and the central passenger elevator bank (`FET_0F_ELEVATOR`).

#### B. First Floor (Level 1) — `WhatsApp Image 2026-10-15 at 1.53.06 PM.jpeg`
- **Floor Plate:** Annular perimeter gallery overlooking the central amphitheater tier.
- **Key Facilities Identified:**
  - `FET_1F_CONCOURSE`: Continuous circulating ring corridor.
  - `FET_1F_AMPHI_TIER`: First-tier spectator balcony overlooking the central arena.
  - `FET_1F_CS_LAB_101`: Primary Computer Science & Software Engineering Laboratory.
  - `FET_1F_DATA_LAB_102`: Data Structures & Algorithm Design Laboratory.
  - `FET_1F_ECE_LAB`: Electronics & Analog Circuits Laboratory.
  - `FET_1F_SMART_103`: Tiered Interactive Smart Classroom 103.
  - `FET_1F_LIBRARY`: Departmental Reading Room & Reference Library.
  - `FET_1F_FACULTY_SUITE`: Faculty workstation suite and academic counseling offices.
  - `FET_1F_RESTROOM_ACC`: Universal accessible restroom.
- **Vertical Circulation:** 4 cardinal stairwells (`FET_1F_STAIRS_NORTH`, `EAST`, `SOUTH`, `WEST`) and elevator (`FET_1F_ELEVATOR`).

#### C. Second Floor (Level 2) — `WhatsApp Image 2026-10-15 at 1.53.06 PM (1).jpeg`
- **Key Facilities Identified:**
  - `FET_2F_CONCOURSE`: Ring corridor.
  - `FET_2F_AI_RESEARCH`: Artificial Intelligence & Neural Networks Laboratory.
  - `FET_2F_CYBER_LAB`: Network Security & Cryptography Laboratory.
  - `FET_2F_VLSI_LAB`: Microelectronics & VLSI Chip Design Laboratory.
  - `FET_2F_SMART_203`: Smart Classroom 203 with hybrid lecture capture.
  - `FET_2F_DEPT_MECH`: Department of Mechanical Engineering administrative office.
  - `FET_2F_HOD_CSE`: Head of Department (Computer Science & Engineering) executive suite.
  - `FET_2F_RESTROOM_ACC`: Universal accessible restroom.
- **Vertical Circulation:** 4 cardinal stairwells (`FET_2F_STAIRS_*`) and elevator (`FET_2F_ELEVATOR`).

#### D. Third Floor (Level 3) — `WhatsApp Image 2026-10-15 at 1.53.06 PM (2).jpeg`
- **Key Facilities Identified:**
  - `FET_3F_CONCOURSE`: Ring corridor.
  - `FET_3F_AVIONICS_LAB`: Aeronautical Avionics & Flight Navigation Simulator.
  - `FET_3F_PROPULSION_LAB`: Aerospace Propulsion & Fluid Dynamics Research Laboratory.
  - `FET_3F_ROBOTICS_LAB`: Autonomous Robotics & Mechatronics Research Cell.
  - `FET_3F_SMART_303`: Collaborative Active Learning Classroom 303.
  - `FET_3F_DEANS_SUITE`: Dean of Engineering & Technology Executive Office.
  - `FET_3F_MAKER_SPACE`: Rapid Prototyping, 3D Printing & Student Maker Facility.
  - `FET_3F_RESTROOM_ACC`: Universal accessible restroom.
- **Vertical Circulation:** 4 cardinal stairwells (`FET_3F_STAIRS_*`) and elevator (`FET_3F_ELEVATOR`).

#### E. Fourth Floor (Level 4) — `WhatsApp Image 2026-10-15 at 1.53.07 PM.jpeg`
- **Key Facilities Identified:**
  - `FET_4F_CONCOURSE`: Ring corridor.
  - `FET_4F_HPC_CLUSTER`: High-Performance Computing (HPC) & Supercomputer Research Cluster.
  - `FET_4F_QUANTUM_LAB`: Quantum Computing & Advanced Algorithmic Simulation Lab.
  - `FET_4F_CONF_HALL`: Grand Academic Senate & Boardroom Conference Hall.
  - `FET_4F_PG_LIBRARY`: Postgraduate Digital Repository & Research Archive.
  - `FET_4F_INCUBATION`: Technology Innovation & Industry Incubation Hub.
  - `FET_4F_TERRACE_SKY`: Accessible Sky Observatory & Astronomical Deck.
  - `FET_4F_RESTROOM_ACC`: Universal accessible restroom.
- **Vertical Circulation:** 4 cardinal stairwells (`FET_4F_STAIRS_*`) and elevator (`FET_4F_ELEVATOR`).

---

### 1.3 Data Classification Matrix

| Category | Elements | Verification Source | Handling Standard |
| :--- | :--- | :--- | :--- |
| **VERIFIED** | FET Building octagonal footprint, central amphitheater, 4 cardinal stairwell locations, central elevator core, 5 distinct floor levels, Kanakapura Road entrance. | Uploaded Fire Escape Route Plans & Google Maps satellite imagery | Modeled with exact topological adjacency and vertical alignment. |
| **IMAGE_DERIVED** | Room divisions, corridor routing, laboratory departmental allocations, outdoor building proximities (Colosseum, Aquatic Center, Cricket Stadium). | Visual inspection of uploaded floor plans and aerial captures | Formulated into normalized room geometries and interconnected graph nodes. |
| **APPROXIMATE** | Exact metric coordinates, architectural ceiling heights (modeled at 6.0m per floor slab, 14.0m in exploded view), road curvature. | Scaled topological modeling from imagery | Normalized around center point (0, 0) with clear UI architectural disclaimer. |
| **UNVERIFIED** | Internal structural column grids, mechanical HVAC shafts, electrical conduits. | Not legible on fire route plans | Omitted to prevent speculative architectural modeling. |

---

## PART 2 — COMPLETE OUTDOOR CAMPUS 3D RECONSTRUCTION

The outdoor campus environment was reconstructed using custom Three.js procedural geometries with distinct architectural characteristics:

```
                                [ NH-948 Kanakapura Road ]
                                             |
                                    [ OUT_GATE_MAIN ]
                                             |
                         +-------------------+-------------------+
                         |                   |                   |
               [ OUT_PARKING_ACC ]    [ OUT_ADMIN_BLOCK ]  [ OUT_COLOSSEUM ]
                         |                   |                   |
                         +-------------------+-------------------+
                                             |
                                   [ OUT_QUAD_CENTRAL ]
                                             |
                  +--------------------------+--------------------------+
                  |                                                     |
         [ OUT_FET_WEST_RAMP ]                                [ OUT_FET_FRONT_PORTICO ]
                  |                                                     |
                  +--------------------------+--------------------------+
                                             |
                                  [ FET 5-FLOOR COMPLEX ]
                                             |
                  +--------------------------+--------------------------+
                  |                          |                          |
        [ OUT_DINING_COMPLEX ]     [ OUT_AQUATICS_POOL ]     [ OUT_CRICKET_STADIUM ]
                  |                          |                          |
        [ OUT_HOSTEL_BLOCKS ]      [ OUT_AEROSPACE_LABS ]               |
```

1. **Terrain & Arterial Grid:**
   - 340m x 340m landscaped terrain with soft terrain gradient (#0B1D15).
   - NH-948 Kanakapura Road corridor with dual-lane markings and arterial entrance boulevard (#1C2420).
   - Paved campus pedestrian avenues (#2A3A30) with curbs and illuminated bollards.
2. **Distinct Campus Buildings:**
   - **FET Engineering Complex:** Octagonal annular structure (68m x 68m, outer radius 34m, inner courtyard radius 14m) with central tiered amphitheater.
   - **Colosseum Sports Arena:** Circular amphitheater/dome facility (radius 22m, height 12m) rendered with distinctive terraced masonry.
   - **JIRS Aquatic Center:** Dedicated pool structure featuring realistic translucid blue water surface (#0284C7) and perimeter stadium seating.
   - **International Cricket Stadium:** Oval turf field (radius 48m x 36m) with central pitch, boundary rope, and red running track (#8B3A2B).
   - **SBMJCE Dining Complex:** Multi-story dining hall and student cafeteria (34m x 22m x 9m).
   - **Student Residence Halls:** Three multi-story dormitory blocks (30m x 14m x 15m each) arranged in residential quadrangle.
   - **University Administrative Block:** Corporate administration headquarters (32m x 20m x 11m) with entrance colonnade.
   - **Aerospace Research Hangars:** High-bay experimental testing hangar (38m x 24m x 10m) with barrel-vaulted roof.

---

## PART 3 — DETAILED FET FIVE-FLOOR INDOOR RECONSTRUCTION

### 3.1 3D Volumetric Room Modeling
Instead of rendering flat lines, the FET building models **true 3D architectural volumes**:
- **Slab Geometry:** Extruded octagonal floor slabs with an inner courtyard hole to accommodate the central amphitheater.
- **Wall Partitions:** Perimeter exterior curtain walls with translucent glass apertures (#264D3D) and opaque structural partitions.
- **Room Meshes:** Extruded room volume boxes (height 2.8m) colored by functional category (Labs, Classrooms, Faculty, Restrooms).
- **Vertical Shafts:**
  - **Elevator Core:** Central glass-paneled elevator shaft spanning `y = 0.5m` to `y = 24.5m` with an animated, glowing elevator cab moving smoothly between floors.
  - **Stairwell Towers:** Four enclosed radial stair towers (North, East, South, West) extending through all 5 floor slabs with yellow/amber stair step indicators.

### 3.2 Floor Elevation & Separation Architecture

| Building Level | Physical Elevation ($y$) | Exploded Elevation ($y$) | Primary Functional Focus |
| :---: | :---: | :---: | :--- |
| **Outdoor Ground** | `0.0 m` | `0.0 m` | Campus pathways, Gate, Quadrangle, Parking |
| **Ground Floor (Level 0)** | `0.5 m` | `0.5 m` | Entrance Foyer, Amphitheater Stage, Heavy Labs, Seminar 01 |
| **First Floor (Level 1)** | `6.5 m` | `14.5 m` | Computer Labs 101/102, ECE Lab, Library, Faculty Suite |
| **Second Floor (Level 2)**| `12.5 m` | `28.5 m` | AI Research Lab, Cyber Lab, VLSI Lab, HOD CSE |
| **Third Floor (Level 3)** | `18.5 m` | `42.5 m` | Avionics Lab, Propulsion Lab, Robotics Lab, Dean's Suite |
| **Fourth Floor (Level 4)**| `24.5 m` | `56.5 m` | HPC Cluster, Quantum Computing Lab, Senate Conference Hall |

---

## PART 4 — INTERACTIVE 3D BUILDING EXPERIENCE

The Three.js viewer incorporates a complete HUD control bar and interactive camera system:

1. **Camera Presets:**
   - **Isometric View:** Classic 45-degree orthographic-style perspective (`x: 75, y: 85, z: 95`) showcasing building depth.
   - **Top-Down Plan View:** Architectural bird's-eye projection (`x: 0, y: 150, z: 0.1`) looking directly down at room layouts.
   - **Front Elevation:** Street-level perspective facing the south entrance portico.
   - **Reset Camera:** Restores original orbit coordinates and camera target.
2. **Domain Mode Switcher:**
   - **All Campus & FET:** Full view of the 300-acre campus with FET positioned at the center.
   - **Outdoor Campus Only:** Focuses camera on external grounds, stadiums, and avenues.
   - **FET Complex Only:** Clips outdoor elements to maximize interior building inspection.
3. **Floor Isolation & Exploded Views:**
   - **Floor Level Buttons (Level 0 to Level 4):** Solo isolates the selected floor, automatically hiding upper and lower slabs.
   - **Stacked View (All 5 Floors):** Renders all 5 floors in natural structural compression.
   - **Exploded View (5F Explode):** Vertically translates each floor slab by `y = 14m * floor_index`, allowing effortless inspection of interior room divisions across all 5 levels simultaneously.
4. **Interactive Raycaster Room Inspection:**
   - Hovering over any 3D room highlights its volume with an emerald green glow.
   - Clicking a room triggers the Three.js raycaster, pinning an on-screen HUD facility card displaying room name, floor, category, step-free access status, and connected corridors.

---

## PART 5 — UNIFIED NAVIGATION GRAPH & PYTHON ENGINE INTEGRATION

### 5.1 Dataset Specifications (`data/jain_global_campus.json`)
- **Total Locations (Nodes):** 79 nodes (12 outdoor campus locations + 67 indoor rooms across 5 floors).
- **Total Pathways (Edges):** 106 bidirectional connections.
- **Zero Self-Loops:** Verified with automated cycle and loop assertions.
- **Full Backward Compatibility:** The canonical benchmark dataset (`data/campus_map.json`, 15 nodes / 17 edges) is 100% preserved, ensuring that all 94 original regression tests continue to pass without modification.

### 5.2 Seamless Outdoor-to-Indoor Navigation
A user can plan a route starting anywhere on campus directly to any room on any floor:
- **Example Route:** `OUT_GATE_MAIN` (Campus Main Gate) $\rightarrow$ `OUT_QUAD_CENTRAL` $\rightarrow$ `OUT_FET_WEST_RAMP` $\rightarrow$ `FET_G_ENTRANCE_FOYER` $\rightarrow$ `FET_0F_ELEVATOR` $\rightarrow$ `FET_1F_ELEVATOR` $\rightarrow$ `FET_2F_ELEVATOR` $\rightarrow$ `FET_3F_ELEVATOR` $\rightarrow$ `FET_4F_ELEVATOR` $\rightarrow$ `FET_4F_HPC_CLUSTER`.
- **Python Source of Truth:** Routes are calculated exclusively by `modules.route_finder.RouteFinder` utilizing **Dijkstra** (shortest distance) or **BFS** (fewest pathway hops).
- **3D Spline Visualization:** The calculated Python path is translated into a 3D spline tube (`THREE.CatmullRomCurve3`) with pulsing particle emitters and an animated light orb traversing the trajectory.

---

## PART 6 — ACCESSIBILITY & DYNAMIC OBSTACLE SYNCHRONIZATION

### 6.1 Wheelchair Step-Free Routing
- **Staircase Restriction:** When `♿ Wheelchair` is checked, the routing engine enforces an absolute barrier on all 4 staircase towers (`has_stairs=True`).
- **Elevator Enforcement:** Multi-floor transitions are routed exclusively through the central elevator shaft (`FET_0F_ELEVATOR` through `FET_4F_ELEVATOR`).
- **Ramp Transition:** Entering the building from outdoor grounds utilizes `OUT_FET_WEST_RAMP` (gentle 1:12 ADA-compliant gradient), bypassing the front portico stairs.

### 6.2 SQLite Obstacle Synchronization
- **Live Database Connection:** Connected directly to `database.db_manager.DatabaseManager` and `modules.obstacle_manager.ObstacleManager`.
- **Verified Hazard Rendering:** Any obstacle marked `Verified` in SQLite renders as a glowing crimson barrier (#F87171) in the 3D scene.
- **Dynamic Detour Rerouting:** The Python backend immediately detects the blocked pathway and calculates an alternative detour. If all vertical elevators are blocked and wheelchair accessibility is active, the engine reports an unreachable destination alert.

---

## PART 7 — QUALITY ASSURANCE & VERIFICATION RESULTS

### 7.1 Regression & Digital Twin Unit Tests
The complete test suite was executed via `.venv\Scripts\python.exe -m unittest discover tests -v`.

```
======================================================================
TEST RESULTS SUMMARY:
- test_accessibility.py:        10 / 10 passed
- test_auth_rbac.py:            20 / 20 passed
- test_campus_map.py:           11 / 11 passed
- test_demo_workflow.py:         1 /  1 passed
- test_indoor_map.py:           12 / 12 passed
- test_jain_campus.py:          12 / 12 passed  <-- NEW PHASE 12 TEST SUITE
- test_obstacle_manager.py:     13 / 13 passed
- test_route_finder.py:          9 /  9 passed
- test_security_audit.py:        6 /  6 passed
- test_three_d_map.py:          12 / 12 passed

TOTAL: 106 TESTS RUN, 106 PASSED, 0 FAILURES, 0 ERRORS (14.855s)
======================================================================
```

### 7.2 Summary of New Unit Tests in `tests/test_jain_campus.py`
1. `test_jain_dataset_structure_and_integrity`: Validates schema, required node attributes, and edge counts (79 nodes, 106 edges).
2. `test_five_floor_levels_present`: Asserts presence of Outdoor level (-1) and all 5 building floors (0, 1, 2, 3, 4).
3. `test_outdoor_buildings_and_pois`: Verifies outdoor facilities (FET, Colosseum, Aquatic Pool, Cricket Stadium, Dining, Hostels, Admin, Aerospace).
4. `test_outdoor_to_indoor_transition`: Verifies step-free path from Campus Main Gate to FET Entrance Foyer.
5. `test_continuous_elevator_bank_across_all_five_floors`: Confirms continuous elevator links connecting 0F $\leftrightarrow$ 1F $\leftrightarrow$ 2F $\leftrightarrow$ 3F $\leftrightarrow$ 4F.
6. `test_staircase_towers_connectivity`: Confirms 4 cardinal stairwells connect adjacent floors and are marked `has_stairs=True`.
7. `test_wheelchair_routing_forces_elevator_and_avoids_stairs`: Proves route to Fourth Floor HPC Cluster avoids all stairs and utilizes elevator.
8. `test_standard_routing_allows_stairs`: Verifies non-wheelchair routing utilizes staircases for direct vertical transfer.
9. `test_active_obstacle_rerouting_on_jain_graph`: Validates dynamic rerouting when an obstacle blocks an elevator or corridor.
10. `test_jain_3d_locations_data_serialization`: Verifies 3D coordinates and elevations for all 79 nodes.
11. `test_jain_3d_pathways_data_serialization`: Verifies 3D geometry and metadata for all 106 pathways.
12. `test_jain_digital_twin_payload_and_html_generation`: Asserts complete JSON payload and standalone Three.js HTML generation.

---

## PART 8 — APPLICATION INTEGRATION & USER WORKFLOW

In `pages/3d_campus_map.py`, users can toggle between:
1. **🏛️ JAIN Global Campus & FET 5-Floor Digital Twin** (Default experience):
   - Full 79-node campus dataset.
   - Interactive 5-floor building explorer.
   - Outdoor and indoor navigation.
2. **📐 Schematic Benchmark Model (15-Node Reference)**:
   - 15-node canonical benchmark dataset.
   - Instant compatibility check.

All existing application pages remain completely intact:
- `main.py` (Navigation hub)
- `pages/dashboard.py` (Campus metrics & KPI cards)
- `pages/navigation.py` (2D route planning)
- `pages/campus_map.py` (Interactive 2D schematic map)
- `pages/accessibility.py` (Accessibility audit & scores)
- `pages/obstacle_reports.py` (Live hazard reporting)
- `pages/login.py` (Role authentication)
- `pages/admin_management.py` (Administrative console & audit logs)

---

## CONCLUSION

Phase 12 successfully realizes a complete, verified, and interactive **3D Digital Twin of JAIN Global Campus and the FET 5-Floor Complex**. The application balances high-performance Three.js WebGL visualization with authoritative Python pathfinding, wheelchair accessibility enforcement, and dynamic SQLite hazard synchronization.
