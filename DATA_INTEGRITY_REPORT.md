# DATA INTEGRITY & GRAPH VALIDATION REPORT
## Accessible Campus Navigator — Spatial Topology, Accessibility & Database Audit

**Audit Date:** 2026-11-25  
**Database Engine:** SQLite (`data/campus_navigation.db`, `schema_version = 3`)  
**Pre-Modification Backup:** `backups/campus_navigation_backup_20261125_173026.db` (`155,648` bytes)

---

## 1. Automated Spatial Graph Topology Validation (`validate_campus_graph`)

Both bundled spatial datasets were validated programmatically after obstacle synchronization via `modules.campus_map.validate_campus_graph()`:

| Metric | JAIN Global Campus & 5-Floor FET (`data/jain_global_campus.json`) | Schematic Benchmark Model (`data/campus_map.json`) |
|---|---:|---:|
| Total Locations (Nodes) | **79** | **15** |
| Total Pathways (Edges) | **106** | **17** |
| Valid Edges | **106** | **17** |
| Invalid Edges | **0** | **0** |
| Duplicate Edges | **0** | **0** |
| Connected Components (All Modes) | **1** | **1** |
| Unreachable Locations (All Modes) | **0** | **0** |
| Wheelchair Connected Components | **1** | **1** |
| Wheelchair Unreachable Locations | **0** | **0** |
| Missing Floor Transitions | **0** | **0** |
| Invalid Accessibility Metadata | **0** | **0** |
| Invalid Pathway Weights | **0** | **0** |
| Unknown Accessibility Edges | **0** | **0** |
| Active Blocked Edges | **0** | **0** |
| Overall Graph Validity (`is_valid`) | **`true`** | **`true`** |

---

## 2. Single-Source Accessibility Analytics (`compute_accessibility_analytics`)

Metrics are computed from `modules/campus_analytics.py` directly backed by `modules/accessibility.py` (`AccessibilityEngine`) after obstacle synchronization:

| Accessibility Metric | JAIN Global Campus (79 / 106) | Benchmark Model (15 / 17) |
|---|---:|---:|
| Accessible Locations | **58** (`73.4%`) | **0** (`0.0%` — location fields unflagged) |
| Inaccessible Locations | **21** | **0** |
| Unknown Accessibility Locations | **0** | **15** |
| Step-Free Pathways | **88** (`83.0%`) | **16** (`94.1%`) |
| Staircase Pathways | **18** | **1** |
| Elevator Pathways | **4** | **1** |
| Ramp Pathways | **3** | **3** |
| Average Pathway Score | **85.4 / 100** | **95.0 / 100** |
| Classification: `Fully Accessible` | **87** | **16** |
| Classification: `Accessible with Assistance` | **1** | **0** |
| Classification: `Not Wheelchair Accessible` | **18** | **1** |
| Classification: `Temporarily Blocked` | **0** | **0** |
| Classification: `Unknown Accessibility` | **0** | **0** |
| Populated Attributes Percentage | **100.0%** | **0.0%** (node-level metadata audit) |
| Schema Attribute Gaps (`information_gaps_count`) | **0** | **15** (`LOC_01` .. `LOC_15`) |

---

## 3. Data Provenance & Physical Verification Transparency

To prevent misleading UI contradictions between schema completeness and real-world survey confirmation:
- **JAIN Digital Twin Node Verification Provenance:** `1 VERIFIED` node and `78 IMAGE_DERIVED` nodes (`1.3%` physically surveyed coverage).
- **JAIN Digital Twin Edge Verification Provenance:** `16 APPROXIMATE` outdoor edges and `90 IMAGE_DERIVED` indoor edges.
- **Dashboard Reporting Fix:** `pages/dashboard.py` now labels these separately as:
  1. **Physical Verification:** `1.3%` (`1 Physically Audited • 78 Floor-Plan Derived`)
  2. **Attribute Gaps / Audit Queue:** `0 / 78` (`0 Missing Attrs • 78 Pending Physical Survey`)
- **Schematic & Verification Notices:** Non-surveyed 2D floor plans and 3D WebGL Digital Twin volumes carry explicit explanatory notices so evaluators distinguish graph pathfinding topology from CAD/surveyed measurements.

---

## 4. Obstacle Reporting & Database Integrity Snapshot

Inspected via `modules.campus_analytics.compute_obstacle_analytics(obs, jain_map)` against preserved SQLite state:
- **Total Obstacle Reports:** `8`
- **Status Breakdown:** `4 Pending`, `0 Verified`, `4 Resolved`, `0 Rejected`
- **Active Verified Hazards Blocking Graph:** `0` (`All corridors operational`)
- **Severity Breakdown:** `0 Low`, `2 Medium`, `6 High`, `0 Critical`
- **Floor Distribution (JAIN Mapping):** Ground (`0`): `2`, Outdoor (`-1`): `4`, Floors `1–4`: `0` each
- **Cross-Dataset Reports (`unmapped_other_dataset_reports`):** `2` (reports targeting Benchmark Model locations/edges accurately accounted for without silent loss)
- **Authentication Accounts Preserved:** `demo_student`, `demo_staff`, `demo_admin` remain `Inactive` (`REVOKED_` hashes) in `data/campus_navigation.db`, preserving fail-closed security and the Admin Bootstrap Setup Wizard on first admin initialization.
