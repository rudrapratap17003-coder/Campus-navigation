"""
scripts/generate_presentation.py
--------------------------------
Generates the professional academic evaluation presentation:
Accessible_Campus_Navigator_Final_Presentation.pptx (15 slides)
with dark forest green glassmorphism styling, clean layout, cards, and tables.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE


def build_presentation(output_path: str):
    prs = Presentation()
    prs.slide_width = Inches(13.333)  # 16:9 Widescreen
    prs.slide_height = Inches(7.5)

    # Color Palette
    C_BG_DARK = RGBColor(0x07, 0x13, 0x0F)      # #07130F Deep Charcoal Forest
    C_CARD_BG = RGBColor(0x0D, 0x1F, 0x18)      # #0D1F18 Translucent Dark Green
    C_EMERALD = RGBColor(0x16, 0xA3, 0x6A)      # #16A36A Primary Green
    C_MINT = RGBColor(0x35, 0xD9, 0x9A)         # #35D99A Accent Mint
    C_WHITE = RGBColor(0xF8, 0xFA, 0xFC)        # #F8FAFC Heading / Primary Text
    C_MUTED = RGBColor(0x9C, 0xAF, 0xA5)        # #9CAFA5 Subtitle / Secondary Text
    C_CARD_BORDER = RGBColor(0x1E, 0x3A, 0x2E)  # Subtle Card Border

    blank_layout = prs.slide_layouts[6]

    def add_base_slide(title_text="", category="ACCESSIBLE CAMPUS NAVIGATOR"):
        slide = prs.slides.add_slide(blank_layout)
        # Background shape
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = C_BG_DARK
        bg.line.color.rgb = C_BG_DARK

        if title_text:
            # Header category pill / top rule
            top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.45), Inches(11.733), Inches(0.04))
            top_bar.fill.solid()
            top_bar.fill.fore_color.rgb = C_EMERALD
            top_bar.line.fill.background()

            # Category tag
            cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.55), Inches(6.0), Inches(0.35))
            tf_c = cat_box.text_frame
            tf_c.word_wrap = True
            p_c = tf_c.paragraphs[0]
            p_c.text = category.upper()
            p_c.font.size = Pt(10)
            p_c.font.bold = True
            p_c.font.color.rgb = C_MINT

            # Title
            title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.85), Inches(11.733), Inches(0.7))
            tf_t = title_box.text_frame
            tf_t.word_wrap = True
            p_t = tf_t.paragraphs[0]
            p_t.text = title_text
            p_t.font.size = Pt(22)
            p_t.font.bold = True
            p_t.font.color.rgb = C_WHITE

        return slide

    def add_card(slide, left, top, width, height, title="", border_color=C_CARD_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = C_CARD_BG
        card.line.color.rgb = border_color
        card.line.width = Pt(1.5)

        if title:
            # Card header title
            tb = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.15), width - Inches(0.4), Inches(0.4))
            tf = tb.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = title
            p.font.size = Pt(13)
            p.font.bold = True
            p.font.color.rgb = C_MINT

        return card

    # =========================================================================
    # SLIDE 1: TITLE SLIDE
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = C_BG_DARK
    bg1.line.fill.background()

    # Decorative green accent banner
    accent = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(1.0), Inches(11.333), Inches(5.5))
    accent.fill.solid()
    accent.fill.fore_color.rgb = C_CARD_BG
    accent.line.color.rgb = C_EMERALD
    accent.line.width = Pt(2)

    tb_t = s1.shapes.add_textbox(Inches(1.5), Inches(1.4), Inches(10.333), Inches(2.2))
    tf1 = tb_t.text_frame
    tf1.word_wrap = True

    p_u = tf1.paragraphs[0]
    p_u.text = "JAIN (DEEMED-TO-BE UNIVERSITY) • FACULTY OF ENGINEERING & TECHNOLOGY"
    p_u.font.size = Pt(11)
    p_u.font.bold = True
    p_u.font.color.rgb = C_MINT

    p_main = tf1.add_paragraph()
    p_main.text = "ACCESSIBLE CAMPUS NAVIGATOR"
    p_main.font.size = Pt(32)
    p_main.font.bold = True
    p_main.font.color.rgb = C_WHITE
    p_main.space_before = Pt(8)

    p_sub = tf1.add_paragraph()
    p_sub.text = "3D Digital Twin & Accessible Multi-Modal Wayfinding Platform for JAIN Global Campus"
    p_sub.font.size = Pt(15)
    p_sub.font.color.rgb = C_MUTED
    p_sub.space_before = Pt(6)

    # Candidate details card
    c_info = s1.shapes.add_textbox(Inches(1.5), Inches(3.8), Inches(10.333), Inches(2.2))
    tf_c = c_info.text_frame
    tf_c.word_wrap = True

    def add_meta_line(tf, label, value):
        p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = label + ": "
        r1.font.bold = True
        r1.font.size = Pt(12)
        r1.font.color.rgb = C_MINT
        r2 = p.add_run()
        r2.text = value
        r2.font.size = Pt(12)
        r2.font.color.rgb = C_WHITE
        p.space_before = Pt(4)

    add_meta_line(tf_c, "Student Name", "Rudra Pratap")
    add_meta_line(tf_c, "University Seat Number (USN)", "25BTRCL214")
    add_meta_line(tf_c, "Degree & Department", "B.Tech in Artificial Intelligence & Machine Learning (Section D)")
    add_meta_line(tf_c, "School / Faculty", "School of Computer Science & Engineering, FET")
    add_meta_line(tf_c, "Academic Evaluation", "Project Viva Voce & Final University Examination 2025–2026")

    # =========================================================================
    # SLIDE 2: PROBLEM STATEMENT
    # =========================================================================
    s2 = add_base_slide("Problem Statement: The Multi-Floor Navigation Barrier", "Context & Motivation")
    add_card(s2, Inches(0.8), Inches(1.8), Inches(3.6), Inches(5.0), "1. Macro-Map Blindness")
    tb2_1 = s2.shapes.add_textbox(Inches(1.0), Inches(2.4), Inches(3.2), Inches(4.2))
    tf2_1 = tb2_1.text_frame
    tf2_1.word_wrap = True
    tf2_1.paragraphs[0].text = "• Commercial mapping services (Google Maps, Apple Maps) stop at campus entrance gates.\n\n• Treat multi-story complex buildings as flat, single-point coordinates.\n\n• Zero visibility into indoor corridors, room numbers, or departments."
    for p in tf2_1.paragraphs:
        p.font.size = Pt(12)
        p.font.color.rgb = C_WHITE

    add_card(s2, Inches(4.8), Inches(1.8), Inches(3.6), Inches(5.0), "2. Vertical Discontinuity")
    tb2_2 = s2.shapes.add_textbox(Inches(5.0), Inches(2.4), Inches(3.2), Inches(4.2))
    tf2_2 = tb2_2.text_frame
    tf2_2.word_wrap = True
    tf2_2.paragraphs[0].text = "• Academic buildings stack departments across multiple floors (FET has 5 physical levels).\n\n• Conventional maps have no awareness of vertical connections (elevators, staircases, ramps).\n\n• Visitors cannot visualize cross-floor paths to 4th-floor research labs."
    for p in tf2_2.paragraphs:
        p.font.size = Pt(12)
        p.font.color.rgb = C_WHITE

    add_card(s2, Inches(8.8), Inches(1.8), Inches(3.7), Inches(5.0), "3. Disability Access Risks")
    tb2_3 = s2.shapes.add_textbox(Inches(9.0), Inches(2.4), Inches(3.3), Inches(4.2))
    tf2_3 = tb2_3.text_frame
    tf2_3.word_wrap = True
    tf2_3.paragraphs[0].text = "• Wheelchair users and injured students encounter impassable staircases without warning.\n\n• 18 pathways in FET are stairs—dead-ends for mobility-impaired users.\n\n• Zero tracking of dynamic maintenance, wet floors, or out-of-order elevators."
    for p in tf2_3.paragraphs:
        p.font.size = Pt(12)
        p.font.color.rgb = C_WHITE

    # =========================================================================
    # SLIDE 3: PROJECT OBJECTIVES
    # =========================================================================
    s3 = add_base_slide("Project Objectives & Research Goals", "Strategic Objectives")
    
    obj_data = [
        ("1. Accurate Spatial Topology", "Construct a verified mathematical graph of JAIN Global Campus and FET Building (79 locations and 106 pathways across 5 physical floors)."),
        ("2. Accessible Shortest Path Routing", "Implement Dijkstra (distance/time) and BFS (fewest turns) algorithms enforcing strict step-free wheelchair invariants with zero stair encounters."),
        ("3. WebGL 3D Digital Twin", "Engineer an interactive Three.js 3D environment featuring full 300-acre outdoor campus geometry, 5-floor FET building, room furnishings, and 5-floor exploded view."),
        ("4. Dynamic Hazard Awareness", "Establish a community reporting and staff verification lifecycle in SQLite WAL mode that dynamically blocks active graph edges and triggers rerouting."),
        ("5. Universal Inclusive Design", "Deliver multilingual support (English, Kannada, Hindi), WCAG AAA high-contrast styling, reduced-motion controls, and bookmarked places.")
    ]
    for idx, (title, desc) in enumerate(obj_data):
        top_y = Inches(1.8 + idx * 1.0)
        card = add_card(s3, Inches(0.8), top_y, Inches(11.733), Inches(0.85))
        tb = s3.shapes.add_textbox(Inches(1.0), top_y + Inches(0.1), Inches(11.3), Inches(0.65))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = title + " — "
        r1.bold = True
        r1.font.size = Pt(12)
        r1.font.color.rgb = C_MINT
        r2 = p1.add_run()
        r2.text = desc
        r2.font.size = Pt(11)
        r2.font.color.rgb = C_WHITE

    # =========================================================================
    # SLIDE 4: PROPOSED SOLUTION
    # =========================================================================
    s4 = add_base_slide("Proposed Solution: Integrated 3D Accessibility Platform", "System Overview")
    
    add_card(s4, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "Core Platform Capabilities")
    tb4_1 = s4.shapes.add_textbox(Inches(1.0), Inches(2.4), Inches(5.2), Inches(4.2))
    tf4_1 = tb4_1.text_frame
    tf4_1.word_wrap = True
    tf4_1.paragraphs[0].text = "• Unified Graph Engine: Seamless routing from campus gates directly to indoor 4th-floor labs.\n\n• ♿ Wheelchair Invariant Guarantee: Eliminates all 18 staircase edges; routes via ADA ramps and central elevator.\n\n• Real-Time Directional Guidance: Computes 2D vector cross-product turns (straight, left, right, elevator ride) and compass bearings.\n\n• Interactive 3D Digital Twin: Full orbit controls, room-level focus camera animation, floor isolation, and 5-floor exploded view."
    for p in tf4_1.paragraphs:
        p.font.size = Pt(12)
        p.font.color.rgb = C_WHITE

    add_card(s4, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0), "User Personas & Operational Roles")
    tb4_2 = s4.shapes.add_textbox(Inches(7.0), Inches(2.4), Inches(5.3), Inches(4.2))
    tf4_2 = tb4_2.text_frame
    tf4_2.word_wrap = True
    tf4_2.paragraphs[0].text = "• Student / Campus User (demo_student):\n  Explore 3D campus, calculate accessible routes, bookmark places, submit field obstacle reports.\n\n• Field Staff (demo_staff):\n  Inspect pending hazard queue, verify obstacles (auto-block pathway on graph), resolve with notes.\n\n• Administrator (demo_admin):\n  User directory governance, role assignment, audit logs, sole-admin protection, data reliability governance."
    for p in tf4_2.paragraphs:
        p.font.size = Pt(12)
        p.font.color.rgb = C_WHITE

    # =========================================================================
    # SLIDE 5: TECHNOLOGY STACK
    # =========================================================================
    s5 = add_base_slide("Modern Full-Stack Engineering Technology Stack", "Architecture & Tech Stack")
    
    tech_categories = [
        ("Presentation & Web UI", "Streamlit 1.67.0", "Python reactive web UI, multi-page routing, session state singletons, dark green glassmorphism CSS."),
        ("3D Graphics Engine", "Three.js (r128 WebGL)", "Hardware-accelerated 3D canvas, directional shadow lights, procedural room geometry, camera presets."),
        ("Graph & Algorithmics", "NetworkX 3.7", "Undirected weighted spatial graph, Dijkstra algorithm, BFS shortest path, dynamic detour penalization."),
        ("Database & Persistence", "SQLite3 (WAL Mode)", "Write-Ahead Logging, 5s timeout, PBKDF2 hashing, automated snapshot backups, audit trails."),
        ("Data Visualization", "Plotly 7.1.0", "Interactive accessibility donuts, hazard lifecycle bars, floor distribution and resolution time gauges."),
        ("Containerization & Proxy", "Docker & Nginx", "Multi-stage python:3.11-slim, non-root user appuser (UID 10001), WebSocket stream reverse proxy.")
    ]
    for idx, (cat, name, detail) in enumerate(tech_categories):
        col = idx % 2
        row = idx // 2
        left = Inches(0.8 + col * 6.0)
        top = Inches(1.8 + row * 1.7)
        add_card(s5, left, top, Inches(5.7), Inches(1.5), cat)
        tb = s5.shapes.add_textbox(left + Inches(0.2), top + Inches(0.5), Inches(5.3), Inches(0.9))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = name + " — "
        r1.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = C_WHITE
        r2 = p1.add_run()
        r2.text = detail
        r2.font.size = Pt(10)
        r2.font.color.rgb = C_MUTED

    # =========================================================================
    # SLIDE 6: SYSTEM ARCHITECTURE
    # =========================================================================
    s6 = add_base_slide("Three-Tier System Architecture & Data Flow", "System Architecture")
    
    add_card(s6, Inches(0.8), Inches(1.8), Inches(3.6), Inches(5.0), "Tier 1: Presentation Layer")
    tb6_1 = s6.shapes.add_textbox(Inches(1.0), Inches(2.4), Inches(3.2), Inches(4.2))
    tf6_1 = tb6_1.text_frame
    tf6_1.word_wrap = True
    tf6_1.paragraphs[0].text = "• Streamlit Multi-Page Router\n• Three.js WebGL 3D Canvas\n• Plotly Analytics Visualizer\n• Multilingual i18n Engine (en, kn, hi)\n• WCAG AAA High-Contrast CSS\n• Responsive Mobile Breakpoints"
    for p in tf6_1.paragraphs:
        p.font.size = Pt(12)
        p.font.color.rgb = C_WHITE

    add_card(s6, Inches(4.8), Inches(1.8), Inches(3.6), Inches(5.0), "Tier 2: Algorithmic Logic")
    tb6_2 = s6.shapes.add_textbox(Inches(5.0), Inches(2.4), Inches(3.2), Inches(4.2))
    tf6_2 = tb6_2.text_frame
    tf6_2.word_wrap = True
    tf6_2.paragraphs[0].text = "• RouteFinder: Dijkstra & BFS\n• AccessibilityEngine: Heuristic scoring\n• ObstacleManager: In-graph blocking\n• DestinationSearch: Relevance ranking\n• NavigationSession: FSM wayfinding\n• NavigationInstructions: Vector cross-product"
    for p in tf6_2.paragraphs:
        p.font.size = Pt(12)
        p.font.color.rgb = C_WHITE

    add_card(s6, Inches(8.8), Inches(1.8), Inches(3.7), Inches(5.0), "Tier 3: Persistence & Security")
    tb6_3 = s6.shapes.add_textbox(Inches(9.0), Inches(2.4), Inches(3.3), Inches(4.2))
    tf6_3 = tb6_3.text_frame
    tf6_3.word_wrap = True
    tf6_3.paragraphs[0].text = "• NetworkX 79-Node Spatial Graph\n• SQLite 3 in WAL Journal Mode\n• PBKDF2-HMAC-SHA256 (600k rounds)\n• Brute-Force Rate Limiting Lockout\n• Immutable Audit Trail Log\n• PostgresMigration: Cloud SQL exporter"
    for p in tf6_3.paragraphs:
        p.font.size = Pt(12)
        p.font.color.rgb = C_WHITE

    # =========================================================================
    # SLIDE 7: CAMPUS DIGITAL TWIN
    # =========================================================================
    s7 = add_base_slide("JAIN Global Campus & 5-Floor FET 3D Digital Twin", "3D Digital Twin")
    
    add_card(s7, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "Complete Outdoor 300-Acre Campus")
    tb7_1 = s7.shapes.add_textbox(Inches(1.0), Inches(2.4), Inches(5.2), Inches(4.2))
    tf7_1 = tb7_1.text_frame
    tf7_1.word_wrap = True
    tf7_1.paragraphs[0].text = "• Kanakapura Road (NH-948) with arterial crosswalks.\n• Octagonal FET Building Complex with central courtyard.\n• Colosseum Arena with classical curved colonnade pillars.\n• JIRS Aquatic Center: 50m Olympic pool & glass pavilion.\n• Cricket Stadium with clay pitch & 4-lane athletic track.\n• SBMJCE Dining Complex & Student Hostel Blocks.\n• Aerospace Testing Labs with barrel-vaulted hangar.\n• 60+ instanced 3D organic trees and illuminated bollards."
    for p in tf7_1.paragraphs:
        p.font.size = Pt(11)
        p.font.color.rgb = C_WHITE

    add_card(s7, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0), "Five-Floor FET Building Reconstruction")
    tb7_2 = s7.shapes.add_textbox(Inches(7.0), Inches(2.4), Inches(5.3), Inches(4.2))
    tf7_2 = tb7_2.text_frame
    tf7_2.word_wrap = True
    tf7_2.paragraphs[0].text = "• Ground Floor (0.0m): Portico, Amphitheater, Civil Lab, ADA Ramp.\n• First Floor (3.5m): Electronics Labs, Microprocessor Lab, Suites.\n• Second Floor (7.0m): AI Labs, HPC Supercomputer Cluster.\n• Third Floor (10.5m): CAD Lab, Robotics & Automation Wing.\n• Fourth Floor (14.0m): Library & Stacks, Ramanujan Conference Hall.\n\n• Mathematical Zero-Shear Invariant: Elevator shaft (-6.0, 18.0) invariant across all 5 tiers (0.00m displacement).\n• 5-Floor Exploded View: Separates slabs vertically along guide rods."
    for p in tf7_2.paragraphs:
        p.font.size = Pt(11)
        p.font.color.rgb = C_WHITE

    # =========================================================================
    # SLIDE 8: NAVIGATION ALGORITHMS
    # =========================================================================
    s8 = add_base_slide("Pathfinding Algorithms: Dijkstra vs. Breadth-First Search", "Algorithms & Complexity")
    
    # Comparison Table
    table_shape = s8.shapes.add_table(5, 4, Inches(0.8), Inches(1.8), Inches(11.733), Inches(2.8))
    t = table_shape.table
    t.columns[0].width = Inches(2.2)
    t.columns[1].width = Inches(3.2)
    t.columns[2].width = Inches(3.2)
    t.columns[3].width = Inches(3.133)

    headers = ["Evaluation Metric", "Dijkstra's Algorithm", "Breadth-First Search (BFS)", "Pedestrian Impact"]
    for i, h in enumerate(headers):
        cell = t.cell(0, i)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_EMERALD
        p = cell.text_frame.paragraphs[0]
        p.font.bold = True
        p.font.size = Pt(11)
        p.font.color.rgb = C_WHITE

    rows = [
        ("Graph Type", "Weighted Graph (Distance / Time)", "Unweighted Graph (Hop Count)", "Dijkstra optimizes meters; BFS turns"),
        ("Time Complexity", "O((V + E) log V) with min-heap", "O(V + E) with FIFO queue", "Both execute in < 2ms on 79-node graph"),
        ("Space Complexity", "O(V) for heap and dist map", "O(V) for visited set & queue", "Minimal memory footprint (< 100 KB)"),
        ("Primary Use Case", "Shortest physical distance walked", "Fewest corridor turns and hops", "Simpler cognitive navigation for visitors")
    ]
    for r_idx, row in enumerate(rows, start=1):
        for c_idx, val in enumerate(row):
            cell = t.cell(r_idx, c_idx)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = C_CARD_BG
            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(10)
            p.font.color.rgb = C_WHITE

    add_card(s8, Inches(0.8), Inches(5.0), Inches(11.733), Inches(1.8), "Algorithm Selection & Trade-Off Comparison")
    tb8 = s8.shapes.add_textbox(Inches(1.0), Inches(5.4), Inches(11.333), Inches(1.3))
    tf8 = tb8.text_frame
    tf8.word_wrap = True
    tf8.paragraphs[0].text = "• The system calculates both Dijkstra and BFS simultaneously, offering users an intelligent trade-off card.\n• Penalty Detour Routing: When alternative routes are requested, visited edges are assigned temporary weight penalties (1.5x) to compute distinct, viable alternative corridors."
    for p in tf8.paragraphs:
        p.font.size = Pt(11)
        p.font.color.rgb = C_WHITE

    # =========================================================================
    # SLIDE 9: WHEELCHAIR ACCESSIBILITY
    # =========================================================================
    s9 = add_base_slide("Wheelchair-Accessible Step-Free Routing Logic", "Universal Accessibility")
    
    add_card(s9, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "Constrained Subgraph Formulation")
    tb9_1 = s9.shapes.add_textbox(Inches(1.0), Inches(2.4), Inches(5.2), Inches(4.2))
    tf9_1 = tb9_1.text_frame
    tf9_1.word_wrap = True
    tf9_1.paragraphs[0].text = "• Strict Edge Pruning: In wheelchair mode, the graph engine removes any edge with has_stairs == True or wheelchair_accessible == False.\n\n• Absolute Staircase Exclusion: All 18 vertical staircase edges are pruned, guaranteeing 0 stair encounters.\n\n• Ramp & Elevator Prioritization: Automatically routes through the West ADA Ramp into the ground foyer and uses the central elevator bank for vertical transitions.\n\n• Verified Invariant: Over 6,162 directed test pairs, 100% of generated wheelchair routes are step-free."
    for p in tf9_1.paragraphs:
        p.font.size = Pt(11)
        p.font.color.rgb = C_WHITE

    add_card(s9, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0), "Continuous Heuristic Accessibility Scoring (0–100)")
    tb9_2 = s9.shapes.add_textbox(Inches(7.0), Inches(2.4), Inches(5.3), Inches(4.2))
    tf9_2 = tb9_2.text_frame
    tf9_2.word_wrap = True
    tf9_2.paragraphs[0].text = "• Transparent Heuristic Formula: Evaluated by AccessibilityEngine:\n  Score = 100 - (Stairs * 40) - (Ramp Slope) - (Obstacle * 100)\n\n• Classification Categories:\n  - Fully Accessible (Score 90–100): Step-free, automated doors, elevator.\n  - Accessible with Assistance (Score 60–89): Steep ramps, manual doors.\n  - Not Wheelchair Accessible (Score 0): Staircase barriers.\n  - Temporarily Blocked: Active hazard or maintenance closure.\n\n• Explicit In-App Disclaimer: Clarified as an optimization heuristic, not an official statutory building certification."
    for p in tf9_2.paragraphs:
        p.font.size = Pt(11)
        p.font.color.rgb = C_WHITE

    # =========================================================================
    # SLIDE 10: OBSTACLE MANAGEMENT
    # =========================================================================
    s10 = add_base_slide("Dynamic Obstacle Management & In-Transit Rerouting", "Hazard Tracking")
    
    stages = [
        ("1. Citizen Reporting", "Students / visitors submit hazard report specifying category (Blocked pathway, Construction), severity, and corridor."),
        ("2. Pending Triage", "Report enters 'Pending' status. Does NOT block graph to prevent malicious denial-of-service disruptions."),
        ("3. Staff Verification", "Field Staff or Admin inspects report and clicks 'Verify'. Edge is immediately blocked in NetworkX graph and rendered in red."),
        ("4. Dynamic Detour", "Active navigation sessions detecting verified hazard along forward route automatically recalculate detour around barrier."),
        ("5. Maintenance Clear", "Staff resolves obstacle with mandatory audit notes. Pathway is restored to operational green immediately.")
    ]
    for idx, (title, desc) in enumerate(stages):
        top_y = Inches(1.8 + idx * 1.0)
        card = add_card(s10, Inches(0.8), top_y, Inches(11.733), Inches(0.85))
        tb = s10.shapes.add_textbox(Inches(1.0), top_y + Inches(0.1), Inches(11.3), Inches(0.65))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = title + " — "
        r1.bold = True
        r1.font.size = Pt(12)
        r1.font.color.rgb = C_MINT
        r2 = p1.add_run()
        r2.text = desc
        r2.font.size = Pt(11)
        r2.font.color.rgb = C_WHITE

    # =========================================================================
    # SLIDE 11: SECURITY & DATABASE ARCHITECTURE
    # =========================================================================
    s11 = add_base_slide("Cybersecurity Hardening & Enterprise Database Design", "Security & Database")
    
    sec_features = [
        ("PBKDF2 Password Hashing", "HMAC-SHA256 with unique 32-byte salts and 600,000 iterations (OWASP compliant). Transparent upgrade of legacy hashes on login."),
        ("Brute-Force Rate Limiting", "Tracks failed attempts per user. Locks account for 15 minutes after 5 consecutive failures, raising SecurityLockoutError."),
        ("Role-Based Access Control", "Backend service-layer RBAC across Student, Field Staff, and Admin. Prevents unauthorized report verification or privilege elevation."),
        ("Sole-Admin Protection", "Database integrity guard preventing the sole active administrator from demoting or deactivating their own account."),
        ("SQLite WAL Journaling", "Write-Ahead Logging with 5000ms busy timeout enables concurrent readers without locking the database writer."),
        ("Immutable Audit Logging", "Every user creation, role elevation, obstacle verification, and resolution writes an immutable record to administrative_audit_log.")
    ]
    for idx, (title, desc) in enumerate(sec_features):
        col = idx % 2
        row = idx // 2
        left = Inches(0.8 + col * 6.0)
        top = Inches(1.8 + row * 1.7)
        add_card(s11, left, top, Inches(5.7), Inches(1.5), title)
        tb = s11.shapes.add_textbox(left + Inches(0.2), top + Inches(0.5), Inches(5.3), Inches(0.9))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = desc
        p.font.size = Pt(10)
        p.font.color.rgb = C_WHITE

    # =========================================================================
    # SLIDE 12: ANALYTICS DASHBOARD
    # =========================================================================
    s12 = add_base_slide("Campus Analytics Dashboard & Telemetry Visualizations", "Campus Intelligence")
    
    add_card(s12, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "Executive Telemetry & KPI Cards")
    tb12_1 = s12.shapes.add_textbox(Inches(1.0), Inches(2.4), Inches(5.2), Inches(4.2))
    tf12_1 = tb12_1.text_frame
    tf12_1.word_wrap = True
    tf12_1.paragraphs[0].text = "• Total Verified Locations: 79 campus facilities.\n• Total Walkable Pathways: 106 spatial connections.\n• Step-Free Accessible Ratio: 83.0% (88 accessible connections).\n• Staircase Barrier Count: 18 pathways.\n• Active Obstacle Tracking: Real-time hazard count.\n• Average Resolution Time: Measured turnaround in hours.\n• Dual-Dataset Switching: Toggle between 79-node JAIN Digital Twin and 15-node Schematic Benchmark."
    for p in tf12_1.paragraphs:
        p.font.size = Pt(11)
        p.font.color.rgb = C_WHITE

    add_card(s12, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0), "Four Interactive Plotly Visualizations")
    tb12_2 = s12.shapes.add_textbox(Inches(7.0), Inches(2.4), Inches(5.3), Inches(4.2))
    tf12_2 = tb12_2.text_frame
    tf12_2.word_wrap = True
    tf12_2.paragraphs[0].text = "1. Pathway Accessibility Classification Donut:\n   Step-free vs. assistance vs. staircase vs. blocked pathways.\n\n2. Obstacle Lifecycle Distribution Bar Chart:\n   Pending vs. verified vs. resolved vs. rejected reports.\n\n3. Floor-by-Floor Hazard Distribution Stacked Chart:\n   Obstacle frequency across Outdoor and Floors 0 through 4.\n\n4. Frequently Blocked Corridors & Resolution Gauge:\n   Operational bottlenecks to guide facility maintenance budgets."
    for p in tf12_2.paragraphs:
        p.font.size = Pt(11)
        p.font.color.rgb = C_WHITE

    # =========================================================================
    # SLIDE 13: TESTING AND RESULTS
    # =========================================================================
    s13 = add_base_slide("Automated Testing, Verification & Quality Assurance", "Testing & Verification")
    
    add_card(s13, Inches(0.8), Inches(1.8), Inches(11.733), Inches(1.4), "Verified Test Execution Results")
    tb13_t = s13.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(11.333), Inches(0.9))
    tf13_t = tb13_t.text_frame
    tf13_t.word_wrap = True
    p = tf13_t.paragraphs[0]
    p.text = "Ran 190 tests in 32.133s — OK (failures=0, errors=0, skipped=0) — 100.0% Pass Rate across 20 Test Modules\nNote: Code coverage tooling was not installed in production venv to preserve stability; line/branch coverage is withheld."
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_MINT

    test_cards = [
        ("Graph & Routing", "test_route_finder.py, test_campus_graph_integrity.py\nAsserts 79 unique IDs, 106 positive weights, all-pairs reachability (6,162 pairs)."),
        ("Accessibility", "test_accessibility.py, test_three_d_map.py\nAsserts 100% staircase exclusion and continuous heuristic score calculations."),
        ("Security & RBAC", "test_auth_rbac.py, test_security_audit.py, test_phase20_security_and_qa.py\nAsserts SQL injection resistance, brute-force lockout, sole-admin protection."),
        ("Deployment & Config", "test_phase21_deployment.py, test_phase17_production_architecture.py\nAsserts Dockerfile appuser non-root security, compose volume mapping, Nginx headers.")
    ]
    for idx, (title, desc) in enumerate(test_cards):
        col = idx % 2
        row = idx // 2
        left = Inches(0.8 + col * 6.0)
        top = Inches(3.4 + row * 1.8)
        add_card(s13, left, top, Inches(5.7), Inches(1.6), title)
        tb = s13.shapes.add_textbox(left + Inches(0.2), top + Inches(0.5), Inches(5.3), Inches(1.0))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = desc
        p.font.size = Pt(10)
        p.font.color.rgb = C_WHITE

    # =========================================================================
    # SLIDE 14: LIMITATIONS AND FUTURE SCOPE
    # =========================================================================
    s14 = add_base_slide("System Limitations & Future Scope", "Limitations & Roadmap")
    
    add_card(s14, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "Academic & System Limitations")
    tb14_1 = s14.shapes.add_textbox(Inches(1.0), Inches(2.4), Inches(5.2), Inches(4.2))
    tf14_1 = tb14_1.text_frame
    tf14_1.word_wrap = True
    tf14_1.paragraphs[0].text = "• Schematic Coordinates: 2D/3D coordinates are illustrative layout values derived from architectural plans, not geodetic GPS survey points.\n\n• Algorithmic Heuristic Advisory: 0–100 accessibility score is an optimization heuristic, not an official ADA or CPWD compliance certificate.\n\n• Simulated Navigation: Real-time traversal simulates 1.2 m/s walking speed; does not interface with physical indoor BLE/UWB hardware.\n\n• Demonstration Hosting: Currently deployed on local host (http://localhost:8501) rather than public cloud domain."
    for p in tf14_1.paragraphs:
        p.font.size = Pt(11)
        p.font.color.rgb = C_WHITE

    add_card(s14, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0), "Future Engineering Enhancements")
    tb14_2 = s14.shapes.add_textbox(Inches(7.0), Inches(2.4), Inches(5.3), Inches(4.2))
    tf14_2 = tb14_2.text_frame
    tf14_2.word_wrap = True
    tf14_2.paragraphs[0].text = "• Physical Indoor Positioning: Integrate Bluetooth Low Energy (BLE) beacon trilateration or Wi-Fi 802.11mc Round Trip Time (RTT).\n\n• Voice-Guided Navigation: Implement Web Speech API text-to-speech to speak directions aloud for visually impaired pedestrians.\n\n• Automated BIM Pipeline: Ingest Autodesk Revit / IFC CAD models to automatically extract multi-floor topological graphs.\n\n• IoT Elevator Outages: Connect campus elevator controller IoT sensors via MQTT to automatically register elevator breakdown reports."
    for p in tf14_2.paragraphs:
        p.font.size = Pt(11)
        p.font.color.rgb = C_WHITE

    # =========================================================================
    # SLIDE 15: CONCLUSION & ACKNOWLEDGEMENTS
    # =========================================================================
    s15 = add_base_slide("Conclusion & Final Academic Handover", "Conclusion")
    
    add_card(s15, Inches(0.8), Inches(1.8), Inches(11.733), Inches(4.0), "Engineering Achievements Summary")
    tb15 = s15.shapes.add_textbox(Inches(1.2), Inches(2.3), Inches(11.0), Inches(3.2))
    tf15 = tb15.text_frame
    tf15.word_wrap = True
    tf15.paragraphs[0].text = "• Successfully transformed JAIN Global Campus into an accessible 3D Digital Twin (79 locations, 106 pathways, 5 floors).\n\n• Formulated mathematically rigorous Dijkstra & BFS routing engines with 100% step-free wheelchair guarantees.\n\n• Built dynamic obstacle tracking, role-based field verification, and automatic in-transit detour recalculation.\n\n• Validated by 190 automated regression tests, SQLite WAL persistence, Docker orchestration, and Nginx proxying.\n\n• Delivered complete academic documentation, presentation, viva preparation, and validation reports."
    for p in tf15.paragraphs:
        p.font.size = Pt(13)
        p.font.color.rgb = C_WHITE

    # Thank you footer card
    add_card(s15, Inches(0.8), Inches(6.0), Inches(11.733), Inches(0.9), "", C_EMERALD)
    tb_ty = s15.shapes.add_textbox(Inches(1.0), Inches(6.15), Inches(11.333), Inches(0.6))
    tf_ty = tb_ty.text_frame
    p_ty = tf_ty.paragraphs[0]
    p_ty.text = "Thank You! Respected Committee Members, I welcome your questions."
    p_ty.font.size = Pt(16)
    p_ty.font.bold = True
    p_ty.font.color.rgb = C_MINT
    p_ty.alignment = PP_ALIGN.CENTER

    prs.save(output_path)
    print(f"[+] PPTX Presentation successfully saved to: {output_path}")


if __name__ == "__main__":
    out_file = os.path.abspath("Accessible_Campus_Navigator_Final_Presentation.pptx")
    build_presentation(out_file)
