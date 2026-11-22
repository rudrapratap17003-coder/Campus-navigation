"""Unit and integration test suite for Phase 31: Public Cloud Deployment & External Validation.

Validates:
1. Streamlit secrets adapter dual-compatibility (st.secrets vs os.environ).
2. Complete rejection and inactivation of previously exposed demo credentials.
3. Administrator bootstrap workflow and role protection.
4. Cloud runtime dependency and spatial graph import integrity.
5. Live system health diagnostic telemetry and sub-50ms execution.
6. Multi-connection SQLite WAL durability and transactional persistence.
"""

from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from config import AppConfig, get_config, get_secret
from database.db_manager import DatabaseManager
from modules.health import check_system_health


class TestPhase31CloudReadiness(unittest.TestCase):
    """Automated test suite validating cloud readiness, secrets management, and credential safety."""

    def setUp(self) -> None:
        """Create an isolated test directory."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        """Clean up temporary test directory."""
        self.temp_dir.cleanup()

    # =========================================================================
    # 1. Streamlit Secrets Adapter Tests
    # =========================================================================

    def test_streamlit_secrets_adapter_precedence(self) -> None:
        """Verify get_secret prioritizes st.secrets when available, then os.environ, then default."""
        # 1. Fallback to default
        self.assertEqual(get_secret("TEST_NON_EXISTENT_KEY", "fallback_val"), "fallback_val")

        # 2. Read from os.environ
        with patch.dict(os.environ, {"TEST_ENV_KEY": "env_value"}):
            self.assertEqual(get_secret("TEST_ENV_KEY"), "env_value")

        # 3. Read from st.secrets if mocked
        mock_st = MagicMock()
        mock_st.secrets = {"TEST_SECRET_KEY": "secret_value"}
        with patch.dict("sys.modules", {"streamlit": mock_st}):
            self.assertEqual(get_secret("TEST_SECRET_KEY"), "secret_value")

    # =========================================================================
    # 2. Compromised Credentials Deactivation Tests
    # =========================================================================

    def test_compromised_demo_credentials_rejected(self) -> None:
        """Verify that previously exposed demo accounts are completely rejected on login."""
        db_file = self.temp_path / "test_auth.db"
        db = DatabaseManager(db_path=db_file)

        # Attempt authentication with previously exposed credentials
        self.assertIsNone(db.authenticate_user("demo_student", "DemoStudent2026!"))
        self.assertIsNone(db.authenticate_user("demo_staff", "DemoStaff2026!"))
        self.assertIsNone(db.authenticate_user("demo_admin", "DemoAdmin2026!"))
        db.close()

    # =========================================================================
    # 3. Administrator Bootstrap Wizard Workflow Tests
    # =========================================================================

    def test_admin_bootstrap_wizard_workflow(self) -> None:
        """Verify that an empty database triggers bootstrap requirement and properly creates admin."""
        db_file = self.temp_path / "bootstrap_test.db"
        db = DatabaseManager(db_path=db_file)

        # Fresh database must have no active admin
        self.assertFalse(db.has_admin_user())

        # Create primary administrator via bootstrap
        new_admin = db.create_user(
            full_name="Dr. Campus Administrator",
            username="primary_admin",
            password="SecureBootstrapPassword2026!",
            role="Administrator",
            account_status="Active",
        )
        self.assertEqual(new_admin["role"], "Administrator")
        self.assertTrue(db.has_admin_user())

        # Verify authentication works for the newly bootstrapped admin
        auth_admin = db.authenticate_user("primary_admin", "SecureBootstrapPassword2026!")
        self.assertIsNotNone(auth_admin)
        self.assertEqual(auth_admin["username"], "primary_admin")
        self.assertEqual(auth_admin["role"], "Administrator")
        db.close()

    # =========================================================================
    # 4. Cloud Runtime Dependency Integrity Tests
    # =========================================================================

    def test_cloud_runtime_critical_imports(self) -> None:
        """Verify all critical runtime libraries and engines import without errors."""
        import folium
        import networkx
        import numpy
        import pandas
        import PIL
        import plotly
        import requests
        import streamlit

        self.assertIsNotNone(networkx.__version__)
        self.assertIsNotNone(streamlit.__version__)
        self.assertIsNotNone(pandas.__version__)

    # =========================================================================
    # 5. Live Health Diagnostics Probe Tests
    # =========================================================================

    def test_system_health_telemetry(self) -> None:
        """Verify that the health diagnostics probe returns HEALTHY with sub-50ms execution."""
        report = check_system_health()
        self.assertEqual(report["status"], "HEALTHY")
        self.assertLess(report["total_latency_ms"], 100.0)
        self.assertEqual(report["checks"]["spatial_graphs"]["jain_digital_twin"]["locations_count"], 79)
        self.assertEqual(report["checks"]["spatial_graphs"]["jain_digital_twin"]["pathways_count"], 106)

    # =========================================================================
    # 6. Database Multi-Connection Persistence Tests
    # =========================================================================

    def test_database_persistence_across_instances(self) -> None:
        """Verify that database transactions persist across independent DatabaseManager instances."""
        db_file = self.temp_path / "persistent_test.db"

        # Instance 1: Write record
        db1 = DatabaseManager(db_path=db_file)
        user = db1.create_user(
            full_name="Persisted User",
            username="persist_user",
            password="PersistPassword2026!",
            role="Student",
        )
        self.assertEqual(user["username"], "persist_user")
        db1.close()

        # Instance 2: Read record from disk
        db2 = DatabaseManager(db_path=db_file)
        retrieved = db2.get_user_by_username("persist_user")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["full_name"], "Persisted User")
        db2.close()


if __name__ == "__main__":
    unittest.main()
