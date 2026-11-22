# Accessible Campus Navigator — 7-Minute Live Demonstration Script

**Project Title:** Accessible Campus Navigator  
**Campus Setting:** JAIN Global Campus — Faculty of Engineering and Technology (FET)  
**Target Duration:** 7 Minutes (420 Seconds)  
**Presenter Target Audience:** Academic Examiners, Project Evaluation Committee & Industry Evaluators  
**Host URL:** `http://localhost:8501`  

---

## ⏱️ Master Timeline & Demonstration Flow

| Timestamp | Phase / Topic | Active Page | Key Action / Visual Target |
| :--- | :--- | :--- | :--- |
| **0:00 – 0:35** | 1. Introduction & Context | Dashboard (`/`) | Introduce JAIN Global Campus & project motivation. |
| **0:35 – 1:10** | 2. Problem Statement | Dashboard (`/`) | Explain multi-floor barriers & physical mobility hurdles. |
| **1:10 – 1:45** | 3. Authentication & Roles | Account & Sign In (`/login`) | Sign in as `demo_student` / show RBAC tier. |
| **1:45 – 2:30** | 4. Route Planning (Standard) | Find Accessible Route (`/navigation`) | Plan route: Main Gate to 4th Floor Conference Hall. |
| **2:30 – 3:15** | 5. Accessible Route Planning | Find Accessible Route (`/navigation`) | Toggle ♿ Wheelchair Mode; show stair avoidance & elevator use. |
| **3:15 – 4:15** | 6. 3D Digital Twin & Exploded View | 3D Campus Map (`/3d_campus_map`) | Show 5 FET floors, Exploded View, Room Focus, and i18n. |
| **4:15 – 5:00** | 7. Live Obstacle Reporting | Obstacle Reports (`/obstacle_reports`) | Report hazard as Student; switch to Staff to verify & block. |
| **5:00 – 5:45** | 8. Dynamic Rerouting Demo | Find Accessible Route (`/navigation`) | Recalculate route; demonstrate real-time detour around blocked corridor. |
| **5:45 – 6:25** | 9. Campus Analytics & Governance | Analytics Dashboard (`/dashboard`) | Review Plotly charts, 79-node dataset KPIs, and audit trail. |
| **6:25 – 7:00** | 10. Conclusion & Q&A | Overview | Summarize achievements, limitations, and future work. |

---

## 🎬 Minute-by-Minute Script & Action Guide

### Minute 0:00 – 0:35 | Step 1: Project Introduction
- **Screen:** Open browser to `http://localhost:8501` (Dashboard).
- **Spoken Narration:**
  > "Good morning, respected members of the evaluation committee. I am pleased to present the **Accessible Campus Navigator**, an intelligent 3D digital twin and accessibility-first wayfinding platform developed for the 300-acre **JAIN Global Campus** and its multi-story **Faculty of Engineering and Technology (FET)** building.
  >
  > Unlike conventional maps that stop at building entrances, our system unifies outdoor campus roadways with detailed 5-floor indoor circulation to provide barrier-free navigation for students, visitors, and persons with mobility challenges."

---

### Minute 0:35 – 1:10 | Step 2: The Multi-Floor Navigation Challenge
- **Screen:** Scroll down Dashboard to the **Campus Pathway Distribution** chart.
- **Spoken Narration:**
  > "Navigating modern academic complexes presents severe obstacles for wheelchair users, individuals recovering from injuries, and visually impaired visitors. Unannounced maintenance, broken elevators, and multi-flight staircases often trap mobility-impaired individuals in dead ends.
  >
  > In our FET building graph of 79 locations and 106 pathways, 18 pathways are staircases that present absolute physical barriers. Our system models every corridor, elevator core, ramp, and room across 5 floors to eliminate these barriers mathematically."

---

### Minute 1:10 – 1:45 | Step 3: Student Login & Role-Based Access Control
- **Screen:** Click sidebar item **Account & Sign In** (`/login`).
- **Action:**
  1. Enter Username: `demo_student`
  2. Enter Password: `DemoStudent2026!`
  3. Click **Sign In**.
- **Spoken Narration:**
  > "We begin by authenticating as a student. The platform implements Role-Based Access Control backed by salted PBKDF2-HMAC-SHA256 password hashing with 600,000 iterations.
  >
  > Once logged in, the sidebar dynamically customizes its navigation links according to student privileges, enabling room bookmarking, accessible route queries, and field obstacle reporting."

---

### Minute 1:45 – 2:30 | Step 4: Standard Route Planning (Main Gate to Floor 4)
- **Screen:** Navigate to **Find Accessible Route** (`/navigation`).
- **Action:**
  1. Origin: Select `OUT_GATE_MAIN (Main Campus Entrance Gate)`
  2. Destination: Select `FET_4F_CONF_HALL (Fourth Floor - Ramanujan Conference Hall)`
  3. Algorithm: `Dijkstra (Shortest Distance)`
  4. Ensure `Wheelchair Accessible` is **unchecked**.
  5. Click **Calculate Route**.
- **Spoken Narration:**
  > "Let's plan a standard route from the Main Campus Gate to the 4th Floor Ramanujan Conference Hall. The Dijkstra algorithm computes a route of 212 meters in 4.1 minutes.
  >
  > Notice the step-by-step guidance: the system guides the pedestrian through the Central Quad, into the Ground Floor portico, and up the South stairwell directly to the 4th floor concourse."

---

### Minute 2:30 – 3:15 | Step 5: Wheelchair-Accessible Step-Free Route Planning
- **Screen:** On **Find Accessible Route**, check the toggle: **♿ Wheelchair Accessible (Avoid Stairs)**.
- **Action:** Click **Calculate Route**.
- **Spoken Narration:**
  > "Now observe what happens when we enable **♿ Wheelchair Accessible**.
  >
  > The routing engine instantly discards all 18 staircase edges. Instead of routing through the front steps, it routes the user via the ADA-compliant **West Access Ramp** into the entrance foyer, and directly to the **Central Elevator Bank**.
  >
  > The user transitions smoothly from Floor 0 to Floor 4 inside the elevator shaft, arriving at the 4th Floor Concourse with 100% step-free compliance and zero stair encounters."

---

### Minute 3:15 – 4:15 | Step 6: The 5-Floor 3D Digital Twin & Exploded View
- **Screen:** Navigate to **3D Campus Map** (`/3d_campus_map`).
- **Action:**
  1. Use Orbit Controls (drag mouse) to rotate the campus 3D view.
  2. Click **View Mode: 5-Floor Exploded View**.
  3. In Destination Search, type `Robotics` or `AI Lab`, and click **"🎯 Focus on Room"**.
  4. Toggle Language to **ಕನ್ನಡ (Kannada)** or **हिंदी (Hindi)** to show localization.
- **Spoken Narration:**
  > "Here is our interactive WebGL 3D Digital Twin built with Three.js. It accurately reconstructs the 300-acre JAIN Global Campus, including the octagonal FET complex, Colosseum, Olympic pool, and athletic stadium.
  >
  > When I switch to **Exploded View**, all 5 physical floors separate vertically along emerald alignment rods. You can clearly inspect the continuous vertical elevator shaft at coordinates `(-6.0, 18.0)`, which is mathematically proven to have zero horizontal shear across all floors.
  >
  > We also support instant room focus and complete multilingual localization in English, Kannada, and Hindi."

---

### Minute 4:15 – 5:00 | Step 7: Dynamic Obstacle Reporting & Staff Verification
- **Screen:** Navigate to **Obstacle Reports** (`/obstacle_reports`).
- **Action:**
  1. As `demo_student`, submit a report on pathway `OUT_FET_FRONT_PORTICO` to `FET_G_ENTRANCE_FOYER`, Category: `Blocked pathway`, Severity: `High`, Description: `Tile repair work in main entrance foyer.`
  2. Click **Submit Report**. Show that status is `Pending` and the pathway remains open until verified.
  3. Sign out and sign in as `demo_staff` / `DemoStaff2026!`.
  4. Return to **Obstacle Reports**, open the **Staff Verification Queue**, and click **Verify & Block Pathway**.
- **Spoken Narration:**
  > "Now let's demonstrate dynamic obstacle awareness. A student encounters wet tile repair work at the main entrance portico and logs a report.
  >
  > To prevent malicious disruption, pending reports do not immediately block paths. When Field Staff logs in, they inspect the pending queue and click **Verify & Block**. The report transitions to `Verified`, and the edge is dynamically blocked in the live NetworkX graph and rendered in glowing crimson red."

---

### Minute 5:00 – 5:45 | Step 8: Dynamic Route Recalculation (Detour Demo)
- **Screen:** Navigate back to **Find Accessible Route** (`/navigation`).
- **Action:**
  1. Calculate route from `OUT_FET_FRONT_PORTICO` to `FET_G_ENTRANCE_FOYER`.
  2. Observe that the navigation engine detects the active obstruction and generates an alternative detour via `OUT_FET_WEST_RAMP`.
- **Spoken Narration:**
  > "Returning to route planning, we attempt to route through the blocked portico.
  >
  > Notice the immediate intelligence: the routing engine detects the verified barrier and detours the pedestrian safely around the construction zone via the West Ramp, arriving safely at the entrance foyer without any manual intervention.
  >
  > Once staff marks the maintenance resolved with notes, the pathway is restored to green immediately."

---

### Minute 5:45 – 6:25 | Step 9: Campus Analytics & Administrative Governance
- **Screen:** Navigate to **Dashboard** (`/dashboard`).
- **Action:** Point out the 4 Plotly charts, the KPI cards, and the dataset switcher (JAIN Global Campus 79-node vs Benchmark 15-node).
- **Spoken Narration:**
  > "The Executive Dashboard provides campus administrators with real-time accessibility intelligence. We track our 79 locations and 106 pathways with an 83% step-free ratio.
  >
  > Administrators can monitor obstacle resolution times, frequently blocked pathways, and historical navigation telemetry. Furthermore, the Admin Console provides an immutable audit log tracking every user role elevation, verification, and resolution event."

---

### Minute 6:25 – 7:00 | Step 10: Conclusion, Limitations & Technical Defense
- **Screen:** Return to the main page overview.
- **Spoken Narration:**
  > "In conclusion, the Accessible Campus Navigator successfully bridges 3D architectural visualization, graph algorithmics, and universal accessibility.
  >
  > The system has been validated by **190 automated unit, integration, and security tests** with zero failures. It runs in a production-hardened Docker container with non-root security and Nginx reverse proxying.
  >
  > As an academic demonstration, our spatial coordinates are schematic approximations based on architectural floor plans rather than geodetic GPS surveys, and heuristic scores represent comparative barrier freedom rather than statutory certifications.
  >
  > Thank you. I welcome your questions."

---

## 💡 Quick Tips for the Presenter

1. **Keep Both Tabs Open:** Open `http://localhost:8501/3d_campus_map` in one tab and `http://localhost:8501/navigation` in another tab for rapid switching.
2. **If You Run Out of Time:** Prioritize showing the **3D Exploded View** (Minute 3:15) and the **Wheelchair Route avoiding stairs** (Minute 2:30). These two features demonstrate the core technical value immediately.
3. **Always Highlight the Disclaimers:** Examiners respect honesty—openly stating that the coordinates are schematic and the 0–100 score is a heuristic builds immediate academic credibility.
