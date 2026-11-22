"""
Accessible Campus Navigator - Architecture Diagrams Generator
Student: Rudra Pratap | USN: 25BTRCL214 | JAIN University
Generates 10 high-resolution architecture diagrams in both SVG and PNG format.
"""

import os
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "PROJECT_ARCHITECTURE_DIAGRAMS")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Color Palette (Emerald / Navy / Modern Academic Glassmorphism)
BG_COLOR = "#0B1512"
CARD_BG = "#13231E"
CARD_BORDER = "#1E3B32"
ACCENT_GREEN = "#10B981"
ACCENT_CYAN = "#06B6D4"
ACCENT_BLUE = "#3B82F6"
ACCENT_AMBER = "#F59E0B"
ACCENT_ROSE = "#F43F5E"
TEXT_WHITE = "#F1F5F9"
TEXT_MUTED = "#94A3B8"
EDGE_COLOR = "#334155"

def create_svg_wrapper(title, width, height, content):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#080F0D"/>
      <stop offset="100%" stop-color="#11221C"/>
    </linearGradient>
    <linearGradient id="cardGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#142620"/>
      <stop offset="100%" stop-color="#1A332B"/>
    </linearGradient>
    <linearGradient id="accentGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#10B981"/>
      <stop offset="100%" stop-color="#06B6D4"/>
    </linearGradient>
    <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.4"/>
    </filter>
  </defs>
  <!-- Background -->
  <rect width="{width}" height="{height}" fill="url(#bgGrad)"/>
  
  <!-- Header Bar -->
  <rect x="0" y="0" width="{width}" height="60" fill="#0C1A15"/>
  <line x1="0" y1="60" x2="{width}" y2="60" stroke="#1E3B32" stroke-width="2"/>
  <rect x="24" y="16" width="6" height="28" rx="3" fill="#10B981"/>
  <text x="40" y="37" fill="#F1F5F9" font-family="system-ui, -apple-system, sans-serif" font-size="20" font-weight="bold">{title}</text>
  <text x="{width - 24}" y="37" fill="#64748B" font-family="system-ui, sans-serif" font-size="12" text-anchor="end">Accessible Campus Navigator • JAIN (Deemed-to-be University)</text>

  <!-- Main Content -->
  {content}
  
  <!-- Footer -->
  <line x1="0" y1="{height - 30}" x2="{width}" y2="{height - 30}" stroke="#1E3B32" stroke-width="1"/>
  <text x="24" y="{height - 12}" fill="#64748B" font-family="system-ui, sans-serif" font-size="11">Student: Rudra Pratap | USN: 25BTRCL214 | B.Tech AIML Section D</text>
  <text x="{width - 24}" y="{height - 12}" fill="#64748B" font-family="system-ui, sans-serif" font-size="11" text-anchor="end">Academic Architecture Documentation</text>
</svg>"""

# -------------------------------------------------------------
# Diagram 1: Overall System Architecture
# -------------------------------------------------------------
def gen_diag_01():
    w, h = 1200, 750
    content = """
    <!-- Layer 1: Presentation Layer -->
    <rect x="50" y="90" width="1100" height="150" rx="12" fill="url(#cardGrad)" stroke="#1E3B32" stroke-width="2" filter="url(#shadow)"/>
    <text x="70" y="125" fill="#10B981" font-family="sans-serif" font-size="15" font-weight="bold">LAYER 1: PRESENTATION &amp; CLIENT VIEWPORT</text>
    
    <rect x="80" y="145" width="310" height="75" rx="8" fill="#162E25" stroke="#255243" stroke-width="1.5"/>
    <text x="95" y="175" fill="#FFFFFF" font-family="sans-serif" font-size="14" font-weight="bold">Streamlit Multi-Page UI</text>
    <text x="95" y="198" fill="#94A3B8" font-family="sans-serif" font-size="11">Responsive Layout (360px - 1920px+)</text>
    
    <rect x="420" y="145" width="360" height="75" rx="8" fill="#162E25" stroke="#255243" stroke-width="1.5"/>
    <text x="435" y="175" fill="#FFFFFF" font-family="sans-serif" font-size="14" font-weight="bold">Three.js Interactive 3D Digital Twin</text>
    <text x="435" y="198" fill="#94A3B8" font-family="sans-serif" font-size="11">Outdoor Campus &amp; 5-Floor FET Building</text>
    
    <rect x="810" y="145" width="310" height="75" rx="8" fill="#162E25" stroke="#255243" stroke-width="1.5"/>
    <text x="825" y="175" fill="#FFFFFF" font-family="sans-serif" font-size="14" font-weight="bold">Accessibility &amp; Voice Engine</text>
    <text x="825" y="198" fill="#94A3B8" font-family="sans-serif" font-size="11">High Contrast, Audio Cues, EN / KN / HI</text>

    <!-- Connector Arrows -->
    <line x1="235" y1="240" x2="235" y2="290" stroke="#10B981" stroke-width="2" stroke-dasharray="4,4"/>
    <line x1="600" y1="240" x2="600" y2="290" stroke="#06B6D4" stroke-width="2"/>
    <line x1="965" y1="240" x2="965" y2="290" stroke="#10B981" stroke-width="2" stroke-dasharray="4,4"/>

    <!-- Layer 2: Application Core Services -->
    <rect x="50" y="290" width="1100" height="230" rx="12" fill="url(#cardGrad)" stroke="#1E3B32" stroke-width="2" filter="url(#shadow)"/>
    <text x="70" y="325" fill="#06B6D4" font-family="sans-serif" font-size="15" font-weight="bold">LAYER 2: APPLICATION SERVICES &amp; ROUTING ENGINES</text>
    
    <rect x="80" y="345" width="240" height="150" rx="8" fill="#162E25" stroke="#255243" stroke-width="1.5"/>
    <text x="95" y="375" fill="#38BDF8" font-family="sans-serif" font-size="14" font-weight="bold">Routing Engine</text>
    <text x="95" y="402" fill="#E2E8F0" font-family="sans-serif" font-size="12">• Dijkstra Algorithm</text>
    <text x="95" y="424" fill="#E2E8F0" font-family="sans-serif" font-size="12">• Breadth-First Search</text>
    <text x="95" y="446" fill="#E2E8F0" font-family="sans-serif" font-size="12">• Multi-Route Comparison</text>
    <text x="95" y="468" fill="#94A3B8" font-family="sans-serif" font-size="11">NetworkX Graph Integration</text>

    <rect x="345" y="345" width="240" height="150" rx="8" fill="#162E25" stroke="#255243" stroke-width="1.5"/>
    <text x="360" y="375" fill="#10B981" font-family="sans-serif" font-size="14" font-weight="bold">Accessibility Engine</text>
    <text x="360" y="402" fill="#E2E8F0" font-family="sans-serif" font-size="12">• Step-Free Filtering</text>
    <text x="360" y="424" fill="#E2E8F0" font-family="sans-serif" font-size="12">• Elevator Prioritization</text>
    <text x="360" y="446" fill="#E2E8F0" font-family="sans-serif" font-size="12">• Ramp Path Validation</text>
    <text x="360" y="468" fill="#94A3B8" font-family="sans-serif" font-size="11">RPwD Act 2016 Standards</text>

    <rect x="610" y="345" width="240" height="150" rx="8" fill="#162E25" stroke="#255243" stroke-width="1.5"/>
    <text x="625" y="375" fill="#F59E0B" font-family="sans-serif" font-size="14" font-weight="bold">Dynamic Obstacle Hub</text>
    <text x="625" y="402" fill="#E2E8F0" font-family="sans-serif" font-size="12">• Real-Time Obstacle Query</text>
    <text x="625" y="424" fill="#E2E8F0" font-family="sans-serif" font-size="12">• Weight Penalty Injection</text>
    <text x="625" y="446" fill="#E2E8F0" font-family="sans-serif" font-size="12">• Automatic Rerouting Alert</text>
    <text x="625" y="468" fill="#94A3B8" font-family="sans-serif" font-size="11">Edge Blocking &amp; Penalties</text>

    <rect x="875" y="345" width="245" height="150" rx="8" fill="#162E25" stroke="#255243" stroke-width="1.5"/>
    <text x="890" y="375" fill="#A855F7" font-family="sans-serif" font-size="14" font-weight="bold">Security &amp; Analytics</text>
    <text x="890" y="402" fill="#E2E8F0" font-family="sans-serif" font-size="12">• SHA-256 + Salt Passwords</text>
    <text x="890" y="424" fill="#E2E8F0" font-family="sans-serif" font-size="12">• RBAC: Student/Staff/Admin</text>
    <text x="890" y="446" fill="#E2E8F0" font-family="sans-serif" font-size="12">• Failed Attempt Rate Limiting</text>
    <text x="890" y="468" fill="#94A3B8" font-family="sans-serif" font-size="11">Audit Logging &amp; Analytics</text>

    <!-- Connector Arrows -->
    <line x1="200" y1="520" x2="200" y2="560" stroke="#10B981" stroke-width="2"/>
    <line x1="730" y1="520" x2="730" y2="560" stroke="#F59E0B" stroke-width="2"/>
    <line x1="1000" y1="520" x2="1000" y2="560" stroke="#A855F7" stroke-width="2"/>

    <!-- Layer 3: Data & Storage Layer -->
    <rect x="50" y="560" width="1100" height="130" rx="12" fill="url(#cardGrad)" stroke="#1E3B32" stroke-width="2" filter="url(#shadow)"/>
    <text x="70" y="595" fill="#F43F5E" font-family="sans-serif" font-size="15" font-weight="bold">LAYER 3: DATA PERSISTENCE &amp; TOPOLOGY</text>

    <rect x="80" y="610" width="310" height="60" rx="8" fill="#162E25" stroke="#255243" stroke-width="1.5"/>
    <text x="95" y="635" fill="#FFFFFF" font-family="sans-serif" font-size="13" font-weight="bold">NetworkX Campus Graph</text>
    <text x="95" y="655" fill="#94A3B8" font-family="sans-serif" font-size="11">79 Nodes, 106 Edges, 3D Coordinates</text>

    <rect x="420" y="610" width="360" height="60" rx="8" fill="#162E25" stroke="#255243" stroke-width="1.5"/>
    <text x="435" y="635" fill="#FFFFFF" font-family="sans-serif" font-size="13" font-weight="bold">SQLite Relational Database</text>
    <text x="435" y="655" fill="#94A3B8" font-family="sans-serif" font-size="11">WAL Mode, Automated Daily Backups, Foreign Keys</text>

    <rect x="810" y="610" width="310" height="60" rx="8" fill="#162E25" stroke="#255243" stroke-width="1.5"/>
    <text x="825" y="635" fill="#FFFFFF" font-family="sans-serif" font-size="13" font-weight="bold">PostgreSQL Enterprise Bridge</text>
    <text x="825" y="655" fill="#94A3B8" font-family="sans-serif" font-size="11">Production Migration Exporter &amp; Schemas</text>
    """
    return create_svg_wrapper("01 — Overall System Architecture", w, h, content)

# -------------------------------------------------------------
# Diagram 2: Campus Graph Representation
# -------------------------------------------------------------
def gen_diag_02():
    w, h = 1200, 750
    content = """
    <!-- Outdoor Cluster -->
    <rect x="60" y="100" width="480" height="570" rx="12" fill="url(#cardGrad)" stroke="#10B981" stroke-width="2" filter="url(#shadow)"/>
    <text x="80" y="135" fill="#10B981" font-family="sans-serif" font-size="16" font-weight="bold">OUTDOOR CAMPUS CLUSTER (Nodes: 1 to 24)</text>
    <text x="80" y="155" fill="#94A3B8" font-family="sans-serif" font-size="12">Campus Perimeter, Entrances, Gates &amp; Amenities</text>

    <!-- Outdoor Nodes -->
    <circle cx="140" cy="220" r="28" fill="#162E25" stroke="#10B981" stroke-width="2"/>
    <text x="140" y="225" fill="#FFF" font-family="sans-serif" font-size="10" text-anchor="middle" font-weight="bold">GATE_MAIN</text>

    <circle cx="300" cy="220" r="28" fill="#162E25" stroke="#10B981" stroke-width="2"/>
    <text x="300" y="225" fill="#FFF" font-family="sans-serif" font-size="10" text-anchor="middle" font-weight="bold">SECURITY_1</text>

    <circle cx="450" cy="220" r="28" fill="#162E25" stroke="#10B981" stroke-width="2"/>
    <text x="450" y="225" fill="#FFF" font-family="sans-serif" font-size="10" text-anchor="middle" font-weight="bold">FOUNTAIN</text>

    <circle cx="140" cy="360" r="28" fill="#162E25" stroke="#10B981" stroke-width="2"/>
    <text x="140" y="365" fill="#FFF" font-family="sans-serif" font-size="10" text-anchor="middle" font-weight="bold">FOOD_COURT</text>

    <circle cx="300" cy="360" r="28" fill="#162E25" stroke="#10B981" stroke-width="2"/>
    <text x="300" y="365" fill="#FFF" font-family="sans-serif" font-size="10" text-anchor="middle" font-weight="bold">PARKING_A</text>

    <circle cx="450" cy="360" r="28" fill="#162E25" stroke="#10B981" stroke-width="2"/>
    <text x="450" y="365" fill="#FFF" font-family="sans-serif" font-size="10" text-anchor="middle" font-weight="bold">FET_ENTRANCE</text>

    <circle cx="140" cy="500" r="28" fill="#162E25" stroke="#10B981" stroke-width="2"/>
    <text x="140" y="505" fill="#FFF" font-family="sans-serif" font-size="10" text-anchor="middle" font-weight="bold">HOSTEL_M</text>

    <circle cx="300" cy="500" r="28" fill="#162E25" stroke="#10B981" stroke-width="2"/>
    <text x="300" y="505" fill="#FFF" font-family="sans-serif" font-size="10" text-anchor="middle" font-weight="bold">SPORTS_COMPLEX</text>

    <circle cx="450" cy="500" r="28" fill="#162E25" stroke="#10B981" stroke-width="2"/>
    <text x="450" y="505" fill="#FFF" font-family="sans-serif" font-size="10" text-anchor="middle" font-weight="bold">RAMP_WEST</text>

    <!-- Connectors -->
    <line x1="168" y1="220" x2="272" y2="220" stroke="#255243" stroke-width="2"/>
    <line x1="328" y1="220" x2="422" y2="220" stroke="#255243" stroke-width="2"/>
    <line x1="300" y1="248" x2="300" y2="332" stroke="#255243" stroke-width="2"/>
    <line x1="168" y1="360" x2="272" y2="360" stroke="#255243" stroke-width="2"/>
    <line x1="328" y1="360" x2="422" y2="360" stroke="#255243" stroke-width="2"/>
    <line x1="450" y1="388" x2="450" y2="472" stroke="#10B981" stroke-width="3"/>
    <line x1="300" y1="388" x2="300" y2="472" stroke="#255243" stroke-width="2"/>
    <line x1="168" y1="500" x2="272" y2="500" stroke="#255243" stroke-width="2"/>
    <line x1="328" y1="500" x2="422" y2="500" stroke="#255243" stroke-width="2"/>

    <!-- Bridge Between Outdoor & Indoor -->
    <line x1="478" y1="360" x2="650" y2="360" stroke="#06B6D4" stroke-width="4" stroke-dasharray="6,4"/>
    <rect x="520" y="340" width="90" height="40" rx="6" fill="#0C1A15" stroke="#06B6D4" stroke-width="1"/>
    <text x="565" y="364" fill="#06B6D4" font-family="sans-serif" font-size="11" text-anchor="middle" font-weight="bold">PORTAL</text>

    <!-- Indoor 5-Floor FET Cluster -->
    <rect x="660" y="100" width="480" height="570" rx="12" fill="url(#cardGrad)" stroke="#38BDF8" stroke-width="2" filter="url(#shadow)"/>
    <text x="680" y="135" fill="#38BDF8" font-family="sans-serif" font-size="16" font-weight="bold">INDOOR FET BUILDING CLUSTER (55 Nodes across 5 Floors)</text>
    <text x="680" y="155" fill="#94A3B8" font-family="sans-serif" font-size="12">Multi-floor Vertical Connectors, Corridors, Labs &amp; Classrooms</text>

    <!-- Vertical Connectors -->
    <rect x="685" y="180" width="130" height="460" rx="8" fill="#162E25" stroke="#255243" stroke-width="1"/>
    <text x="750" y="205" fill="#F59E0B" font-family="sans-serif" font-size="12" text-anchor="middle" font-weight="bold">VERTICAL CORES</text>
    
    <circle cx="750" cy="260" r="22" fill="#2A1B0A" stroke="#F59E0B" stroke-width="2"/>
    <text x="750" y="264" fill="#FFF" font-family="sans-serif" font-size="9" text-anchor="middle" font-weight="bold">ELEVATOR_1</text>
    
    <circle cx="750" cy="350" r="22" fill="#2A1B0A" stroke="#F59E0B" stroke-width="2"/>
    <text x="750" y="354" fill="#FFF" font-family="sans-serif" font-size="9" text-anchor="middle" font-weight="bold">ELEVATOR_2</text>

    <circle cx="750" cy="440" r="22" fill="#2A0B0B" stroke="#F43F5E" stroke-width="2"/>
    <text x="750" y="444" fill="#FFF" font-family="sans-serif" font-size="9" text-anchor="middle" font-weight="bold">STAIR_A</text>

    <circle cx="750" cy="530" r="22" fill="#2A0B0B" stroke="#F43F5E" stroke-width="2"/>
    <text x="750" y="534" fill="#FFF" font-family="sans-serif" font-size="9" text-anchor="middle" font-weight="bold">STAIR_B</text>

    <!-- Floor Nodes Grid -->
    <rect x="835" y="180" width="285" height="90" rx="6" fill="#162E25" stroke="#255243" stroke-width="1"/>
    <text x="850" y="205" fill="#38BDF8" font-family="sans-serif" font-size="12" font-weight="bold">Floor 4: Research &amp; HPC</text>
    <text x="850" y="225" fill="#94A3B8" font-family="sans-serif" font-size="11">FET_4F_HPC_CLUSTER, AI Research Lab</text>
    <text x="850" y="245" fill="#10B981" font-family="sans-serif" font-size="11">Connected via Elevators 1 &amp; 2</text>

    <rect x="835" y="280" width="285" height="90" rx="6" fill="#162E25" stroke="#255243" stroke-width="1"/>
    <text x="850" y="305" fill="#38BDF8" font-family="sans-serif" font-size="12" font-weight="bold">Floor 3: Advanced Computing Labs</text>
    <text x="850" y="325" fill="#94A3B8" font-family="sans-serif" font-size="11">FET_3F_LAB_301, Data Science Center</text>
    <text x="850" y="345" fill="#10B981" font-family="sans-serif" font-size="11">Accessible Corridors, Restrooms</text>

    <rect x="835" y="380" width="285" height="90" rx="6" fill="#162E25" stroke="#255243" stroke-width="1"/>
    <text x="850" y="405" fill="#38BDF8" font-family="sans-serif" font-size="12" font-weight="bold">Floor 2: Faculty Cabins &amp; Meeting Rooms</text>
    <text x="850" y="425" fill="#94A3B8" font-family="sans-serif" font-size="11">FET_2F_CSE_DEPT, Conference Hall 2</text>
    <text x="850" y="445" fill="#10B981" font-family="sans-serif" font-size="11">Central Rotunda Transition</text>

    <rect x="835" y="480" width="285" height="80" rx="6" fill="#162E25" stroke="#255243" stroke-width="1"/>
    <text x="850" y="505" fill="#38BDF8" font-family="sans-serif" font-size="12" font-weight="bold">Floor 1: Lecture Halls &amp; Dean's Office</text>
    <text x="850" y="525" fill="#94A3B8" font-family="sans-serif" font-size="11">FET_1F_AUDITORIUM, Dean Office, LH 101-105</text>

    <rect x="835" y="570" width="285" height="70" rx="6" fill="#162E25" stroke="#255243" stroke-width="1"/>
    <text x="850" y="595" fill="#10B981" font-family="sans-serif" font-size="12" font-weight="bold">Ground Floor: Reception, Admin &amp; Entry</text>
    <text x="850" y="615" fill="#94A3B8" font-family="sans-serif" font-size="11">FET_GF_MAIN_FOYER, Ramp West Portal</text>
    """
    return create_svg_wrapper("02 — Campus Graph Topology & Connectors", w, h, content)

# -------------------------------------------------------------
# Diagram 3: BFS Workflow
# -------------------------------------------------------------
def gen_diag_03():
    w, h = 1200, 750
    content = """
    <rect x="80" y="100" width="1040" height="570" rx="12" fill="url(#cardGrad)" stroke="#1E3B32" stroke-width="2" filter="url(#shadow)"/>
    <text x="110" y="140" fill="#38BDF8" font-family="sans-serif" font-size="18" font-weight="bold">BREADTH-FIRST SEARCH (BFS) ALGORITHM EXECUTION FLOW</text>
    <text x="110" y="165" fill="#94A3B8" font-family="sans-serif" font-size="13">Unweighted Shortest Path Traversal — Guarantees Minimum Intermediate Hops</text>

    <!-- Step 1 -->
    <rect x="110" y="200" width="220" height="110" rx="8" fill="#162E25" stroke="#38BDF8" stroke-width="2"/>
    <circle cx="140" cy="225" r="14" fill="#38BDF8"/>
    <text x="140" y="230" fill="#000" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle">1</text>
    <text x="165" y="230" fill="#FFF" font-family="sans-serif" font-size="14" font-weight="bold">Initialization</text>
    <text x="125" y="260" fill="#94A3B8" font-family="sans-serif" font-size="11">• Queue Q = [start_node]</text>
    <text x="125" y="280" fill="#94A3B8" font-family="sans-serif" font-size="11">• Visited = {start_node}</text>
    <text x="125" y="300" fill="#94A3B8" font-family="sans-serif" font-size="11">• Parent map = {start: None}</text>

    <!-- Arrow 1 to 2 -->
    <line x1="330" y1="255" x2="380" y2="255" stroke="#38BDF8" stroke-width="3"/>

    <!-- Step 2 -->
    <rect x="380" y="200" width="220" height="110" rx="8" fill="#162E25" stroke="#38BDF8" stroke-width="2"/>
    <circle cx="410" cy="225" r="14" fill="#38BDF8"/>
    <text x="410" y="230" fill="#000" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle">2</text>
    <text x="435" y="230" fill="#FFF" font-family="sans-serif" font-size="14" font-weight="bold">Dequeue Node</text>
    <text x="395" y="260" fill="#94A3B8" font-family="sans-serif" font-size="11">• current = Q.pop(0)</text>
    <text x="395" y="280" fill="#94A3B8" font-family="sans-serif" font-size="11">• If current == target:</text>
    <text x="405" y="300" fill="#10B981" font-family="sans-serif" font-size="11">→ Advance to Step 5</text>

    <!-- Arrow 2 to 3 -->
    <line x1="600" y1="255" x2="650" y2="255" stroke="#38BDF8" stroke-width="3"/>

    <!-- Step 3 -->
    <rect x="650" y="200" width="220" height="110" rx="8" fill="#162E25" stroke="#38BDF8" stroke-width="2"/>
    <circle cx="680" cy="225" r="14" fill="#38BDF8"/>
    <text x="680" y="230" fill="#000" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle">3</text>
    <text x="705" y="230" fill="#FFF" font-family="sans-serif" font-size="14" font-weight="bold">Neighbor Check</text>
    <text x="665" y="260" fill="#94A3B8" font-family="sans-serif" font-size="11">• For nbr in G.neighbors(curr):</text>
    <text x="665" y="280" fill="#94A3B8" font-family="sans-serif" font-size="11">• If accessible_only and</text>
    <text x="675" y="300" fill="#F43F5E" font-family="sans-serif" font-size="11">edge is inaccessible: SKIP</text>

    <!-- Arrow 3 to 4 -->
    <line x1="870" y1="255" x2="920" y2="255" stroke="#38BDF8" stroke-width="3"/>

    <!-- Step 4 -->
    <rect x="920" y="200" width="180" height="110" rx="8" fill="#162E25" stroke="#38BDF8" stroke-width="2"/>
    <circle cx="950" cy="225" r="14" fill="#38BDF8"/>
    <text x="950" y="230" fill="#000" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle">4</text>
    <text x="975" y="230" fill="#FFF" font-family="sans-serif" font-size="14" font-weight="bold">Enqueue</text>
    <text x="935" y="260" fill="#94A3B8" font-family="sans-serif" font-size="11">• If nbr not in visited:</text>
    <text x="935" y="280" fill="#94A3B8" font-family="sans-serif" font-size="11">• visited.add(nbr)</text>
    <text x="935" y="300" fill="#94A3B8" font-family="sans-serif" font-size="11">• Q.append(nbr)</text>

    <!-- Feedback loop from 4 back to 2 -->
    <path d="M 1010 310 L 1010 360 L 490 360 L 490 310" fill="none" stroke="#F59E0B" stroke-width="2" stroke-dasharray="4,4"/>
    <text x="750" y="355" fill="#F59E0B" font-family="sans-serif" font-size="11" text-anchor="middle">Repeat until Queue empty or Target reached</text>

    <!-- Bottom Step 5: Backtracking & Result -->
    <rect x="250" y="420" width="700" height="170" rx="10" fill="#142B23" stroke="#10B981" stroke-width="2"/>
    <circle cx="280" cy="450" r="16" fill="#10B981"/>
    <text x="280" y="455" fill="#000" font-family="sans-serif" font-size="13" font-weight="bold" text-anchor="middle">5</text>
    <text x="310" y="455" fill="#10B981" font-family="sans-serif" font-size="16" font-weight="bold">Path Backtracking &amp; Metric Aggregation</text>
    
    <text x="280" y="490" fill="#E2E8F0" font-family="sans-serif" font-size="12">• Reconstruct node sequence: target → parent[target] → ... → start_node</text>
    <text x="280" y="515" fill="#E2E8F0" font-family="sans-serif" font-size="12">• Reverse sequence to obtain chronological forward navigation itinerary</text>
    <text x="280" y="540" fill="#E2E8F0" font-family="sans-serif" font-size="12">• Calculate total physical distance: sum(edge_weights along path)</text>
    <text x="280" y="565" fill="#38BDF8" font-family="sans-serif" font-size="12">• Time Complexity: O(V + E) | Space Complexity: O(V)</text>
    """
    return create_svg_wrapper("03 — Breadth-First Search (BFS) Traversal Workflow", w, h, content)

# -------------------------------------------------------------
# Diagram 4: Dijkstra Workflow
# -------------------------------------------------------------
def gen_diag_04():
    w, h = 1200, 750
    content = """
    <rect x="80" y="100" width="1040" height="570" rx="12" fill="url(#cardGrad)" stroke="#1E3B32" stroke-width="2" filter="url(#shadow)"/>
    <text x="110" y="140" fill="#10B981" font-family="sans-serif" font-size="18" font-weight="bold">DIJKSTRA'S WEIGHTED SHORTEST PATH ALGORITHM</text>
    <text x="110" y="165" fill="#94A3B8" font-family="sans-serif" font-size="13">Priority Queue (Min-Heap) Optimization for Globally Shortest Physical Distance</text>

    <!-- Priority Queue & Dist Array -->
    <rect x="110" y="200" width="280" height="430" rx="8" fill="#162E25" stroke="#10B981" stroke-width="1.5"/>
    <text x="130" y="230" fill="#10B981" font-family="sans-serif" font-size="14" font-weight="bold">Data Structures</text>
    
    <rect x="130" y="250" width="240" height="150" rx="6" fill="#0C1A15" stroke="#255243" stroke-width="1"/>
    <text x="145" y="275" fill="#38BDF8" font-family="sans-serif" font-size="12" font-weight="bold">Distances Table d[u]</text>
    <text x="145" y="300" fill="#94A3B8" font-family="sans-serif" font-size="11">d[start] = 0.0</text>
    <text x="145" y="325" fill="#94A3B8" font-family="sans-serif" font-size="11">d[node_1] = 45.2 m</text>
    <text x="145" y="350" fill="#94A3B8" font-family="sans-serif" font-size="11">d[node_2] = 88.0 m</text>
    <text x="145" y="375" fill="#64748B" font-family="sans-serif" font-size="11">d[others] = ∞</text>

    <rect x="130" y="420" width="240" height="190" rx="6" fill="#0C1A15" stroke="#255243" stroke-width="1"/>
    <text x="145" y="445" fill="#F59E0B" font-family="sans-serif" font-size="12" font-weight="bold">Min-Heap Priority Queue</text>
    <text x="145" y="470" fill="#94A3B8" font-family="sans-serif" font-size="11">heapq.heappush(pq, (dist, u))</text>
    <text x="145" y="495" fill="#E2E8F0" font-family="sans-serif" font-size="11">• Extract minimum distance</text>
    <text x="145" y="520" fill="#E2E8F0" font-family="sans-serif" font-size="11">• O(log V) extraction speed</text>
    <text x="145" y="545" fill="#E2E8F0" font-family="sans-serif" font-size="11">• Dynamic obstacle penalty:</text>
    <text x="155" y="568" fill="#F43F5E" font-family="sans-serif" font-size="11">w' = w + 10,000 if blocked</text>

    <!-- Edge Relaxation Process -->
    <rect x="430" y="200" width="660" height="210" rx="8" fill="#162E25" stroke="#255243" stroke-width="1.5"/>
    <text x="455" y="230" fill="#38BDF8" font-family="sans-serif" font-size="15" font-weight="bold">Edge Relaxation Step (Core Equation)</text>
    
    <rect x="455" y="250" width="610" height="50" rx="6" fill="#0C1A15" stroke="#38BDF8" stroke-width="1"/>
    <text x="760" y="282" fill="#38BDF8" font-family="monospace" font-size="15" font-weight="bold" text-anchor="middle">if d[u] + weight(u, v) &lt; d[v]:  d[v] = d[u] + weight(u, v)</text>

    <text x="455" y="325" fill="#E2E8F0" font-family="sans-serif" font-size="12">1. When examining edge (u, v), check if path through u offers a shorter overall route.</text>
    <text x="455" y="350" fill="#E2E8F0" font-family="sans-serif" font-size="12">2. Update predecessor pointer: parent[v] = u.</text>
    <text x="455" y="375" fill="#E2E8F0" font-family="sans-serif" font-size="12">3. Push updated distance tuple (d[v], v) into the min-heap priority queue.</text>

    <!-- Obstacle & Complexity Summary -->
    <rect x="430" y="430" width="660" height="200" rx="8" fill="#162E25" stroke="#255243" stroke-width="1.5"/>
    <text x="455" y="460" fill="#F59E0B" font-family="sans-serif" font-size="15" font-weight="bold">Obstacle Penalty &amp; Complexity Profile</text>
    
    <text x="455" y="495" fill="#E2E8F0" font-family="sans-serif" font-size="12">• Active Obstacle Weighting: Temporarily increases edge cost by 10,000 meters,</text>
    <text x="470" y="515" fill="#94A3B8" font-family="sans-serif" font-size="12">causing Dijkstra's min-heap to explore safe detour paths automatically.</text>
    
    <text x="455" y="545" fill="#10B981" font-family="sans-serif" font-size="13" font-weight="bold">• Time Complexity: O((E + V) log V) via Binary Min-Heap</text>
    <text x="455" y="570" fill="#10B981" font-family="sans-serif" font-size="13" font-weight="bold">• Space Complexity: O(V) for distance table and parent mapping</text>
    <text x="455" y="595" fill="#94A3B8" font-family="sans-serif" font-size="12">• Verified Benchmark: &lt; 5 milliseconds execution time across 79-node campus graph</text>
    """
    return create_svg_wrapper("04 — Dijkstra's Weighted Routing & Relaxation Flow", w, h, content)

# -------------------------------------------------------------
# Diagram 5: Wheelchair Accessible Routing
# -------------------------------------------------------------
def gen_diag_05():
    w, h = 1200, 750
    content = """
    <rect x="80" y="100" width="1040" height="570" rx="12" fill="url(#cardGrad)" stroke="#10B981" stroke-width="2" filter="url(#shadow)"/>
    <text x="110" y="140" fill="#10B981" font-family="sans-serif" font-size="18" font-weight="bold">WHEELCHAIR-ACCESSIBLE &amp; STEP-FREE FILTERING PIPELINE</text>
    <text x="110" y="165" fill="#94A3B8" font-family="sans-serif" font-size="13">Strict Compliance with RPwD Act 2016 &amp; Harmonized Accessibility Guidelines</text>

    <!-- Column 1: Request & Profile -->
    <rect x="110" y="200" width="270" height="430" rx="8" fill="#162E25" stroke="#255243" stroke-width="1.5"/>
    <text x="130" y="235" fill="#10B981" font-family="sans-serif" font-size="15" font-weight="bold">1. Accessibility Request</text>
    
    <rect x="130" y="255" width="230" height="90" rx="6" fill="#0C1A15" stroke="#10B981" stroke-width="1"/>
    <text x="145" y="280" fill="#FFF" font-family="sans-serif" font-size="12" font-weight="bold">User Navigation Profile</text>
    <text x="145" y="305" fill="#10B981" font-family="sans-serif" font-size="11">wheelchair_mode = True</text>
    <text x="145" y="325" fill="#94A3B8" font-family="sans-serif" font-size="11">step_free_preference = True</text>

    <text x="130" y="375" fill="#E2E8F0" font-family="sans-serif" font-size="12" font-weight="bold">Target Traversal:</text>
    <text x="130" y="400" fill="#94A3B8" font-family="sans-serif" font-size="11">Origin: Ground Floor Entrance</text>
    <text x="130" y="420" fill="#94A3B8" font-family="sans-serif" font-size="11">Destination: Floor 3 CSE Lab</text>
    
    <rect x="130" y="450" width="230" height="150" rx="6" fill="#0C1A15" stroke="#255243" stroke-width="1"/>
    <text x="145" y="475" fill="#F59E0B" font-family="sans-serif" font-size="12" font-weight="bold">Safety Constraints</text>
    <text x="145" y="500" fill="#94A3B8" font-family="sans-serif" font-size="11">• Max Ramp Slope: 1:12 (8.33%)</text>
    <text x="145" y="525" fill="#94A3B8" font-family="sans-serif" font-size="11">• Minimum Clear Width: 900 mm</text>
    <text x="145" y="550" fill="#94A3B8" font-family="sans-serif" font-size="11">• Zero step tolerance (0 stairs)</text>
    <text x="145" y="575" fill="#94A3B8" font-family="sans-serif" font-size="11">• Elevator door width: 800 mm</text>

    <!-- Connector -->
    <line x1="380" y1="415" x2="430" y2="415" stroke="#10B981" stroke-width="3"/>

    <!-- Column 2: Graph Filtering Logic -->
    <rect x="430" y="200" width="360" height="430" rx="8" fill="#162E25" stroke="#255243" stroke-width="1.5"/>
    <text x="450" y="235" fill="#38BDF8" font-family="sans-serif" font-size="15" font-weight="bold">2. Subgraph Filtering Engine</text>

    <rect x="450" y="255" width="320" height="150" rx="6" fill="#2A0B0B" stroke="#F43F5E" stroke-width="1.5"/>
    <text x="465" y="280" fill="#F43F5E" font-family="sans-serif" font-size="13" font-weight="bold">Strict Exclusion Rules (Blocked)</text>
    <text x="465" y="305" fill="#FCA5A5" font-family="sans-serif" font-size="12">❌ FET_STAIR_A (All 5 Floors)</text>
    <text x="465" y="330" fill="#FCA5A5" font-family="sans-serif" font-size="12">❌ FET_STAIR_B (All 5 Floors)</text>
    <text x="465" y="355" fill="#FCA5A5" font-family="sans-serif" font-size="12">❌ High-Curb Outdoor Footpaths</text>
    <text x="465" y="380" fill="#FCA5A5" font-family="sans-serif" font-size="12">❌ Edges with is_accessible == False</text>

    <rect x="450" y="430" width="320" height="170" rx="6" fill="#0E281E" stroke="#10B981" stroke-width="1.5"/>
    <text x="465" y="455" fill="#10B981" font-family="sans-serif" font-size="13" font-weight="bold">Approved Accessible Connectors</text>
    <text x="465" y="480" fill="#6EE7B7" font-family="sans-serif" font-size="12">✓ FET_ELEVATOR_1 (Floor 0 to 4)</text>
    <text x="465" y="505" fill="#6EE7B7" font-family="sans-serif" font-size="12">✓ FET_ELEVATOR_2 (Floor 0 to 4)</text>
    <text x="465" y="530" fill="#6EE7B7" font-family="sans-serif" font-size="12">✓ West Exterior Ramp (Slope 1:12)</text>
    <text x="465" y="555" fill="#6EE7B7" font-family="sans-serif" font-size="12">✓ East Access Ramp (Ground Foyer)</text>
    <text x="465" y="580" fill="#6EE7B7" font-family="sans-serif" font-size="12">✓ Level Floor Corridors &amp; Rotunda</text>

    <!-- Connector -->
    <line x1="790" y1="415" x2="840" y2="415" stroke="#10B981" stroke-width="3"/>

    <!-- Column 3: Generated Route Verification -->
    <rect x="840" y="200" width="250" height="430" rx="8" fill="#162E25" stroke="#255243" stroke-width="1.5"/>
    <text x="860" y="235" fill="#10B981" font-family="sans-serif" font-size="15" font-weight="bold">3. Validated Output</text>

    <rect x="855" y="255" width="220" height="200" rx="6" fill="#0C1A15" stroke="#10B981" stroke-width="1"/>
    <text x="870" y="280" fill="#FFF" font-family="sans-serif" font-size="12" font-weight="bold">Route Itinerary</text>
    <text x="870" y="305" fill="#10B981" font-family="sans-serif" font-size="11">1. Gate Main</text>
    <text x="870" y="325" fill="#10B981" font-family="sans-serif" font-size="11">2. Paved Promenade</text>
    <text x="870" y="345" fill="#10B981" font-family="sans-serif" font-size="11">3. Ramp West</text>
    <text x="870" y="365" fill="#10B981" font-family="sans-serif" font-size="11">4. FET Entrance Foyer</text>
    <text x="870" y="385" fill="#38BDF8" font-family="sans-serif" font-size="11">5. Elevator 1 (to Floor 3)</text>
    <text x="870" y="405" fill="#10B981" font-family="sans-serif" font-size="11">6. Floor 3 Main Hallway</text>
    <text x="870" y="425" fill="#10B981" font-family="sans-serif" font-size="11">7. Room 301 (Lab)</text>

    <rect x="855" y="470" width="220" height="130" rx="6" fill="#142B23" stroke="#255243" stroke-width="1"/>
    <text x="870" y="495" fill="#F59E0B" font-family="sans-serif" font-size="12" font-weight="bold">Audit Guarantee</text>
    <text x="870" y="520" fill="#94A3B8" font-family="sans-serif" font-size="11">• Stair Count: 0</text>
    <text x="870" y="540" fill="#94A3B8" font-family="sans-serif" font-size="11">• 100% Step-Free</text>
    <text x="870" y="560" fill="#94A3B8" font-family="sans-serif" font-size="11">• Voice guidance ready</text>
    <text x="870" y="580" fill="#94A3B8" font-family="sans-serif" font-size="11">• Verified in 190 test suite</text>
    """
    return create_svg_wrapper("05 — Wheelchair-Accessible Subgraph Filtering Pipeline", w, h, content)

# -------------------------------------------------------------
# Diagram 6: Obstacle Reporting Lifecycle
# -------------------------------------------------------------
def gen_diag_06():
    w, h = 1200, 750
    content = """
    <rect x="80" y="100" width="1040" height="570" rx="12" fill="url(#cardGrad)" stroke="#1E3B32" stroke-width="2" filter="url(#shadow)"/>
    <text x="110" y="140" fill="#F59E0B" font-family="sans-serif" font-size="18" font-weight="bold">COMMUNITY OBSTACLE REPORTING &amp; DYNAMIC REROUTING LIFECYCLE</text>
    <text x="110" y="165" fill="#94A3B8" font-family="sans-serif" font-size="13">End-to-End Workflow: Student Submission → Administrative Governance → Real-Time Graph Detour</text>

    <!-- Step 1: User Submission -->
    <rect x="110" y="210" width="210" height="160" rx="8" fill="#162E25" stroke="#F59E0B" stroke-width="1.5"/>
    <circle cx="135" cy="235" r="12" fill="#F59E0B"/>
    <text x="135" y="239" fill="#000" font-family="sans-serif" font-size="10" font-weight="bold" text-anchor="middle">1</text>
    <text x="155" y="239" fill="#FFF" font-family="sans-serif" font-size="13" font-weight="bold">User Submits Report</text>
    
    <text x="125" y="270" fill="#E2E8F0" font-family="sans-serif" font-size="11">• Location: FET_1F_CORRIDOR_E</text>
    <text x="125" y="290" fill="#E2E8F0" font-family="sans-serif" font-size="11">• Hazard: Floor cleaning / spill</text>
    <text x="125" y="310" fill="#E2E8F0" font-family="sans-serif" font-size="11">• Severity: Medium (slippery)</text>
    <text x="125" y="330" fill="#F59E0B" font-family="sans-serif" font-size="11">• Initial Status: 'pending'</text>
    <text x="125" y="350" fill="#94A3B8" font-family="sans-serif" font-size="10">Saved to SQLite obstacles table</text>

    <!-- Arrow 1 to 2 -->
    <line x1="320" y1="290" x2="370" y2="290" stroke="#F59E0B" stroke-width="2"/>

    <!-- Step 2: Governance & Review -->
    <rect x="370" y="210" width="220" height="160" rx="8" fill="#162E25" stroke="#38BDF8" stroke-width="1.5"/>
    <circle cx="395" cy="235" r="12" fill="#38BDF8"/>
    <text x="395" y="239" fill="#000" font-family="sans-serif" font-size="10" font-weight="bold" text-anchor="middle">2</text>
    <text x="415" y="239" fill="#FFF" font-family="sans-serif" font-size="13" font-weight="bold">Admin Governance</text>
    
    <text x="385" y="270" fill="#E2E8F0" font-family="sans-serif" font-size="11">• Admin logs into Console</text>
    <text x="385" y="290" fill="#E2E8F0" font-family="sans-serif" font-size="11">• Reviews pending submissions</text>
    <text x="385" y="310" fill="#E2E8F0" font-family="sans-serif" font-size="11">• Action: Verify or Dismiss</text>
    <text x="385" y="330" fill="#10B981" font-family="sans-serif" font-size="11">• Transition: → 'verified'</text>
    <text x="385" y="350" fill="#94A3B8" font-family="sans-serif" font-size="10">Logged in audit_logs with admin ID</text>

    <!-- Arrow 2 to 3 -->
    <line x1="590" y1="290" x2="640" y2="290" stroke="#10B981" stroke-width="2"/>

    <!-- Step 3: Graph Rerouting -->
    <rect x="640" y="210" width="220" height="160" rx="8" fill="#162E25" stroke="#10B981" stroke-width="1.5"/>
    <circle cx="665" cy="235" r="12" fill="#10B981"/>
    <text x="665" y="239" fill="#000" font-family="sans-serif" font-size="10" font-weight="bold" text-anchor="middle">3</text>
    <text x="685" y="239" fill="#FFF" font-family="sans-serif" font-size="13" font-weight="bold">Dynamic Graph Mutation</text>
    
    <text x="655" y="270" fill="#E2E8F0" font-family="sans-serif" font-size="11">• Routing Engine loads obstacles</text>
    <text x="655" y="290" fill="#E2E8F0" font-family="sans-serif" font-size="11">• Affected edge identified</text>
    <text x="655" y="310" fill="#E2E8F0" font-family="sans-serif" font-size="11">• Severity 'high': edge omitted</text>
    <text x="655" y="330" fill="#E2E8F0" font-family="sans-serif" font-size="11">• Severity 'med': weight + 10km</text>
    <text x="655" y="350" fill="#10B981" font-family="sans-serif" font-size="10">Active routes re-evaluated</text>

    <!-- Arrow 3 to 4 -->
    <line x1="860" y1="290" x2="910" y2="290" stroke="#10B981" stroke-width="2"/>

    <!-- Step 4: User Notification & Detour -->
    <rect x="910" y="210" width="200" height="160" rx="8" fill="#162E25" stroke="#F43F5E" stroke-width="1.5"/>
    <circle cx="935" cy="235" r="12" fill="#F43F5E"/>
    <text x="935" y="239" fill="#000" font-family="sans-serif" font-size="10" font-weight="bold" text-anchor="middle">4</text>
    <text x="955" y="239" fill="#FFF" font-family="sans-serif" font-size="13" font-weight="bold">Live User Detour</text>
    
    <text x="925" y="270" fill="#E2E8F0" font-family="sans-serif" font-size="11">• In-app banner alerts user</text>
    <text x="925" y="290" fill="#E2E8F0" font-family="sans-serif" font-size="11">• 3D digital twin flashes red</text>
    <text x="925" y="310" fill="#E2E8F0" font-family="sans-serif" font-size="11">• Alternative corridor selected</text>
    <text x="925" y="330" fill="#10B981" font-family="sans-serif" font-size="11">• Zero user disruption</text>
    <text x="925" y="350" fill="#94A3B8" font-family="sans-serif" font-size="10">Turn-by-turn recalculated</text>

    <!-- Resolution & Clearance Cycle -->
    <rect x="250" y="420" width="700" height="180" rx="10" fill="#0C1A15" stroke="#255243" stroke-width="1.5"/>
    <text x="280" y="455" fill="#38BDF8" font-family="sans-serif" font-size="15" font-weight="bold">Obstacle Clearance &amp; System Restoration Cycle</text>
    
    <text x="280" y="490" fill="#E2E8F0" font-family="sans-serif" font-size="12">1. Maintenance crew clears the hazard → Admin marks status as 'resolved'.</text>
    <text x="280" y="515" fill="#E2E8F0" font-family="sans-serif" font-size="12">2. Routing engine removes edge penalty on next polling cycle (&lt; 2 seconds).</text>
    <text x="280" y="540" fill="#E2E8F0" font-family="sans-serif" font-size="12">3. Primary shortest path restored automatically in campus navigation graph.</text>
    <text x="280" y="565" fill="#10B981" font-family="sans-serif" font-size="12">4. Complete audit trail stored with timestamps, reporter user, and verifying admin.</text>
    """
    return create_svg_wrapper("06 — Dynamic Obstacle Lifecycle & Rerouting Architecture", w, h, content)

# -------------------------------------------------------------
# Diagram 7: Authentication & RBAC
# -------------------------------------------------------------
def gen_diag_07():
    w, h = 1200, 750
    content = """
    <rect x="80" y="100" width="1040" height="570" rx="12" fill="url(#cardGrad)" stroke="#1E3B32" stroke-width="2" filter="url(#shadow)"/>
    <text x="110" y="140" fill="#A855F7" font-family="sans-serif" font-size="18" font-weight="bold">AUTHENTICATION, BRUTE-FORCE RATE LIMITING &amp; RBAC</text>
    <text x="110" y="165" fill="#94A3B8" font-family="sans-serif" font-size="13">Cryptographic Password Hashing, Progressive Delays &amp; Role-Based Authorization</text>

    <!-- Auth Flow -->
    <rect x="110" y="200" width="360" height="430" rx="8" fill="#162E25" stroke="#255243" stroke-width="1.5"/>
    <text x="130" y="235" fill="#38BDF8" font-family="sans-serif" font-size="15" font-weight="bold">Authentication &amp; Security Pipeline</text>

    <rect x="130" y="255" width="320" height="80" rx="6" fill="#0C1A15" stroke="#38BDF8" stroke-width="1"/>
    <text x="145" y="280" fill="#FFF" font-family="sans-serif" font-size="12" font-weight="bold">1. Input Credentials</text>
    <text x="145" y="305" fill="#94A3B8" font-family="sans-serif" font-size="11">username, plain_password (via HTTPS)</text>
    <text x="145" y="325" fill="#94A3B8" font-family="sans-serif" font-size="11">Sanitization &amp; SQL-injection defense</text>

    <rect x="130" y="350" width="320" height="110" rx="6" fill="#0C1A15" stroke="#A855F7" stroke-width="1"/>
    <text x="145" y="375" fill="#A855F7" font-family="sans-serif" font-size="12" font-weight="bold">2. SHA-256 + Per-User Salt Hash</text>
    <text x="145" y="400" fill="#94A3B8" font-family="monospace" font-size="10">salt = secrets.token_hex(16)</text>
    <text x="145" y="420" fill="#94A3B8" font-family="monospace" font-size="10">hash = hashlib.sha256(pwd + salt)</text>
    <text x="145" y="440" fill="#10B981" font-family="sans-serif" font-size="11">Constant-time string comparison</text>

    <rect x="130" y="475" width="320" height="135" rx="6" fill="#2A0B0B" stroke="#F43F5E" stroke-width="1"/>
    <text x="145" y="500" fill="#F43F5E" font-family="sans-serif" font-size="12" font-weight="bold">3. Brute-Force Rate Limiter</text>
    <text x="145" y="525" fill="#E2E8F0" font-family="sans-serif" font-size="11">• Max 5 consecutive failures</text>
    <text x="145" y="545" fill="#E2E8F0" font-family="sans-serif" font-size="11">• 15-minute temporary lockout</text>
    <text x="145" y="565" fill="#E2E8F0" font-family="sans-serif" font-size="11">• Exponential backoff jitter</text>
    <text x="145" y="585" fill="#94A3B8" font-family="sans-serif" font-size="10">Security audit log generated on lockout</text>

    <!-- Connector -->
    <line x1="470" y1="415" x2="520" y2="415" stroke="#10B981" stroke-width="3"/>

    <!-- RBAC Matrix -->
    <rect x="520" y="200" width="570" height="430" rx="8" fill="#162E25" stroke="#255243" stroke-width="1.5"/>
    <text x="545" y="235" fill="#10B981" font-family="sans-serif" font-size="15" font-weight="bold">Role-Based Access Control (RBAC) Matrix</text>

    <!-- Student Role Card -->
    <rect x="545" y="255" width="520" height="105" rx="6" fill="#0C1A15" stroke="#10B981" stroke-width="1"/>
    <text x="565" y="280" fill="#10B981" font-family="sans-serif" font-size="13" font-weight="bold">STUDENT ROLE (Base Permissions)</text>
    <text x="565" y="305" fill="#E2E8F0" font-family="sans-serif" font-size="11">• Interactive 3D Digital Twin Navigation &amp; Search</text>
    <text x="565" y="325" fill="#E2E8F0" font-family="sans-serif" font-size="11">• Save Favorite Locations &amp; Preferred Routes</text>
    <text x="565" y="345" fill="#E2E8F0" font-family="sans-serif" font-size="11">• Submit New Obstacle Reports (Starts in 'pending' status)</text>

    <!-- Staff Role Card -->
    <rect x="545" y="375" width="520" height="105" rx="6" fill="#0C1A15" stroke="#38BDF8" stroke-width="1"/>
    <text x="565" y="400" fill="#38BDF8" font-family="sans-serif" font-size="13" font-weight="bold">STAFF ROLE (Faculty &amp; Campus Officials)</text>
    <text x="565" y="425" fill="#E2E8F0" font-family="sans-serif" font-size="11">• All Student Permissions Included</text>
    <text x="565" y="445" fill="#E2E8F0" font-family="sans-serif" font-size="11">• Expedited Priority Obstacle Submissions</text>
    <text x="565" y="465" fill="#E2E8F0" font-family="sans-serif" font-size="11">• Departmental Facility Inspection &amp; Occupancy Views</text>

    <!-- Admin Role Card -->
    <rect x="545" y="495" width="520" height="120" rx="6" fill="#0C1A15" stroke="#A855F7" stroke-width="1"/>
    <text x="565" y="520" fill="#A855F7" font-family="sans-serif" font-size="13" font-weight="bold">ADMINISTRATOR ROLE (Full Governance)</text>
    <text x="565" y="545" fill="#E2E8F0" font-family="sans-serif" font-size="11">• All Staff and Student Permissions</text>
    <text x="565" y="565" fill="#E2E8F0" font-family="sans-serif" font-size="11">• Obstacle Review: Verify, Reject, Resolve, or Remove</text>
    <text x="565" y="585" fill="#E2E8F0" font-family="sans-serif" font-size="11">• Security Governance: Unlock Accounts, View Audit Logs, DB Backup</text>
    <text x="565" y="605" fill="#E2E8F0" font-family="sans-serif" font-size="11">• Analytics Telemetry &amp; System Health Monitoring</text>
    """
    return create_svg_wrapper("07 — Security, Password Hashing & RBAC Architecture", w, h, content)

# -------------------------------------------------------------
# Diagram 8: Database Relationships ER
# -------------------------------------------------------------
def gen_diag_08():
    w, h = 1200, 750
    content = """
    <rect x="80" y="100" width="1040" height="570" rx="12" fill="url(#cardGrad)" stroke="#1E3B32" stroke-width="2" filter="url(#shadow)"/>
    <text x="110" y="140" fill="#06B6D4" font-family="sans-serif" font-size="18" font-weight="bold">RELATIONAL DATABASE SCHEMA &amp; ENTITY RELATIONSHIPS (ER)</text>
    <text x="110" y="165" fill="#94A3B8" font-family="sans-serif" font-size="13">SQLite 3 Architecture with WAL Mode, Foreign Keys &amp; PostgreSQL Exporter Compatibility</text>

    <!-- Table 1: users -->
    <rect x="110" y="200" width="220" height="200" rx="6" fill="#162E25" stroke="#06B6D4" stroke-width="1.5"/>
    <rect x="110" y="200" width="220" height="35" rx="6" fill="#0C1A15"/>
    <text x="125" y="224" fill="#06B6D4" font-family="sans-serif" font-size="13" font-weight="bold">users</text>
    <text x="125" y="255" fill="#E2E8F0" font-family="monospace" font-size="11">PK  id INTEGER</text>
    <text x="125" y="275" fill="#E2E8F0" font-family="monospace" font-size="11">    username TEXT (UQ)</text>
    <text x="125" y="295" fill="#E2E8F0" font-family="monospace" font-size="11">    password_hash TEXT</text>
    <text x="125" y="315" fill="#E2E8F0" font-family="monospace" font-size="11">    salt TEXT</text>
    <text x="125" y="335" fill="#E2E8F0" font-family="monospace" font-size="11">    role TEXT</text>
    <text x="125" y="355" fill="#E2E8F0" font-family="monospace" font-size="11">    failed_attempts INT</text>
    <text x="125" y="375" fill="#E2E8F0" font-family="monospace" font-size="11">    locked_until TIMESTAMP</text>

    <!-- Table 2: user_favorites -->
    <rect x="110" y="440" width="220" height="190" rx="6" fill="#162E25" stroke="#10B981" stroke-width="1.5"/>
    <rect x="110" y="440" width="220" height="35" rx="6" fill="#0C1A15"/>
    <text x="125" y="464" fill="#10B981" font-family="sans-serif" font-size="13" font-weight="bold">user_favorites</text>
    <text x="125" y="495" fill="#E2E8F0" font-family="monospace" font-size="11">PK  id INTEGER</text>
    <text x="125" y="515" fill="#38BDF8" font-family="monospace" font-size="11">FK  user_id INTEGER</text>
    <text x="125" y="535" fill="#E2E8F0" font-family="monospace" font-size="11">    origin_id TEXT</text>
    <text x="125" y="555" fill="#E2E8F0" font-family="monospace" font-size="11">    destination_id TEXT</text>
    <text x="125" y="575" fill="#E2E8F0" font-family="monospace" font-size="11">    created_at TIMESTAMP</text>
    <text x="125" y="595" fill="#94A3B8" font-family="sans-serif" font-size="10">REFERENCES users(id)</text>

    <!-- Relationship 1: users to favorites -->
    <line x1="220" y1="400" x2="220" y2="440" stroke="#38BDF8" stroke-width="2"/>
    <text x="230" y="425" fill="#38BDF8" font-family="sans-serif" font-size="10">1 : N</text>

    <!-- Table 3: obstacles -->
    <rect x="420" y="200" width="250" height="230" rx="6" fill="#162E25" stroke="#F59E0B" stroke-width="1.5"/>
    <rect x="420" y="200" width="250" height="35" rx="6" fill="#0C1A15"/>
    <text x="435" y="224" fill="#F59E0B" font-family="sans-serif" font-size="13" font-weight="bold">obstacles</text>
    <text x="435" y="255" fill="#E2E8F0" font-family="monospace" font-size="11">PK  id INTEGER</text>
    <text x="435" y="275" fill="#E2E8F0" font-family="monospace" font-size="11">    location_id TEXT</text>
    <text x="435" y="295" fill="#E2E8F0" font-family="monospace" font-size="11">    description TEXT</text>
    <text x="435" y="315" fill="#E2E8F0" font-family="monospace" font-size="11">    severity TEXT</text>
    <text x="435" y="335" fill="#E2E8F0" font-family="monospace" font-size="11">    status TEXT</text>
    <text x="435" y="355" fill="#E2E8F0" font-family="monospace" font-size="11">    reporter_name TEXT</text>
    <text x="435" y="375" fill="#E2E8F0" font-family="monospace" font-size="11">    reported_at TIMESTAMP</text>
    <text x="435" y="395" fill="#E2E8F0" font-family="monospace" font-size="11">    verified_by TEXT</text>
    <text x="435" y="415" fill="#E2E8F0" font-family="monospace" font-size="11">    verified_at TIMESTAMP</text>

    <!-- Table 4: navigation_logs -->
    <rect x="420" y="460" width="250" height="170" rx="6" fill="#162E25" stroke="#38BDF8" stroke-width="1.5"/>
    <rect x="420" y="460" width="250" height="35" rx="6" fill="#0C1A15"/>
    <text x="435" y="484" fill="#38BDF8" font-family="sans-serif" font-size="13" font-weight="bold">navigation_logs</text>
    <text x="435" y="515" fill="#E2E8F0" font-family="monospace" font-size="11">PK  id INTEGER</text>
    <text x="435" y="535" fill="#E2E8F0" font-family="monospace" font-size="11">    session_id TEXT</text>
    <text x="435" y="555" fill="#E2E8F0" font-family="monospace" font-size="11">    origin TEXT</text>
    <text x="435" y="575" fill="#E2E8F0" font-family="monospace" font-size="11">    destination TEXT</text>
    <text x="435" y="595" fill="#E2E8F0" font-family="monospace" font-size="11">    distance REAL</text>
    <text x="435" y="615" fill="#E2E8F0" font-family="monospace" font-size="11">    timestamp TIMESTAMP</text>

    <!-- Table 5: audit_logs -->
    <rect x="740" y="200" width="350" height="230" rx="6" fill="#162E25" stroke="#A855F7" stroke-width="1.5"/>
    <rect x="740" y="200" width="350" height="35" rx="6" fill="#0C1A15"/>
    <text x="755" y="224" fill="#A855F7" font-family="sans-serif" font-size="13" font-weight="bold">audit_logs</text>
    <text x="755" y="255" fill="#E2E8F0" font-family="monospace" font-size="11">PK  id INTEGER</text>
    <text x="755" y="275" fill="#38BDF8" font-family="monospace" font-size="11">    user_id INTEGER (Optional)</text>
    <text x="755" y="295" fill="#E2E8F0" font-family="monospace" font-size="11">    action TEXT (LOGIN, VERIFY, BACKUP)</text>
    <text x="755" y="315" fill="#E2E8F0" font-family="monospace" font-size="11">    target TEXT (resource identifier)</text>
    <text x="755" y="335" fill="#E2E8F0" font-family="monospace" font-size="11">    details TEXT (JSON metadata)</text>
    <text x="755" y="355" fill="#E2E8F0" font-family="monospace" font-size="11">    timestamp TIMESTAMP</text>
    <text x="755" y="380" fill="#94A3B8" font-family="sans-serif" font-size="10">Immutable tamper-evident security log</text>

    <!-- Architecture Features -->
    <rect x="740" y="460" width="350" height="170" rx="6" fill="#0C1A15" stroke="#255243" stroke-width="1"/>
    <text x="755" y="490" fill="#10B981" font-family="sans-serif" font-size="13" font-weight="bold">Database Engineering Highlights</text>
    <text x="755" y="515" fill="#E2E8F0" font-family="sans-serif" font-size="11">• WAL Mode: Concurrent non-blocking reads/writes</text>
    <text x="755" y="535" fill="#E2E8F0" font-family="sans-serif" font-size="11">• Automated Backups: Timestamped snapshot exporter</text>
    <text x="755" y="555" fill="#E2E8F0" font-family="sans-serif" font-size="11">• Schema Versioning: Dynamic migration tracking</text>
    <text x="755" y="575" fill="#E2E8F0" font-family="sans-serif" font-size="11">• PostgreSQL Bridge: Production DDL &amp; DML exports</text>
    <text x="755" y="595" fill="#E2E8F0" font-family="sans-serif" font-size="11">• Connection Pooling &amp; Safe Context Managers</text>
    """
    return create_svg_wrapper("08 — Relational Database Entity-Relationship Schema", w, h, content)

# -------------------------------------------------------------
# Diagram 9: Navigation Session FSM
# -------------------------------------------------------------
def gen_diag_09():
    w, h = 1200, 750
    content = """
    <rect x="80" y="100" width="1040" height="570" rx="12" fill="url(#cardGrad)" stroke="#1E3B32" stroke-width="2" filter="url(#shadow)"/>
    <text x="110" y="140" fill="#38BDF8" font-family="sans-serif" font-size="18" font-weight="bold">REAL-TIME INDOOR &amp; OUTDOOR WAYFINDING STATE MACHINE (FSM)</text>
    <text x="110" y="165" fill="#94A3B8" font-family="sans-serif" font-size="13">Interactive Step Progression, Floor Transition Modals &amp; Dynamic Detour Handling</text>

    <!-- State 1: IDLE -->
    <rect x="110" y="240" width="180" height="100" rx="8" fill="#162E25" stroke="#38BDF8" stroke-width="2"/>
    <text x="200" y="275" fill="#FFF" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle">1. IDLE STATE</text>
    <text x="200" y="300" fill="#94A3B8" font-family="sans-serif" font-size="11" text-anchor="middle">Origin / Dest selection</text>
    <text x="200" y="318" fill="#94A3B8" font-family="sans-serif" font-size="11" text-anchor="middle">3D Campus Exploration</text>

    <!-- Arrow 1 to 2 -->
    <line x1="290" y1="290" x2="350" y2="290" stroke="#38BDF8" stroke-width="2"/>
    <text x="320" y="280" fill="#38BDF8" font-family="sans-serif" font-size="9" text-anchor="middle">Click Calculate</text>

    <!-- State 2: ROUTE_READY -->
    <rect x="350" y="240" width="190" height="100" rx="8" fill="#162E25" stroke="#10B981" stroke-width="2"/>
    <text x="445" y="275" fill="#FFF" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle">2. ROUTE_READY</text>
    <text x="445" y="300" fill="#10B981" font-family="sans-serif" font-size="11" text-anchor="middle">Path geometry rendered</text>
    <text x="445" y="318" fill="#10B981" font-family="sans-serif" font-size="11" text-anchor="middle">Multi-route comparison</text>

    <!-- Arrow 2 to 3 -->
    <line x1="540" y1="290" x2="600" y2="290" stroke="#10B981" stroke-width="2"/>
    <text x="570" y="280" fill="#10B981" font-family="sans-serif" font-size="9" text-anchor="middle">Start Navigation</text>

    <!-- State 3: ACTIVE_GUIDANCE -->
    <rect x="600" y="240" width="220" height="100" rx="8" fill="#162E25" stroke="#F59E0B" stroke-width="2"/>
    <text x="710" y="275" fill="#FFF" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle">3. ACTIVE_GUIDANCE</text>
    <text x="710" y="300" fill="#F59E0B" font-family="sans-serif" font-size="11" text-anchor="middle">Step index i = 0</text>
    <text x="710" y="318" fill="#F59E0B" font-family="sans-serif" font-size="11" text-anchor="middle">Audio cues + 3D Camera</text>

    <!-- Step Advancement Loop -->
    <path d="M 710 340 L 710 390 L 620 390 L 620 340" fill="none" stroke="#F59E0B" stroke-width="2" stroke-dasharray="3,3"/>
    <text x="665" y="405" fill="#F59E0B" font-family="sans-serif" font-size="10" text-anchor="middle">Next Step: i = i + 1</text>

    <!-- Branch A: Floor Transition Modal -->
    <rect x="350" y="460" width="220" height="100" rx="8" fill="#162E25" stroke="#38BDF8" stroke-width="2"/>
    <text x="460" y="495" fill="#38BDF8" font-family="sans-serif" font-size="13" font-weight="bold" text-anchor="middle">FLOOR TRANSITION</text>
    <text x="460" y="520" fill="#E2E8F0" font-family="sans-serif" font-size="11" text-anchor="middle">Elevator / Stair arrival</text>
    <text x="460" y="538" fill="#94A3B8" font-family="sans-serif" font-size="11" text-anchor="middle">Auto-switches 3D view</text>
    
    <path d="M 660 340 L 660 480 L 570 480" fill="none" stroke="#38BDF8" stroke-width="2"/>
    <path d="M 460 460 L 460 380 L 630 380 L 630 340" fill="none" stroke="#38BDF8" stroke-width="2" stroke-dasharray="3,3"/>

    <!-- Branch B: Obstacle Detour -->
    <rect x="660" y="460" width="220" height="100" rx="8" fill="#162E25" stroke="#F43F5E" stroke-width="2"/>
    <text x="770" y="495" fill="#F43F5E" font-family="sans-serif" font-size="13" font-weight="bold" text-anchor="middle">DYNAMIC DETOUR</text>
    <text x="770" y="520" fill="#E2E8F0" font-family="sans-serif" font-size="11" text-anchor="middle">Obstacle detected ahead</text>
    <text x="770" y="538" fill="#F43F5E" font-family="sans-serif" font-size="11" text-anchor="middle">Dijkstra reroutes path</text>

    <path d="M 760 340 L 760 460" stroke="#F43F5E" stroke-width="2"/>
    <path d="M 880 510 L 920 510 L 920 370 L 780 370 L 780 340" fill="none" stroke="#F43F5E" stroke-width="2" stroke-dasharray="3,3"/>

    <!-- State 4: DESTINATION REACHED -->
    <rect x="890" y="240" width="200" height="100" rx="8" fill="#162E25" stroke="#10B981" stroke-width="2"/>
    <text x="990" y="275" fill="#10B981" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle">4. ARRIVED</text>
    <text x="990" y="300" fill="#E2E8F0" font-family="sans-serif" font-size="11" text-anchor="middle">Destination reached</text>
    <text x="990" y="318" fill="#10B981" font-family="sans-serif" font-size="11" text-anchor="middle">Summary telemetry log</text>

    <line x1="820" y1="290" x2="890" y2="290" stroke="#10B981" stroke-width="2"/>
    <text x="855" y="280" fill="#10B981" font-family="sans-serif" font-size="9" text-anchor="middle">i == target</text>
    """
    return create_svg_wrapper("09 — Wayfinding Finite State Machine (FSM)", w, h, content)

# -------------------------------------------------------------
# Diagram 10: Docker Deployment Architecture
# -------------------------------------------------------------
def gen_diag_010():
    w, h = 1200, 750
    content = """
    <rect x="80" y="100" width="1040" height="570" rx="12" fill="url(#cardGrad)" stroke="#1E3B32" stroke-width="2" filter="url(#shadow)"/>
    <text x="110" y="140" fill="#10B981" font-family="sans-serif" font-size="18" font-weight="bold">DOCKER CONTAINER TOPOLOGY &amp; DEPLOYMENT ARCHITECTURE</text>
    <text x="110" y="165" fill="#94A3B8" font-family="sans-serif" font-size="13">Nginx Reverse Proxy, SSL Termination, Streamlit App Container &amp; Persistent Volumes</text>

    <!-- Client / Browser -->
    <rect x="110" y="240" width="190" height="260" rx="8" fill="#162E25" stroke="#38BDF8" stroke-width="1.5"/>
    <text x="205" y="275" fill="#38BDF8" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle">Client Browsers</text>
    <text x="205" y="300" fill="#94A3B8" font-family="sans-serif" font-size="11" text-anchor="middle">• Desktop Workstations</text>
    <text x="205" y="325" fill="#94A3B8" font-family="sans-serif" font-size="11" text-anchor="middle">• Mobile Handheld Devices</text>
    <text x="205" y="350" fill="#94A3B8" font-family="sans-serif" font-size="11" text-anchor="middle">• Assistive Screen Readers</text>
    <text x="205" y="375" fill="#94A3B8" font-family="sans-serif" font-size="11" text-anchor="middle">• Campus Kiosks</text>

    <rect x="130" y="410" width="150" height="60" rx="6" fill="#0C1A15" stroke="#255243" stroke-width="1"/>
    <text x="205" y="435" fill="#FFF" font-family="sans-serif" font-size="11" text-anchor="middle">HTTPS / WebSocket</text>
    <text x="205" y="455" fill="#10B981" font-family="sans-serif" font-size="11" text-anchor="middle">Port 80 / 443</text>

    <!-- Connector -->
    <line x1="300" y1="370" x2="360" y2="370" stroke="#38BDF8" stroke-width="3"/>

    <!-- Docker Compose Boundary -->
    <rect x="360" y="200" width="730" height="430" rx="10" fill="#0C1A15" stroke="#10B981" stroke-width="2" stroke-dasharray="6,4"/>
    <text x="390" y="230" fill="#10B981" font-family="sans-serif" font-size="13" font-weight="bold">DOCKER COMPOSE ORCHESTRATION NETWORK (campus_net)</text>

    <!-- Nginx Container -->
    <rect x="390" y="250" width="290" height="200" rx="8" fill="#162E25" stroke="#06B6D4" stroke-width="1.5"/>
    <text x="410" y="280" fill="#06B6D4" font-family="sans-serif" font-size="14" font-weight="bold">nginx_reverse_proxy</text>
    <text x="410" y="305" fill="#E2E8F0" font-family="sans-serif" font-size="11">• Inbound SSL / TLS Termination</text>
    <text x="410" y="325" fill="#E2E8F0" font-family="sans-serif" font-size="11">• Gzip &amp; Brotli Compression</text>
    <text x="410" y="345" fill="#E2E8F0" font-family="sans-serif" font-size="11">• Static Asset Caching</text>
    <text x="410" y="365" fill="#E2E8F0" font-family="sans-serif" font-size="11">• Rate Limiting (10 req/sec)</text>
    <text x="410" y="385" fill="#E2E8F0" font-family="sans-serif" font-size="11">• WebSocket Upgrade Proxying</text>
    <text x="410" y="405" fill="#94A3B8" font-family="sans-serif" font-size="10">Proxy target: app:8501</text>

    <!-- App Container -->
    <rect x="740" y="250" width="320" height="200" rx="8" fill="#162E25" stroke="#10B981" stroke-width="1.5"/>
    <text x="760" y="280" fill="#10B981" font-family="sans-serif" font-size="14" font-weight="bold">campus_navigator_app</text>
    <text x="760" y="305" fill="#E2E8F0" font-family="sans-serif" font-size="11">• Streamlit Headless Server (:8501)</text>
    <text x="760" y="325" fill="#E2E8F0" font-family="sans-serif" font-size="11">• Python 3.11/3.14 Runtime</text>
    <text x="760" y="345" fill="#E2E8F0" font-family="sans-serif" font-size="11">• NetworkX Routing Engine</text>
    <text x="760" y="365" fill="#E2E8F0" font-family="sans-serif" font-size="11">• Three.js 3D Campus Assets</text>
    <text x="760" y="385" fill="#E2E8F0" font-family="sans-serif" font-size="11">• Session State Telemetry Engine</text>
    <text x="760" y="405" fill="#94A3B8" font-family="sans-serif" font-size="10">Healthcheck: curl http://localhost:8501/_stcore/health</text>

    <!-- Connector between Nginx and App -->
    <line x1="680" y1="350" x2="740" y2="350" stroke="#10B981" stroke-width="2"/>
    <text x="710" y="340" fill="#10B981" font-family="sans-serif" font-size="9" text-anchor="middle">HTTP :8501</text>

    <!-- Persistent Volume Container -->
    <rect x="520" y="480" width="410" height="120" rx="8" fill="#162E25" stroke="#F59E0B" stroke-width="1.5"/>
    <text x="540" y="510" fill="#F59E0B" font-family="sans-serif" font-size="13" font-weight="bold">Persistent Docker Volume: campus_data_vol</text>
    <text x="540" y="535" fill="#E2E8F0" font-family="sans-serif" font-size="11">• campus_navigation.db (SQLite WAL Mode)</text>
    <text x="540" y="555" fill="#E2E8F0" font-family="sans-serif" font-size="11">• Daily automated backup archives (.db.bak)</text>
    <text x="540" y="575" fill="#E2E8F0" font-family="sans-serif" font-size="11">• Audit logs &amp; user credentials</text>

    <!-- Connector to Volume -->
    <line x1="880" y1="450" x2="880" y2="480" stroke="#F59E0B" stroke-width="2"/>
    """
    return create_svg_wrapper("10 — Production Docker &amp; Reverse Proxy Deployment", w, h, content)

def render_png_card(title, subtitle, filename, width=1200, height=750):
    """Generates a clean raster PNG visual card for presentation & documentation."""
    im = Image.new("RGB", (width, height), color=(11, 21, 18))
    draw = ImageDraw.Draw(im)
    
    # Outer Border
    draw.rectangle([(20, 20), (width - 20, height - 20)], outline=(30, 59, 50), width=2)
    
    # Header Bar
    draw.rectangle([(20, 20), (width - 20, 80)], fill=(12, 26, 21), outline=(30, 59, 50), width=2)
    draw.rectangle([(35, 35), (42, 65)], fill=(16, 185, 129))
    
    # Header Text
    draw.text((55, 38), title, fill=(241, 245, 249))
    draw.text((width - 450, 42), "Accessible Campus Navigator • JAIN University", fill=(100, 116, 139))
    
    # Content Area
    draw.rectangle([(50, 110), (width - 50, height - 70)], fill=(19, 35, 30), outline=(30, 59, 50), width=2)
    draw.text((80, 140), subtitle, fill=(16, 185, 129))
    
    # Three Inner Panels
    panel_w = (width - 180) // 3
    for idx, (p_title, p_desc, col) in enumerate([
        ("Architecture Specifications", "• Verified Graph Topology: 79 Nodes, 106 Edges\n• Routing: Dijkstra & BFS with Min-Heap Optimization\n• Multi-Floor FET Model: Ground to 4th Floor\n• Wheelchair Filtering: 100% Step-Free Paths", (56, 189, 248)),
        ("Engineering Guarantees", "• Subgraph Pruning for Inaccessible Staircases\n• Dynamic Edge Penalty on Verified Obstacles\n• Sub-5ms Route Calculation Benchmark\n• Automated Daily SQLite WAL Mode Backups", (16, 185, 129)),
        ("Academic Validation", "• Student: Rudra Pratap | USN: 25BTRCL214\n• B.Tech AIML Section D | JAIN University\n• 190 Automated Unit & Regression Tests Passed\n• Production Docker & Reverse Proxy Topology", (245, 158, 11))
    ]):
        px = 70 + idx * (panel_w + 20)
        draw.rectangle([(px, 180), (px + panel_w, height - 100)], fill=(22, 46, 37), outline=(37, 82, 67), width=1)
        draw.text((px + 15, 200), p_title, fill=col)
        draw.text((px + 15, 240), p_desc, fill=(226, 232, 240))
        
    # Footer
    draw.text((35, height - 45), "Author: Rudra Pratap (25BTRCL214) | JAIN (Deemed-to-be University)", fill=(100, 116, 139))
    draw.text((width - 320, height - 45), "Phase 26 Architectural Validation", fill=(100, 116, 139))
    
    im.save(filename, "PNG")

def main():
    print(f"Generating 10 architecture diagrams in: {OUTPUT_DIR}")
    generators = [
        ("01_overall_system_architecture", gen_diag_01, "01 — Overall Three-Tier System Architecture"),
        ("02_campus_graph_representation", gen_diag_02, "02 — Campus Graph Topology & Multi-Floor Connectors"),
        ("03_bfs_workflow", gen_diag_03, "03 — Breadth-First Search (BFS) Traversal Workflow"),
        ("04_dijkstra_workflow", gen_diag_04, "04 — Dijkstra's Weighted Routing & Relaxation Flow"),
        ("05_wheelchair_accessible_routing", gen_diag_05, "05 — Wheelchair-Accessible Subgraph Filtering Pipeline"),
        ("06_obstacle_reporting_lifecycle", gen_diag_06, "06 — Dynamic Obstacle Lifecycle & Rerouting Architecture"),
        ("07_authentication_and_rbac", gen_diag_07, "07 — Security, Password Hashing & RBAC Architecture"),
        ("08_database_relationships_er", gen_diag_08, "08 — Relational Database Entity-Relationship Schema"),
        ("09_navigation_session_fsm", gen_diag_09, "09 — Wayfinding Finite State Machine (FSM)"),
        ("10_docker_deployment_architecture", gen_diag_010, "10 — Production Docker & Reverse Proxy Deployment")
    ]
    
    for basename, func, display_title in generators:
        svg_path = os.path.join(OUTPUT_DIR, f"{basename}.svg")
        png_path = os.path.join(OUTPUT_DIR, f"{basename}.png")
        
        # Write SVG
        svg_content = func()
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
            
        # Write PNG companion
        render_png_card(display_title, f"Visual Architecture Blueprint — {basename}", png_path)
        print(f"Generated: {basename}.svg and {basename}.png")

if __name__ == "__main__":
    main()
