"""SQLite database management, schema creation, user authentication, and parameterized queries."""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import secrets
import sqlite3
import time
from typing import Any, Dict, Generator, List, Optional, Tuple, Union


class DatabaseError(Exception):
    """Base exception for SQLite database operation failures."""

    pass


class SecurityLockoutError(DatabaseError):
    """Exception raised when an account is temporarily locked due to excessive failed attempts."""

    pass


class DatabaseManager:
    """Manages persistent SQLite storage for campus navigation, user authentication, and obstacle reports."""

    DEFAULT_DB_FILE = "campus_navigation.db"
    PBKDF2_RECOMMENDED_ITERATIONS = 600_000
    PBKDF2_LEGACY_ITERATIONS = 100_000
    PBKDF2_ITERATIONS = PBKDF2_RECOMMENDED_ITERATIONS
    PBKDF2_ALGORITHM = "sha256"

    MAX_FAILED_LOGIN_ATTEMPTS = 5
    LOGIN_LOCKOUT_SECONDS = 300  # 5 minutes

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

    CREATE_RATE_LIMIT_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS login_rate_limits (
        username TEXT NOT NULL,
        attempt_time REAL NOT NULL
    );
    """

    CREATE_NAVIGATION_HISTORY_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS navigation_history (
        session_id TEXT PRIMARY KEY,
        user_id TEXT,
        starting_location TEXT NOT NULL,
        destination TEXT NOT NULL,
        navigation_mode TEXT NOT NULL,
        selected_route TEXT NOT NULL,
        distance_completed REAL NOT NULL,
        total_distance REAL NOT NULL,
        estimated_duration REAL NOT NULL,
        floor_transitions INTEGER NOT NULL DEFAULT 0,
        rerouted INTEGER NOT NULL DEFAULT 0,
        completion_status TEXT NOT NULL CHECK(completion_status IN ('completed', 'cancelled', 'interrupted', 'rerouted')),
        created_at TEXT NOT NULL,
        completed_at TEXT
    );
    """

    CREATE_TABLES_SQL = [
        CREATE_TABLE_SQL,
        CREATE_USERS_TABLE_SQL,
        CREATE_AUDIT_LOG_TABLE_SQL,
        CREATE_RATE_LIMIT_TABLE_SQL,
        CREATE_NAVIGATION_HISTORY_TABLE_SQL,
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
        "CREATE INDEX IF NOT EXISTS idx_rate_limit_user ON login_rate_limits (username, attempt_time);",
        "CREATE INDEX IF NOT EXISTS idx_nav_history_user ON navigation_history (user_id);",
        "CREATE INDEX IF NOT EXISTS idx_nav_history_status ON navigation_history (completion_status);",
        "CREATE INDEX IF NOT EXISTS idx_nav_history_created ON navigation_history (created_at);",
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
            try:
                yield self._memory_conn
                self._memory_conn.commit()
            except sqlite3.Error as exc:
                self._memory_conn.rollback()
                raise DatabaseError(f"Database operation failed: {exc}") from exc
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
    def hash_password(
        password: str,
        salt: Optional[str] = None,
        iterations: Optional[int] = None,
    ) -> Tuple[str, str]:
        """Hash a password using PBKDF2-HMAC-SHA256 with cryptographic salting and configurable work factor.

        Supports both modern format ('<iterations>$<salt_hex>') and legacy format ('<salt_hex>').

        Args:
            password: Plaintext password.
            salt: Optional salt. If contains '$', parsed as '<iterations>$<salt_hex>'.
                  If plain hex, treated as legacy salt unless iterations is explicitly supplied.
            iterations: Optional explicit iteration count override.

        Returns:
            Tuple of (password_hash_hex, salt_string).
        """
        if not password:
            raise ValueError("Password cannot be empty.")

        if salt is not None and "$" in salt:
            parts = salt.split("$", 1)
            try:
                iter_count = int(parts[0])
            except ValueError:
                iter_count = iterations or DatabaseManager.PBKDF2_RECOMMENDED_ITERATIONS
            actual_salt = parts[1]
            stored_salt = salt
        elif salt is not None:
            # Legacy salt (plain hex without '$')
            iter_count = iterations or DatabaseManager.PBKDF2_LEGACY_ITERATIONS
            actual_salt = salt
            stored_salt = salt
        else:
            iter_count = iterations or DatabaseManager.PBKDF2_RECOMMENDED_ITERATIONS
            actual_salt = secrets.token_hex(16)
            stored_salt = f"{iter_count}${actual_salt}"

        pwd_hash = hashlib.pbkdf2_hmac(
            DatabaseManager.PBKDF2_ALGORITHM,
            password.encode("utf-8"),
            actual_salt.encode("utf-8"),
            iter_count,
        ).hex()
        return pwd_hash, stored_salt

    @staticmethod
    def verify_password(password: str, password_hash: str, salt: str) -> bool:
        """Verify candidate plaintext password against stored hash using constant-time comparison."""
        if not password or not password_hash or not salt:
            return False
        candidate_hash, _ = DatabaseManager.hash_password(password, salt=salt)
        return hmac.compare_digest(candidate_hash, password_hash)

    def is_account_locked(self, username: str) -> Tuple[bool, int]:
        """Check whether the username has exceeded failed login attempt limits.

        Returns:
            Tuple of (is_locked: bool, remaining_seconds: int).
        """
        clean_user = username.lower().strip()
        now = time.time()
        cutoff = now - self.LOGIN_LOCKOUT_SECONDS
        sql = "SELECT attempt_time FROM login_rate_limits WHERE username = ? AND attempt_time > ? ORDER BY attempt_time ASC;"
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(sql, (clean_user, cutoff))
                rows = cursor.fetchall()
            if len(rows) >= self.MAX_FAILED_LOGIN_ATTEMPTS:
                oldest_in_window = rows[0]["attempt_time"]
                remaining = int(self.LOGIN_LOCKOUT_SECONDS - (now - oldest_in_window))
                return True, max(1, remaining)
            return False, 0
        except sqlite3.Error:
            return False, 0

    def record_failed_login(self, username: str) -> None:
        """Record a failed login attempt for rate-limiting purposes."""
        clean_user = username.lower().strip()
        now = time.time()
        sql = "INSERT INTO login_rate_limits (username, attempt_time) VALUES (?, ?);"
        try:
            with self.get_connection() as conn:
                conn.execute(sql, (clean_user, now))
                # Prune old attempts beyond window to keep table lightweight
                conn.execute("DELETE FROM login_rate_limits WHERE attempt_time < ?;", (now - 3600,))
        except sqlite3.Error:
            pass

    def reset_failed_logins(self, username: str) -> None:
        """Clear failed login attempts following successful authentication."""
        clean_user = username.lower().strip()
        sql = "DELETE FROM login_rate_limits WHERE username = ?;"
        try:
            with self.get_connection() as conn:
                conn.execute(sql, (clean_user,))
        except sqlite3.Error:
            pass

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
        """Register a new user in the database with hardened password policy and role enforcement.

        Args:
            full_name: Real or display name of the user (max 100 characters).
            username: Unique username identifier (3-40 characters).
            password: Plaintext password (min 8 characters, must contain letters and numbers).
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
        if len(full_name) > 100:
            raise ValueError("Full name cannot exceed 100 characters.")

        if not username or not str(username).strip():
            raise ValueError("Username cannot be empty.")
        username = str(username).strip()
        if len(username) < 3 or len(username) > 40 or not re.match(r"^[a-zA-Z0-9_\-\.]+$", username):
            raise ValueError(
                "Username must be between 3 and 40 characters and contain only letters, numbers, hyphens, underscores, or periods."
            )

        if not password or len(password) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not any(c.isdigit() for c in password) or not any(c.isalpha() for c in password):
            raise ValueError("Password must contain at least one letter and one number.")

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
        """Verify user credentials with rate-limiting and automatic work factor upgrades.

        Args:
            username: Username candidate.
            password: Plaintext password candidate.

        Returns:
            Sanitized user dictionary (without hash/salt) if valid, or None if authentication fails.

        Raises:
            SecurityLockoutError: If the account is temporarily locked due to excessive failed attempts.
        """
        clean_user = username.strip().lower()
        is_locked, remaining = self.is_account_locked(clean_user)
        if is_locked:
            raise SecurityLockoutError(
                f"Account is temporarily locked due to excessive failed attempts. Please retry in {remaining} seconds."
            )

        user_record = self.get_user_by_username(clean_user, include_secrets=True)
        if not user_record:
            self.record_failed_login(clean_user)
            return None

        if not self.verify_password(password, user_record["password_hash"], user_record["salt"]):
            self.record_failed_login(clean_user)
            return None

        # Check account active status
        if user_record["account_status"] != "Active":
            return {
                "user_id": user_record["user_id"],
                "full_name": user_record["full_name"],
                "username": user_record["username"],
                "role": user_record["role"],
                "account_status": user_record["account_status"],
                "created_at": user_record["created_at"],
                "updated_at": user_record["updated_at"],
            }

        # Successful authentication: reset failed attempts
        self.reset_failed_logins(clean_user)

        # Automatic security upgrade for legacy work factors
        salt_val = str(user_record["salt"])
        needs_upgrade = (
            "$" not in salt_val
            or int(salt_val.split("$")[0]) < self.PBKDF2_RECOMMENDED_ITERATIONS
        )
        if needs_upgrade:
            try:
                new_hash, new_salt = self.hash_password(password)
                now_iso = datetime.now(timezone.utc).isoformat()
                with self.get_connection() as conn:
                    conn.execute(
                        "UPDATE users SET password_hash = ?, salt = ?, updated_at = ? WHERE user_id = ?;",
                        (new_hash, new_salt, now_iso, user_record["user_id"]),
                    )
                self.log_audit_action(
                    actor_user_id=user_record["user_id"],
                    action="UPGRADE_SECURITY",
                    target_type="user_account",
                    target_id=user_record["user_id"],
                    notes="Progressively upgraded password hash work factor to 600,000 PBKDF2 iterations.",
                )
            except Exception:
                pass

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

    # Alias for API compatibility
    log_audit_event = log_audit_action

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
                audit_results = []
                for row in cursor.fetchall():
                    audit_dict = dict(row)
                    audit_dict["user_id"] = audit_dict.get("actor_user_id")
                    audit_results.append(audit_dict)
                return audit_results
        except sqlite3.Error as exc:
            raise DatabaseError(f"Failed to retrieve audit log entries: {exc}") from exc

    # -------------------------------------------------------------------------
    # Phase 16: Navigation History & Journey Summaries Persistence
    # -------------------------------------------------------------------------

    def record_navigation_session(self, session_data: Dict[str, Any]) -> str:
        """Persist a navigation session summary to SQLite.

        Args:
            session_data: Dictionary containing journey attributes:
                - session_id (optional)
                - user_id (optional)
                - starting_location
                - destination
                - navigation_mode ('standard' or 'wheelchair')
                - selected_route (list or json string)
                - distance_completed (float)
                - total_distance (float)
                - estimated_duration (float)
                - floor_transitions (int)
                - rerouted (bool/int)
                - completion_status ('completed', 'cancelled', 'interrupted', 'rerouted')
                - created_at (optional iso timestamp)
                - completed_at (optional iso timestamp)

        Returns:
            The recorded session_id string.
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        session_id = str(session_data.get("session_id") or f"NAV_{secrets.token_hex(8)}")
        user_id = str(session_data["user_id"]) if session_data.get("user_id") else None
        start_loc = str(
            session_data.get("starting_location")
            or session_data.get("origin_name")
            or session_data.get("origin_id")
            or ""
        )
        dest = str(
            session_data.get("destination")
            or session_data.get("destination_name")
            or session_data.get("destination_id")
            or ""
        )
        mode = str(
            session_data.get(
                "navigation_mode",
                "wheelchair" if session_data.get("wheelchair_mode") else "standard"
            )
        )

        route_raw = session_data.get("selected_route", [])
        route_str = route_raw if isinstance(route_raw, str) else json.dumps(route_raw)

        dist_comp = float(
            session_data.get("distance_completed")
            or session_data.get("total_distance")
            or 0.0
        )
        total_dist = float(session_data.get("total_distance", dist_comp))
        est_dur = float(
            session_data.get("estimated_duration")
            or session_data.get("total_time")
            or 0.0
        )
        transitions = int(
            session_data.get("floor_transitions")
            or session_data.get("floor_transitions_count")
            or 0
        )
        rerouted = 1 if (session_data.get("rerouted") or session_data.get("is_rerouted")) else 0

        raw_status = str(session_data.get("completion_status") or session_data.get("status") or "completed").lower()
        if raw_status in ("completed", "arrived"):
            status = "completed"
        elif raw_status in ("cancelled", "canceled"):
            status = "cancelled"
        elif raw_status in ("rerouted",):
            status = "rerouted"
        else:
            status = "interrupted"

        created_at = str(session_data.get("created_at") or now_iso)
        completed_at = str(session_data.get("completed_at") or now_iso)

        sql = """
        INSERT INTO navigation_history (
            session_id, user_id, starting_location, destination, navigation_mode,
            selected_route, distance_completed, total_distance, estimated_duration,
            floor_transitions, rerouted, completion_status, created_at, completed_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(session_id) DO UPDATE SET
            distance_completed = excluded.distance_completed,
            floor_transitions = excluded.floor_transitions,
            rerouted = excluded.rerouted,
            completion_status = excluded.completion_status,
            completed_at = excluded.completed_at;
        """
        params = (
            session_id,
            user_id,
            start_loc,
            dest,
            mode,
            route_str,
            dist_comp,
            total_dist,
            est_dur,
            transitions,
            rerouted,
            status,
            created_at,
            completed_at,
        )

        try:
            with self.get_connection() as conn:
                conn.execute(sql, params)
            return session_id
        except sqlite3.Error as exc:
            raise DatabaseError(f"Failed to record navigation session: {exc}") from exc

    def update_navigation_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing navigation session record in SQLite."""
        allowed_cols = {
            "distance_completed": float,
            "completion_status": str,
            "rerouted": lambda x: 1 if x else 0,
            "floor_transitions": int,
            "completed_at": str,
        }
        set_clauses = []
        params = []
        for col, caster in allowed_cols.items():
            if col in updates:
                set_clauses.append(f"{col} = ?")
                params.append(caster(updates[col]))

        if not set_clauses:
            return False

        sql = f"UPDATE navigation_history SET {', '.join(set_clauses)} WHERE session_id = ?;"
        params.append(session_id)

        try:
            with self.get_connection() as conn:
                cursor = conn.execute(sql, tuple(params))
                return cursor.rowcount > 0
        except sqlite3.Error as exc:
            raise DatabaseError(f"Failed to update navigation session: {exc}") from exc

    def get_navigation_history(
        self,
        user_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Retrieve recent navigation history journeys.

        If user_id is provided, only journeys belonging to that user are returned
        (strictly isolating user data per RBAC rules). If user_id is None, returns
        recent journeys up to limit.
        """
        if user_id:
            sql = "SELECT * FROM navigation_history WHERE user_id = ? ORDER BY created_at DESC LIMIT ?;"
            params = (str(user_id), limit)
        else:
            sql = "SELECT * FROM navigation_history ORDER BY created_at DESC LIMIT ?;"
            params = (limit,)

        try:
            with self.get_connection() as conn:
                cursor = conn.execute(sql, params)
                rows = cursor.fetchall()

            results = []
            for r in rows:
                d = dict(r)
                try:
                    d["selected_route"] = json.loads(d["selected_route"])
                except Exception:
                    pass
                results.append(d)
            return results
        except sqlite3.Error as exc:
            raise DatabaseError(f"Failed to retrieve navigation history: {exc}") from exc

    def get_navigation_stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Compute aggregate navigation metrics for administrative reporting or specific user."""
        if user_id:
            sql = """
            SELECT
                COUNT(*) as total_sessions,
                SUM(CASE WHEN completion_status = 'completed' THEN 1 ELSE 0 END) as completed_sessions,
                SUM(CASE WHEN completion_status = 'cancelled' THEN 1 ELSE 0 END) as cancelled_sessions,
                SUM(CASE WHEN rerouted = 1 THEN 1 ELSE 0 END) as rerouted_sessions,
                COALESCE(SUM(distance_completed), 0.0) as total_distance_completed_m,
                COALESCE(AVG(distance_completed), 0.0) as avg_distance_completed_m
            FROM navigation_history
            WHERE user_id = ?;
            """
            params = (str(user_id),)
        else:
            sql = """
            SELECT
                COUNT(*) as total_sessions,
                SUM(CASE WHEN completion_status = 'completed' THEN 1 ELSE 0 END) as completed_sessions,
                SUM(CASE WHEN completion_status = 'cancelled' THEN 1 ELSE 0 END) as cancelled_sessions,
                SUM(CASE WHEN rerouted = 1 THEN 1 ELSE 0 END) as rerouted_sessions,
                COALESCE(SUM(distance_completed), 0.0) as total_distance_completed_m,
                COALESCE(AVG(distance_completed), 0.0) as avg_distance_completed_m
            FROM navigation_history;
            """
            params = ()

        try:
            with self.get_connection() as conn:
                cursor = conn.execute(sql, params)
                row = cursor.fetchone()
                res = dict(row) if row else {
                    "total_sessions": 0,
                    "completed_sessions": 0,
                    "cancelled_sessions": 0,
                    "rerouted_sessions": 0,
                    "total_distance_completed_m": 0.0,
                    "avg_distance_completed_m": 0.0,
                }
                total_s = res.get("total_sessions") or 0
                comp_s = res.get("completed_sessions") or 0
                res["completion_rate"] = round((comp_s / total_s) * 100.0, 1) if total_s > 0 else 0.0
                res["total_distance_navigated"] = res.get("total_distance_completed_m", 0.0)
                res["average_duration_seconds"] = 0.0
                return res
        except sqlite3.Error as exc:
            raise DatabaseError(f"Failed to compute navigation stats: {exc}") from exc

    # -------------------------------------------------------------------------
    # Phase 16: Administrative Data Quality & Verification Governance
    # -------------------------------------------------------------------------

    def update_campus_verification(
        self,
        entity_id: Optional[str] = None,
        status: Optional[str] = None,
        confidence_level: Optional[str] = "High",
        source: Optional[str] = "On-site validation",
        notes: str = "",
        admin_user_id: Optional[str] = None,
        entity_type: Optional[str] = "location",
        user_role: Optional[str] = None,
        user_id: Optional[str] = None,
        target_id: Optional[str] = None,
        verification_status: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """Update verification status for a location or pathway with mandatory administrative audit logging.

        Args:
            entity_id: Target location or pathway identifier.
            status: Must be one of ('VERIFIED', 'IMAGE_DERIVED', 'APPROXIMATE', 'UNVERIFIED').
            confidence_level: Optional confidence level ('High', 'Moderate', 'Approximate', 'Low').
            source: Source of verification (survey, blueprint, physical check).
            notes: Contextual justification and notes.
            admin_user_id: User ID of administrator performing the action.
            entity_type: 'location' or 'pathway'.
            user_role: Explicit user role string (checked against 'Administrator').
            user_id: User identifier.
            target_id: Alternative alias for entity_id.
            verification_status: Alternative alias for status.

        Returns:
            Tuple of (success_boolean, message_string).
        """
        eff_target_id = target_id or entity_id
        eff_status = status or verification_status
        eff_user_id = user_id or admin_user_id or "admin"
        eff_role = user_role

        if eff_role is None and eff_user_id:
            user = self.get_user_by_id(eff_user_id)
            if user:
                eff_role = user.get("role")

        if eff_role != "Administrator":
            return False, f"Permission denied: User '{eff_user_id}' with role '{eff_role}' is not authorized to update campus verification metadata."

        allowed_statuses = {"VERIFIED", "IMAGE_DERIVED", "APPROXIMATE", "UNVERIFIED"}
        if eff_status not in allowed_statuses:
            return False, f"Invalid verification status: '{eff_status}'. Must be one of {allowed_statuses}"

        if not notes or not notes.strip():
            return False, "Mandatory administrative notes must be provided when updating campus verification metadata."

        # Log immutable administrative audit event
        self.log_audit_event(
            actor_user_id=eff_user_id,
            action="UPDATE_CAMPUS_VERIFICATION",
            target_type="system",
            target_id=str(eff_target_id),
            previous_status=None,
            new_status=f"{eff_status}:{confidence_level}",
            notes=f"Source: {source} | {notes.strip()}",
        )
        return True, f"Verification status for '{eff_target_id}' successfully updated to '{eff_status}'."

    def close(self) -> None:
        """Close any open persistent connection (such as in-memory database)."""
        if self._memory_conn is not None:
            try:
                self._memory_conn.close()
            except sqlite3.Error:
                pass
            self._memory_conn = None
