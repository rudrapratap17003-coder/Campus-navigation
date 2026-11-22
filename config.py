"""Production Configuration Management for Accessible Campus Navigator.

Supports Development, Testing, and Production environments with secure defaults,
environment variable overrides, and Streamlit secrets compatibility.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

# Base directories
BASE_DIR: Path = Path(__file__).resolve().parent
DATA_DIR: Path = BASE_DIR / "data"
LOGS_DIR: Path = BASE_DIR / "logs"
DATABASE_DIR: Path = BASE_DIR / "database"

# Ensure runtime directories exist
LOGS_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class DatabaseConfig:
    """Database connection and reliability configuration."""

    db_path: str = field(
        default_factory=lambda: os.getenv(
            "CAMPUS_DB_PATH",
            str(DATABASE_DIR / "campus_navigation.db"),
        )
    )
    timeout_seconds: float = field(
        default_factory=lambda: float(os.getenv("CAMPUS_DB_TIMEOUT", "10.0"))
    )
    busy_timeout_ms: int = field(
        default_factory=lambda: int(os.getenv("CAMPUS_DB_BUSY_TIMEOUT_MS", "5000"))
    )
    journal_mode: str = field(
        default_factory=lambda: os.getenv("CAMPUS_DB_JOURNAL_MODE", "WAL")
    )
    synchronous: str = field(
        default_factory=lambda: os.getenv("CAMPUS_DB_SYNCHRONOUS", "NORMAL")
    )
    foreign_keys: bool = True
    auto_backup_on_startup: bool = field(
        default_factory=lambda: os.getenv("CAMPUS_AUTO_BACKUP", "false").lower() == "true"
    )
    backup_dir: Path = field(default_factory=lambda: BASE_DIR / "backups")


@dataclass
class SecurityConfig:
    """Security, password hashing, and session authentication configuration."""

    password_salt_bytes: int = field(
        default_factory=lambda: int(os.getenv("CAMPUS_SALT_BYTES", "32"))
    )
    pbkdf2_iterations: int = field(
        default_factory=lambda: int(os.getenv("CAMPUS_HASH_ITERATIONS", "600000"))
    )
    min_password_length: int = field(
        default_factory=lambda: int(os.getenv("CAMPUS_MIN_PASSWORD_LEN", "8"))
    )
    require_alpha_num: bool = True
    session_lifetime_hours: int = field(
        default_factory=lambda: int(os.getenv("CAMPUS_SESSION_HOURS", "12"))
    )
    max_login_attempts: int = field(
        default_factory=lambda: int(os.getenv("CAMPUS_MAX_LOGIN_ATTEMPTS", "5"))
    )
    lockout_duration_seconds: int = field(
        default_factory=lambda: int(os.getenv("CAMPUS_LOCKOUT_SECONDS", "300"))
    )


@dataclass
class MapConfig:
    """Campus map dataset and spatial configuration."""

    jain_data_file: Path = field(
        default_factory=lambda: Path(
            os.getenv("CAMPUS_JAIN_DATA_FILE", str(DATA_DIR / "jain_global_campus.json"))
        )
    )
    benchmark_data_file: Path = field(
        default_factory=lambda: Path(
            os.getenv("CAMPUS_BENCHMARK_DATA_FILE", str(DATA_DIR / "campus_data.json"))
        )
    )
    cache_graph_in_memory: bool = True
    enable_3d_engine: bool = True
    default_elevation_scale: float = 1.0


@dataclass
class LoggingConfig:
    """Structured application logging configuration."""

    log_level: str = field(
        default_factory=lambda: os.getenv("CAMPUS_LOG_LEVEL", "INFO").upper()
    )
    log_file: Path = field(default_factory=lambda: LOGS_DIR / "campus_navigator.log")
    max_log_bytes: int = field(
        default_factory=lambda: int(os.getenv("CAMPUS_LOG_MAX_BYTES", str(10 * 1024 * 1024)))
    )
    backup_count: int = field(
        default_factory=lambda: int(os.getenv("CAMPUS_LOG_BACKUP_COUNT", "5"))
    )
    json_format: bool = field(
        default_factory=lambda: os.getenv("CAMPUS_LOG_JSON", "false").lower() == "true"
    )
    redact_sensitive_keys: bool = True


@dataclass
class AppConfig:
    """Root application configuration."""

    app_name: str = "Accessible Campus Navigator"
    app_version: str = "2.1.0"
    environment: str = field(
        default_factory=lambda: os.getenv("CAMPUS_ENV", "development").lower()
    )
    debug: bool = field(
        default_factory=lambda: os.getenv("CAMPUS_DEBUG", "false").lower() == "true"
    )
    server_port: int = field(
        default_factory=lambda: int(os.getenv("CAMPUS_PORT", "8501"))
    )

    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    campus_map: MapConfig = field(default_factory=MapConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"

    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.environment == "testing"


# Singleton configuration instance
_CONFIG_INSTANCE: Optional[AppConfig] = None


def get_config(reload: bool = False) -> AppConfig:
    """Retrieve or initialize global application configuration singleton.

    Args:
        reload: Force re-instantiation from current environment.

    Returns:
        Configured AppConfig instance.
    """
    global _CONFIG_INSTANCE
    if _CONFIG_INSTANCE is None or reload:
        _CONFIG_INSTANCE = AppConfig()
    return _CONFIG_INSTANCE
