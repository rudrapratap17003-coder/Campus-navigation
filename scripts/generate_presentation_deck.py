"""Generate widescreen 16:9 PowerPoint (.pptx) and PDF presentations for Accessible Campus Navigator."""

import os
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

from reportlab.lib.pagesizes import landscape
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

base_dir = Path.cwd()
pkg_pres_dir = base_dir / "FINAL_PRESENTATION_PACKAGE" / "PRESENTATION"
pkg_pres_dir.mkdir(parents=True, exist_ok=True)

# Color Palette Constants
COLOR_BG = RGBColor(7, 19, 15)          # #07130F
COLOR_CARD = RGBColor(18, 40, 32)       # #122820
COLOR_PRIMARY = RGBColor(22, 163, 106)  # #16A36A
COLOR_ACCENT = RGBColor(53, 217, 154)   # #35D99A
COLOR_MINT = RGBColor(167, 243, 208)    # #A7F3D0
COLOR_WHITE = RGBColor(248, 250, 252)   # #F8FAFC
COLOR_MUTED = RGBColor(156, 175, 165)   # #9CAFA5
COLOR_WARNING = RGBColor(245, 185, 66)  # #F5B942

# ReportLab Colors
RL_BG = colors.HexColor("#07130F")
RL_CARD = colors.HexColor("#122820")
RL_PRIMARY = colors.HexColor("#16A36A")
RL_ACCENT = colors.HexColor("#35D99A")
RL_MINT = colors.HexColor("#A7F3D0")
RL_WHITE = colors.HexColor("#F8FAFC")
RL_MUTED = colors.HexColor("#9CAFA5")

# Diagram & Screenshot Paths
DIAG_DIR = base_dir / "FINAL_PRESENTATION_PACKAGE" / "DIAGRAMS"
SHOT_DIR = base_dir / "FINAL_PRESENTATION_PACKAGE" / "SCREENSHOTS"

def create_pptx():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    slides_data = [
        # Slide 1: Title
        {
            "num": 1,
            "title": "Accessible Campus Navigator",
            "subtitle": "An Intelligent and Accessibility-Aware Campus Wayfinding System",
            "type": "title",
            "content": [
                ("Presenter", "Rudra Pratap"),
                ("USN", "25BTRCL214"),
                ("Department", "Artificial Intelligence & Machine Learning"),
                ("Institution", "JAIN (Deemed-to-be University) - FET"),
                ("Academic Year", "2025 - 2026"),
                ("Core Technologies", "Python • NetworkX • SQLite • Three.js • Streamlit"),
            ],
            "img": SHOT_DIR / "dashboard" / "01_main_dashboard.png"
        },
        # Slide 2: Problem Statement
        {
            "num": 2,
            "title": "Problem Statement",
            "subtitle": "The Challenge of Complex, Inaccessible Campus Navigation",
            "type": "two_col",
            "col1_title": "Real-World Campus Obstacles",
            "col1_points": [
                "Expansive Campus Layout: 79+ locations across sprawling outdoor terrain and multi-storey academic wings create disorientation.",
                "Multi-Storey Indoor Complexity: Traditional navigation apps fail inside multi-floor academic buildings like FET.",
                "Mobility & Accessibility Barriers: Students in wheelchairs or with temporary injuries face dead-end staircases and missing ramps.",
                "Dynamic Campus Disruptions: Routine maintenance, broken elevators, and cleaning hazards are not reflected in static maps.",
                "Fragmented Campus Knowledge: Visitors lack unified, verified directory information for departmental labs and faculty cabins."
            ],
            "col2_title": "Core Technical Gaps",
            "col2_points": [
                "Lack of accessible routing algorithms incorporating step-free constraints.",
                "Absence of dynamic obstacle detection and real-time graph edge severance.",
                "No unified representation bridging outdoor pathways and multi-floor indoor floor plans.",
                "Lack of spatial digital twins for intuitive pre-visit landmark recognition."
            ],
            "img": None
        },
        # Slide 3: Proposed Solution
        {
            "num": 3,
            "title": "Proposed Solution",
            "subtitle": "A Unified, Accessibility-Aware Digital Navigation Platform",
            "type": "split_img",
            "points": [
                "Spatial Graph Engine: Models 79 nodes and 106 pathways with wheelchair, width, and gradient attributes.",
                "Dual Routing System: Implements Dijkstra (distance-optimized) and BFS (fewest transitions) pathfinding.",
                "Step-Free Accessibility Filter: Dynamically excludes staircases and routes exclusively via certified elevators and ramps.",
                "Dynamic Obstacle Lifecycle: Enables campus reporting with real-time graph severance upon staff verification.",
                "Interactive 3D Digital Twin: Procedural Three.js WebGL visualization supporting floor isolation slicing."
            ],
            "img": SHOT_DIR / "digital_twin" / "01_outdoor_campus_digital_twin.png"
        },
        # Slide 4: Project Objectives
        {
            "num": 4,
            "title": "Project Objectives",
            "subtitle": "Clear, Measurable Engineering Goals",
            "type": "grid_4",
            "cards": [
                ("1. Unified Wayfinding", "Seamlessly connect outdoor university pathways with indoor academic facilities into a single continuous navigational graph."),
                ("2. Deterministic Routing", "Calculate optimal paths using Dijkstra and BFS, providing clear metric comparison of distance vs. transitions."),
                ("3. Step-Free Equity", "Guarantee wheelchair-accessible routing with heuristic scoring, ensuring no student encounters unexpected stair barriers."),
                ("4. Dynamic Resilience", "Provide operational obstacle reporting with administrative verification and automatic real-time route recalculation.")
            ],
            "img": None
        },
        # Slide 5: System Architecture
        {
            "num": 5,
            "title": "System Architecture",
            "subtitle": "Modular, Layered Software Architecture",
            "type": "diagram",
            "points": [
                "Presentation Layer: Responsive Streamlit UI with WCAG 2.1 AA dark-forest green visual design.",
                "Application Services: RouteFinder, AccessibilityEngine, ObstacleManager, CampusAnalytics.",
                "Graph & Spatial Layer: NetworkX undirected weighted graph with multi-floor edge modeling.",
                "Data Persistence: SQLite in WAL mode with PBKDF2-HMAC-SHA256 authentication and audit logs."
            ],
            "img": DIAG_DIR / "system_architecture" / "01_overall_system_architecture.png"
        },
        # Slide 6: Technology Stack
        {
            "num": 6,
            "title": "Technology Stack",
            "subtitle": "Selected Frameworks & Engineering Rationale",
            "type": "grid_6",
            "cards": [
                ("Python 3.11+", "High-performance graph traversal, clean object-oriented architecture, and data science ecosystem."),
                ("Streamlit", "Reactive web UI enabling rapid operational state binding without complex frontend bloat."),
                ("NetworkX", "Robust graph data structures, native adjacency matrices, and shortest-path graph algorithms."),
                ("SQLite (WAL)", "Lightweight, zero-configuration relational database with concurrent read-write persistence."),
                ("Three.js & WebGL", "Hardware-accelerated 3D digital twin rendering with interactive camera orbit controls."),
                ("Plotly & Folium", "Interactive geospatial campus mapping, barrier distribution histograms, and analytics.")
            ],
            "img": None
        },
        # Slide 7: Campus Graph & Navigation Model
        {
            "num": 7,
            "title": "Campus Graph & Navigation Model",
            "subtitle": "Mathematical Formulation of Campus Topology",
            "type": "diagram",
            "points": [
                "Graph Formulation: G = (V, E) where |V| = 79 physical locations and |E| = 106 navigable pathways.",
                "Node Attributes: {id, name, floor_id, category, x, y, is_accessible}.",
                "Edge Attributes: {distance_meters, edge_type, incline_pct, is_step_free, is_blocked}.",
                "Dual Representation: Supports full JAIN Global Campus (79 nodes) and Benchmark Model (15 nodes)."
            ],
            "img": DIAG_DIR / "system_architecture" / "02_campus_graph_representation.png"
        },
        # Slide 8: BFS vs Dijkstra Algorithms
        {
            "num": 8,
            "title": "Algorithmic Analysis: BFS vs Dijkstra",
            "subtitle": "Comparing Graph Traversal Paradigms for Pedestrian Wayfinding",
            "type": "table_algo",
            "points": [
                "Breadth-First Search: Explores level-by-level using a FIFO queue. Minimizes edge hops, ignoring physical path lengths.",
                "Dijkstra's Algorithm: Priority-queue min-heap traversal. Minimizes cumulative non-negative edge costs (distance + incline).",
                "Practical Demonstration: For Main Gate -> FET Auditorium, Dijkstra finds a 420m path (7 nodes) while BFS yields 465m (6 nodes)."
            ],
            "img": DIAG_DIR / "algorithms" / "04_dijkstra_workflow.png"
        },
        # Slide 9: Accessibility-Aware Navigation
        {
            "num": 9,
            "title": "Accessibility-Aware Navigation",
            "subtitle": "Deterministic Constraint Solving & Heuristic Scoring",
            "type": "diagram",
            "points": [
                "Dynamic Subgraph Pruning: Construct G' = (V, E \\ E_stairs) upon user toggling Wheelchair Mode.",
                "Mandatory Elevator Routing: Forces vertical traversal strictly through validated passenger elevators.",
                "Accessibility Score Heuristic (0-100): Calculated from path clearance width, ramp gradient, and surface paving.",
                "Honest Boundary: Accessibility scores are heuristic; real-world verification remains essential."
            ],
            "img": DIAG_DIR / "algorithms" / "05_wheelchair_accessible_routing.png"
        },
        # Slide 10: Five-Floor FET Indoor Navigation
        {
            "num": 10,
            "title": "Five-Floor FET Indoor Navigation",
            "subtitle": "Multi-Storey Academic Facility Mapping",
            "type": "diagram",
            "points": [
                "Floor Decomposition: Discrete 2D coordinate planes for Ground (0), First (1), Second (2), Third (3), and Fourth (4) floors.",
                "Vertical Spine: Elevators and staircases model inter-floor transitions as weighted directed edges.",
                "Seamless Traversal: Path seamlessly connects outdoor campus walkways, enters foyer, ascends elevator, and terminates at lab.",
                "Complete Directory: Mapped 45+ academic labs, faculty cabins, seminar halls, and student amenities."
            ],
            "img": DIAG_DIR / "system_architecture" / "08_five_floor_indoor_structure.png"
        },
        # Slide 11: 3D Digital Twin
        {
            "num": 11,
            "title": "Interactive 3D Digital Twin",
            "subtitle": "Procedural WebGL Campus Visualization with Three.js",
            "type": "split_img",
            "points": [
                "Procedural Geometry: Generates 3D building blocks and pathways directly from spatial JSON metadata.",
                "Floor Isolation Slicing: Interactive UI buttons lift upper storeys to reveal internal floor layouts.",
                "Glowing Route Spline: Renders the active 3D path trajectory calculated by the Dijkstra routing engine.",
                "Engineering Clarification: Schematic digital twin for spatial intuition, not a surveyed BIM/CAD model.",
                "Hardware Efficiency: 60 FPS rendering in standard web browsers without requiring dedicated GPUs."
            ],
            "img": DIAG_DIR / "system_architecture" / "09_3d_digital_twin_architecture.png"
        },
        # Slide 12: Dynamic Obstacle Management
        {
            "num": 12,
            "title": "Dynamic Obstacle Reporting & Rerouting",
            "subtitle": "Closed-Loop Incident Lifecycle & Edge Severance",
            "type": "diagram",
            "points": [
                "Reporting: Students or staff submit reports with target pathway, severity, and photo attachment.",
                "Lifecycle Safeguard: Reports start as PENDING; only VERIFIED reports sever graph edges to prevent vandalism.",
                "Real-Time Rerouting: Verified obstacles set edge weight w(u,v) = infinity, forcing automatic route recalculation.",
                "Staff Resolution: Field staff mark hazards RESOLVED with mandatory resolution notes, restoring normal routing."
            ],
            "img": DIAG_DIR / "workflows" / "06_obstacle_reporting_lifecycle.png"
        },
        # Slide 13: Security & Administration
        {
            "num": 13,
            "title": "Security, Governance & Administration",
            "subtitle": "Enterprise-Grade Access Control & Audit Trails",
            "type": "grid_4",
            "cards": [
                ("PBKDF2 Password Hashing", "600,000 SHA-256 iterations with 32-byte cryptographic salts. Zero plaintext credentials."),
                ("Role-Based Access Control", "Three isolated tiers: Student (view/report), Field Staff (verify/resolve), Admin (user management)."),
                ("Brute-Force Rate Limiting", "Exponential login lockout (5 failed attempts locks IP/user for 300 seconds)."),
                ("Immutable Audit Logging", "Every role change, login event, and obstacle transition records user ID, IP, and timestamp.")
            ],
            "img": None
        },
        # Slide 14: Testing, Results & Limitations
        {
            "num": 14,
            "title": "Verification, Test Results & Limitations",
            "subtitle": "Rigorous Empirical Validation & Honest Boundary Disclosure",
            "type": "two_col",
            "col1_title": "Automated Test Suite (208 Tests)",
            "col1_points": [
                "208 automated unit and regression tests passing with 0 failures and 0 errors in 52.3s.",
                "100% test coverage across graph algorithms, schema migrations, RBAC, and security policies.",
                "Continuous validation of wheelchair constraints, obstacle state transitions, and WAL persistence.",
                "Production build verification with Python compileall (Exit Code 0)."
            ],
            "col2_title": "Known Project Limitations",
            "col2_points": [
                "Schematic Coordinates: Node coordinates are mapped to campus ground plans, not geodetic GPS surveys.",
                "Manual Waypoint Entry: Current version does not include real-time BLE indoor beacon trilateration.",
                "Heuristic Scores: Accessibility percentages represent heuristic estimates, requiring physical audits.",
                "Deployment Status: Containerized and production-ready; live public cloud activation requires owner OAuth."
            ],
            "img": None
        },
        # Slide 15: Conclusion & Future Scope
        {
            "num": 15,
            "title": "Conclusion & Future Scope",
            "subtitle": "Making University Campuses More Inclusive for Everyone",
            "type": "conclusion",
            "achievements": [
                "Engineered a full-featured campus navigation platform combining outdoor walkways and 5-floor indoor plans.",
                "Demonstrated rigorous algorithmic comparison between Dijkstra and BFS routing paradigms.",
                "Delivered practical accessibility equity via dynamic step-free filtering and obstacle management.",
                "Created an interactive 3D digital twin running at 60 FPS on standard student laptops."
            ],
            "future_work": [
                "Integration with Bluetooth Low Energy (BLE) beacons for real-time indoor positioning.",
                "Voice-guided turn-by-turn navigation with audio announcements for visually impaired students.",
                "Crowdsourced accessibility tagging and live campus event rerouting."
            ],
            "closing": "THANK YOU!\nMaking Campus Navigation More Accessible for Everyone."
        }
    ]

    for data in slides_data:
        slide = prs.slides.add_slide(blank_layout)
        
        # Dark Background
        bg_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg_shape.fill.solid()
        bg_shape.fill.fore_color.rgb = COLOR_BG
        bg_shape.line.fill.background()

        # Header Box
        header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(1.1))
        tf = header_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        p = tf.paragraphs[0]
        p.text = data["title"]
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = COLOR_ACCENT
        p.font.name = "Segoe UI"

        p2 = tf.add_paragraph()
        p2.text = data["subtitle"]
        p2.font.size = Pt(14)
        p2.font.color.rgb = COLOR_MUTED
        p2.font.name = "Segoe UI"

        # Content based on slide type
        stype = data["type"]

        if stype == "title":
            # Left Card with Presenter Info
            info_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.8), Inches(4.8))
            info_box.fill.solid()
            info_box.fill.fore_color.rgb = COLOR_CARD
            info_box.line.color.rgb = COLOR_PRIMARY
            info_box.line.width = Pt(1.5)
            
            itf = info_box.text_frame
            itf.word_wrap = True
            itf.margin_left = Inches(0.4)
            itf.margin_top = Inches(0.4)
            
            p = itf.paragraphs[0]
            p.text = "Project Metadata & Credentials"
            p.font.size = Pt(18)
            p.font.bold = True
            p.font.color.rgb = COLOR_ACCENT
            
            for label, val in data["content"]:
                p_item = itf.add_paragraph()
                p_item.text = f"{label}: {val}"
                p_item.font.size = Pt(13)
                p_item.font.color.rgb = COLOR_WHITE
                p_item.space_before = Pt(10)

            # Right Side Image
            if data["img"] and data["img"].exists():
                slide.shapes.add_picture(str(data["img"]), Inches(7.0), Inches(1.8), width=Inches(5.5))

        elif stype == "two_col":
            # Col 1
            col1 = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0))
            col1.fill.solid()
            col1.fill.fore_color.rgb = COLOR_CARD
            col1.line.color.rgb = COLOR_PRIMARY
            c1_tf = col1.text_frame
            c1_tf.word_wrap = True
            c1_tf.margin_left = c1_tf.margin_right = Inches(0.3)
            c1_tf.margin_top = Inches(0.3)
            p = c1_tf.paragraphs[0]
            p.text = data["col1_title"]
            p.font.size = Pt(16)
            p.font.bold = True
            p.font.color.rgb = COLOR_ACCENT
            for pt in data["col1_points"]:
                p_pt = c1_tf.add_paragraph()
                p_pt.text = f"• {pt}"
                p_pt.font.size = Pt(12)
                p_pt.font.color.rgb = COLOR_WHITE
                p_pt.space_before = Pt(8)

            # Col 2
            col2 = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0))
            col2.fill.solid()
            col2.fill.fore_color.rgb = COLOR_CARD
            col2.line.color.rgb = COLOR_PRIMARY
            c2_tf = col2.text_frame
            c2_tf.word_wrap = True
            c2_tf.margin_left = c2_tf.margin_right = Inches(0.3)
            c2_tf.margin_top = Inches(0.3)
            p = c2_tf.paragraphs[0]
            p.text = data["col2_title"]
            p.font.size = Pt(16)
            p.font.bold = True
            p.font.color.rgb = COLOR_ACCENT
            for pt in data["col2_points"]:
                p_pt = c2_tf.add_paragraph()
                p_pt.text = f"• {pt}"
                p_pt.font.size = Pt(12)
                p_pt.font.color.rgb = COLOR_WHITE
                p_pt.space_before = Pt(8)

        elif stype in ("split_img", "diagram", "table_algo"):
            # Left points card
            card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.8), Inches(5.0))
            card.fill.solid()
            card.fill.fore_color.rgb = COLOR_CARD
            card.line.color.rgb = COLOR_PRIMARY
            ctf = card.text_frame
            ctf.word_wrap = True
            ctf.margin_left = ctf.margin_right = Inches(0.3)
            ctf.margin_top = Inches(0.3)
            p = ctf.paragraphs[0]
            p.text = "Key Technical Highlights"
            p.font.size = Pt(16)
            p.font.bold = True
            p.font.color.rgb = COLOR_ACCENT
            for pt in data["points"]:
                p_pt = ctf.add_paragraph()
                p_pt.text = f"• {pt}"
                p_pt.font.size = Pt(12)
                p_pt.font.color.rgb = COLOR_WHITE
                p_pt.space_before = Pt(10)

            # Right image / diagram
            if data["img"] and data["img"].exists():
                slide.shapes.add_picture(str(data["img"]), Inches(6.9), Inches(1.8), width=Inches(5.6))

        elif stype == "grid_4":
            positions = [
                (Inches(0.8), Inches(1.8)),
                (Inches(6.8), Inches(1.8)),
                (Inches(0.8), Inches(4.3)),
                (Inches(6.8), Inches(4.3)),
            ]
            for (gx, gy), (head, body) in zip(positions, data["cards"]):
                card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, gx, gy, Inches(5.7), Inches(2.2))
                card.fill.solid()
                card.fill.fore_color.rgb = COLOR_CARD
                card.line.color.rgb = COLOR_PRIMARY
                ctf = card.text_frame
                ctf.word_wrap = True
                ctf.margin_left = ctf.margin_right = Inches(0.3)
                ctf.margin_top = Inches(0.25)
                p = ctf.paragraphs[0]
                p.text = head
                p.font.size = Pt(15)
                p.font.bold = True
                p.font.color.rgb = COLOR_ACCENT
                p2 = ctf.add_paragraph()
                p2.text = body
                p2.font.size = Pt(12)
                p2.font.color.rgb = COLOR_WHITE
                p2.space_before = Pt(6)

        elif stype == "grid_6":
            positions = [
                (Inches(0.8), Inches(1.8)),
                (Inches(4.8), Inches(1.8)),
                (Inches(8.8), Inches(1.8)),
                (Inches(0.8), Inches(4.4)),
                (Inches(4.8), Inches(4.4)),
                (Inches(8.8), Inches(4.4)),
            ]
            for (gx, gy), (head, body) in zip(positions, data["cards"]):
                card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, gx, gy, Inches(3.7), Inches(2.3))
                card.fill.solid()
                card.fill.fore_color.rgb = COLOR_CARD
                card.line.color.rgb = COLOR_PRIMARY
                ctf = card.text_frame
                ctf.word_wrap = True
                ctf.margin_left = ctf.margin_right = Inches(0.25)
                ctf.margin_top = Inches(0.25)
                p = ctf.paragraphs[0]
                p.text = head
                p.font.size = Pt(14)
                p.font.bold = True
                p.font.color.rgb = COLOR_ACCENT
                p2 = ctf.add_paragraph()
                p2.text = body
                p2.font.size = Pt(11)
                p2.font.color.rgb = COLOR_WHITE
                p2.space_before = Pt(4)

        elif stype == "conclusion":
            # Left side achievements & future work
            card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(7.5), Inches(5.0))
            card.fill.solid()
            card.fill.fore_color.rgb = COLOR_CARD
            card.line.color.rgb = COLOR_PRIMARY
            ctf = card.text_frame
            ctf.word_wrap = True
            ctf.margin_left = ctf.margin_right = Inches(0.4)
            ctf.margin_top = Inches(0.3)
            
            p = ctf.paragraphs[0]
            p.text = "Key Project Achievements"
            p.font.size = Pt(16)
            p.font.bold = True
            p.font.color.rgb = COLOR_ACCENT
            for ach in data["achievements"]:
                p_a = ctf.add_paragraph()
                p_a.text = f"✓ {ach}"
                p_a.font.size = Pt(12)
                p_a.font.color.rgb = COLOR_WHITE
                p_a.space_before = Pt(6)

            p_f = ctf.add_paragraph()
            p_f.text = "Future Directions"
            p_f.font.size = Pt(16)
            p_f.font.bold = True
            p_f.font.color.rgb = COLOR_ACCENT
            p_f.space_before = Pt(14)
            for f in data["future_work"]:
                p_f_item = ctf.add_paragraph()
                p_f_item.text = f"→ {f}"
                p_f_item.font.size = Pt(12)
                p_f_item.font.color.rgb = COLOR_MUTED
                p_f_item.space_before = Pt(4)

            # Right Banner
            rbanner = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.7), Inches(1.8), Inches(3.8), Inches(5.0))
            rbanner.fill.solid()
            rbanner.fill.fore_color.rgb = COLOR_PRIMARY
            rtf = rbanner.text_frame
            rtf.word_wrap = True
            rtf.margin_left = rtf.margin_right = Inches(0.3)
            rtf.margin_top = Inches(1.5)
            rp = rtf.paragraphs[0]
            rp.text = data["closing"]
            rp.alignment = PP_ALIGN.CENTER
            rp.font.size = Pt(20)
            rp.font.bold = True
            rp.font.color.rgb = COLOR_WHITE

        # Footer
        footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(6.9), Inches(11.7), Inches(0.4))
        ftf = footer_box.text_frame
        ftf.margin_left = ftf.margin_right = ftf.margin_top = ftf.margin_bottom = 0
        fp = ftf.paragraphs[0]
        fp.text = f"Accessible Campus Navigator | Slide {data['num']} of 15 | JAIN (Deemed-to-be University) - FET"
        fp.font.size = Pt(10)
        fp.font.color.rgb = COLOR_MUTED
        fp.alignment = PP_ALIGN.RIGHT

    # Save PPTX
    out_pptx_pkg = pkg_pres_dir / "FINAL_ACCESSIBLE_CAMPUS_NAVIGATOR_PRESENTATION.pptx"
    out_pptx_root = base_dir / "FINAL_ACCESSIBLE_CAMPUS_NAVIGATOR_PRESENTATION.pptx"
    prs.save(out_pptx_pkg)
    prs.save(out_pptx_root)
    print(f"Generated PPTX: {out_pptx_pkg} and {out_pptx_root}")

def create_pdf():
    # ReportLab 16:9 widescreen canvas
    width, height = 960, 540  # points
    out_pdf_pkg = pkg_pres_dir / "FINAL_ACCESSIBLE_CAMPUS_NAVIGATOR_PRESENTATION.pdf"
    out_pdf_root = base_dir / "FINAL_ACCESSIBLE_CAMPUS_NAVIGATOR_PRESENTATION.pdf"

    c = canvas.Canvas(str(out_pdf_pkg), pagesize=(width, height))
    
    # 15 Slides metadata for PDF
    slides_titles = [
        ("1. Accessible Campus Navigator", "An Intelligent and Accessibility-Aware Campus Wayfinding System", "Presenter: Rudra Pratap (USN: 25BTRCL214)\nDepartment: Artificial Intelligence & Machine Learning\nInstitution: JAIN (Deemed-to-be University) - FET\nAcademic Year: 2025-2026\nStatus: 208 Unit Tests Passed | v1.0.0 Release Ready"),
        ("2. Problem Statement", "The Challenge of Complex, Inaccessible Campus Navigation", "• Expansive Campus Layout: 79+ locations across outdoor terrain and multi-storey academic wings.\n• Indoor Disorientation: Traditional navigation maps end at the building entrance gate.\n• Mobility Barriers: Staircases create impassable obstacles for students in wheelchairs.\n• Dynamic Maintenance: Daily construction, cleaning, and elevator outages are not tracked.\n• Fragmented Directory: Students and visitors struggle to find departmental labs."),
        ("3. Proposed Solution", "A Unified, Accessibility-Aware Digital Navigation Platform", "• Spatial Graph Model: 79 physical locations and 106 pathways with accessibility metadata.\n• Dual-Algorithm Routing: Dijkstra (distance cost) and BFS (fewest transitions) comparison.\n• Step-Free Accessibility Engine: Strictly avoids staircases and routes via certified elevators.\n• Dynamic Obstacle Management: Closed-loop reporting with real-time graph edge severance.\n• 3D Digital Twin: Interactive Three.js WebGL visualization supporting floor isolation."),
        ("4. Project Objectives", "Clear, Measurable Engineering Goals", "1. Unified Wayfinding: Seamlessly integrate outdoor pathways with 5-floor indoor rooms.\n2. Deterministic Routing: Compute optimal paths using Dijkstra and BFS algorithms.\n3. Step-Free Accessibility: Guarantee barrier-free routes with heuristic accessibility scores.\n4. Dynamic Resilience: Invalidate blocked pathways dynamically upon staff verification."),
        ("5. System Architecture", "Layered, Modular Software Architecture", "• Presentation Layer: Responsive Streamlit UI with dark-forest green visual styling.\n• Application Logic: RouteFinder, AccessibilityEngine, ObstacleManager, CampusAnalytics.\n• Graph Engine: NetworkX weighted undirected graph with multi-floor edge modeling.\n• Persistence: SQLite in WAL mode with PBKDF2 password hashing and audit logs."),
        ("6. Technology Stack", "Frameworks & Engineering Rationale", "• Python 3.11+: Core backend logic, graph algorithms, and data modeling.\n• Streamlit: Modern reactive interface with zero JavaScript overhead.\n• NetworkX: Mathematical graph representation, adjacency matrices, and shortest paths.\n• SQLite (WAL): High-performance ACID relational database with concurrent read-write.\n• Three.js & WebGL: Hardware-accelerated 3D digital twin rendering at 60 FPS.\n• Plotly & Folium: Interactive spatial heatmaps and barrier distribution charts."),
        ("7. Campus Graph & Navigation Model", "Mathematical Formulation of Campus Topology", "• Graph Formulation: G = (V, E) where |V| = 79 locations and |E| = 106 pathways.\n• Vertices (V): Main Gate, Library, FET Foyer, Laboratories, Classrooms, Elevators.\n• Edges (E): Footpaths, corridors, ramps, elevators, and staircases with distances.\n• Edge Weights: w(e) = distance_meters + incline_cost + surface_penalty."),
        ("8. BFS vs Dijkstra Routing", "Comparing Graph Traversal Paradigms", "• Breadth-First Search (BFS): Explores level-by-level using FIFO queue. Finds fewest hops.\n• Dijkstra's Algorithm: Min-priority queue traversal. Finds minimum cumulative distance.\n• Comparison Result: For Main Gate -> FET Auditorium, Dijkstra finds 420m (7 nodes) while BFS yields 465m (6 nodes).\n• Key Takeaway: Weighted Dijkstra is essential for physically realistic pedestrian paths."),
        ("9. Accessibility-Aware Navigation", "Deterministic Constraint Solving & Heuristic Scoring", "• Dynamic Subgraph Pruning: Strips staircase edges: G' = (V, E \\ E_stairs).\n• Mandatory Elevator Routing: Vertical transitions restricted to validated passenger elevators.\n• Heuristic Accessibility Score: 0-100 score based on pathway width, slope, and surface.\n• Real-World Integrity: Heuristic scores represent estimates; physical audits still required."),
        ("10. Five-Floor FET Indoor Navigation", "Multi-Storey Academic Facility Mapping", "• Discrete Floor Planes: Floor 0 (Ground), Floor 1, Floor 2, Floor 3, and Floor 4.\n• Vertical Transitions: Dual elevator shafts and central staircases connect floor slices.\n• Continuous Pathing: Navigates from outdoor campus gate directly to second-floor AI lab.\n• Spatial Directory: Mapped 45+ academic labs, faculty cabins, and seminar halls."),
        ("11. Interactive 3D Digital Twin", "Procedural WebGL Campus Visualization", "• Three.js Scene: Procedural box geometries generated directly from spatial JSON data.\n• Camera Interaction: OrbitControls enable intuitive pan, tilt, and zoom across campus.\n• Floor Isolation: Slicing controls lift upper storeys to reveal interior room corridors.\n• Route Trajectory: Glowing 3D spline overlays exact coordinates calculated by Dijkstra.\n• Transparent Distinction: Schematic digital twin for intuition, NOT a surveyed BIM model."),
        ("12. Dynamic Obstacle Management", "Closed-Loop Incident Lifecycle & Edge Severance", "• Reporting: Users submit obstacle reports with pathway target, severity, and photo.\n• Verification: Reports remain PENDING until field staff validates to prevent false reports.\n• Invalidation: Verified obstacle sets edge weight w(e) = infinity, forcing rerouting.\n• Resolution: Staff marks cleared with mandatory notes, automatically restoring edge."),
        ("13. Security & Administration", "Enterprise Access Control & Audit Trails", "• PBKDF2 Hashing: 600,000 iterations with 32-byte salts. Zero plaintext passwords.\n• Role-Based Access: Three tiers - Student, Field Staff, Administrator.\n• Brute-Force Rate Limiting: 5 failed attempts locks user/IP for 300 seconds.\n• Immutable Audit Logs: All operational transitions record timestamp, user ID, and IP."),
        ("14. Verification, Tests & Limitations", "Rigorous Test Suite & Honest Boundary Disclosure", "• Test Suite: 208 automated unit and regression tests passing with 0 failures.\n• 100% Coverage: Routing, schema migration, RBAC, and security policies verified.\n• Limitation 1: Schematic coordinates mapped to campus plans, not geodetic GPS.\n• Limitation 2: No active hardware BLE indoor beacons; origin selected manually.\n• Limitation 3: Containerized and ready; public cloud activation requires owner OAuth."),
        ("15. Conclusion & Future Scope", "Making Campuses More Inclusive for Everyone", "• Key Achievements: Unified 79-node graph, 5-floor indoor map, 3D twin, 208 passing tests.\n• Algorithmic Rigor: Proved Dijkstra vs BFS differences on live campus pathways.\n• Social Impact: Prioritized accessibility for students with mobility impairments.\n• Future Scope: BLE beacon indoor positioning, voice navigation, crowdsourced notes.\n• Closing: THANK YOU! Making Campus Navigation More Accessible for Everyone.")
    ]

    for idx, (title, sub, body) in enumerate(slides_titles, 1):
        # Draw background
        c.setFillColor(RL_BG)
        c.rect(0, 0, width, height, fill=1, stroke=0)

        # Header Box
        c.setFillColor(RL_ACCENT)
        c.setFont("Helvetica-Bold", 22)
        c.drawString(50, height - 50, title)

        c.setFillColor(RL_MUTED)
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 70, sub)

        # Content Card
        c.setFillColor(RL_CARD)
        c.setStrokeColor(RL_PRIMARY)
        c.setLineWidth(1.5)
        c.roundRect(50, 60, width - 100, height - 150, 10, fill=1, stroke=1)

        # Text Lines in Card
        c.setFillColor(RL_WHITE)
        c.setFont("Helvetica", 12)
        
        y_text = height - 120
        for line in body.split("\n"):
            if ":" in line and not line.startswith("•") and not line.startswith("1."):
                parts = line.split(":", 1)
                c.setFillColor(RL_ACCENT)
                c.setFont("Helvetica-Bold", 12)
                c.drawString(75, y_text, parts[0] + ":")
                c.setFillColor(RL_WHITE)
                c.setFont("Helvetica", 12)
                c.drawString(75 + c.stringWidth(parts[0] + ":  "), y_text, parts[1])
            elif line.startswith("•") or line.startswith("1.") or line.startswith("2.") or line.startswith("3.") or line.startswith("4."):
                c.setFillColor(RL_WHITE)
                c.drawString(75, y_text, line)
            elif line.startswith("THANK YOU"):
                c.setFillColor(RL_ACCENT)
                c.setFont("Helvetica-Bold", 18)
                c.drawCentredString(width / 2, y_text - 40, line)
                c.setFont("Helvetica", 12)
            else:
                c.drawString(75, y_text, line)
            y_text -= 22

        # Footer
        c.setFillColor(RL_MUTED)
        c.setFont("Helvetica", 9)
        c.drawString(50, 30, "Accessible Campus Navigator — Final Academic Presentation")
        c.drawRightString(width - 50, 30, f"Slide {idx} of 15 | JAIN (Deemed-to-be University) - FET")

        c.showPage()

    c.save()
    # Copy to root as well
    import shutil
    shutil.copy2(out_pdf_pkg, out_pdf_root)
    print(f"Generated PDF: {out_pdf_pkg} and {out_pdf_root}")

if __name__ == "__main__":
    create_pptx()
    create_pdf()
