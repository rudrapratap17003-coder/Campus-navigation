"""Demonstration environment preparation utility for Accessible Campus Navigator.

Safely initializes labeled academic demonstration accounts (Student, Field Staff, Administrator)
without modifying or overwriting existing user data or obstacle reports.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is on PYTHONPATH
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from database.db_manager import DatabaseManager


def prepare_demo_environment() -> None:
    """Provision labeled demonstration accounts if they do not already exist."""
    print("=" * 70)
    print("ACCESSIBLE CAMPUS NAVIGATOR - DEMONSTRATION SETUP")
    print("=" * 70)
    print("Notice: These accounts are created strictly for academic evaluation")
    print("and project demonstrations. Do not use these accounts in production.")
    print("-" * 70)

    db = DatabaseManager()

    # 1. Primary Demo Administrator
    admin_user = db.get_user_by_username("demo_admin")
    if not admin_user:
        admin_user = db.create_user(
            full_name="Demonstration Administrator",
            username="demo_admin",
            password="DemoAdmin2026!",
            role="Administrator",
            account_status="Active",
        )
        print("✅ Created Demo Administrator: @demo_admin (Role: Administrator)")
    else:
        print("ℹ️ Demo Administrator already exists: @demo_admin")

    # 2. Demo Field Staff
    if not db.get_user_by_username("demo_staff"):
        db.create_user(
            full_name="Demonstration Field Staff",
            username="demo_staff",
            password="DemoStaff2026!",
            role="Field Staff",
            account_status="Active",
            actor_user=admin_user,
        )
        print("✅ Created Demo Field Staff:   @demo_staff (Role: Field Staff)")
    else:
        print("ℹ️ Demo Field Staff already exists:   @demo_staff")

    # 3. Demo Student / Campus User
    if not db.get_user_by_username("demo_student"):
        db.create_user(
            full_name="Demonstration Student",
            username="demo_student",
            password="DemoStudent2026!",
            role="Student",
            account_status="Active",
        )
        print("✅ Created Demo Student:       @demo_student (Role: Student)")
    else:
        print("ℹ️ Demo Student already exists:       @demo_student")

    print("-" * 70)
    print("Demonstration credentials ready:")
    print("  • Student:       demo_student / DemoStudent2026!")
    print("  • Field Staff:   demo_staff   / DemoStaff2026!")
    print("  • Administrator: demo_admin   / DemoAdmin2026!")
    print("=" * 70)


if __name__ == "__main__":
    prepare_demo_environment()
