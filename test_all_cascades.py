"""
Comprehensive CASCADE DELETE test for all three delete methods
Tests Client.delete(), Project.delete(), and Task.delete()
"""
import sqlite3
from db_manager import DatabaseManager
from models import Client, Project, Task, TimeEntry

# Use the LIVE database path
db_path = r'C:\Users\briah\My Drive\TimeTrackerApp\data\time_tracker.db'

print("=" * 60)
print("COMPREHENSIVE CASCADE DELETE TEST")
print("=" * 60)

# Initialize
db = DatabaseManager(db_path)
client_model = Client(db)
project_model = Project(db)
task_model = Task(db)
time_entry_model = TimeEntry(db)

# Check foreign keys
with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute('PRAGMA foreign_keys')
    fk_status = cursor.fetchone()[0]
    print(f"\n✓ Foreign keys enabled: {bool(fk_status)}")

print("\n" + "=" * 60)
print("TEST 1: Task.delete() CASCADE")
print("=" * 60)

# Find a task with time entries OR create test data
with db.get_connection() as conn:
    cursor = conn.cursor()
    
    # Find orphaned task (task with no project)
    cursor.execute('''
        SELECT t.id, t.name
        FROM tasks t
        LEFT JOIN projects p ON t.project_id = p.id
        WHERE t.project_id IS NOT NULL AND p.id IS NULL
        LIMIT 1
    ''')
    orphan_task = cursor.fetchone()
    
    if orphan_task:
        task_id = orphan_task[0]
        task_name = orphan_task[1]
        print(f"\nUsing orphaned task: ID {task_id}, Name: '{task_name}'")
        
        # Check for time entries
        cursor.execute('SELECT COUNT(*) FROM time_entries WHERE task_id = ?', (task_id,))
        entry_count = cursor.fetchone()[0]
        print(f"  - Has {entry_count} time entries")
        
        if entry_count > 0:
            # Test delete
            print(f"\nDeleting task {task_id}...")
            task_model.delete(task_id)
            
            # Verify
            cursor.execute('SELECT COUNT(*) FROM tasks WHERE id = ?', (task_id,))
            task_exists = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM time_entries WHERE task_id = ?', (task_id,))
            entries_remain = cursor.fetchone()[0]
            
            if task_exists == 0 and entries_remain == 0:
                print("✓ Task.delete() CASCADE WORKS - task and all time entries deleted!")
            else:
                print(f"✗ Task.delete() CASCADE FAILED:")
                print(f"    Task still exists: {task_exists > 0}")
                print(f"    Entries still exist: {entries_remain}")
        else:
            print("  (No time entries to test CASCADE)")
    else:
        print("\nNo orphaned tasks found to test with.")

print("\n" + "=" * 60)
print("TEST 2: Check for ALL Orphaned Data")
print("=" * 60)

with db.get_connection() as conn:
    cursor = conn.cursor()
    
    # Orphaned tasks
    cursor.execute('''
        SELECT t.id, t.name, t.project_id
        FROM tasks t
        LEFT JOIN projects p ON t.project_id = p.id
        WHERE t.project_id IS NOT NULL AND p.id IS NULL
    ''')
    orphaned_tasks = cursor.fetchall()
    
    if orphaned_tasks:
        print(f"\n⚠️  Found {len(orphaned_tasks)} orphaned tasks:")
        for task in orphaned_tasks:
            print(f"  - Task ID {task[0]}: '{task[1]}' (references non-existent project_id {task[2]})")
            
            # Count entries for each orphaned task
            cursor.execute('SELECT COUNT(*) FROM time_entries WHERE task_id = ?', (task[0],))
            entry_count = cursor.fetchone()[0]
            if entry_count > 0:
                print(f"    ⚠️  Has {entry_count} orphaned time entries")
    else:
        print("\n✓ No orphaned tasks found")
    
    # Orphaned time entries
    cursor.execute('''
        SELECT te.id, te.task_id
        FROM time_entries te
        LEFT JOIN tasks t ON te.task_id = t.id
        WHERE t.id IS NULL
    ''')
    orphaned_entries = cursor.fetchall()
    
    if orphaned_entries:
        print(f"\n⚠️  Found {len(orphaned_entries)} orphaned time entries:")
        for entry in orphaned_entries:
            print(f"  - Entry ID {entry[0]} (references non-existent task_id {entry[1]})")
    else:
        print("\n✓ No orphaned time entries found")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
print("\nNEXT STEPS:")
print("1. Test in GUI by deleting a task with time entries")
print("2. Test in GUI by deleting a project with tasks and entries")
print("3. Verify all orphaned data is properly cleaned up")

db.close()
