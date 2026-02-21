"""Test CASCADE delete functionality"""
import sqlite3
import os
from db_manager import DatabaseManager
from models import Client, Project, Task

# Database path
db_path = r"C:\Users\briah\My Drive\TimeTrackerApp\data\time_tracker.db"

print("=" * 70)
print("CASCADE DELETE TEST")
print("=" * 70)
print()
print("⚠️  WARNING: This test will CREATE and DELETE real data!")
print("⚠️  Make sure you have a backup if needed.")
print()

# Initialize
db = DatabaseManager(db_path)
client_model = Client(db)
project_model = Project(db)
task_model = Task(db)

# Step 1: Create test data
print("STEP 1: Creating test data...")
print("-" * 70)

# Create test client
client_model.create("TEST_CLIENT_CASCADE", "Test Company", "test@test.com", "555-0000", "Test Address")
clients = client_model.get_all()
test_client = [c for c in clients if c[1] == "TEST_CLIENT_CASCADE"][0]
client_id = test_client[0]
print(f"✅ Created client: TEST_CLIENT_CASCADE (ID: {client_id})")

# Create test project
project_model.create(client_id, "TEST_PROJECT_CASCADE", "Test project", 100.0, False, 0)
projects = project_model.get_all()
test_project = [p for p in projects if p[2] == "TEST_PROJECT_CASCADE"][0]
project_id = test_project[0]
print(f"✅ Created project: TEST_PROJECT_CASCADE (ID: {project_id})")

# Create test task
task_model.create("TEST_TASK_CASCADE", "Test task", 50.0, False, 0, project_id, False)
tasks = task_model.get_all()
test_task = [t for t in tasks if t[2] == "TEST_TASK_CASCADE"][0]
task_id = test_task[0]
print(f"✅ Created task: TEST_TASK_CASCADE (ID: {task_id})")

print()

# Step 2: Verify data exists
print("STEP 2: Verifying data exists...")
print("-" * 70)

with db.get_connection() as conn:
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM clients WHERE id = ?", (client_id,))
    client_count = cursor.fetchone()[0]
    print(f"Clients with ID {client_id}: {client_count}")
    
    cursor.execute("SELECT COUNT(*) FROM projects WHERE id = ?", (project_id,))
    project_count = cursor.fetchone()[0]
    print(f"Projects with ID {project_id}: {project_count}")
    
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE id = ?", (task_id,))
    task_count = cursor.fetchone()[0]
    print(f"Tasks with ID {task_id}: {task_count}")

print()

# Step 3: Delete the project (should CASCADE to task)
print("STEP 3: Deleting project (should cascade to task)...")
print("-" * 70)
project_model.delete(project_id)
print(f"✅ Deleted project ID {project_id}")

print()

# Step 4: Check if task was deleted by CASCADE
print("STEP 4: Checking if task was deleted...")
print("-" * 70)

with db.get_connection() as conn:
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM projects WHERE id = ?", (project_id,))
    project_count = cursor.fetchone()[0]
    print(f"Projects with ID {project_id}: {project_count} (should be 0)")
    
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE id = ?", (task_id,))
    task_count = cursor.fetchone()[0]
    print(f"Tasks with ID {task_id}: {task_count} (should be 0)")
    
    if project_count == 0 and task_count == 0:
        print("✅ SUCCESS! Project and task both deleted (CASCADE worked!)")
    elif project_count == 0 and task_count > 0:
        print("❌ FAILURE! Project deleted but task still exists (CASCADE failed)")
    else:
        print("❌ UNEXPECTED! Check database manually")

print()

# Step 5: Delete the client (should CASCADE to any remaining data)
print("STEP 5: Cleaning up - deleting test client...")
print("-" * 70)
client_model.delete(client_id)
print(f"✅ Deleted client ID {client_id}")

print()

# Step 6: Final verification
print("STEP 6: Final verification - all test data should be gone...")
print("-" * 70)

with db.get_connection() as conn:
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM clients WHERE id = ?", (client_id,))
    client_count = cursor.fetchone()[0]
    print(f"Clients with ID {client_id}: {client_count} (should be 0)")
    
    cursor.execute("SELECT COUNT(*) FROM projects WHERE client_id = ?", (client_id,))
    project_count = cursor.fetchone()[0]
    print(f"Projects for client {client_id}: {project_count} (should be 0)")
    
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE project_id = ?", (project_id,))
    task_count = cursor.fetchone()[0]
    print(f"Tasks for project {project_id}: {task_count} (should be 0)")
    
    if client_count == 0 and project_count == 0 and task_count == 0:
        print("✅ SUCCESS! All test data cleaned up via CASCADE!")
    else:
        print("❌ FAILURE! Some test data remains (CASCADE not working fully)")

print()
print("=" * 70)
print("TEST COMPLETE")
print("=" * 70)
