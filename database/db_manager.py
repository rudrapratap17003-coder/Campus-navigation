"""SQLite database management, schema creation, user authentication, and parameterized queries."""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import hmac
import os
from pathlib import Path
import re
import secrets
import sqlite3
from typing import Any, Dict, Generator, List, Optional, Tuple, Union


class DatabaseError(Exception):
    """Base exception for SQLite database operation failures."""

    pass


class DatabaseManager:
    """Manages persistent SQLite storage for campus navigation, user authentication, and obstacle reports."""

    DEFAULT_DB_FILE = "campus_navigation.db"
    PBKDF2_ITERATIONS = 100_000
    PBKDF2_ALGORITHM = "sha256"

    ALLOWED_ROLES: Tuple[str, ...] = ("Student", "Field Staff", "Administrator")
    ALLOWED_USER_STATUSES: Tuple[str, ...] = ("Active", "Inactive")

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

    CREATE_USERS_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        full_name TEXT NOT NULL,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('Student', 'Field Staff', 'Administrator')),
        account_status TEXT NOT NULL CHECK(account_status IN ('Active', 'Inactive')),
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """

    CREATE_AUDIT_LOG_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS administrative_audit_log (
        audit_id TEXT PRIMARY KEY,
        actor_user_id TEXT NOT NULL,
        action TEXT NOT NULL,
        target_type TEXT NOT NULL CHECK(target_type IN ('obstacle_report', 'user_account', 'system')),
        target_id TEXT NOT NULL,
        previous_status TEXT,
        new_status TEXT,
        timestamp TEXT NOT NULL,
        notes TEXT
    );
    """

    CREATE_TABLES_SQL = [
        CREATE_TABLE_SQL,
        CREATE_USERS_TABLE_SQL,
        CREATE_AUDIT_LOG_TABLE_SQL,
    ]

    CREATE_INDEXES_SQL = [
        "CREATE INDEX IF NOT EXISTS idx_obstacle_status ON obstacle_reports (status);",
        "CREATE INDEX IF NOT EXISTS idx_obstacle_location ON obstacle_reports (location_id);",
        "CREATE INDEX IF NOT EXISTS idx_obstacle_pathway ON obstacle_reports (source_location_id, destination_location_id);",
        "CREATE INDEX IF NOT EXISTS idx_obstacle_reported_at ON obstacle_reports (reported_at);",
        "CREATE INDEX IF NOT EXISTS idx_users_username ON users (username);",
        "CREATE INDEX IF NOT EXISTS idx_users_role ON users (role);",
        "CREATE INDEX IF NOT EXISTS idx_users_status ON users (account_status);",
        "CREATE INDEX IF NOT EXISTS idx_audit_actor ON administrative_audit_log (actor_user_id);",
        "CREATE INDEX IF NOT EXISTS idx_audit_action ON administrative_audit_log (action);",
        "CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON administrative_audit_log (timestamp);",
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

        # Check environment variables for initial admin bootstrap if configured
        env_admin_user = os.environ.get("CAMPUS_ADMIN_USERNAME")
        env_admin_pass = os.environ.get("CAMPUS_ADMIN_PASSWORD")
        if env_admin_user and env_admin_pass and not self.has_admin_user():
            try:
                self.create_user(
                    full_name="System Administrator",
                    username=env_admin_user.strip(),
                    password=env_admin_pass.strip(),
                    role="Administrator",
                    account_status="Active",
                )
            except Exception:
                pass

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
                for table_sql in self.CREATE_TABLES_SQL:
                    conn.execute(table_sql)
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

    # =========================================================================
    # USER AUTHENTICATION & ROLE-BASED ACCESS CONTROL (RBAC)
    # =========================================================================

    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """Hash a password using PBKDF2-HMAC-SHA256 with a unique cryptographic salt.

        Args:
            password: Plaintext password.
            salt: Optional hex salt. If None, a secure 16-byte random salt is generated.

        Returns:
            Tuple of (password_hash_hex, salt_hex).
        """
        if not password:
            raise ValueError("Password cannot be empty.")
        if salt is None:
            salt = secrets.token_hex(16)
        pwd_hash = hashlib.pbkdf2_hmac(
            DatabaseManager.PBKDF2_ALGORITHM,
            password.encode("utf-8"),
            salt.encode("utf-8"),
            DatabaseManager.PBKDF2_ITERATIONS,
        ).hex()
        return pwd_hash, salt

    @staticmethod
    def verify_password(password: str, password_hash: str, salt: str) -> bool:
        """Verify a plaintext password against a stored PBKDF2-HMAC-SHA256 hash using constant-time comparison.

        Args:
            password: Plaintext password candidate.
            password_hash: Stored hex hash.
            salt: Stored hex salt.

        Returns:
            True if candidate password matches, False otherwise.
        """
        if not password or not password_hash or not salt:
            return False
        candidate_hash, _ = DatabaseManager.hash_password(password, salt=salt)
        return hmac.compare_digest(candidate_hash, password_hash)

    def create_user(
        self,
        full_name: str,
        username: str,
        password: str,
        role: str = "Student",
        account_status: str = "Active",
        actor_user: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Register a new user in the database with hashed credentials and role enforcement.

        Args:
            full_name: Real or display name of the user.
            username: Unique username identifier.
            password: Plaintext password (min 6 characters).
            role: 'Student', 'Field Staff', or 'Administrator'.
            account_status: 'Active' or 'Inactive'.
            actor_user: Optional dict of the acting authenticated user performing the creation.
            user_id: Optional custom user ID.

        Returns:
            Sanitized dictionary representation of the newly created user.

        Raises:
            ValueError: If input validation fails (e.g. invalid username, weak password).
            PermissionError: If creating an elevated account without Administrator authority.
            DatabaseError: If insertion or query execution fails.
        """
        if not full_name or not str(full_name).strip():
            raise ValueError("Full name cannot be empty.")
        full_name = str(full_name).strip()

        if not username or not str(username).strip():
            raise ValueError("Username cannot be empty.")
        username = str(username).strip()
        if len(username) < 3 or not re.match(r"^[a-zA-Z0-9_\-\.]+$", username):
            raise ValueError(
                "Username must be at least 3 characters and contain only letters, numbers, hyphens, underscores, or periods."
            )

        if not password or len(password) < 6:
            raise ValueError("Password must be at least 6 characters long.")

        if role not in self.ALLOWED_ROLES:
            raise ValueError(f"Invalid role '{role}'. Must be one of: {', '.join(self.ALLOWED_ROLES)}.")

        if account_status not in self.ALLOWED_USER_STATUSES:
            raise ValueError(
                f"Invalid account_status '{account_status}'. Must be one of: {', '.join(self.ALLOWED_USER_STATUSES)}."
            )

        # Check existing username uniqueness (case-insensitive)
        existing = self.get_user_by_username(username)
        if existing is not None:
            raise ValueError(f"Username '{username}' is already registered.")

        # RBAC Check: Creating elevated roles ('Field Staff' or 'Administrator')
        # Only allowed during initial setup (if no admin exists) OR by an active Administrator.
        if role in ("Field Staff", "Administrator"):
            has_admin = self.has_admin_user()
            if has_admin:
                if (
                    not actor_user
                    or actor_user.get("role") != "Administrator"
                    or actor_user.get("account_status") != "Active"
                ):
                    raise PermissionError(
                        "Permission Denied: Only an active Administrator can register or assign Field Staff or Administrator roles."
                    )

        if not user_id:
            user_id = f"USR-{secrets.token_hex(4).upper()}"

        pwd_hash, salt = self.hash_password(password)
        now_iso = datetime.now(timezone.utc).isoformat()

        sql = """
        INSERT INTO users (
            user_id, full_name, username, password_hash, salt, role, account_status, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        params = (user_id, full_name, username, pwd_hash, salt, role, account_status, now_iso, now_iso)

        try:
            with self.get_connection() as conn:
                conn.execute(sql, params)
        except sqlite3.Error as exc:
            raise DatabaseError(f"Failed to create user '{username}': {exc}") from exc

        # Audit log creation
        actor_id = actor_user.get("user_id", "system") if actor_user else "system"
        self.log_audit_action(
            actor_user_id=actor_id,
            action="CREATE_USER",
            target_type="user_account",
            target_id=user_id,
            new_status=f"Role: {role}, Status: {account_status}",
            notes=f"Created user @{username} ({full_name})",
        )

        return {
            "user_id": user_id,
            "full_name": full_name,
            "username": username,
            "role": role,
            "account_status": account_status,
            "created_at": now_iso,
            "updated_at": now_iso,
        }

    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Verify user credentials and return sanitized user record if valid.

        Args:
            username: Username candidate.
            password: Plaintext password candidate.

        Returns:
            Sanitized user dictionary (without hash/salt) if valid, or None if authentication fails.
        """
        user_record = self.get_user_by_username(username, include_secrets=True)
        if not user_record:
            return None

        if not self.verify_password(password, user_record["password_hash"], user_record["salt"]):
            return None

        # Return sanitized dict
        return {
            "user_id": user_record["user_id"],
            "full_name": user_record["full_name"],
            "username": user_record["username"],
            "role": user_record["role"],
            "account_status": user_record["account_status"],
            "created_at": user_record["created_at"],
            "updated_at": user_record["updated_at"],
        }

    def get_user_by_id(self, user_id: str, include_secrets: bool = False) -> Optional[Dict[str, Any]]:
        """Retrieve user record by unique user_id."""
        sql = "SELECT * FROM users WHERE user_id = ?;"
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(sql, (user_id,))
                row = cursor.fetchone()
                if not row:
                    return None
                data = dict(row)
                if not include_secrets:
                    data.pop("password_hash", None)
                    data.pop("salt", None)
                return data
        except sqlite3.Error as exc:
            raise DatabaseError(f"Failed to retrieve user ID '{user_id}': {exc}") from exc

    def get_user_by_username(self, username: str, include_secrets: bool = False) -> Optional[Dict[str, Any]]:
        """Retrieve user record by username (case-insensitive)."""
        sql = "SELECT * FROM users WHERE LOWER(username) = LOWER(?);"
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(sql, (username.strip(),))
                row = cursor.fetchone()
                if not row:
                    return None
                data = dict(row)
                if not include_secrets:
                    data.pop("password_hash", None)
                    data.pop("salt", None)
                return data
        except sqlite3.Error as exc:
            raise DatabaseError(f"Failed to retrieve user '@{username}': {exc}") from exc

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Retrieve all registered users without sensitive hash/salt information."""
        sql = "SELECT user_id, full_name, username, role, account_status, created_at, updated_at FROM users ORDER BY created_at DESC;"
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(sql)
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as exc:
            raise DatabaseError(f"Failed to retrieve all users: {exc}") from exc

    def update_user_role(
        self,
        user_id: str,
        new_role: str,
        actor_user: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Update a user's role with Administrator verification and self-demotion prevention."""
        if actor_user is not None:
            if actor_user.get("role") != "Administrator" or actor_user.get("account_status") != "Active":
                raise PermissionError("Only an active Administrator can modify user roles.")

        if new_role not in self.ALLOWED_ROLES:
            raise ValueError(f"Invalid role '{new_role}'. Must be one of: {', '.join(self.ALLOWED_ROLES)}.")

        target_user = self.get_user_by_id(user_id)
        if not target_user:
            raise ValueError(f"User ID '{user_id}' does not exist.")

        prev_role = target_user["role"]
        if prev_role == new_role:
            return True

        # Guard: Prevent demoting the last remaining active Administrator
        if prev_role == "Administrator" and new_role != "Administrator":
            active_admins = self.get_users_by_role("Administrator", status="Active")
            if len(active_admins) <= 1 and any(u["user_id"] == user_id for u in active_admins):
                raise ValueError("Cannot demote the last remaining active Administrator.")

        now_iso = datetime.now(timezone.utc).isoformat()
        sql = "UPDATE users SET role = ?, updated_at = ? WHERE user_id = ?;"
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(sql, (new_role, now_iso, user_id))
                updated = cursor.rowcount > 0
        except sqlite3.Error as exc:
            raise DatabaseError(f"Failed to update role for user '{user_id}': {exc}") from exc

        actor_id = actor_user.get("user_id", "system") if actor_user else "system"
        self.log_audit_action(
            actor_user_id=actor_id,
            action="ASSIGN_ROLE",
            target_type="user_account",
            target_id=user_id,
            previous_status=prev_role,
            new_status=new_role,
            notes=f"Changed role of @{target_user['username']} from {prev_role} to {new_role}",
        )
        return updated

    def update_user_status(
        self,
        user_id: str,
        new_status: str,
        actor_user: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Activate or deactivate a user account with Administrator authorization."""
        if actor_user is not None:
            if actor_user.get("role") != "Administrator" or actor_user.get("account_status") != "Active":
                raise PermissionError("Only an active Administrator can modify account activation status.")

        if new_status not in self.ALLOWED_USER_STATUSES:
            raise ValueError(f"Invalid status '{new_status}'. Must be one of: {', '.join(self.ALLOWED_USER_STATUSES)}.")

        target_user = self.get_user_by_id(user_id)
        if not target_user:
            raise ValueError(f"User ID '{user_id}' does not exist.")

        prev_status = target_user["account_status"]
        if prev_status == new_status:
            return True

        # Guard: Prevent deactivating the last remaining active Administrator
        if target_user["role"] == "Administrator" and new_status == "Inactive":
            active_admins = self.get_users_by_role("Administrator", status="Active")
            if len(active_admins) <= 1 and any(u["user_id"] == user_id for u in active_admins):
                raise ValueError("Cannot deactivate the last remaining active Administrator.")

        now_iso = datetime.now(timezone.utc).isoformat()
        sql = "UPDATE users SET account_status = ?, updated_at = ? WHERE user_id = ?;"
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(sql, (new_status, now_iso, user_id))
                updated = cursor.rowcount > 0
        except sqlite3.Error as exc:
            raise DatabaseError(f"Failed to update status for user '{user_id}': {exc}") from exc

        actor_id = actor_user.get("user_id", "system") if actor_user else "system"
        self.log_audit_action(
            actor_user_id=actor_id,
            action="UPDATE_USER_STATUS",
            target_type="user_account",
            target_id=user_id,
            previous_status=prev_status,
            new_status=new_status,
            notes=f"Changed status of @{target_user['username']} to {new_status}",
        )
        return updated

    def has_admin_user(self) -> bool:
        """Check whether at least one active Administrator account exists in the database."""
        sql = "SELECT COUNT(*) as count FROM users WHERE role = 'Administrator' AND account_status = 'Active';"
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(sql)
                row = cursor.fetchone()
                return bool(row and row["count"] > 0)
        except sqlite3.Error as exc:
            raise DatabaseError(f"Failed to query administrator accounts: {exc}") from exc

    def get_users_by_role(self, role: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve users filtered by role and optional status."""
        if status:
            sql = "SELECT user_id, full_name, username, role, account_status, created_at, updated_at FROM users WHERE role = ? AND account_status = ? ORDER BY username ASC;"
            params = (role, status)
        else:
            sql = "SELECT user_id, full_name, username, role, account_status, created_at, updated_at FROM users WHERE role = ? ORDER BY username ASC;"
            params = (role,)
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(sql, params)
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as exc:
            raise DatabaseError(f"Failed to retrieve users by role '{role}': {exc}") from exc

    def get_user_statistics(self) -> Dict[str, Any]:
        """Aggregate statistical metrics for registered user accounts."""
        stats: Dict[str, Any] = {
            "total_users": 0,
            "active_users": 0,
            "inactive_users": 0,
            "role_counts": {
                "Student": 0,
                "Field Staff": 0,
                "Administrator": 0,
            },
        }
        sql = "SELECT role, account_status, COUNT(*) as count FROM users GROUP BY role, account_status;"
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(sql)
                rows = cursor.fetchall()

            for row in rows:
                r = row["role"]
                st = row["account_status"]
                cnt = row["count"]

                stats["total_users"] += cnt
                if st == "Active":
                    stats["active_users"] += cnt
                else:
                    stats["inactive_users"] += cnt

                stats["role_counts"][r] = stats["role_counts"].get(r, 0) + cnt

            return stats
        except sqlite3.Error as exc:
            raise DatabaseError(f"Failed to calculate user statistics: {exc}") from exc

    # =========================================================================
    # ADMINISTRATIVE AUDIT LOGGING
    # =========================================================================

    def log_audit_action(
        self,
        actor_user_id: str,
        action: str,
        target_type: str,
        target_id: str,
        previous_status: Optional[str] = None,
        new_status: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> str:
        """Record an administrative or operational event in the audit log.

        Args:
            actor_user_id: ID or username of the user performing the action.
            action: Descriptive action code (e.g. 'VERIFY_OBSTACLE', 'ASSIGN_ROLE').
            target_type: 'obstacle_report', 'user_account', or 'system'.
            target_id: Identifier of affected entity.
            previous_status: Optional prior state.
            new_status: Optional resulting state.
            notes: Optional contextual details.

        Returns:
            The generated audit_id string.
        """
        now = datetime.now(timezone.utc)
        audit_id = f"AUD-{now.strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(2).upper()}"
        sql = """
        INSERT INTO administrative_audit_log (
            audit_id, actor_user_id, action, target_type, target_id, previous_status, new_status, timestamp, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        params = (
            audit_id,
            str(actor_user_id),
            str(action),
            str(target_type),
            str(target_id),
            str(previous_status) if previous_status else None,
            str(new_status) if new_status else None,
            now.isoformat(),
            str(notes) if notes else None,
        )
        try:
            with self.get_connection() as conn:
                conn.execute(sql, params)
            return audit_id
        except sqlite3.Error as exc:
            raise DatabaseError(f"Failed to log audit event: {exc}") from exc

    def get_audit_logs(self, limit: int = 50, action: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve recent administrative audit log entries."""
        if action:
            sql = "SELECT * FROM administrative_audit_log WHERE action = ? ORDER BY timestamp DESC LIMIT ?;"
            params = (action, limit)
        else:
            sql = "SELECT * FROM administrative_audit_log ORDER BY timestamp DESC LIMIT ?;"
            params = (limit,)
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(sql, params)
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as exc:
            raise DatabaseError(f"Failed to retrieve audit log entries: {exc}") from exc

    def close(self) -> None:
        """Close any open persistent connection (such as in-memory database)."""
        if self._memory_conn is not None:
            try:
                self._memory_conn.close()
            except sqlite3.Error:
                pass
            self._memory_conn = None
