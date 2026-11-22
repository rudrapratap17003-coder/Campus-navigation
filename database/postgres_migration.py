"""PostgreSQL Migration Framework and DDL Generator for Accessible Campus Navigator.

Provides production migration tools for transitioning from SQLite to PostgreSQL
when enterprise concurrency, row-level locking, and high availability require it.
"""

from __future__ import annotations

import json
from pathlib import Path
import sqlite3
from typing import Any, Dict, List, Optional, Union

POSTGRES_DDL = """-- Accessible Campus Navigator - Production PostgreSQL Schema
-- Generated for PostgreSQL 14+ / Supabase / Google Cloud SQL

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table: users
CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(64) PRIMARY KEY,
    full_name VARCHAR(128) NOT NULL,
    username VARCHAR(64) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    salt VARCHAR(128) NOT NULL,
    role VARCHAR(32) NOT NULL CHECK (role IN ('Student', 'Field Staff', 'Administrator')),
    account_status VARCHAR(16) NOT NULL DEFAULT 'Active' CHECK (account_status IN ('Active', 'Inactive')),
    failed_login_attempts INTEGER NOT NULL DEFAULT 0,
    lockout_until TIMESTAMPTZ NULL,
    last_login_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_pg_users_username ON users (username);
CREATE INDEX IF NOT EXISTS idx_pg_users_role ON users (role);
CREATE INDEX IF NOT EXISTS idx_pg_users_status ON users (account_status);

-- Table: obstacle_reports
CREATE TABLE IF NOT EXISTS obstacle_reports (
    report_id VARCHAR(64) PRIMARY KEY,
    location_id VARCHAR(64),
    source_location_id VARCHAR(64),
    destination_location_id VARCHAR(64),
    target_type VARCHAR(16) NOT NULL CHECK (target_type IN ('location', 'pathway')),
    obstacle_category VARCHAR(64) NOT NULL,
    description TEXT NOT NULL,
    severity VARCHAR(16) NOT NULL CHECK (severity IN ('Low', 'Medium', 'High', 'Critical')),
    reported_at TIMESTAMPTZ NOT NULL,
    reporter_name VARCHAR(128) NOT NULL,
    status VARCHAR(16) NOT NULL CHECK (status IN ('Pending', 'Verified', 'Resolved', 'Rejected')),
    resolution_notes TEXT,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_pg_obstacle_status ON obstacle_reports (status);
CREATE INDEX IF NOT EXISTS idx_pg_obstacle_location ON obstacle_reports (location_id);
CREATE INDEX IF NOT EXISTS idx_pg_obstacle_pathway ON obstacle_reports (source_location_id, destination_location_id);
CREATE INDEX IF NOT EXISTS idx_pg_obstacle_reported_at ON obstacle_reports (reported_at);

-- Table: administrative_audit_log
CREATE TABLE IF NOT EXISTS administrative_audit_log (
    log_id VARCHAR(64) PRIMARY KEY,
    actor_user_id VARCHAR(64) NOT NULL,
    action VARCHAR(64) NOT NULL,
    target_type VARCHAR(32) NOT NULL CHECK (target_type IN ('obstacle_report', 'user_account', 'system')),
    target_id VARCHAR(64) NOT NULL,
    details_json TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    FOREIGN KEY (actor_user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_pg_audit_actor ON administrative_audit_log (actor_user_id);
CREATE INDEX IF NOT EXISTS idx_pg_audit_action ON administrative_audit_log (action);
CREATE INDEX IF NOT EXISTS idx_pg_audit_timestamp ON administrative_audit_log (timestamp);

-- Table: login_rate_limits
CREATE TABLE IF NOT EXISTS login_rate_limits (
    limit_id VARCHAR(64) PRIMARY KEY,
    username VARCHAR(64) NOT NULL,
    attempt_time TIMESTAMPTZ NOT NULL,
    success BOOLEAN NOT NULL,
    ip_address VARCHAR(64)
);

CREATE INDEX IF NOT EXISTS idx_pg_rate_limit_user ON login_rate_limits (username, attempt_time);

-- Table: navigation_history
CREATE TABLE IF NOT EXISTS navigation_history (
    session_id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    origin_id VARCHAR(64) NOT NULL,
    origin_name VARCHAR(128) NOT NULL,
    destination_id VARCHAR(64) NOT NULL,
    destination_name VARCHAR(128) NOT NULL,
    route_mode VARCHAR(32) NOT NULL,
    total_distance_m DOUBLE PRECISION NOT NULL,
    estimated_duration_min DOUBLE PRECISION NOT NULL,
    actual_duration_min DOUBLE PRECISION NULL,
    steps_count INTEGER NOT NULL,
    floors_traversed VARCHAR(64) NOT NULL,
    rerouted_count INTEGER NOT NULL DEFAULT 0,
    completion_status VARCHAR(32) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_pg_nav_history_user ON navigation_history (user_id);
CREATE INDEX IF NOT EXISTS idx_pg_nav_history_status ON navigation_history (completion_status);
CREATE INDEX IF NOT EXISTS idx_pg_nav_history_created ON navigation_history (created_at);
"""


def generate_postgres_ddl() -> str:
    """Return the complete PostgreSQL production DDL script."""
    return POSTGRES_DDL.strip()


def export_sqlite_to_postgres_sql(
    sqlite_db_path: Union[str, Path],
    output_sql_path: Union[str, Path],
) -> int:
    """Export existing SQLite records into a PostgreSQL-compatible SQL insert script.

    Args:
        sqlite_db_path: Path to existing SQLite database file.
        output_sql_path: Path to destination .sql migration file.

    Returns:
        Total number of rows exported across all tables.
    """
    src_conn = sqlite3.connect(str(sqlite_db_path))
    src_conn.row_factory = sqlite3.Row

    tables = ["users", "obstacle_reports", "administrative_audit_log", "login_rate_limits", "navigation_history"]
    total_rows = 0

    lines: List[str] = [
        "-- Accessible Campus Navigator - SQLite Data Migration to PostgreSQL",
        "-- Auto-generated export",
        "BEGIN;",
        "",
    ]

    try:
        for table in tables:
            cursor = src_conn.cursor()
            try:
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
            except sqlite3.OperationalError:
                continue

            if not rows:
                continue

            lines.append(f"-- Data for table: {table}")
            col_names = [d[0] for d in cursor.description]
            cols_clause = ", ".join(col_names)

            for row in rows:
                val_strs = []
                for val in row:
                    if val is None:
                        val_strs.append("NULL")
                    elif isinstance(val, (int, float)):
                        val_strs.append(str(val))
                    elif isinstance(val, bool):
                        val_strs.append("TRUE" if val else "FALSE")
                    else:
                        escaped = str(val).replace("'", "''")
                        val_strs.append(f"'{escaped}'")
                vals_clause = ", ".join(val_strs)
                lines.append(f"INSERT INTO {table} ({cols_clause}) VALUES ({vals_clause}) ON CONFLICT DO NOTHING;")
                total_rows += 1

            lines.append("")

        lines.append("COMMIT;")
        Path(output_sql_path).write_text("\n".join(lines), encoding="utf-8")
        return total_rows
    finally:
        src_conn.close()
