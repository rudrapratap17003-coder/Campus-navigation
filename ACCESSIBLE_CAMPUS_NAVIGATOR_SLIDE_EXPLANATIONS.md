# Accessible Campus Navigator — Presentation Slide Explanations & Speaker Notes

**Presentation File:** `Accessible_Campus_Navigator_Final_Presentation.pptx`  
**Presenter:** Rudra Pratap (USN: 25BTRCL214)  
**Academic Program:** B.Tech in Artificial Intelligence & Machine Learning (Section D)  
**Department:** School of Computer Science & Engineering, Faculty of Engineering & Technology  
**Institution:** JAIN (Deemed-to-be University)  
**Total Slides:** 15 Widescreen (16:9) Professional Slides  

---

## SLIDE 1 — TITLE SLIDE: PROJECT OVERVIEW

### Visual Layout
- Dark forest green background (`#07130F`) with emerald border framing (`#16A36A`).
- Institutional heading: JAIN (Deemed-to-be University) • Faculty of Engineering & Technology.
- Large title: **ACCESSIBLE CAMPUS NAVIGATOR**.
- Subtitle: 3D Digital Twin & Accessible Multi-Modal Wayfinding Platform for JAIN Global Campus.
- Formal candidate metadata card: Rudra Pratap, USN 25BTRCL214, B.Tech AIML Section D.

### Spoken Narration (30–45 Seconds)
> "Respected members of the academic evaluation committee, good morning. My name is Rudra Pratap, USN 25BTRCL214, from the Department of Artificial Intelligence and Machine Learning, Section D.
> 
> Today, I am proud to present my final university engineering project: the **Accessible Campus Navigator**. This platform provides an interactive 3D digital twin and multi-modal, accessibility-first wayfinding system developed specifically for the 300-acre JAIN Global Campus on Kanakapura Road and its five-floor Faculty of Engineering and Technology (FET) building complex.
> 
> The project addresses the real-world navigation barriers faced by wheelchair users, injured students, and first-time campus visitors by unifying outdoor roads with indoor multi-floor architecture."

---

## SLIDE 2 — PROBLEM STATEMENT: THE MULTI-FLOOR NAVIGATION BARRIER

### Visual Layout
- Three distinct diagnostic cards:
  1. **Macro-Map Blindness:** Commercial maps stop at outer gates; treat complexes as flat 2D polygons.
  2. **Vertical Discontinuity:** Inability to visualize multi-floor departments across 5 levels.
  3. **Disability Access Risks:** 18 staircase pathways in FET pose impassable physical barriers for wheelchair users.

### Spoken Narration (45 Seconds)
> "To understand the necessity of this project, consider how university navigation functions today.
> 
> First, commercial mapping services such as Google Maps stop at campus entrance gates. They map multi-story buildings as flat, single-point coordinates with zero visibility into internal corridors, classrooms, or research labs.
> 
> Second, university buildings like FET are vertical architectures with five physical floors. Traditional maps cannot represent vertical circulation cores.
> 
> Most critically, persons with disabilities face severe accessibility risks. In our FET building graph, 18 pathways are staircases. A wheelchair user or injured visitor guided blindly toward a staircase faces an insurmountable dead-end. Furthermore, conventional mapping possesses zero dynamic awareness of wet floors, maintenance work, or broken elevators."

---

## SLIDE 3 — PROJECT OBJECTIVES & RESEARCH GOALS

### Visual Layout
- Five horizontal emerald-accented goal cards:
  1. Accurate Spatial Topology (79 locations, 106 pathways across 5 floors).
  2. Accessible Shortest Path Routing (Dijkstra distance/time, BFS turn minimization, stair exclusion).
  3. WebGL 3D Digital Twin (Three.js 300-acre campus, 5-floor FET, exploded view).
  4. Dynamic Hazard Awareness (Community reporting, staff verification, in-graph blocking).
  5. Universal Inclusive Design (Multilingual i18n in en/kn/hi, WCAG AAA high contrast, reduced motion).

### Spoken Narration (45 Seconds)
> "To solve these challenges, our project established five core engineering objectives:
> 
> 1. To model the campus as a mathematically rigorous graph of 79 verified locations and 106 walkable pathways.
> 2. To develop routing algorithms that optimize physical distance, transit duration, and turn count, while strictly excluding all 18 staircase pathways for wheelchair users.
> 3. To reconstruct the campus in an interactive WebGL 3D Digital Twin featuring a 5-floor exploded architectural view.
> 4. To implement a dynamic obstacle reporting and verification system in SQLite WAL mode that dynamically blocks graph edges upon staff verification.
> 5. To provide universal accessibility through multilingual support in English, Kannada, and Hindi, along with WCAG AAA high-contrast styling."

---

## SLIDE 4 — PROPOSED SOLUTION: INTEGRATED 3D ACCESSIBILITY PLATFORM

### Visual Layout
- Two large side-by-side cards:
  - Left Card: Core Platform Capabilities (Unified graph, wheelchair guarantee, 2D vector cross-product turn guidance, 3D WebGL twin).
  - Right Card: User Personas & Operational Roles (Student, Field Staff, Administrator).

### Spoken Narration (40 Seconds)
> "Our proposed solution unifies outdoor roads and five building floors into an integrated web platform.
> 
> For users, the system provides turn-by-turn guidance calculated using 2D vector cross-products, compass bearings, and 3D avatar visualization.
> 
> To ensure operational integrity, the platform implements Role-Based Access Control: Students can explore, plan routes, bookmark places, and submit field hazard reports; Field Staff verify hazards, which dynamically blocks paths on the live graph, and resolve them with notes; and Administrators govern user accounts, inspect immutable audit trails, and manage campus data reliability tiers."

---

## SLIDE 5 — TECHNOLOGY STACK

### Visual Layout
- Grid of six technology cards:
  1. Presentation & Web UI: Streamlit 1.67.0
  2. 3D Graphics Engine: Three.js (r128 WebGL)
  3. Graph & Algorithmics: NetworkX 3.7
  4. Database & Persistence: SQLite3 (WAL Mode)
  5. Data Visualization: Plotly 7.1.0
  6. Containerization & Proxy: Docker & Nginx

### Spoken Narration (40 Seconds)
> "The architecture relies entirely on modern, robust open-source technologies:
> 
> The front-end is built using Streamlit 1.67 with custom dark-forest glassmorphism styling, integrating Three.js for hardware-accelerated 3D graphics and Plotly for interactive telemetry charts.
> 
> The core routing and graph intelligence is powered by NetworkX, executing our custom Dijkstra and BFS implementations.
> 
> Persistence is managed by SQLite3 in Write-Ahead Logging mode, while the entire production system is containerized in Docker with an Nginx reverse proxy managing WebSocket streams and security headers."

---

## SLIDE 6 — THREE-TIER SYSTEM ARCHITECTURE & DATA FLOW

### Visual Layout
- Three column architecture flow:
  - Tier 1: Presentation Layer (Streamlit, Three.js WebGL, Plotly, i18n Localization, WCAG AAA CSS).
  - Tier 2: Algorithmic Logic (RouteFinder, AccessibilityEngine, ObstacleManager, DestinationSearch, NavigationSession FSM).
  - Tier 3: Persistence & Security (NetworkX 79-Node Graph, SQLite WAL, PBKDF2 600k rounds, Audit Logs, Postgres Migration Exporter).

### Spoken Narration (45 Seconds)
> "Here we illustrate our three-tier system architecture and data flow.
> 
> The Client Presentation Layer handles user interaction, rendering the 3D WebGL scene and interactive charts.
> 
> The Algorithmic Service Layer contains our routing engine, accessibility classifier, and obstacle manager. When a route is requested, RouteFinder evaluates active blocked edges, filters out staircases if wheelchair mode is enabled, and generates waypoint splines and directional instructions.
> 
> The Data Layer maintains our 79-location graph and SQLite database. Every administrative action and obstacle verification writes an immutable audit record, and singletons are cached in session state to prevent redundant disk reads."

---

## SLIDE 7 — JAIN GLOBAL CAMPUS & 5-FLOOR FET 3D DIGITAL TWIN

### Visual Layout
- Left Card: Complete Outdoor 300-Acre Campus (NH-948 highway, Octagonal FET, Colosseum, JIRS 50m Olympic Pool, Cricket Stadium with running track, Hostels, Aerospace Hangar).
- Right Card: Five-Floor FET Building Reconstruction (Ground Floor to 4th Floor, procedural interior furnishings, elevator shaft zero-shear invariant proof, 5-floor exploded view).

### Spoken Narration (50 Seconds)
> "Slide 7 details our 3D Digital Twin.
> 
> Outdoors, we reconstructed the 300-acre JAIN Global Campus, including the distinctive octagonal FET building, the Colosseum arena with colonnade pillars, the JIRS Olympic aquatic center, and the international cricket stadium with its 4-lane athletic track.
> 
> Indoors, we modeled all five physical floors of FET from architectural floor plans: Ground Floor portico and amphitheater, First Floor electronics labs, Second Floor AI and supercomputing clusters, Third Floor robotics wings, and Fourth Floor library and conference halls.
> 
> A critical mathematical achievement was proving the vertical elevator shaft invariant: across all five tiers, the shaft maintains planar coordinates (-6.0, 18.0) with exactly 0.00 meters of horizontal displacement, ensuring vertical alignment in both 3D rendering and 5-floor exploded views."

---

## SLIDE 8 — NAVIGATION ALGORITHMS: DIJKSTRA VS. BFS

### Visual Layout
- Central comparison table comparing Dijkstra and BFS across Graph Type, Time Complexity, Space Complexity, and Primary Use Case.
- Bottom Card: Algorithm Selection & Trade-Off Comparison (Penalty detour routing, simultaneous calculation).

### Spoken Narration (50 Seconds)
> "In Slide 8, we compare our two core graph search algorithms: Dijkstra's algorithm and Breadth-First Search (BFS).
> 
> Dijkstra operates on weighted edges to compute the path of absolute shortest physical distance or estimated walking time. Using a binary min-heap, its time complexity is O((V + E) log V). On our 79-node graph, it executes in under 2 milliseconds.
> 
> Conversely, Breadth-First Search treats the graph as unweighted, traversing level-by-level in O(V + E) time to find the path with the fewest corridor transitions and turns.
> 
> Our platform computes both routes simultaneously, presenting pedestrians with an intelligent trade-off card so they can choose between walking fewer meters or taking a simpler, straight-line route with fewer turns."

---

## SLIDE 9 — WHEELCHAIR-ACCESSIBLE STEP-FREE ROUTING LOGIC

### Visual Layout
- Left Card: Constrained Subgraph Formulation (Strict edge pruning, absolute staircase exclusion, ramp & elevator prioritization, 6,162 verified test pairs).
- Right Card: Continuous Heuristic Accessibility Scoring (0–100 formula, classification categories: Fully Accessible, Accessible with Assistance, Not Wheelchair Accessible, Temporarily Blocked).

### Spoken Narration (50 Seconds)
> "Slide 9 highlights our core accessibility contribution: guaranteed step-free routing.
> 
> When the wheelchair toggle is activated, RouteFinder generates a constrained subgraph that strictly strips all 18 staircase edges. The algorithm forces routing through the ADA-compliant West Access Ramp and the central elevator bank. Across all 6,162 directed test pairs, 100% of generated wheelchair routes are proven step-free.
> 
> In addition, our AccessibilityEngine calculates a continuous heuristic score from 0 to 100 based on step-free status, ramp gradients, and door widths, categorizing paths into standardized accessibility tiers. We explicitly clarify in the UI that this score is an algorithmic routing heuristic rather than an official statutory building compliance certificate."

---

## SLIDE 10 — DYNAMIC OBSTACLE MANAGEMENT & IN-TRANSIT REROUTING

### Visual Layout
- 5-step operational pipeline cards:
  1. Citizen Reporting (Student logs hazard).
  2. Pending Triage (Does not block graph; prevents denial of service).
  3. Staff Verification (Staff verifies; edge blocked dynamically in NetworkX).
  4. Dynamic Detour (In-transit navigation detects barrier and detours).
  5. Maintenance Clear (Staff resolves with notes; path restored to green).

### Spoken Narration (45 Seconds)
> "Dynamic hazard awareness is modeled as a 5-step lifecycle.
> 
> A student encountering maintenance work logs a report. To prevent malicious disruptions, reports enter a 'Pending' queue without affecting navigation.
> 
> When Field Staff verify the issue, ObstacleManager dynamically marks the edge 'blocked' in the live NetworkX graph and turns the 3D pathway crimson red.
> 
> If a pedestrian is currently navigating along that corridor, the system detects the barrier and automatically recalculates an alternative detour around the blocked area. Once maintenance is completed, staff resolve the report with audit notes, immediately restoring the edge to operational green."

---

## SLIDE 11 — CYBERSECURITY HARDENING & ENTERPRISE DATABASE DESIGN

### Visual Layout
- Grid of six security cards:
  1. PBKDF2 Password Hashing (600k rounds, 32-byte salts).
  2. Brute-Force Rate Limiting (5 failed attempts trigger 15-min lockout).
  3. Role-Based Access Control (Backend service-layer verification).
  4. Sole-Admin Protection (Prevents accidental demotion of last admin).
  5. SQLite WAL Journaling (Concurrent readers, 5s timeout).
  6. Immutable Audit Logging (Records all administrative events).

### Spoken Narration (45 Seconds)
> "Security and reliability are engineered into every layer.
> 
> User authentication uses PBKDF2-HMAC-SHA256 with 600,000 hash iterations and unique 32-byte salts, exceeding OWASP standards. Brute-force attacks are mitigated by automatically locking accounts for 15 minutes after 5 consecutive failed attempts.
> 
> All database queries use parameterized SQL to prevent SQL injection.
> 
> Furthermore, we enforce sole-admin demotion prevention, ensuring the system can never lose administrative control, and our SensitiveDataFilter scrubs credentials and tokens from application logs."

---

## SLIDE 12 — CAMPUS ANALYTICS DASHBOARD & TELEMETRY

### Visual Layout
- Left Card: Executive Telemetry & KPI Cards (79 verified facilities, 106 pathways, 83.0% step-free ratio, active obstacles, dual-dataset switcher).
- Right Card: Four Interactive Plotly Visualizations (Donut chart of pathway accessibility, lifecycle bar chart, floor-level hazard breakdown, resolution turnaround gauge).

### Spoken Narration (40 Seconds)
> "The Executive Dashboard provides facilities managers with real-time accessibility intelligence.
> 
> Our KPI cards track our 79 facilities and 106 pathways, highlighting an 83% step-free ratio.
> 
> Four interactive Plotly charts visualize pathway classifications, obstacle lifecycle distributions, floor-level hazard frequency, and average resolution times in hours.
> 
> Crucially, our dataset switcher allows evaluators to toggle between the full 79-location JAIN Digital Twin and the 15-location Schematic Benchmark, ensuring transparent academic evaluation."

---

## SLIDE 13 — AUTOMATED TESTING, VERIFICATION & QUALITY ASSURANCE

### Visual Layout
- Top Banner: **Ran 190 tests in 32.133s — OK (failures=0, errors=0, skipped=0) — 100.0% Pass Rate**.
- Four Category Cards: Graph & Routing (reachability), Accessibility (stair exclusion), Security & RBAC (SQL injection & lockout), Deployment & Config (Docker appuser & Nginx headers).

### Spoken Narration (45 Seconds)
> "Slide 13 presents our empirical testing results.
> 
> The platform is verified by a comprehensive automated test suite of **190 tests executing in 32.1 seconds with 0 failures, 0 errors, and 0 skipped tests**.
> 
> The suite rigorously asserts all-pairs graph reachability across 6,162 directed pairs, 100% staircase exclusion in wheelchair mode, SQL injection immunity, brute-force rate-limiting lockouts, and Docker container security.
> 
> In accordance with academic honesty, we distinguish test pass rate from code coverage: third-party coverage tools were not installed in the clean production environment to preserve dependency stability, so line coverage percentages are not claimed."

---

## SLIDE 14 — SYSTEM LIMITATIONS & FUTURE SCOPE

### Visual Layout
- Left Card: Academic & System Limitations (Schematic coordinates, heuristic score disclaimer, simulated pedestrian motion, local host demo).
- Right Card: Future Engineering Enhancements (Indoor BLE beacon trilateration, Web Speech API audio guidance, automated BIM CAD ingestion, IoT elevator sensors).

### Spoken Narration (40 Seconds)
> "We maintain complete academic transparency regarding project limitations:
> 
> First, our spatial coordinates are topological layout values derived from architectural floor plans rather than centimeter-accurate GPS surveys.
> Second, our 0–100 score is an algorithmic routing heuristic, not a certified statutory ADA rating.
> Third, real-time traversal simulates 1.2 m/s walking speed rather than tracking physical hardware beacons.
> 
> In the future, we plan to integrate Bluetooth Low Energy beacon trilateration for live blue-dot tracking, text-to-speech audio guidance for visually impaired users, and automated BIM model parsers."

---

## SLIDE 15 — CONCLUSION & FINAL ACADEMIC HANDOVER

### Visual Layout
- Main Card: Engineering Achievements Summary (JAIN 3D twin, Dijkstra/BFS routing, wheelchair guarantee, obstacle lifecycle, 190 passing tests, complete documentation).
- Bottom Emerald Banner: **Thank You! Respected Committee Members, I welcome your questions.**

### Spoken Narration (30 Seconds)
> "In conclusion, the Accessible Campus Navigator successfully bridges graph algorithmics, 3D computer graphics, cybersecurity, and universal design principles.
> 
> It provides JAIN Global Campus with a verified, accessible, and dynamic wayfinding platform that mathematically eliminates mobility barriers.
> 
> With 190 passing automated tests, hardened Docker deployment, and complete academic documentation, the project is fully validated and ready for defense.
> 
> Thank you, respected committee members. I am now open to your questions."
