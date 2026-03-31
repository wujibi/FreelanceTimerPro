# Version: 2026-02-03
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
from core.client_resolution import resolve_client_id_by_name
from core.project_resolution import resolve_project_id_by_names
from core.task_list_builders import build_task_displays_for_project
from core.task_resolution import (
    GLOBAL_TASK_PREFIX,
    format_task_display,
    resolve_task_id_for_timer,
)
from db_manager import DatabaseManager
from models import Client, Project, Task, TimeEntry, CompanyInfo
from themes import AVAILABLE_THEMES
import sqlite3
import threading
import time
import tempfile
from config import (
    APP_ICON_FILENAME,
    APP_TITLE,
    ASSETS_DIRNAME,
    DEFAULT_MIN_WINDOW_SIZE,
    DEFAULT_THEME_NAME,
    DEFAULT_WINDOW_GEOMETRY,
)
from ui_helpers import (
    center_dialog,
    center_window,
    load_theme_preference,
    restore_tree_state,
    save_theme_preference,
    save_tree_state,
)
from ui.tk.clients_tab import ClientsTabMixin
from ui.tk.clients_runtime import ClientsRuntimeMixin
from ui.tk.company_tab import CompanyTabMixin
from ui.tk.company_runtime import CompanyRuntimeMixin
from ui.tk.email_tab import EmailTabMixin
from ui.tk.invoice_tab import InvoiceTabMixin
from ui.tk.invoice_runtime import InvoiceRuntimeMixin
from ui.tk.projects_tab import ProjectsTabMixin
from ui.tk.projects_runtime import ProjectsRuntimeMixin
from ui.tk.tasks_tab import TasksTabMixin
from ui.tk.tasks_runtime import TasksRuntimeMixin
from ui.tk.manual_entry_runtime import ManualEntryRuntimeMixin
from ui.tk.time_entries_tab import TimeEntriesTabMixin
from ui.tk.time_entries_runtime import TimeEntriesRuntimeMixin
from ui.tk.timer_tab import TimerTabMixin
from ui.tk.timer_runtime import TimerRuntimeMixin


class TimeTrackerApp(
    InvoiceRuntimeMixin,
    CompanyRuntimeMixin,
    TimeEntriesRuntimeMixin,
    TasksRuntimeMixin,
    ProjectsRuntimeMixin,
    ClientsRuntimeMixin,
    ManualEntryRuntimeMixin,
    TimerRuntimeMixin,
    TimerTabMixin,
    ClientsTabMixin,
    ProjectsTabMixin,
    TasksTabMixin,
    TimeEntriesTabMixin,
    CompanyTabMixin,
    EmailTabMixin,
    InvoiceTabMixin,
):
    def __init__(self, root, db_path=None):
        """Initialize the Time Tracker application.

        Args:
            root: The tkinter root window
            db_path: Path to the database file (optional, defaults to 'time_tracker.db')
        """
        try:
            print("[DEBUG] TimeTrackerApp.__init__ starting...")
            self.root = root
            self.root.title(APP_TITLE)
            
            # Modern window setup
            self.root.geometry(DEFAULT_WINDOW_GEOMETRY)
            self.root.minsize(*DEFAULT_MIN_WINDOW_SIZE)  # Much more flexible for small screens
            
            # Try to set custom icon (if exists)
            try:
                # Get absolute path to icon file relative to this script
                script_dir = os.path.dirname(os.path.abspath(__file__))
                icon_path = os.path.join(script_dir, ASSETS_DIRNAME, APP_ICON_FILENAME)
                if os.path.exists(icon_path):
                    self.root.iconbitmap(icon_path)
            except Exception as e:
                print(f"[DEBUG] Could not set icon: {e}")  # Debug
                pass  # Use default icon if custom not available
            
            # Initialize database FIRST (needed for theme preference)
            if db_path:
                print(f"[DEBUG] Initializing DatabaseManager with path: {db_path}")
                self.db = DatabaseManager(db_path)
            else:
                print(f"[DEBUG] Initializing DatabaseManager with default path")
                self.db = DatabaseManager()
            print(f"[DEBUG] DatabaseManager initialized successfully")
            
            # Load theme (colors and fonts) AFTER database is ready
            print("[DEBUG] Loading theme...")
            saved_theme = self.load_theme_preference()
            # Get theme from registry, fallback to first available theme if not found
            self.current_theme = AVAILABLE_THEMES.get(saved_theme, list(AVAILABLE_THEMES.values())[0])
            self.colors = self.current_theme.get_colors()
            self.fonts = self.current_theme.get_fonts()
            print(f"[DEBUG] Theme loaded: {saved_theme} ({len(self.colors)} colors, {len(self.fonts)} fonts)")

            # Initialize models
            print("[DEBUG] Initializing models...")
            self.client_model = Client(self.db)
            self.project_model = Project(self.db)
            self.task_model = Task(self.db)
            self.time_entry_model = TimeEntry(self.db)
            self.company_model = CompanyInfo(self.db)
            print("[DEBUG] Models initialized")

            # Timer variables
            self.timer_running = False
            self.timer_start_time = None
            self.current_task_id = None
            
            # Daily session tracking
            self.session_date = datetime.now().date()
            self.daily_client_totals = {}  # {client_id: total_seconds}
            self.daily_project_totals = {}  # {(client_id, project_id): total_seconds}
            self.last_timer_elapsed = 0
            self.last_timer_client_id = None
            self.last_timer_project_id = None
            print("[DEBUG] Timer variables initialized")

            print("[DEBUG] Creating widgets...")
            self.create_widgets()
            print("[DEBUG] Widgets created")

            print("[DEBUG] Refreshing data...")
            self.refresh_all_data()
            print("[DEBUG] Data refreshed")
            
            # Apply modern theme and center window
            print("[DEBUG] Applying modern theme...")
            self.apply_modern_theme()
            self.center_window()
            print("[DEBUG] Theme applied")

            print("[DEBUG] TimeTrackerApp initialization complete!")

        except Exception as e:
            print(f"\n{'=' * 60}")
            print(f"ERROR IN TimeTrackerApp.__init__:")
            print(f"{'=' * 60}")
            print(f"{e}")
            import traceback
            traceback.print_exc()
            print(f"{'=' * 60}\n")
            raise
    
    def center_window(self):
        center_window(self.root)
    
    def center_dialog(self, dialog, width, height):
        center_dialog(self.root, dialog, width, height)
    
    def apply_modern_theme(self):
        """Apply theme styling to the application using theme system"""
        print("[DEBUG] Applying theme styles...")
        style = ttk.Style()
        
        # Apply current theme
        self.current_theme.apply_theme(style, self.colors, self.fonts)
        
        # Set root window background
        self.root.configure(bg=self.colors['background'])
        print("[DEBUG] Theme styles applied successfully")
    
    def load_theme_preference(self):
        return load_theme_preference(self.db.db_path, default_theme=DEFAULT_THEME_NAME)
    
    def save_theme_preference(self, theme_name):
        try:
            save_theme_preference(self.db.db_path, theme_name)
        except Exception as e:
            print(f"[ERROR] Could not save theme preference: {e}")
    
    def switch_theme(self, theme_name):
        """Switch to a different theme"""
        if theme_name not in AVAILABLE_THEMES:
            messagebox.showerror("Error", f"Theme '{theme_name}' not found")
            return
        
        # Load new theme
        self.current_theme = AVAILABLE_THEMES[theme_name]
        self.colors = self.current_theme.get_colors()
        self.fonts = self.current_theme.get_fonts()
        
        # Save preference
        self.save_theme_preference(theme_name)
        
        # Reapply theme
        self.apply_modern_theme()
        
        messagebox.showinfo("Theme Changed", 
                          f"Theme changed to '{theme_name}'\n\n" +
                          "Your preference has been saved.\n" +
                          "Note: Some changes may require restarting the app for full effect.")

    def save_tree_state(self, tree):
        return save_tree_state(tree)
    
    def restore_tree_state(self, tree, expanded_items, expand_all=False):
        restore_tree_state(tree, expanded_items, expand_all=expand_all)

    def create_widgets(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Create tabs
        self.create_timer_tab()
        self.create_clients_tab()
        self.create_projects_tab()
        self.create_tasks_tab()
        self.create_time_entries_tab()
        self.create_company_tab()
        self.create_invoice_tab()
        self.create_email_tab()
    
    def generate_invoice_data(self, client_id, start_date, end_date):
        conn = self.db.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
                       SELECT *
                       FROM invoice_view
                       WHERE client_id = ?
                         AND DATE (start_time) BETWEEN ?
                         AND ?
                         AND (is_billed = 0
                          OR is_billed IS NULL)
                       ''', (client_id, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))

        entries = cursor.fetchall()
        conn.row_factory = None

        if not entries:
            messagebox.showinfo("No Unbilled Hours", "No unbilled hours found for the selected client and date range.")
            return None

        self.pending_entry_ids = [row['entry_id'] for row in entries]
        invoice_items = []

        # Simple task grouping
        tasks = {}
        for row in entries:
            key = f"{row['project_name']} - {row['task_name']}"
            if key not in tasks:
                tasks[key] = {'minutes': 0, 'rate': row['task_rate'] or row['project_rate']}
            tasks[key]['minutes'] += row['duration_minutes'] or 0

        for task_name, data in tasks.items():
            hours = data['minutes'] / 60.0
            invoice_items.append({
                'description': task_name,
                'quantity': f"{hours:.2f} hrs",
                'rate': f"${data['rate']:.2f}/hr",
                'amount': hours * data['rate']
            })

        return {
            'client_id': client_id,
            'start_date': start_date,
            'end_date': end_date,
            'items': invoice_items,
            'total': sum(item['amount'] for item in invoice_items)
        }

    # Refresh methods
    def refresh_clients(self):
        # Clear tree
        for item in self.client_tree.get_children():
            self.client_tree.delete(item)

        # Add clients
        clients = self.client_model.get_all()
        for client in clients:
            self.client_tree.insert('', 'end', values=(
                client[0],  # ID
                client[1],  # Name
                client[2] or "",  # Company
                client[3] or "",  # Email
                client[4] or ""  # Phone
            ))

    def refresh_projects(self):
        # Clear tree
        for item in self.project_tree.get_children():
            self.project_tree.delete(item)

        # Add projects
        projects = self.project_model.get_all()
        for project in projects:
            # Project structure from models.py get_all():
            # 0: id, 1: client_id, 2: name, 3: description,
            # 4: hourly_rate, 5: is_lump_sum, 6: lump_sum_amount,
            # 7: created_at, 8: updated_at, 9: client_name (from JOIN)

            billing_type = "Lump Sum" if project[5] else "Hourly"
            rate = f"${project[6]:.2f}" if project[5] else f"${project[4]:.2f}/hr"
            client_name = project[9] if len(project) > 9 else "Unknown Client"

            self.project_tree.insert('', 'end', values=(
                project[0],  # ID
                client_name,  # Client name (was project[7], should be project[9])
                project[2],  # Project name
                billing_type,
                rate
            ))

    def refresh_tasks(self):
        # Save expansion state before clearing
        expanded_items = self.save_tree_state(self.task_tree)
        
        # Clear tree
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)

        # Get all tasks and organize hierarchically
        tasks = self.task_model.get_all()
        global_tasks = self.task_model.get_global_tasks()
        
        # Build hierarchy: {client_name: {project_name: [tasks]}}
        hierarchy = {}
        
        for task in tasks:
            client_name = task[9] if len(task) > 9 and task[9] else "Unknown Client"
            project_name = task[8] if len(task) > 8 and task[8] else "Unknown Project"
            
            if client_name not in hierarchy:
                hierarchy[client_name] = {}
            if project_name not in hierarchy[client_name]:
                hierarchy[client_name][project_name] = []
            
            hierarchy[client_name][project_name].append(task)
        
        # Display hierarchy
        for client_name in sorted(hierarchy.keys()):
            # Insert client node
            client_id = self.task_tree.insert('', 'end',
                text=f"📁 {client_name}",
                values=('Client', '', '', '', ''),
                tags=('client', 'client_row'))
            
            for project_name in sorted(hierarchy[client_name].keys()):
                # Insert project node
                project_id = self.task_tree.insert(client_id, 'end',
                    text=f"  📂 {project_name}",
                    values=('Project', '', '', '', ''),
                    tags=('project', 'project_row'))
                
                # Insert tasks under project
                for task in hierarchy[client_name][project_name]:
                    billing_type = "Lump Sum" if task[5] else "Hourly"
                    rate = f"${task[6]:.2f}" if task[5] else f"${task[4]:.2f}/hr"
                    
                    self.task_tree.insert(project_id, 'end',
                        text=f"    ⚙️ {task[2]}",
                        values=('Task', task[0], '', billing_type, rate),
                        tags=('task', 'task_row', f'task_id_{task[0]}'))
        
        # Add global tasks section if any exist
        if global_tasks:
            global_node = self.task_tree.insert('', 'end',
                text="📁 [GLOBAL TASKS]",
                values=('Global', '', '', '', ''),
                tags=('global',))
            
            for task in global_tasks:
                billing_type = "Lump Sum" if task[5] else "Hourly"
                rate = f"${task[6]:.2f}" if task[5] else f"${task[4]:.2f}/hr"
                
                self.task_tree.insert(global_node, 'end',
                    text=f"  ⚙️ {task[2]}",
                    values=('Global Task', task[0], '', billing_type, rate),
                    tags=('task', f'task_id_{task[0]}'))
        
        # Configure tag colors
        self.task_tree.tag_configure('client', font=('Arial', 10, 'bold'))
        self.task_tree.tag_configure('project', font=('Arial', 9, 'bold'))
        self.task_tree.tag_configure('task', font=('Arial', 9))
        self.task_tree.tag_configure('global', font=('Arial', 10, 'bold'), foreground='#10b981')
        
        # Restore expansion state (expand all by default)
        self.restore_tree_state(self.task_tree, expanded_items, expand_all=True)


    def refresh_time_entries(self):
        # Save expansion state before clearing
        expanded_items = self.save_tree_state(self.entries_tree)
        
        # Clear tree
        for item in self.entries_tree.get_children():
            self.entries_tree.delete(item)

        # Get filter value
        filter_val = self.time_entries_filter_var.get() if hasattr(self, 'time_entries_filter_var') else 'unbilled'
        
        # Build WHERE clause
        where_clause = ""
        if filter_val == "unbilled":
            where_clause = "WHERE te.is_billed = 0"
        elif filter_val == "billed":
            where_clause = "WHERE te.is_billed = 1"
        # else "all" - no filter
        
        # Get time entries with filter
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                SELECT te.id, te.client_name, te.project_name, te.task_name,
                       te.start_time, te.end_time, te.duration_minutes, te.description,
                       te.is_billed, te.invoice_number
                FROM time_entries te
                {where_clause}
                ORDER BY te.client_name, te.project_name, te.task_name, te.start_time DESC
            ''')
            entries = cursor.fetchall()
        
        if not entries:
            return
        
        # Group entries by Client > Project > Task
        hierarchy = {}  # {client_name: {project_name: {task_name: [entries]}}}
        
        for entry in entries:
            client_name = entry[1]
            project_name = entry[2]
            task_name = entry[3]
            
            if client_name not in hierarchy:
                hierarchy[client_name] = {}
            if project_name not in hierarchy[client_name]:
                hierarchy[client_name][project_name] = {}
            if task_name not in hierarchy[client_name][project_name]:
                hierarchy[client_name][project_name][task_name] = []
            
            hierarchy[client_name][project_name][task_name].append(entry)
        
        # Build the tree structure
        for client_name in sorted(hierarchy.keys()):
            # Calculate client total
            client_total_minutes = 0
            for project_name in hierarchy[client_name]:
                for task_name in hierarchy[client_name][project_name]:
                    for entry in hierarchy[client_name][project_name][task_name]:
                        client_total_minutes += entry[6] if entry[6] else 0
            
            client_total_hours = client_total_minutes / 60.0
            
            # Insert client node
            client_id = self.entries_tree.insert('', 'end', 
                text=f"📁 {client_name}",
                values=('Client', '', '', f"{client_total_hours:.2f} hrs", ''),
                tags=('client', 'client_row'))
            
            # Add projects under client
            for project_name in sorted(hierarchy[client_name].keys()):
                # Calculate project total
                project_total_minutes = 0
                for task_name in hierarchy[client_name][project_name]:
                    for entry in hierarchy[client_name][project_name][task_name]:
                        project_total_minutes += entry[6] if entry[6] else 0
                
                project_total_hours = project_total_minutes / 60.0
                
                # Insert project node
                project_id = self.entries_tree.insert(client_id, 'end',
                    text=f"  📂 {project_name}",
                    values=('Project', '', '', f"{project_total_hours:.2f} hrs", ''),
                    tags=('project', 'project_row'))
                
                # Add tasks under project
                for task_name in sorted(hierarchy[client_name][project_name].keys()):
                    task_entries = hierarchy[client_name][project_name][task_name]
                    
                    # Calculate task total
                    task_total_minutes = sum(e[6] if e[6] else 0 for e in task_entries)
                    task_total_hours = task_total_minutes / 60.0
                    
                    # Check if any entry is billed
                    has_billed = any(e[8] for e in task_entries)
                    billed_indicator = " [BILLED]" if has_billed else ""
                    
                    # Insert task node
                    task_id = self.entries_tree.insert(project_id, 'end',
                        text=f"    📋 {task_name}{billed_indicator}",
                        values=('Task', f"{len(task_entries)} entries", '', f"{task_total_hours:.2f} hrs", ''),
                        tags=('task', 'task_row'))
                    
                    # Add individual entries under task
                    for entry in task_entries:
                        duration_minutes = entry[6] if entry[6] else 0
                        duration_hours = duration_minutes / 60.0
                        
                        # Format start time
                        start_time = entry[4]
                        try:
                            dt = datetime.fromisoformat(start_time)
                            start_display = dt.strftime("%m/%d/%y %I:%M %p")
                        except:
                            start_display = start_time
                        
                        # Billed indicator for individual entry
                        is_billed = entry[8]
                        entry_billed = " [BILLED]" if is_billed else ""
                        
                        # Store entry ID in tags for later retrieval
                        # Calculate row number for alternating colors
                        entry_index = task_entries.index(entry)
                        row_tag = 'oddrow' if entry_index % 2 == 0 else 'evenrow'
                        
                        entry_id = self.entries_tree.insert(task_id, 'end',
                            text=f"      ⏱️ Entry",
                            values=('Entry' + entry_billed, '', start_display, f"{duration_hours:.2f} hrs", entry[7] or ''),
                            tags=('entry', f'entry_id_{entry[0]}', 'entry_row'))
        
        # Configure tag colors
        self.entries_tree.tag_configure('client', font=('Arial', 10, 'bold'))
        self.entries_tree.tag_configure('project', font=('Arial', 9, 'bold'))
        self.entries_tree.tag_configure('task', font=('Arial', 9))
        self.entries_tree.tag_configure('entry', font=('Arial', 8))
        
        # Restore expansion state (expand all by default)
        self.restore_tree_state(self.entries_tree, expanded_items, expand_all=True)

    def refresh_combos(self):
        # Refresh timer combos
        clients = self.client_model.get_all()
        client_names = [c[1] for c in clients]
        self.timer_client_combo['values'] = client_names

        # Refresh project combo
        self.project_client_combo['values'] = client_names

        # Refresh task client combo
        self.task_client_combo['values'] = client_names

        # Refresh task combo for manual entry (include global tasks)
        tasks = self.task_model.get_all()
        global_tasks = self.task_model.get_global_tasks()
        
        task_displays = [format_task_display(task) for task in global_tasks]
        task_displays.extend(format_task_display(task) for task in tasks)
        
        self.manual_task_combo['values'] = task_displays

        # Refresh invoice client combo
        self.invoice_client_combo['values'] = client_names
        
        # Refresh manual entry client combo
        self.manual_client_combo['values'] = client_names

    def generate_invoice_data(self, client_id, start_date, end_date):
        # Get connection directly (not using context manager for row_factory)
        conn = self.db.conn
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
                       SELECT *
                       FROM invoice_view
                       WHERE client_id = ?
                         AND DATE (start_time) BETWEEN ?
                         AND ?
                         AND (is_billed = 0
                          OR is_billed IS NULL)
                       ''', (client_id, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))

        entries = cursor.fetchall()
        conn.row_factory = None  # Reset to default

        if not entries:
            messagebox.showinfo("No Unbilled Hours", "No unbilled hours found for the selected client and date range.")
            return None

        self.pending_entry_ids = [row['entry_id'] for row in entries]
        invoice_items = []

        # Simple task grouping
        tasks = {}
        for row in entries:
            key = f"{row['project_name']} - {row['task_name']}"
            if key not in tasks:
                tasks[key] = {'minutes': 0, 'rate': row['task_rate'] or row['project_rate']}
            tasks[key]['minutes'] += row['duration_minutes'] or 0

        for task_name, data in tasks.items():
            hours = data['minutes'] / 60.0
            invoice_items.append({
                'description': task_name,
                'quantity': f"{hours:.2f} hrs",
                'rate': f"${data['rate']:.2f}/hr",
                'amount': hours * data['rate']
            })

        return {
            'client_id': client_id,
            'start_date': start_date,
            'end_date': end_date,
            'items': invoice_items,
            'total': sum(item['amount'] for item in invoice_items)
        }

    # Email Settings Methods
    def on_email_provider_select(self):
        """Auto-fill SMTP settings based on provider selection"""
        provider = self.email_provider_var.get()
        
        if provider == "gmail":
            self.smtp_server_entry.delete(0, tk.END)
            self.smtp_server_entry.insert(0, "smtp.gmail.com")
            self.smtp_port_entry.delete(0, tk.END)
            self.smtp_port_entry.insert(0, "587")
        elif provider == "outlook":
            self.smtp_server_entry.delete(0, tk.END)
            self.smtp_server_entry.insert(0, "smtp.office365.com")
            self.smtp_port_entry.delete(0, tk.END)
            self.smtp_port_entry.insert(0, "587")
        # Custom provider - let user fill manually
    
    def toggle_password_visibility(self):
        """Show/hide email password"""
        if self.show_password_var.get():
            self.email_password_entry.config(show='')
        else:
            self.email_password_entry.config(show='*')
    
    def save_email_settings(self):
        """Save email settings to database"""
        smtp_server = self.smtp_server_entry.get().strip()
        smtp_port = self.smtp_port_entry.get().strip()
        email_address = self.email_address_entry.get().strip()
        email_password = self.email_password_entry.get().strip()
        from_name = self.email_from_name_entry.get().strip()
        
        if not all([smtp_server, smtp_port, email_address, email_password]):
            messagebox.showerror("Error", "Please fill in all required fields (SMTP server, port, email, password)")
            return
        
        try:
            smtp_port = int(smtp_port)
        except ValueError:
            messagebox.showerror("Error", "Port must be a number")
            return
        
        # Save to database
        success = self.db.save_email_settings(
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            email_address=email_address,
            email_password=email_password,
            from_name=from_name or None,
            send_copy_to_self=self.send_copy_to_self_var.get(),
            show_preview_before_send=self.show_preview_var.get()
        )
        
        if success:
            messagebox.showinfo("Success", "Email settings saved successfully!\n\nClick 'Test Connection' to verify.")
        else:
            messagebox.showerror("Error", "Failed to save email settings")
    
    def load_email_settings(self):
        """Load email settings from database"""
        settings = self.db.get_email_settings()
        
        if not settings:
            messagebox.showinfo("No Settings", "No email settings found. Please configure your SMTP settings.")
            return
        
        # Populate fields
        self.smtp_server_entry.delete(0, tk.END)
        self.smtp_server_entry.insert(0, settings[1])  # smtp_server
        
        self.smtp_port_entry.delete(0, tk.END)
        self.smtp_port_entry.insert(0, str(settings[2]))  # smtp_port
        
        self.email_address_entry.delete(0, tk.END)
        self.email_address_entry.insert(0, settings[3])  # email_address
        
        self.email_password_entry.delete(0, tk.END)
        self.email_password_entry.insert(0, settings[4])  # email_password
        
        if settings[5]:  # from_name
            self.email_from_name_entry.delete(0, tk.END)
            self.email_from_name_entry.insert(0, settings[5])
        
        self.send_copy_to_self_var.set(bool(settings[6]))  # send_copy_to_self
        self.show_preview_var.set(bool(settings[7]))  # show_preview_before_send
        
        messagebox.showinfo("Loaded", "Email settings loaded successfully!")
    
    def test_email_connection(self):
        """Test SMTP connection and send test email"""
        smtp_server = self.smtp_server_entry.get().strip()
        smtp_port = self.smtp_port_entry.get().strip()
        email_address = self.email_address_entry.get().strip()
        email_password = self.email_password_entry.get().strip()
        
        if not all([smtp_server, smtp_port, email_address, email_password]):
            messagebox.showerror("Error", "Please fill in all fields first")
            return
        
        try:
            smtp_port = int(smtp_port)
        except ValueError:
            messagebox.showerror("Error", "Port must be a number")
            return
        
        # Import email sender
        from email_sender import EmailSender
        
        # Create sender and test
        sender = EmailSender(smtp_server, smtp_port, email_address, email_password)
        
        # First test connection
        success, message = sender.test_connection()
        
        if success:
            # Connection worked, now send test email
            if messagebox.askyesno("Connection Successful!", 
                "SMTP connection successful! ✅\n\nWould you like to send a test email to yourself?"):
                success, message = sender.send_test_email()
                messagebox.showinfo("Test Email", message)
        else:
            messagebox.showerror("Connection Failed", message)
    
    # Email Template Methods
    def on_template_select(self, event=None):
        """Template selected from dropdown"""
        pass  # Just for binding, actual load happens on Load button
    
    def load_selected_template(self):
        """Load the selected template"""
        template_name = self.template_combo.get()
        if not template_name:
            messagebox.showwarning("No Selection", "Please select a template first")
            return
        
        # Try to load from database first
        template = self.db.get_email_template(template_name=template_name)
        
        if template:
            # Load from database
            print(f"[DEBUG] Loading template '{template_name}' from DATABASE")
            print(f"[DEBUG] Subject: {template[2][:50]}...")
            print(f"[DEBUG] Body length: {len(template[3])} chars")
            
            self.template_subject_entry.delete(0, tk.END)
            self.template_subject_entry.insert(0, template[2])  # subject
            
            self.template_body_text.delete('1.0', tk.END)
            self.template_body_text.insert('1.0', template[3])  # body
        else:
            # Load from defaults
            print(f"[DEBUG] Template '{template_name}' NOT in database, loading from DEFAULTS")
            from email_sender import EmailTemplate
            default_template = EmailTemplate.get_template(template_name)
            
            if default_template:
                self.template_subject_entry.delete(0, tk.END)
                self.template_subject_entry.insert(0, default_template['subject'])
                
                self.template_body_text.delete('1.0', tk.END)
                self.template_body_text.insert('1.0', default_template['body'])
            else:
                messagebox.showerror("Error", f"Template '{template_name}' not found")
                return
        
        self.update_template_preview()
    
    def reset_template_to_default(self):
        """Reset current template to default version"""
        template_name = self.template_combo.get()
        if not template_name:
            messagebox.showwarning("No Selection", "Please select a template first")
            return
        
        from email_sender import EmailTemplate
        default_template = EmailTemplate.get_template(template_name)
        
        if default_template:
            self.template_subject_entry.delete(0, tk.END)
            self.template_subject_entry.insert(0, default_template['subject'])
            
            self.template_body_text.delete('1.0', tk.END)
            self.template_body_text.insert('1.0', default_template['body'])
            
            self.update_template_preview()
            messagebox.showinfo("Reset", f"Template '{template_name}' reset to default")
        else:
            messagebox.showerror("Error", f"Default template '{template_name}' not found")
    
    def insert_variable(self, variable):
        """Insert a variable at cursor position in body text"""
        self.template_body_text.insert(tk.INSERT, variable)
        self.template_body_text.focus_set()
    
    def update_template_preview(self):
        """Update the preview pane with rendered template"""
        from email_sender import EmailTemplate
        import html
        
        # Get current template text
        subject = self.template_subject_entry.get()
        body = self.template_body_text.get('1.0', tk.END)
        
        # Sample data
        sample_data = {
            'client_name': 'John Smith',
            'client_company': 'Smith & Associates',
            'client_email': 'john@company.com',
            'invoice_number': 'INV-20260129-123456',
            'invoice_date': 'January 29, 2026',
            'invoice_total': '$1,234.56',
            'payment_terms': 'Payment due within 30 days',
            'due_date': 'February 28, 2026',
            'date_range': 'January 1-29, 2026',
            'company_name': 'Your Company Name',
            'company_email': 'you@company.com',
            'company_phone': '(555) 123-4567',
            'company_website': 'www.yourcompany.com'
        }
        
        # Render template
        rendered_subject = EmailTemplate.render_template(subject, sample_data)
        rendered_body = EmailTemplate.render_template(body, sample_data)
        
        # Strip HTML for preview (simple approach)
        import re
        preview_body = re.sub('<[^<]+?>', '', rendered_body)
        preview_body = html.unescape(preview_body)
        
        # Update preview
        self.template_preview_text.config(state='normal')
        self.template_preview_text.delete('1.0', tk.END)
        self.template_preview_text.insert('1.0', f"Subject: {rendered_subject}\n\n{preview_body}")
        self.template_preview_text.config(state='disabled')
    
    def save_current_template(self):
        """Save the current template to database"""
        print("[DEBUG] ===== SAVE_CURRENT_TEMPLATE CALLED =====")
        template_name = self.template_combo.get()
        print(f"[DEBUG] Template name: {template_name}")
        if not template_name:
            messagebox.showwarning("No Selection", "Please select a template first")
            return
        
        subject = self.template_subject_entry.get().strip()
        body = self.template_body_text.get('1.0', tk.END).strip()
        
        if not subject or not body:
            messagebox.showerror("Error", "Subject and body cannot be empty")
            return
        
        # Save to database
        success = self.db.save_email_template(template_name, subject, body, is_default=False)
        
        if success:
            # Verify by reloading from database
            saved_template = self.db.get_email_template(template_name=template_name)
            if saved_template and saved_template[2] == subject and saved_template[3] == body:
                messagebox.showinfo("Success", f"Template '{template_name}' saved successfully!")
            else:
                messagebox.showwarning("Warning", f"Template saved but verification failed. Try loading the template to confirm.")
        else:
            messagebox.showerror("Error", "Failed to save template")
    
    def send_test_template_email(self):
        """Send a test email using current template"""
        # Check if email settings exist
        settings = self.db.get_email_settings()
        if not settings:
            messagebox.showerror("No Email Settings", 
                "Please configure your email settings in the Email Settings tab first")
            return
        
        # Get current template
        subject = self.template_subject_entry.get().strip()
        body = self.template_body_text.get('1.0', tk.END).strip()
        
        if not subject or not body:
            messagebox.showerror("Error", "Please create a template first")
            return
        
        from email_sender import EmailSender, EmailTemplate
        
        # Sample data
        sample_data = {
            'client_name': 'John Smith',
            'client_company': 'Smith & Associates',
            'client_email': 'john@company.com',
            'invoice_number': 'INV-TEST-123456',
            'invoice_date': datetime.now().strftime('%B %d, %Y'),
            'invoice_total': '$1,234.56',
            'payment_terms': 'Payment due within 30 days',
            'due_date': (datetime.now() + timedelta(days=30)).strftime('%B %d, %Y'),
            'date_range': 'January 1-29, 2026',
            'company_name': settings[5] or 'Your Company',
            'company_email': settings[3],
            'company_phone': '(555) 123-4567',
            'company_website': 'www.yourcompany.com'
        }
        
        # Render template
        rendered_subject = EmailTemplate.render_template(subject, sample_data)
        rendered_body = EmailTemplate.render_template(body, sample_data)
        
        # Create sender
        sender = EmailSender(settings[1], settings[2], settings[3], settings[4])
        
        # Send test email
        success, message = sender.send_email(
            to_address=settings[3],  # Send to self
            subject=f"TEST: {rendered_subject}",
            body_html=rendered_body,
            from_name=settings[5]
        )
        
        if success:
            messagebox.showinfo("Success", f"{message}\n\nCheck your inbox!")
        else:
            messagebox.showerror("Failed", message)
    
    def refresh_all_data(self):
        self.refresh_clients()
        self.refresh_projects()
        self.refresh_tasks()
        self.refresh_time_entries()
        self.refresh_combos()
        self.load_company_info()
        self.update_daily_totals_display()
        self.refresh_email_templates()
        self.load_email_settings_silent()  # Auto-load email settings on startup  # Initialize daily totals display
        
        # Load email templates list if tab exists
        if hasattr(self, 'template_combo'):
            from email_sender import EmailTemplate
            template_names = EmailTemplate.get_template_names()
            self.template_combo['values'] = template_names
            if template_names:
                self.template_combo.set(template_names[0])  # Select first template
        
        if hasattr(self, 'billed_invoices_tree'):
            self.refresh_billed_invoices()  # Refresh billed invoices if tab exists
    
    def show_invoice_preview_dialog(self, client_id, client_name, entry_ids):
        """Show invoice preview dialog with EDIT and CREATE buttons"""
        import sqlite3
        
        # Create dialog
        preview_dialog = tk.Toplevel(self.root)
        preview_dialog.title(f"Invoice Preview - {client_name}")
        self.center_dialog(preview_dialog, 800, 600)
        
        # Get entry details for invoice
        conn = self.db.conn
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        placeholders = ','.join(['?' for _ in entry_ids])
        cursor.execute(f'''
            SELECT te.id as entry_id, te.start_time, te.duration_minutes, te.description,
                   p.name as project_name, p.hourly_rate as project_rate, p.is_lump_sum as project_lump_sum,
                   p.lump_sum_amount as project_lump_amount,
                   t.name as task_name, t.hourly_rate as task_rate, t.is_lump_sum as task_lump_sum,
                   t.lump_sum_amount as task_lump_amount
            FROM time_entries te
            JOIN tasks t ON te.task_id = t.id
            JOIN projects p ON te.project_id = p.id
            WHERE te.id IN ({placeholders})
        ''', entry_ids)
        
        entries = cursor.fetchall()
        conn.row_factory = None
        
        # Group by project -> task with subtotals
        project_groups = {}  # {project_name: {tasks: {task_name: data}, subtotal: 0}}
        
        for entry in entries:
            project_name = entry['project_name']
            task_name = entry['task_name']
            
            if project_name not in project_groups:
                project_groups[project_name] = {'tasks': {}, 'subtotal': 0}
            
            if task_name not in project_groups[project_name]['tasks']:
                project_groups[project_name]['tasks'][task_name] = {
                    'minutes': 0,
                    'rate': entry['task_rate'] or entry['project_rate'],
                    'is_lump_sum': entry['task_lump_sum'] or entry['project_lump_sum'],
                    'lump_sum_amount': entry['task_lump_amount'] or entry['project_lump_amount']
                }
            
            project_groups[project_name]['tasks'][task_name]['minutes'] += entry['duration_minutes'] or 0
        
        # Build invoice items with project/task hierarchy
        invoice_items = []
        total_amount = 0
        total_hours = 0  # Track total hours across all tasks
        
        for project_name, project_data in project_groups.items():
            # Add project header
            invoice_items.append({
                'description': f'**{project_name}**',
                'quantity': '',
                'rate': '',
                'amount': '',
                'is_header': True
            })
            
            project_subtotal = 0
            
            for task_name, task_data in project_data['tasks'].items():
                hours = task_data['minutes'] / 60.0
                total_hours += hours  # Add to running total
                
                if task_data['is_lump_sum']:
                    amount = task_data['lump_sum_amount']
                    invoice_items.append({
                        'description': f'  • {task_name}',
                        'quantity': '1',
                        'rate': f"${amount:.2f}",
                        'amount': amount,
                        'is_task': True
                    })
                else:
                    amount = hours * task_data['rate']
                    invoice_items.append({
                        'description': f'  • {task_name}',
                        'quantity': f"{hours:.2f} hrs",
                        'rate': f"${task_data['rate']:.2f}/hr",
                        'amount': amount,
                        'is_task': True
                    })
                
                project_subtotal += amount
            
            # Add project subtotal
            invoice_items.append({
                'description': f'  {project_name} Subtotal',
                'quantity': '',
                'rate': '',
                'amount': project_subtotal,
                'is_subtotal': True
            })
            
            total_amount += project_subtotal
        
        # Get date range from entries
        start_dates = [datetime.fromisoformat(e['start_time']) for e in entries]
        start_date = min(start_dates) if start_dates else datetime.now()
        end_date = max(start_dates) if start_dates else datetime.now()
        
        # Store for later use
        self.current_invoice_data = {
            'client_id': client_id,
            'client_name': client_name,
            'entry_ids': entry_ids,
            'items': invoice_items,
            'total': total_amount,
            'start_date': start_date,
            'end_date': end_date
        }
        
        # Header
        header_frame = ttk.Frame(preview_dialog)
        header_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Label(header_frame, text=f"INVOICE PREVIEW", 
                 font=('Arial', 16, 'bold')).pack()
        ttk.Label(header_frame, text=f"Client: {client_name}", 
                 font=('Arial', 12)).pack(pady=5)
        ttk.Label(header_frame, text=f"Date: {datetime.now().strftime('%B %d, %Y')}", 
                 font=('Arial', 10)).pack()
        
        # Items tree
        items_frame = ttk.LabelFrame(preview_dialog, text="Invoice Items")
        items_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        items_tree = ttk.Treeview(items_frame, 
            columns=('Description', 'Quantity', 'Rate', 'Amount'),
            show='headings')
        
        items_tree.heading('Description', text='Description')
        items_tree.heading('Quantity', text='Quantity')
        items_tree.heading('Rate', text='Rate')
        items_tree.heading('Amount', text='Amount')
        
        items_tree.column('Description', width=350)
        items_tree.column('Quantity', width=100)
        items_tree.column('Rate', width=100)
        items_tree.column('Amount', width=100)
        
        for item in invoice_items:
            if item.get('is_header'):
                # Bold project header
                items_tree.insert('', 'end', values=(
                    item['description'].replace('**', ''),
                    '', '', ''
                ), tags=('header',))
            elif item.get('is_subtotal'):
                # Project subtotal row
                items_tree.insert('', 'end', values=(
                    item['description'],
                    '', '',
                    f"${item['amount']:.2f}"
                ), tags=('subtotal',))
            else:
                # Regular task row
                amount_display = f"${item['amount']:.2f}" if isinstance(item['amount'], (int, float)) else ''
                items_tree.insert('', 'end', values=(
                    item['description'],
                    item['quantity'],
                    item['rate'],
                    amount_display
                ))
        
        # Configure tags for styling
        items_tree.tag_configure('header', font=('Arial', 10, 'bold'), background='#e8f4f8')
        items_tree.tag_configure('subtotal', font=('Arial', 9, 'bold'), background='#f0f0f0')
        
        items_tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Total
        total_frame = ttk.Frame(preview_dialog)
        total_frame.pack(fill='x', padx=20, pady=10)
        
        # Total hours label (left side)
        ttk.Label(total_frame, text=f"Total Hours: {total_hours:.2f} hrs", 
                 font=('Arial', 12, 'bold'),
                 foreground=self.colors['text_secondary']).pack(side='left')
        
        # Total amount label (right side)
        ttk.Label(total_frame, text=f"TOTAL: ${total_amount:.2f}", 
                 font=('Arial', 14, 'bold')).pack(side='right')
        
        # Buttons
        button_frame = ttk.Frame(preview_dialog)
        button_frame.pack(fill='x', padx=20, pady=20)
        
        def create_invoice():
            """Mark entries as billed and generate PDF"""
            if messagebox.askyesno("Confirm", 
                f"Create invoice for ${total_amount:.2f}?\n\n" +
                "This will mark all selected time entries as BILLED."):
                
                # Generate invoice number
                invoice_date = datetime.now()
                invoice_number = f"INV-{invoice_date.strftime('%Y%m%d-%H%M%S')}"
                
                # Ask for save location
                filename = filedialog.asksaveasfilename(
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf")],
                    initialfile=f"Invoice_{client_name.replace(' ', '_')}_{invoice_number}.pdf"
                )
                
                if filename:
                    try:
                        # Generate PDF
                        from invoice_generator import InvoiceGenerator
                        generator = InvoiceGenerator(self.db)
                        
                        print(f"[DEBUG] Generating PDF with data: {self.current_invoice_data.keys()}")
                        print(f"[DEBUG] Start date: {self.current_invoice_data['start_date']}")
                        print(f"[DEBUG] End date: {self.current_invoice_data['end_date']}")
                        print(f"[DEBUG] Total items: {len(self.current_invoice_data['items'])}")
                        
                        generator.generate_pdf(self.current_invoice_data, filename, invoice_number)
                        
                        print(f"[DEBUG] PDF generated successfully at: {filename}")
                        
                        # Mark entries as billed
                        conn = self.db.conn  # Use direct connection
                        cursor = conn.cursor()
                        placeholders = ','.join(['?' for _ in entry_ids])
                        cursor.execute(f'''
                            UPDATE time_entries 
                            SET is_billed = 1, 
                                invoice_number = ?,
                                billing_date = ?
                            WHERE id IN ({placeholders})
                        ''', [invoice_number, invoice_date.strftime("%Y-%m-%d")] + entry_ids)
                        conn.commit()
                        
                        print(f"[DEBUG] Marked {len(entry_ids)} entries as billed")
                        
                        # Refresh displays
                        self.refresh_time_entries()
                        self.load_invoiceable_entries()
                        
                        preview_dialog.destroy()
                        
                        messagebox.showinfo("Success", 
                            f"Invoice created successfully!\n\n" +
                            f"File: {filename}\n" +
                            f"Invoice #: {invoice_number}\n" +
                            f"Total: ${total_amount:.2f}\n\n" +
                            f"{len(entry_ids)} time entries marked as billed.")
                    
                    except Exception as e:
                        import traceback
                        error_details = traceback.format_exc()
                        print(f"[ERROR] Invoice generation failed:")
                        print(error_details)
                        messagebox.showerror("Error", 
                            f"Failed to create invoice:\n\n{str(e)}\n\n" +
                            f"Check console for details.")
        
        def edit_time_entries_from_preview():
            """Allow editing time entries from the invoice preview"""
            # Create a selection window showing all time entries in this invoice
            edit_window = tk.Toplevel(preview_dialog)
            edit_window.title("Edit Time Entries")
            self.center_dialog(edit_window, 700, 500)
            
            # Header
            ttk.Label(edit_window, text="Select a time entry to edit:", 
                     font=('Arial', 12, 'bold')).pack(padx=20, pady=10)
            
            # Tree showing all entries
            tree_frame = ttk.Frame(edit_window)
            tree_frame.pack(fill='both', expand=True, padx=20, pady=10)
            
            edit_tree = ttk.Treeview(tree_frame,
                columns=('Date', 'Project', 'Task', 'Hours', 'Description'),
                show='headings',
                selectmode='browse')
            
            edit_tree.heading('Date', text='Date')
            edit_tree.heading('Project', text='Project')
            edit_tree.heading('Task', text='Task')
            edit_tree.heading('Hours', text='Hours')
            edit_tree.heading('Description', text='Description')
            
            edit_tree.column('Date', width=120)
            edit_tree.column('Project', width=120)
            edit_tree.column('Task', width=120)
            edit_tree.column('Hours', width=80)
            edit_tree.column('Description', width=200)
            
            # Scrollbar for tree
            scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=edit_tree.yview)
            edit_tree.configure(yscrollcommand=scrollbar.set)
            
            edit_tree.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
            
            # Load time entry details
            conn = self.db.conn
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            placeholders = ','.join(['?' for _ in entry_ids])
            cursor.execute(f'''
                SELECT te.id as entry_id, te.start_time, te.end_time, te.duration_minutes, 
                       te.description, p.name as project_name, t.name as task_name
                FROM time_entries te
                JOIN tasks t ON te.task_id = t.id
                JOIN projects p ON te.project_id = p.id
                WHERE te.id IN ({placeholders})
                ORDER BY te.start_time
            ''', entry_ids)
            
            time_entries = cursor.fetchall()
            conn.row_factory = None
            
            # Populate tree
            for entry in time_entries:
                try:
                    dt = datetime.fromisoformat(entry['start_time'])
                    date_display = dt.strftime("%m/%d/%y %I:%M %p")
                except:
                    date_display = entry['start_time'][:10]
                
                hours = (entry['duration_minutes'] or 0) / 60.0
                
                edit_tree.insert('', 'end',
                    values=(
                        date_display,
                        entry['project_name'],
                        entry['task_name'],
                        f"{hours:.2f}",
                        entry['description'] or ''
                    ),
                    tags=(f"entry_id_{entry['entry_id']}",))
            
            # Button frame
            btn_frame = ttk.Frame(edit_window)
            btn_frame.pack(fill='x', padx=20, pady=20)
            
            def edit_selected_entry():
                """Edit the selected time entry"""
                selection = edit_tree.selection()
                if not selection:
                    messagebox.showerror("Error", "Please select a time entry to edit")
                    return
                
                # Extract entry ID from tags
                tags = edit_tree.item(selection[0])['tags']
                entry_id = None
                for tag in tags:
                    if tag.startswith('entry_id_'):
                        entry_id = int(tag.replace('entry_id_', ''))
                        break
                
                if not entry_id:
                    messagebox.showerror("Error", "Could not find entry ID")
                    return
                
                # Close the edit selection window
                edit_window.destroy()
                
                # Open the edit dialog (reuse existing method)
                self.open_edit_time_entry_dialog(entry_id)
                
                # Note: User must manually refresh using "Refresh & Close" button after editing
                # This prevents the confusing auto-refresh before user has made changes
            
            def refresh_invoice_preview():
                """Refresh the invoice preview with updated data"""
                edit_window.destroy()
                preview_dialog.destroy()
                # Reload the invoice entries to show updated data
                self.load_invoiceable_entries()
                messagebox.showinfo("Refreshed", 
                    "Invoice data refreshed. Select entries and preview again to see changes.")
            
            ttk.Button(btn_frame, text="✏️ Edit Selected Entry", 
                      command=edit_selected_entry).pack(side='left', padx=5)
            ttk.Button(btn_frame, text="🔄 Refresh & Close", 
                      command=refresh_invoice_preview).pack(side='left', padx=5)
            ttk.Button(btn_frame, text="Cancel", 
                      command=edit_window.destroy).pack(side='right', padx=5)
        
        def email_invoice():
            """Email the invoice to the client"""
            # First, check if email is configured
            email_settings = self.db.get_email_settings()
            if not email_settings:
                if messagebox.askyesno("Email Not Configured",
                    "Email settings haven't been configured yet.\n\n" +
                    "Would you like to set them up now?"):
                    # Switch to Email Settings tab
                    self.notebook.select(6)  # Email Settings tab index
                    preview_dialog.destroy()
                return
            
            # Get client email
            client = self.client_model.get_by_id(client_id)
            if not client or not client[3]:  # client[3] is email
                messagebox.showerror("No Email Address",
                    f"Client '{client_name}' doesn't have an email address on file.\n\n" +
                    "Please add their email in the Clients tab first.")
                return
            
            client_email = client[3]
            
            # Show email send dialog
            self.show_email_invoice_dialog(preview_dialog, client_name, client_email, 
                                           client_id, entry_ids, invoice_items, total_amount,
                                           start_date, end_date)
        
        ttk.Button(button_frame, text="✏️ Edit Entries", 
                  command=edit_time_entries_from_preview).pack(side='left', padx=5)
        ttk.Button(button_frame, text="📧 Email Invoice", 
                  command=email_invoice).pack(side='right', padx=5)
        ttk.Button(button_frame, text="✅ CREATE INVOICE", 
                  command=create_invoice,
                  style='Accent.TButton').pack(side='right', padx=5)
        ttk.Button(button_frame, text="Cancel", 
                  command=preview_dialog.destroy).pack(side='right', padx=5)
    
    def show_email_invoice_dialog(self, parent_dialog, client_name, client_email, 
                                   client_id, entry_ids, invoice_items, total_amount,
                                   start_date, end_date):
        """Show dialog to send invoice via email"""
        import tempfile
        from email_sender import EmailSender, EmailTemplate
        
        # Create email dialog
        email_dialog = tk.Toplevel(parent_dialog)
        email_dialog.title("Email Invoice")
        email_dialog.geometry("600x700")
        email_dialog.transient(parent_dialog)
        email_dialog.grab_set()
        
        # Header
        header_frame = ttk.Frame(email_dialog)
        header_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Label(header_frame, text="📧 Email Invoice", 
                 font=('Arial', 16, 'bold')).pack()
        ttk.Label(header_frame, text=f"To: {client_name} ({client_email})", 
                 font=('Arial', 10)).pack(pady=5)
        
        # Form
        form_frame = ttk.LabelFrame(email_dialog, text="Email Details")
        form_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Template selection
        ttk.Label(form_frame, text="Template:").grid(row=0, column=0, sticky='w', padx=10, pady=5)
        template_var = tk.StringVar(value="Professional")
        template_combo = ttk.Combobox(form_frame, textvariable=template_var, 
                                     values=EmailTemplate.get_template_names(), state='readonly')
        template_combo.grid(row=0, column=1, sticky='ew', padx=10, pady=5)
        
        # Subject
        ttk.Label(form_frame, text="Subject:").grid(row=1, column=0, sticky='w', padx=10, pady=5)
        subject_entry = ttk.Entry(form_frame, width=50)
        subject_entry.grid(row=1, column=1, sticky='ew', padx=10, pady=5)
        
        # CC (optional)
        ttk.Label(form_frame, text="CC (optional):").grid(row=2, column=0, sticky='w', padx=10, pady=5)
        cc_entry = ttk.Entry(form_frame, width=50)
        cc_entry.grid(row=2, column=1, sticky='ew', padx=10, pady=5)
        ttk.Label(form_frame, text="Separate multiple emails with commas", 
                 font=('Arial', 8), foreground='gray').grid(row=3, column=1, sticky='w', padx=10)
        
        # Message body
        ttk.Label(form_frame, text="Message:").grid(row=4, column=0, sticky='nw', padx=10, pady=5)
        message_text = tk.Text(form_frame, height=15, wrap='word')
        message_text.grid(row=4, column=1, sticky='ew', padx=10, pady=5)
        
        # Scrollbar for message
        message_scroll = ttk.Scrollbar(form_frame, orient='vertical', command=message_text.yview)
        message_text.configure(yscrollcommand=message_scroll.set)
        message_scroll.grid(row=4, column=2, sticky='ns', pady=5)
        
        form_frame.columnconfigure(1, weight=1)
        
        # Function to update template preview
        def update_template(*args):
            template_name = template_var.get()
            template = EmailTemplate.get_template(template_name)
            if template:
                # Get company info
                company = self.company_model.get()
                
                # Prepare variables for template
                invoice_number = f"INV-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                date_range = f"{start_date.strftime('%m/%d/%y')} - {end_date.strftime('%m/%d/%y')}"
                
                variables = {
                    'client_name': client_name,
                    'client_email': client_email,
                    'invoice_number': invoice_number,
                    'invoice_date': datetime.now().strftime('%B %d, %Y'),
                    'invoice_total': f"${total_amount:.2f}",
                    'payment_terms': company[7] if company and len(company) > 7 else 'Net 30',
                    'due_date': (datetime.now() + timedelta(days=30)).strftime('%B %d, %Y'),
                    'date_range': date_range,
                    'company_name': company[1] if company else 'Your Company',
                    'company_email': company[4] if company and len(company) > 4 else '',
                    'company_phone': company[3] if company and len(company) > 3 else '',
                    'company_website': company[6] if company and len(company) > 6 else ''
                }
                
                # Render template
                subject = EmailTemplate.render_template(template['subject'], variables)
                body = EmailTemplate.render_template(template['body'], variables)
                
                # Update fields
                subject_entry.delete(0, tk.END)
                subject_entry.insert(0, subject)
                
                message_text.delete('1.0', tk.END)
                message_text.insert('1.0', body)
        
        # Bind template change
        template_combo.bind('<<ComboboxSelected>>', update_template)
        
        # Load initial template
        update_template()
        
        # Buttons
        button_frame = ttk.Frame(email_dialog)
        button_frame.pack(fill='x', padx=20, pady=20)
        
        def send_email():
            """Send the email with invoice attached"""
            try:
                # Get email settings
                email_settings = self.db.get_email_settings()
                if not email_settings:
                    messagebox.showerror("Error", "Email settings not found")
                    return
                
                smtp_server = email_settings[1]
                smtp_port = email_settings[2]
                email_address = email_settings[3]
                email_password = email_settings[4]
                from_name = email_settings[5] if len(email_settings) > 5 else None
                
                # Initialize email sender
                sender = EmailSender(smtp_server, smtp_port, email_address, email_password)
                
                # Generate invoice PDF in temp location
                invoice_number = f"INV-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                temp_dir = tempfile.gettempdir()
                pdf_path = os.path.join(temp_dir, f"{invoice_number}.pdf")
                
                # Create invoice data
                invoice_data = {
                    'client_id': client_id,
                    'client_name': client_name,
                    'entry_ids': entry_ids,
                    'items': invoice_items,
                    'total': total_amount,
                    'start_date': start_date,
                    'end_date': end_date
                }
                
                # Generate PDF
                from invoice_generator import InvoiceGenerator
                generator = InvoiceGenerator(self.db)
                generator.generate_pdf(invoice_data, pdf_path, invoice_number)
                
                # Get email details
                subject = subject_entry.get().strip()
                body_html = message_text.get('1.0', tk.END).strip()
                
                # Parse CC addresses
                cc_addresses = None
                cc_text = cc_entry.get().strip()
                if cc_text:
                    cc_addresses = [email.strip() for email in cc_text.split(',')]
                
                # Send email
                success, message = sender.send_email(
                    to_address=client_email,
                    subject=subject,
                    body_html=body_html,
                    attachment_path=pdf_path,
                    cc_addresses=cc_addresses,
                    from_name=from_name
                )
                
                # Clean up temp PDF
                try:
                    os.remove(pdf_path)
                except:
                    pass
                
                if success:
                    # Ask if they want to mark as billed
                    if messagebox.askyesno("Email Sent!",
                        f"Invoice emailed successfully to {client_email}!\n\n" +
                        "Would you like to mark these time entries as BILLED now?"):
                        
                        # Mark entries as billed
                        invoice_date = datetime.now()
                        conn = self.db.conn
                        cursor = conn.cursor()
                        placeholders = ','.join(['?' for _ in entry_ids])
                        cursor.execute(f'''
                            UPDATE time_entries 
                            SET is_billed = 1, 
                                invoice_number = ?,
                                billing_date = ?
                            WHERE id IN ({placeholders})
                        ''', [invoice_number, invoice_date.strftime("%Y-%m-%d")] + entry_ids)
                        conn.commit()
                        
                        # Refresh displays
                        self.refresh_time_entries()
                        self.load_invoiceable_entries()
                        
                        messagebox.showinfo("Success",
                            f"Invoice #{invoice_number} sent and {len(entry_ids)} entries marked as billed!")
                    
                    # Close dialogs
                    email_dialog.destroy()
                    parent_dialog.destroy()
                else:
                    messagebox.showerror("Send Failed", message)
                    
            except Exception as e:
                import traceback
                traceback.print_exc()
                messagebox.showerror("Error", f"Failed to send email:\n\n{str(e)}")
        
        ttk.Button(button_frame, text="📧 Send Invoice", 
                  command=send_email,
                  style='Accent.TButton').pack(side='right', padx=5)
        ttk.Button(button_frame, text="Cancel", 
                  command=email_dialog.destroy).pack(side='right', padx=5)
    
