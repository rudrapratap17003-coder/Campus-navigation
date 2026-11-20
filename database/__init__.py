"""Database package for data persistence and SQLite interactions."""

from database.db_manager import DatabaseError, DatabaseManager

__all__ = [
    "DatabaseManager",
    "DatabaseError",
]
