# FINAL 7-TO-10 MINUTE LIVE DEMONSTRATION SCRIPT

**Project:** Accessible Campus Navigator — JAIN Global Campus  
**Presenter:** Rudra Pratap (USN: `25BTRCL214`)  
**Department:** Artificial Intelligence and Machine Learning  
**Target Duration:** 8 minutes 30 seconds (Paced for 7–10 minute demonstration slot)  
**Live Application URL:** `http://localhost:8501`  

---

## TIMELINE OVERVIEW

```
0:00 - 0:45 | Part 1: Introduction, Problem Statement & Dashboard
0:45 - 1:45 | Part 2: Campus Map & Spatial Graph Navigation
1:45 - 3:15 | Part 3: Algorithmic Comparison — BFS vs Dijkstra
3:15 - 4:45 | Part 4: Wheelchair-Accessible Routing & Heuristic Scoring
4:45 - 6:15 | Part 5: Five-Floor FET Indoor Navigation & Vertical Transitions
6:15 - 7:15 | Part 6: Interactive 3D Digital Twin & Floor Slicing
7:15 - 8:15 | Part 7: Dynamic Obstacle Reporting & Graph Rerouting
8:15 - 9:00 | Part 8: Administrative Console, Audit Logging & Analytics
9:00 - 9:30 | Part 9: Conclusion & Engineering Summary
```

---

## PART 1 — INTRODUCTION & DASHBOARD (0:00 – 0:45)

### Actions & Navigation
1. Open Chrome/Edge at `http://localhost:8501`.
2. Ensure you are on the **Dashboard** (`pages/dashboard.py`).
3. Scroll slightly so the **Hero Welcome Banner** and the top 4 KPI cards are fully visible.

### Speaking Script
> *"Good morning, respected professors and evaluators. My name is Rudra Pratap, USN 25BTRCL214, from the Department of Artificial Intelligence and Machine Learning. Today, I am proud to demonstrate the **Accessible Campus Navigator**, designed specifically for our JAIN Global Campus and the Faculty of Engineering and Technology.*
>
> *Navigating large university campuses is a daily challenge, especially for first-year students, visitors, and individuals with mobility impairments. Staircases, broken pathways, and temporary obstacles can turn an ordinary 5-minute walk into a major barrier.*
>
> *Here on the main dashboard, you can see our real-time spatial metrics: 79 campus locations, 106 mapped pathways across 5 building floors, with over 72% currently verified as step-free accessible. Every metric you see here is calculated directly from our spatial graph and operational database—not simulated estimates."*

### Expected Result
- Dark-forest-green dashboard loads cleanly with 4 KPI cards: Campus Locations (79), Total Pathways (106), Step-Free Pathways (76), Active Obstacles (0 or low count).

### Recovery If Needed
- If the dataset radio button is set to "Schematic Benchmark", toggle it to "JAIN Global Campus & FET 5-Floor Digital Twin".

---

## PART 2 — CAMPUS NAVIGATION & SPATIAL GRAPH (0:45 – 1:45)

### Actions & Navigation
1. In the left sidebar, click on **Find Accessible Route** (`pages/navigation.py`).
2. Point out the Origin and Destination dropdown menus.
3. Select:
   - **Origin:** `Main Entrance Gate`
   - **Destination:** `FET Auditorium (Ground Floor)`
4. Leave "Wheelchair Accessible" unchecked for this first search.
5. Click **Calculate Route**.

### Speaking Script
> *"Let us look at how the navigation engine operates. We model the campus as an undirected, weighted graph $G = (V, E)$, where vertices $V$ represent physical landmarks—such as entrance gates, departments, laboratories, and elevators—and edges $E$ represent navigable pathways.*
>
> *When I request a route from the Main Entrance Gate to the FET Auditorium, the application traverses the graph, determines the continuous path, and outputs the turn-by-turn wayfinding instructions. Notice that the system provides the physical distance—420 meters—estimated walking time, elevation changes, and detailed navigational waypoints."*

### Expected Result
- Route appears with step-by-step turn cards, total distance, and time estimate.

### Recovery If Needed
- If dropdown does not respond immediately, ensure the selection is committed (click outside or press Enter).

---

## PART 3 — ALGORITHMIC COMPARISON: BFS VS DIJKSTRA (1:45 – 3:15)

### Actions & Navigation
1. Under the route configuration panel, locate the **Routing Algorithm** selector.
2. Select **Compare Both Algorithms (BFS vs Dijkstra)**.
3. Click **Recalculate**.
4. Scroll to the comparison table and side-by-side metric cards.

### Speaking Script
> *"One of the primary computer science contributions of this project is our dual-algorithm routing engine. Here we compare Breadth-First Search and Dijkstra's Algorithm.*
>
> *Breadth-First Search explores the campus graph level-by-level, treating all edges as unweighted. It finds the path with the minimum number of edge transitions—in this case, 6 transitions.*
>
> *However, minimum transitions do not necessarily mean minimum physical walking distance. Dijkstra's Algorithm uses a min-priority queue to explore paths based on non-negative edge weights—incorporating physical distance and surface gradients.*
>
> *As you can see on screen, Dijkstra identified a route of 420 meters, whereas unweighted BFS selected a 465-meter route because it crossed fewer corridor segments. This proves why weighted graph modeling is essential for realistic pedestrian wayfinding."*

### Expected Result
- Side-by-side comparison cards display:
  - Dijkstra: Total Distance 420 m | 7 Nodes Traversed | Optimal weighted cost.
  - BFS: Total Distance 465 m | 6 Nodes Traversed | Fewest edge hops.

### Recovery If Needed
- If both yield identical distance for a simple route, select `Hostel Block A` to `Robotics & AI Research Lab` to clearly demonstrate the divergence.

---

## PART 4 — WHEELCHAIR-ACCESSIBLE ROUTING & HEURISTICS (3:15 – 4:45)

### Actions & Navigation
1. Keep the destination as a multi-floor target:
   - **Origin:** `FET Main Foyer (Ground Floor)`
   - **Destination:** `Machine Learning Lab (Second Floor)`
2. First, click **Calculate Route** without wheelchair mode. Point out that the standard route uses the **Central Staircase**.
3. Now, check the box: **♿ Wheelchair Accessible Only**.
4. Click **Recalculate Route**.

### Speaking Script
> *"Now let us examine our accessibility engine. For a student using a wheelchair or carrying heavy equipment, stairs are an impassable barrier.*
>
> *When we enable 'Wheelchair Accessible Only', the engine activates our accessibility filter. It constructs a constrained subgraph $G' = (V, E')$, dynamically pruning any edge categorized as a staircase ($E_{stairs} \subset E$).*
>
> *Watch what happens: the standard route directed us up the Central Staircase. But with accessibility mode enabled, the algorithm routes the student along the ground floor corridor to the **FET North Passenger Elevator**, takes the elevator up to the Second Floor, and exits directly into the Computer Science wing.*
>
> *Our accessibility heuristic also calculates a route confidence score from 0 to 100 based on doorway widths, ramp inclinations, and paved surfaces. This route achieves a 95% accessibility score because it is 100% step-free."*

### Expected Result
- Visual route changes: Staircase icon 🪜 is replaced with Elevator icon 🛗.
- The step list shows "Take North Passenger Elevator from Floor 0 to Floor 2".
- Accessibility Score displays: `95/100 (Step-Free Verified)`.

### Recovery If Needed
- If elevator route is blocked, check that the obstacle database was not left with active elevator blocks from earlier testing.

---

## PART 5 — FIVE-FLOOR FET INDOOR NAVIGATION (4:45 – 6:15)

### Actions & Navigation
1. In the sidebar, click on **Campus Map** (`pages/campus_map.py`).
2. Switch view to **FET Building Indoor View**.
3. Use the **Floor Selector** buttons: click `Ground Floor (0)`, then `First Floor (1)`, then `Second Floor (2)`, then `Third Floor (3)`.
4. Point out the laboratory locations, faculty cabins, and vertical connectors.

### Speaking Script
> *"Outdoor navigation ends at the building entrance, but university life happens indoors. Here, we present our Five-Floor FET Indoor Navigation system.*
>
> *Each floor plan is mapped as a discrete coordinate plane. On Ground Floor, we have the Administrative offices and Mechanical workshops. On Floor 1, Electronics and Circuit labs. On Floor 2, AIML and Computer Science laboratories. On Floor 3 and 4, advanced research centers and aeronautical labs.*
>
> *What makes our model powerful is how vertical connectors—elevators and stairs—bridge these separate 2D planes into a unified 3D graph. When a path is calculated between different floors, the system computes the exact indoor corridor traversal on Floor 1, transitions vertically through the elevator node, and seamlessly resumes horizontal pathing on Floor 3."*

### Expected Result
- Interactive 2D map cleanly updates floor plans as buttons are clicked.
- Color-coded pins highlight classrooms, laboratories, restrooms, and accessible ramps.

---

## PART 6 — INTERACTIVE 3D DIGITAL TWIN (6:15 – 7:15)

### Actions & Navigation
1. In the sidebar, click on **3D Campus Map** (`pages/3d_campus_map.py`).
2. In the 3D WebGL viewport:
   - Left-click and drag to rotate the camera around the campus.
   - Scroll wheel to zoom in on the FET Building.
   - Click the **Isolate Floor 2** button.
3. Show the glowing route spline connecting the entrance to the second-floor lab.

### Speaking Script
> *"To provide spatial intuition beyond flat 2D maps, we engineered an interactive 3D Digital Twin using Three.js and WebGL.*
>
> *I can smoothly rotate the campus view, inspect building elevations, and examine surrounding pathways. When we activate 'Floor Isolation', the upper floors become transparent or lift away, revealing the interior corridor corridors of Floor 2.*
>
> *Notice the glowing 3D navigational spline: it traces the exact coordinates output by our Dijkstra graph solver, illustrating both horizontal motion through hallways and vertical elevation through the elevator shaft.*
>
> *We want to be transparent: this 3D model is a schematic digital twin derived from building dimensions and floor diagrams, rather than an expensive laser-scanned architectural BIM model. This ensures it loads in under two seconds on standard student laptops without requiring specialized GPU hardware."*

### Expected Result
- High-performance 60 FPS WebGL rendering.
- OrbitControls respond smoothly to mouse dragging and zooming.
- Floor isolation visually separates the building storeys.

### Recovery If Needed
- If WebGL canvas is slow on projector, click "Toggle Low Overhead Mode" or reload the page.

---

## PART 7 — DYNAMIC OBSTACLE REPORTING (7:15 – 8:15)

### Actions & Navigation
1. In the sidebar, click on **Obstacle Reports** (`pages/obstacle_reports.py`).
2. Fill out a sample report:
   - **Target Pathway / Location:** `Ground Floor Corridor near Central Staircase`
   - **Obstacle Type:** `Floor Maintenance / Water Leakage`
   - **Severity:** `High (Path Completely Blocked)`
   - **Description:** `Maintenance work in progress. Pathway temporarily impassable.`
3. Click **Submit Obstacle Report**.
4. Show confirmation message: "Report #... submitted with status: PENDING".
5. Briefly explain the Field Staff verification step:
   - Pending reports do NOT immediately block the map to prevent vandalism.
   - Once Field Staff or Admin marks it **Verified**, the engine marks the edge weight as infinite ($\infty$), forcing immediate dynamic rerouting.

### Speaking Script
> *"Real campuses are dynamic environments. Construction, cleaning, or broken elevators can suddenly block an accessible route.*
>
> *Here, any student or staff member can report an obstacle. I have just submitted a report for water maintenance near the Central Staircase.*
>
> *To prevent false reports or student pranks from disrupting navigation, we implemented a strict operational lifecycle: Pending, Verified, Resolved, or Rejected. A pending report alerts campus supervisors, but the graph remains open until Field Staff verifies the issue on the ground.*
>
> *Once verified, the navigation engine immediately severs the edge in memory. Any subsequent route calculation will dynamically reroute students through the South Corridor, avoiding the hazard completely."*

### Expected Result
- Success alert: "Obstacle report recorded in database".
- Active obstacle table reflects the new record with yellow `Pending` badge.

---

## PART 8 — ADMINISTRATIVE CONSOLE & ANALYTICS (8:15 – 9:00)

### Actions & Navigation
1. In the sidebar, click on **Administrative Console** (`pages/admin_management.py`).
   *(If prompted, demonstrate admin privileges).*
2. Show:
   - **User Role Management:** Student, Field Staff, Administrator role switcher.
   - **Audit Logs Table:** Show recent entries with timestamps, user IDs, and actions.
3. Switch back to **Dashboard** (`pages/dashboard.py`) and scroll to the bottom **Analytics** charts:
   - Barrier distribution by floor.
   - Obstacle resolution time statistics.

### Speaking Script
> *"Behind the user interface is a secure enterprise backend. Our administrative console enforces Role-Based Access Control using PBKDF2-HMAC-SHA256 password hashing and session tokens.*
>
> *Every administrative action—verifying an obstacle, resolving a ticket, or modifying user permissions—is committed to an immutable audit log table in SQLite with ISO timestamps.*
>
> *Furthermore, our campus analytics engine aggregates barrier frequencies, enabling campus facilities management to identify chronic problem areas—such as recurring elevator outages—and prioritize accessibility infrastructure investments."*

### Expected Result
- Admin dashboard shows secure user management table and immutable audit log rows.
- Analytics charts render barrier distributions and pathway statistics cleanly.

---

## PART 9 — CONCLUSION & ENGINEERING SUMMARY (9:00 – 9:30)

### Actions & Navigation
1. Return to the **Dashboard** welcome screen.
2. Address the panel of evaluators directly.

### Speaking Script
> *"To conclude: Accessible Campus Navigator demonstrates how foundational computer science principles—graph theory, Dijkstra's algorithm, relational database design, and interactive 3D graphics—can be engineered into an impactful real-world solution.*
>
> *With 79 locations, 106 pathways, five-floor indoor navigation, dynamic obstacle rerouting, and 208 passing automated tests, we have built a dependable, accessible platform that helps JAIN University become more inclusive for all students and visitors.*
>
> *Thank you very much. I am now open to your questions."*

---

## RAPID RECOVERY MATRIX FOR DEMONSTRATION

| Issue | Quick Fix |
|---|---|
| Page is blank / reloaded | Press browser Back or click `Dashboard` in sidebar. Session state persists. |
| Selected route says "No Path Found" | Ensure you haven't blocked both the stairs AND the elevator on that wing. |
| Projector cuts off right side | Zoom browser out to 90% (`Ctrl` + `-`). |
| Database lock warning | Refresh page; SQLite WAL mode automatically releases locks within 5 seconds. |
