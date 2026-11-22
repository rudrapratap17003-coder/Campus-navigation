# PHASE 31 — PUBLIC HOSTING PLATFORM EVALUATION & DECISION
## Accessible Campus Navigator — JAIN Global Campus (Faculty of Engineering and Technology)

**Project:** Accessible Campus Navigator  
**Institution:** JAIN (Deemed-to-be University)  
**Lead Developer:** Rudra Pratap (USN: 25BTRCL214)  
**Repository:** `https://github.com/rudrapratap17003-coder/Campus-navigation`  
**Milestone:** Phase 31 — Public Cloud Deployment & External Validation  
**Date:** November 2026  
**Status:** **EVALUATION COMPLETE — PRIMARY CANDIDATE SELECTED**

---

## 1. EVALUATION OBJECTIVES

Phase 31 requires establishing a publicly accessible demonstration environment with valid HTTPS so students, examiners, and visitors can access Accessible Campus Navigator from external devices.

This evaluation assesses five hosting alternatives against real application constraints:
1. Long-running Python runtime and Streamlit WebSocket connections.
2. Three.js WebGL 3D digital twin asset delivery.
3. Database persistence (SQLite durability vs PostgreSQL migration).
4. Automated SSL/TLS certificate lifecycle.
5. Operating costs and free-tier limitations.

---

## 2. HOSTING PLATFORM COMPARATIVE MATRIX

```
====================================================================================================
                                DETAILED HOSTING COMPARISON MATRIX
====================================================================================================
Platform                Free Tier           Persistence         WebSockets   HTTPS   Cost / Month
----------------------------------------------------------------------------------------------------
Streamlit Cloud         Free (Unlimited)    Ephemeral (Reboots) Native       Auto    $0.00
Render Web Service      750 hrs/month       Paid Disk Only      Supported    Auto    $0 - $7/month
Railway PaaS            $5 Trial Credit     Volume Mounts       Supported    Auto    $5 - $10/month
University Cloud Server Institutional       Full SAN / Volume   Full Proxy   Custom  University Infra
Cloud VPS (Docker+Nginx) No Free Tier       100% Host Storage   Nginx Proxy  Certbot $4 - $6/month
====================================================================================================
```

---

## 3. IN-DEPTH PLATFORM ASSESSMENTS

### 1. Streamlit Community Cloud (`share.streamlit.io`)
- **Compatibility:** Excellent. Built natively for Streamlit applications; automatically detects `requirements.txt`, executes on Python 3.10–3.12, and terminates SSL/TLS with automatic certificate renewal.
- **WebSocket Routing:** Native low-latency support for Streamlit's real-time component stream (`/_stcore/stream`).
- **Persistence Limitation:** The container filesystem is ephemeral. Local SQLite database writes do not persist across app reboots or version rebuilds. To maintain persistent data on Streamlit Cloud, the application must connect to an external managed database (e.g. Supabase, Neon, or Cloud SQL) using the provided `database/postgres_migration.py` pipeline.
- **Resource Allocations:** 1 GB RAM, 1 Shared vCPU. Ample for concurrent graph pathfinding (< 2ms) and 3D scene payload serialization (< 15ms).
- **Cost:** Free.

### 2. Render (`render.com`)
- **Compatibility:** Native Docker container execution from the repository's `Dockerfile`.
- **Limitation:** The free tier spins down web services after 15 minutes of inactivity, resulting in a 30–50 second cold-start delay for visitors. Persistent disks are only supported on paid tiers.
- **Cost:** Free tier (with spin-down) or \$7.00/month for persistent disk.

### 3. Railway (`railway.app`)
- **Compatibility:** Native Docker support; easy persistent volume attachment for `/app/database`.
- **Limitation:** Railway discontinued its permanent free tier; accounts receive a \$5.00 trial credit, after which an active credit card and usage-based subscription are mandatory.
- **Cost:** \$5.00 – \$10.00/month.

### 4. University-Managed Cloud Server (Internal FET Infrastructure)
- **Compatibility:** Ideal for long-term institutional deployment. Runs inside the campus intranet or DMZ, integrating directly with university directory services.
- **Limitation:** Requires formal departmental IP allocation, firewall NAT configuration, and institutional administrative provisioning.
- **Cost:** Covered under university operational infrastructure.

### 5. Dedicated Cloud VPS with Docker & Nginx (AWS Lightsail / DigitalOcean / Hetzner)
- **Compatibility:** 100% architecture match. Executes `docker-compose.yml` and `nginx/nginx.conf` with persistent volume mappings. Local SQLite database has 100% durability across restarts. Zero spin-down delays.
- **Cost:** \$4.00 – \$6.00/month.

---

## 4. FINAL DEPLOYMENT SELECTION & JUSTIFICATION

In accordance with institutional guidelines to **avoid incurring unapproved financial charges** while delivering an accessible public demonstration:

### Primary Candidate: Streamlit Community Cloud
- **Portal:** `https://share.streamlit.io/`
- **Source Repository:** `https://github.com/rudrapratap17003-coder/Campus-navigation`
- **Main Entrypoint:** `main.py`
- **Branch:** `main`
- **Selection Rationale:**
  1. Zero cost: 100% free with unlimited public access.
  2. Native Streamlit WebSocket optimization: Eliminates proxy latency and buffering issues.
  3. Automatic HTTPS: Delivers a validated public SSL certificate (`https://*.streamlit.app`).
  4. Instant Continuous Deployment: Any future commit pushed to `main` automatically builds and redeploys without manual server intervention.
  5. Dual-Configuration Support: Supported via the Phase 31 `config.get_secret()` adapter, which seamlessly reads configuration from `st.secrets`.

---

## 5. CONCLUSION & NEXT STEPS

Streamlit Community Cloud is selected as the primary public deployment platform. Staging proceeds to secrets management and persistence verification.

*Evaluation Certified By:*  
**Rudra Pratap** (USN: 25BTRCL214)  
Lead Software Developer & System Architect  
November 2026
