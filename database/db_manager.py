"""SQLite database management, schema creation, and parameterized query execution."""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
from typing import Any, Dict, Generator, List, Optional, Union


class DatabaseError(Exception):
    """Base exception for SQLite database operation failures."""

    pass


class DatabaseManager:
    """Manages persistent SQLite storage for campus navigation data and obstacle reports."""

    DEFAULT_DB_FILE = "campus_navigation.db"

    CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS obstacle_reports (
        report_id TEXT PRIMARY KEY,
        location_id TEXT,
        source_location_id TEXT,
        destination_location_id TEXT,
        target_type TEXT NOT NULL CHECK(target_type IN ('location', 'pathway')),
        obstacle_category TEXT NOT NULL,
        description TEXT NOT NULL,
        severity TEXT NOT NULL CHECK(severity IN ('Low', 'Medium', 'High', 'Critical')),
        reported_at TEXT NOT NULL,
        reporter_name TEXT NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('Pending', 'Verified', 'Resolved', 'Rejected')),
        resolution_notes TEXT,
        updated_at TEXT NOT NULL
    );
    """

    CREATE_INDEXES_SQL = [
        "CREATE INDEX IF NOT EXISTS idx_obstacle_status ON obstacle_reports (status);",
        "CREATE INDEX IF NOT EXISTS idx_obstacle_location ON obstacle_reports (location_id);",
        "CREATE INDEX IF NOT EXISTS idx_obstacle_pathway ON obstacle_reports (source_location_id, destination_location_id);",
        "CREATE INDEX IF NOT EXISTS idx_obstacle_reported_at ON obstacle_reports (reported_at);",
    ]

    def __init__(self, db_path: Optional[Union[str, Path]] = None) -> None:
        """Initialize the DatabaseManager.

        Args:
            db_path: Path to SQLite database file. Pass ':memory:' for transient in-memory database.
                     If None, defaults to 'data/campus_navigation.db' relative to project root.
        """
        if db_path is None:
            project_root = Path(__file__).resolve().parent.parent
            self.db_path: Union[str, Path] = project_root / "data" / self.DEFAULT_DB_FILE
            # Ensure parent data directory exists
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        elif str(db_path) == ":memory:":
            self.db_path = ":memory:"
            # Keep a persistent connection for in-memory DB so tables don't vanish
            self._memory_conn: Optional[sqlite3.Connection] = sqlite3.connect(
                ":memory:", detect_types=sqlite3.PARSE_DECLTYPES
            )
            self._memory_conn.row_factory = sqlite3.Row
            self._memory_conn.execute("PRAGMA foreign_keys = ON;")
        else:
            self.db_path = Path(db_path)
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self._memory_conn = None

        self.initialize_schema()

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager yielding a configured SQLite connection with foreign keys enabled."""
        if str(self.db_path) == ":memory:" and self._memory_conn is not None:
            yield self._memory_conn
            return

        conn = sqlite3.connect(str(self.db_path), detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            yield conn
            conn.commit()
        except sqlite3.Error as exc:
            conn.rollback()
            raise DatabaseError(f"Database operation failed: {exc}") from exc
        finally:
            conn.close()

    def initialize_schema(self) -> None:
        """Create required tables and performance indexes if they do not exist."""
        try:
            with self.get_connection() as conn:
                conn.execute(self.CREATE_TABLE_SQL)
                for index_sql in self.CREATE_INDEXES_SQL:
                    conn.execute(index_sql)
        except sqlite3.Error as exc:
            raise DatabaseError(f"Failed to initialize database schema: {exc}") from exc

    def insert_report(self, report_data: Dict[str, Any]) -> str:
        """Insert a new obstacle report into the database using parameterized queries.

        Args:
            report_data: Dictionary containing obstacle report attributes.

        Returns:
            The unique report_id string.

        Raises:
            DatabaseError: If insertion fails.
        """
        sql = """
        INSERT INTO obstacle_reports (
            report_id,
            location_id,
            source_location_id,
            destination_location_id,
            target_type,
            obstacle_category,
            description,
            severity,
            reported_at,
            reporter_name,
            status,
            resolution_notes,
            updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        report_id = str(report_data.get("report_id"))

        params = (
            report_id,
            report_data.get("location_id"),
            report_data.get("source_location_id"),
            report_data.get("destination_location_id"),
            report_data.get("target_type", "location"),
            report_data.get("obstacle_category"),
            report_data.get("description"),
            report_data.get("severity"),
            report_data.get("reported_at", now_iso),
            report_data.get("reporter_name", "Anonymous"),
            report_data.get("status", "Pending"),
            report_data.get("resolution_notes"),
            report_data.get("updated_at", now_iso),
        )

        try:
            with self.get_connection() as conn:
                conn.execute(sql, params)
            return report_id
        except sqlite3.Error as exc:
            raise DatabaseError(f"Failed to insert obstacle report '{report_id}': {exc}") from exc

    def get_report_by_id(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single obstacle report by its unique ID.

        Args:
            report_id: Unique string identifier.

        Returns:
            Dictionary representation of the report or None if not found.
        """
        sql = "SELECT * FROM obstacle_reports WHERE report_id = ?;"
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(sql, (report_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except sqlite3.Error as exc:
            raise DatabaseError(f"Failed to retrieve report '{report_id}': {exc}") from exc

    def get_all_reports(self) -> List[Dict[str, Any]]:
        """Retrieve all obstacle reports ordered by latest reported date.

        Returns:
            List of report dictionaries.
        """
        sql = "SELECT * FROM obstacle_reports ORDER BY reported_at DESC;"
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(sql)
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as exc:
            raise DatabaseError(f"Failed to retrieve all reports: {exc}") from exc

    def get_reports_by_location(self, location_id: str) -> List[Dict[str, Any]]:
        """Retrieve all reports associated with a specific location (either as node or endpoint).

        Args:
            location_id: Unique location ID.

        Returns:
            List of matching report dictionaries.
        """
        sql = """
        SELECT * FROM obstacle_reports
        WHERE location_id = ? OR source_location_id = ? OR destination_location_id = ?
        ORDER BY reported_at DESC;
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(sql, (location_id, location_id, location_id))
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as exc:
            raise DatabaseError(
                f"Failed to retrieve reports for location '{location_id}': {exc}"
            ) from exc

    def get_reports_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Retrieve reports filtered by status (Pending, Verified, Resolved, Rejected).

        Args:
            status: Target status string.

        Returns:
            List of matching report dictionaries.
        """
        sql = "SELECT * FROM obstacle_reports WHERE status = ? ORDER BY reported_at DESC;"
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(sql, (status,))
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as exc:
            raise DatabaseError(f"Failed to retrieve reports by status '{status}': {exc}") from exc

    def get_reports_by_pathway(self, source: str, destination: str) -> List[Dict[str, Any]]:
        """Retrieve reports affecting a specific connection between two locations (bidirectional).

        Args:
            source: Source location ID.
            destination: Destination location ID.

        Returns:
            List of matching report dictionaries.
        """
        sql = """
        SELECT * FROM obstacle_reports
        WHERE (source_location_id = ? AND destination_location_id = ?)
           OR (source_location_id = ? AND destination_location_id = ?)
        ORDER BY reported_at DESC;
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(sql, (source, destination, destination, source))
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as exc:
            raise DatabaseError(
                f"Failed to retrieve reports for pathway {source}<->{destination}: {exc}"
            ) from exc

    def update_report_status(
        self,
        report_id: str,
        new_status: str,
        resolution_notes: Optional[str] = None,
    ) -> bool:
        """Update the status and resolution notes of an existing report.

        Args:
            report_id: Unique identifier of the report.
            new_status: Updated status ('Pending', 'Verified', 'Resolved', 'Rejected').
            resolution_notes: Optional descriptive resolution or rejection reason.

        Returns:
            True if a row was updated, False if report_id was not found.
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        if resolution_notes is not None:
            sql = """
            UPDATE obstacle_reports
            SET status = ?, resolution_notes = ?, updated_at = ?
            WHERE report_id = ?;
            """
            params = (new_status, resolution_notes, now_iso, report_id)
        else:
            sql = """
            UPDATE obstacle_reports
            SET status = ?, updated_at = ?
            WHERE report_id = ?;
            """
            params = (new_status, now_iso, report_id)

        try:
            with self.get_connection() as conn:
                cursor = conn.execute(sql, params)
                return cursor.rowcount > 0
        except sqlite3.Error as exc:
            raise DatabaseError(
                f"Failed to update status for report '{report_id}': {exc}"
            ) from exc

    def get_active_reports(self) -> List[Dict[str, Any]]:
        """Retrieve all currently active and confirmed obstacle reports (status = 'Verified').

        Returns:
            List of active report dictionaries.
        """
        return self.get_reports_by_status("Verified")

    def get_statistics(self) -> Dict[str, Any]:
        """Aggregate statistical metrics of all recorded obstacle reports.

        Returns:
            Dictionary with total reports, status counts, severity counts, and category counts.
        """
        stats: Dict[str, Any] = {
            "total_reports": 0,
            "status_counts": {
                "Pending": 0,
                "Verified": 0,
                "Resolved": 0,
                "Rejected": 0,
            },
            "severity_counts": {
                "Low": 0,
                "Medium": 0,
                "High": 0,
                "Critical": 0,
            },
            "category_counts": {},
            "active_obstacles_count": 0,
        }

        sql = "SELECT status, severity, obstacle_category, COUNT(*) as count FROM obstacle_reports GROUP BY status, severity, obstacle_category;"
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(sql)
                rows = cursor.fetchall()

            for row in rows:
                st = row["status"]
                sev = row["severity"]
                cat = row["obstacle_category"]
                cnt = row["count"]

                stats["total_reports"] += cnt
                stats["status_counts"][st] = stats["status_counts"].get(st, 0) + cnt
                stats["severity_counts"][sev] = stats["severity_counts"].get(sev, 0) + cnt
                stats["category_counts"][cat] = stats["category_counts"].get(cat, 0) + cnt

            stats["active_obstacles_count"] = stats["status_counts"].get("Verified", 0)
            return stats
        except sqlite3.Error as exc:
            raise DatabaseError(f"Failed to calculate obstacle statistics: {exc}") from exc

    def close(self) -> None:
        """Close any open persistent connection (such as in-memory database)."""
        if self._memory_conn is not None:
            try:
                self._memory_conn.close()
            except sqlite3.Error:
                pass
            self._memory_conn = None
