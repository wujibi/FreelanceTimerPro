"""
Database Manager for Time Tracking App
Handles all database operations including time entries, clients, projects, and billing
"""
import os
import re
import sqlite3
import logging

from datetime import datetime, timedelta
from pathlib import Path
from contextlib import contextmanager
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, db_path: str = 'time_tracker.db') -> None:
        """Initialize database connection and setup tables."""
        print(f"[DEBUG] DatabaseManager.__init__ called with db_path: {db_path}")

        self.db_path = db_path
        self.conn = None  # Initialize to None FIRST
        self.backup_dir = 'backups'
        self.lock = None  # Initialize lock as None too

        try:
            print(f"[DEBUG] Attempting to connect to database at: {self.db_path}")
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            
            # CRITICAL: Enable foreign key constraints (disabled by default in SQLite)
            self.conn.execute("PRAGMA foreign_keys = ON")
            print(f"[DEBUG] Foreign key constraints enabled")
            
            import threading
            self.lock = threading.Lock()
            print(f"[DEBUG] Database connection established, calling setup_database()")
            self.setup_database()
            print(f"[DEBUG] Database setup complete")
        except Exception as e:
            print(f"\n{'=' * 60}")
            print(f"CRITICAL DATABASE ERROR in __init__:")
            print(f"{'=' * 60}")
            print(f"{e}")
            import traceback
            traceback.print_exc()
            print(f"{'=' * 60}\n")
            # Clean up if connection was partially created
            if self.conn:
                try:
                    self.conn.close()
                except:
                    pass
                self.conn = None
            raise  # Re-raise the exception

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        try:
            yield self.conn
        finally:
            pass  # Connection stays open, managed by __init__ and close()

    def setup_database(self):
        """Comprehensive database setup with validation and migration"""
        print("Setting up database...")

        # Check if database is new or existing
        db_is_new = not os.path.exists(self.db_path) or os.path.getsize(self.db_path) == 0

    # def get_connection(self):
        # """Context manager for database connections"""
        # yield self.conn

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

        # Backfill legacy billed invoices that were not persisted to billing_history.
        self.backfill_missing_billing_history()

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
        self.create_email_settings_table()
        self.create_email_templates_table()
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

    def _column_def_for_alter_table(self, column_definition: str) -> Tuple[str, bool]:
        """
        SQLite ADD COLUMN only allows constant defaults. CURRENT_TIMESTAMP / datetime('now')
        often fail with "Cannot add a column with non-constant default".
        Returns (definition_for_alter, needs_timestamp_backfill).
        """
        s = column_definition.strip()
        s = s.replace('PRIMARY KEY AUTOINCREMENT', '').replace('AUTOINCREMENT', '')
        backfill = False
        if re.search(r"DEFAULT\s+CURRENT_TIMESTAMP", s, re.IGNORECASE):
            s = re.sub(r"\s+DEFAULT\s+CURRENT_TIMESTAMP\s*", " ", s, flags=re.IGNORECASE).strip()
            backfill = True
        if re.search(r"DEFAULT\s+datetime\s*\(\s*'now'\s*\)", s, re.IGNORECASE):
            s = re.sub(
                r"\s+DEFAULT\s+datetime\s*\(\s*'now'\s*\)\s*",
                " ",
                s,
                flags=re.IGNORECASE,
            ).strip()
            backfill = True
        return s, backfill

    def add_column_if_missing(self, table_name, column_name, column_definition):
        """Add column to table if it doesn't exist"""
        columns = self.get_table_columns(table_name)
        if column_name not in columns:
            alter_def, backfill_ts = self._column_def_for_alter_table(column_definition)
            query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {alter_def}"
            if self.execute_query(query):
                print(f"Added column {column_name} to {table_name}")
                if backfill_ts:
                    self.execute_query(
                        f"UPDATE {table_name} SET {column_name} = datetime('now') "
                        f"WHERE {column_name} IS NULL"
                    )
            else:
                print(f"Note: Could not add {column_name} to {table_name}")

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
            project_id INTEGER,
            name TEXT NOT NULL,
            description TEXT,
            hourly_rate REAL DEFAULT 0,
            is_lump_sum INTEGER DEFAULT 0,
            lump_sum_amount REAL DEFAULT 0,
            is_global INTEGER DEFAULT 0,
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
            payment_terms TEXT,
            thank_you_message TEXT,
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
            'is_global': 'INTEGER DEFAULT 0',
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
            'payment_terms': 'TEXT',
            'thank_you_message': 'TEXT',
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
                is_paid INTEGER DEFAULT 0,
                date_paid TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES clients (id)
            )
            '''
            self.execute_query(query)
        
        # Add payment tracking columns if missing (for existing databases)
        self.add_column_if_missing('billing_history', 'is_paid', 'INTEGER DEFAULT 0')
        self.add_column_if_missing('billing_history', 'date_paid', 'TEXT')
        
        # Add email tracking columns if missing
        self.add_column_if_missing('billing_history', 'email_sent_date', 'TEXT')
        self.add_column_if_missing('billing_history', 'email_sent_to', 'TEXT')
        self.add_column_if_missing('billing_history', 'email_subject', 'TEXT')
        self.add_column_if_missing('billing_history', 'email_body', 'TEXT')

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

    def get_billing_history(self, client_id=None, paid_status=None):
        """Get billing history with optional client and payment status filter
        
        Args:
            client_id: Optional client ID to filter by
            paid_status: Optional payment status filter (0=unpaid, 1=paid, None=all)
        """
        query = '''
        SELECT * FROM billing_history
        WHERE 1=1
        '''
        params = []
        if client_id:
            query += ' AND client_id = ?'
            params.append(client_id)
        if paid_status is not None:
            query += ' AND is_paid = ?'
            params.append(paid_status)
        query += ' ORDER BY invoice_date DESC'
        return self.fetch_all(query, params)

    def backfill_missing_billing_history(self):
        """Create billing_history rows for legacy billed entries missing invoice records."""
        import json

        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT
                te.invoice_number,
                COALESCE(te.client_id, p.client_id) AS client_id,
                COALESCE(c.name, te.client_name, 'Unknown') AS client_name,
                MIN(DATE(te.start_time)) AS period_start,
                MAX(DATE(te.start_time)) AS period_end,
                COALESCE(MAX(te.billing_date), MAX(DATE(te.start_time)), DATE('now')) AS invoice_date,
                COUNT(*) AS entry_count,
                SUM(COALESCE(te.duration_minutes, 0)) / 60.0 AS total_hours,
                SUM((COALESCE(te.duration_minutes, 0) / 60.0) * COALESCE(t.hourly_rate, p.hourly_rate, 0)) AS total_amount
            FROM time_entries te
            LEFT JOIN tasks t ON te.task_id = t.id
            LEFT JOIN projects p ON te.project_id = p.id
            LEFT JOIN clients c ON c.id = COALESCE(te.client_id, p.client_id)
            WHERE te.is_billed = 1
              AND te.invoice_number IS NOT NULL
              AND TRIM(te.invoice_number) != ''
              AND te.invoice_number NOT IN (SELECT invoice_number FROM billing_history)
            GROUP BY te.invoice_number, COALESCE(te.client_id, p.client_id), COALESCE(c.name, te.client_name, 'Unknown')
            """
        )
        missing_invoices = cursor.fetchall()

        if not missing_invoices:
            return 0

        created_count = 0
        for row in missing_invoices:
            invoice_number = row[0]
            client_id = row[1]
            client_name = row[2] or "Unknown"
            period_start = row[3] or row[5]
            period_end = row[4] or row[5]
            invoice_date = row[5] or datetime.now().strftime("%Y-%m-%d")
            entry_count = row[6] or 0
            total_hours = row[7] or 0.0
            total_amount = row[8] or 0.0

            if client_id is None:
                continue

            invoice_items = json.dumps(
                [
                    {
                        "description": f"Backfilled from {entry_count} billed time entries",
                        "quantity": f"{total_hours:.2f} hrs",
                        "rate": "$0.00/hr",
                        "amount": total_amount,
                    }
                ]
            )

            cursor.execute(
                """
                INSERT OR IGNORE INTO billing_history
                (invoice_number, client_id, client_name, invoice_date, period_start, period_end,
                 total_amount, total_hours, invoice_items, pdf_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    invoice_number,
                    client_id,
                    client_name,
                    invoice_date,
                    period_start,
                    period_end,
                    total_amount,
                    total_hours,
                    invoice_items,
                    None,
                ),
            )
            created_count += cursor.rowcount

            cursor.execute(
                """
                INSERT OR IGNORE INTO billing_entry_link (invoice_number, time_entry_id)
                SELECT ?, te.id
                FROM time_entries te
                WHERE te.invoice_number = ?
                """,
                (invoice_number, invoice_number),
            )

        self.conn.commit()
        if created_count:
            print(f"[INFO] Backfilled {created_count} missing invoice record(s) into billing_history")
        return created_count
    
    def mark_invoice_paid(self, invoice_number, date_paid):
        """Mark an invoice as paid with the payment date
        
        Args:
            invoice_number: The invoice number to mark as paid
            date_paid: The date payment was received (YYYY-MM-DD format)
        """
        query = '''
        UPDATE billing_history
        SET is_paid = 1,
            date_paid = ?
        WHERE invoice_number = ?
        '''
        return self.execute_query(query, [date_paid, invoice_number])
    
    def mark_invoice_unpaid(self, invoice_number):
        """Mark an invoice as unpaid (undo payment)
        
        Args:
            invoice_number: The invoice number to mark as unpaid
        """
        query = '''
        UPDATE billing_history
        SET is_paid = 0,
            date_paid = NULL
        WHERE invoice_number = ?
        '''
        return self.execute_query(query, [invoice_number])
    
    def get_invoice_by_number(self, invoice_number):
        """Get a specific invoice by invoice number
        
        Args:
            invoice_number: The invoice number to retrieve
        """
        query = '''
        SELECT * FROM billing_history
        WHERE invoice_number = ?
        '''
        return self.fetch_one(query, [invoice_number])

    def delete_invoice(self, invoice_number):
        """Delete an invoice and un-bill its linked time entries.

        This removes invoice metadata and links, then clears billed flags
        on any time entries that were assigned to the invoice number.
        """
        try:
            cursor = self.conn.cursor()

            cursor.execute(
                '''
                UPDATE time_entries
                SET is_billed = 0,
                    billing_date = NULL,
                    invoice_number = NULL
                WHERE invoice_number = ?
                ''',
                (invoice_number,),
            )

            cursor.execute(
                'DELETE FROM billing_entry_link WHERE invoice_number = ?',
                (invoice_number,),
            )
            cursor.execute(
                'DELETE FROM billing_history WHERE invoice_number = ?',
                (invoice_number,),
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Database error deleting invoice {invoice_number}: {e}")
            self.conn.rollback()
            return False

    def create_email_settings_table(self):
        """Create email settings table for SMTP configuration"""
        query = '''
        CREATE TABLE IF NOT EXISTS email_settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            smtp_server TEXT NOT NULL,
            smtp_port INTEGER NOT NULL DEFAULT 587,
            email_address TEXT NOT NULL,
            email_password TEXT NOT NULL,
            from_name TEXT,
            send_copy_to_self INTEGER DEFAULT 1,
            show_preview_before_send INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
        self.execute_query(query)
    
    def create_email_templates_table(self):
        """Create email templates table"""
        query = '''
        CREATE TABLE IF NOT EXISTS email_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            subject TEXT NOT NULL,
            body TEXT NOT NULL,
            is_default INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
        self.execute_query(query)
    
    # Email Settings Methods
    def get_email_settings(self):
        """Get email SMTP settings"""
        query = 'SELECT * FROM email_settings WHERE id = 1'
        return self.fetch_one(query)
    
    def save_email_settings(self, smtp_server, smtp_port, email_address, 
                           email_password, from_name=None, send_copy_to_self=True,
                           show_preview_before_send=True):
        """Save or update email settings"""
        query = '''
        INSERT OR REPLACE INTO email_settings
        (id, smtp_server, smtp_port, email_address, email_password, from_name,
         send_copy_to_self, show_preview_before_send, updated_at)
        VALUES (1, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        '''
        params = [
            smtp_server, smtp_port, email_address, email_password, from_name,
            1 if send_copy_to_self else 0,
            1 if show_preview_before_send else 0
        ]
        return self.execute_query(query, params)
    
    # Email Template Methods
    def get_email_templates(self):
        """Get all email templates"""
        query = 'SELECT * FROM email_templates ORDER BY name'
        return self.fetch_all(query)
    
    def get_email_template(self, template_id=None, template_name=None):
        """Get a specific email template by ID or name"""
        if template_id:
            query = 'SELECT * FROM email_templates WHERE id = ?'
            return self.fetch_one(query, [template_id])
        elif template_name:
            query = 'SELECT * FROM email_templates WHERE name = ?'
            return self.fetch_one(query, [template_name])
        return None
    
    def get_default_template(self):
        """Get the default email template"""
        query = 'SELECT * FROM email_templates WHERE is_default = 1 LIMIT 1'
        return self.fetch_one(query)
    
    def save_email_template(self, name, subject, body, is_default=False):
        """Save or update an email template"""
        # If setting as default, unset all others first
        if is_default:
            self.execute_query('UPDATE email_templates SET is_default = 0')
        
        query = '''
        INSERT INTO email_templates (name, subject, body, is_default, updated_at)
        VALUES (?, ?, ?, ?, datetime('now'))
        ON CONFLICT(name) DO UPDATE SET
            subject = excluded.subject,
            body = excluded.body,
            is_default = excluded.is_default,
            updated_at = datetime('now')
        '''
        return self.execute_query(query, [name, subject, body, 1 if is_default else 0])
    
    def delete_email_template(self, template_id):
        """Delete an email template"""
        query = 'DELETE FROM email_templates WHERE id = ?'
        return self.execute_query(query, [template_id])
    
    def update_invoice_email_sent(self, invoice_number, recipient_email, 
                                  email_subject, email_body):
        """Update billing history with email sent information"""
        query = '''
        UPDATE billing_history
        SET email_sent_date = datetime('now'),
            email_sent_to = ?,
            email_subject = ?,
            email_body = ?
        WHERE invoice_number = ?
        '''
        return self.execute_query(query, [recipient_email, email_subject, 
                                         email_body, invoice_number])

    def close(self):
        """Close the database connection"""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()

    def __del__(self):
        """Cleanup database connection."""
        try:
            if hasattr(self, 'conn') and self.conn:
                self.conn.close()
                logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")
