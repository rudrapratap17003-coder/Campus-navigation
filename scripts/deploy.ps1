# ==============================================================================
# Accessible Campus Navigator - Production Deployment Automation (PowerShell)
# ==============================================================================

[CmdletBinding()]
param(
    [switch]$SkipBackup = $false
)

$ErrorActionPreference = "Stop"

$AppDir = Split-Path -Parent $PSScriptRoot
Set-Location $AppDir

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host " Starting Accessible Campus Navigator Deployment (PowerShell)" -ForegroundColor Cyan
Write-Host " Directory: $AppDir" -ForegroundColor Cyan
Write-Host " Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan

# 1. Verify Prerequisites
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "[-] ERROR: docker command could not be found. Please install Docker Desktop."
    exit 1
}

$ComposeCmd = $null
try {
    docker compose version | Out-Null
    $ComposeCmd = "docker compose"
} catch {
    if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
        $ComposeCmd = "docker-compose"
    } else {
        Write-Error "[-] ERROR: docker compose or docker-compose is required."
        exit 1
    }
}

# 2. Ensure Persistent Directories Exist
Write-Host "[+] Ensuring persistent storage directories exist..." -ForegroundColor Green
$Dirs = @("data", "database", "backups", "logs")
foreach ($dir in $Dirs) {
    $fullPath = Join-Path $AppDir $dir
    if (-not (Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
    }
}

# 3. Create Pre-Deployment Database Backup
$DbFile = Join-Path $AppDir "database\campus.db"
if ((Test-Path $DbFile) -and (-not $SkipBackup)) {
    $Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $BackupFile = Join-Path $AppDir "backups\campus_backup_$Timestamp.db"
    Write-Host "[+] Creating pre-deployment database backup -> $BackupFile" -ForegroundColor Green
    Copy-Item -Path $DbFile -Destination $BackupFile -Force
}

# 4. Build and Launch Containers
Write-Host "[+] Building and launching containers via $ComposeCmd..." -ForegroundColor Green
if ($ComposeCmd -eq "docker compose") {
    docker compose build --pull
    docker compose up -d --remove-orphans
} else {
    docker-compose build --pull
    docker-compose up -d --remove-orphans
}

# 5. Health Check Verification
Write-Host "[+] Waiting for application container to become healthy..." -ForegroundColor Green
$MaxAttempts = 20
$Attempt = 0
$HealthUrl = "http://localhost:8501/_stcore/health"
$Healthy = $false

while ($Attempt -lt $MaxAttempts) {
    $Attempt++
    try {
        $Response = Invoke-WebRequest -Uri $HealthUrl -UseBasicParsing -TimeoutSec 3 -ErrorAction SilentlyContinue
        if ($Response.StatusCode -eq 200) {
            Write-Host "[+] Service is HEALTHY (HTTP 200) after $Attempt attempt(s)!" -ForegroundColor Green
            $Healthy = $true
            break
        }
    } catch {
        # Continue retry
    }
    Write-Host "    [Attempt $Attempt/$MaxAttempts] Service waiting... Retrying in 3s." -ForegroundColor Yellow
    Start-Sleep -Seconds 3
}

if (-not $Healthy) {
    Write-Warning "[-] WARNING: Health check timed out. Please inspect logs via: $ComposeCmd logs"
    exit 1
}

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host " Accessible Campus Navigator Deployed Successfully!" -ForegroundColor Green
Write-Host " UI Endpoint: http://localhost:8501" -ForegroundColor Cyan
Write-Host " 3D Digital Twin: http://localhost:8501/3d_campus_map" -ForegroundColor Cyan
Write-Host " Analytics Dashboard: http://localhost:8501/dashboard" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan
