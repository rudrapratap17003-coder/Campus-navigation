# FINAL PRESENTATION BACKUP & TROUBLESHOOTING GUIDE

**Project:** Accessible Campus Navigator — JAIN Global Campus  
**Presenter:** Rudra Pratap (USN: `25BTRCL214`)  
**Department:** Artificial Intelligence and Machine Learning  
**Target Environment:** Classroom Projector, Viva Voce Panel, Academic Demo Session  

---

## 1. Classroom Emergency Scenarios & Solutions

| Emergency Scenario | Immediate On-Site Fix | Backup Fallback |
|---|---|---|
| **Internet / WiFi Fails in Presentation Room** | The application runs 100% locally on `localhost:8501`. It requires zero external internet access for routing, database, or 3D digital twin. | Continue demo normally on localhost; no internet required. |
| **Streamlit Server Not Responding** | Open PowerShell and run: `& ".venv\Scripts\python.exe" -m streamlit run main.py --server.port 8501`. | Present offline slides and high-resolution screenshot sequence from `FINAL_PRESENTATION_PACKAGE/SCREENSHOTS/`. |
| **Projector Resolution Crops UI (e.g. 1024x768)** | Press `Ctrl` + `-` in Chrome to zoom out to 80% or 90%. | All cards and KPI blocks reflow automatically to standard responsive breakpoints. |
| **Database File Locked / Busy Error** | SQLite WAL mode automatically releases locks within 5 seconds. If blocked, refresh browser page (`Ctrl` + `F5`). | Execute: `& ".venv\Scripts\python.exe" -c "from database.db_manager import DatabaseManager; DatabaseManager().initialize_schema()"`. |
| **3D Digital Twin Renders Slowly on Projector Laptop** | In `pages/3d_campus_map.py`, click the "Toggle Low Overhead Mode" or use 2D Campus Map instead. | 2D Campus Map provides 100% equivalent spatial routing and floor selection without WebGL overhead. |
| **Evaluators Ask for Code or Test Proof** | Open a terminal and run live: `& ".venv\Scripts\python.exe" -m unittest discover tests -v`. | Shows all 208 passing tests live on terminal in ~52 seconds. |

---

## 2. Fast Recovery Commands Reference

### 2.1 Restarting Streamlit Daemon
```powershell
# Terminate existing hung processes and restart cleanly
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like "*streamlit*"} | Stop-Process -Force
& ".venv\Scripts\python.exe" -m streamlit run main.py --server.headless true --server.port 8501
```

### 2.2 Verifying Server Health
```powershell
& ".venv\Scripts\python.exe" -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8501/_stcore/health').read().decode())"
# Output should be: 200 ok
```

### 2.3 Clearing Demo Obstacles Before Committee
```powershell
& ".venv\Scripts\python.exe" -c "
from database.db_manager import DatabaseManager
db = DatabaseManager()
with db.get_connection() as conn:
    conn.execute(\"DELETE FROM obstacle_reports WHERE title LIKE '%Test%' OR title LIKE '%Demo%'\")
    conn.commit()
print('Cleaned temporary demo obstacle records.')
"
```

---

## 3. Offline Visual Presentation Backup
If hardware failure prevents live application execution:
1. Open `FINAL_ACCESSIBLE_CAMPUS_NAVIGATOR_PRESENTATION.pdf` in Adobe Acrobat or Edge in full-screen presentation mode (`Ctrl` + `L`).
2. Follow the speaking script: `FINAL_PRESENTATION_SPEAKING_SCRIPT.md`.
3. Reference genuine visual evidence from `FINAL_PRESENTATION_PACKAGE/SCREENSHOTS/`.
4. Point to architectural diagrams in `FINAL_PRESENTATION_PACKAGE/DIAGRAMS/`.
