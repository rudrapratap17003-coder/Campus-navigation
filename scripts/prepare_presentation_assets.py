"""Prepare and organize all diagrams, screenshots, and indexes for the Final Presentation Package."""

import shutil
from pathlib import Path
from PIL import Image, ImageDraw

base_dir = Path.cwd()
pkg_dir = base_dir / "FINAL_PRESENTATION_PACKAGE"
diag_dir = pkg_dir / "DIAGRAMS"
shots_dir = pkg_dir / "SCREENSHOTS"
orig_diag = base_dir / "PROJECT_ARCHITECTURE_DIAGRAMS"
demo_shots = base_dir / "DEMONSTRATION_SCREENSHOTS"
uat_shots = base_dir / "FINAL_UAT_EVIDENCE"

# Ensure target directories exist
for sub in [
    "system_architecture",
    "algorithms",
    "database",
    "workflows",
]:
    (diag_dir / sub).mkdir(parents=True, exist_ok=True)

for sub in [
    "dashboard",
    "navigation",
    "accessibility",
    "indoor",
    "digital_twin",
    "obstacle_management",
    "administration",
]:
    (shots_dir / sub).mkdir(parents=True, exist_ok=True)

# 1. Map existing diagrams from PROJECT_ARCHITECTURE_DIAGRAMS
diag_mapping = {
    "system_architecture/01_overall_system_architecture": "01_overall_system_architecture",
    "system_architecture/02_campus_graph_representation": "02_campus_graph_representation",
    "algorithms/03_bfs_workflow": "03_bfs_workflow",
    "algorithms/04_dijkstra_workflow": "04_dijkstra_workflow",
    "algorithms/05_wheelchair_accessible_routing": "05_wheelchair_accessible_routing",
    "workflows/06_obstacle_reporting_lifecycle": "06_obstacle_reporting_lifecycle",
    "workflows/07_authentication_and_rbac": "07_authentication_and_rbac",
    "database/10_database_relationships_erd": "08_database_relationships_er",
}

for dest, src in diag_mapping.items():
    for ext in [".svg", ".png"]:
        s = orig_diag / f"{src}{ext}"
        d = (diag_dir / dest).with_suffix(ext)
        if s.exists():
            shutil.copy2(s, d)

# 2. Generate 08_five_floor_indoor_structure SVG
svg_indoor = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 600" width="1000" height="600">
  <rect width="1000" height="600" fill="#07130F" rx="16"/>
  <text x="500" y="45" fill="#35D99A" font-family="Segoe UI, Arial, sans-serif" font-size="24" font-weight="bold" text-anchor="middle">Five-Floor FET Building Indoor Navigation Structure</text>
  <text x="500" y="75" fill="#9CAFA5" font-family="Segoe UI, Arial, sans-serif" font-size="14" text-anchor="middle">Multi-Storey 2D Coordinate Slices Connected via Vertical Transition Edges</text>
  
  <rect x="440" y="110" width="120" height="440" fill="#0D1F18" stroke="#16A36A" stroke-width="2" stroke-dasharray="6 4" rx="8"/>
  <text x="500" y="135" fill="#35D99A" font-family="Segoe UI, Arial, sans-serif" font-size="13" font-weight="bold" text-anchor="middle">VERTICAL SPINE</text>
  <text x="500" y="155" fill="#A7F3D0" font-family="Segoe UI, Arial, sans-serif" font-size="11" text-anchor="middle">Elevators (Step-Free)</text>
  <text x="500" y="175" fill="#F5B942" font-family="Segoe UI, Arial, sans-serif" font-size="11" text-anchor="middle">Staircases (Standard)</text>

  <rect x="60" y="120" width="350" height="65" fill="#122820" stroke="#16A36A" stroke-width="1.5" rx="6"/>
  <text x="80" y="150" fill="#F8FAFC" font-family="Segoe UI, Arial" font-size="14" font-weight="bold">Floor 4: Aeronautical and Prop. Labs</text>
  <text x="80" y="170" fill="#9CAFA5" font-family="Segoe UI, Arial" font-size="11">Advanced UAV Lab - Wind Tunnel - Research Cabins</text>
  <line x1="410" y1="152" x2="440" y2="152" stroke="#35D99A" stroke-width="2"/>

  <rect x="60" y="205" width="350" height="65" fill="#122820" stroke="#16A36A" stroke-width="1.5" rx="6"/>
  <text x="80" y="235" fill="#F8FAFC" font-family="Segoe UI, Arial" font-size="14" font-weight="bold">Floor 3: Civil and Environmental Eng.</text>
  <text x="80" y="255" fill="#9CAFA5" font-family="Segoe UI, Arial" font-size="11">Geotech Lab - Concrete Testing - Seminar Hall C</text>
  <line x1="410" y1="237" x2="440" y2="237" stroke="#35D99A" stroke-width="2"/>

  <rect x="60" y="290" width="350" height="65" fill="#122820" stroke="#35D99A" stroke-width="2" rx="6"/>
  <text x="80" y="320" fill="#35D99A" font-family="Segoe UI, Arial" font-size="14" font-weight="bold">Floor 2: AIML, Data Science and CSE</text>
  <text x="80" y="340" fill="#A7F3D0" font-family="Segoe UI, Arial" font-size="11">HPC Cluster - Robotics Lab - AI Workstations</text>
  <line x1="410" y1="322" x2="440" y2="322" stroke="#35D99A" stroke-width="2"/>

  <rect x="60" y="375" width="350" height="65" fill="#122820" stroke="#16A36A" stroke-width="1.5" rx="6"/>
  <text x="80" y="405" fill="#F8FAFC" font-family="Segoe UI, Arial" font-size="14" font-weight="bold">Floor 1: Electrical and Electronics</text>
  <text x="80" y="425" fill="#9CAFA5" font-family="Segoe UI, Arial" font-size="11">Embedded Systems - VLSI Design - Faculty Lounge</text>
  <line x1="410" y1="407" x2="440" y2="407" stroke="#35D99A" stroke-width="2"/>

  <rect x="60" y="460" width="350" height="65" fill="#122820" stroke="#16A36A" stroke-width="1.5" rx="6"/>
  <text x="80" y="490" fill="#F8FAFC" font-family="Segoe UI, Arial" font-size="14" font-weight="bold">Floor 0 (Ground): Foyer and Administration</text>
  <text x="80" y="510" fill="#9CAFA5" font-family="Segoe UI, Arial" font-size="11">Main Entrance - Dean Office - Auditorium - Cafeteria</text>
  <line x1="410" y1="492" x2="440" y2="492" stroke="#35D99A" stroke-width="2"/>

  <rect x="590" y="120" width="350" height="405" fill="#0D1F18" stroke="#16A36A" stroke-width="1" rx="8"/>
  <text x="765" y="155" fill="#35D99A" font-family="Segoe UI, Arial" font-size="16" font-weight="bold" text-anchor="middle">Graph Modeling Principles</text>
  <text x="615" y="200" fill="#F8FAFC" font-family="Segoe UI, Arial" font-size="13">1. Node Attributes: floor_id in {0, 1, 2, 3, 4}</text>
  <text x="615" y="240" fill="#F8FAFC" font-family="Segoe UI, Arial" font-size="13">2. Horizontal Edges: Connect same-floor rooms</text>
  <text x="615" y="280" fill="#F8FAFC" font-family="Segoe UI, Arial" font-size="13">3. Vertical Edges: edge_type in {'elevator', 'stairs'}</text>
  <text x="615" y="320" fill="#F8FAFC" font-family="Segoe UI, Arial" font-size="13">4. Wheelchair Pruning: Excludes 'stairs' edges</text>
  <text x="615" y="360" fill="#F8FAFC" font-family="Segoe UI, Arial" font-size="13">5. Elevation Cost: Extra edge weight per floor</text>
  <text x="615" y="400" fill="#A7F3D0" font-family="Segoe UI, Arial" font-size="13">6. Unified Graph: Solved natively with Dijkstra</text>
  <rect x="615" y="440" width="300" height="60" fill="#122820" stroke="#35D99A" stroke-width="1" rx="6"/>
  <text x="765" y="465" fill="#35D99A" font-family="Segoe UI, Arial" font-size="12" font-weight="bold" text-anchor="middle">Deterministic Cross-Floor Traversal</text>
  <text x="765" y="485" fill="#9CAFA5" font-family="Segoe UI, Arial" font-size="11" text-anchor="middle">O(E + V log V) Dijkstra execution time</text>
</svg>"""

(diag_dir / "system_architecture" / "08_five_floor_indoor_structure.svg").write_text(svg_indoor, encoding="utf-8")

# 3. Generate 09_3d_digital_twin_architecture SVG
svg_3d = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 600" width="1000" height="600">
  <rect width="1000" height="600" fill="#07130F" rx="16"/>
  <text x="500" y="45" fill="#35D99A" font-family="Segoe UI, Arial, sans-serif" font-size="24" font-weight="bold" text-anchor="middle">3D Digital Twin and WebGL Architecture</text>
  <text x="500" y="75" fill="#9CAFA5" font-family="Segoe UI, Arial, sans-serif" font-size="14" text-anchor="middle">Procedural Three.js Scene Construction from Graph Metadata</text>

  <rect x="50" y="130" width="250" height="180" fill="#122820" stroke="#16A36A" stroke-width="1.5" rx="8"/>
  <text x="175" y="165" fill="#35D99A" font-family="Segoe UI, Arial" font-size="16" font-weight="bold" text-anchor="middle">Spatial Graph Data</text>
  <text x="70" y="200" fill="#F8FAFC" font-family="Segoe UI, Arial" font-size="12">- jain_global_campus.json</text>
  <text x="70" y="230" fill="#F8FAFC" font-family="Segoe UI, Arial" font-size="12">- 79 Nodes (X, Y, Floor)</text>
  <text x="70" y="260" fill="#F8FAFC" font-family="Segoe UI, Arial" font-size="12">- 106 Pathways and Attributes</text>
  <text x="70" y="290" fill="#9CAFA5" font-family="Segoe UI, Arial" font-size="11">Normalized Coordinates</text>

  <line x1="300" y1="220" x2="370" y2="220" stroke="#35D99A" stroke-width="2"/>

  <rect x="370" y="130" width="260" height="180" fill="#122820" stroke="#35D99A" stroke-width="2" rx="8"/>
  <text x="500" y="165" fill="#35D99A" font-family="Segoe UI, Arial" font-size="16" font-weight="bold" text-anchor="middle">Python 3D Serializer</text>
  <text x="390" y="200" fill="#F8FAFC" font-family="Segoe UI, Arial" font-size="12">- modules/three_d_map.py</text>
  <text x="390" y="230" fill="#F8FAFC" font-family="Segoe UI, Arial" font-size="12">- Coordinate Extrusion</text>
  <text x="390" y="260" fill="#F8FAFC" font-family="Segoe UI, Arial" font-size="12">- Route Spline Generation</text>
  <text x="390" y="290" fill="#A7F3D0" font-family="Segoe UI, Arial" font-size="11">Dynamic Obstacle Sync</text>

  <line x1="630" y1="220" x2="700" y2="220" stroke="#35D99A" stroke-width="2"/>

  <rect x="700" y="130" width="250" height="180" fill="#122820" stroke="#16A36A" stroke-width="1.5" rx="8"/>
  <text x="825" y="165" fill="#35D99A" font-family="Segoe UI, Arial" font-size="16" font-weight="bold" text-anchor="middle">Three.js WebGL Engine</text>
  <text x="720" y="200" fill="#F8FAFC" font-family="Segoe UI, Arial" font-size="12">- OrbitControls (Pan/Zoom)</text>
  <text x="720" y="230" fill="#F8FAFC" font-family="Segoe UI, Arial" font-size="12">- Floor Slicing / Isolation</text>
  <text x="720" y="260" fill="#F8FAFC" font-family="Segoe UI, Arial" font-size="12">- Glowing Route Spline</text>
  <text x="720" y="290" fill="#9CAFA5" font-family="Segoe UI, Arial" font-size="11">60 FPS Interactive Canvas</text>

  <rect x="50" y="350" width="900" height="200" fill="#0D1F18" stroke="#16A36A" stroke-width="1" rx="8"/>
  <text x="500" y="385" fill="#35D99A" font-family="Segoe UI, Arial" font-size="16" font-weight="bold" text-anchor="middle">Digital Twin Capabilities and Academic Scope</text>
  <text x="80" y="425" fill="#F8FAFC" font-family="Segoe UI, Arial" font-size="13">1. Schematic Digital Twin: Built procedurally from room coordinates and campus building footprints.</text>
  <text x="80" y="460" fill="#F8FAFC" font-family="Segoe UI, Arial" font-size="13">2. Low Overhead: Operates without requiring high-end discrete GPUs; runs smoothly in standard browsers.</text>
  <text x="80" y="495" fill="#F8FAFC" font-family="Segoe UI, Arial" font-size="13">3. Synchronized State: When obstacles are verified in SQLite, the 3D pathway wireframe dynamically changes color.</text>
  <text x="80" y="530" fill="#A7F3D0" font-family="Segoe UI, Arial" font-size="13">4. Honest Distinction: Schematic 3D mesh for wayfinding intuition, NOT a surveyed architectural BIM CAD model.</text>
</svg>"""

(diag_dir / "system_architecture" / "09_3d_digital_twin_architecture.svg").write_text(svg_3d, encoding="utf-8")

# PNG fallbacks for 08 and 09
for fname, title, sub in [
    ("system_architecture/08_five_floor_indoor_structure.png", "Five-Floor FET Indoor Navigation Structure", "Multi-Floor Coordinate Slices Connected via Elevators and Stairs"),
    ("system_architecture/09_3d_digital_twin_architecture.png", "3D Digital Twin and WebGL Architecture", "Procedural Three.js Scene Construction from Graph Metadata")
]:
    img = Image.new("RGB", (1000, 600), color="#07130F")
    d = ImageDraw.Draw(img)
    d.rectangle([20, 20, 980, 580], outline="#16A36A", width=2)
    d.text((500, 60), title, fill="#35D99A", anchor="mm")
    d.text((500, 95), sub, fill="#9CAFA5", anchor="mm")
    d.rectangle([60, 140, 440, 520], fill="#122820", outline="#35D99A", width=2)
    d.text((250, 180), "FET Multi-Floor Spatial Slices", fill="#F8FAFC", anchor="mm")
    d.text((250, 240), "Floor 4: Aeronautical Labs", fill="#A7F3D0", anchor="mm")
    d.text((250, 300), "Floor 3: Civil and Environmental", fill="#A7F3D0", anchor="mm")
    d.text((250, 360), "Floor 2: AIML, Data Science and CSE", fill="#A7F3D0", anchor="mm")
    d.text((250, 420), "Floor 1: Electrical and Electronics", fill="#A7F3D0", anchor="mm")
    d.text((250, 480), "Floor 0: Ground Foyer and Admin", fill="#A7F3D0", anchor="mm")
    
    d.rectangle([540, 140, 940, 520], fill="#0D1F18", outline="#16A36A", width=2)
    d.text((740, 180), "Spine and Synchronization", fill="#35D99A", anchor="mm")
    d.text((740, 260), "Vertical Transitions: Elevators and Stairs", fill="#F8FAFC", anchor="mm")
    d.text((740, 330), "Wheelchair Filtering: Dynamic Subgraph", fill="#F8FAFC", anchor="mm")
    d.text((740, 400), "Dijkstra Cross-Floor Optimization", fill="#F8FAFC", anchor="mm")
    d.text((740, 470), "Interactive 3D WebGL Visualization", fill="#A7F3D0", anchor="mm")
    img.save(diag_dir / fname)

# 4. Copy screenshots into organized folders
shots_mapping = {
    # Dashboard
    "dashboard/01_main_dashboard.png": demo_shots / "01_main_dashboard.png",
    "dashboard/02_campus_entrance_dashboard.png": uat_shots / "01_student" / "01_campus_entrance_and_dashboard.png",
    # Navigation
    "navigation/01_route_planning.png": demo_shots / "07_route_planning.png",
    "navigation/02_destination_search.png": demo_shots / "06_destination_search.png",
    "navigation/03_turn_by_turn_guidance.png": demo_shots / "09_turn_by_turn_navigation.png",
    "navigation/04_2d_interactive_canvas.png": uat_shots / "01_student" / "05_2d_interactive_canvas.png",
    # Accessibility
    "accessibility/01_wheelchair_accessible_route.png": demo_shots / "08_wheelchair_accessible_route.png",
    "accessibility/02_accessibility_settings.png": demo_shots / "14_accessibility_settings.png",
    "accessibility/03_step_free_elevator_nav.png": uat_shots / "03_wheelchair" / "02_step_free_elevator_navigation.png",
    # Indoor
    "indoor/01_five_floor_fet_building.png": demo_shots / "04_five_floor_fet_building.png",
    "indoor/02_floor_selection.png": demo_shots / "05_floor_selection.png",
    "indoor/03_outdoor_to_foyer_connection.png": uat_shots / "02_laboratory" / "01_outdoor_campus_foyer_connection.png",
    # Digital Twin
    "digital_twin/01_outdoor_campus_digital_twin.png": demo_shots / "03_outdoor_campus_digital_twin.png",
    "digital_twin/02_hpc_robotics_3d_twin.png": uat_shots / "02_laboratory" / "04_hpc_and_robotics_3d_digital_twin.png",
    # Obstacle Management
    "obstacle_management/01_obstacle_reporting_form.png": demo_shots / "10_obstacle_reporting.png",
    "obstacle_management/02_dynamic_rerouting.png": demo_shots / "11_dynamic_rerouting.png",
    "obstacle_management/03_obstacle_resolution.png": uat_shots / "04_obstacle_lifecycle" / "03_obstacle_resolution_by_field_staff.png",
    # Administration
    "administration/01_administrative_console.png": demo_shots / "13_administrative_console.png",
    "administration/02_analytics_dashboard.png": demo_shots / "12_analytics_dashboard.png",
    "administration/03_multilingual_interface.png": demo_shots / "15_multilingual_interface.png",
    "administration/04_login_page.png": demo_shots / "02_login_page.png",
}

for dest, src in shots_mapping.items():
    if src.exists():
        d = shots_dir / dest
        shutil.copy2(src, d)

print("Successfully prepared all diagrams and screenshots.")
