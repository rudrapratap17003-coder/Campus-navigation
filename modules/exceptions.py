"""Domain-specific structured exceptions for Accessible Campus Navigator.

Provides a unified error hierarchy for database, authentication, routing,
obstacle management, and configuration operations while maintaining
backward-compatibility with standard Python exceptions.
"""

from __future__ import annotations
from typing import Optional, Dict, Any


class CampusNavigationError(Exception):
    """Base exception for all Accessible Campus Navigator domain errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} (details: {self.details})"
        return self.message


# Configuration Exceptions
class ConfigurationError(CampusNavigationError, ValueError):
    """Raised when environment or runtime configuration is invalid or missing."""
    pass


# Database Exceptions
class DatabaseError(CampusNavigationError):
    """Base exception for persistence and database operation failures."""
    pass


class DatabaseConnectionError(DatabaseError):
    """Raised when establishing a connection to SQLite/PostgreSQL fails."""
    pass


class DatabaseQueryError(DatabaseError):
    """Raised when an executed SQL statement or query violates integrity or syntax."""
    pass


class DatabaseMigrationError(DatabaseError):
    """Raised when schema migration or backup verification fails."""
    pass


# Data Validation Exceptions
class DataValidationError(CampusNavigationError, ValueError):
    """Raised when data input fails schema, range, or sanitization constraints."""
    pass


# Routing & Spatial Exceptions
class RoutingError(CampusNavigationError):
    """Base exception for graph navigation and pathfinding errors."""
    pass


class NoPathFoundError(RoutingError):
    """Raised when no valid path connects origin and destination under specified constraints."""
    pass


class InvalidLocationError(RoutingError, ValueError):
    """Raised when a requested campus node or coordinate identifier does not exist."""
    pass


class AccessibilityViolationError(RoutingError):
    """Raised when an accessible path is requested but cannot be traversed without stairs/obstacles."""
    pass


# Security & Authentication Exceptions
class SecurityError(CampusNavigationError):
    """Base exception for authentication, authorization, and RBAC errors."""
    pass


class AuthenticationError(SecurityError, ValueError):
    """Raised when user credentials or session tokens fail verification."""
    pass


class SecurityLockoutError(SecurityError, DatabaseError):
    """Exception raised when an account is temporarily locked due to excessive failed attempts."""
    pass


class AuthorizationError(SecurityError, PermissionError):
    """Raised when a user lacks required permissions or role for an administrative action."""
    pass


class SessionExpiredError(SecurityError):
    """Raised when an authenticated session has timed out or been revoked."""
    pass


# Obstacle Management Exceptions
class ObstacleError(CampusNavigationError):
    """Base exception for obstacle lifecycle and verification operations."""
    pass


class ObstacleNotFoundError(ObstacleError, KeyError):
    """Raised when an obstacle ID does not correspond to an existing record."""
    pass
