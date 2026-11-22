# PHASE 16 — REFERENCE IMAGE & FLOOR PLAN AUDIT REPORT
## Accessible Campus Navigator — JAIN Global Campus & FET 3D Digital Twin

---

## 1. Overview & Audit Methodology

This document presents a comprehensive audit of the primary visual reference materials utilized for the 3D reconstruction and topological navigation graph of **JAIN Global Campus** and the **Faculty of Engineering & Technology (FET)** building.

The audit inspects the nine physical and aerial reference images located in `assets/floor_plans/`:
- **Four Outdoor Campus Aerial References:** Capturing campus orientation, arterial road networks, peripheral facilities, and the circular FET complex footprint.
- **Five FET Evacuation Floor Plan References:** Official building emergency evacuation schematics for Ground Floor (Level 0), First Floor (Level 1), Second Floor (Level 2), Third Floor (Level 3), and Fourth Floor (Level 4).

Every observation evaluates:
1. **Reference Asset:** File name and perspective.
2. **Existing Project Representation:** Corresponding 3D mesh, node ID, and coordinate assignment in `data/jain_global_campus.json`.
3. **Observed Characteristics & Discrepancies:** Architectural fidelity, circulation patterns, and spatial relationships.
4. **Data Verification Status:** `VERIFIED`, `IMAGE_DERIVED`, `APPROXIMATE`, or `UNVERIFIED`.
5. **Recommended Calibration:** Enhancements to data confidence and navigation intelligence.

---

## 2. Outdoor Campus Aerial Reference Analysis

### 2.1 Asset 1: `Screenshot 2026-11-21 132059.png` (FET Building Aerial Close-Up)
- **Source:** High-resolution aerial satellite capture of the primary academic core.
- **Observed Physical Features:**
  - Distinctive octagonal annular ring with a central open-air amphitheater courtyard.
  - Four radial wings projecting toward the cardinal/ordinal quadrants.
  - Front monumental portico on the south-east façade with drop-off apron.
  - Accessible ramp approach along the south-west perimeter.
  - Perimeter access ring road with parking bays and landscaped pedestrian walkways.
- **Existing Digital Twin Representation:**
  - Building `BLD_FET` modeled as an octagonal annular structure (`width: 80.0m`, `depth: 80.0m`, `height: 22.0m`) centered at $(0, 0)$.
  - Nodes: `OUT_FET_FRONT_PORTICO` $(10.0, 28.0)$, `OUT_FET_WEST_RAMP` $(-18.0, 22.0)$.
- **Confidence Classification:** `IMAGE_DERIVED`.
- **Calibration Notes:** Coordinates accurately preserve the relational approach from the central quadrangle; exact metric perimeter dimensions remain approximate based on visual scaling.

### 2.2 Asset 2: `Screenshot 2026-11-21 132358.png` (Comprehensive Campus Aerial Overview)
- **Source:** Wide oblique aerial perspective of the 300-acre JAIN Global Campus.
- **Observed Physical Features:**
  - Primary campus access from National Highway 948 (Kanakapura Road) on the south-eastern boundary.
  - Grand central quadrangle boulevard extending northward from the main gate to the academic core.
  - Administration block flanking the central promenade.
  - Extensive sports and recreational facilities situated northeast and north of the academic sector.
- **Existing Digital Twin Representation:**
  - `OUT_GATE_MAIN` $(20.0, 140.0)$, `OUT_PARKING_ACC` $(25.0, 105.0)$, `OUT_QUAD_CENTRAL` $(30.0, 60.0)$, `OUT_ADMIN_BLOCK` $(45.0, 60.0)$.
- **Confidence Classification:** `IMAGE_DERIVED` (Road alignment & spatial arrangement) / `APPROXIMATE` (Metric distances between gates and pavilions).
- **Calibration Notes:** Highway access and promenade direction match the actual geographic axis.

### 2.3 Asset 3: `Screenshot 2026-11-21 132418.png` (Sports Complex & Colosseum Perspective)
- **Source:** Oblique aerial capture of the recreational and athletic sector.
- **Observed Physical Features:**
  - Multi-purpose indoor athletic pavilion ("The Colosseum") featuring classical colonnaded exterior.
  - Standard turf cricket oval with athletic running tracks and spectator pavilion.
  - 50-meter Olympic swimming pool and aquatic training complex (JIRS).
  - Student residential hostel blocks located east of the dining complex.
- **Existing Digital Twin Representation:**
  - `OUT_COLOSSEUM` $(95.0, -65.0)$, `OUT_CRICKET_STADIUM` $(30.0, -95.0)$, `OUT_AQUATICS_POOL` $(-20.0, -110.0)$, `OUT_HOSTEL_BLOCKS` $(105.0, -15.0)$.
- **Confidence Classification:** `IMAGE_DERIVED`.
- **Calibration Notes:** Relative spatial sequence (Dining $\rightarrow$ Hostels $\rightarrow$ Colosseum $\rightarrow$ Cricket Stadium $\rightarrow$ Aquatics) matches physical topography.

### 2.4 Asset 4: `Screenshot 2026-11-21 132429.png` (Aerospace & Research Sector)
- **Source:** North-western campus aerial view.
- **Observed Physical Features:**
  - Dedicated aerospace hangars, propulsion test beds, and unmanned aerial vehicle flight apron.
  - Direct service road connection from the FET engineering workshops to the aerospace hangars.
- **Existing Digital Twin Representation:**
  - `OUT_AEROSPACE_LABS` $(-60.0, -40.0)$ connected to `OUT_FET_WEST_RAMP` and `OUT_AQUATICS_POOL`.
- **Confidence Classification:** `IMAGE_DERIVED`.
- **Calibration Notes:** Preserves industrial access route for heavy machinery and student flight test vehicles.

---

## 3. Five-Floor FET Evacuation Floor Plan Audit

The indoor architecture of the Faculty of Engineering & Technology building is reconstructed directly from the official building fire evacuation plans.

```
                    [ NORTH STAIRWELL ] (0, -22)
                           |
          +----------------+----------------+
          |                                 |
[ WEST STAIRWELL ]                     [ EAST STAIRWELL ]
    (-22, 0)      [ AMPHITHEATER ]         (22, 0)
          |           COURTYARD             |
          +----------------+----------------+
                           |
        [ ELEVATOR BANK ]  |  [ SOUTH STAIRS ]
           (-6, 18)        |     (6, 20)
                           v
               [ ENTRANCE FOYER / CONCOURSE ]
```

### 3.1 Ground Floor (Level 0) — `WhatsApp Image 2026-10-15 at 1.53.06 PM.jpeg`
- **Floor Plan Title:** Ground Floor Fire Escape & Evacuation Plan.
- **Documented Architectural Elements:**
  - **Circulation Cores:**
    - Main Entrance Foyer with double-height reception atrium (`FET_G_ENTRANCE_FOYER`).
    - Central Accessible Elevator Core located at $(X=-6.0, Y=18.0)$.
    - Four cardinal fire escape stairwells: North $(0.0, -22.0)$, South $(6.0, 20.0)$, East $(22.0, 0.0)$, West $(-22.0, 0.0)$.
  - **Key Facilities & Labs:**
    - Mechanical & Manufacturing Workshop (`FET_G_MECH_LAB`): Heavy engineering wing with wide roll-in doors.
    - Civil & Materials Testing Lab (`FET_G_CIVIL_LAB`): Direct exterior access for soil/aggregate delivery.
    - Engineering Physics & Chemistry Labs (`FET_G_PHYSICS_LAB`, `FET_G_CHEM_LAB`): East wing.
    - Sir M. Visvesvaraya Seminar Hall (`FET_G_SEMINAR_01`): 250-seat tiered auditorium with ramped entry.
    - Accessible Sanitary Facility (`FET_G_RESTROOM_ACC`): Adjacent to elevator lobby.
    - East Fire Exit (`FET_G_FIRE_EXIT_EAST`): Dedicated emergency ramp discharging to ground.
- **Verification Status:** `IMAGE_DERIVED` (Room connectivity and core placement verified from schematic).

### 3.2 First Floor (Level 1) — `WhatsApp Image 2026-10-15 at 1.53.06 PM (1).jpeg`
- **Floor Plan Title:** First Floor Academic Plan.
- **Documented Architectural Elements:**
  - **Circulation Cores:**
    - Academic Concourse (`FET_1F_CONCOURSE`) at $(0.0, 18.0)$.
    - Elevator Core aligned at $(-6.0, 18.0)$.
    - 4 Cardinal Stairwells aligned at $(0, -22)$, $(6, 20)$, $(22, 0)$, $(-22, 0)$.
  - **Key Facilities & Labs:**
    - Computer Science & AI Lab 101 (`FET_1F_CS_LAB_101`): West wing computing center.
    - Data Engineering & Cloud Lab 102 (`FET_1F_DATA_LAB_102`): Adjoining software lab.
    - Electronics & Signal Processing Lab (`FET_1F_ECE_LAB`): East wing hardware laboratory.
    - Smart Lecture Hall 103 (`FET_1F_SMART_103`): Multimedia classroom.
    - Departmental Library & Reading Hall (`FET_1F_LIBRARY`): North wing.
    - Faculty Workspaces (`FET_1F_FACULTY_SUITE`): Consultation cabins.
- **Verification Status:** `IMAGE_DERIVED`.

### 3.3 Second Floor (Level 2) — `WhatsApp Image 2026-10-15 at 1.53.06 PM (2).jpeg`
- **Floor Plan Title:** Second Floor Engineering Laboratories Plan.
- **Documented Architectural Elements:**
  - **Circulation Cores:** Concourse at $(0, 18)$, Elevator at $(-6, 18)$, Stairwells aligned.
  - **Key Facilities & Labs:**
    - Center for Machine Intelligence 201 (`FET_2F_AI_RESEARCH`): Advanced AI/ML GPU workstations.
    - Cyber Security & Forensics Lab 202 (`FET_2F_CYBER_LAB`): Specialized security laboratory.
    - VLSI Design & Microelectronics Lab (`FET_2F_VLSI_LAB`): Cleanroom hardware synthesis lab.
    - Smart Lecture Hall 203 (`FET_2F_SMART_203`).
    - Mechanical & Aerospace Faculty Suite (`FET_2F_DEPT_MECH`).
    - HOD Office - Computer Science (`FET_2F_HOD_CSE`).
- **Verification Status:** `IMAGE_DERIVED`.

### 3.4 Third Floor (Level 3) — `WhatsApp Image 2026-10-15 at 1.53.07 PM.jpeg`
- **Floor Plan Title:** Third Floor Aerospace & Advanced Research Plan.
- **Documented Architectural Elements:**
  - **Circulation Cores:** Concourse at $(0, 18)$, Elevator at $(-6, 18)$, Stairwells aligned.
  - **Key Facilities & Labs:**
    - Avionics & Flight Simulation Studio (`FET_3F_AVIONICS_LAB`): Flight simulator trainer.
    - Aerospace Propulsion Research Lab (`FET_3F_PROPULSION_LAB`): Aerodynamics modeling.
    - Robotics & Autonomous Systems Studio (`FET_3F_ROBOTICS_LAB`): Drone and robotic testbed.
    - Aerospace Design Lecture Hall 303 (`FET_3F_SMART_303`).
    - Dean's Executive Suite & Boardroom (`FET_3F_DEANS_SUITE`).
    - Student Innovation Maker Space (`FET_3F_MAKER_SPACE`).
- **Verification Status:** `IMAGE_DERIVED`.

### 3.5 Fourth Floor (Level 4) — `WhatsApp Image 2026-10-15 at 1.53.07 PM (1).jpeg`
- **Floor Plan Title:** Fourth Floor Supercomputing & Post-Graduate Research Plan.
- **Documented Architectural Elements:**
  - **Circulation Cores:** Concourse at $(0, 18)$, Elevator at $(-6, 18)$, Stairwells aligned.
  - **Key Facilities & Labs:**
    - High-Performance Supercomputing Facility (`FET_4F_HPC_CLUSTER`): High-density server cabinets.
    - Quantum Computing & Photonics Lab (`FET_4F_QUANTUM_LAB`): Laser optics tables.
    - Ramanujan Executive Conference Hall (`FET_4F_CONF_HALL`): 120-seat executive conference hall.
    - Postgraduate Archives & Digital Repository (`FET_4F_PG_LIBRARY`).
    - Technology Incubation Cell (`FET_4F_INCUBATION`).
    - Green Terrace & Weather Observatory Access (`FET_4F_TERRACE_SKY`).
- **Verification Status:** `IMAGE_DERIVED`.

---

## 4. Vertical Circulation Invariance & Spatial Alignment Audit

A mathematical validation of all vertical shaft coordinates across the five physical building tiers confirms perfect spatial alignment:

| Circulation Shaft | Floor 0 | Floor 1 | Floor 2 | Floor 3 | Floor 4 | Alignment Status |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Accessible Elevator Core** | $(-6.0, 18.0)$ | $(-6.0, 18.0)$ | $(-6.0, 18.0)$ | $(-6.0, 18.0)$ | $(-6.0, 18.0)$ | **100% Invariant (Aligned)** |
| **South Cardinal Staircase** | $(6.0, 20.0)$ | $(6.0, 20.0)$ | $(6.0, 20.0)$ | $(6.0, 20.0)$ | $(6.0, 20.0)$ | **100% Invariant (Aligned)** |
| **North Cardinal Staircase** | $(0.0, -22.0)$ | $(0.0, -22.0)$ | $(0.0, -22.0)$ | $(0.0, -22.0)$ | $(0.0, -22.0)$ | **100% Invariant (Aligned)** |
| **East Cardinal Staircase** | $(22.0, 0.0)$ | $(22.0, 0.0)$ | $(22.0, 0.0)$ | $(22.0, 0.0)$ | $(22.0, 0.0)$ | **100% Invariant (Aligned)** |
| **West Cardinal Staircase** | $(-22.0, 0.0)$ | $(-22.0, 0.0)$ | $(-22.0, 0.0)$ | $(-22.0, 0.0)$ | $(-22.0, 0.0)$ | **100% Invariant (Aligned)** |

### Vertical Elevation Calibration ($Y$-Axis)
- **Floor -1 (Outdoor Grounds):** Base $Y = 0.5\text{m}$.
- **Floor 0 (Ground Level):** $Y = 0.5\text{m}$ (Building Ground Slab).
- **Floor 1 (First Floor):** $Y = 6.0\text{m}$.
- **Floor 2 (Second Floor):** $Y = 12.0\text{m}$.
- **Floor 3 (Third Floor):** $Y = 18.0\text{m}$.
- **Floor 4 (Fourth Floor):** $Y = 24.0\text{m}$.
- **Exploded View Mode:** Vertical separation multiplier expands floor spacing to $14.0\text{m}$ per tier, allowing complete visual inspection of room interiors.

---

## 5. Summary of Discrepancies & Recommendations

1. **Explicit Data Confidence Metadata:**
   - *Observation:* Previous datasets contained raw geometry without metadata indicating the derivation source.
   - *Recommendation:* Add `verification_status`, `verification_source`, `confidence_level`, and `verification_notes` to all 79 locations and 106 connections.
2. **Search Alias Enrichment:**
   - *Observation:* Users searching for "AI Lab" or "Robotics" previously needed to know exact room numbers or long formal strings.
   - *Recommendation:* Annotate each facility with searchable abbreviations, department affiliations, and colloquial aliases (`search_keywords`, `department`).
3. **Disclosure of Coordinate Nature:**
   - *Observation:* Users might mistake schematic graph coordinates for GPS land-surveyed coordinates.
   - *Recommendation:* Clearly annotate in the Destination Inspector and Route Guidance that planar coordinates are schematic layout representations derived from architectural floor plans and aerial photography.
