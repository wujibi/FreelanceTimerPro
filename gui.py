# Version: 2026-02-03
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from db_manager import DatabaseManager
from models import Client, Project, Task, TimeEntry, CompanyInfo
from themes import AVAILABLE_THEMES
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
from ui.tk.refresh_runtime import RefreshRuntimeMixin
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
    RefreshRuntimeMixin,
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
    
