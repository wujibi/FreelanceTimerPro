"""Test if database persists between app restarts"""
import sqlite3
import os

db_path = "data/time_tracker.db"

print(f"Checking database at: {os.path.abspath(db_path)}")
print(f"Database exists: {os.path.exists(db_path)}")

if os.path.exists(db_path):
    print(f"Database size: {os.path.getsize(db_path)} bytes")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check for data
    cursor.execute("SELECT COUNT(*) FROM clients")
    client_count = cursor.fetchone()[0]
    print(f"Clients in database: {client_count}")

    cursor.execute("SELECT COUNT(*) FROM projects")
    project_count = cursor.fetchone()[0]
    print(f"Projects in database: {project_count}")

    cursor.execute("SELECT COUNT(*) FROM tasks")
    task_count = cursor.fetchone()[0]
    print(f"Tasks in database: {task_count}")

    cursor.execute("SELECT COUNT(*) FROM time_entries")
    entry_count = cursor.fetchone()[0]
    print(f"Time entries in database: {entry_count}")

    if client_count > 0:
        print("\nClients:")
        cursor.execute("SELECT id, name FROM clients")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]}")

    conn.close()
else:
    print("Database file does not exist!")
