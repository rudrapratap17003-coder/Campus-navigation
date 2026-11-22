# PHASE 30 — DATABASE MIGRATION & PERSISTENCE REPORT
## Accessible Campus Navigator — JAIN Global Campus (Faculty of Engineering and Technology)

**Project:** Accessible Campus Navigator  
**Institution:** JAIN (Deemed-to-be University)  
**Lead Developer:** Rudra Pratap (USN: 25BTRCL214)  
**Repository:** `https://github.com/rudrapratap17003-coder/Campus-navigation`  
**Current Milestone:** Phase 30 — Production Deployment & Release Engineering  
**Database Architecture:** SQLite 3.45+ (Primary Durable) & PostgreSQL 14+ (Enterprise Migration Target)  
**Status:** **VERIFIED & OPERATIONAL (ZERO DATA LOSS, FULL BACKWARD COMPATIBILITY)**

---

## 1. EXECUTIVE DATABASE SUMMARY

Accessible Campus Navigator manages relational campus data across eight distinct tables: user authentication and RBAC accounts, real-time obstacle reports, administrative audit trails, brute-force rate limits, navigation session logs, saved places, favourite routes, and user feedback.

The Phase 30 database audit verified:
1. **Durable SQLite Operation:** Write-Ahead Logging (`WAL`), 5,000ms busy timeout, foreign key enforcement, and non-blocking concurrent reads.
2. **Atomic Backup and Verified Restore:** Native SQLite online backup and tested atomic restore mechanics ([`test_database_backup_and_restore_roundtrip`](file:///c:/Users/rudra%20pratap/OneDrive/Documents/Campus%20navigation/tests/test_phase30_production_deployment.py)).
3. **Enterprise PostgreSQL Migration:** Turnkey DDL generation and data export via [`database/postgres_migration.py`](file:///c:/Users/rudra%20pratap/OneDrive/Documents/Campus%20navigation/database/postgres_migration.py) for environments requiring external managed database instances (Supabase, Neon, AWS RDS, Google Cloud SQL).

---

## 2. DATABASE RELATIONAL SCHEMA (VERSION 3)

```mermaid
erDiagram
    USERS ||--o{ ADMINISTRATIVE_AUDIT_LOG : logs
    USERS ||--o{ NAVIGATION_HISTORY : records
    USERS ||--o{ USER_SAVED_PLACES : bookmarks
    USERS ||--o{ USER_FAVOURITE_ROUTES : saves
    USERS ||--o{ CAMPUS_USER_FEEDBACK : submits
    
    USERS {
        string user_id PK
        string full_name
        string username UK
        string password_hash
        string salt
        string role
        string account_status
        string created_at
        string updated_at
    }

    OBSTACLE_REPORTS {
        string report_id PK
        string location_id
        string source_location_id
        string destination_location_id
        string target_type
        string obstacle_category
        string description
        string severity
        string reported_at
        string reporter_name
        string status
        string resolution_notes
        string updated_at
    }

    ADMINISTRATIVE_AUDIT_LOG {
        string audit_id PK
        string actor_user_id FK
        string action
        string target_type
        string target_id
        string previous_status
        string new_status
        string timestamp
        string notes
    }

    LOGIN_RATE_LIMITS {
        string username
        float attempt_time
    }

    NAVIGATION_HISTORY {
        string session_id PK
        string user_id FK
        string starting_location
        string destination
        string navigation_mode
        string selected_route
        float distance_completed
        float total_distance
        float estimated_duration
        int floor_transitions
        int rerouted
        string completion_status
        string created_at
        string completed_at
    }

    USER_SAVED_PLACES {
        string saved_id PK
        string user_id FK
        string location_id
        string custom_name
        string created_at
    }

    USER_FAVOURITE_ROUTES {
        string route_id PK
        string user_id FK
        string origin_id
        string destination_id
        string route_mode
        string custom_label
        string created_at
    }

    CAMPUS_USER_FEEDBACK {
        string feedback_id PK
        string user_id FK
        string feedback_type
        string target_id
        string details
        string status
        string submitted_at
        string reviewed_at
        string reviewer_user_id
        string admin_notes
    }
```

---

## 3. SQLITE PRODUCTION PERSISTENCE & PRAGMA CONFIGURATION

In a containerized or virtual server environment, SQLite operates with high performance and zero external dependencies when configured with modern reliability pragmas:

```sql
-- Production Pragmas Enforced on Every Connection:
PRAGMA foreign_keys = ON;
PRAGMA busy_timeout = 5000;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
```

### Technical Benefits of SQLite WAL Mode
1. **Concurrent Readers and Writers:** Readers do not block writers, and writers do not block readers. Streamlit's multi-threaded background workers can read graph and location metadata without locking obstacle reporting transactions.
2. **Crash Resilience:** Write-Ahead Logging commits transactions to a separate `.db-wal` log file before flushing to the main `.db` database, preventing database corruption during unexpected container termination.
3. **Low Latency:** Query benchmarks demonstrate sub-millisecond execution times for index lookups (`test_performance_benchmarks.py`).

---

## 4. POSTGRESQL MIGRATION FRAMEWORK

For deployments on serverless hosting platforms (such as Streamlit Community Cloud or Vercel) where local filesystems are ephemeral, the repository provides a native PostgreSQL migration pipeline in [`database/postgres_migration.py`](file:///c:/Users/rudra%20pratap/OneDrive/Documents/Campus%20navigation/database/postgres_migration.py).

### 1. DDL Schema Generation
Executing `generate_postgres_ddl()` emits PostgreSQL 14+ compatible SQL with exact constraint parity:
- `VARCHAR(64)` primary keys matching UUID strings.
- Enforced `CHECK` constraints on user roles (`'Student'`, `'Field Staff'`, `'Administrator'`).
- `TIMESTAMPTZ` with timezone preservation.
- Full performance indices on usernames, roles, report statuses, and audit timestamps.

### 2. Automated SQLite-to-PostgreSQL Data Exporter
The `export_sqlite_to_postgres_sql(sqlite_db_path, output_sql_path)` function:
1. Connects to the active SQLite database using `sqlite3.Row` factory.
2. Reads records from all eight core tables.
3. Sanitizes and escapes string literals (`'` escaped as `''`).
4. Generates an atomic transactional SQL script:
   ```sql
   BEGIN;
   -- Data for table: users
   INSERT INTO users (user_id, full_name, username, ...) VALUES (...) ON CONFLICT DO NOTHING;
   -- Data for table: obstacle_reports
   INSERT INTO obstacle_reports (...) VALUES (...) ON CONFLICT DO NOTHING;
   COMMIT;
   ```
5. Verified by automated test `test_postgres_ddl_and_export_integrity` in `tests/test_phase30_production_deployment.py`.

---

## 5. MIGRATION RUNBOOK (STEP-BY-STEP EXPORT & IMPORT)

When migrating from local SQLite storage to an external PostgreSQL cloud instance (e.g. Supabase, Neon, or Google Cloud SQL):

### Step 1: Generate Migration SQL Script
Run the automated migration exporter from the project root:
```powershell
& ".venv\Scripts\python.exe" -c "
from database.postgres_migration import generate_postgres_ddl, export_sqlite_to_postgres_sql
from pathlib import Path

# 1. Output DDL schema
Path('database/postgres_schema.sql').write_text(generate_postgres_ddl(), encoding='utf-8')
print('[+] PostgreSQL DDL written to database/postgres_schema.sql')

# 2. Output Data Insert Script
exported_count = export_sqlite_to_postgres_sql('data/campus_navigation.db', 'database/postgres_data.sql')
print(f'[+] Exported {exported_count} rows to database/postgres_data.sql')
"
```

### Step 2: Execute DDL & Data Import in PostgreSQL
Connect to your target PostgreSQL database using `psql` or the cloud provider SQL editor:
```bash
# Apply schema tables and indexes
psql -h db.example.com -U campus_user -d campus_nav -f database/postgres_schema.sql

# Apply initial data records
psql -h db.example.com -U campus_user -d campus_nav -f database/postgres_data.sql
```

### Step 3: Configure Application Environment
In the production `.env` or cloud secrets configuration:
```ini
DATABASE_URL=postgresql://campus_user:your_password@db.example.com:5432/campus_nav?sslmode=require
```

---

## 6. BACKUP & VERIFIED RESTORE PROCEDURES

The application features programmatic, non-locking database backups and verified restorations implemented in `DatabaseManager`:

### Programmatic Backup
```python
db = DatabaseManager()
backup_file_path = db.backup_database()
# Output: C:\...\backups\campus_navigation_backup_20261123_013000.db
```
- Utilizes the native SQLite Online Backup API (`src_conn.backup(target_conn)`).
- Captures a complete, transactionally consistent snapshot while the application continues serving active user traffic.

### Programmatic Verified Restore
```python
db = DatabaseManager()
success = db.restore_database("backups/campus_navigation_backup_20261123_013000.db")
# Output: True
```
- Performs a pre-flight `PRAGMA quick_check;` on the backup file to ensure zero file corruption before touching the active database.
- Atomically replaces active database pages using the native backup engine.
- Re-establishes connection pools without data loss.

---

## 7. CONCLUSION

The database architecture provides complete operational continuity:
- **Zero data loss** during routine restarts through Docker persistent host volumes.
- **Immediate disaster recovery** through tested online backup and restore methods.
- **Enterprise elasticity** through turnkey PostgreSQL DDL and data migration scripts.

*Report Certified By:*  
**Rudra Pratap** (USN: 25BTRCL214)  
Lead Software Developer & Database Architect  
November 2026
