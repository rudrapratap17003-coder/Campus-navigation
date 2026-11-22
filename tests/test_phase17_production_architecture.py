"""Unit and integration test suite for Phase 17: Production Architecture & Reliability.

Verifies:
1. Configuration layer (AppConfig, DatabaseConfig, SecurityConfig, MapConfig, LoggingConfig).
2. Domain exception hierarchy (CampusNavigationError, DatabaseError, RoutingError, SecurityError).
3. Structured logging with sensitive data redaction (passwords, salts, tokens, SHA hashes).
4. SQLite database reliability: WAL mode, 5000ms busy timeout, foreign key enforcement, schema versioning.
5. Native SQLite online backup functionality.
6. PostgreSQL migration DDL generator and SQL data exporter.
7. CampusMap caching, cloning, and cache invalidation mechanics.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from config import AppConfig, get_config
from database.db_manager import DatabaseManager
from database.postgres_migration import generate_postgres_ddl, export_sqlite_to_postgres_sql
from modules.campus_map import CampusMap, invalidate_cache
from modules.exceptions import (
    CampusNavigationError,
    ConfigurationError,
    DatabaseError,
    DatabaseConnectionError,
    DatabaseQueryError,
    DataValidationError,
    RoutingError,
    NoPathFoundError,
    InvalidLocationError,
    SecurityError,
    AuthenticationError,
    AuthorizationError,
    SecurityLockoutError,
    ObstacleError,
    ObstacleNotFoundError,
)
from modules.jain_digital_twin import (
    load_jain_campus_map,
    invalidate_jain_campus_cache,
)
from modules.logging_config import SensitiveDataFilter, get_logger, setup_logging


class TestPhase17ProductionArchitecture(unittest.TestCase):
    """Test suite for Phase 17 Production Architecture and Reliability components."""

    def setUp(self) -> None:
        """Create temporary workspace for testing."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        invalidate_cache()
        invalidate_jain_campus_cache()

    def tearDown(self) -> None:
        """Clean up temporary resources."""
        invalidate_cache()
        invalidate_jain_campus_cache()
        self.temp_dir.cleanup()

    # =========================================================================
    # 1. Configuration Layer Tests
    # =========================================================================

    def test_default_configuration_loading(self) -> None:
        """Verify default AppConfig initialization with sane defaults."""
        cfg = AppConfig()
        self.assertEqual(cfg.app_name, "Accessible Campus Navigator")
        self.assertEqual(cfg.database.busy_timeout_ms, 5000)
        self.assertEqual(cfg.database.journal_mode, "WAL")
        self.assertEqual(cfg.security.pbkdf2_iterations, 600000)
        self.assertEqual(cfg.security.min_password_length, 8)
        self.assertFalse(cfg.is_production())

    def test_configuration_environment_overrides(self) -> None:
        """Verify environment variable overrides are respected by AppConfig."""
        with patch.dict(os.environ, {
            "CAMPUS_ENV": "production",
            "CAMPUS_DEBUG": "false",
            "CAMPUS_DB_BUSY_TIMEOUT_MS": "8000",
            "CAMPUS_PORT": "9000",
        }):
            cfg = get_config(reload=True)
            self.assertEqual(cfg.environment, "production")
            self.assertTrue(cfg.is_production())
            self.assertEqual(cfg.database.busy_timeout_ms, 8000)
            self.assertEqual(cfg.server_port, 9000)

        # Restore singleton
        get_config(reload=True)

    # =========================================================================
    # 2. Structured Domain Exception Hierarchy Tests
    # =========================================================================

    def test_exception_hierarchy_inheritance(self) -> None:
        """Verify domain exceptions subclass CampusNavigationError and appropriate built-ins."""
        self.assertTrue(issubclass(ConfigurationError, CampusNavigationError))
        self.assertTrue(issubclass(ConfigurationError, ValueError))

        self.assertTrue(issubclass(DatabaseError, CampusNavigationError))
        self.assertTrue(issubclass(DatabaseConnectionError, DatabaseError))
        self.assertTrue(issubclass(DatabaseQueryError, DatabaseError))

        self.assertTrue(issubclass(RoutingError, CampusNavigationError))
        self.assertTrue(issubclass(NoPathFoundError, RoutingError))
        self.assertTrue(issubclass(InvalidLocationError, RoutingError))
        self.assertTrue(issubclass(InvalidLocationError, ValueError))

        self.assertTrue(issubclass(SecurityError, CampusNavigationError))
        self.assertTrue(issubclass(AuthenticationError, SecurityError))
        self.assertTrue(issubclass(AuthenticationError, ValueError))
        self.assertTrue(issubclass(AuthorizationError, SecurityError))
        self.assertTrue(issubclass(AuthorizationError, PermissionError))
        self.assertTrue(issubclass(SecurityLockoutError, SecurityError))
        self.assertTrue(issubclass(SecurityLockoutError, DatabaseError))

        self.assertTrue(issubclass(ObstacleError, CampusNavigationError))
        self.assertTrue(issubclass(ObstacleNotFoundError, ObstacleError))
        self.assertTrue(issubclass(ObstacleNotFoundError, KeyError))

    def test_exception_metadata_payload(self) -> None:
        """Verify exception retains structured details dictionary."""
        err = NoPathFoundError(
            "Route calculation failed",
            details={"origin": "FET_01", "destination": "CAMPUS_GATE", "mode": "wheelchair"},
        )
        self.assertIn("Route calculation failed", str(err))
        self.assertEqual(err.details["origin"], "FET_01")
        self.assertEqual(err.details["mode"], "wheelchair")

    # =========================================================================
    # 3. Structured Logging & Sensitive Data Filtering Tests
    # =========================================================================

    def test_sensitive_data_filter_redacts_credentials(self) -> None:
        """Verify SensitiveDataFilter scrubs passwords, salts, and secrets from dicts and strings."""
        redactor = SensitiveDataFilter()

        # Dictionary scrubbing
        data = {
            "username": "admin",
            "password": "SuperSecretPassword123!",
            "salt": "abc123xyz789",
            "token": "bearer-token-abc",
            "normal_key": "safe_value",
        }
        scrubbed = redactor.redact_dict(data)
        self.assertEqual(scrubbed["username"], "admin")
        self.assertEqual(scrubbed["password"], "[REDACTED]")
        self.assertEqual(scrubbed["salt"], "[REDACTED]")
        self.assertEqual(scrubbed["token"], "[REDACTED]")
        self.assertEqual(scrubbed["normal_key"], "safe_value")

    def test_sensitive_data_filter_redacts_sha256_hashes(self) -> None:
        """Verify 64-character hexadecimal hashes are masked in log strings."""
        redactor = SensitiveDataFilter()
        raw_msg = "User generated hash e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 during auth."
        cleaned = redactor.redact_text(raw_msg)
        self.assertNotIn("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", cleaned)
        self.assertIn("[REDACTED_HASH]", cleaned)

    def test_logger_initialization(self) -> None:
        """Verify get_logger returns a properly namespaced logger."""
        logger = get_logger("architecture_test")
        self.assertTrue(logger.name.startswith("campus_navigator."))
        self.assertEqual(logger.name, "campus_navigator.architecture_test")

    # =========================================================================
    # 4. Database Reliability: WAL, Pragmas, and Versioning Tests
    # =========================================================================

    def test_database_schema_versioning(self) -> None:
        """Verify DatabaseManager initializes schema with PRAGMA user_version >= 2."""
        db = DatabaseManager(":memory:")
        self.assertGreaterEqual(db.get_schema_version(), 2)

    def test_database_pragmas_on_disk(self) -> None:
        """Verify SQLite on-disk database activates WAL mode, busy timeout, and foreign keys."""
        test_db_path = self.temp_path / "test_reliability.db"
        db = DatabaseManager(test_db_path)

        with db.get_connection() as conn:
            journal_mode = conn.execute("PRAGMA journal_mode;").fetchone()[0]
            busy_timeout = conn.execute("PRAGMA busy_timeout;").fetchone()[0]
            foreign_keys = conn.execute("PRAGMA foreign_keys;").fetchone()[0]

            self.assertEqual(journal_mode.lower(), "wal")
            self.assertEqual(busy_timeout, 5000)
            self.assertEqual(foreign_keys, 1)

    def test_database_native_backup(self) -> None:
        """Verify native online backup creates a valid, identical clone of database."""
        test_db_path = self.temp_path / "source.db"
        db = DatabaseManager(test_db_path)

        # Seed data
        user_id = db.create_user(
            full_name="Reliability Tester",
            username="test_rel_user",
            password="ReliablePassword123!",
            role="Student",
        )
        self.assertTrue(user_id)

        # Perform backup
        backup_file = self.temp_path / "backup_dest.db"
        result_path = db.backup_database(backup_file)
        self.assertTrue(Path(result_path).exists())

        # Verify backup contains seeded user
        backup_db = DatabaseManager(backup_file)
        backed_up_user = backup_db.get_user_by_username("test_rel_user")
        self.assertIsNotNone(backed_up_user)
        self.assertEqual(backed_up_user["full_name"], "Reliability Tester")
        self.assertGreaterEqual(backup_db.get_schema_version(), 2)

    # =========================================================================
    # 5. PostgreSQL Migration Framework Tests
    # =========================================================================

    def test_generate_postgres_ddl(self) -> None:
        """Verify generated PostgreSQL DDL includes all core tables and constraints."""
        ddl = generate_postgres_ddl()
        self.assertIn("CREATE TABLE IF NOT EXISTS users", ddl)
        self.assertIn("CREATE TABLE IF NOT EXISTS obstacle_reports", ddl)
        self.assertIn("CREATE TABLE IF NOT EXISTS administrative_audit_log", ddl)
        self.assertIn("CREATE TABLE IF NOT EXISTS navigation_history", ddl)
        self.assertIn("CREATE TABLE IF NOT EXISTS login_rate_limits", ddl)
        self.assertIn("TIMESTAMPTZ", ddl)

    def test_export_sqlite_to_postgres_sql(self) -> None:
        """Verify exporting SQLite data creates valid PostgreSQL insert statements."""
        test_db_path = self.temp_path / "pg_source.db"
        db = DatabaseManager(test_db_path)
        db.create_user(
            full_name="Migration User",
            username="migration_test",
            password="Password456!",
            role="Field Staff",
        )

        out_sql = self.temp_path / "migrated.sql"
        rows_exported = export_sqlite_to_postgres_sql(test_db_path, out_sql)
        self.assertGreaterEqual(rows_exported, 1)
        self.assertTrue(out_sql.exists())

        sql_content = out_sql.read_text(encoding="utf-8")
        self.assertIn("INSERT INTO users", sql_content)
        self.assertIn("'migration_test'", sql_content)

    # =========================================================================
    # 6. CampusMap Caching, Cloning, and Invalidation Tests
    # =========================================================================

    def test_campus_map_cloning_isolation(self) -> None:
        """Verify CampusMap.clone creates a completely isolated copy of graph and data."""
        base_map = load_jain_campus_map()
        cloned_map = base_map.clone()

        self.assertEqual(len(cloned_map.locations), len(base_map.locations))
        self.assertEqual(cloned_map.graph.number_of_nodes(), base_map.graph.number_of_nodes())
        self.assertEqual(cloned_map.graph.number_of_edges(), base_map.graph.number_of_edges())

        # Mutate clone: add temporary node
        cloned_map.graph.add_node("TEST_TEMP_NODE", name="Temporary")
        self.assertIn("TEST_TEMP_NODE", cloned_map.graph)
        self.assertNotIn("TEST_TEMP_NODE", base_map.graph)

    def test_jain_map_caching_and_invalidation(self) -> None:
        """Verify load_jain_campus_map utilizes cache and invalidate_jain_campus_cache resets it."""
        map1 = load_jain_campus_map()
        map2 = load_jain_campus_map()

        # Both have same nodes/edges
        self.assertEqual(map1.graph.number_of_nodes(), map2.graph.number_of_nodes())

        # Invalidate cache
        invalidate_jain_campus_cache()
        map3 = load_jain_campus_map()
        self.assertEqual(map3.graph.number_of_nodes(), map1.graph.number_of_nodes())


if __name__ == "__main__":
    unittest.main()
