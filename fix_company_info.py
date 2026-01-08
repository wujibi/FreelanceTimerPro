"""
Fix company_info table - ensure columns are in correct order and set proper defaults
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

print(f"Fixing database at: {DB_PATH}\n")

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # First, check current schema
    cursor.execute("PRAGMA table_info(company_info)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"Current columns: {columns}\n")
    
    # Get existing data
    cursor.execute("SELECT id, name, address, phone, email, logo_path, website FROM company_info WHERE id = 1")
    existing_data = cursor.fetchone()
    
    if existing_data:
        print(f"Found existing company data:")
        print(f"  Name: {existing_data[1]}")
        print(f"  Email: {existing_data[4]}")
        print(f"  Logo: {existing_data[5]}")
        print(f"  Website: {existing_data[6] if len(existing_data) > 6 else 'None'}")
    
    # Drop the old table
    print("\nDropping old company_info table...")
    cursor.execute("DROP TABLE IF EXISTS company_info")
    
    # Create new table with correct schema
    print("Creating new company_info table with correct schema...")
    cursor.execute('''
        CREATE TABLE company_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT,
            phone TEXT,
            email TEXT,
            logo_path TEXT,
            website TEXT,
            payment_terms TEXT DEFAULT 'Payment is due within 30 days',
            thank_you_message TEXT DEFAULT 'Thank you for your business!',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Re-insert the data if it existed
    if existing_data:
        print("Restoring company data with proper defaults...")
        cursor.execute('''
            INSERT INTO company_info 
            (id, name, address, phone, email, logo_path, website, payment_terms, thank_you_message)
            VALUES (1, ?, ?, ?, ?, ?, ?, 'Payment is due within 30 days', 'Thank you for your business!')
        ''', (
            existing_data[1],  # name
            existing_data[2],  # address
            existing_data[3],  # phone
            existing_data[4],  # email
            existing_data[5],  # logo_path
            existing_data[6] if len(existing_data) > 6 else None  # website
        ))
    else:
        print("No existing data, creating default entry...")
        cursor.execute('''
            INSERT INTO company_info 
            (name, address, phone, email, payment_terms, thank_you_message)
            VALUES ('Your Company Name', 'Your Address', 'Your Phone', 'your-email@example.com',
                    'Payment is due within 30 days', 'Thank you for your business!')
        ''')
    
    conn.commit()
    
    # Verify the fix
    print("\n" + "=" * 60)
    print("VERIFICATION - NEW SCHEMA:")
    print("=" * 60)
    cursor.execute("PRAGMA table_info(company_info)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"Position {col[0]}: {col[1]} ({col[2]})")
    
    print("\n" + "=" * 60)
    print("VERIFICATION - DATA:")
    print("=" * 60)
    cursor.execute("SELECT * FROM company_info WHERE id = 1")
    row = cursor.fetchone()
    
    if row:
        column_names = [col[1] for col in columns]
        for i, col_name in enumerate(column_names):
            value = row[i] if i < len(row) else "N/A"
            print(f"{col_name}: {value}")
    
    conn.close()
    
    print("\n✅ Database fixed successfully!")
    print("\nNow restart your app and:")
    print("1. Go to Company Info tab")
    print("2. Click 'Load Current Info' to refresh the fields")
    print("3. Edit Payment Terms and Thank You Message")
    print("4. Click 'Save Company Info'")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
