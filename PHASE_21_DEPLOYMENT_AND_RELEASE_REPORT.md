# PHASE 21 — DEPLOYMENT & RELEASE ENGINEERING REPORT

**Project:** Accessible Campus Navigator  
**Campus:** JAIN Global Campus — Faculty of Engineering and Technology (FET)  
**Milestone:** Phase 21: Production Deployment, Containerization & Release Engineering  
**Date:** November 22, 2026  
**Status:** Completed & Validated  

---

## 1. Executive Summary

Phase 21 establishes the enterprise-grade production deployment and release engineering infrastructure for the **Accessible Campus Navigator**. This platform serves the 79-location, 106-pathway 3D Digital Twin and accessibility wayfinding engine for JAIN Global Campus.

To ensure resilience, continuous availability, zero data loss, and seamless operational scaling, Phase 21 delivers:
1. **Hardened Multi-Stage / Slim Containerization (`Dockerfile`)**: Built on `python:3.11-slim` running under a dedicated non-root security principal (`appuser:appgroup`, UID/GID 10001) with native Python healthcheck probing.
2. **Orchestration & Persistence Specification (`docker-compose.yml`)**: Declarative service orchestration isolating application networking (`campus-net`), mounting persistent volumes for database files, backups, logs, and geo-data, configured with `restart: unless-stopped`.
3. **High-Performance Nginx Reverse Proxy (`nginx/nginx.conf`)**: Production reverse proxy configured for full-duplex Streamlit WebSocket synchronization (`/_stcore/stream`), security headers (HSTS, X-Frame-Options, CSP, X-Content-Type-Options), and 25MB body upload buffers.
4. **Cross-Platform Deployment Automation (`scripts/deploy.sh`, `scripts/deploy.ps1`)**: Idempotent POSIX bash and PowerShell deployment automation featuring automated pre-deployment database snapshotting, dependency verification, container pull/build, and iterative healthcheck polling.
5. **Automated Deployment Validation (`tests/test_phase21_deployment.py`)**: 5 new automated tests validating container syntax, compose specs, ignore rules, proxy directives, and script safety.

---

## 2. Containerization Architecture (`Dockerfile`)

### 2.1 Multi-Stage Slim Image
The container image is built from `python:3.11-slim` to minimize attack surface and image footprint while providing essential glibc and Python 3.11 runtimes:

```dockerfile
FROM python:3.11-slim AS base

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*
```

### 2.2 Security Hardening (Non-Root User)
The container strictly enforces non-root execution:
- Creates dedicated user `appuser` (UID 10001) and group `appgroup` (GID 10001).
- Creates persistent directories `/app/data`, `/app/database`, `/app/backups`, and `/app/logs` owned by `appuser`.
- Drops privileges using `USER appuser` prior to runtime initialization.

### 2.3 Native Health Probing
Avoids reliance on external binary utilities for container health monitoring:
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1
```

---

## 3. Persistent Volume & Orchestration Strategy (`docker-compose.yml`)

The production deployment decouples volatile application logic from persistent campus data:

| Host Directory | Container Path | Purpose | Persistence Strategy |
| :--- | :--- | :--- | :--- |
| `./data` | `/app/data` | JSON Graph & GeoJSON Definitions (`jain_global_campus.json`) | Read/Write persistent storage |
| `./database` | `/app/database` | SQLite Primary Database (`campus.db`) | Read/Write WAL-mode database |
| `./backups` | `/app/backups` | Automated Point-in-Time Database Snapshots | Append-only backup archive |
| `./logs` | `/app/logs` | Structured Application & Audit Logs | Append-only log stream |

### Service Configuration
- **Container Name:** `accessible-campus-navigator`
- **Network Isolation:** Dedicated bridge network `campus-net`.
- **Environment Overrides:** Injects `CAMPUS_ENV=production`, `CAMPUS_PORT=8501`, `CAMPUS_DB_JOURNAL_MODE=WAL`, `PYTHONUNBUFFERED=1`.
- **Port Mapping:** Exposes port `8501:8501`.

---

## 4. Reverse Proxy & WebSocket Configuration (`nginx/nginx.conf`)

Streamlit requires full-duplex WebSocket connections for bidirectional state synchronization between the Python backend and browser clients.

### Key Nginx Directives:
```nginx
upstream streamlit_backend {
    server campus-navigator:8501;
    keepalive 32;
}

server {
    listen 80;
    server_name localhost _;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdnjs.cloudflare.com https://cdn.jsdelivr.net data: blob:;" always;

    # WebSocket stream proxying
    location /_stcore/stream {
        proxy_pass http://streamlit_backend/_stcore/stream;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;
    }
}
```

---

## 5. Deployment Automation (`scripts/deploy.sh` & `scripts/deploy.ps1`)

Both POSIX bash and Windows PowerShell deployment scripts follow an idempotent 5-step operational pipeline:
1. **Prerequisite Check**: Verifies `docker` and `docker compose` availability.
2. **Directory Initialization**: Automatically generates `data/`, `database/`, `backups/`, and `logs/`.
3. **Automated Snapshot**: Backs up `campus.db` to `backups/campus_backup_YYYYMMDD_HHMMSS.db` prior to tearing down or replacing containers.
4. **Build & Up**: Builds container images (`--pull`) and boots containers (`--remove-orphans`).
5. **Healthcheck Polling**: Loops up to 20 attempts against `/_stcore/health` until an HTTP 200 response is verified.

---

## 6. Verification and Testing

Automated test module `tests/test_phase21_deployment.py` covers 5 mission-critical deployment assertions:
- `test_dockerfile_structure_and_security`: Verified base image, `appuser`, healthcheck, CMD.
- `test_docker_compose_configuration`: Verified services, ports, volume targets, environment variables.
- `test_dockerignore_coverage`: Verified `.env`, `*.db`, `backups/`, `logs/`, `.git`, `.venv` exclusions.
- `test_nginx_reverse_proxy_configuration`: Verified upstream, WebSocket upgrade headers, security headers.
- `test_deployment_scripts_integrity`: Verified script commands, backup triggers, and healthcheck verification.

All 5 Phase 21 tests passed cleanly.
