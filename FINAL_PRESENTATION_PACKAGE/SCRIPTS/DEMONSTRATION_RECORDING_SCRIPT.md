# DEMONSTRATION RECORDING SCRIPT & SHOT LIST (5–7 MINUTES)

**Project:** Accessible Campus Navigator — JAIN Global Campus  
**Presenter / Narrator:** Rudra Pratap (USN: `25BTRCL214`)  
**Department:** Artificial Intelligence and Machine Learning  
**Target Video Duration:** 6 minutes 15 seconds  
**Resolution:** 1080p (1920x1080, 60 FPS)  
**Audio Quality:** Crisp microphone voiceover, zero background music  

---

## SHOT LIST & TIMELINE

```
0:00 - 0:40 | Shot 1: Title Screen & System Overview
0:40 - 1:30 | Shot 2: Campus Map & Destination Search
1:30 - 2:30 | Shot 3: Algorithmic Comparison: Dijkstra vs BFS
2:30 - 3:30 | Shot 4: Step-Free Wheelchair Routing & Elevator Guidance
3:30 - 4:25 | Shot 5: Five-Floor FET Indoor Navigation & Room Mapping
4:25 - 5:10 | Shot 6: Interactive 3D Digital Twin & Floor Isolation
5:10 - 5:50 | Shot 7: Obstacle Reporting, Verification & Dynamic Rerouting
5:50 - 6:15 | Shot 8: Administrative Console, Test Proof & Concluding Remarks
```

---

## SHOT-BY-SHOT SCRIPT & ACTIONS

### SHOT 1: TITLE SCREEN & SYSTEM OVERVIEW (0:00 – 0:40)
- **Visual:** Browser showing `http://localhost:8501` on the **Dashboard** (`pages/dashboard.py`). Cursor smoothly points to the hero welcome banner and the 4 KPI cards.
- **Action:**
  - Hover cursor over "79 Campus Locations" and "106 Total Pathways" KPI cards.
  - Scroll down slightly to show the barrier distribution by floor chart.
- **Voiceover:**
  > *"Welcome to the technical demonstration of Accessible Campus Navigator, developed for JAIN Global Campus and the Faculty of Engineering and Technology. This system provides intelligent, accessible wayfinding across 79 physical locations and 106 pathways. Every metric shown on this dashboard is computed directly from our spatial graph and operational database."*

---

### SHOT 2: CAMPUS MAP & DESTINATION SEARCH (0:40 – 1:30)
- **Visual:** Transition to **Find Accessible Route** (`pages/navigation.py`).
- **Action:**
  - Click on the Destination dropdown.
  - Type `Audi` to demonstrate real-time autocomplete filtering.
  - Select `FET Auditorium (Ground Floor)`.
  - Origin set to `Main Entrance Gate`.
  - Click `Calculate Route`.
- **Voiceover:**
  > *"To plan a journey, the student selects an origin and destination. The system indexes outdoor walkways, academic buildings, and indoor laboratories. When we calculate the route from the Main Entrance Gate to the FET Auditorium, the navigation engine executes in under two milliseconds, outputting turn-by-turn guidance, distance in meters, estimated walk time, and cardinal compass bearings."*

---

### SHOT 3: ALGORITHMIC COMPARISON: DIJKSTRA VS BFS (1:30 – 2:30)
- **Visual:** Route comparison panel in `pages/navigation.py`.
- **Action:**
  - Select "Compare Both Algorithms (BFS vs Dijkstra)".
  - Click `Recalculate`.
  - Zoom in on side-by-side metric comparison cards.
- **Voiceover:**
  > *"Here we examine our algorithmic comparison. Breadth-First Search traverses unweighted edges, seeking the fewest transitions. It finds a path with 6 hops covering 465 meters. Dijkstra's algorithm utilizes a min-priority queue with edge weights reflecting physical distance and incline. Dijkstra identifies a 7-node path covering only 420 meters. This side-by-side evidence shows why weighted routing is essential for real-world pedestrian navigation."*

---

### SHOT 4: STEP-FREE WHEELCHAIR ROUTING (2:30 – 3:30)
- **Visual:** Navigation settings and multi-floor routing.
- **Action:**
  - Change destination to `Machine Learning Lab (Second Floor)`.
  - Calculate standard route: point out the Central Staircase step.
  - Toggle the checkbox `♿ Wheelchair Accessible Only`.
  - Click `Recalculate Route`.
  - Point out that the staircase is replaced with the North Passenger Elevator, and the accessibility score updates to 95/100.
- **Voiceover:**
  > *"When a user enables Wheelchair Accessible mode, our accessibility engine dynamically prunes all staircase edges from the active graph. Notice how the route changes: the staircase is completely bypassed, and the student is routed through the ground-floor corridor to the North Passenger Elevator, ascending to Floor 2 without encountering a single step. The route achieves a 95% step-free accessibility rating."*

---

### SHOT 5: FIVE-FLOOR FET INDOOR NAVIGATION (3:30 – 4:25)
- **Visual:** Transition to **Campus Map** (`pages/campus_map.py`) in indoor FET mode.
- **Action:**
  - Click floor buttons in sequence: `Ground Floor (0)`, `First Floor (1)`, `Second Floor (2)`, `Third Floor (3)`, `Fourth Floor (4)`.
  - Hover over specific lab pins (AIML Lab, Robotics Center, Wind Tunnel).
- **Voiceover:**
  > *"Our Five-Floor FET Indoor Navigation system decomposes the building into discrete spatial coordinate slices. Each floor plan highlights departmental laboratories and vertical connection spines. Whether a student is heading to the Fluid Mechanics lab on Ground Floor or the Aeronautical Wind Tunnel on the 4th floor, the vertical graph connections seamlessly link multi-storey indoor spaces."*

---

### SHOT 6: INTERACTIVE 3D DIGITAL TWIN (4:25 – 5:10)
- **Visual:** Transition to **3D Campus Map** (`pages/3d_campus_map.py`).
- **Action:**
  - Click and drag mouse to rotate camera 360 degrees around the campus.
  - Scroll wheel to zoom in on the FET Building.
  - Click `Isolate Floor 2` button to demonstrate floor slicing.
  - Show the glowing green route spline connecting ground level to the second-floor lab.
- **Voiceover:**
  > *"Using Three.js and WebGL, our interactive 3D digital twin provides spatial intuition before walking. The user can rotate, tilt, and zoom across the campus. When we activate floor isolation, upper storeys lift away, revealing the interior second-floor corridor. The glowing spline traces the exact 3D Dijkstra path output by our routing solver, running at a smooth 60 frames per second."*

---

### SHOT 7: DYNAMIC OBSTACLE MANAGEMENT (5:10 – 5:50)
- **Visual:** Transition to **Obstacle Reports** (`pages/obstacle_reports.py`).
- **Action:**
  - Fill out a hazard report: select pathway `Ground Floor Corridor near Central Staircase`.
  - Severity: `High`.
  - Click `Submit Obstacle Report`. Show `Pending` status.
  - Switch to Field Staff review view: verify the report.
  - Return to route finder and recalculate: show how the route immediately diverts around the blocked hallway.
- **Voiceover:**
  > *"When hazards occur, students submit obstacle reports. Reports begin in Pending status to prevent false disruptions. Once Field Staff verifies the hazard on site, the edge weight is set to infinity in memory, instantly severing the path. Notice that when we recalculate, the route automatically diverts through the South Corridor, keeping students safe from active hazards."*

---

### SHOT 8: ADMINISTRATIVE CONSOLE & CONCLUDING REMARKS (5:50 – 6:15)
- **Visual:** Administrative Console (`pages/admin_management.py`), showing role management and immutable audit logs.
- **Action:**
  - Scroll through the audit log table.
  - Show terminal window with `python -m unittest discover tests -v` displaying `Ran 208 tests ... OK`.
- **Voiceover:**
  > *"The administrative console enforces Role-Based Access Control and immutable audit logging backed by PBKDF2 password hashing. With 208 passing automated tests and clean architectural separation, Accessible Campus Navigator proves that computer science and accessibility engineering can combine to make our university inclusive for everyone. Thank you."*

---

## VIDEO ENCODING & EXPORT GUIDELINES
- Format: MP4 (H.264 video, AAC audio).
- Target File Size: Under 45 megabytes for easy distribution via USB or campus portals.
- Naming: `FINAL_PRESENTATION_PACKAGE/BACKUP/FINAL_PRESENTATION_DEMO_VIDEO.mp4`.
