"""
Database Manager for Time Tracking App
Handles all database operations including time entries, clients, projects, and billing
"""
import os
import sqlite3

from datetime import datetime, timedelta
from pathlib import Path
from contextlib import contextmanager


class DatabaseManager:
    # In database.py __init__ method
    def __init__(self, db_path="data/time_tracker.db"):
        """Initialize database manager and create data directory if needed"""
        # Convert to absolute path based on script location
        if not os.path.isabs(db_path):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(script_dir, db_path)

        self.db_path = db_path

        # Create data directory if it doesn't exist
        data_dir = Path(db_path).parent
        data_dir.mkdir(exist_ok=True)

        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.execute("PRAGMA foreign_keys = ON")

        # Comprehensive database setup
        self.setup_database()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        yield self.conn

    def setup_database(self):
        """Comprehensive database setup with validation and migration"""
        print("Setting up database...")

        # Check if database is new or existing
        db_is_new = not os.path.exists(self.db_path) or os.path.getsize(self.db_path) == 0

        if db_is_new:
            print("Creating new database...")
        else:
            print(f"Using existing database at: {self.db_path}")

        # Create all base tables (uses IF NOT EXISTS, so safe)
        self.create_all_tables()

        # Validate and fix schema (only adds missing columns, doesn't drop data)
        self.validate_and_fix_schema()

        # Debug output
        self.debug_schema()

        print("Database setup complete.")

    def create_all_tables(self):
        """Create all necessary tables"""
        # Core tables
        self.create_clients_table()
        self.create_projects_table()
        self.create_tasks_table()
        self.create_time_entries_table()

        # Company and billing tables
        self.create_company_info_table()
        self.create_billing_records_table()
        self.create_billing_time_entries_table()

    def validate_and_fix_schema(self):
        """Validate and fix all table schemas"""
        print("Validating database schema...")

        # Check and fix each table
        self.fix_clients_table()
        self.fix_projects_table()
        self.fix_tasks_table()
        self.fix_time_entries_table()
        self.fix_company_info_table()
        self.fix_billing_tables()

        print("Schema validation complete.")

    def get_table_columns(self, table_name):
        """Get list of columns for a table"""
        cursor = self.conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        return [column[1] for column in cursor.fetchall()]

    def table_exists(self, table_name):
        """Check if table exists"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        return cursor.fetchone() is not None

    def add_column_if_missing(self, table_name, column_name, column_definition):
        """Add column to table if it doesn't exist"""
        columns = self.get_table_columns(table_name)
        if column_name not in columns:
            # Clean up the column definition
            clean_definition = column_definition.replace('PRIMARY KEY AUTOINCREMENT', '')
            clean_definition = clean_definition.replace('AUTOINCREMENT', '')

            try:
                query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {clean_definition}"
                self.execute_query(query)
                print(f"Added column {column_name} to {table_name}")
            except sqlite3.Error as e:
                print(f"Note: Could not add {column_name} to {table_name}: {e}")

    def debug_schema(self):
        """Print current schema for debugging"""
        tables = ['clients', 'projects', 'tasks', 'time_entries', 'billing_records']
        for table in tables:
            if self.table_exists(table):
                columns = self.get_table_columns(table)
                print(f"\n{table.upper()} columns:")
                for col in columns:
                    print(f"  - {col}")

    # Table Creation Methods
    def create_clients_table(self):
        """Create the clients table"""
        query = '''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            company TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
        self.execute_query(query)

    def create_projects_table(self):
        """Create the projects table"""
        query = '''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            hourly_rate REAL DEFAULT 0,
            is_lump_sum INTEGER DEFAULT 0,
            lump_sum_amount REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE
        )
        '''
        self.execute_query(query)

    def create_tasks_table(self):
        """Create the tasks table"""
        query = '''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            hourly_rate REAL DEFAULT 0,
            is_lump_sum INTEGER DEFAULT 0,
            lump_sum_amount REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
        '''
        self.execute_query(query)

    def create_time_entries_table(self):
        """Create the time_entries table"""
        query = '''
        CREATE TABLE IF NOT EXISTS time_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            task_name TEXT,
            project_id INTEGER,
            project_name TEXT,
            client_id INTEGER,
            client_name TEXT,
            date TEXT,
            start_time TEXT NOT NULL,
            end_time TEXT,
            duration REAL,
            duration_minutes INTEGER DEFAULT 0,
            description TEXT,
            is_manual INTEGER DEFAULT 0,
            is_billed INTEGER DEFAULT 0,
            billing_date TEXT,
            invoice_number TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE,
            FOREIGN KEY (project_id) REFERENCES projects (id),
            FOREIGN KEY (client_id) REFERENCES clients (id)
        )
        '''
        self.execute_query(query)

    def create_company_info_table(self):
        """Create the company_info table for invoice details"""
        query = '''
        CREATE TABLE IF NOT EXISTS company_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT,
            phone TEXT,
            email TEXT,
            logo_path TEXT,
            website TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
        self.execute_query(query)

        # Insert default company info if table is empty
        count_query = "SELECT COUNT(*) FROM company_info"
        result = self.fetch_one(count_query)

        if result and result[0] == 0:
            default_query = '''
            INSERT INTO company_info (name, address, phone, email)
            VALUES (?, ?, ?, ?)
            '''
            default_params = [
                "Your Company Name",
                "Your Address",
                "Your Phone",
                "your-email@example.com"
            ]
            self.execute_query(default_query, default_params)

    def create_billing_records_table(self):
        """Create table to track billing records"""
        query = '''
        CREATE TABLE IF NOT EXISTS billing_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            client_id INTEGER,
            project_name TEXT,
            project_id INTEGER,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            total_hours REAL NOT NULL,
            hourly_rate REAL NOT NULL,
            total_amount REAL NOT NULL,
            billing_date TEXT NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients (id),
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
        '''
        self.execute_query(query)

    def create_billing_time_entries_table(self):
        """Create junction table linking billing records to specific time entries"""
        query = '''
        CREATE TABLE IF NOT EXISTS billing_time_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            billing_record_id INTEGER NOT NULL,
            time_entry_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (billing_record_id) REFERENCES billing_records (id),
            FOREIGN KEY (time_entry_id) REFERENCES time_entries (id),
            UNIQUE(billing_record_id, time_entry_id)
        )
        '''
        self.execute_query(query)

    # Schema Fix Methods
    def fix_clients_table(self):
        """Ensure clients table has all required columns"""
        if not self.table_exists('clients'):
            self.create_clients_table()
            return

        required_columns = {
            'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
        }

        for column_name, column_def in required_columns.items():
            self.add_column_if_missing('clients', column_name, column_def)

    def fix_projects_table(self):
        """Ensure projects table has all required columns"""
        if not self.table_exists('projects'):
            self.create_projects_table()
            return

        required_columns = {
            'is_lump_sum': 'INTEGER DEFAULT 0',
            'lump_sum_amount': 'REAL DEFAULT 0',
            'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
        }

        for column_name, column_def in required_columns.items():
            self.add_column_if_missing('projects', column_name, column_def)

    def fix_tasks_table(self):
        """Ensure tasks table has all required columns"""
        if not self.table_exists('tasks'):
            self.create_tasks_table()
            return

        required_columns = {
            'hourly_rate': 'REAL DEFAULT 0',
            'is_lump_sum': 'INTEGER DEFAULT 0',
            'lump_sum_amount': 'REAL DEFAULT 0',
            'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
        }

        for column_name, column_def in required_columns.items():
            self.add_column_if_missing('tasks', column_name, column_def)

    def fix_time_entries_table(self):
        """Ensure time_entries table has all required columns"""
        if not self.table_exists('time_entries'):
            self.create_time_entries_table()
            return

        required_columns = {
            'task_name': 'TEXT',
            'client_id': 'INTEGER',
            'client_name': 'TEXT',
            'project_id': 'INTEGER',
            'project_name': 'TEXT',
            'date': 'TEXT',
            'duration_minutes': 'INTEGER DEFAULT 0',
            'description': 'TEXT',
            'is_manual': 'INTEGER DEFAULT 0',
            'is_billed': 'INTEGER DEFAULT 0',
            'billing_date': 'TEXT',
            'invoice_number': 'TEXT',
            'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
        }

        for column_name, column_def in required_columns.items():
            self.add_column_if_missing('time_entries', column_name, column_def)

    def fix_company_info_table(self):
        """Ensure company_info table has all required columns"""
        if not self.table_exists('company_info'):
            self.create_company_info_table()
            return

        required_columns = {
            'logo_path': 'TEXT',
            'website': 'TEXT',
            'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
        }

        for column_name, column_def in required_columns.items():
            self.add_column_if_missing('company_info', column_name, column_def)

    def fix_billing_tables(self):
        """Ensure billing tables have all required columns"""
        if not self.table_exists('billing_records'):
            self.create_billing_records_table()

        if not self.table_exists('billing_time_entries'):
            self.create_billing_time_entries_table()

        # Create billing_history table if doesn't exist
        if not self.table_exists('billing_history'):
            query = '''
            CREATE TABLE IF NOT EXISTS billing_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT UNIQUE NOT NULL,
                client_id INTEGER NOT NULL,
                client_name TEXT NOT NULL,
                invoice_date TEXT NOT NULL,
                period_start TEXT NOT NULL,
                period_end TEXT NOT NULL,
                total_amount REAL NOT NULL,
                total_hours REAL NOT NULL,
                invoice_items TEXT NOT NULL,
                pdf_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES clients (id)
            )
            '''
            self.execute_query(query)

        # Create billing_entry_link table if doesn't exist
        if not self.table_exists('billing_entry_link'):
            query = '''
            CREATE TABLE IF NOT EXISTS billing_entry_link (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT NOT NULL,
                time_entry_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (time_entry_id) REFERENCES time_entries (id),
                UNIQUE(invoice_number, time_entry_id)
            )
            '''
            self.execute_query(query)

        # Create invoice_view for simpler queries
        self.execute_query("DROP VIEW IF EXISTS invoice_view")
        query = '''
        CREATE VIEW IF NOT EXISTS invoice_view AS
        SELECT 
            te.id as entry_id,
            te.task_id,
            te.duration_minutes,
            te.is_billed,
            c.id as client_id,
            c.name as client_name,
            p.id as project_id,
            p.name as project_name,
            p.hourly_rate as project_rate,
            p.is_lump_sum as project_lump_sum,
            p.lump_sum_amount as project_lump_amount,
            t.name as task_name,
            t.hourly_rate as task_rate,
            t.is_lump_sum as task_lump_sum,
            t.lump_sum_amount as task_lump_amount,
            te.start_time,
            te.end_time
        FROM time_entries te
        JOIN tasks t ON te.task_id = t.id
        JOIN projects p ON t.project_id = p.id
        JOIN clients c ON p.client_id = c.id
        '''
        self.execute_query(query)

    # Query Execution Methods
    def execute_query(self, query, params=None):
        """Execute a query with optional parameters"""
        try:
            cursor = self.conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False

    def fetch_all(self, query, params=None):
        """Fetch all results from a query"""
        try:
            cursor = self.conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []

    def fetch_one(self, query, params=None):
        """Fetch one result from a query"""
        try:
            cursor = self.conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None

    # Billing Methods
    def mark_entries_billed(self, entry_ids, invoice_number):
        """Mark time entries as billed"""
        if not entry_ids:
            return False

        placeholders = ','.join(['?' for _ in entry_ids])
        query = f'''
        UPDATE time_entries
        SET is_billed = 1, 
            billing_date = datetime('now'),
            invoice_number = ?
        WHERE id IN ({placeholders})
        '''
        params = [invoice_number] + entry_ids

        # Also create links in billing_entry_link
        for entry_id in entry_ids:
            link_query = '''
            INSERT OR IGNORE INTO billing_entry_link (invoice_number, time_entry_id)
            VALUES (?, ?)
            '''
            self.execute_query(link_query, [invoice_number, entry_id])

        return self.execute_query(query, params)

    def save_billing_history(self, invoice_data, invoice_number, pdf_path=None):
        """Save invoice to billing history"""
        import json

        query = '''
        INSERT INTO billing_history
        (invoice_number, client_id, client_name, invoice_date, 
         period_start, period_end, total_amount, total_hours, 
         invoice_items, pdf_path)
        VALUES (?, ?, ?, datetime('now'), ?, ?, ?, ?, ?, ?)
        '''

        # Calculate total hours
        total_hours = 0
        for item in invoice_data['items']:
            qty_str = str(item['quantity'])
            if 'hrs' in qty_str:
                try:
                    total_hours += float(qty_str.replace('hrs', '').strip())
                except:
                    pass

        # Get client name
        cursor = self.conn.cursor()
        cursor.execute('SELECT name FROM clients WHERE id = ?', (invoice_data['client_id'],))
        result = cursor.fetchone()
        client_name = result[0] if result else "Unknown"

        params = [
            invoice_number,
            invoice_data['client_id'],
            client_name,
            invoice_data['start_date'].strftime('%Y-%m-%d'),
            invoice_data['end_date'].strftime('%Y-%m-%d'),
            invoice_data['total'],
            total_hours,
            json.dumps(invoice_data['items']),
            pdf_path
        ]
        return self.execute_query(query, params)

    def get_billing_history(self, client_id=None):
        """Get billing history with optional client filter"""
        query = '''
        SELECT * FROM billing_history
        WHERE 1=1
        '''
        params = []
        if client_id:
            query += ' AND client_id = ?'
            params.append(client_id)
        query += ' ORDER BY invoice_date DESC'
        return self.fetch_all(query, params)

    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()

    def __del__(self):
        """Ensure database connection is closed when object is destroyed"""
        self.close()
