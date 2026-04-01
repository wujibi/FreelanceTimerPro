"""
Repair missing parent rows (clients / projects / tasks) so SQLite foreign keys
hold, then run DatabaseManager setup (including billing_history backfill).

Usage (from repo root):
  python scripts/repair_invoice_fk_and_backfill.py "C:\\path\\to\\time_tracker.db"

Default LIVE path (override with argument):
  C:\\Users\\briah\\My Drive\\TimeTrackerApp\\data\\time_tracker.db
"""
from __future__ import annotations

import argparse
import os
import sqlite3
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB = r"C:\Users\briah\My Drive\TimeTrackerApp\data\time_tracker.db"


def insert_stub_fk_parents(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    # Names match billing_history / time_entries denormalized data where known.
    clients = [
        (1, "Client 1"),
        (2, "Test Client"),
        (3, "Wendy Flanagan"),
        (4, "Novel Crafting"),
        (5, "Me"),
        (8, "Archived client (restored id 8)"),
        (9, "Archived client (restored id 9)"),
    ]
    cur.executemany(
        "INSERT OR IGNORE INTO clients (id, name) VALUES (?, ?)",
        clients,
    )

    projects = [
        (1, 1, "Project 1"),
        (2, 2, "Test Client Project"),
        (13, 6, "Project Analysis and Reporting"),
    ]
    cur.executemany(
        "INSERT OR IGNORE INTO projects (id, client_id, name) VALUES (?, ?, ?)",
        projects,
    )

    cur.execute(
        """
        INSERT OR IGNORE INTO tasks (id, project_id, name, hourly_rate, is_global)
        VALUES (?, ?, ?, 0, 0)
        """,
        (2, 1, "Billing Stuff"),
    )

    conn.commit()


def main() -> int:
    parser = argparse.ArgumentParser(description="Repair FK stubs and backfill billing_history.")
    parser.add_argument(
        "db_path",
        nargs="?",
        default=DEFAULT_DB,
        help="Path to time_tracker.db",
    )
    args = parser.parse_args()
    db_path = os.path.abspath(args.db_path)

    if not os.path.isfile(db_path):
        print(f"ERROR: database file not found: {db_path}", file=sys.stderr)
        return 1

    print(f"Repairing FK parents on: {db_path}")
    conn = sqlite3.connect(db_path)
    try:
        insert_stub_fk_parents(conn)
    finally:
        conn.close()

    sys.path.insert(0, REPO_ROOT)
    from db_manager import DatabaseManager  # noqa: E402

    print("Running DatabaseManager setup (schema + billing_history backfill)...")
    db = DatabaseManager(db_path)
    db.close()

    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    fk = conn.execute("PRAGMA foreign_key_check").fetchall()
    bh = conn.execute("SELECT COUNT(*) FROM billing_history").fetchone()[0]
    gap = conn.execute(
        """
        SELECT COUNT(DISTINCT te.invoice_number)
        FROM time_entries te
        WHERE te.is_billed = 1
          AND te.invoice_number IS NOT NULL
          AND TRIM(te.invoice_number) != ''
          AND te.invoice_number NOT IN (SELECT invoice_number FROM billing_history)
        """
    ).fetchone()[0]
    conn.close()

    print(f"Done. FK violations remaining: {len(fk)}")
    print(f"billing_history rows: {bh}")
    print(f"Billed invoices still missing billing_history: {gap}")
    if fk:
        print("Sample FK issues (first 5):")
        for row in fk[:5]:
            print(dict(row))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
