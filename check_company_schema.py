"""
Check the company_info table schema and data
"""
import sqlite3
from pathlib import Path

# Database path
DB_PATH = Path.home() / "My Drive" / "TimeTrackerApp" / "data" / "time_tracker.db"

# Alternative path for laptop
if not DB_PATH.exists():
    DB_PATH = Path("G:/My Drive/TimeTrackerApp/data/time_tracker.db")

if not DB_PATH.exists():
    DB_PATH = Path("data/time_tracker.db")

print(f"Checking database at: {DB_PATH}\n")

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get schema with column positions
    cursor.execute("PRAGMA table_info(company_info)")
    columns = cursor.fetchall()
    
    print("=" * 60)
    print("COMPANY_INFO TABLE SCHEMA:")
    print("=" * 60)
    for col in columns:
        print(f"Position {col[0]}: {col[1]} ({col[2]}) - Default: {col[4]}")
    
    print("\n" + "=" * 60)
    print("CURRENT DATA IN COMPANY_INFO:")
    print("=" * 60)
    
    # Get all data
    cursor.execute("SELECT * FROM company_info")
    row = cursor.fetchone()
    
    if row:
        for i, col_info in enumerate(columns):
            col_name = col_info[1]
            value = row[i] if i < len(row) else "N/A"
            print(f"{col_name}: {value}")
    else:
        print("No data found")
    
    conn.close()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
