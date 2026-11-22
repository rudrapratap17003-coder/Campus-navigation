# SLIDE CONTENT REFERENCE — 15-SLIDE FINAL ACADEMIC PRESENTATION

**Project:** Accessible Campus Navigator — JAIN Global Campus  
**Presenter:** Rudra Pratap (USN: `25BTRCL214`)  
**Department:** Artificial Intelligence and Machine Learning  
**Institution:** JAIN (Deemed-to-be University) — Faculty of Engineering and Technology (FET)  
**Deliverables:**
- PowerPoint: `FINAL_ACCESSIBLE_CAMPUS_NAVIGATOR_PRESENTATION.pptx`
- PDF Export: `FINAL_ACCESSIBLE_CAMPUS_NAVIGATOR_PRESENTATION.pdf`

---

## Slide-by-Slide Technical Reference

### Slide 1: Title & Credentials
- **Slide Title:** Accessible Campus Navigator
- **Subtitle:** An Intelligent and Accessibility-Aware Campus Wayfinding System
- **Key Fields:**
  - Lead Developer: Rudra Pratap
  - USN: 25BTRCL214
  - Department: Artificial Intelligence and Machine Learning
  - Institution: JAIN (Deemed-to-be University) - Faculty of Engineering and Technology (FET)
  - Academic Year: 2025 – 2026
  - Technical Baseline: Python 3.11, NetworkX, SQLite, Streamlit, Three.js, WebGL
  - Verified Benchmark: 208 Unit Tests Passed (100%), Release v1.0.0 Ready

### Slide 2: Problem Statement
- **Slide Title:** Problem Statement
- **Subtitle:** The Challenge of Complex, Inaccessible Campus Navigation
- **Key Points:**
  - **Scale & Disorientation:** 79+ physical locations across a multi-acre campus create navigation bottlenecks for freshmen and visitors.
  - **Indoor Map Blindspots:** Commercial GPS applications terminate routing at the building perimeter, providing zero internal floor guidance.
  - **Physical Mobility Barriers:** Students with physical disabilities or injuries encounter sudden staircases, steep gradients, and locked elevator doors without prior warning.
  - **Dynamic Maintenance Hazards:** Daily campus disruptions (water spills, construction, maintenance) are not reflected in static paper maps.
  - **Fragmented Directory Systems:** Lack of centralized, search-indexed lab and departmental room location data.

### Slide 3: Proposed Solution
- **Slide Title:** Proposed Solution
- **Subtitle:** A Unified, Accessibility-Aware Digital Navigation Platform
- **Key Points:**
  - **Comprehensive Spatial Graph:** Single integrated graph bridging outdoor walkways and 5 indoor building floors.
  - **Multi-Algorithm Routing Engine:** Side-by-side execution of Dijkstra (weighted shortest distance) and BFS (fewest transitions).
  - **Step-Free Accessibility Filter:** Automatic pruning of staircases and mandatory elevator routing for wheelchair users.
  - **Dynamic Obstacle Management:** Closed-loop reporting workflow with instantaneous in-memory graph edge invalidation upon staff verification.
  - **Interactive 3D Digital Twin:** Procedural Three.js WebGL visualization offering floor-by-floor isolation slicing.

### Slide 4: Project Objectives
- **Slide Title:** Project Objectives
- **Subtitle:** Clear, Measurable Engineering Goals
- **Key Points:**
  1. **Unified Wayfinding:** Model campus topology into a single mathematical graph uniting 79 nodes and 106 pathways.
  2. **Deterministic Routing:** Implement Dijkstra and BFS algorithms with verified $O(E + V \log V)$ and $O(V + E)$ bounds.
  3. **Accessibility Equity:** Implement heuristic accessibility scoring and certified step-free paths for wheelchair users.
  4. **Operational Resilience:** Deploy SQLite obstacle reporting with role-based access control and live rerouting.

### Slide 5: System Architecture
- **Slide Title:** System Architecture
- **Subtitle:** Modular, Layered Software Architecture
- **Key Components:**
  - **Presentation Layer:** Responsive Streamlit interface adhering to WCAG 2.1 AA accessibility guidelines.
  - **Service Layer:** `RouteFinder`, `AccessibilityEngine`, `ObstacleManager`, `CampusAnalytics`.
  - **Graph Layer:** NetworkX undirected weighted graph containing floor identifiers and pathway attributes.
  - **Database Layer:** SQLite operating in WAL mode with PBKDF2-HMAC-SHA256 authentication and audit logging.

### Slide 6: Technology Stack
- **Slide Title:** Technology Stack
- **Subtitle:** Selected Frameworks & Engineering Rationale
- **Key Technologies:**
  - **Python 3.11+:** Robust standard library, rapid graph processing, and clean object-oriented architecture.
  - **Streamlit:** High-productivity web framework enabling real-time session state management.
  - **NetworkX:** Industry-standard graph theory library with native shortest-path algorithms and adjacency structures.
  - **SQLite (WAL):** Zero-configuration serverless database with concurrent read-write support and ACID guarantees.
  - **Three.js & WebGL:** Hardware-accelerated 3D rendering directly in browser canvas at 60 FPS without plugins.
  - **Plotly & Folium:** Dynamic geospatial mapping, barrier distribution charts, and traffic analytics.

### Slide 7: Campus Graph & Navigation Model
- **Slide Title:** Campus Graph & Navigation Model
- **Subtitle:** Mathematical Formulation of Campus Topology
- **Key Formulas & Attributes:**
  - Mathematical Graph: $G = (V, E)$, $|V| = 79$, $|E| = 106$.
  - Vertex Data: $v = \{\text{id}, \text{name}, \text{floor\_id}, \text{category}, x, y, \text{is\_accessible}\}$.
  - Edge Weight: $w(u, v) = \text{distance\_meters} + \text{incline\_cost} + \text{surface\_penalty}$.
  - Dual Dataset Support: Full JAIN Global Campus (79 nodes) and Benchmark Model (15 nodes).

### Slide 8: BFS vs Dijkstra Algorithms
- **Slide Title:** Algorithmic Analysis: BFS vs Dijkstra
- **Subtitle:** Comparing Graph Traversal Paradigms for Pedestrian Wayfinding
- **Comparison Matrix:**
  - **BFS:** Explores level-by-level via FIFO queue; minimizes edge count; ignores edge weights; $O(V + E)$.
  - **Dijkstra:** Explores via min-priority heap; minimizes cumulative path weight; accounts for distance and incline; $O(E + V \log V)$.
  - **Empirical Demonstration:** Main Gate to FET Auditorium:
    - Dijkstra: 420 meters (7 nodes traversed) — physically shorter.
    - BFS: 465 meters (6 nodes traversed) — fewer corridor segments, but physically longer.

### Slide 9: Accessibility-Aware Navigation
- **Slide Title:** Accessibility-Aware Navigation
- **Subtitle:** Deterministic Constraint Solving & Heuristic Scoring
- **Key Highlights:**
  - **Dynamic Subgraph Formulation:** $G' = (V, E \setminus E_{\text{stairs}})$.
  - **Elevator Enforcement:** Inter-floor travel strictly routes through validated passenger elevators.
  - **Accessibility Score (0–100):** Heuristic rating calculated from pathway width, surface smoothness, and ramp gradient.
  - **Heuristic Boundary:** Disclosed that scores are heuristic approximations requiring on-ground physical confirmation.

### Slide 10: Five-Floor FET Indoor Navigation
- **Slide Title:** Five-Floor FET Indoor Navigation
- **Subtitle:** Multi-Storey Academic Facility Mapping
- **Key Details:**
  - Multi-Plane Structure: Floor 0 (Ground), Floor 1, Floor 2, Floor 3, Floor 4 mapped as discrete 2D spatial planes.
  - Vertical Transition Spine: Dual elevator shafts and central staircases connect storeys as weighted edges.
  - End-to-End Continuity: Traverses from outdoor campus entrance through FET foyer, up elevator, to second-floor AI lab.
  - Coverage: 45+ specialized laboratories, lecture halls, faculty offices, and accessibility ramps.

### Slide 11: Interactive 3D Digital Twin
- **Slide Title:** Interactive 3D Digital Twin
- **Subtitle:** Procedural WebGL Campus Visualization with Three.js
- **Key Points:**
  - Procedural Geometry: Box meshes and pathway wireframes generated directly from spatial JSON metadata.
  - Camera Controls: OrbitControls allow panning, zooming, and tilting across campus grounds.
  - Floor Isolation: UI controls lift upper storeys to reveal internal room corridors.
  - 3D Navigational Spline: Glowing trajectory directly visualizes Dijkstra waypoint coordinates in 3D space.
  - Engineering Boundary: Schematic representation for wayfinding intuition, not a surveyed BIM/CAD model.

### Slide 12: Dynamic Obstacle Management
- **Slide Title:** Dynamic Obstacle Reporting & Rerouting
- **Subtitle:** Closed-Loop Incident Lifecycle & Edge Severance
- **Lifecycle Sequence:**
  1. **Submission:** User reports obstacle with location, severity, and photo. Status: `PENDING`.
  2. **Verification:** Field Staff inspects on-ground; marks status `VERIFIED`.
  3. **Graph Invalidation:** Engine assigns edge weight $w(e) = \infty$, forcing immediate dynamic rerouting.
  4. **Resolution:** Staff resolves issue with mandatory notes; edge weight restored to original distance.

### Slide 13: Security & Administration
- **Slide Title:** Security, Governance & Administration
- **Subtitle:** Enterprise-Grade Access Control & Audit Trails
- **Key Features:**
  - **PBKDF2 Password Hashing:** 600,000 SHA-256 iterations with 32-byte cryptographic salts.
  - **Role-Based Access Control (RBAC):** Three distinct tiers: Student, Field Staff, Administrator.
  - **Brute-Force Rate Limiting:** 5 failed login attempts triggers 300-second lockout.
  - **Immutable Audit Logging:** Every role change, login event, and obstacle transition records user ID, IP, and timestamp.

### Slide 14: Testing, Results & Limitations
- **Slide Title:** Verification, Test Results & Limitations
- **Subtitle:** Rigorous Empirical Validation & Honest Boundary Disclosure
- **Test Metrics:**
  - 208 automated unit and regression tests passing with 0 failures and 0 errors in 52.3 seconds.
  - Python byte compilation: `compileall -q .` exited with code 0.
- **Honest Limitations:**
  - Node coordinates are schematic representations mapped to campus ground plans, not geodetic GPS.
  - Indoor positioning is manual waypoint selection; hardware BLE beacon trilateration is future scope.
  - Cloud hosting is deployment-prepared (Status C); live public domain activation requires owner GitHub OAuth.

### Slide 15: Conclusion & Future Scope
- **Slide Title:** Conclusion & Future Scope
- **Subtitle:** Making University Campuses More Inclusive for Everyone
- **Key Takeaways:**
  - Integrated 79-location graph, 5-floor indoor map, accessibility engine, and interactive 3D digital twin.
  - Validated algorithmic differences between Dijkstra and BFS on real university campus pathways.
  - Promoted physical inclusivity through step-free routing and dynamic obstacle management.
- **Future Roadmap:**
  - Hardware integration with BLE beacons for live indoor positioning.
  - Voice-guided navigation for visually impaired students.
  - Crowdsourced accessibility tagging and live university timetable integration.
- **Closing Statement:**
  - *"THANK YOU! Making Campus Navigation More Accessible for Everyone."*
