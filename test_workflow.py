"""Test basic workflow - Client -> Project -> Task"""
import sqlite3
from datetime import datetime


def test_workflow():
    conn = sqlite3.connect("data/time_tracker.db")
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    try:
        # 1. Create test client
        cursor.execute("""
                       INSERT INTO clients (name, company, email)
                       VALUES ('Test Client', 'Test Company', 'test@example.com')
                       """)
        client_id = cursor.lastrowid
        print(f"✓ Created client ID: {client_id}")

        # 2. Create test project
        cursor.execute("""
                       INSERT INTO projects (client_id, name, description, hourly_rate)
                       VALUES (?, 'Test Project', 'Test Description', 100.00)
                       """, (client_id,))
        project_id = cursor.lastrowid
        print(f"✓ Created project ID: {project_id}")

        # 3. Create test task
        cursor.execute("""
                       INSERT INTO tasks (project_id, name, description, hourly_rate)
                       VALUES (?, 'Test Task', 'Test Task Description', 75.00)
                       """, (project_id,))
        task_id = cursor.lastrowid
        print(f"✓ Created task ID: {task_id}")

        # 4. Create test time entry
        cursor.execute("""
                       INSERT INTO time_entries (task_id, start_time, end_time, duration_minutes, is_manual, is_billed)
                       VALUES (?, ?, ?, 120, 1, 0)
                       """, (task_id, datetime.now().isoformat(), datetime.now().isoformat()))
        entry_id = cursor.lastrowid
        print(f"✓ Created time entry ID: {entry_id}")

        conn.commit()
        print("\n✓ All test data created successfully!")
        print("You should now see this test data in the app.")

    except Exception as e:
        print(f"✗ Error: {e}")
        conn.rollback()

        # Check what's in the tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"\nExisting tables: {[t[0] for t in tables]}")

        # Check projects table structure
        cursor.execute("PRAGMA table_info(projects)")
        print("\nProjects table structure:")
        for col in cursor.fetchall():
            print(f"  {col}")

    finally:
        conn.close()


if __name__ == "__main__":
    test_workflow()
