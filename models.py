from db_manager import DatabaseManager
from datetime import datetime, timedelta
import sqlite3


class Client:
    def __init__(self, db_manager):
        self.db = db_manager

    def create(self, name, company="", email="", phone="", address=""):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                           INSERT INTO clients (name, company, email, phone, address)
                           VALUES (?, ?, ?, ?, ?)
                           ''', (name, company, email, phone, address))
            conn.commit()  # ADDED
            return cursor.lastrowid

    def get_all(self):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM clients ORDER BY name')
            return cursor.fetchall()

    def get_by_id(self, client_id):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM clients WHERE id = ?', (client_id,))
            return cursor.fetchone()

    def update(self, client_id, name, company="", email="", phone="", address=""):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                           UPDATE clients
                           SET name=?,
                               company=?,
                               email=?,
                               phone=?,
                               address=?
                           WHERE id = ?
                           ''', (name, company, email, phone, address, client_id))
            conn.commit()  # ADDED

    def delete(self, client_id):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM clients WHERE id=?', (client_id,))
            conn.commit()  # ADDED


class Project:
    def __init__(self, db_manager):
        self.db = db_manager

    def create(self, client_id, name, description="", hourly_rate=0, is_lump_sum=False, lump_sum_amount=0):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                           INSERT INTO projects (client_id, name, description, hourly_rate, is_lump_sum,
                                                 lump_sum_amount)
                           VALUES (?, ?, ?, ?, ?, ?)
                           ''', (client_id, name, description, hourly_rate, is_lump_sum, lump_sum_amount))
            conn.commit()  # ADDED
            return cursor.lastrowid

    def get_by_client(self, client_id):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                           SELECT p.*, c.name as client_name
                           FROM projects p
                                    JOIN clients c ON p.client_id = c.id
                           WHERE p.client_id = ?
                           ORDER BY p.name
                           ''', (client_id,))
            return cursor.fetchall()

    def get_all(self):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                           SELECT p.*, c.name as client_name
                           FROM projects p
                                    JOIN clients c ON p.client_id = c.id
                           ORDER BY c.name, p.name
                           ''')
            return cursor.fetchall()

    def get_by_id(self, project_id):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
            return cursor.fetchone()

    def update(self, project_id, client_id, name, description="", hourly_rate=0, is_lump_sum=False, lump_sum_amount=0):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                           UPDATE projects
                           SET client_id=?,
                               name=?,
                               description=?,
                               hourly_rate=?,
                               is_lump_sum=?,
                               lump_sum_amount=?
                           WHERE id = ?
                           ''', (client_id, name, description, hourly_rate, is_lump_sum, lump_sum_amount, project_id))
            conn.commit()  # ADDED

    def delete(self, project_id):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM projects WHERE id=?', (project_id,))
            conn.commit()  # ADDED


class Task:
    def __init__(self, db_manager):
        self.db = db_manager

    def get_global_tasks(self):
        """Get all global tasks (not tied to any project)"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, project_id, name, description, hourly_rate, is_lump_sum, lump_sum_amount, is_global
                FROM tasks
                WHERE is_global = 1
                ORDER BY name
            ''')
            return cursor.fetchall()

    def get_all_for_project(self, project_id):
        """Get all tasks for a project including global tasks"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, project_id, name, description, hourly_rate, is_lump_sum, lump_sum_amount, is_global
                FROM tasks
                WHERE project_id = ? OR is_global = 1
                ORDER BY is_global DESC, name
            ''', (project_id,))
            return cursor.fetchall()

    def create(self, name, description="", hourly_rate=0, is_lump_sum=False, lump_sum_amount=0, project_id=None, is_global=False):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                           INSERT INTO tasks (project_id, name, description, hourly_rate, is_lump_sum, lump_sum_amount, is_global)
                           VALUES (?, ?, ?, ?, ?, ?, ?)
                           ''', (project_id, name, description, hourly_rate, is_lump_sum, lump_sum_amount, is_global))
            conn.commit()
            return cursor.lastrowid

    def get_by_project(self, project_id):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                           SELECT t.*, p.name as project_name, c.name as client_name
                           FROM tasks t
                                    JOIN projects p ON t.project_id = p.id
                                    JOIN clients c ON p.client_id = c.id
                           WHERE t.project_id = ?
                           ORDER BY t.name
                           ''', (project_id,))
            return cursor.fetchall()

    def get_all(self):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                           SELECT t.*, p.name as project_name, c.name as client_name
                           FROM tasks t
                                    JOIN projects p ON t.project_id = p.id
                                    JOIN clients c ON p.client_id = c.id
                           ORDER BY c.name, p.name, t.name
                           ''')
            return cursor.fetchall()

    def get_by_id(self, task_id):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
            return cursor.fetchone()

    def update(self, task_id, name, description="", hourly_rate=0, is_lump_sum=False, lump_sum_amount=0):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                           UPDATE tasks
                           SET name=?,
                               description=?,
                               hourly_rate=?,
                               is_lump_sum=?,
                               lump_sum_amount=?
                           WHERE id = ?
                           ''', (name, description, hourly_rate, is_lump_sum, lump_sum_amount, task_id))
            conn.commit()  # ADDED

    def delete(self, task_id):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM tasks WHERE id=?', (task_id,))
            conn.commit()  # ADDED


class TimeEntry:
    def __init__(self, db_manager):
        self.db = db_manager
        self.current_entry = None

    def start_timer(self, task_id, description="", project_id_override=None):
        """Start a timer for a task. Handles both project-specific and global tasks."""
        # Stop any existing timer first
        if self.current_entry:
            self.stop_timer()

        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # First check if task is global
            cursor.execute('SELECT is_global FROM tasks WHERE id = ?', (task_id,))
            task_result = cursor.fetchone()
            if not task_result:
                raise ValueError("Task not found")

            is_global = task_result[0]

            if is_global:
                # For global tasks, use the provided project_id_override
                if not project_id_override:
                    raise ValueError("Global tasks require a project context")

                cursor.execute('''
                               SELECT t.name, p.id, p.name, c.id, c.name
                               FROM tasks t, projects p
                               JOIN clients c ON p.client_id = c.id
                               WHERE t.id = ? AND p.id = ?
                               ''', (task_id, project_id_override))
            else:
                # Regular project-specific task
                cursor.execute('''
                               SELECT t.name, p.id, p.name, c.id, c.name
                               FROM tasks t
                               JOIN projects p ON t.project_id = p.id
                               JOIN clients c ON p.client_id = c.id
                               WHERE t.id = ?
                               ''', (task_id,))

            task_info = cursor.fetchone()
            if not task_info:
                raise ValueError("Task not found")

            task_name, project_id, project_name, client_id, client_name = task_info
            start_time = datetime.now()
            date_str = start_time.strftime('%Y-%m-%d')

            cursor.execute('''
                           INSERT INTO time_entries (task_id, task_name, project_id, project_name,
                                                     client_id, client_name, date, start_time,
                                                     description, is_manual, is_billed)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0)
                           ''', (task_id, task_name, project_id, project_name,
                                 client_id, client_name, date_str, start_time.isoformat(), description))
            conn.commit()
            self.current_entry = cursor.lastrowid
            return self.current_entry

    def stop_timer(self):
        if self.current_entry:
            end_time = datetime.now()
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT start_time FROM time_entries WHERE id = ?', (self.current_entry,))
                result = cursor.fetchone()
                if result:
                    start_time = datetime.fromisoformat(result[0])
                    duration_minutes = int((end_time - start_time).total_seconds() / 60)
                    duration_hours = duration_minutes / 60.0

                    cursor.execute('''
                                   UPDATE time_entries
                                   SET end_time=?,
                                       duration_minutes=?,
                                       duration=?
                                   WHERE id = ?
                                   ''', (end_time.isoformat(), duration_minutes, duration_hours, self.current_entry))
                    conn.commit()  # ADDED
            self.current_entry = None

    def add_manual_entry(self, task_id, start_time, end_time, description="", project_id_override=None):
        """Add a manual time entry. Handles both project-specific and global tasks.
        
        Args:
            task_id: ID of the task
            start_time: Start datetime
            end_time: End datetime
            description: Optional description
            project_id_override: Required for global tasks to specify which project context
        """
        duration_minutes = int((end_time - start_time).total_seconds() / 60)
        duration_hours = duration_minutes / 60.0

        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # First check if task is global
            cursor.execute('SELECT is_global, project_id FROM tasks WHERE id = ?', (task_id,))
            task_result = cursor.fetchone()
            if not task_result:
                raise ValueError("Task not found")

            is_global = task_result[0]
            task_project_id = task_result[1]

            if is_global:
                # For global tasks, we MUST have a project_id_override
                if not project_id_override:
                    raise ValueError("Global tasks require a project context (project_id_override)")

                # Get task name and project/client info separately
                cursor.execute('SELECT name FROM tasks WHERE id = ?', (task_id,))
                task_name_result = cursor.fetchone()
                task_name = task_name_result[0] if task_name_result else "Unknown Task"

                cursor.execute('''
                               SELECT p.id, p.name, c.id, c.name
                               FROM projects p
                               JOIN clients c ON p.client_id = c.id
                               WHERE p.id = ?
                               ''', (project_id_override,))
                project_info = cursor.fetchone()
                
                if not project_info:
                    raise ValueError(f"Project {project_id_override} not found")
                
                project_id, project_name, client_id, client_name = project_info
            else:
                # Regular project-specific task
                cursor.execute('''
                               SELECT t.name, p.id, p.name, c.id, c.name
                               FROM tasks t
                               JOIN projects p ON t.project_id = p.id
                               JOIN clients c ON p.client_id = c.id
                               WHERE t.id = ?
                               ''', (task_id,))

                task_info = cursor.fetchone()
                if not task_info:
                    raise ValueError("Task not found or has no associated project")

                task_name, project_id, project_name, client_id, client_name = task_info

            # Extract date from start_time
            date_str = start_time.strftime('%Y-%m-%d')

            cursor.execute('''
                           INSERT INTO time_entries (task_id, task_name, project_id, project_name,
                                                     client_id, client_name, date, start_time, end_time,
                                                     duration_minutes, duration, description, is_manual, is_billed)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 0)
                           ''', (task_id, task_name, project_id, project_name,
                                 client_id, client_name, date_str, start_time.isoformat(), end_time.isoformat(),
                                 duration_minutes, duration_hours, description))
            conn.commit()
            return cursor.lastrowid

    def get_by_task(self, task_id):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                           SELECT *
                           FROM time_entries
                           WHERE task_id = ?
                           ORDER BY start_time DESC
                           ''', (task_id,))
            return cursor.fetchall()

    def get_all(self):
        """Get all time entries with clean column structure"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                           SELECT te.id,
                                  c.name as client_name,
                                  p.name as project_name,
                                  t.name as task_name,
                                  te.start_time,
                                  te.end_time,
                                  te.duration_minutes,
                                  te.description,
                                  te.is_billed,
                                  te.invoice_number
                           FROM time_entries te
                                    JOIN tasks t ON te.task_id = t.id
                                    JOIN projects p ON t.project_id = p.id
                                    JOIN clients c ON p.client_id = c.id
                           ORDER BY te.start_time DESC
                           ''')
            return cursor.fetchall()

    def update(self, entry_id, start_time, end_time, description=""):
        duration_minutes = int((end_time - start_time).total_seconds() / 60)
        duration_hours = duration_minutes / 60.0

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                           UPDATE time_entries
                           SET start_time=?,
                               end_time=?,
                               duration_minutes=?,
                               duration=?,
                               description=?
                           WHERE id = ?
                           ''',
                           (start_time.isoformat(), end_time.isoformat(), duration_minutes, duration_hours, description,
                            entry_id))
            conn.commit()  # ADDED

    def delete(self, entry_id):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM time_entries WHERE id=?', (entry_id,))
            conn.commit()  # ADDED


class CompanyInfo:
    def __init__(self, db_manager):
        self.db = db_manager

    def save(self, name, address="", phone="", email="", logo_path=""):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO company_info (id, name, address, phone, email, logo_path)
                VALUES (1, ?, ?, ?, ?, ?)
            ''', (name, address, phone, email, logo_path))
            conn.commit()  # ADDED

    def get(self):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM company_info WHERE id = 1')
            return cursor.fetchone()
