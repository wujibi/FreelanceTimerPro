"""Test if foreign keys are enabled in the database"""
import sqlite3
import os

# Get database path
db_path = r"C:\Users\briah\My Drive\TimeTrackerApp\data\time_tracker.db"

print(f"Testing database: {db_path}")
print(f"File exists: {os.path.exists(db_path)}")
print()

# Test with db_manager (should work)
print("=" * 60)
print("TEST 1: Using db_manager.py (SHOULD have foreign keys ON)")
print("=" * 60)
from db_manager import DatabaseManager
db = DatabaseManager(db_path)
with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys")
    result = cursor.fetchone()
    print(f"Foreign keys: {result}")
    if result[0] == 1:
        print("✅ Foreign keys are ENABLED via db_manager")
    else:
        print("❌ Foreign keys are DISABLED via db_manager")

print()

# Test direct connection (mimics gui.py theme methods BEFORE our fix)
print("=" * 60)
print("TEST 2: Direct sqlite3.connect() WITHOUT pragma (OLD gui.py)")
print("=" * 60)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys")
result = cursor.fetchone()
print(f"Foreign keys: {result}")
if result[0] == 1:
    print("✅ Foreign keys are ENABLED")
else:
    print("❌ Foreign keys are DISABLED - this is why CASCADE failed!")
conn.close()

print()

# Test direct connection WITH pragma (AFTER our fix)
print("=" * 60)
print("TEST 3: Direct sqlite3.connect() WITH pragma (FIXED gui.py)")
print("=" * 60)
conn = sqlite3.connect(db_path)
conn.execute("PRAGMA foreign_keys = ON")  # THIS IS THE FIX
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys")
result = cursor.fetchone()
print(f"Foreign keys: {result}")
if result[0] == 1:
    print("✅ Foreign keys are ENABLED with our fix")
else:
    print("❌ Foreign keys are STILL DISABLED (shouldn't happen)")
conn.close()

print()
print("=" * 60)
print("SUMMARY:")
print("=" * 60)
print("If TEST 2 shows (0,) and TEST 3 shows (1,), the fix works!")
print("Every sqlite3.connect() call MUST include: conn.execute('PRAGMA foreign_keys = ON')")
