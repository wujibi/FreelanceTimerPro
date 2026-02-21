"""
Test Project.delete() method with real database
This will show us exactly what's happening when Project 67 is deleted
"""
import sqlite3
from db_manager import DatabaseManager
from models import Project

# Use the LIVE database path
db_path = r'C:\Users\briah\My Drive\TimeTrackerApp\data\time_tracker.db'

# Connect and verify foreign keys
print("=" * 60)
print("Testing Project.delete() method")
print("=" * 60)

# Initialize database manager
db = DatabaseManager(db_path)
project_model = Project(db)

# Check foreign keys status
with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute('PRAGMA foreign_keys')
    fk_status = cursor.fetchone()[0]
    print(f"\n✓ Foreign keys enabled: {bool(fk_status)}")

# Find Project 67 or any test project
print("\nLooking for Project 67...")
with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM projects WHERE id = 67')
    project = cursor.fetchone()
    
    if project:
        print(f"✓ Found: Project ID {project[0]}, Name: '{project[2]}'")
        
        # Count associated tasks
        cursor.execute('SELECT COUNT(*) FROM tasks WHERE project_id = 67')
        task_count = cursor.fetchone()[0]
        print(f"  - Associated tasks: {task_count}")
        
        # Count associated time entries
        cursor.execute('''
            SELECT COUNT(*) FROM time_entries 
            WHERE task_id IN (SELECT id FROM tasks WHERE project_id = 67)
        ''')
        entry_count = cursor.fetchone()[0]
        print(f"  - Associated time entries: {entry_count}")
        
        # Show the tasks and entries
        if task_count > 0:
            cursor.execute('SELECT id, name FROM tasks WHERE project_id = 67')
            tasks = cursor.fetchall()
            print(f"\n  Tasks under Project 67:")
            for task in tasks:
                print(f"    - Task ID {task[0]}: {task[1]}")
                
                # Show entries for this task
                cursor.execute('SELECT id FROM time_entries WHERE task_id = ?', (task[0],))
                entries = cursor.fetchall()
                if entries:
                    print(f"      Time entries: {[e[0] for e in entries]}")
    else:
        print("✗ Project 67 not found")
        # Find any project with tasks and entries for testing
        cursor.execute('''
            SELECT p.id, p.name, COUNT(DISTINCT t.id), COUNT(te.id)
            FROM projects p
            LEFT JOIN tasks t ON t.project_id = p.id
            LEFT JOIN time_entries te ON te.task_id = t.id
            GROUP BY p.id
            HAVING COUNT(t.id) > 0
            LIMIT 1
        ''')
        test_project = cursor.fetchone()
        if test_project:
            print(f"\nFound test project: ID {test_project[0]}, Name: '{test_project[1]}'")
            print(f"  - Tasks: {test_project[2]}, Entries: {test_project[3]}")
            print(f"\nTo test, delete this project from the GUI and check if data remains.")

print("\n" + "=" * 60)
print("IMPORTANT: Do NOT delete anything in this script")
print("This is just a diagnostic to understand the data structure")
print("=" * 60)

db.close()
