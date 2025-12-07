from database import DatabaseManager
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
                SET name=?, company=?, email=?, phone=?, address=?
                WHERE id=?
            ''', (name, company, email, phone, address, client_id))
    
    def delete(self, client_id):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM clients WHERE id=?', (client_id,))

class Project:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def create(self, client_id, name, description="", hourly_rate=0, is_lump_sum=False, lump_sum_amount=0):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO projects (client_id, name, description, hourly_rate, is_lump_sum, lump_sum_amount)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (client_id, name, description, hourly_rate, is_lump_sum, lump_sum_amount))
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
    
    def update(self, project_id, name, description="", hourly_rate=0, is_lump_sum=False, lump_sum_amount=0):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE projects 
                SET name=?, description=?, hourly_rate=?, is_lump_sum=?, lump_sum_amount=?
                WHERE id=?
            ''', (name, description, hourly_rate, is_lump_sum, lump_sum_amount, project_id))
    
    def delete(self, project_id):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM projects WHERE id=?', (project_id,))

class Task:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def create(self, project_id, name, description="", hourly_rate=0, is_lump_sum=False, lump_sum_amount=0):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO tasks (project_id, name, description, hourly_rate, is_lump_sum, lump_sum_amount)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (project_id, name, description, hourly_rate, is_lump_sum, lump_sum_amount))
            return cursor.lastrowid
    
    def get_by_project(self, project_id):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT t.*, p.name as project_name 
                FROM tasks t 
                JOIN projects p ON t.project_id = p.id 
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
                SET name=?, description=?, hourly_rate=?, is_lump_sum=?, lump_sum_amount=?
                WHERE id=?
            ''', (name, description, hourly_rate, is_lump_sum, lump_sum_amount, task_id))
    
    def delete(self, task_id):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM tasks WHERE id=?', (task_id,))

class TimeEntry:
    def __init__(self, db_manager):
        self.db = db_manager
        self.current_entry = None
    
    def start_timer(self, task_id, description=""):
        # Stop any existing timer first
        if self.current_entry:
            self.stop_timer()
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO time_entries (task_id, start_time, description, is_manual)
                VALUES (?, ?, ?, 0)
            ''', (task_id, datetime.now(), description))
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
                    duration = int((end_time - start_time).total_seconds() / 60)
                    cursor.execute('''
                        UPDATE time_entries 
                        SET end_time=?, duration_minutes=? 
                        WHERE id=?
                    ''', (end_time, duration, self.current_entry))
            self.current_entry = None

    def add_manual_entry(self, task_id, start_time, end_time, description=""):
        duration = int((end_time - start_time).total_seconds() / 60)
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # Get task, project, and client info
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

            # Extract date from start_time
            date_str = start_time.strftime('%Y-%m-%d')

            cursor.execute('''
                           INSERT INTO time_entries (task_id, task_name, project_id, project_name,
                                                     client_id, client_name, date, start_time, end_time,
                                                     duration_minutes, duration, description, is_manual, is_billed)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 0)
                           ''', (task_id, task_name, project_id, project_name,
                                 client_id, client_name, date_str, start_time.isoformat(), end_time.isoformat(),
                                 duration, duration / 60.0, description))
            return cursor.lastrowid

    def get_by_task(self, task_id):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM time_entries 
                WHERE task_id = ? 
                ORDER BY start_time DESC
            ''', (task_id,))
            return cursor.fetchall()
    
    def get_all(self):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT te.*, t.name as task_name, p.name as project_name, c.name as client_name
                FROM time_entries te
                JOIN tasks t ON te.task_id = t.id
                JOIN projects p ON t.project_id = p.id
                JOIN clients c ON p.client_id = c.id
                ORDER BY te.start_time DESC
            ''')
            return cursor.fetchall()
    
    def update(self, entry_id, start_time, end_time, description=""):
        duration = int((end_time - start_time).total_seconds() / 60)
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE time_entries 
                SET start_time=?, end_time=?, duration_minutes=?, description=?
                WHERE id=?
            ''', (start_time, end_time, duration, description, entry_id))
    
    def delete(self, entry_id):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM time_entries WHERE id=?', (entry_id,))

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
    
    def get(self):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM company_info WHERE id = 1')
            return cursor.fetchone()
