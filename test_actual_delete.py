"""
Test actual Project.delete() execution with error trapping
This will show us if exceptions are being raised and swallowed
"""
import sqlite3
from db_manager import DatabaseManager
from models import Project

# Use the LIVE database path
db_path = r'C:\Users\briah\My Drive\TimeTrackerApp\data\time_tracker.db'

print("=" * 60)
print("Testing ACTUAL Project.delete() Execution")
print("=" * 60)

# Initialize database manager
db = DatabaseManager(db_path)
project_model = Project(db)

# Use Project 3 (has 1 task, 0 entries)
project_id = 3

print(f"\nPreparing to test delete on Project ID: {project_id}")

# BEFORE: Check what exists
print("\n--- BEFORE DELETE ---")
with db.get_connection() as conn:
    cursor = conn.cursor()
    
    # Check project
    cursor.execute('SELECT id, name FROM projects WHERE id = ?', (project_id,))
    project = cursor.fetchone()
    if project:
        print(f"✓ Project exists: ID {project[0]}, Name: '{project[1]}'")
    else:
        print(f"✗ Project {project_id} not found")
        db.close()
        exit(1)
    
    # Check tasks
    cursor.execute('SELECT id, name FROM tasks WHERE project_id = ?', (project_id,))
    tasks = cursor.fetchall()
    print(f"  Tasks: {len(tasks)}")
    for task in tasks:
        print(f"    - Task ID {task[0]}: {task[1]}")
        
        # Check time entries
        cursor.execute('SELECT id FROM time_entries WHERE task_id = ?', (task[0],))
        entries = cursor.fetchall()
        if entries:
            print(f"      Time entries: {[e[0] for e in entries]}")

print("\n--- EXECUTING DELETE ---")

try:
    # This is what the GUI calls
    project_model.delete(project_id)
    print("✓ project_model.delete() completed without exception")
except Exception as e:
    print(f"✗ Exception caught: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# AFTER: Check what remains
print("\n--- AFTER DELETE ---")
with db.get_connection() as conn:
    cursor = conn.cursor()
    
    # Check project
    cursor.execute('SELECT id, name FROM projects WHERE id = ?', (project_id,))
    project = cursor.fetchone()
    if project:
        print(f"⚠️  Project STILL EXISTS: ID {project[0]}, Name: '{project[1]}'")
    else:
        print(f"✓ Project deleted successfully")
    
    # Check tasks
    cursor.execute('SELECT id, name FROM tasks WHERE project_id = ?', (project_id,))
    tasks = cursor.fetchall()
    if tasks:
        print(f"⚠️  {len(tasks)} tasks STILL EXIST:")
        for task in tasks:
            print(f"    - Task ID {task[0]}: {task[1]}")
            
            # Check time entries
            cursor.execute('SELECT id FROM time_entries WHERE task_id = ?', (task[0],))
            entries = cursor.fetchall()
            if entries:
                print(f"      ⚠️  {len(entries)} time entries STILL EXIST: {[e[0] for e in entries]}")
    else:
        print(f"✓ Tasks deleted successfully")

print("\n" + "=" * 60)
print("Test complete")
print("=" * 60)

db.close()
