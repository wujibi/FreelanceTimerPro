"""
Database Migration Script for Billing Status Feature
Adds billing tracking to prevent double-billing
"""

import sqlite3
from datetime import datetime
from pathlib import Path
import sys


def migrate_database(db_path="data/time_tracker.db"):
    """Run database migrations for billing status tracking"""

    print("=" * 50)
    print("Database Migration - Billing Status Feature")
    print("=" * 50)
    print()

    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()

        # Check current schema
        print("Checking current database schema...")

        # 1. Add is_billed column to time_entries if it doesn't exist
        cursor.execute("PRAGMA table_info(time_entries)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'is_billed' not in columns:
            print("Adding is_billed column to time_entries table...")
            cursor.execute('''
                           ALTER TABLE time_entries
                               ADD COLUMN is_billed INTEGER DEFAULT 0
                           ''')
            print("✓ Added is_billed column")
        else:
            print("✓ is_billed column already exists")

        # 2. Add billing_date column if it doesn't exist
        if 'billing_date' not in columns:
            print("Adding billing_date column to time_entries table...")
            cursor.execute('''
                           ALTER TABLE time_entries
                               ADD COLUMN billing_date TEXT
                           ''')
            print("✓ Added billing_date column")
        else:
            print("✓ billing_date column already exists")

        # 3. Add invoice_number column if it doesn't exist
        if 'invoice_number' not in columns:
            print("Adding invoice_number column to time_entries table...")
            cursor.execute('''
                           ALTER TABLE time_entries
                               ADD COLUMN invoice_number TEXT
                           ''')
            print("✓ Added invoice_number column")
        else:
            print("✓ invoice_number column already exists")

        # 4. Create billing_history table if it doesn't exist
        print("Creating billing_history table...")
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS billing_history
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           invoice_number
                           TEXT
                           UNIQUE
                           NOT
                           NULL,
                           client_id
                           INTEGER
                           NOT
                           NULL,
                           client_name
                           TEXT
                           NOT
                           NULL,
                           invoice_date
                           TEXT
                           NOT
                           NULL,
                           period_start
                           TEXT
                           NOT
                           NULL,
                           period_end
                           TEXT
                           NOT
                           NULL,
                           total_amount
                           REAL
                           NOT
                           NULL,
                           total_hours
                           REAL
                           NOT
                           NULL,
                           invoice_items
                           TEXT
                           NOT
                           NULL,
                           pdf_path
                           TEXT,
                           created_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP,
                           FOREIGN
                           KEY
                       (
                           client_id
                       ) REFERENCES clients
                       (
                           id
                       )
                           )
                       ''')
        print("✓ billing_history table ready")

        # 5. Create billing_entry_link table for many-to-many relationship
        print("Creating billing_entry_link table...")
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS billing_entry_link
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           invoice_number
                           TEXT
                           NOT
                           NULL,
                           time_entry_id
                           INTEGER
                           NOT
                           NULL,
                           created_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP,
                           FOREIGN
                           KEY
                       (
                           time_entry_id
                       ) REFERENCES time_entries
                       (
                           id
                       ),
                           UNIQUE
                       (
                           invoice_number,
                           time_entry_id
                       )
                           )
                       ''')
        print("✓ billing_entry_link table ready")

        # Create index for performance
        print("Creating indexes...")
        cursor.execute('''
                       CREATE INDEX IF NOT EXISTS idx_time_entries_billed
                           ON time_entries(is_billed)
                       ''')
        cursor.execute('''
                       CREATE INDEX IF NOT EXISTS idx_billing_history_client
                           ON billing_history(client_id)
                       ''')
        cursor.execute('''
                       CREATE INDEX IF NOT EXISTS idx_billing_entry_link_invoice
                           ON billing_entry_link(invoice_number)
                       ''')
        print("✓ Indexes created")

        # Commit changes
        conn.commit()

        print()
        print("=" * 50)
        print("Migration completed successfully!")
        print("=" * 50)

        # Display summary
        cursor.execute("SELECT COUNT(*) FROM time_entries WHERE is_billed = 0 OR is_billed IS NULL")
        unbilled = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM time_entries WHERE is_billed = 1")
        billed = cursor.fetchone()[0]

        print()
        print("Summary:")
        print(f"  Unbilled entries: {unbilled}")
        print(f"  Billed entries: {billed}")

        conn.close()
        return True

    except Exception as e:
        print(f"ERROR: Migration failed - {e}")
        return False


def backup_database(db_path="data/time_tracker.db"):
    """Create backup before migration"""
    from shutil import copy2
    import os

    if os.path.exists(db_path):
        backup_path = db_path + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"Creating backup: {backup_path}")
        copy2(db_path, backup_path)
        print("✓ Backup created")
        return True
    return False


if __name__ == "__main__":
    print("Starting database migration...")
    print()

    # Check if database exists
    db_path = "data/time_tracker.db"
    if not Path(db_path).exists():
        print(f"Database not found at {db_path}")
        print("Please ensure the Time Tracker app has been run at least once.")
        sys.exit(1)

    # Create backup
    if backup_database(db_path):
        # Run migration
        if migrate_database(db_path):
            print("\nMigration successful! You can now run the Time Tracker app.")
        else:
            print("\nMigration failed. The database backup has been preserved.")
            sys.exit(1)
    else:
        print("Could not create backup. Migration aborted.")
        sys.exit(1)
