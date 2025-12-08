"""Fix time_entries table structure"""
import sqlite3


def fix_time_entries_table():
    conn = sqlite3.connect("data/time_tracker.db")
    cursor = conn.cursor()

    print("Checking time_entries table structure...")
    cursor.execute("PRAGMA table_info(time_entries)")
    columns = {col[1]: col[2] for col in cursor.fetchall()}
    print(f"Current columns: {list(columns.keys())}")

    # Add missing columns
    missing_columns = {
        'duration_minutes': 'INTEGER DEFAULT 0',
        'is_manual': 'INTEGER DEFAULT 0',
        'description': 'TEXT'
    }

    for col_name, col_type in missing_columns.items():
        if col_name not in columns:
            print(f"Adding column: {col_name}")
            cursor.execute(f"ALTER TABLE time_entries ADD COLUMN {col_name} {col_type}")
            print(f"✓ Added {col_name}")
        else:
            print(f"✓ Column {col_name} already exists")

    conn.commit()

    # Verify the structure
    print("\nUpdated time_entries structure:")
    cursor.execute("PRAGMA table_info(time_entries)")
    for col in cursor.fetchall():
        print(f"  {col[1]}: {col[2]}")

    conn.close()
    print("\n✓ time_entries table fixed!")


if __name__ == "__main__":
    fix_time_entries_table()
