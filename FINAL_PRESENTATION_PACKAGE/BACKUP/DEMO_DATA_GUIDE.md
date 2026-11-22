# DEMONSTRATION DATA GUIDE & SEED SPECIFICATIONS

**Project:** Accessible Campus Navigator — JAIN Global Campus  
**Presenter:** Rudra Pratap (USN: `25BTRCL214`)  
**Department:** Artificial Intelligence and Machine Learning  
**Target Environment:** Academic Demonstration, Committee Evaluation & Viva Voce  

---

## 1. Safe Demonstration Data Philosophy

To protect system integrity and comply with security rules:
- No real student passwords or private contact numbers are stored in demonstration datasets.
- Demonstration obstacle records are clearly tagged with descriptive, non-destructive titles (e.g., `Demo Maintenance Barrier`, `Temporary Water Leakage`).
- All sample records are completely removable using automated cleanup scripts without affecting base campus topology or core user accounts.

---

## 2. Sample Demonstration Personas & Records

### 2.1 Demonstration Roles & Credentials
| Role | Username | Purpose in Demonstration | Access Permissions |
|---|---|---|---|
| **Administrator** | Created via Admin Bootstrap Wizard on first run (or `admin_presenter`) | Demonstrating user governance, role elevation/demotion, system configuration, and audit logs. | Full access to all pages and administrative operations. |
| **Field Staff** | `staff_demo` | Demonstrating obstacle verification, on-ground inspection, edge severance, and ticket resolution. | Access to Navigation, Obstacle Reports, and Verification workflows. |
| **Student** | `student_demo` (or Guest Mode) | Demonstrating standard journey planning, wheelchair accessibility filters, and submitting new hazard reports. | Read access to routes and maps; submission of pending obstacle reports. |

### 2.2 Recommended Demonstration Waypoints
| Origin Landmark | Destination Landmark | Purpose | Expected Outcome |
|---|---|---|---|
| **Main Entrance Gate** | **FET Auditorium (Ground Floor)** | Outdoor-to-Indoor Journey | Dijkstra yields 420m (7 nodes); BFS yields 465m (6 nodes). Proves weighted algorithm efficiency. |
| **FET Main Foyer (Floor 0)** | **Machine Learning Lab (Floor 2)** | Wheelchair vs Stairs Test | Standard route uses Central Staircase; Wheelchair mode diverts to North Passenger Elevator (Score: 95/100). |
| **Hostel Block A** | **Robotics & AI Research Lab (Floor 2)** | Long Campus Cross-Section | Demonstrates outdoor walkway navigation, entry through West Wing, and vertical elevator transit. |

### 2.3 Demonstration Obstacle Scenarios
- **Scenario 1 (Corridor Water Spill):**
  - Location: `Ground Floor Central Corridor`
  - Severity: `High (Completely Blocked)`
  - Verification: Field Staff verifies → Edge weight becomes $\infty$ → Route reroutes through South Corridor.
- **Scenario 2 (Elevator Maintenance):**
  - Location: `FET South Elevator`
  - Severity: `High`
  - Verification: Field staff verifies → Wheelchair routes dynamically switch to North Elevator.

---

## 3. Automated Demonstration Data Cleanup Script
To reset the demonstration database to pristine baseline after evaluation:
```powershell
& ".venv\Scripts\python.exe" -c "
from database.db_manager import DatabaseManager
db = DatabaseManager()
with db.get_connection() as conn:
    conn.execute(\"DELETE FROM obstacle_reports WHERE title LIKE '%Demo%' OR title LIKE '%Test%'\")
    conn.commit()
print('Demonstration records cleared successfully.')
"
```
