"""
Migration script to add payment_terms and thank_you_message fields to company_info table
Run this once to update your database schema
"""
import sqlite3
from pathlib import Path

# Database path - update if needed
DB_PATH = Path.home() / "My Drive" / "TimeTrackerApp" / "data" / "time_tracker.db"

# Alternative path for laptop
if not DB_PATH.exists():
    DB_PATH = Path("G:/My Drive/TimeTrackerApp/data/time_tracker.db")

if not DB_PATH.exists():
    DB_PATH = Path("data/time_tracker.db")

print(f"Updating database at: {DB_PATH}")

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check current columns
    cursor.execute("PRAGMA table_info(company_info)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"Current columns: {columns}")
    
    # Add payment_terms if missing
    if 'payment_terms' not in columns:
        cursor.execute("ALTER TABLE company_info ADD COLUMN payment_terms TEXT DEFAULT 'Payment is due within 30 days'")
        print("✓ Added payment_terms column")
    else:
        print("✓ payment_terms column already exists")
    
    # Add thank_you_message if missing
    if 'thank_you_message' not in columns:
        cursor.execute("ALTER TABLE company_info ADD COLUMN thank_you_message TEXT DEFAULT 'Thank you for your business!'")
        print("✓ Added thank_you_message column")
    else:
        print("✓ thank_you_message column already exists")
    
    conn.commit()
    
    # Show updated schema
    cursor.execute("PRAGMA table_info(company_info)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"\nUpdated columns: {columns}")
    
    conn.close()
    print("\n✅ Database migration completed successfully!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
