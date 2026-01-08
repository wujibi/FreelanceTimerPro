"""
Database Migration Script: Add Payment Tracking to Billing History
Adds is_paid and date_paid columns to billing_history table
"""
import sqlite3
import sys
from pathlib import Path

def migrate_database(db_path):
    """Add payment tracking columns to billing_history table"""
    
    print(f"Connecting to database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(billing_history)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"Current billing_history columns: {columns}")
        
        # Add is_paid column if missing
        if 'is_paid' not in columns:
            print("Adding 'is_paid' column...")
            cursor.execute('''
                ALTER TABLE billing_history 
                ADD COLUMN is_paid INTEGER DEFAULT 0
            ''')
            print("✓ Added 'is_paid' column")
        else:
            print("✓ 'is_paid' column already exists")
        
        # Add date_paid column if missing
        if 'date_paid' not in columns:
            print("Adding 'date_paid' column...")
            cursor.execute('''
                ALTER TABLE billing_history 
                ADD COLUMN date_paid TEXT
            ''')
            print("✓ Added 'date_paid' column")
        else:
            print("✓ 'date_paid' column already exists")
        
        conn.commit()
        
        # Verify changes
        cursor.execute("PRAGMA table_info(billing_history)")
        new_columns = [column[1] for column in cursor.fetchall()]
        print(f"\nUpdated billing_history columns: {new_columns}")
        
        conn.close()
        print("\n✅ Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    # Try multiple common database paths
    possible_paths = [
        Path.home() / "My Drive" / "TimeTrackerApp" / "data" / "time_tracker.db",
        Path("C:/Users/briah/My Drive/TimeTrackerApp/data/time_tracker.db"),
        Path.home() / "Google Drive" / "TimeTrackerApp" / "data" / "time_tracker.db",
        Path("data") / "time_tracker.db",
    ]
    
    db_path = None
    for path in possible_paths:
        if path.exists():
            db_path = str(path)
            print(f"Found database at: {db_path}")
            break
    
    if db_path is None:
        print("ERROR: Could not find database file!")
        print("Searched paths:")
        for path in possible_paths:
            print(f"  - {path}")
        sys.exit(1)
    
    success = migrate_database(db_path)
    
    if not success:
        sys.exit(1)
