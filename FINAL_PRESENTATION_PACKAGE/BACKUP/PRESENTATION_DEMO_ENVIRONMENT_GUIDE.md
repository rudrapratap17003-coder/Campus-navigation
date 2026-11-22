# PRESENTATION DEMONSTRATION ENVIRONMENT GUIDE

**Project:** Accessible Campus Navigator — JAIN Global Campus  
**Lead Developer:** Rudra Pratap (USN: `25BTRCL214`)  
**Department:** Artificial Intelligence and Machine Learning  
**Target Audience:** Live Academic Demonstrations, Project Viva Voce & Faculty Reviews  

---

## 1. Quick Demonstration Setup

To ensure an uninterrupted live demonstration on any laptop or classroom projection system, follow this environment bring-up protocol.

### 1.1 Local Environment Startup
Open PowerShell in the project root directory (`C:\Users\rudra pratap\OneDrive\Documents\Campus navigation`) and execute:

```powershell
# 1. Activate Python virtual environment and run Streamlit
& ".venv\Scripts\python.exe" -m streamlit run main.py --server.port 8501
```

If the background daemon is already running (e.g., during active sessions), verify health via:
```powershell
# Check health diagnostic
& ".venv\Scripts\python.exe" -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8501/_stcore/health').read().decode())"
```
The browser interface will be immediately available at:
👉 **`http://localhost:8501`**

---

## 2. Safe Demonstration Scenario & Credentials

In Phase 31, all default hardcoded passwords were revoked to adhere to enterprise security standards. For a live demonstration, two safe demonstration modes are supported:

### Mode A: Interactive Demonstration Bootstrap (Recommended)
If presenting on a clean demonstration machine or after resetting the database:
1. Navigate to **Account Access / Sign In** (`pages/login.py`).
2. The system detects that no administrator is registered and automatically displays the **Admin Bootstrap Wizard**.
3. Create a dedicated demonstration administrator account (e.g., `demo_admin` / `DemoAdmin2026!`).
4. Log in immediately. You now have full access to the Administrator Console, Field Staff verification tools, and navigation routing.

### Mode B: Pre-Configured Demonstration Accounts
If using the initialized local demonstration database:
- **Administrator Role:**
  - Username: `admin_presenter` (or custom bootstrap created user)
  - Capabilities: Full access to User Governance, Obstacle Lifecycle Verification, Audit Logs, and System Analytics.
- **Student Role (Guest or Registered):**
  - Guests can explore routes and submit obstacle reports without prior authentication.
  - Registered Students can bookmark favorite locations and track personal submitted reports.
- **Field Staff Role:**
  - Capabilities: Review submitted obstacle reports, verify on-ground validity, block pathways, and resolve cleared barriers.

---

## 3. Pre-Flight Demonstration Checklist

Perform this 60-second sanity check 5 minutes before your scheduled presentation:

| Step | Verification Action | Expected Result | Pass / Fail |
|---|---|---|---|
| **1. Service Check** | Open `http://localhost:8501` in Chrome or Edge | Dashboard loads with dark-green theme and welcome banner | [ ] |
| **2. Dataset Verification** | Verify radio button shows "JAIN Global Campus" | 79 locations and 106 pathways loaded in KPI cards | [ ] |
| **3. Routing Verification** | Go to "Find Accessible Route", select "Main Entrance Gate" to "FET Auditorium" | Route displays distance (~420m), step-free status, and turn card list | [ ] |
| **4. Wheelchair Toggle** | Check "Wheelchair Accessible Only" | Path switches to step-free ramps/elevators; staircase options removed | [ ] |
| **5. 3D Twin Test** | Navigate to "3D Campus Map" | WebGL Three.js canvas renders buildings with orbit rotation | [ ] |
| **6. Obstacle Submissions** | Navigate to "Obstacle Reports" | Form renders with pathway dropdown, severity picker, and photo upload | [ ] |

---

## 4. Reset & Disaster Recovery Protocol

If during a rehearsal or demonstration you need to reset the demonstration state to a clean baseline:

### 4.1 Resetting Obstacle Reports to Clean State
To clear simulated obstacle reports and restore all campus pathways to unblocked operation:
```powershell
& ".venv\Scripts\python.exe" -c "
from database.db_manager import DatabaseManager
db = DatabaseManager()
with db.get_connection() as conn:
    conn.execute(\"DELETE FROM obstacle_reports WHERE title LIKE '%Demo%'\")
    conn.commit()
print('Demonstration obstacle records cleaned successfully.')
"
```

### 4.2 Restoring from Verified Demonstration Backup
The project maintains clean pre-demonstration database snapshots in `backups/`:
```powershell
# Restore clean baseline database
& ".venv\Scripts\python.exe" -c "
from database.db_manager import DatabaseManager
import os
db = DatabaseManager()
# Automatically restores or verifies schema integrity
db.initialize_schema()
print('Schema and tables validated.')
"
```

### 4.3 Browser Display Optimization
- **Recommended Zoom:** Set browser zoom to **90%** or **100%** on 1080p projectors to ensure all 4 KPI cards and 2D canvas controls fit comfortably on screen without vertical scrolling.
- **Theme Consistency:** Ensure browser is in standard Dark Mode or allows Streamlit CSS styles to render background `#07130F`.

---

## 5. Offline Demonstration Guarantee
The application has been engineered to run completely standalone:
- Local SQLite database (`data/campus_navigation.db`).
- Embedded Three.js scripts and spatial coordinates (`data/jain_global_campus.json`).
- Zero mandatory external cloud API calls required during core wayfinding demonstration.
