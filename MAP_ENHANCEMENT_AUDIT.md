# ACCESSIBLE CAMPUS NAVIGATOR
## MAP UX, VISUAL CLARITY & PERFORMANCE ENHANCEMENT AUDIT

**Project:** Accessible Campus Navigator  
**Student:** Rudra Pratap (USN: 25BTRCL214) | JAIN (Deemed-to-be University)  
**Date:** 2026-11-22  
**Current Branch:** `main` | **Target Milestone:** Map UX, Visual Clarity & Performance Enhancement  
**Baseline Test Status:** 190 Automated Tests Passing (0 Failures, 0 Errors)

---

## 1. EXECUTIVE AUDIT & PROBLEM DIAGNOSIS

The Accessible Campus Navigator features a comprehensive backend routing engine (Dijkstra, BFS), dynamic SQLite obstacle synchronization, and a Three.js 3D digital twin. However, an in-depth audit of the user interface, visual presentation, and interaction flow across both the **3D Campus Map** and the **2D Campus Map** revealed critical usability, clarity, and performance bottlenecks:

### 1.1 3D Campus Map Bottlenecks (`pages/3d_campus_map.py` & `modules/jain_digital_twin.py`)
1. **Severe Label Clutter & Text Overlap:**
   - *Symptom:* In the default isometric view, up to 79 text sprites are rendered simultaneously. Because sprites were created with `depthTest: false`, all room labels from lower and upper floors bleed through solid concrete slabs, creating an overlapping, unreadable cluster of text.
   - *Root Cause:* Absence of distance-based Level-of-Detail (LOD), absence of screen-space density filtering, and lack of floor-visibility culling for billboarding sprites.
2. **Suboptimal Default Camera Framing & Perspective:**
   - *Symptom:* The default camera is positioned far away at `(110, 120, 140)` with look-at `(10, 8, 10)`. The 5-floor circular FET building appears small, skewed, and visually crowded with excessive background expanse.
   - *Root Cause:* Camera coordinate presets were set without bounding-box fitting around the FET central rotunda and core campus spine.
3. **Dark Lighting & Architectural Indistinctness:**
   - *Symptom:* Building slabs, corridors, and room volumes appear excessively dark (`0x22362C`, `0x0E261D`) with low ambient lighting, making indoor navigation pathways hard to distinguish from walls.
   - *Root Cause:* Lighting relies heavily on dark directional fill lights without a soft sky-to-ground hemisphere light; material roughness and diffuse colors absorb too much light.
4. **Scattered Top HUD Controls (20 Buttons):**
   - *Symptom:* The Three.js canvas header contained 5 separate button groups with 20 individual buttons wrapping into multiple jagged rows, confusing first-time student users.
   - *Root Cause:* Controls for camera presets, domain views, cutaway styles, floor filters, and route animation were placed as separate raw button lists rather than a compact, structured toolbar.
5. **Cramped Streamlit Controls Column & Panel Clipping:**
   - *Symptom:* The Streamlit page was split into `[2.3, 1.0]`, forcing Route Planning, Destination Search, Facility Inspector, and Hazard lists into a narrow ~300px sidebar where dropdown labels and buttons wrap awkwardly or clip.
   - *Root Cause:* Lack of responsive layout proportioning and lack of tabbed/accordion segmentation for secondary inspection cards.
6. **WebGL Performance & Memory Overhead:**
   - *Symptom:* High draw-call count, 79 distinct canvas textures generated on every scene initialization, and animation frame loops executing continuous matrix recalculations even when the camera is stationary.
   - *Root Cause:* Textures and geometries were not properly pooled or cached, and sprite visibility was recalculated redundantly every frame.

### 1.2 2D Campus Map Bottlenecks (`pages/campus_map.py` & `modules/indoor_map.py`)
1. **Model Disconnect (15-Node Benchmark vs 79-Location Campus):**
   - *Symptom:* The 2D map page was hardcoded to only display the legacy 15-node benchmark model (`cmap = services["campus_map"]`). Users could not explore the full 79-location JAIN Global Campus & 5-Floor FET Building in 2D!
   - *Root Cause:* Lack of environment switching in `pages/campus_map.py` and lack of multi-floor layout coordinate mappings for the 5-floor FET complex in `modules/indoor_map.py`.
2. **Abstract Graph Appearance instead of Architectural Map:**
   - *Symptom:* Nodes were rendered as generic scatter dots with thin raw lines, giving the impression of an abstract math graph rather than an intuitive campus floor plan.
   - *Root Cause:* Absence of architectural zone boundary shapes, corridor width styling, room category iconography (🚪, 🛗, 🪜, 🔬, 📚, 🚻), and directional wayfinding arrows.
3. **Cumbersome Floor Level Navigation:**
   - *Symptom:* Floor filter was restricted to "All Floors", "Floor 0", and "Floor 1", with side-by-side display of only two floors, completely lacking support for Floors 2, 3, 4, and Outdoor grounds.
   - *Root Cause:* Floor level parser assumed maximum floor index of 1.

---

## 2. REPOSITORY & FILE AUDIT

| File Inspected | Role in Navigation Experience | Current Status & Audit Findings |
| :--- | :--- | :--- |
| `pages/3d_campus_map.py` | 3D Map Presentation Page | Column width `[2.3, 1.0]` cramps controls; lacks streamlined toolbar; search match selection is separated from route inputs. |
| `modules/jain_digital_twin.py` | Three.js WebGL Engine & Shader Canvas | 20 scattered HUD buttons; 79 overlapping billboarding sprites with `depthTest: false`; dark lighting; lack of distance LOD. |
| `pages/campus_map.py` | 2D Interactive Map Page | Hardcoded to 15-node benchmark; missing 79-node JAIN campus; floor filter limited to 2 floors; layout lacks architectural clarity. |
| `modules/indoor_map.py` | Plotly Cartography Engine | Renders bare node dots; lacks room glyphs/icons, clear corridor outlines, and 5-floor JAIN campus support. |
| `modules/destination_search.py` | Room & Facility Intelligence Engine | Robust multi-field search engine exists; needs tighter UI integration for auto-centering, live suggestions, and 1-click routing. |
| `modules/ui_theme.py` | Design System & Styling | Dark-green palette established; needs responsive styling adjustments for compact map toolbars and inspect panels. |

---

## 3. ROOT CAUSE ANALYSIS & PLANNED ENHANCEMENTS

### Strategy 1: Intelligent 3D Labeling & Camera System
- **Distance-Based Level-of-Detail (LOD):**
  - Far/Campus View ($dist > 120$m): Only display key building/landmark labels (Main Entrance, FET Complex, Hostels, Sports Arena).
  - Medium View ($60\text{m} < dist \le 120\text{m}$): Show major wings, vertical cores (Elevators, Stairs), and primary halls.
  - Close/Inspection View ($dist \le 60$m): Show individual room and laboratory labels for the currently visible floor.
- **Occlusion & Active Floor Filtering:**
  - When viewing Floor $k$, strictly cull labels from all other floors.
  - Enable `depthTest: true` with gentle depth write to prevent lower-floor labels from shining through upper-floor concrete slabs.
- **Priority Pinning:**
  - Selected inspect target, route origin (🟢), route destination (🏁), and active detour points ALWAYS remain visible regardless of zoom level.
- **Optimized Default Camera Angle:**
  - Position camera at an intuitive 45° isometric viewpoint centered on the FET building rotunda: `camera.position.set(60, 52, 70); controls.target.set(0, 10, 0);`
  - Smooth camera transition tweening with ease-out interpolation (`lerp`).

### Strategy 2: Streamlined Map Toolbar & Clean Viewport Layout
- **Unified Compact Map Toolbar:**
  - Replace the 20 scattered buttons with a clean, segmented 4-group HUD:
    1. **View:** 2D ↔ 3D Toggle
    2. **Campus Area:** All Campus | Outdoor | FET Building
    3. **Floor Selector:** Compact pill strip: `All | G | 1F | 2F | 3F | 4F`
    4. **Camera:** Default | Top | Front | Auto-Rotate | Reset View
- **Balanced Page Proportions:**
  - Rebalance Streamlit layout to `[2.8, 1.2]` on wide screens with collapsible cards, expanding map visibility while keeping route planning clean and comfortable.

### Strategy 3: Professional 2D Architectural Cartography
- **Support Full 79-Location JAIN Campus in 2D:**
  - Allow switching between JAIN Global Campus (79 locations, 5 floors + outdoor) and the benchmark complex.
- **Architectural Floor Plan Visuals:**
  - Add room zone floor boundaries, wide corridor traces, and high-visibility step-free pathways.
  - Distinctive facility symbols: 🚪 Entrances, 🛗 Elevators, 🪜 Stairs, 🔬 Laboratories, 📚 Libraries, 🚻 Restrooms, 🏛️ Dean/Admin, 💻 HPC.
  - Interactive selection highlight connecting 2D map clicks directly to the Location Inspector and Route Planner.

### Strategy 4: High-Performance WebGL Optimization
- Reuse shared Three.js materials and geometries.
- Throttle label visibility computations to camera move events rather than unconditional per-frame execution.
- Add WebGL context disposal logic upon iframe destruction to prevent browser VRAM accumulation.
- Respect system `prefers-reduced-motion` settings.

---

## 4. VERIFICATION CRITERIA
1. **Zero Regressions:** All 190 automated unit tests must continue passing.
2. **Visual Inspection:** Verify in live browser that labels no longer overlap, camera framing is clear, and 2D/3D switching works seamlessly.
3. **Code Safety:** Zero destructive git actions, zero data loss, and complete preservation of real campus coordinate data.
