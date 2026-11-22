#!/usr/bin/env bash
# ==============================================================================
# Accessible Campus Navigator - Production Deployment Automation (POSIX Bash)
# ==============================================================================

set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$APP_DIR"

echo "=================================================================="
echo " Starting Accessible Campus Navigator Deployment"
echo " Directory: $APP_DIR"
echo " Date: $(date)"
echo "=================================================================="

# 1. Verify Prerequisites
if ! command -v docker &> /dev/null; then
    echo "[-] ERROR: docker command could not be found. Please install Docker." >&2
    exit 1
fi

COMPOSE_CMD=""
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    echo "[-] ERROR: docker compose or docker-compose is required." >&2
    exit 1
fi

# 2. Ensure Persistent Directories Exist
echo "[+] Ensuring persistent storage directories exist..."
mkdir -p "$APP_DIR/data" "$APP_DIR/database" "$APP_DIR/backups" "$APP_DIR/logs"

# 3. Create Pre-Deployment Database Backup if DB exists
DB_FILE="$APP_DIR/database/campus.db"
if [ -f "$DB_FILE" ]; then
    BACKUP_FILE="$APP_DIR/backups/campus_backup_$(date +%Y%m%d_%H%M%S).db"
    echo "[+] Creating pre-deployment database backup -> $BACKUP_FILE"
    cp "$DB_FILE" "$BACKUP_FILE"
fi

# 4. Build and Launch Containers
echo "[+] Building and launching containers via $COMPOSE_CMD..."
$COMPOSE_CMD build --pull
$COMPOSE_CMD up -d --remove-orphans

# 5. Health Check Verification
echo "[+] Waiting for application container to become healthy..."
MAX_ATTEMPTS=20
ATTEMPT=0
HEALTH_URL="http://localhost:8501/_stcore/health"

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    ATTEMPT=$((ATTEMPT + 1))
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_URL" || true)
    if [ "$HTTP_STATUS" = "200" ]; then
        echo "[+] Service is HEALTHY (HTTP 200) after $ATTEMPT attempts!"
        break
    fi
    echo "    [Attempt $ATTEMPT/$MAX_ATTEMPTS] Service status: $HTTP_STATUS. Retrying in 3s..."
    sleep 3
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    echo "[-] WARNING: Health check timed out. Please inspect logs via: $COMPOSE_CMD logs" >&2
    exit 1
fi

echo "=================================================================="
echo " Accessible Campus Navigator Deployed Successfully!"
echo " UI Endpoint: http://localhost:8501"
echo " 3D Digital Twin: http://localhost:8501/3d_campus_map"
echo " Analytics Dashboard: http://localhost:8501/dashboard"
echo "=================================================================="
