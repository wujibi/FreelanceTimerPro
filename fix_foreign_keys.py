"""Fix foreign key constraints issue"""
import sqlite3


def fix_database():
    conn = sqlite3.connect("data/time_tracker.db")
    cursor = conn.cursor()

    # Temporarily disable foreign keys
    conn.execute("PRAGMA foreign_keys = OFF")

    # Check and recreate tasks table with proper constraints
    cursor.execute("PRAGMA table_info(tasks)")
    existing_columns = cursor.fetchall()

    # Backup existing tasks data
    cursor.execute("SELECT * FROM tasks")
    tasks_data = cursor.fetchall()

    # Drop and recreate tasks table with correct schema
    cursor.execute("DROP TABLE IF EXISTS tasks_temp")
    cursor.execute("""
                   CREATE TABLE tasks_temp
                   (
                       id              INTEGER PRIMARY KEY AUTOINCREMENT,
                       project_id      INTEGER NOT NULL,
                       name            TEXT    NOT NULL,
                       description     TEXT,
                       hourly_rate     REAL      DEFAULT 0,
                       is_lump_sum     INTEGER   DEFAULT 0,
                       lump_sum_amount REAL      DEFAULT 0,
                       created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                       FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
                   )
                   """)

    # Restore data if any
    if tasks_data:
        for task in tasks_data:
            cursor.execute("""
                           INSERT INTO tasks_temp (id, project_id, name, description,
                                                   hourly_rate, is_lump_sum, lump_sum_amount)
                           VALUES (?, ?, ?, ?, ?, ?, ?)
                           """, task[:7])

    # Replace old table
    cursor.execute("DROP TABLE IF EXISTS tasks")
    cursor.execute("ALTER TABLE tasks_temp RENAME TO tasks")

    # Re-enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON")
    conn.commit()

    print("Fixed foreign key constraints")

    # Verify
    cursor.execute("PRAGMA foreign_key_check")
    issues = cursor.fetchall()
    if issues:
        print(f"Warning: Foreign key issues remain: {issues}")
    else:
        print("✓ All foreign key constraints valid")

    conn.close()


if __name__ == "__main__":
    fix_database()
