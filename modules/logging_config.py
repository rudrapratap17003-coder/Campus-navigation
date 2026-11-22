"""Production Structured Logging Configuration for Accessible Campus Navigator.

Provides:
- Rotating file logging with size and backup count limits.
- Sensitive data filtering to prevent credentials, hashes, and salts in logs.
- Optional JSON formatted log lines for production observability.
- Standardized logger acquisition across modules.
"""

from __future__ import annotations

import json
import logging
import os
import re
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict, Optional

# Patterns and keys to redact
SENSITIVE_KEYS = {
    "password",
    "password_hash",
    "salt",
    "token",
    "secret",
    "api_key",
    "auth_token",
    "session_token",
    "private_key",
}

REDACTION_PATTERNS = [
    (re.compile(r'(["\']?(?:' + '|'.join(SENSITIVE_KEYS) + r')["\']?\s*[:=]\s*["\'])([^"\']+)(["\'])', re.IGNORECASE), r'\1[REDACTED]\3'),
    (re.compile(r'(\b[a-f0-9]{64}\b)', re.IGNORECASE), '[REDACTED_HASH]'),
]


class SensitiveDataFilter(logging.Filter):
    """Filters and redacts sensitive data (passwords, tokens, salts, hashes) from log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = self.redact_text(record.msg)
        elif isinstance(record.msg, dict):
            record.msg = self.redact_dict(record.msg)

        if record.args:
            if isinstance(record.args, dict):
                record.args = self.redact_dict(record.args)
            elif isinstance(record.args, tuple):
                record.args = tuple(
                    self.redact_text(arg) if isinstance(arg, str) else arg
                    for arg in record.args
                )
        return True

    @staticmethod
    def redact_text(text: str) -> str:
        """Scrub sensitive keywords and hexadecimal hashes from string."""
        for pattern, replacement in REDACTION_PATTERNS:
            text = pattern.sub(replacement, text)
        return text

    @classmethod
    def redact_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively scrub sensitive keys from dictionaries."""
        scrubbed = {}
        for k, v in data.items():
            if str(k).lower() in SENSITIVE_KEYS:
                scrubbed[k] = "[REDACTED]"
            elif isinstance(v, dict):
                scrubbed[k] = cls.redact_dict(v)
            elif isinstance(v, str):
                scrubbed[k] = cls.redact_text(v)
            else:
                scrubbed[k] = v
        return scrubbed


class JsonFormatter(logging.Formatter):
    """Structured JSON log formatter for production monitoring."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)


_LOGGING_INITIALIZED = False


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[Path] = None,
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
    json_format: bool = False,
) -> None:
    """Initialize structured logging for application with rotation and redacting.

    Args:
        log_level: Log level string (INFO, DEBUG, WARN, ERROR).
        log_file: Destination path for log file.
        max_bytes: Max size before log file rotates.
        backup_count: Number of rotated backups to keep.
        json_format: If true, formats records as single-line JSON.
    """
    global _LOGGING_INITIALIZED
    if _LOGGING_INITIALIZED:
        return

    # Fallback default values
    level_str = log_level or os.getenv("CAMPUS_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_str, logging.INFO)

    file_path = log_file or Path(os.getenv("CAMPUS_LOG_FILE", "logs/campus_navigator.log"))
    file_path.parent.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger("campus_navigator")
    root_logger.setLevel(level)

    # Avoid duplicate handlers
    if not root_logger.handlers:
        # File handler with rotation
        file_handler = RotatingFileHandler(
            filename=str(file_path),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(level)

        if json_format:
            file_handler.setFormatter(JsonFormatter())
        else:
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s [%(levelname)s] [%(name)s:%(lineno)d]: %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
            )

        file_handler.addFilter(SensitiveDataFilter())
        root_logger.addHandler(file_handler)

        # Console handler for development
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(
            logging.Formatter("[%(levelname)s] %(name)s: %(message)s")
        )
        console_handler.addFilter(SensitiveDataFilter())
        root_logger.addHandler(console_handler)

    _LOGGING_INITIALIZED = True


def get_logger(name: str) -> logging.Logger:
    """Retrieve a child logger under the campus_navigator root namespace.

    Args:
        name: Subsystem or module name (e.g. 'db_manager', 'route_finder').

    Returns:
        Configured logging.Logger instance with sensitive data filter.
    """
    if not _LOGGING_INITIALIZED:
        setup_logging()

    if name.startswith("campus_navigator."):
        logger = logging.getLogger(name)
    else:
        logger = logging.getLogger(f"campus_navigator.{name}")

    return logger
