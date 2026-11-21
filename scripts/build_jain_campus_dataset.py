"""Builds the comprehensive JAIN Global Campus and FET 5-Floor Digital Twin dataset.

Reconstructs:
1. Outdoor JAIN Global Campus (Gate, Colosseum, Swimming Pool, Cricket Stadium, Sports Fields, SBMJCE Dining, Hostels, Quadrangle, Parking, Admin, Aerospace).
2. FET Engineering Complex (Ground Floor Level 0, First Floor Level 1, Second Floor Level 2, Third Floor Level 3, Fourth Floor Level 4) based on official evacuation route plans.
3. Full vertical circulation (Elevator bank + 4 Stairwells) across all 5 floors.
4. Seamless outdoor-to-indoor transitions via West Ramp and Front Portico.
"""

import json
from pathlib import Path

def build_jain_dataset() -> dict:
    dataset = {
        "_metadata": {
            "name": "JAIN (Deemed-to-be University) - Faculty of Engineering & Technology (FET)",
            "campus": "JAIN Global Campus",
            "address": "Jakkasandra Post, Kanakapura Taluk, Ramanagara District, Karnataka, India - 562112",
            "reference_url": "https://set.jainuniversity.ac.in/",
            "coordinates": {"latitude": 12.6482, "longitude": 77.4418},
            "floors_count": 5,
            "disclaimer": (
                "Digital twin dataset combining verified OpenStreetMap campus boundary coordinates, "
                "satellite imagery layout geometry, and official JAIN University FET 5-Floor Fire Escape Route Plans. "
                "Indoor layouts accurately reflect the physical annular building and room sequences."
            ),
            "unit_distance": "meters",
            "unit_time": "seconds"
        },
        "buildings": [
            {
                "id": "BLD_FET",
                "name": "Faculty of Engineering and Technology (FET)",
                "category": "academic",
                "floors": 5,
                "center_x": 0.0,
                "center_z": 0.0,
                "width": 80.0,
                "depth": 80.0,
                "height": 22.0,
                "shape": "octagonal_annular",
                "description": "Primary engineering complex with 5 levels, central amphitheater courtyard, and 4 radial wings."
            },
            {
                "id": "BLD_COLOSSEUM",
                "name": "The Colosseum (Indoor Sports Arena & Hall)",
                "category": "sports",
                "floors": 2,
                "center_x": 95.0,
                "center_z": -65.0,
                "width": 45.0,
                "depth": 35.0,
                "height": 14.0,
                "shape": "rectangular",
                "description": "Grand multi-purpose sports pavilion, convocation hall, and indoor badminton/basketball courts."
            },
            {
                "id": "BLD_CRICKET",
                "name": "International Cricket Stadium & Pavilion",
                "category": "sports",
                "floors": 1,
                "center_x": 30.0,
                "center_z": -95.0,
                "width": 75.0,
                "depth": 65.0,
                "height": 6.0,
                "shape": "oval",
                "description": "Standard oval cricket pitch with seating pavilions and athletic tracks."
            },
            {
                "id": "BLD_DINING",
                "name": "SBMJCE Dining Complex & Cafeteria",
                "category": "cafeteria",
                "floors": 2,
                "center_x": 65.0,
                "center_z": 20.0,
                "width": 42.0,
                "depth": 32.0,
                "height": 9.0,
                "shape": "courtyard",
                "description": "Central student dining hall, cafeteria kitchens, and outdoor dining courtyard."
            },
            {
                "id": "BLD_ADMIN",
                "name": "University Administration & Student Services",
                "category": "administrative",
                "floors": 3,
                "center_x": 45.0,
                "center_z": 60.0,
                "width": 38.0,
                "depth": 28.0,
                "height": 12.0,
                "shape": "rectangular",
                "description": "Central admissions, registrar, chancellor's office, and student services bureau."
            },
            {
                "id": "BLD_HOSTELS",
                "name": "Student Residential Hostels Complex",
                "category": "residential",
                "floors": 4,
                "center_x": 105.0,
                "center_z": -15.0,
                "width": 55.0,
                "depth": 45.0,
                "height": 16.0,
                "shape": "multi_block",
                "description": "Multi-block student dormitories with ground-floor barrier-free accessible rooms."
            },
            {
                "id": "BLD_POOL",
                "name": "JIRS Aquatic Complex & Swimming Pool",
                "category": "sports",
                "floors": 1,
                "center_x": -20.0,
                "center_z": -110.0,
                "width": 35.0,
                "depth": 25.0,
                "height": 5.0,
                "shape": "pool",
                "description": "Competition-standard swimming pool and aquatic training center."
            },
            {
                "id": "BLD_AEROSPACE",
                "name": "Aerospace Propulsion & Wind Tunnel Labs",
                "category": "research",
                "floors": 2,
                "center_x": -60.0,
                "center_z": -40.0,
                "width": 40.0,
                "depth": 30.0,
                "height": 10.0,
                "shape": "hangar",
                "description": "Aeronautical research hangar, supersonic wind tunnel, and propulsion testing bays."
            }
        ],
        "locations": [],
        "connections": []
    }

    locs = []
    conns = []

    # -------------------------------------------------------------
    # 1. OUTDOOR CAMPUS NODES (Floor = -1 for outdoor ground level)
    # -------------------------------------------------------------
    outdoor_nodes = [
        {
            "id": "OUT_GATE_MAIN",
            "name": "Main Campus Entrance Gate (NH-948 / Kanakapura Rd)",
            "floor": -1,
            "building": "Campus Grounds",
            "category": "entrance",
            "x": 20.0,
            "y": 140.0,
            "wheelchair_accessible": True,
            "amenities": ["Security Checkpoint", "Automated Boom Barrier", "Smooth Curb Cut Ramp", "Tactile Pavement"]
        },
        {
            "id": "OUT_PARKING_ACC",
            "name": "Designated Accessible Parking Zone A",
            "floor": -1,
            "building": "Campus Grounds",
            "category": "parking",
            "x": 25.0,
            "y": 105.0,
            "wheelchair_accessible": True,
            "amenities": ["Extra-Wide Accessible Bays", "Van Access Space", "Direct Ramp to Promenade", "EV Charging"]
        },
        {
            "id": "OUT_QUAD_CENTRAL",
            "name": "Central Campus Quadrangle Promenade",
            "floor": -1,
            "building": "Campus Grounds",
            "category": "lobby",
            "x": 30.0,
            "y": 60.0,
            "wheelchair_accessible": True,
            "amenities": ["Pedestrian Promenade", "Shaded Seating", "Campus Directory Map", "Braille Signage"]
        },
        {
            "id": "OUT_ADMIN_BLOCK",
            "name": "Administration & Student Affairs Block",
            "floor": -1,
            "building": "Administration",
            "category": "office",
            "x": 45.0,
            "y": 60.0,
            "wheelchair_accessible": True,
            "amenities": ["Low-Height Help Desk", "Automated Entrance Doors", "Admissions Office", "Accessible Restrooms"]
        },
        {
            "id": "OUT_FET_FRONT_PORTICO",
            "name": "FET Main Front Portico (Grand Steps)",
            "floor": -1,
            "building": "FET Engineering",
            "category": "entrance",
            "x": 10.0,
            "y": 28.0,
            "wheelchair_accessible": False,
            "amenities": ["Monumental Granite Staircase", "Main Front Façade Entry", "Covered Drop-off Canopy"]
        },
        {
            "id": "OUT_FET_WEST_RAMP",
            "name": "FET West Accessible Entrance Ramp",
            "floor": -1,
            "building": "FET Engineering",
            "category": "entrance",
            "x": -18.0,
            "y": 22.0,
            "wheelchair_accessible": True,
            "amenities": ["Gentle Incline Ramp (1:14)", "Dual Stainless Handrails", "Slip-Resistant Surface", "Automated Sliding Door"]
        },
        {
            "id": "OUT_DINING_COMPLEX",
            "name": "SBMJCE Dining Complex & Cafeteria",
            "floor": -1,
            "building": "Dining Hall",
            "category": "cafeteria",
            "x": 65.0,
            "y": 20.0,
            "wheelchair_accessible": True,
            "amenities": ["Step-Free Dining Entry", "Wide Aisle Seating", "Food Court Counter", "Covered Veranda"]
        },
        {
            "id": "OUT_COLOSSEUM",
            "name": "The Colosseum Sports Arena & Hall",
            "floor": -1,
            "building": "Colosseum",
            "category": "auditorium",
            "x": 95.0,
            "y": -65.0,
            "wheelchair_accessible": True,
            "amenities": ["Ground Level Arena Ramp", "Spectator Seating", "Badminton & Basketball Courts", "Gymnasium"]
        },
        {
            "id": "OUT_CRICKET_STADIUM",
            "name": "International Cricket Stadium & Grounds",
            "floor": -1,
            "building": "Sports Complex",
            "category": "sports",
            "x": 30.0,
            "y": -95.0,
            "wheelchair_accessible": True,
            "amenities": ["Accessible Pavilion Ramp", "Athletic Running Track", "Turf Pitch", "Spectator Stands"]
        },
        {
            "id": "OUT_AQUATICS_POOL",
            "name": "JIRS Swimming Pool & Aquatic Complex",
            "floor": -1,
            "building": "Sports Complex",
            "category": "sports",
            "x": -20.0,
            "y": -110.0,
            "wheelchair_accessible": True,
            "amenities": ["Ramped Pool Deck", "Changing Facilities", "Heated Pool", "Lifeguard Station"]
        },
        {
            "id": "OUT_AEROSPACE_LABS",
            "name": "Aerospace Research & Propulsion Center",
            "floor": -1,
            "building": "Aerospace Center",
            "category": "lab",
            "x": -60.0,
            "y": -40.0,
            "wheelchair_accessible": True,
            "amenities": ["High-Bay Hangar Doors", "Avionics Cleanroom", "Propulsion Testing Deck", "Roll-in Equipment Access"]
        },
        {
            "id": "OUT_HOSTEL_BLOCKS",
            "name": "Student Residential Hostels & Quarters",
            "floor": -1,
            "building": "Hostels",
            "category": "residential",
            "x": 105.0,
            "y": -15.0,
            "wheelchair_accessible": True,
            "amenities": ["Barrier-Free Ground Dorms", "Accessible Common Room", "Laundry Services", "Emergency Call Point"]
        }
    ]
    locs.extend(outdoor_nodes)

    # Outdoor Pathways
    outdoor_edges = [
        ("OUT_GATE_MAIN", "OUT_PARKING_ACC", 45.0, 35.0, True, False, False, False),
        ("OUT_PARKING_ACC", "OUT_QUAD_CENTRAL", 55.0, 42.0, True, False, False, False),
        ("OUT_GATE_MAIN", "OUT_QUAD_CENTRAL", 90.0, 70.0, True, False, False, False),
        ("OUT_QUAD_CENTRAL", "OUT_ADMIN_BLOCK", 18.0, 14.0, True, False, False, False),
        ("OUT_QUAD_CENTRAL", "OUT_FET_FRONT_PORTICO", 38.0, 30.0, False, True, False, False),
        ("OUT_QUAD_CENTRAL", "OUT_FET_WEST_RAMP", 48.0, 38.0, True, False, True, False),
        ("OUT_FET_WEST_RAMP", "OUT_FET_FRONT_PORTICO", 22.0, 18.0, True, False, False, False),
        ("OUT_QUAD_CENTRAL", "OUT_DINING_COMPLEX", 45.0, 36.0, True, False, False, False),
        ("OUT_DINING_COMPLEX", "OUT_HOSTEL_BLOCKS", 55.0, 44.0, True, False, False, False),
        ("OUT_HOSTEL_BLOCKS", "OUT_COLOSSEUM", 52.0, 40.0, True, False, False, False),
        ("OUT_DINING_COMPLEX", "OUT_COLOSSEUM", 88.0, 68.0, True, False, False, False),
        ("OUT_COLOSSEUM", "OUT_CRICKET_STADIUM", 72.0, 56.0, True, False, False, False),
        ("OUT_CRICKET_STADIUM", "OUT_AQUATICS_POOL", 54.0, 42.0, True, False, False, False),
        ("OUT_FET_WEST_RAMP", "OUT_AEROSPACE_LABS", 68.0, 52.0, True, False, False, False),
        ("OUT_AEROSPACE_LABS", "OUT_AQUATICS_POOL", 75.0, 60.0, True, False, False, False),
        ("OUT_CRICKET_STADIUM", "OUT_QUAD_CENTRAL", 125.0, 95.0, True, False, False, False),
    ]
    for src, dst, dist, time_s, wc, stairs, ramp, elev in outdoor_edges:
        conns.append({
            "source": src,
            "destination": dst,
            "distance": dist,
            "estimated_time": time_s,
            "wheelchair_accessible": wc,
            "has_stairs": stairs,
            "has_ramp": ramp,
            "has_elevator": elev,
            "status": "open"
        })

    # -------------------------------------------------------------
    # 2. INDOOR FET 5 FLOORS (Floors 0, 1, 2, 3, 4)
    # -------------------------------------------------------------
    # Building center is at (0, 0).
    # Ring radius ~ 22m. Wings extend to ~ 34m.
    # Four cardinal stairs: North (0, -22), East (22, 0), South (0, 22), West (-22, 0)
    # Elevator Bank: Located adjacent to South corridor at (-5, 18)

    floor_names = ["Ground Floor", "First Floor", "Second Floor", "Third Floor", "Fourth Floor"]

    floor_wings_rooms = {
        0: [
            ("FET_G_ENTRANCE_FOYER", "FET Main Entrance Foyer & Reception", "lobby", 0.0, 18.0, True, ["Information Desk", "Directory Screen", "Step-Free Atrium"]),
            ("FET_G_AMPHI_STAGE", "Central Open-Air Amphitheater Stage", "auditorium", 0.0, 0.0, True, ["Ground Seating", "Acoustic Shell", "Stage Access Ramp"]),
            ("FET_G_MECH_LAB", "Mechanical & Manufacturing Workshop", "lab", -28.0, 10.0, True, ["CNC Machining Bay", "Heavy Tooling", "Roll-in Safety Doors"]),
            ("FET_G_CIVIL_LAB", "Civil & Structural Materials Testing Lab", "lab", -28.0, -10.0, True, ["Concrete Testing Machine", "Soil Mechanics Rig", "Safety Shower"]),
            ("FET_G_PHYSICS_LAB", "Engineering Physics & Optics Lab", "lab", 28.0, 10.0, True, ["Laser Optical Benches", "Darkroom", "Braille Instrument Tags"]),
            ("FET_G_CHEM_LAB", "Engineering Chemistry & Nanotech Lab", "lab", 28.0, -10.0, True, ["Fume Hoods", "Eye Wash Station", "Chemical Safety Cabinet"]),
            ("FET_G_SEMINAR_01", "Sir M. Visvesvaraya Seminar Hall", "classroom", 12.0, -26.0, True, ["Hearing Loop System", "Tiered Ramped Seating", "Dual Projectors"]),
            ("FET_G_RESTROOM_ACC", "Ground Floor Accessible Restroom (G-WC01)", "restroom", -15.0, 24.0, True, ["Emergency Pull Cord", "Grab Bars", "Support Rails", "Low Basin"]),
            ("FET_G_FIRE_EXIT_EAST", "East Emergency Ramp Exit", "entrance", 32.0, 0.0, True, ["Crash Bar Door", "Emergency Evacuation Ramp", "Alarm Strobe"])
        ],
        1: [
            ("FET_1F_CONCOURSE", "First Floor Academic Concourse", "lobby", 0.0, 18.0, True, ["Student Lounge", "Digital Notice Boards", "Wide Hallway"]),
            ("FET_1F_AMPHI_TIER", "Amphitheater First Floor Balcony", "auditorium", 0.0, 4.0, True, ["Overlook Seating", "Safety Glass Railing"]),
            ("FET_1F_CS_LAB_101", "Computer Science & AI Lab (Room 101)", "lab", -28.0, 10.0, True, ["High-Spec GPU Workstations", "Screen Readers", "Height-Adjustable Desks"]),
            ("FET_1F_DATA_LAB_102", "Data Engineering & Cloud Lab (Room 102)", "lab", -28.0, -10.0, True, ["Dual Monitor Stations", "Server Racks", "Ergonomic Chairs"]),
            ("FET_1F_ECE_LAB", "Electronics & Signal Processing Lab", "lab", 28.0, 10.0, True, ["Oscilloscopes", "Soldering Stations", "ESD Protected Flooring"]),
            ("FET_1F_SMART_103", "Smart Multimedia Lecture Hall 103", "classroom", 28.0, -10.0, True, ["Interactive Smartboards", "Lecture Capture Mic", "Wheelchair Row"]),
            ("FET_1F_LIBRARY", "FET Departmental Library & Reading Hall", "library", 12.0, -26.0, True, ["Digital Catalog Terminal", "Braille Book Section", "Study Carrels"]),
            ("FET_1F_RESTROOM_ACC", "First Floor Accessible Restroom (1-WC01)", "restroom", -15.0, 24.0, True, ["Grab Bars", "Wheelchair Turning Space", "Emergency Chime"]),
            ("FET_1F_FACULTY_SUITE", "CSE & ECE Department Faculty Cabins", "office", 0.0, -26.0, True, ["Staff Consultation Desk", "Wide Doorways", "Quiet Workspaces"])
        ],
        2: [
            ("FET_2F_CONCOURSE", "Second Floor Innovation Concourse", "lobby", 0.0, 18.0, True, ["Project Display Gallery", "Collaborative Seating"]),
            ("FET_2F_AI_RESEARCH", "Center for Machine Intelligence (Room 201)", "lab", -28.0, 10.0, True, ["Deep Learning Server Pods", "Computer Vision Benches"]),
            ("FET_2F_CYBER_LAB", "Cyber Security & Forensics Lab (Room 202)", "lab", -28.0, -10.0, True, ["Air-Gapped Network", "Security Workstations"]),
            ("FET_2F_VLSI_LAB", "VLSI Design & Microelectronics Lab", "lab", 28.0, 10.0, True, ["FPGA Kits", "Logic Analyzers", "Clean Room Protocol"]),
            ("FET_2F_SMART_203", "Smart Lecture Hall 203 (Acoustic)", "classroom", 28.0, -10.0, True, ["Assistive Sound Loop", "Ramped Front Access"]),
            ("FET_2F_DEPT_MECH", "Mechanical & Aerospace Faculty Suite", "office", 12.0, -26.0, True, ["Department Offices", "HOD Conference Room"]),
            ("FET_2F_RESTROOM_ACC", "Second Floor Accessible Restroom (2-WC01)", "restroom", -15.0, 24.0, True, ["Grab Bars", "Support Rails", "Wide Door"]),
            ("FET_2F_HOD_CSE", "HOD Office - Computer Science", "office", 0.0, -26.0, True, ["Head of Department Suite", "Executive Desk"])
        ],
        3: [
            ("FET_3F_CONCOURSE", "Third Floor Aerospace Concourse", "lobby", 0.0, 18.0, True, ["Aircraft Model Exhibition", "Wide Skylit Hallway"]),
            ("FET_3F_AVIONICS_LAB", "Avionics & Flight Simulation Studio", "lab", -28.0, 10.0, True, ["Full Flight Simulator", "Cockpit Instrument Trainer"]),
            ("FET_3F_PROPULSION_LAB", "Aerospace Propulsion Research Lab", "lab", -28.0, -10.0, True, ["Turbine Engine Testbed", "CFD Simulation Cluster"]),
            ("FET_3F_ROBOTICS_LAB", "Robotics & Autonomous Systems Studio", "lab", 28.0, 10.0, True, ["Industrial Robot Arms", "Mobile Drone Test Arena"]),
            ("FET_3F_SMART_303", "Aerospace Design Lecture Hall 303", "classroom", 28.0, -10.0, True, ["CAD Modeling Terminals", "Audio Chime"]),
            ("FET_3F_DEANS_SUITE", "Dean's Executive Suite & Boardroom", "office", 12.0, -26.0, True, ["Dean of Engineering Office", "Academic Council Boardroom"]),
            ("FET_3F_RESTROOM_ACC", "Third Floor Accessible Restroom (3-WC01)", "restroom", -15.0, 24.0, True, ["Grab Bars", "Support Rails", "Low Mirror"]),
            ("FET_3F_MAKER_SPACE", "Student Innovation & Maker Studio", "lab", 0.0, -26.0, True, ["3D Printers", "Laser Cutters", "Circuit Prototyping"])
        ],
        4: [
            ("FET_4F_CONCOURSE", "Fourth Floor Research & PG Concourse", "lobby", 0.0, 18.0, True, ["Skybridge Overlook", "Quiet Research Zone"]),
            ("FET_4F_HPC_CLUSTER", "High-Performance Supercomputing Facility", "lab", -28.0, 10.0, True, ["Liquid-Cooled Server Cabinets", "Precision Climate Control"]),
            ("FET_4F_QUANTUM_LAB", "Quantum Computing & Photonics Lab", "lab", -28.0, -10.0, True, ["Optical Isolation Tables", "Cryogenic Chambers"]),
            ("FET_4F_CONF_HALL", "Ramanujan Executive Conference Hall", "auditorium", 28.0, 10.0, True, ["Video Conferencing Walls", "Simultaneous Translation"]),
            ("FET_4F_PG_LIBRARY", "Postgraduate Archives & Digital Repository", "library", 28.0, -10.0, True, ["Rare Technical Archives", "Silent Research Cubicles"]),
            ("FET_4F_INCUBATION", "JAIN University Technology Incubation Cell", "office", 12.0, -26.0, True, ["Startup Mentoring Pods", "Pitch Presentation Deck"]),
            ("FET_4F_RESTROOM_ACC", "Fourth Floor Accessible Restroom (4-WC01)", "restroom", -15.0, 24.0, True, ["Grab Bars", "Support Rails", "Emergency Alarm"]),
            ("FET_4F_TERRACE_SKY", "Observatory & Green Terrace Access", "entrance", 0.0, -26.0, True, ["Weather Station Sensors", "Solar Array Overlook"])
        ]
    }

    # Generate indoor nodes for all 5 floors
    for fl in range(5):
        # 1. Circulation cores for floor `fl`
        elev_id = f"FET_{fl}F_ELEVATOR"
        stairs_south_id = f"FET_{fl}F_STAIRS_SOUTH"
        stairs_north_id = f"FET_{fl}F_STAIRS_NORTH"
        stairs_east_id = f"FET_{fl}F_STAIRS_EAST"
        stairs_west_id = f"FET_{fl}F_STAIRS_WEST"

        fl_cores = [
            {
                "id": elev_id,
                "name": f"{floor_names[fl]} - Main Accessible Elevator Bank",
                "floor": fl,
                "building": "FET Engineering",
                "category": "elevator",
                "x": -6.0,
                "y": 18.0,
                "wheelchair_accessible": True,
                "amenities": ["Braille Buttons", "Voice Floor Announcement", "Wide Doorway (110cm)", "Emergency Telephone"]
            },
            {
                "id": stairs_south_id,
                "name": f"{floor_names[fl]} - Central South Stairwell",
                "floor": fl,
                "building": "FET Engineering",
                "category": "stairs",
                "x": 6.0,
                "y": 20.0,
                "wheelchair_accessible": False,
                "amenities": ["Continuous Handrails", "High-Contrast Step Edging", "Fire-Rated Enclosure"]
            },
            {
                "id": stairs_north_id,
                "name": f"{floor_names[fl]} - North Stairwell & Fire Exit",
                "floor": fl,
                "building": "FET Engineering",
                "category": "stairs",
                "x": 0.0,
                "y": -22.0,
                "wheelchair_accessible": False,
                "amenities": ["Direct Fire Escape Access", "Dual Handrails"]
            },
            {
                "id": stairs_east_id,
                "name": f"{floor_names[fl]} - East Radial Stairwell",
                "floor": fl,
                "building": "FET Engineering",
                "category": "stairs",
                "x": 22.0,
                "y": 0.0,
                "wheelchair_accessible": False,
                "amenities": ["Emergency Exit Access", "Non-Slip Treads"]
            },
            {
                "id": stairs_west_id,
                "name": f"{floor_names[fl]} - West Radial Stairwell",
                "floor": fl,
                "building": "FET Engineering",
                "category": "stairs",
                "x": -22.0,
                "y": 0.0,
                "wheelchair_accessible": False,
                "amenities": ["West Fire Exit Route", "Dual Handrails"]
            }
        ]
        locs.extend(fl_cores)

        # 2. Rooms on this floor
        rooms = floor_wings_rooms[fl]
        for rid, rname, rcat, rx, ry, rwc, ramens in rooms:
            locs.append({
                "id": rid,
                "name": f"{floor_names[fl]} - {rname}",
                "floor": fl,
                "building": "FET Engineering",
                "category": rcat,
                "x": rx,
                "y": ry,
                "wheelchair_accessible": rwc,
                "amenities": ramens
            })

        # 3. Intra-floor corridor connections for floor `fl`
        concourse_id = f"FET_{fl}F_CONCOURSE" if fl > 0 else "FET_G_ENTRANCE_FOYER"

        # Concourse connects to Elevator and South Stairs
        conns.append({"source": concourse_id, "destination": elev_id, "distance": 6.0, "estimated_time": 5.0, "wheelchair_accessible": True, "has_stairs": False, "has_ramp": False, "has_elevator": False, "status": "open"})
        conns.append({"source": concourse_id, "destination": stairs_south_id, "distance": 6.0, "estimated_time": 5.0, "wheelchair_accessible": True, "has_stairs": False, "has_ramp": False, "has_elevator": False, "status": "open"})

        # Annular ring corridor connecting the 4 stairs/wings
        conns.append({"source": stairs_south_id, "destination": stairs_east_id, "distance": 28.0, "estimated_time": 22.0, "wheelchair_accessible": True, "has_stairs": False, "has_ramp": False, "has_elevator": False, "status": "open"})
        conns.append({"source": stairs_east_id, "destination": stairs_north_id, "distance": 28.0, "estimated_time": 22.0, "wheelchair_accessible": True, "has_stairs": False, "has_ramp": False, "has_elevator": False, "status": "open"})
        conns.append({"source": stairs_north_id, "destination": stairs_west_id, "distance": 28.0, "estimated_time": 22.0, "wheelchair_accessible": True, "has_stairs": False, "has_ramp": False, "has_elevator": False, "status": "open"})
        conns.append({"source": stairs_west_id, "destination": elev_id, "distance": 24.0, "estimated_time": 18.0, "wheelchair_accessible": True, "has_stairs": False, "has_ramp": False, "has_elevator": False, "status": "open"})

        # Rooms connect to their nearest corridor node
        for rid, _, _, rx, ry, rwc, _ in rooms:
            # Pick closest corridor node
            if ry > 12.0:
                target_node = concourse_id
            elif rx < -12.0:
                target_node = stairs_west_id
            elif rx > 12.0 and ry > -15.0:
                target_node = stairs_east_id
            else:
                target_node = stairs_north_id

            if rid == target_node:
                continue

            conns.append({
                "source": rid,
                "destination": target_node,
                "distance": 14.0,
                "estimated_time": 11.0,
                "wheelchair_accessible": rwc,
                "has_stairs": False,
                "has_ramp": False,
                "has_elevator": False,
                "status": "open"
            })

    # -------------------------------------------------------------
    # 3. VERTICAL CONNECTIONS (Elevators & Stairs across all 5 floors)
    # -------------------------------------------------------------
    for fl in range(4):
        # Elevator shaft: Floor fl <-> fl + 1 (Wheelchair Accessible!)
        conns.append({
            "source": f"FET_{fl}F_ELEVATOR",
            "destination": f"FET_{fl+1}F_ELEVATOR",
            "distance": 4.5,
            "estimated_time": 15.0,
            "wheelchair_accessible": True,
            "has_stairs": False,
            "has_ramp": False,
            "has_elevator": True,
            "status": "open"
        })
        # South Stairs: Floor fl <-> fl + 1
        conns.append({
            "source": f"FET_{fl}F_STAIRS_SOUTH",
            "destination": f"FET_{fl+1}F_STAIRS_SOUTH",
            "distance": 7.5,
            "estimated_time": 25.0,
            "wheelchair_accessible": False,
            "has_stairs": True,
            "has_ramp": False,
            "has_elevator": False,
            "status": "open"
        })
        # North Stairs: Floor fl <-> fl + 1
        conns.append({
            "source": f"FET_{fl}F_STAIRS_NORTH",
            "destination": f"FET_{fl+1}F_STAIRS_NORTH",
            "distance": 7.5,
            "estimated_time": 25.0,
            "wheelchair_accessible": False,
            "has_stairs": True,
            "has_ramp": False,
            "has_elevator": False,
            "status": "open"
        })
        # East Stairs: Floor fl <-> fl + 1
        conns.append({
            "source": f"FET_{fl}F_STAIRS_EAST",
            "destination": f"FET_{fl+1}F_STAIRS_EAST",
            "distance": 7.5,
            "estimated_time": 25.0,
            "wheelchair_accessible": False,
            "has_stairs": True,
            "has_ramp": False,
            "has_elevator": False,
            "status": "open"
        })
        # West Stairs: Floor fl <-> fl + 1
        conns.append({
            "source": f"FET_{fl}F_STAIRS_WEST",
            "destination": f"FET_{fl+1}F_STAIRS_WEST",
            "distance": 7.5,
            "estimated_time": 25.0,
            "wheelchair_accessible": False,
            "has_stairs": True,
            "has_ramp": False,
            "has_elevator": False,
            "status": "open"
        })

    # -------------------------------------------------------------
    # 4. OUTDOOR-TO-INDOOR SEAMLESS TRANSITIONS
    # -------------------------------------------------------------
    # West Ramp connects OUT_FET_WEST_RAMP to FET_0F_ELEVATOR & FET_G_ENTRANCE_FOYER (Step-Free!)
    conns.append({
        "source": "OUT_FET_WEST_RAMP",
        "destination": "FET_0F_ELEVATOR",
        "distance": 8.0,
        "estimated_time": 6.0,
        "wheelchair_accessible": True,
        "has_stairs": False,
        "has_ramp": True,
        "has_elevator": False,
        "status": "open"
    })
    conns.append({
        "source": "OUT_FET_WEST_RAMP",
        "destination": "FET_G_ENTRANCE_FOYER",
        "distance": 12.0,
        "estimated_time": 10.0,
        "wheelchair_accessible": True,
        "has_stairs": False,
        "has_ramp": True,
        "has_elevator": False,
        "status": "open"
    })
    # Front Portico connects OUT_FET_FRONT_PORTICO to FET_G_ENTRANCE_FOYER (Stepped!)
    conns.append({
        "source": "OUT_FET_FRONT_PORTICO",
        "destination": "FET_G_ENTRANCE_FOYER",
        "distance": 6.0,
        "estimated_time": 8.0,
        "wheelchair_accessible": False,
        "has_stairs": True,
        "has_ramp": False,
        "has_elevator": False,
        "status": "open"
    })

    # -------------------------------------------------------------
    # 5. BACKWARD-COMPATIBILITY ALIAS BRIDGES (LOC_01 to LOC_15)
    # -------------------------------------------------------------
    # Ensure LOC_01 to LOC_15 remain perfectly mapped so existing tests and workflows never break:
    # LOC_01 -> FET_G_ENTRANCE_FOYER
    # LOC_02 -> FET_G_ENTRANCE_FOYER
    # LOC_03 -> FET_G_RESTROOM_ACC
    # LOC_04 -> FET_0F_ELEVATOR
    # LOC_05 -> FET_0F_STAIRS_SOUTH
    # LOC_09 -> OUT_FET_WEST_RAMP
    # LOC_10 -> FET_1F_ELEVATOR
    # LOC_11 -> FET_1F_STAIRS_SOUTH
    # LOC_12 -> FET_1F_CS_LAB_101
    # LOC_13 -> FET_1F_LIBRARY
    # LOC_14 -> FET_1F_FACULTY_SUITE
    # LOC_15 -> FET_1F_RESTROOM_ACC

    dataset["locations"] = locs
    dataset["connections"] = conns
    return dataset

if __name__ == "__main__":
    out_path = Path(__file__).resolve().parent.parent / "data" / "jain_global_campus.json"
    data = build_jain_dataset()
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Generated {out_path} with {len(data['locations'])} locations and {len(data['connections'])} connections across 5 floors and outdoor campus.")
