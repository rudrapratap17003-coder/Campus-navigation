# FINAL PRESENTATION SPEAKING SCRIPT (15 SLIDES)

**Project:** Accessible Campus Navigator — JAIN Global Campus  
**Presenter:** Rudra Pratap (USN: `25BTRCL214`)  
**Department:** Artificial Intelligence and Machine Learning  
**Target Speaking Duration:** 8 minutes 45 seconds (Paced for 8–10 minute evaluation window)  
**Tone:** Confident, articulate, academically grounded, student-friendly  

---

## SLIDE 1 — TITLE & CREDENTIALS
- **Slide Title:** Accessible Campus Navigator
- **Approximate Duration:** 30 seconds
- **Spoken Explanation:**
  > *"Good morning, respected members of the evaluation committee and faculty members. My name is Rudra Pratap, USN 25BTRCL214, from the Department of Artificial Intelligence and Machine Learning. Today, I am honored to present my major project: **Accessible Campus Navigator**, developed for our JAIN Global Campus and the Faculty of Engineering and Technology. This project is a software-based, accessibility-aware wayfinding and digital twin platform designed to make university spaces easier to explore, navigate, and experience for everyone."*
- **What to Emphasize:** State your name, USN, and the core purpose clearly. Establish that this is a practical engineering solution targeting real campus accessibility.
- **Transition:**
  > *"To understand why this system was necessary, let us look at the day-to-day navigation challenges faced by students and visitors on our campus."*

---

## SLIDE 2 — PROBLEM STATEMENT
- **Slide Title:** Problem Statement
- **Approximate Duration:** 40 seconds
- **Spoken Explanation:**
  > *"Our campus is large, covering multiple academic departments, residential blocks, and specialized research centers. For first-year students and visitors, finding a specific laboratory or faculty room can be disorienting. Commercial navigation systems like Google Maps stop at the campus entrance; they provide no guidance once you step inside a building.
  >
  > Furthermore, for students with mobility impairments or temporary injuries, physical barriers such as unexpected staircases, broken pathways, or out-of-service elevators turn an ordinary 5-minute walk into a frustrating, dead-end detour. Static campus maps cannot adapt when a hallway is temporarily blocked for maintenance."*
- **What to Emphasize:** Highlight the gap between outdoor maps and indoor multi-floor facilities, and the daily reality of mobility barriers.
- **Transition:**
  > *"To solve these interconnected challenges, we designed and built the Accessible Campus Navigator."*

---

## SLIDE 3 — PROPOSED SOLUTION
- **Slide Title:** Proposed Solution
- **Approximate Duration:** 40 seconds
- **Spoken Explanation:**
  > *"Our solution brings together five core technical capabilities into a single unified web platform. First, a comprehensive spatial graph modeling 79 physical campus locations and 106 pathways. Second, an intelligent routing engine comparing Dijkstra's shortest path and Breadth-First Search. Third, an accessibility engine that dynamically removes stairs and calculates certified step-free paths. Fourth, a dynamic obstacle reporting lifecycle that severs blocked pathways in real time. And fifth, an interactive 3D digital twin that lets students explore campus buildings before they even arrive."*
- **What to Emphasize:** Emphasize that the solution is a unified system rather than disconnected tools.
- **Transition:**
  > *"Let us translate these capabilities into the four specific engineering objectives we set out to achieve."*

---

## SLIDE 4 — PROJECT OBJECTIVES
- **Slide Title:** Project Objectives
- **Approximate Duration:** 35 seconds
- **Spoken Explanation:**
  > *"Our project established four core objectives: First, unified wayfinding—connecting outdoor campus roads and indoor building corridors into one continuous mathematical graph. Second, deterministic routing—providing clear, mathematically proven routes with side-by-side comparisons of distance versus edge transitions. Third, step-free equity—guaranteeing wheelchair-accessible paths with heuristic accessibility scores. And fourth, dynamic resilience—ensuring that real-world obstacle reports immediately trigger automatic route recalculations."*
- **What to Emphasize:** The balance between algorithmic rigor and social impact (accessibility equity).
- **Transition:**
  > *"To achieve these goals, we designed a clean, modular software architecture."*

---

## SLIDE 5 — SYSTEM ARCHITECTURE
- **Slide Title:** System Architecture
- **Approximate Duration:** 40 seconds
- **Spoken Explanation:**
  > *"As shown in this architecture diagram, the system follows a layered software pattern. At the top is the Presentation Layer, built with Streamlit and styled with a WCAG 2.1 AA compliant dark-forest theme. Below that, the Service Layer coordinates routing, accessibility heuristics, obstacle management, and campus analytics.
  >
  > These services interact with our Core Engines: NetworkX handles graph algorithms in memory, SQLite in Write-Ahead Logging mode provides relational persistence, and Three.js powers the 3D WebGL viewport. Notice that the entire pipeline is decoupled, ensuring reliability and fast response times."*
- **What to Emphasize:** Point to the clear separation of concerns—UI, business logic, graph traversal, and database persistence.
- **Transition:**
  > *"Next, let us examine the technology stack that powers each of these layers."*

---

## SLIDE 6 — TECHNOLOGY STACK
- **Slide Title:** Technology Stack
- **Approximate Duration:** 35 seconds
- **Spoken Explanation:**
  > *"We deliberately selected proven, open-source technologies suited for rapid, maintainable engineering. Python 3.11 provides the algorithmic foundation. Streamlit delivers an interactive, stateful web interface without heavy frontend frameworks. NetworkX gives us optimized graph structures and shortest-path algorithms.
  >
  > SQLite in WAL mode ensures concurrent read-write access for obstacle reports. Three.js and WebGL provide hardware-accelerated 3D graphics in standard browsers without plugins, while Plotly renders our spatial analytics charts."*
- **What to Emphasize:** Justify each technology choice based on engineering requirements rather than trends.
- **Transition:**
  > *"Now, let us delve into the mathematical foundation of our wayfinding system: the campus graph model."*

---

## SLIDE 7 — CAMPUS GRAPH & NAVIGATION MODEL
- **Slide Title:** Campus Graph & Navigation Model
- **Approximate Duration:** 45 seconds
- **Spoken Explanation:**
  > *"We model JAIN Global Campus as an undirected, weighted graph $G = (V, E)$, consisting of 79 vertices and 106 edges. Vertices represent key landmarks: campus gates, cafeterias, building entrances, elevators, stairwells, and specific departmental laboratories.
  >
  > Each edge represents a traversable walkway with rich metadata: physical distance in meters, pathway type, incline percentage, and accessibility status. The total weight of an edge is calculated as a function of physical distance plus incline penalties, ensuring our algorithms choose gentle, navigable pathways."*
- **What to Emphasize:** The mathematical formulation: nodes represent physical spaces, edges represent traversable paths with rich attributes.
- **Transition:**
  > *"On top of this graph model, we implemented and evaluated two classic graph search algorithms."*

---

## SLIDE 8 — BFS VS DIJKSTRA ALGORITHMS
- **Slide Title:** Algorithmic Analysis: BFS vs Dijkstra
- **Approximate Duration:** 45 seconds
- **Spoken Explanation:**
  > *"A central academic contribution of this work is comparing Breadth-First Search and Dijkstra's algorithm for pedestrian wayfinding. Breadth-First Search operates on unweighted graphs, exploring level by level to find the path with the fewest edge hops.
  >
  > Dijkstra's algorithm uses a min-priority queue to find the path with the lowest cumulative weight. In pedestrian navigation, fewest hops does not mean shortest distance. For example, routing from the Main Gate to the FET Auditorium, BFS chose a 6-node path covering 465 meters, while Dijkstra found a 7-node path covering only 420 meters because it selected shorter corridor segments. This proves why weighted routing is indispensable."*
- **What to Emphasize:** The practical difference: BFS minimizes transitions, while Dijkstra minimizes actual physical walking distance.
- **Transition:**
  > *"Next, let us see how we adapted Dijkstra's algorithm for wheelchair users."*

---

## SLIDE 9 — ACCESSIBILITY-AWARE NAVIGATION
- **Slide Title:** Accessibility-Aware Navigation
- **Approximate Duration:** 40 seconds
- **Spoken Explanation:**
  > *"When a student selects 'Wheelchair Accessible Only', the navigation engine constructs a constrained subgraph, mathematically removing all edges tagged as staircases. This forces the pathfinding solver to route exclusively through certified ramps and passenger elevators.
  >
  > We also compute a heuristic accessibility score from 0 to 100 based on path width, surface smoothness, and ramp gradient. A path with a wide elevator achieves a 95% rating. We must be transparent: these scores are heuristic approximations based on recorded attributes, and real-world physical verification is always encouraged."*
- **What to Emphasize:** The subgraph pruning concept $G' = (V, E \setminus E_{\text{stairs}})$ and the honest disclosure about heuristic scoring.
- **Transition:**
  > *"This brings us to one of our biggest engineering challenges: multi-floor indoor navigation inside the FET Building."*

---

## SLIDE 10 — FIVE-FLOOR FET INDOOR NAVIGATION
- **Slide Title:** Five-Floor FET Indoor Navigation
- **Approximate Duration:** 40 seconds
- **Spoken Explanation:**
  > *"The Faculty of Engineering and Technology building spans five distinct levels, from Ground Floor to the Fourth Floor. We mapped each floor as an independent 2D coordinate plane with its specific laboratories—such as the AIML Lab, High Performance Computing Center, and Robotics Lab.
  >
  > The key breakthrough is our vertical transition spine: elevator shafts and staircases are modeled as inter-floor vertical edges. When a user requests a path from the campus gate to the 2nd-floor AI lab, the engine seamlessly routes across the outdoor walkway, enters the foyer, transitions vertically via the elevator, and navigates the 2nd-floor hallway."*
- **What to Emphasize:** How vertical edges bridge flat 2D planes into a continuous 3D navigable network.
- **Transition:**
  > *"To help users visualize this multi-storey environment before walking it, we built an interactive 3D digital twin."*

---

## SLIDE 11 — INTERACTIVE 3D DIGITAL TWIN
- **Slide Title:** Interactive 3D Digital Twin
- **Approximate Duration:** 35 seconds
- **Spoken Explanation:**
  > *"Using Three.js and WebGL, we built a procedural 3D digital twin of JAIN Global Campus. Users can interactively rotate, zoom, and pan around the campus. The model supports floor isolation slicing—users can lift upper storeys to inspect internal room arrangements.
  >
  > When a route is calculated, the system renders a glowing 3D trajectory spline showing the exact path through corridors and elevator shafts. Importantly, this is a schematic digital twin generated from spatial metadata, not a heavy CAD/BIM model, enabling smooth 60 FPS performance on standard student laptops."*
- **What to Emphasize:** The practical benefits of procedural WebGL rendering—spatial intuition, floor slicing, and lightweight execution.
- **Transition:**
  > *"However, static maps fail when real-world conditions change. Here is how our obstacle reporting system handles live disruptions."*

---

## SLIDE 12 — DYNAMIC OBSTACLE MANAGEMENT
- **Slide Title:** Dynamic Obstacle Reporting & Rerouting
- **Approximate Duration:** 40 seconds
- **Spoken Explanation:**
  > *"When maintenance work, water spills, or broken elevators occur, any student or staff member can submit an obstacle report through the app. To prevent vandalism or false reports from disrupting navigation, reports enter a strict operational lifecycle: Pending, Verified, Resolved, or Rejected.
  >
  > While a report is Pending, it alerts facility staff. Once Field Staff verifies the hazard on site, the navigation engine sets the corresponding edge weight to infinity. Any subsequent route calculation automatically reroutes students around the barrier. Once cleared, staff resolve the ticket, instantly restoring normal traffic."*
- **What to Emphasize:** The operational lifecycle that balances crowdsourced reporting with administrative verification to prevent false disruptions.
- **Transition:**
  > *"Underpinning this entire workflow is a secure, role-based administrative architecture."*

---

## SLIDE 13 — SECURITY, GOVERNANCE & ADMINISTRATION
- **Slide Title:** Security, Governance & Administration
- **Approximate Duration:** 30 seconds
- **Spoken Explanation:**
  > *"Security and data integrity are built into every level of the backend. User authentication utilizes PBKDF2 with 600,000 SHA-256 iterations and unique 32-byte salts, eliminating plaintext password risks.
  >
  > We enforce Role-Based Access Control across three tiers: Students can view routes and report obstacles; Field Staff can verify and resolve hazards; and Administrators manage user roles and review immutable audit logs. In addition, brute-force rate limiting protects accounts from automated attacks."*
- **What to Emphasize:** Enterprise-grade security practices—PBKDF2, RBAC separation, and immutable audit logs.
- **Transition:**
  > *"Let us look at how rigorously this application has been tested and verified."*

---

## SLIDE 14 — VERIFICATION, TEST RESULTS & LIMITATIONS
- **Slide Title:** Verification, Test Results & Limitations
- **Approximate Duration:** 35 seconds
- **Spoken Explanation:**
  > *"Quality assurance has been an ongoing priority. The codebase contains a comprehensive automated test suite of 208 unit and regression tests, achieving a 100% pass rate in approximately 52 seconds. Every algorithm, schema migration, and security policy is continuously validated.
  >
  > In the spirit of academic honesty, we also acknowledge our project limitations: our coordinates are schematic rather than satellite-surveyed GPS; indoor positioning is currently manual waypoint selection; accessibility scores are heuristic; and public cloud hosting is fully containerized and deployment-prepared, awaiting owner OAuth activation."*
- **What to Emphasize:** The 208 passing automated tests and the honest, transparent acknowledgment of limitations.
- **Transition:**
  > *"Finally, let us summarize our achievements and look toward the future."*

---

## SLIDE 15 — CONCLUSION & FUTURE SCOPE
- **Slide Title:** Conclusion & Future Scope
- **Approximate Duration:** 35 seconds
- **Spoken Explanation:**
  > *"In conclusion, Accessible Campus Navigator demonstrates how foundational computer science principles—graph theory, Dijkstra's algorithm, relational databases, and WebGL graphics—can be engineered into an impactful real-world solution for JAIN University. We have bridged outdoor and 5-floor indoor navigation, prioritized accessibility equity, and delivered dynamic resilience.
  >
  > In the future, we plan to integrate Bluetooth Low Energy beacons for live indoor positioning and add synthetic voice guidance for visually impaired students.
  >
  > Thank you very much, professors and evaluators. I am now open to your questions."*
- **What to Emphasize:** Summarize the core engineering contribution, thank the committee warmly, and invite questions with confidence.
