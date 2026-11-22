"""Production Health Monitoring & Diagnostic Service for Accessible Campus Navigator.

Provides structured, unauthenticated-safe health probe results for container orchestrators,
Nginx upstream healthchecks, and DevOps monitoring systems without leaking sensitive credentials.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import sys
import time
from typing import Any, Dict, List, Optional

from config import get_config
from database.db_manager import DatabaseManager
from modules.campus_map import load_campus_map
from modules.jain_digital_twin import load_jain_campus_map


def check_system_health(
    check_database: bool = True,
    check_maps: bool = True,
) -> Dict[str, Any]:
    """Execute a comprehensive, safe health check of all core services.

    Returns a clean JSON-serializable dictionary with status indicators.
    Never exposes internal passwords, connection tokens, or raw paths.

    Args:
        check_database: Whether to test SQLite database connection and latency.
        check_maps: Whether to verify spatial graph topology in memory.

    Returns:
        Structured dictionary with status: "HEALTHY" | "DEGRADED" | "UNHEALTHY".
    """
    cfg = get_config()
    issues: List[str] = []
    checks: Dict[str, Any] = {}

    start_time = time.perf_counter()

    # 1. Database Connectivity Probe
    if check_database:
        db_start = time.perf_counter()
        try:
            db_mgr = DatabaseManager()
            with db_mgr.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1;")
                res = cursor.fetchone()
                if not res or res[0] != 1:
                    issues.append("Database query returned unexpected result.")
                cursor.execute("PRAGMA user_version;")
                v_row = cursor.fetchone()
                schema_version = int(v_row[0]) if v_row else 0

            db_latency_ms = round((time.perf_counter() - db_start) * 1000, 2)
            checks["database"] = {
                "status": "healthy",
                "latency_ms": db_latency_ms,
                "schema_version": schema_version,
            }
        except Exception as exc:
            issues.append(f"Database connection failed: {exc.__class__.__name__}")
            checks["database"] = {
                "status": "unhealthy",
                "error": exc.__class__.__name__,
            }

    # 2. Campus Spatial Graphs Probe
    if check_maps:
        map_start = time.perf_counter()
        try:
            jain_map = load_jain_campus_map()
            jain_nodes = len(jain_map.locations)
            jain_edges = len(jain_map.connections)

            bench_map = load_campus_map()
            bench_nodes = len(bench_map.locations)
            bench_edges = len(bench_map.connections)

            map_latency_ms = round((time.perf_counter() - map_start) * 1000, 2)

            if jain_nodes < 70 or jain_edges < 90:
                issues.append("JAIN spatial graph node/pathway count is lower than expected baseline.")

            checks["spatial_graphs"] = {
                "status": "healthy",
                "latency_ms": map_latency_ms,
                "jain_digital_twin": {
                    "locations_count": jain_nodes,
                    "pathways_count": jain_edges,
                },
                "benchmark_model": {
                    "locations_count": bench_nodes,
                    "pathways_count": bench_edges,
                },
            }
        except Exception as exc:
            issues.append(f"Spatial graph loading failed: {exc.__class__.__name__}")
            checks["spatial_graphs"] = {
                "status": "unhealthy",
                "error": exc.__class__.__name__,
            }

    # 3. Configuration & Environment Checks
    checks["configuration"] = {
        "status": "healthy" if not issues else "degraded",
        "environment": cfg.environment,
        "debug_mode": cfg.debug,
        "port": cfg.server_port,
        "log_level": cfg.logging.log_level,
    }

    # Determine overall status
    if not issues:
        overall_status = "HEALTHY"
    elif any("failed" in i.lower() for i in issues):
        overall_status = "UNHEALTHY"
    else:
        overall_status = "DEGRADED"

    total_latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

    return {
        "status": overall_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_latency_ms": total_latency_ms,
        "app": {
            "name": cfg.app_name,
            "version": cfg.app_version,
            "environment": cfg.environment,
        },
        "system": {
            "python_version": platform.python_version(),
            "os": platform.system(),
        },
        "checks": checks,
        "issues": issues,
    }


def main() -> int:
    """CLI entrypoint for container healthcheck and automated probes."""
    report = check_system_health()
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "HEALTHY" else 1


if __name__ == "__main__":
    sys.exit(main())
