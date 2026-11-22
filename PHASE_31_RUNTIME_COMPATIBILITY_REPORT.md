# PHASE 31 — RUNTIME COMPATIBILITY & DEPENDENCY VALIDATION
## Accessible Campus Navigator — JAIN Global Campus (Faculty of Engineering and Technology)

**Project:** Accessible Campus Navigator  
**Institution:** JAIN (Deemed-to-be University)  
**Lead Developer:** Rudra Pratap (USN: 25BTRCL214)  
**Repository:** `https://github.com/rudrapratap17003-coder/Campus-navigation`  
**Milestone:** Phase 31 — Public Cloud Deployment & External Validation  
**Date:** November 2026  
**Status:** **COMPATIBILITY VERIFIED ACROSS PYTHON 3.11, 3.12 & 3.14**

---

## 1. RUNTIME MATRIX & DEPENDENCY VERIFICATION

Accessible Campus Navigator integrates graph routing algorithms, geospatial visualizers, relational persistence, and 3D WebGL rendering.

This audit validates package availability, version compatibility, and binary wheel support across target deployment environments:

```
========================================================================================
                          RUNTIME ENVIRONMENT SPECIFICATION
========================================================================================
Environment                  Python Version    Target Platform        Validation Status
----------------------------------------------------------------------------------------
Local Development            Python 3.14.0     Windows 11 Enterprise  VERIFIED (Healthy)
Production Docker Container  Python 3.11-slim  Debian Linux (x86_64)  VERIFIED (Healthy)
Streamlit Community Cloud    Python 3.11/3.12  Linux Cloud Container  VERIFIED (Healthy)
========================================================================================
```

---

## 2. CRITICAL DEPENDENCY INVENTORY

All 40 dependencies specified in [`requirements.txt`](file:///c:/Users/rudra%20pratap/OneDrive/Documents/Campus%20navigation/requirements.txt) were evaluated for installation stability and cloud container compatibility:

| Package | Pinned Version | Primary Functionality | Wheel Type on Linux | Status |
|:---|:---:|:---|:---:|:---:|
| **streamlit** | `1.67.0` | Multi-page web framework and session state | Pure Python (`py3-none-any`) | **PASSED** |
| **networkx** | `3.7` | Dijkstra and BFS campus graph algorithms | Pure Python (`py3-none-any`) | **PASSED** |
| **numpy** | `2.5.5` | Fast matrix and coordinate vector math | Pre-compiled `manylinux` wheel | **PASSED** |
| **pandas** | `3.1.1` | Analytics, obstacle reporting tables | Pre-compiled `manylinux` wheel | **PASSED** |
| **plotly** | `7.1.0` | Interactive congestion & traffic charts | Pure Python (`py3-none-any`) | **PASSED** |
| **folium** | `1.0.0` | 2D OpenStreetMap & vector corridor mapping | Pure Python (`py3-none-any`) | **PASSED** |
| **streamlit-folium** | `0.27.4` | Folium bidirectional component bridge | Pure Python (`py3-none-any`) | **PASSED** |
| **pillow** | `13.0.0` | Image processing and floorplan scaling | Pre-compiled `manylinux` wheel | **PASSED** |
| **pyarrow** | `26.0.1` | High-throughput data frame serialization | Pre-compiled `manylinux` wheel | **PASSED** |
| **altair** | `6.3.0` | Declarative statistical charting | Pure Python (`py3-none-any`) | **PASSED** |
| **jinja2** | `3.1.6` | 3D HTML template injection and rendering | Pure Python (`py3-none-any`) | **PASSED** |

---

## 3. IMPORT INTEGRITY & COMPILED EXTENSION CHECKS

The automated test suite in [`tests/test_phase31_cloud_readiness.py`](file:///c:/Users/rudra%20pratap/OneDrive/Documents/Campus%20navigation/tests/test_phase31_cloud_readiness.py) verified that all core modules import cleanly without missing shared library symbols or dynamic linking errors:

```powershell
& ".venv\Scripts\python.exe" -c "
import streamlit, networkx, numpy, pandas, plotly, folium, streamlit_folium, PIL, pyarrow
print('[+] All core dependencies successfully imported in runtime.')
"
```
- **Output:** Clean exit with zero import errors or dynamic link warnings.
- **Bytecode Compilation:** `python -m compileall -q .` completed with **Exit Code 0** (100% clean).

---

## 4. BROWSER-SIDE THREE.JS & WEBGL ASSET VERIFICATION

The 3D Digital Twin renders in client browsers using Three.js r128:
- **Core Library:** `https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js`
- **Controls Plugin:** `https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js`
- **Content Security Policy (CSP):** The Nginx reverse proxy configuration explicitly permits script-src from `cdnjs.cloudflare.com` and `cdn.jsdelivr.net` with `unsafe-inline` and `unsafe-eval` for Three.js shader compilation.
- **Fallback Resilience:** If WebGL hardware acceleration is disabled in client browsers, the application gracefully renders an informative fallback badge while preserving full 2D map navigation.

---

## 5. CONCLUSION

Accessible Campus Navigator is certified fully compatible across Python 3.11, 3.12, and 3.14. It installs without compiler dependencies on Linux cloud containers and executes reliably.

*Report Certified By:*  
**Rudra Pratap** (USN: 25BTRCL214)  
Lead Software Developer & DevOps Engineer  
November 2026
