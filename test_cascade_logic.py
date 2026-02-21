"""
Test the CASCADE DELETE logic step by step
This will help us understand why manual CASCADE isn't working
"""
import sqlite3
from db_manager import DatabaseManager

# Use the LIVE database path
db_path = r'C:\Users\briah\My Drive\TimeTrackerApp\data\time_tracker.db'

print("=" * 60)
print("Testing CASCADE DELETE Logic")
print("=" * 60)

# Initialize database manager
db = DatabaseManager(db_path)

# Use Project 3 for testing (has 1 task, 0 entries)
project_id = 3

print(f"\nTesting with Project ID: {project_id}")

with db.get_connection() as conn:
    cursor = conn.cursor()
    
    # Check foreign keys
    cursor.execute('PRAGMA foreign_keys')
    fk_status = cursor.fetchone()[0]
    print(f"Foreign keys enabled: {bool(fk_status)}")
    
    # Get project info
    cursor.execute('SELECT id, name FROM projects WHERE id = ?', (project_id,))
    project = cursor.fetchone()
    if not project:
        print(f"\n✗ Project {project_id} not found!")
        db.close()
        exit(1)
    
    print(f"\n✓ Project: ID {project[0]}, Name: '{project[1]}'")
    
    # Find tasks for this project
    cursor.execute('SELECT id, name FROM tasks WHERE project_id = ?', (project_id,))
    tasks = cursor.fetchall()
    print(f"  - Tasks: {len(tasks)}")
    if tasks:
        for task in tasks:
            print(f"    Task ID {task[0]}: {task[1]}")
            
            # Find time entries for each task
            cursor.execute('SELECT id FROM time_entries WHERE task_id = ?', (task[0],))
            entries = cursor.fetchall()
            if entries:
                print(f"      Time entries: {[e[0] for e in entries]}")
    
    # Now test the DELETE queries that Project.delete() uses
    print("\n" + "-" * 60)
    print("Testing DELETE queries (DRY RUN - no actual deletion)")
    print("-" * 60)
    
    # Query 1: Find time entries to delete
    print("\nQuery 1: Find time entries for tasks under this project")
    cursor.execute('''
        SELECT id FROM time_entries 
        WHERE task_id IN (
            SELECT id FROM tasks WHERE project_id = ?
        )
    ''', (project_id,))
    entries_to_delete = cursor.fetchall()
    print(f"  Would delete {len(entries_to_delete)} time entries: {[e[0] for e in entries_to_delete]}")
    
    # Query 2: Find tasks to delete
    print("\nQuery 2: Find tasks for this project")
    cursor.execute('SELECT id, name FROM tasks WHERE project_id = ?', (project_id,))
    tasks_to_delete = cursor.fetchall()
    print(f"  Would delete {len(tasks_to_delete)} tasks:")
    for task in tasks_to_delete:
        print(f"    - Task ID {task[0]}: {task[1]}")
    
    # Query 3: The project itself
    print("\nQuery 3: The project itself")
    print(f"  Would delete project ID {project_id}")
    
    print("\n" + "-" * 60)
    print("Now let's look for orphaned data (tasks/entries with no project)")
    print("-" * 60)
    
    # Find tasks with no project (project_id doesn't exist in projects table)
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
            
            # Find time entries for these orphaned tasks
            cursor.execute('SELECT id FROM time_entries WHERE task_id = ?', (task[0],))
            orphan_entries = cursor.fetchall()
            if orphan_entries:
                print(f"    ⚠️  Has {len(orphan_entries)} time entries: {[e[0] for e in orphan_entries]}")
    else:
        print("\n✓ No orphaned tasks found")
    
    # Find time entries with invalid task_id
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
print("Diagnostic complete - no data was modified")
print("=" * 60)

db.close()
