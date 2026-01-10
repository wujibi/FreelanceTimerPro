import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
from db_manager import DatabaseManager
from models import Client, Project, Task, TimeEntry, CompanyInfo
import sqlite3
import threading
import time


class TimeTrackerApp:
    def __init__(self, root, db_path=None):
        """Initialize the Time Tracker application.

        Args:
            root: The tkinter root window
            db_path: Path to the database file (optional, defaults to 'time_tracker.db')
        """
        try:
            print("[DEBUG] TimeTrackerApp.__init__ starting...")
            self.root = root
            self.root.title("Time Tracker Pro V2.0 - Professional Time & Invoice Management")
            
            # Modern window setup
            self.root.geometry("1200x800")
            self.root.minsize(600, 400)  # Much more flexible for small screens
            
            # Try to set custom icon (if exists)
            try:
                icon_path = "assets/icon.ico"
                if os.path.exists(icon_path):
                    self.root.iconbitmap(icon_path)
            except:
                pass  # Use default icon if custom not available
            
            # Modern color scheme
            self.colors = {
                'primary': '#2563eb',      # Professional Blue
                'secondary': '#64748b',    # Slate Gray  
                'accent': '#10b981',       # Success Green
                'background': '#f8fafc',   # Light Gray
                'text': '#1e293b',         # Dark Slate
                'border': '#e2e8f0',       # Light Border
                'hover': '#3b82f6',        # Lighter Blue
                'error': '#ef4444',        # Red
                'success': '#22c55e'       # Green
            }
            
            # Configure modern fonts
            self.fonts = {
                'heading': ('Segoe UI', 12, 'bold'),
                'subheading': ('Segoe UI', 10, 'bold'),
                'body': ('Segoe UI', 10),
                'small': ('Segoe UI', 9),
                'title': ('Segoe UI', 14, 'bold'),
                'large_display': ('Segoe UI', 24)
            }

            # Initialize database with the provided path
            if db_path:
                print(f"[DEBUG] Initializing DatabaseManager with path: {db_path}")
                self.db = DatabaseManager(db_path)
            else:
                print(f"[DEBUG] Initializing DatabaseManager with default path")
                self.db = DatabaseManager()

            print(f"[DEBUG] DatabaseManager initialized successfully")

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
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def apply_modern_theme(self):
        """Apply modern styling to the application"""
        style = ttk.Style()
        
        # Try to use 'clam' theme as base (modern looking)
        try:
            style.theme_use('clam')
        except:
            pass  # Use default if clam not available
        
        # Configure Notebook (tabs)
        style.configure('TNotebook', 
                       background=self.colors['background'],
                       borderwidth=0)
        style.configure('TNotebook.Tab',
                       padding=[20, 10],
                       font=self.fonts['subheading'])
        style.map('TNotebook.Tab',
                 background=[('selected', self.colors['primary'])],
                 foreground=[('selected', 'white')])
        
        # Configure Buttons
        style.configure('TButton',
                       font=self.fonts['body'],
                       padding=[10, 5],
                       borderwidth=1)
        style.map('TButton',
                 background=[('active', self.colors['hover'])],
                 foreground=[('active', 'white')])
        
        # Accent button style (for primary actions)
        style.configure('Accent.TButton',
                       font=self.fonts['subheading'],
                       background=self.colors['primary'],
                       foreground='white',
                       padding=[15, 8])
        
        # Configure Labels
        style.configure('TLabel',
                       font=self.fonts['body'],
                       background=self.colors['background'])
        
        style.configure('Title.TLabel',
                       font=self.fonts['title'])
        
        # Configure Entry
        style.configure('TEntry',
                       font=self.fonts['body'],
                       fieldbackground='white',
                       borderwidth=1)
        
        # Configure Treeview (tables)
        style.configure('Treeview',
                       font=self.fonts['body'],
                       rowheight=25,
                       borderwidth=1)
        style.configure('Treeview.Heading',
                       font=self.fonts['subheading'],
                       background=self.colors['secondary'],
                       foreground='white',
                       borderwidth=1)
        style.map('Treeview',
                 background=[('selected', self.colors['primary'])],
                 foreground=[('selected', 'white')])
        
        # Configure LabelFrame
        style.configure('TLabelframe',
                       borderwidth=2,
                       relief='solid',
                       background=self.colors['background'])
        style.configure('TLabelframe.Label',
                       font=self.fonts['subheading'],
                       foreground=self.colors['text'])
        
        # Set root window background
        self.root.configure(bg=self.colors['background'])

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
        self.create_billed_invoices_tab()

    def create_timer_tab(self):
        # Timer tab with scrolling support
        timer_frame = ttk.Frame(self.notebook)
        self.notebook.add(timer_frame, text="Timer")
        
        # Create canvas and scrollbar for scrolling
        canvas = tk.Canvas(timer_frame, bg=self.colors['background'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(timer_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Now use scrollable_frame instead of timer_frame for all content
        timer_frame = scrollable_frame

        # Timer display
        timer_display_frame = ttk.LabelFrame(timer_frame, text="Active Timer")
        timer_display_frame.pack(fill='x', padx=10, pady=10)

        self.timer_label = ttk.Label(timer_display_frame, text="00:00:00", font=self.fonts['large_display'])
        self.timer_label.pack(pady=10)

        # Client, Project, and Task selection
        selection_frame = ttk.Frame(timer_display_frame)
        selection_frame.pack(fill='x', padx=10, pady=5)

        # Client selection
        client_frame = ttk.Frame(selection_frame)
        client_frame.pack(fill='x', pady=2)

        ttk.Label(client_frame, text="Client:").pack(side='left')
        self.timer_client_combo = ttk.Combobox(client_frame, state='readonly')
        self.timer_client_combo.pack(side='left', fill='x', expand=True, padx=5)
        self.timer_client_combo.bind('<<ComboboxSelected>>', self.on_timer_client_select)

        # Project selection
        project_frame = ttk.Frame(selection_frame)
        project_frame.pack(fill='x', pady=2)

        ttk.Label(project_frame, text="Project:").pack(side='left')
        self.timer_project_combo = ttk.Combobox(project_frame, state='readonly')
        self.timer_project_combo.pack(side='left', fill='x', expand=True, padx=5)
        self.timer_project_combo.bind('<<ComboboxSelected>>', self.on_timer_project_select)

        # Task selection
        task_frame = ttk.Frame(selection_frame)
        task_frame.pack(fill='x', pady=2)

        ttk.Label(task_frame, text="Task:").pack(side='left')
        self.timer_task_combo = ttk.Combobox(task_frame, state='readonly')
        self.timer_task_combo.pack(side='left', fill='x', expand=True, padx=5)

        # Timer buttons
        button_frame = ttk.Frame(timer_display_frame)
        button_frame.pack(pady=10)

        self.start_button = ttk.Button(button_frame, text="Start Timer", command=self.start_timer)
        self.start_button.pack(side='left', padx=5)

        self.stop_button = ttk.Button(button_frame, text="Stop Timer", command=self.stop_timer, state='disabled')
        self.stop_button.pack(side='left', padx=5)

        # Manual time entry section
        manual_frame = ttk.LabelFrame(timer_frame, text="Manual Time Entry")
        manual_frame.pack(fill='both', expand=True, padx=10, pady=10)

        form_frame = ttk.Frame(manual_frame)
        form_frame.pack(fill='x', padx=10, pady=10)

        # Date
        ttk.Label(form_frame, text="Date (MM/DD/YY):").grid(row=0, column=0, sticky='w', pady=2)
        self.manual_date_entry = ttk.Entry(form_frame)
        self.manual_date_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=2)
        self.manual_date_entry.insert(0, datetime.now().strftime("%m/%d/%y"))
        
        # Entry mode selection (Start/End Time OR Decimal Hours)
        ttk.Label(form_frame, text="Entry Mode:").grid(row=1, column=0, sticky='w', pady=2)
        mode_frame = ttk.Frame(form_frame)
        mode_frame.grid(row=1, column=1, sticky='ew', padx=5, pady=2)
        
        self.manual_entry_mode = tk.StringVar(value="time_range")
        ttk.Radiobutton(mode_frame, text="Start/End Time", variable=self.manual_entry_mode,
                       value="time_range", command=self.toggle_manual_entry_mode).pack(side='left')
        ttk.Radiobutton(mode_frame, text="Decimal Hours", variable=self.manual_entry_mode,
                       value="decimal", command=self.toggle_manual_entry_mode).pack(side='left', padx=10)

        # Start Time
        ttk.Label(form_frame, text="Start Time (HH:MM AM/PM):").grid(row=2, column=0, sticky='w', pady=2)
        self.manual_start_entry = ttk.Entry(form_frame)
        self.manual_start_entry.grid(row=2, column=1, sticky='ew', padx=5, pady=2)
        self.manual_start_entry.insert(0, "09:00 AM")

        # End Time
        ttk.Label(form_frame, text="End Time (HH:MM AM/PM):").grid(row=3, column=0, sticky='w', pady=2)
        self.manual_end_entry = ttk.Entry(form_frame)
        self.manual_end_entry.grid(row=3, column=1, sticky='ew', padx=5, pady=2)
        self.manual_end_entry.insert(0, "05:00 PM")
        
        # Decimal Hours (hidden by default)
        self.manual_decimal_label = ttk.Label(form_frame, text="Hours (decimal):")
        self.manual_decimal_label.grid(row=4, column=0, sticky='w', pady=2)
        self.manual_decimal_label.grid_remove()  # Hide initially
        
        self.manual_decimal_entry = ttk.Entry(form_frame)
        self.manual_decimal_entry.grid(row=4, column=1, sticky='ew', padx=5, pady=2)
        self.manual_decimal_entry.grid_remove()  # Hide initially
        
        # Helper text for decimal entry
        self.manual_decimal_help = ttk.Label(form_frame, text="Examples: 1.5, 0.75, 2.25", 
                                            font=('Arial', 8), foreground='gray')
        self.manual_decimal_help.grid(row=5, column=1, sticky='w', padx=5)
        self.manual_decimal_help.grid_remove()  # Hide initially

        # Task
        ttk.Label(form_frame, text="Task:").grid(row=6, column=0, sticky='w', pady=2)
        self.manual_task_combo = ttk.Combobox(form_frame, state='readonly')
        self.manual_task_combo.grid(row=6, column=1, sticky='ew', padx=5, pady=2)

        # Description
        ttk.Label(form_frame, text="Description:").grid(row=7, column=0, sticky='nw', pady=2)
        self.manual_desc_text = tk.Text(form_frame, height=3)
        self.manual_desc_text.grid(row=7, column=1, sticky='ew', padx=5, pady=2)

        form_frame.columnconfigure(1, weight=1)

        # Manual entry buttons
        manual_button_frame = ttk.Frame(manual_frame)
        manual_button_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(manual_button_frame, text="Add Entry", command=self.add_manual_entry).pack(side='left', padx=5)
        ttk.Button(manual_button_frame, text="Clear", command=self.clear_manual_entry_form).pack(side='left', padx=5)
        
        # Daily Totals Section
        daily_frame = ttk.LabelFrame(timer_frame, text="Today's Time by Client")
        daily_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Text widget for displaying daily totals
        daily_text_frame = ttk.Frame(daily_frame)
        daily_text_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.daily_totals_text = tk.Text(daily_text_frame, height=6, wrap='word', 
                                         font=('Courier', 10), state='disabled')
        self.daily_totals_text.pack(side='left', fill='both', expand=True)
        
        # Scrollbar for daily totals
        daily_scrollbar = ttk.Scrollbar(daily_text_frame, command=self.daily_totals_text.yview)
        daily_scrollbar.pack(side='right', fill='y')
        self.daily_totals_text.config(yscrollcommand=daily_scrollbar.set)
        
        # Buttons for daily totals
        daily_button_frame = ttk.Frame(daily_frame)
        daily_button_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(daily_button_frame, text="Refresh Totals", 
                  command=self.update_daily_totals_display).pack(side='left', padx=5)
        ttk.Button(daily_button_frame, text="Reset Daily Totals", 
                  command=self.reset_daily_totals).pack(side='left', padx=5)

    def create_clients_tab(self):
        # Clients tab
        clients_frame = ttk.Frame(self.notebook)
        self.notebook.add(clients_frame, text="Clients")

        # Client form
        client_form = ttk.LabelFrame(clients_frame, text="Client Information")
        client_form.pack(fill='x', padx=10, pady=10)

        form_frame = ttk.Frame(client_form)
        form_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, sticky='w', pady=2)
        self.client_name_entry = ttk.Entry(form_frame)
        self.client_name_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=2)

        ttk.Label(form_frame, text="Company:").grid(row=1, column=0, sticky='w', pady=2)
        self.client_company_entry = ttk.Entry(form_frame)
        self.client_company_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=2)

        ttk.Label(form_frame, text="Email:").grid(row=2, column=0, sticky='w', pady=2)
        self.client_email_entry = ttk.Entry(form_frame)
        self.client_email_entry.grid(row=2, column=1, sticky='ew', padx=5, pady=2)

        ttk.Label(form_frame, text="Phone:").grid(row=3, column=0, sticky='w', pady=2)
        self.client_phone_entry = ttk.Entry(form_frame)
        self.client_phone_entry.grid(row=3, column=1, sticky='ew', padx=5, pady=2)

        ttk.Label(form_frame, text="Address:").grid(row=4, column=0, sticky='nw', pady=2)
        self.client_address_text = tk.Text(form_frame, height=3)
        self.client_address_text.grid(row=4, column=1, sticky='ew', padx=5, pady=2)

        form_frame.columnconfigure(1, weight=1)

        # Client buttons
        button_frame = ttk.Frame(client_form)
        button_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(button_frame, text="Add Client", command=self.add_client).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Update Client", command=self.update_client).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_client_form).pack(side='left', padx=5)

        # Client list
        list_frame = ttk.LabelFrame(clients_frame, text="Clients")
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.client_tree = ttk.Treeview(list_frame, columns=('ID', 'Name', 'Company', 'Email', 'Phone'),
                                        show='headings')
        self.client_tree.heading('ID', text='ID')
        self.client_tree.heading('Name', text='Name')
        self.client_tree.heading('Company', text='Company')
        self.client_tree.heading('Email', text='Email')
        self.client_tree.heading('Phone', text='Phone')

        self.client_tree.column('ID', width=50)
        self.client_tree.column('Name', width=150)
        self.client_tree.column('Company', width=150)
        self.client_tree.column('Email', width=200)
        self.client_tree.column('Phone', width=100)

        self.client_tree.pack(fill='both', expand=True, padx=10, pady=10)
        self.client_tree.bind('<<TreeviewSelect>>', self.on_client_select)

        # Client buttons
        client_button_frame = ttk.Frame(list_frame)
        client_button_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(client_button_frame, text="Delete Client", command=self.delete_client).pack(side='left', padx=5)

    def create_projects_tab(self):
        # Projects tab
        projects_frame = ttk.Frame(self.notebook)
        self.notebook.add(projects_frame, text="Projects")

        # Project form
        project_form = ttk.LabelFrame(projects_frame, text="Project Information")
        project_form.pack(fill='x', padx=10, pady=10)

        form_frame = ttk.Frame(project_form)
        form_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(form_frame, text="Client:").grid(row=0, column=0, sticky='w', pady=2)
        self.project_client_combo = ttk.Combobox(form_frame, state='readonly')
        self.project_client_combo.grid(row=0, column=1, sticky='ew', padx=5, pady=2)

        ttk.Label(form_frame, text="Name:").grid(row=1, column=0, sticky='w', pady=2)
        self.project_name_entry = ttk.Entry(form_frame)
        self.project_name_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=2)

        ttk.Label(form_frame, text="Description:").grid(row=2, column=0, sticky='nw', pady=2)
        self.project_desc_text = tk.Text(form_frame, height=3)
        self.project_desc_text.grid(row=2, column=1, sticky='ew', padx=5, pady=2)

        # Project billing options
        billing_frame = ttk.Frame(form_frame)
        billing_frame.grid(row=3, column=1, sticky='ew', padx=5, pady=2)

        self.project_billing_var = tk.StringVar(value="hourly")
        ttk.Radiobutton(billing_frame, text="Hourly Rate", variable=self.project_billing_var,
                        value="hourly", command=self.toggle_project_billing).pack(side='left')
        ttk.Radiobutton(billing_frame, text="Lump Sum", variable=self.project_billing_var,
                        value="lump_sum", command=self.toggle_project_billing).pack(side='left', padx=10)

        ttk.Label(form_frame, text="Rate/Amount:").grid(row=4, column=0, sticky='w', pady=2)
        self.project_rate_entry = ttk.Entry(form_frame)
        self.project_rate_entry.grid(row=4, column=1, sticky='ew', padx=5, pady=2)

        form_frame.columnconfigure(1, weight=1)

        # Project buttons
        button_frame = ttk.Frame(project_form)
        button_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(button_frame, text="Add Project", command=self.add_project).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Update Project", command=self.update_project).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_project_form).pack(side='left', padx=5)

        # Project list
        list_frame = ttk.LabelFrame(projects_frame, text="Projects")
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.project_tree = ttk.Treeview(list_frame, columns=('ID', 'Client', 'Name', 'Type', 'Rate'),
                                         show='headings')
        self.project_tree.heading('ID', text='ID')
        self.project_tree.heading('Client', text='Client')
        self.project_tree.heading('Name', text='Project')
        self.project_tree.heading('Type', text='Billing Type')
        self.project_tree.heading('Rate', text='Rate/Amount')

        self.project_tree.column('ID', width=50)
        self.project_tree.column('Client', width=150)
        self.project_tree.column('Name', width=200)
        self.project_tree.column('Type', width=100)
        self.project_tree.column('Rate', width=100)

        self.project_tree.pack(fill='both', expand=True, padx=10, pady=10)
        self.project_tree.bind('<<TreeviewSelect>>', self.on_project_select)

        # Project buttons
        project_button_frame = ttk.Frame(list_frame)
        project_button_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(project_button_frame, text="Delete Project", command=self.delete_project).pack(side='left', padx=5)

    def create_tasks_tab(self):
        # Tasks tab
        tasks_frame = ttk.Frame(self.notebook)
        self.notebook.add(tasks_frame, text="Tasks")

        # Task form
        task_form = ttk.LabelFrame(tasks_frame, text="Task Information")
        task_form.pack(fill='x', padx=10, pady=10)

        form_frame = ttk.Frame(task_form)
        form_frame.pack(fill='x', padx=10, pady=10)

        # Client selector
        ttk.Label(form_frame, text="Client:").grid(row=0, column=0, sticky='w', pady=2)
        self.task_client_combo = ttk.Combobox(form_frame, state='readonly')
        self.task_client_combo.grid(row=0, column=1, sticky='ew', padx=5, pady=2)
        self.task_client_combo.bind('<<ComboboxSelected>>', self.on_task_client_select)

        # Project selector
        ttk.Label(form_frame, text="Project:").grid(row=1, column=0, sticky='w', pady=2)
        self.task_project_combo = ttk.Combobox(form_frame, state='readonly')
        self.task_project_combo.grid(row=1, column=1, sticky='ew', padx=5, pady=2)

        ttk.Label(form_frame, text="Name:").grid(row=2, column=0, sticky='w', pady=2)
        self.task_name_entry = ttk.Entry(form_frame)
        self.task_name_entry.grid(row=2, column=1, sticky='ew', padx=5, pady=2)

        ttk.Label(form_frame, text="Description:").grid(row=3, column=0, sticky='nw', pady=2)
        self.task_desc_text = tk.Text(form_frame, height=3)
        self.task_desc_text.grid(row=3, column=1, sticky='ew', padx=5, pady=2)
        
        # Global task checkbox
        global_frame = ttk.Frame(form_frame)
        global_frame.grid(row=4, column=0, columnspan=2, sticky='w', pady=10)

        self.task_global_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            global_frame,
            text="[GLOBAL] Make this available for all projects",
            variable=self.task_global_var,
            command=self.toggle_task_project_field
        ).pack(side='left')

        # Task billing options
        billing_frame = ttk.Frame(form_frame)
        billing_frame.grid(row=5, column=1, sticky='ew', padx=5, pady=2)

        self.task_billing_var = tk.StringVar(value="hourly")
        ttk.Radiobutton(billing_frame, text="Hourly Rate", variable=self.task_billing_var,
                        value="hourly", command=self.toggle_task_billing).pack(side='left')
        ttk.Radiobutton(billing_frame, text="Lump Sum", variable=self.task_billing_var,
                        value="lump_sum", command=self.toggle_task_billing).pack(side='left', padx=10)

        ttk.Label(form_frame, text="Rate/Amount:").grid(row=6, column=0, sticky='w', pady=2)
        self.task_rate_entry = ttk.Entry(form_frame)
        self.task_rate_entry.grid(row=6, column=1, sticky='ew', padx=5, pady=2)

        form_frame.columnconfigure(1, weight=1)

        # Task buttons
        button_frame = ttk.Frame(task_form)
        button_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(button_frame, text="Add Task", command=self.add_task).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Update Task", command=self.update_task).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_task_form).pack(side='left', padx=5)

        # Task list
        list_frame = ttk.LabelFrame(tasks_frame, text="Tasks")
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.task_tree = ttk.Treeview(list_frame, columns=('Type', 'ID', 'Extra', 'Billing', 'Rate'))
        self.task_tree.heading('#0', text='Hierarchy')
        self.task_tree.heading('Type', text='Type')
        self.task_tree.heading('ID', text='ID')
        self.task_tree.heading('Extra', text='')
        self.task_tree.heading('Billing', text='Billing Type')
        self.task_tree.heading('Rate', text='Rate/Amount')

        self.task_tree.column('#0', width=300)
        self.task_tree.column('Type', width=100)
        self.task_tree.column('ID', width=50)
        self.task_tree.column('Extra', width=100)
        self.task_tree.column('Billing', width=100)
        self.task_tree.column('Rate', width=100)

        self.task_tree.pack(fill='both', expand=True, padx=10, pady=10)
        self.task_tree.bind('<<TreeviewSelect>>', self.on_task_select)

        # Task buttons
        task_button_frame = ttk.Frame(list_frame)
        task_button_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(task_button_frame, text="Delete Task", command=self.delete_task).pack(side='left', padx=5)

    def create_time_entries_tab(self):
        # Time entries tab
        entries_frame = ttk.Frame(self.notebook)
        self.notebook.add(entries_frame, text="Time Entries")

        # Time entries list with grouping
        list_frame = ttk.LabelFrame(entries_frame, text="Time Entries (Grouped by Client > Project > Task)")
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Filter controls
        filter_frame = ttk.Frame(list_frame)
        filter_frame.pack(fill='x', padx=10, pady=(5, 0))
        
        ttk.Label(filter_frame, text="Show:", font=('Arial', 9, 'bold')).pack(side='left', padx=5)
        
        self.time_entries_filter_var = tk.StringVar(value="unbilled")
        ttk.Radiobutton(filter_frame, text="✅ Unbilled Only", 
                       variable=self.time_entries_filter_var, value="unbilled",
                       command=self.refresh_time_entries).pack(side='left', padx=5)
        ttk.Radiobutton(filter_frame, text="💰 Billed Only", 
                       variable=self.time_entries_filter_var, value="billed",
                       command=self.refresh_time_entries).pack(side='left', padx=5)
        ttk.Radiobutton(filter_frame, text="📋 All Entries", 
                       variable=self.time_entries_filter_var, value="all",
                       command=self.refresh_time_entries).pack(side='left', padx=5)
        
        # Add instruction label - NO bottom padding
        instruction_label = ttk.Label(list_frame, 
            text="💡 Click the ▶ arrows to expand/collapse groups and view individual entries with descriptions",
            font=('Arial', 9, 'italic'), foreground='#666')
        instruction_label.pack(anchor='w', padx=10, pady=(3, 3))
        
        # Entry buttons - MINIMAL spacing
        entry_button_frame = ttk.Frame(list_frame)
        entry_button_frame.pack(fill='x', padx=10, pady=(0, 5))

        ttk.Button(entry_button_frame, text="⚠️ Use Invoices Tab Instead",
                   command=lambda: messagebox.showinfo("Use Invoices Tab", 
                                                       "Please use the 'Invoices' tab for generating invoices.\n\n" +
                                                       "The new Invoices tab has better filtering and preview features!"),
                   state='disabled').pack(side='left', padx=5)
        ttk.Button(entry_button_frame, text="Edit Entry",
                   command=self.edit_time_entry).pack(side='left', padx=5)
        ttk.Button(entry_button_frame, text="Delete Entry",
                   command=self.delete_time_entry).pack(side='left', padx=5)
        ttk.Button(entry_button_frame, text="📊 Export to Excel",
                   command=self.export_time_entries_to_excel).pack(side='left', padx=5)
        
        # Create a frame for tree and scrollbar IMMEDIATELY after buttons
        tree_container = ttk.Frame(list_frame)
        tree_container.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Create tree with hierarchical display
        self.entries_tree = ttk.Treeview(tree_container, columns=('Type', 'Name', 'Start', 'Duration', 'Description'), 
                                        selectmode='extended')
        
        # Configure columns
        self.entries_tree.heading('#0', text='Hierarchy')  # Tree column
        self.entries_tree.heading('Type', text='Type')
        self.entries_tree.heading('Name', text='Details')
        self.entries_tree.heading('Start', text='Start Time')
        self.entries_tree.heading('Duration', text='Duration')
        self.entries_tree.heading('Description', text='Description')

        self.entries_tree.column('#0', width=250)  # Tree hierarchy column
        self.entries_tree.column('Type', width=80)
        self.entries_tree.column('Name', width=150)
        self.entries_tree.column('Start', width=150)
        self.entries_tree.column('Duration', width=100)
        self.entries_tree.column('Description', width=250)
        
        # Add scrollbar
        tree_scroll = ttk.Scrollbar(tree_container, orient='vertical', command=self.entries_tree.yview)
        self.entries_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.entries_tree.pack(side='left', fill='both', expand=True)
        tree_scroll.pack(side='right', fill='y')

    def create_company_tab(self):
        # Company info tab
        company_frame = ttk.Frame(self.notebook)
        self.notebook.add(company_frame, text="Company Info")

        # Company form
        company_form = ttk.LabelFrame(company_frame, text="Company Information (For Invoices)")
        company_form.pack(fill='both', expand=True, padx=10, pady=10)

        form_frame = ttk.Frame(company_form)
        form_frame.pack(fill='both', expand=True, padx=10, pady=10)

        ttk.Label(form_frame, text="Company Name:").grid(row=0, column=0, sticky='w', pady=2)
        self.company_name_entry = ttk.Entry(form_frame)
        self.company_name_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=2)

        ttk.Label(form_frame, text="Address:").grid(row=1, column=0, sticky='nw', pady=2)
        self.company_address_text = tk.Text(form_frame, height=3)
        self.company_address_text.grid(row=1, column=1, sticky='ew', padx=5, pady=2)

        ttk.Label(form_frame, text="Phone:").grid(row=2, column=0, sticky='w', pady=2)
        self.company_phone_entry = ttk.Entry(form_frame)
        self.company_phone_entry.grid(row=2, column=1, sticky='ew', padx=5, pady=2)

        ttk.Label(form_frame, text="Email:").grid(row=3, column=0, sticky='w', pady=2)
        self.company_email_entry = ttk.Entry(form_frame)
        self.company_email_entry.grid(row=3, column=1, sticky='ew', padx=5, pady=2)

        ttk.Label(form_frame, text="Logo:").grid(row=4, column=0, sticky='w', pady=2)
        logo_frame = ttk.Frame(form_frame)
        logo_frame.grid(row=4, column=1, sticky='ew', padx=5, pady=2)

        self.logo_path_var = tk.StringVar()
        ttk.Entry(logo_frame, textvariable=self.logo_path_var, state='readonly').pack(side='left', fill='x',
                                                                                      expand=True)
        ttk.Button(logo_frame, text="Browse", command=self.browse_logo).pack(side='left', padx=5)

        # Website
        ttk.Label(form_frame, text="Website:").grid(row=5, column=0, sticky='w', pady=2)
        self.company_website_entry = ttk.Entry(form_frame)
        self.company_website_entry.grid(row=5, column=1, sticky='ew', padx=5, pady=2)

        # Payment Terms
        ttk.Label(form_frame, text="Payment Terms:").grid(row=6, column=0, sticky='w', pady=2)
        self.company_payment_terms_entry = ttk.Entry(form_frame, width=50)
        self.company_payment_terms_entry.grid(row=6, column=1, sticky='ew', padx=5, pady=2)

        # Thank You Message
        ttk.Label(form_frame, text="Thank You Message:").grid(row=7, column=0, sticky='w', pady=2)
        self.company_thank_you_entry = ttk.Entry(form_frame, width=50)
        self.company_thank_you_entry.grid(row=7, column=1, sticky='ew', padx=5, pady=2)

        form_frame.columnconfigure(1, weight=1)

        # Company buttons
        button_frame = ttk.Frame(company_form)
        button_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(button_frame, text="Save Company Info", command=self.save_company_info).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Load Current Info", command=self.load_company_info).pack(side='left', padx=5)

    def create_invoice_tab(self):
        # Invoice tab - COMPLETELY REDESIGNED
        invoice_frame = ttk.Frame(self.notebook)
        self.notebook.add(invoice_frame, text="Invoices")

        # Selection section at top
        selection_frame = ttk.LabelFrame(invoice_frame, text="📋 Invoice Selection")
        selection_frame.pack(fill='x', padx=10, pady=10)

        form_frame = ttk.Frame(selection_frame)
        form_frame.pack(fill='x', padx=10, pady=10)

        # Client selection
        ttk.Label(form_frame, text="Client:").grid(row=0, column=0, sticky='w', pady=5)
        self.invoice_client_combo = ttk.Combobox(form_frame, state='readonly', width=30)
        self.invoice_client_combo.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        self.invoice_client_combo.bind('<<ComboboxSelected>>', self.on_invoice_client_select)

        # Project selection (optional)
        ttk.Label(form_frame, text="Project (optional):").grid(row=0, column=2, sticky='w', pady=5, padx=(20, 0))
        self.invoice_project_combo = ttk.Combobox(form_frame, state='readonly', width=30)
        self.invoice_project_combo.grid(row=0, column=3, sticky='w', padx=5, pady=5)
        self.invoice_project_combo.bind('<<ComboboxSelected>>', self.on_invoice_project_select)

        # Date filter options
        ttk.Label(form_frame, text="Filter:").grid(row=1, column=0, sticky='w', pady=5)
        filter_options_frame = ttk.Frame(form_frame)
        filter_options_frame.grid(row=1, column=1, columnspan=3, sticky='w', padx=5, pady=5)

        self.invoice_filter_var = tk.StringVar(value="all_uninvoiced")
        ttk.Radiobutton(filter_options_frame, text="All Uninvoiced", 
                       variable=self.invoice_filter_var, value="all_uninvoiced",
                       command=self.toggle_invoice_date_filter).pack(side='left', padx=5)
        ttk.Radiobutton(filter_options_frame, text="Date Range", 
                       variable=self.invoice_filter_var, value="date_range",
                       command=self.toggle_invoice_date_filter).pack(side='left', padx=5)

        # Date range inputs (hidden by default)
        self.date_range_frame = ttk.Frame(filter_options_frame)
        self.date_range_frame.pack(side='left', padx=20)

        self.invoice_start_date = ttk.Entry(self.date_range_frame, width=12)
        self.invoice_start_date.pack(side='left')
        self.invoice_start_date.insert(0, (datetime.now() - timedelta(days=30)).strftime("%m/%d/%y"))

        ttk.Label(self.date_range_frame, text=" to ").pack(side='left', padx=2)

        self.invoice_end_date = ttk.Entry(self.date_range_frame, width=12)
        self.invoice_end_date.pack(side='left')
        self.invoice_end_date.insert(0, datetime.now().strftime("%m/%d/%y"))
        
        # Hide date range by default
        self.date_range_frame.pack_forget()

        # Load entries button
        button_row = ttk.Frame(selection_frame)
        button_row.pack(fill='x', padx=10, pady=(0, 10))
        
        ttk.Button(button_row, text="🔍 Load Time Entries", 
                  command=self.load_invoiceable_entries).pack(side='left', padx=5)
        ttk.Button(button_row, text="🔄 Refresh", 
                  command=self.refresh_invoice_combos).pack(side='left', padx=5)

        # Time entries display section
        entries_frame = ttk.LabelFrame(invoice_frame, text="⏱️ Select Time Entries to Invoice")
        entries_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Info label
        info_label = ttk.Label(entries_frame, 
            text="💡 Select individual time entries below, then click 'Preview Invoice' to generate",
            font=('Arial', 9, 'italic'), foreground='#666')
        info_label.pack(anchor='w', padx=10, pady=(5, 0))

        # Tree for selectable time entries
        tree_container = ttk.Frame(entries_frame)
        tree_container.pack(fill='both', expand=True, padx=10, pady=(5, 10))

        self.invoice_entries_tree = ttk.Treeview(tree_container, 
            columns=('Date', 'Project', 'Task', 'Duration', 'Description'), 
            selectmode='extended')
        
        self.invoice_entries_tree.heading('#0', text='Select')
        self.invoice_entries_tree.heading('Date', text='Date')
        self.invoice_entries_tree.heading('Project', text='Project')
        self.invoice_entries_tree.heading('Task', text='Task')
        self.invoice_entries_tree.heading('Duration', text='Duration')
        self.invoice_entries_tree.heading('Description', text='Description')

        self.invoice_entries_tree.column('#0', width=50)
        self.invoice_entries_tree.column('Date', width=100)
        self.invoice_entries_tree.column('Project', width=150)
        self.invoice_entries_tree.column('Task', width=150)
        self.invoice_entries_tree.column('Duration', width=100)
        self.invoice_entries_tree.column('Description', width=250)

        tree_scroll = ttk.Scrollbar(tree_container, orient='vertical', 
                                   command=self.invoice_entries_tree.yview)
        self.invoice_entries_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.invoice_entries_tree.pack(side='left', fill='both', expand=True)
        tree_scroll.pack(side='right', fill='y')

        # Summary and action buttons
        summary_frame = ttk.Frame(entries_frame)
        summary_frame.pack(fill='x', padx=10, pady=10)

        self.invoice_summary_label = ttk.Label(summary_frame, 
            text="No entries loaded. Select a client and click 'Load Time Entries'.",
            font=('Arial', 10))
        self.invoice_summary_label.pack(side='left', padx=10)

        ttk.Button(summary_frame, text="📄 Preview Invoice", 
                  command=self.preview_invoice, 
                  style='Accent.TButton').pack(side='right', padx=5)
        ttk.Button(summary_frame, text="Select All", 
                  command=self.select_all_invoice_entries).pack(side='right', padx=5)
        ttk.Button(summary_frame, text="Deselect All", 
                  command=self.deselect_all_invoice_entries).pack(side='right', padx=5)

    # ADD THIS METHOD TO gui.py AFTER create_invoice_tab() method
    # This is the complete Billed Invoices tab implementation

    def create_billed_invoices_tab(self):
        """Create the Billed Invoices tab with Paid/Unpaid views"""
        billed_frame = ttk.Frame(self.notebook)
        self.notebook.add(billed_frame, text="💰 Billed Invoices")

        # Top control frame
        control_frame = ttk.Frame(billed_frame)
        control_frame.pack(fill='x', padx=10, pady=10)

        # View selector
        view_label_frame = ttk.LabelFrame(control_frame, text="View")
        view_label_frame.pack(side='left', padx=5)

        self.invoice_view_var = tk.StringVar(value="unpaid")
        ttk.Radiobutton(view_label_frame, text="Unpaid",
                        variable=self.invoice_view_var, value="unpaid",
                        command=self.refresh_billed_invoices).pack(side='left', padx=5, pady=5)
        ttk.Radiobutton(view_label_frame, text="Paid",
                        variable=self.invoice_view_var, value="paid",
                        command=self.refresh_billed_invoices).pack(side='left', padx=5, pady=5)
        ttk.Radiobutton(view_label_frame, text="All",
                        variable=self.invoice_view_var, value="all",
                        command=self.refresh_billed_invoices).pack(side='left', padx=5, pady=5)

        ttk.Button(control_frame, text="Refresh",
                   command=self.refresh_billed_invoices).pack(side='right', padx=5)

        # Invoice list
        list_frame = ttk.LabelFrame(billed_frame, text="Invoices")
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)

        tree_frame = ttk.Frame(list_frame)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.billed_invoices_tree = ttk.Treeview(tree_frame,
                                                 columns=('Invoice', 'Client', 'Date', 'Amount', 'Status', 'Paid Date'),
                                                 show='headings', selectmode='extended')

        self.billed_invoices_tree.heading('Invoice', text='Invoice #')
        self.billed_invoices_tree.heading('Client', text='Client')
        self.billed_invoices_tree.heading('Date', text='Invoice Date')
        self.billed_invoices_tree.heading('Amount', text='Amount')
        self.billed_invoices_tree.heading('Status', text='Status')
        self.billed_invoices_tree.heading('Paid Date', text='Date Paid')

        self.billed_invoices_tree.column('Invoice', width=150)
        self.billed_invoices_tree.column('Client', width=150)
        self.billed_invoices_tree.column('Date', width=100)
        self.billed_invoices_tree.column('Amount', width=100)
        self.billed_invoices_tree.column('Status', width=80)
        self.billed_invoices_tree.column('Paid Date', width=100)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.billed_invoices_tree.yview)
        self.billed_invoices_tree.configure(yscrollcommand=vsb.set)
        self.billed_invoices_tree.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')

        # Action buttons
        action_frame = ttk.Frame(billed_frame)
        action_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(action_frame, text="Mark as PAID",
                   command=self.mark_invoices_paid_dialog).pack(side='left', padx=5)
        ttk.Button(action_frame, text="Mark as UNPAID",
                   command=self.mark_invoices_unpaid).pack(side='left', padx=5)

        self.billed_summary_label = ttk.Label(action_frame, text="")
        self.billed_summary_label.pack(side='right', padx=10)

    # ADD THESE METHODS TO gui.py (at the end, before refresh_all_data)

    def refresh_billed_invoices(self):
        """Refresh the billed invoices list"""
        for item in self.billed_invoices_tree.get_children():
            self.billed_invoices_tree.delete(item)
        
        view = self.invoice_view_var.get()
        paid_status = 1 if view == "paid" else (0 if view == "unpaid" else None)
        
        invoices = self.db.get_billing_history(paid_status=paid_status)
        
        # Configure row colors
        self.billed_invoices_tree.tag_configure('paid', background='#d4edda')  # Light green
        self.billed_invoices_tree.tag_configure('unpaid', background='#fff3cd')  # Light yellow
        
        total = 0
        for inv in invoices:
            inv_num = inv[1]
            client = inv[3]
            date = inv[4][:10]
            amount = inv[7]
            is_paid = inv[12]
            date_paid = inv[13] if inv[13] else ""
            status = "PAID" if is_paid else "UNPAID"
            
            tag = 'paid' if is_paid else 'unpaid'
            self.billed_invoices_tree.insert('', 'end', values=(
                inv_num, client, date, f"${amount:.2f}", status, date_paid
            ), tags=(tag,))
            total += amount
        
        count = len(invoices)
        self.billed_summary_label.config(text=f"{count} invoices | Total: ${total:.2f}")

    def mark_invoices_paid_dialog(self):
        """Show dialog to mark invoices as paid"""
        selection = self.billed_invoices_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select invoices to mark as paid")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Mark Invoices as Paid")
        dialog.geometry("300x150")

        ttk.Label(dialog, text=f"Mark {len(selection)} invoice(s) as PAID?").pack(pady=10)
        ttk.Label(dialog, text="Date Paid (YYYY-MM-DD):").pack(pady=5)

        date_entry = ttk.Entry(dialog)
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        date_entry.pack(pady=5)

        def confirm():
            date_paid = date_entry.get().strip()
            if not date_paid:
                messagebox.showerror("Error", "Date is required")
                return

            for item in selection:
                values = self.billed_invoices_tree.item(item)['values']
                invoice_num = values[0]
                self.db.mark_invoice_paid(invoice_num, date_paid)

            dialog.destroy()
            self.refresh_billed_invoices()
            messagebox.showinfo("Success", f"{len(selection)} invoice(s) marked as PAID")

        ttk.Button(dialog, text="Confirm", command=confirm).pack(side='left', padx=20, pady=10)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).pack(side='right', padx=20, pady=10)

    def mark_invoices_unpaid(self):
        """Mark selected invoices as unpaid (undo)"""
        selection = self.billed_invoices_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select invoices to mark as unpaid")
            return

        if messagebox.askyesno("Confirm", f"Mark {len(selection)} invoice(s) as UNPAID?"):
            for item in selection:
                values = self.billed_invoices_tree.item(item)['values']
                invoice_num = values[0]
                self.db.mark_invoice_unpaid(invoice_num)

            self.refresh_billed_invoices()
            messagebox.showinfo("Success", f"{len(selection)} invoice(s) marked as UNPAID")

    # Timer methods
    def start_timer(self):
        if not self.timer_client_combo.get():
            messagebox.showerror("Error", "Please select a client first")
            return

        if not self.timer_project_combo.get():
            messagebox.showerror("Error", "Please select a project first")
            return

        if not self.timer_task_combo.get():
            messagebox.showerror("Error", "Please select a task first")
            return

        # Get task ID from the selected display text
        task_text = self.timer_task_combo.get()
        client_name = self.timer_client_combo.get()
        project_name = self.timer_project_combo.get()

        # Check if it's a global task
        if task_text.startswith('[GLOBAL] '):
            # Extract task name from "[GLOBAL] TaskName"
            task_name = task_text.replace('[GLOBAL] ', '')

            # Find the global task
            global_tasks = self.task_model.get_global_tasks()
            self.current_task_id = None

            for task in global_tasks:
                if task[2] == task_name:
                    self.current_task_id = task[0]
                    break
        else:
            # Regular project-specific task
            # Extract task name from "Client - Project - Task" format
            parts = task_text.split(' - ')
            if len(parts) >= 3:
                task_name = ' - '.join(parts[2:])
            else:
                messagebox.showerror("Error", "Invalid task format")
                return

            # Find the task by matching client, project, and task names
            tasks = self.task_model.get_all()
            self.current_task_id = None

            for task in tasks:
                if task[9] == client_name and task[8] == project_name and task[2] == task_name:
                    self.current_task_id = task[0]
                    break

        if not self.current_task_id:
            messagebox.showerror("Error", f"Could not find task: {task_name}")
            return

        try:
            # Start the timer
            self.timer_running = True
            self.timer_start_time = datetime.now()

            # Get current project ID for global tasks
            project_id = self.get_current_timer_project_id()
            self.time_entry_model.start_timer(self.current_task_id, project_id_override=project_id)

            # Update UI
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.timer_label.config(text="00:00:00", foreground='green')  # Reset and show green

            # Start timer thread
            self.update_timer_display()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start timer: {str(e)}")
            self.timer_running = False

    def stop_timer(self):
        if self.timer_running:
            # Calculate elapsed time BEFORE stopping
            elapsed_seconds = (datetime.now() - self.timer_start_time).total_seconds()
            
            # Get current client and project IDs for tracking
            client_id = self.get_current_timer_client_id()
            project_id = self.get_current_timer_project_id()
            
            # Stop the timer in database
            self.timer_running = False
            self.time_entry_model.stop_timer()

            # Update daily totals (both client and project)
            if client_id:
                if client_id not in self.daily_client_totals:
                    self.daily_client_totals[client_id] = 0
                self.daily_client_totals[client_id] += elapsed_seconds
                self.last_timer_client_id = client_id
                
                # Track project totals
                if project_id:
                    key = (client_id, project_id)
                    if key not in self.daily_project_totals:
                        self.daily_project_totals[key] = 0
                    self.daily_project_totals[key] += elapsed_seconds
                    self.last_timer_project_id = project_id
            
            # Store elapsed time for display
            self.last_timer_elapsed = elapsed_seconds
            
            # Update UI with FINAL time (don't reset to zero!)
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            self.update_timer_display_final()
            
            # Update daily totals display
            self.update_daily_totals_display()

            self.refresh_time_entries()
            
            # Show success with elapsed time
            hours = int(elapsed_seconds // 3600)
            minutes = int((elapsed_seconds % 3600) // 60)
            seconds = int(elapsed_seconds % 60)
            messagebox.showinfo("Success", 
                              f"Timer stopped and time entry saved\n\n" +
                              f"Time recorded: {hours:02d}:{minutes:02d}:{seconds:02d}")

    def update_timer_display(self):
        if self.timer_running and self.timer_start_time:
            elapsed = datetime.now() - self.timer_start_time
            hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            self.timer_label.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}", foreground='green')
            self.root.after(1000, self.update_timer_display)
    
    def update_timer_display_final(self):
        """Display final elapsed time after stopping (don't reset to zero)"""
        if self.last_timer_elapsed > 0:
            hours = int(self.last_timer_elapsed // 3600)
            minutes = int((self.last_timer_elapsed % 3600) // 60)
            seconds = int(self.last_timer_elapsed % 60)
            
            self.timer_label.config(
                text=f"Last: {hours:02d}:{minutes:02d}:{seconds:02d}",
                foreground='gray'
            )
        else:
            self.timer_label.config(text="00:00:00", foreground='black')

    def on_timer_client_select(self, event):
        client_name = self.timer_client_combo.get()
        if client_name:
            # Get client ID
            clients = self.client_model.get_all()
            client_id = None
            for client in clients:
                if client[1] == client_name:
                    client_id = client[0]
                    break

            if client_id:
                # Load projects for this client
                projects = self.project_model.get_by_client(client_id)
                self.timer_project_combo['values'] = [p[2] for p in projects]
                self.timer_project_combo.set('')
                self.timer_task_combo.set('')

    def on_timer_project_select(self, event):
        project_name = self.timer_project_combo.get()
        client_name = self.timer_client_combo.get()

        if project_name and client_name:
            # Get project ID by matching client and project names
            projects = self.project_model.get_all()
            project_id = None
            for project in projects:
                proj_client_name = project[9] if len(project) > 9 else None
                if proj_client_name == client_name and project[2] == project_name:
                    project_id = project[0]
                    break

            if project_id:
                # Load tasks for this project AND global tasks
                project_tasks = self.task_model.get_by_project(project_id)
                global_tasks = self.task_model.get_global_tasks()

                # Combine both lists
                all_tasks = list(global_tasks) + list(project_tasks)

                # Format task displays
                task_displays = []
                for t in all_tasks:
                    if t[1] is None:  # project_id is None means it's global
                        task_displays.append(f"[GLOBAL] {t[2]}")
                    else:
                        task_displays.append(f"{client_name} - {project_name} - {t[2]}")

                self.timer_task_combo['values'] = task_displays
                self.timer_task_combo.set('')
            else:
                self.timer_task_combo['values'] = []
                self.timer_task_combo.set('')


    def get_current_timer_client_id(self):
        """Get the client ID for the currently selected timer task"""
        try:
            client_name = self.timer_client_combo.get()
            if not client_name:
                return None
            
            clients = self.client_model.get_all()
            for client in clients:
                if client[1] == client_name:
                    return client[0]
            return None
        except:
            return None
    
    def get_current_timer_project_id(self):
        """Get the project ID for the currently selected timer project"""
        try:
            client_name = self.timer_client_combo.get()
            project_name = self.timer_project_combo.get()
            
            if not client_name or not project_name:
                return None
            
            # Get all projects and find matching one
            projects = self.project_model.get_all()
            for project in projects:
                # project structure: [0:id, ..., 9:client_name]
                proj_client_name = project[9] if len(project) > 9 else None
                if proj_client_name == client_name and project[2] == project_name:
                    return project[0]
            return None
        except:
            return None
    
    def update_daily_totals_display(self):
        """Update the daily totals display showing time accumulated per client with project breakdowns"""
        # Check if we need to reset for new day
        current_date = datetime.now().date()
        if current_date != self.session_date:
            self.daily_client_totals = {}
            self.daily_project_totals = {}
            self.session_date = current_date
        
        # Enable text widget for editing
        self.daily_totals_text.config(state='normal')
        self.daily_totals_text.delete('1.0', 'end')
        
        if not self.daily_client_totals:
            self.daily_totals_text.insert('1.0', 
                f"📊 Daily Time Tracker - {self.session_date.strftime('%B %d, %Y')}\n\n" +
                "No time tracked yet today.\n\n" +
                "Start a timer to begin tracking!")
        else:
            # Build header
            text = f"📊 Daily Time Tracker - {self.session_date.strftime('%B %d, %Y')}\n"
            text += "=" * 50 + "\n\n"
            
            # Calculate grand total
            grand_total_seconds = sum(self.daily_client_totals.values())
            grand_total_hours = grand_total_seconds / 3600
            
            # Get client and project names
            clients = self.client_model.get_all()
            client_dict = {c[0]: c[1] for c in clients}
            
            projects = self.project_model.get_all()
            project_dict = {p[0]: p[2] for p in projects}  # {project_id: project_name}
            
            # Group projects by client for display
            client_projects = {}  # {client_id: [(project_id, seconds), ...]}
            for (client_id, project_id), seconds in self.daily_project_totals.items():
                if client_id not in client_projects:
                    client_projects[client_id] = []
                client_projects[client_id].append((project_id, seconds))
            
            # Display each client with project breakdowns
            for client_id, total_seconds in sorted(self.daily_client_totals.items(), 
                                                   key=lambda x: x[1], reverse=True):
                client_name = client_dict.get(client_id, f"Client #{client_id}")
                hours = total_seconds / 3600
                
                # Format client total as HH:MM:SS and decimal hours
                h = int(total_seconds // 3600)
                m = int((total_seconds % 3600) // 60)
                s = int(total_seconds % 60)
                
                text += f"📌 {client_name}:  {h:02d}:{m:02d}:{s:02d}  ({hours:.2f} hrs)\n"
                
                # Show project breakdown if available
                if client_id in client_projects:
                    # Sort projects by time (most first)
                    sorted_projects = sorted(client_projects[client_id], 
                                           key=lambda x: x[1], reverse=True)
                    
                    for project_id, proj_seconds in sorted_projects:
                        project_name = project_dict.get(project_id, f"Project #{project_id}")
                        proj_hours = proj_seconds / 3600
                        
                        # Format project time
                        ph = int(proj_seconds // 3600)
                        pm = int((proj_seconds % 3600) // 60)
                        ps = int(proj_seconds % 60)
                        
                        text += f"    └─ {project_name}:  {ph:02d}:{pm:02d}:{ps:02d}  ({proj_hours:.2f} hrs)\n"
                
                text += "\n"  # Blank line between clients
            
            # Add grand total
            text += "=" * 50 + "\n"
            h = int(grand_total_seconds // 3600)
            m = int((grand_total_seconds % 3600) // 60)
            s = int(grand_total_seconds % 60)
            text += f"  TOTAL TODAY:  {h:02d}:{m:02d}:{s:02d}  ({grand_total_hours:.2f} hrs)"
            
            self.daily_totals_text.insert('1.0', text)
        
        # Disable editing
        self.daily_totals_text.config(state='disabled')
    
    def reset_daily_totals(self):
        """Manually reset daily totals"""
        if not self.daily_client_totals:
            messagebox.showinfo("Nothing to Reset", "No daily totals to reset.")
            return
        
        response = messagebox.askyesno(
            "Reset Daily Totals",
            "Are you sure you want to reset today's accumulated time?\n\n" +
            "This will only reset the daily display tracker.\n" +
            "Saved time entries will not be affected."
        )
        
        if response:
            self.daily_client_totals = {}
            self.daily_project_totals = {}
            self.last_timer_elapsed = 0
            self.update_daily_totals_display()
            self.timer_label.config(text="00:00:00", foreground='black')
            messagebox.showinfo("Reset Complete", "Daily totals have been reset.")
    
    def on_task_client_select(self, event):
        """When client is selected in tasks tab, populate projects"""
        client_name = self.task_client_combo.get()
        if client_name:
            # Get client ID
            clients = self.client_model.get_all()
            client_id = None
            for client in clients:
                if client[1] == client_name:
                    client_id = client[0]
                    break

            if client_id:
                # Load projects for this client
                projects = self.project_model.get_by_client(client_id)
                self.task_project_combo['values'] = [p[2] for p in projects]
                self.task_project_combo.set('')

    def toggle_manual_entry_mode(self):
        """Toggle between time range and decimal hour entry modes"""
        mode = self.manual_entry_mode.get()
        
        if mode == "time_range":
            # Show start/end time fields
            self.manual_start_entry.grid()
            self.manual_end_entry.grid()
            
            # Hide decimal fields
            self.manual_decimal_label.grid_remove()
            self.manual_decimal_entry.grid_remove()
            self.manual_decimal_help.grid_remove()
        else:  # decimal
            # Hide start/end time fields
            self.manual_start_entry.grid_remove()
            self.manual_end_entry.grid_remove()
            
            # Show decimal fields
            self.manual_decimal_label.grid()
            self.manual_decimal_entry.grid()
            self.manual_decimal_help.grid()
    
    def add_manual_entry(self):
        task_text = self.manual_task_combo.get()
        date_str = self.manual_date_entry.get().strip()
        description = self.manual_desc_text.get("1.0", tk.END).strip()
        mode = self.manual_entry_mode.get()

        if not task_text:
            messagebox.showerror("Error", "Please select a task")
            return

        try:
            # Parse date MM/DD/YY
            date_obj = datetime.strptime(date_str, "%m/%d/%y")
            
            if mode == "time_range":
                # Original time range mode
                start_str = self.manual_start_entry.get().strip()
                end_str = self.manual_end_entry.get().strip()
                
                # Parse times HH:MM AM/PM
                start_time_obj = datetime.strptime(f"{date_str} {start_str}", "%m/%d/%y %I:%M %p")
                end_time_obj = datetime.strptime(f"{date_str} {end_str}", "%m/%d/%y %I:%M %p")

                if end_time_obj <= start_time_obj:
                    messagebox.showerror("Error", "End time must be after start time")
                    return
            
            else:  # decimal mode
                # Parse decimal hours
                decimal_str = self.manual_decimal_entry.get().strip()
                
                if not decimal_str:
                    messagebox.showerror("Error", "Please enter hours in decimal format")
                    return
                
                try:
                    decimal_hours = float(decimal_str)
                    
                    if decimal_hours <= 0:
                        messagebox.showerror("Error", "Hours must be greater than 0")
                        return
                    
                    if decimal_hours > 24:
                        messagebox.showerror("Error", "Hours cannot exceed 24 in a single entry")
                        return
                    
                except ValueError:
                    messagebox.showerror("Error", 
                                       f"Invalid decimal format: '{decimal_str}'\n\n" +
                                       "Examples: 1.5, 0.75, 2.25")
                    return
                
                # Calculate start and end times from decimal hours
                # Use 9 AM as default start time for decimal entries
                start_time_obj = datetime.strptime(f"{date_str} 09:00 AM", "%m/%d/%y %I:%M %p")
                
                # Calculate end time by adding decimal hours
                duration = timedelta(hours=decimal_hours)
                end_time_obj = start_time_obj + duration

        except ValueError as e:
            messagebox.showerror("Error",
                                 f"Invalid date/time format.\nUse MM/DD/YY for date and HH:MM AM/PM for time.\nError: {str(e)}")
            return

        # Get task ID
        tasks = self.task_model.get_all()
        task_id = None
        for task in tasks:
            client_name = task[9]
            project_name = task[8]
            task_display = f"{client_name} - {project_name} - {task[2]}"
            if task_display == task_text:
                task_id = task[0]
                break

        if not task_id:
            messagebox.showerror("Error", "Invalid task selected")
            return

        self.time_entry_model.add_manual_entry(task_id, start_time_obj, end_time_obj, description)
        self.refresh_time_entries()
        
        # Calculate duration for display and daily totals
        duration = end_time_obj - start_time_obj
        hours = duration.total_seconds() / 3600
        duration_seconds = duration.total_seconds()
        
        # Update daily totals if entry is for today
        entry_date = start_time_obj.date()
        today = datetime.now().date()
        
        if entry_date == today:
            # Get client and project IDs from the task
            tasks = self.task_model.get_all()
            for task in tasks:
                client_name = task[9]
                project_name = task[8]
                task_display = f"{client_name} - {project_name} - {task[2]}"
                if task_display == task_text:
                    project_id = task[1]
                    # Get client_id from project
                    projects = self.project_model.get_all()
                    for project in projects:
                        if project[0] == project_id:
                            client_id = project[1]
                            
                            # Update client totals
                            if client_id not in self.daily_client_totals:
                                self.daily_client_totals[client_id] = 0
                            self.daily_client_totals[client_id] += duration_seconds
                            
                            # Update project totals
                            key = (client_id, project_id)
                            if key not in self.daily_project_totals:
                                self.daily_project_totals[key] = 0
                            self.daily_project_totals[key] += duration_seconds
                            
                            break
                    break
            
            # Refresh the daily totals display
            self.update_daily_totals_display()
        
        # Show success message with details
        if mode == "decimal":
            messagebox.showinfo("Success", 
                              f"Time entry added successfully\n\n" +
                              f"Duration: {decimal_hours} hours\n" +
                              f"Date: {date_obj.strftime('%m/%d/%y')}")
        else:
            messagebox.showinfo("Success", 
                              f"Time entry added successfully\n\n" +
                              f"Duration: {hours:.2f} hours\n" +
                              f"From: {start_time_obj.strftime('%I:%M %p')} to {end_time_obj.strftime('%I:%M %p')}")
        
        self.clear_manual_entry_form()

    def clear_manual_entry_form(self):
        self.manual_date_entry.delete(0, tk.END)
        self.manual_date_entry.insert(0, datetime.now().strftime("%m/%d/%y"))
        self.manual_start_entry.delete(0, tk.END)
        self.manual_start_entry.insert(0, "09:00 AM")
        self.manual_end_entry.delete(0, tk.END)
        self.manual_end_entry.insert(0, "05:00 PM")
        self.manual_decimal_entry.delete(0, tk.END)
        self.manual_task_combo.set('')
        self.manual_desc_text.delete("1.0", tk.END)

    # Client methods
    def add_client(self):
        name = self.client_name_entry.get().strip()
        company = self.client_company_entry.get().strip()
        email = self.client_email_entry.get().strip()
        phone = self.client_phone_entry.get().strip()
        address = self.client_address_text.get("1.0", tk.END).strip()

        if not name:
            messagebox.showerror("Error", "Client name is required")
            return

        # CHECK FOR DUPLICATE CLIENT NAME
        existing_clients = self.client_model.get_all()
        for client in existing_clients:
            if client[1].lower() == name.lower():  # Case-insensitive comparison
                messagebox.showerror("Error", f"Client '{name}' already exists")
                return

        self.client_model.create(name, company, email, phone, address)
        self.clear_client_form()
        self.refresh_clients()
        self.refresh_combos()
        messagebox.showinfo("Success", "Client added successfully")

    def update_client(self):
        selection = self.client_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a client to update")
            return

        client_id = self.client_tree.item(selection[0])['values'][0]
        name = self.client_name_entry.get().strip()
        company = self.client_company_entry.get().strip()
        email = self.client_email_entry.get().strip()
        phone = self.client_phone_entry.get().strip()
        address = self.client_address_text.get("1.0", tk.END).strip()

        if not name:
            messagebox.showerror("Error", "Client name is required")
            return

        self.client_model.update(client_id, name, company, email, phone, address)
        self.clear_client_form()
        self.refresh_clients()
        self.refresh_combos()
        messagebox.showinfo("Success", "Client updated successfully")

    def delete_client(self):
        selection = self.client_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a client to delete")
            return

        if messagebox.askyesno("Confirm",
                               "Delete this client? This will also delete all associated projects, tasks, and time entries."):
            client_id = self.client_tree.item(selection[0])['values'][0]
            self.client_model.delete(client_id)
            self.refresh_clients()
            self.refresh_combos()
            messagebox.showinfo("Success", "Client deleted successfully")

    def clear_client_form(self):
        self.client_name_entry.delete(0, tk.END)
        self.client_company_entry.delete(0, tk.END)
        self.client_email_entry.delete(0, tk.END)
        self.client_phone_entry.delete(0, tk.END)
        self.client_address_text.delete("1.0", tk.END)

    def on_client_select(self, event):
        selection = self.client_tree.selection()
        if selection:
            client_id = self.client_tree.item(selection[0])['values'][0]
            client = self.client_model.get_by_id(client_id)
            if client:
                self.client_name_entry.delete(0, tk.END)
                self.client_name_entry.insert(0, client[1])

                self.client_company_entry.delete(0, tk.END)
                self.client_company_entry.insert(0, client[2] or "")

                self.client_email_entry.delete(0, tk.END)
                self.client_email_entry.insert(0, client[3] or "")

                self.client_phone_entry.delete(0, tk.END)
                self.client_phone_entry.insert(0, client[4] or "")

                self.client_address_text.delete("1.0", tk.END)
                self.client_address_text.insert("1.0", client[5] or "")

    # Project methods
    def add_project(self):
        client_text = self.project_client_combo.get()
        name = self.project_name_entry.get().strip()
        description = self.project_desc_text.get("1.0", tk.END).strip()

        if not client_text or not name:
            messagebox.showerror("Error", "Client and project name are required")
            return

        # Get client ID by name
        clients = self.client_model.get_all()
        client_id = None
        for client in clients:
            if client[1] == client_text:
                client_id = client[0]
                break

        if not client_id:
            messagebox.showerror("Error", "Invalid client selected")
            return

        # CHECK FOR DUPLICATE PROJECT NAME UNDER SAME CLIENT
        existing_projects = self.project_model.get_by_client(client_id)
        for proj in existing_projects:
            if proj[2].lower() == name.lower():  # Case-insensitive comparison
                messagebox.showerror("Error", f"Project '{name}' already exists for this client")
                return

        rate = float(self.project_rate_entry.get() or 0)
        is_lump_sum = self.project_billing_var.get() == "lump_sum"

        if is_lump_sum:
            self.project_model.create(client_id, name, description, 0, True, rate)
        else:
            self.project_model.create(client_id, name, description, rate, False, 0)

        self.clear_project_form()
        self.refresh_projects()
        self.refresh_combos()
        messagebox.showinfo("Success", "Project added successfully")

    def update_project(self):
        selection = self.project_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a project to update")
            return

        project_id = self.project_tree.item(selection[0])['values'][0]
        client_text = self.project_client_combo.get()
        name = self.project_name_entry.get().strip()
        description = self.project_desc_text.get("1.0", tk.END).strip()

        if not client_text or not name:
            messagebox.showerror("Error", "Client and project name are required")
            return

        # Get client ID by name
        clients = self.client_model.get_all()
        client_id = None
        for client in clients:
            if client[1] == client_text:
                client_id = client[0]
                break

        if not client_id:
            messagebox.showerror("Error", "Invalid client selected")
            return

        rate = float(self.project_rate_entry.get() or 0)
        is_lump_sum = self.project_billing_var.get() == "lump_sum"

        if is_lump_sum:
            self.project_model.update(project_id, client_id, name, description, 0, True, rate)
        else:
            self.project_model.update(project_id, client_id, name, description, rate, False, 0)

        self.clear_project_form()
        self.refresh_projects()
        self.refresh_combos()
        messagebox.showinfo("Success", "Project updated successfully")

    def delete_project(self):
        selection = self.project_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a project to delete")
            return

        if messagebox.askyesno("Confirm",
                               "Delete this project? This will also delete all associated tasks and time entries."):
            project_id = self.project_tree.item(selection[0])['values'][0]
            self.project_model.delete(project_id)
            self.refresh_projects()
            self.refresh_combos()
            messagebox.showinfo("Success", "Project deleted successfully")

    def clear_project_form(self):
        self.project_client_combo.set("")
        self.project_name_entry.delete(0, tk.END)
        self.project_desc_text.delete("1.0", tk.END)
        self.project_rate_entry.delete(0, tk.END)
        self.project_billing_var.set("hourly")

    def on_project_select(self, event):
        selection = self.project_tree.selection()
        if selection:
            project_id = self.project_tree.item(selection[0])['values'][0]
            project = self.project_model.get_by_id(project_id)
            if project:
                # Set client
                client = self.client_model.get_by_id(project[1])
                if client:
                    self.project_client_combo.set(client[1])

                # Set project details
                self.project_name_entry.delete(0, tk.END)
                self.project_name_entry.insert(0, project[2])

                self.project_desc_text.delete("1.0", tk.END)
                self.project_desc_text.insert("1.0", project[3] or "")

                if project[5]:  # is_lump_sum
                    self.project_billing_var.set("lump_sum")
                    self.project_rate_entry.delete(0, tk.END)
                    self.project_rate_entry.insert(0, str(project[6]))
                else:
                    self.project_billing_var.set("hourly")
                    self.project_rate_entry.delete(0, tk.END)
                    self.project_rate_entry.insert(0, str(project[4]))

    def toggle_project_billing(self):
        pass

    # Task methods
    def add_task(self):
        name = self.task_name_entry.get().strip()
        description = self.task_desc_text.get("1.0", tk.END).strip()
        is_global = self.task_global_var.get()

        if not name:
            messagebox.showerror("Error", "Please enter a task name")
            return

        if is_global:
            # Create global task (project_id will be None)
            rate = float(self.task_rate_entry.get() or 0)
            is_lump_sum_flag = self.task_billing_var.get() == "lump_sum"

            if is_lump_sum_flag:
                self.task_model.create(name, description, 0, True, rate, None, True)
            else:
                self.task_model.create(name, description, rate, False, 0, None, True)

            messagebox.showinfo("Success", f"Global task '{name}' created!")
        else:
            # Create project-specific task
            client_text = self.task_client_combo.get()
            project_text = self.task_project_combo.get()

            if not client_text or not project_text:
                messagebox.showerror("Error", "Please select a client and project for non-global tasks")
                return

            # Get project ID by matching client and project names
            projects = self.project_model.get_all()
            project_id = None
            for project in projects:
                client_name = project[9] if len(project) > 9 else None
                if client_name == client_text and project[2] == project_text:
                    project_id = project[0]
                    break

            if not project_id:
                messagebox.showerror("Error", "Invalid project selected")
                return

            # CHECK FOR DUPLICATE TASK NAME UNDER SAME PROJECT
            existing_tasks = self.task_model.get_by_project(project_id)
            for task in existing_tasks:
                if task[2].lower() == name.lower():
                    messagebox.showerror("Error", f"Task '{name}' already exists for this project")
                    return

            rate = float(self.task_rate_entry.get() or 0)
            is_lump_sum_flag = self.task_billing_var.get() == "lump_sum"

            if is_lump_sum_flag:
                self.task_model.create(name, description, 0, True, rate, project_id, False)
            else:
                self.task_model.create(name, description, rate, False, 0, project_id, False)

            messagebox.showinfo("Success", f"Task '{name}' created!")

        self.clear_task_form()
        self.refresh_tasks()
        self.refresh_combos()


    def update_task(self):
        selection = self.task_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a task to update")
            return

        task_id = self.task_tree.item(selection[0])['values'][0]
        name = self.task_name_entry.get().strip()
        description = self.task_desc_text.get("1.0", tk.END).strip()

        if not name:
            messagebox.showerror("Error", "Task name is required")
            return

        rate = float(self.task_rate_entry.get() or 0)
        is_lump_sum = self.task_billing_var.get() == "lump_sum"

        if is_lump_sum:
            self.task_model.update(task_id, name, description, 0, True, rate)
        else:
            self.task_model.update(task_id, name, description, rate, False, 0)

        self.clear_task_form()
        self.refresh_tasks()
        self.refresh_combos()
        messagebox.showinfo("Success", "Task updated successfully")

    def delete_task(self):
        selection = self.task_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a task to delete")
            return

        if messagebox.askyesno("Confirm", "Delete this task? This will also delete all associated time entries."):
            task_id = self.task_tree.item(selection[0])['values'][0]
            self.task_model.delete(task_id)
            self.refresh_tasks()
            self.refresh_combos()
            messagebox.showinfo("Success", "Task deleted successfully")

    def clear_task_form(self):
        self.task_client_combo.set("")
        self.task_project_combo.set("")
        self.task_name_entry.delete(0, tk.END)
        self.task_desc_text.delete("1.0", tk.END)
        self.task_rate_entry.delete(0, tk.END)
        self.task_billing_var.set("hourly")

    def on_task_select(self, event):
        selection = self.task_tree.selection()
        if selection:
            task_id = self.task_tree.item(selection[0])['values'][0]
            task = self.task_model.get_by_id(task_id)
            if task:
                # Set project and client
                project = self.project_model.get_by_id(task[1])
                if project:
                    client = self.client_model.get_by_id(project[1])
                    if client:
                        self.task_client_combo.set(client[1])
                        # Trigger the client selection to populate projects
                        clients = self.client_model.get_all()
                        for c in clients:
                            if c[1] == client[1]:
                                projects = self.project_model.get_by_client(c[0])
                                self.task_project_combo['values'] = [p[2] for p in projects]
                                break
                        self.task_project_combo.set(project[2])

                # Set task details
                self.task_name_entry.delete(0, tk.END)
                self.task_name_entry.insert(0, task[2])

                self.task_desc_text.delete("1.0", tk.END)
                self.task_desc_text.insert("1.0", task[3] or "")

                if task[5]:  # is_lump_sum
                    self.task_billing_var.set("lump_sum")
                    self.task_rate_entry.delete(0, tk.END)
                    self.task_rate_entry.insert(0, str(task[6]))
                else:
                    self.task_billing_var.set("hourly")
                    self.task_rate_entry.delete(0, tk.END)
                    self.task_rate_entry.insert(0, str(task[4]))

    def toggle_task_billing(self):
        pass

    
    def toggle_task_project_field(self):
        """Enable or disable project selection based on global checkbox"""
        is_global = self.task_global_var.get()
        if is_global:
            self.task_client_combo.set('')
            self.task_client_combo.config(state='disabled')
            self.task_project_combo.set('')
            self.task_project_combo.config(state='disabled')
        else:
            self.task_client_combo.config(state='readonly')
            self.task_project_combo.config(state='readonly')

    # Time Entry methods
    def edit_time_entry(self):
        selection = self.entries_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a time entry to edit")
            return
        
        # Get the selected item
        selected_item = selection[0]
        item_tags = self.entries_tree.item(selected_item)['tags']
        
        # Only allow editing of actual entries, not group nodes
        if 'entry' not in item_tags:
            messagebox.showerror("Error", "Please select an individual time entry (not a group)")
            return
        
        # Extract entry ID from tags
        entry_id = None
        for tag in item_tags:
            if tag.startswith('entry_id_'):
                entry_id = int(tag.replace('entry_id_', ''))
                break
        
        if not entry_id:
            messagebox.showerror("Error", "Could not find entry ID")
            return

        self.open_edit_time_entry_dialog(entry_id)

    def open_edit_time_entry_dialog(self, entry_id):
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Time Entry")
        edit_window.geometry("500x400")

        # Get the entry details
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                           SELECT te.*, t.name as task_name, p.name as project_name, c.name as client_name
                           FROM time_entries te
                                    JOIN tasks t ON te.task_id = t.id
                                    JOIN projects p ON t.project_id = p.id
                                    JOIN clients c ON p.client_id = c.id
                           WHERE te.id = ?''', (entry_id,))
            entry = cursor.fetchone()

        if not entry:
            messagebox.showerror("Error", "Time entry not found")
            edit_window.destroy()
            return

        # Create form
        form_frame = ttk.Frame(edit_window)
        form_frame.pack(fill='both', expand=True, padx=15, pady=15)

        # Try to get task/project/client names from proper positions
        try:
            task_name = entry[-3] if len(entry) > 3 else "Unknown"
            project_name = entry[-2] if len(entry) > 2 else "Unknown"
            client_name = entry[-1] if len(entry) > 1 else "Unknown"
        except:
            task_name = project_name = client_name = "Unknown"

        ttk.Label(form_frame, text=f"Task: {client_name} - {project_name} - {task_name}", 
                 font=('Arial', 9, 'bold')).grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 10))

        # Get original start and end times
        try:
            original_start = datetime.fromisoformat(entry[2])  # start_time from DB
            original_end = datetime.fromisoformat(entry[3])    # end_time from DB
            original_duration = (original_end - original_start).total_seconds() / 3600
        except:
            original_start = datetime.now()
            original_end = datetime.now()
            original_duration = 0

        # Date field
        ttk.Label(form_frame, text="Date (MM/DD/YY):").grid(row=1, column=0, sticky='w', pady=5)
        date_entry = ttk.Entry(form_frame, width=15)
        date_entry.grid(row=1, column=1, sticky='w', padx=5, pady=5)
        date_entry.insert(0, original_start.strftime("%m/%d/%y"))
        
        # Entry mode selection (Start/End Time OR Decimal Hours)
        ttk.Label(form_frame, text="Entry Mode:").grid(row=2, column=0, sticky='w', pady=5)
        mode_frame = ttk.Frame(form_frame)
        mode_frame.grid(row=2, column=1, sticky='w', padx=5, pady=5)
        
        edit_entry_mode = tk.StringVar(value="decimal")  # Default to decimal
        ttk.Radiobutton(mode_frame, text="Start/End Time", variable=edit_entry_mode,
                       value="time_range").pack(side='left')
        ttk.Radiobutton(mode_frame, text="Decimal Hours", variable=edit_entry_mode,
                       value="decimal").pack(side='left', padx=10)

        # Start Time (for time_range mode)
        start_time_label = ttk.Label(form_frame, text="Start Time (HH:MM AM/PM):")
        start_time_label.grid(row=3, column=0, sticky='w', pady=5)
        start_time_entry = ttk.Entry(form_frame, width=20)
        start_time_entry.grid(row=3, column=1, sticky='w', padx=5, pady=5)
        start_time_entry.insert(0, original_start.strftime("%I:%M %p"))

        # End Time (for time_range mode)
        end_time_label = ttk.Label(form_frame, text="End Time (HH:MM AM/PM):")
        end_time_label.grid(row=4, column=0, sticky='w', pady=5)
        end_time_entry = ttk.Entry(form_frame, width=20)
        end_time_entry.grid(row=4, column=1, sticky='w', padx=5, pady=5)
        end_time_entry.insert(0, original_end.strftime("%I:%M %p"))
        
        # Decimal Hours (for decimal mode) - hidden by default
        hours_label = ttk.Label(form_frame, text="Duration (hours):")
        hours_label.grid(row=5, column=0, sticky='w', pady=5)
        hours_entry = ttk.Entry(form_frame, width=15)
        hours_entry.grid(row=5, column=1, sticky='w', padx=5, pady=5)
        hours_entry.insert(0, f"{original_duration:.2f}")
        
        hours_help = ttk.Label(form_frame, text="(e.g., 1.5, 2.25, 0.75)", 
                 font=('Arial', 8), foreground='gray')
        hours_help.grid(row=6, column=1, sticky='w', padx=5)
        
        # Toggle function
        def toggle_edit_mode():
            mode = edit_entry_mode.get()
            if mode == "time_range":
                # Show start/end time
                start_time_entry.grid()
                end_time_entry.grid()
                # Hide decimal
                hours_entry.grid_remove()
                hours_label.grid_remove()
                hours_help.grid_remove()
            else:  # decimal
                # Hide start/end time
                start_time_entry.grid_remove()
                end_time_entry.grid_remove()
                # Show decimal
                hours_entry.grid()
                hours_label.grid()
                hours_help.grid()
        
        # Bind toggle
        mode_frame.winfo_children()[0].configure(command=toggle_edit_mode)
        mode_frame.winfo_children()[1].configure(command=toggle_edit_mode)
        
        # Start in decimal mode
        toggle_edit_mode()

        # Description
        ttk.Label(form_frame, text="Description:").grid(row=7, column=0, sticky='nw', pady=5)
        desc_text = tk.Text(form_frame, height=3, width=30)
        desc_text.grid(row=7, column=1, sticky='ew', padx=5, pady=5)
        desc_text.insert('1.0', entry[4] if entry[4] else "")  # description from DB

        form_frame.columnconfigure(1, weight=1)

        # Buttons
        button_frame = ttk.Frame(edit_window)
        button_frame.pack(fill='x', padx=15, pady=(0, 15))

        def save_changes():
            try:
                # Get date
                date_str = date_entry.get().strip()
                date_obj = datetime.strptime(date_str, "%m/%d/%y")
                
                mode = edit_entry_mode.get()
                
                if mode == "time_range":
                    # Start/End Time mode
                    start_str = start_time_entry.get().strip()
                    end_str = end_time_entry.get().strip()
                    
                    if not start_str or not end_str:
                        messagebox.showerror("Error", "Please enter both start and end times")
                        return
                    
                    # Parse times
                    start_time = datetime.strptime(f"{date_str} {start_str}", "%m/%d/%y %I:%M %p")
                    end_time = datetime.strptime(f"{date_str} {end_str}", "%m/%d/%y %I:%M %p")
                    
                    if end_time <= start_time:
                        messagebox.showerror("Error", "End time must be after start time")
                        return
                    
                    duration_hours = (end_time - start_time).total_seconds() / 3600
                    
                else:  # decimal mode
                    # Decimal Hours mode
                    duration_str = hours_entry.get().strip()
                    
                    if not duration_str:
                        messagebox.showerror("Error", "Please enter duration in hours")
                        return
                    
                    duration_hours = float(duration_str)
                    
                    if duration_hours <= 0:
                        messagebox.showerror("Error", "Duration must be greater than 0")
                        return
                    
                    if duration_hours > 24:
                        messagebox.showerror("Error", "Duration cannot exceed 24 hours")
                        return
                    
                    # Use 9 AM as default start time for decimal mode
                    start_time = datetime.strptime(f"{date_str} 09:00 AM", "%m/%d/%y %I:%M %p")
                    end_time = start_time + timedelta(hours=duration_hours)
                
                # Get description
                description = desc_text.get('1.0', 'end').strip()

                # Update the entry
                self.time_entry_model.update(entry_id, start_time, end_time, description)
                self.refresh_time_entries()
                edit_window.destroy()
                messagebox.showinfo("Success", 
                                  f"Time entry updated successfully\n\n" +
                                  f"Duration: {duration_hours:.2f} hours")

            except ValueError as e:
                messagebox.showerror("Error", f"Invalid input: {str(e)}")

        ttk.Button(button_frame, text="Save Changes", command=save_changes).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Cancel", command=edit_window.destroy).pack(side='right')

    def delete_time_entry(self):
        selection = self.entries_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a time entry to delete")
            return
        
        # Get the selected item
        selected_item = selection[0]
        item_tags = self.entries_tree.item(selected_item)['tags']
        
        # Only allow deletion of actual entries, not group nodes
        if 'entry' not in item_tags:
            messagebox.showerror("Error", "Please select an individual time entry (not a group)")
            return
        
        # Extract entry ID from tags
        entry_id = None
        for tag in item_tags:
            if tag.startswith('entry_id_'):
                entry_id = int(tag.replace('entry_id_', ''))
                break
        
        if not entry_id:
            messagebox.showerror("Error", "Could not find entry ID")
            return

        if messagebox.askyesno("Confirm", "Delete this time entry?"):
            self.time_entry_model.delete(entry_id)
            self.refresh_time_entries()
            messagebox.showinfo("Success", "Time entry deleted successfully")

    def export_time_entries_to_excel(self):
        """Export time entries to Excel file, respecting current filter or selection"""
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill, Alignment
        except ImportError as e:
            messagebox.showerror("Error",
                                 f"openpyxl library not installed.\n\nError: {e}\n\nInstall with: pip install openpyxl")
            return

        try:
            # Check if user has selected specific entries
            selected_items = self.entries_tree.selection()


            if selected_items:
                # Export only selected entries
                selected_ids = []
                for item in selected_items:
                    item_data = self.entries_tree.item(item)
                    tags = item_data['tags']
                    # Entry ID is stored in tags like 'entry_id_123'
                    if tags:
                        for tag in tags:
                            if tag.startswith('entry_id_'):
                                try:
                                    entry_id = int(tag.replace('entry_id_', ''))
                                    selected_ids.append(entry_id)
                                    break
                                except (ValueError, TypeError):
                                    pass

                if not selected_ids:
                    messagebox.showinfo("No Selection", "Please select time entries (not group headers) to export.")
                    return

                with self.db.get_connection() as conn:
                    cursor = conn.cursor()
                    placeholders = ','.join('?' * len(selected_ids))
                    cursor.execute(f'''
                        SELECT te.id, te.client_name, te.project_name, te.task_name,
                               te.start_time, te.end_time, te.duration_minutes, te.description,
                               te.is_billed, te.invoice_number, te.date
                        FROM time_entries te
                        WHERE te.id IN ({placeholders})
                        ORDER BY te.date DESC, te.start_time DESC
                    ''', selected_ids)
                    entries = cursor.fetchall()

                export_scope = "Selected"
            else:
                filter_val = self.time_entries_filter_var.get() if hasattr(self,
                                                                           'time_entries_filter_var') else 'unbilled'

                where_clause = ""
                if filter_val == "unbilled":
                    where_clause = "WHERE te.is_billed = 0"
                elif filter_val == "billed":
                    where_clause = "WHERE te.is_billed = 1"

                with self.db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(f'''
                        SELECT te.id, te.client_name, te.project_name, te.task_name,
                               te.start_time, te.end_time, te.duration_minutes, te.description,
                               te.is_billed, te.invoice_number, te.date
                        FROM time_entries te
                        {where_clause}
                        ORDER BY te.date DESC, te.start_time DESC
                    ''')
                    entries = cursor.fetchall()

                export_scope = filter_val.capitalize()

            if not entries:
                messagebox.showinfo("No Data", "No time entries found to export.")
                return

            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile=f"TimeEntries_{export_scope}_{datetime.now().strftime('%Y%m%d')}.xlsx"
            )

            if not filename:
                return

            wb = Workbook()
            ws = wb.active
            ws.title = f"Time Entries ({export_scope})"

            headers = ['Date', 'Client', 'Project', 'Task', 'Start Time', 'End Time', 'Duration (hrs)', 'Description',
                       'Billed', 'Invoice #']
            ws.append(headers)

            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            header_font = Font(bold=True, color="FFFFFF")
            for cell in ws[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center")

            for entry in entries:
                entry_id, client, project, task, start_time, end_time, duration_mins, description, is_billed, invoice_num, date = entry

                try:
                    start_dt = datetime.fromisoformat(start_time)
                    start_display = start_dt.strftime("%I:%M %p")
                except:
                    start_display = start_time

                try:
                    end_dt = datetime.fromisoformat(end_time)
                    end_display = end_dt.strftime("%I:%M %p")
                except:
                    end_display = end_time

                duration_hours = (duration_mins / 60.0) if duration_mins else 0
                billed_status = "Yes" if is_billed else "No"

                ws.append([
                    date,
                    client,
                    project,
                    task,
                    start_display,
                    end_display,
                    round(duration_hours, 2),
                    description or "",
                    billed_status,
                    invoice_num or ""
                ])

            for column in ws.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column_letter].width = adjusted_width

            wb.save(filename)
            messagebox.showinfo("Success", f"Exported {len(entries)} time entries to:\n\n{filename}")

            if messagebox.askyesno("Open File?", "Would you like to open the exported file now?"):
                import os
                os.startfile(filename)

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export time entries:\n\n{e}\n\n{type(e).__name__}")
            import traceback
            traceback.print_exc()


    def invoice_selected_entries(self):
        """Generate invoice from selected time entries"""
        selection = self.entries_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select one or more time entries to invoice")
            return

        # Get selected entry IDs and check if any are already billed
        entry_ids = []
        billed_entries = []
        client_id = None
        client_name = None

        for item in selection:
            item_tags = self.entries_tree.item(item)['tags']
            
            # Skip non-entry items (groups)
            if 'entry' not in item_tags:
                continue
            
            # Extract entry ID from tags
            entry_id = None
            for tag in item_tags:
                if tag.startswith('entry_id_'):
                    entry_id = int(tag.replace('entry_id_', ''))
                    break
            
            if not entry_id:
                continue
            
            # Get entry details from database
            all_entries = self.time_entry_model.get_all()
            entry_data = None
            for e in all_entries:
                if e[0] == entry_id:
                    entry_data = e
                    break
            
            if not entry_data:
                continue
            
            entry_client = entry_data[1]
            entry_task = entry_data[3]

            # Check if already billed
            if '[BILLED]' in entry_task:
                billed_entries.append(entry_id)
                continue

            entry_ids.append(entry_id)

            # Get client_id from first entry
            if client_id is None:
                client_name = entry_client
                # Find client ID
                clients = self.client_model.get_all()
                for client in clients:
                    if client[1] == entry_client:
                        client_id = client[0]
                        break

        # Warn about billed entries
        if billed_entries:
            messagebox.showwarning("Already Billed",
                                   f"{len(billed_entries)} selected entry(ies) already billed and will be skipped.")

        if not entry_ids:
            messagebox.showerror("Error", "No unbilled entries selected")
            return

        if not client_id:
            messagebox.showerror("Error", "Could not determine client for selected entries")
            return

        # Verify all entries are from same client
        for item in selection:
            if self.entries_tree.item(item)['values'][1] != client_name:
                messagebox.showerror("Error",
                                     "All selected entries must be from the same client.\n"
                                     "Please select entries from one client only.")
                return

        # Confirm before generating invoice
        if not messagebox.askyesno("Confirm Invoice",
                                   f"Generate invoice for {len(entry_ids)} time entry(ies) from {client_name}?"):
            return

        # Generate invoice from selected entries
        self.generate_invoice_from_entries(client_id, client_name, entry_ids)

    def generate_invoice_from_entries(self, client_id, client_name, entry_ids):
        """Generate invoice data from specific entry IDs"""
        import sqlite3

        # Get entry details
        conn = self.db.conn
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        placeholders = ','.join(['?' for _ in entry_ids])
        cursor.execute(f'''
            SELECT * FROM invoice_view
            WHERE entry_id IN ({placeholders})
            AND (is_billed = 0 OR is_billed IS NULL)
        ''', entry_ids)

        entries = cursor.fetchall()
        conn.row_factory = None

        if not entries:
            messagebox.showinfo("No Entries", "Selected entries are already billed or not found.")
            return

        self.pending_entry_ids = [row['entry_id'] for row in entries]
        invoice_items = []

        # Group by task
        tasks = {}
        for row in entries:
            key = f"{row['project_name']} - {row['task_name']}"
            if key not in tasks:
                # Check if it's a lump sum task
                if row['task_lump_sum']:
                    tasks[key] = {
                        'minutes': 0,
                        'rate': 0,
                        'is_lump_sum': True,
                        'lump_sum_amount': row['task_lump_amount']
                    }
                elif row['project_lump_sum']:
                    tasks[key] = {
                        'minutes': 0,
                        'rate': 0,
                        'is_lump_sum': True,
                        'lump_sum_amount': row['project_lump_amount']
                    }
                else:
                    tasks[key] = {
                        'minutes': 0,
                        'rate': row['task_rate'] or row['project_rate'],
                        'is_lump_sum': False,
                        'lump_sum_amount': 0
                    }

            tasks[key]['minutes'] += row['duration_minutes'] or 0

        # Build invoice items
        for task_name, data in tasks.items():
            hours = data['minutes'] / 60.0

            if data['is_lump_sum']:
                invoice_items.append({
                    'description': task_name,
                    'quantity': '1',
                    'rate': f"${data['lump_sum_amount']:.2f}",
                    'amount': data['lump_sum_amount']
                })
            else:
                invoice_items.append({
                    'description': task_name,
                    'quantity': f"{hours:.2f} hrs",
                    'rate': f"${data['rate']:.2f}/hr",
                    'amount': hours * data['rate']
                })

        # Get earliest and latest dates from selected entries
        start_date = None
        end_date = None
        for row in entries:
            entry_date = datetime.fromisoformat(row['start_time']).date()
            if start_date is None or entry_date < start_date:
                start_date = entry_date
            if end_date is None or entry_date > end_date:
                end_date = entry_date

        # Create invoice data
        self.current_invoice_data = {
            'client_id': client_id,
            'start_date': datetime.combine(start_date, datetime.min.time()),
            'end_date': datetime.combine(end_date, datetime.max.time()),
            'items': invoice_items,
            'total': sum(item['amount'] for item in invoice_items)
        }

        # Switch to Invoices tab and display preview
        self.notebook.select(6)  # Invoices tab is index 6
        self.display_invoice_preview()

        messagebox.showinfo("Invoice Generated",
                            f"Invoice preview ready for {client_name}\n"
                            f"Total: ${self.current_invoice_data['total']:.2f}\n\n"
                            "Review and click 'Save as PDF' to finalize.")

    # Company info methods
    def browse_logo(self):
        filename = filedialog.askopenfilename(
            title="Select Logo Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if filename:
            self.logo_path_var.set(filename)

    def save_company_info(self):
        name = self.company_name_entry.get().strip()
        address = self.company_address_text.get("1.0", tk.END).strip()
        phone = self.company_phone_entry.get().strip()
        email = self.company_email_entry.get().strip()
        logo_path = self.logo_path_var.get()
        website = self.company_website_entry.get().strip()
        payment_terms = self.company_payment_terms_entry.get().strip()
        thank_you_message = self.company_thank_you_entry.get().strip()

        if not name:
            messagebox.showerror("Error", "Company name is required")
            return

        # Save to database with new fields
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO company_info 
                    (id, name, address, phone, email, logo_path, website, payment_terms, thank_you_message)
                    VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (name, address, phone, email, logo_path, website, payment_terms, thank_you_message))
                conn.commit()
            messagebox.showinfo("Success", "Company information saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save company info: {str(e)}")

    def load_company_info(self):
        company = self.company_model.get()
        if company:
            self.company_name_entry.delete(0, tk.END)
            self.company_name_entry.insert(0, company[1])

            self.company_address_text.delete("1.0", tk.END)
            self.company_address_text.insert("1.0", company[2] or "")

            self.company_phone_entry.delete(0, tk.END)
            self.company_phone_entry.insert(0, company[3] or "")

            self.company_email_entry.delete(0, tk.END)
            self.company_email_entry.insert(0, company[4] or "")

            if len(company) > 5 and company[5]:
                self.logo_path_var.set(company[5])
            
            # Load new fields (website, payment_terms, thank_you_message)
            if len(company) > 6 and company[6]:
                self.company_website_entry.delete(0, tk.END)
                self.company_website_entry.insert(0, company[6])
            
            if len(company) > 7 and company[7]:
                self.company_payment_terms_entry.delete(0, tk.END)
                self.company_payment_terms_entry.insert(0, company[7])
            else:
                # Default value if not in database yet
                self.company_payment_terms_entry.delete(0, tk.END)
                self.company_payment_terms_entry.insert(0, "Payment is due within 30 days")
            
            if len(company) > 8 and company[8]:
                self.company_thank_you_entry.delete(0, tk.END)
                self.company_thank_you_entry.insert(0, company[8])
            else:
                # Default value if not in database yet
                self.company_thank_you_entry.delete(0, tk.END)
                self.company_thank_you_entry.insert(0, "Thank you for your business!")

    # Invoice methods
    def generate_invoice(self):
        client_text = self.invoice_client_combo.get()

        if not client_text:
            messagebox.showerror("Error", "Please select a client")
            return

        # Get client ID
        clients = self.client_model.get_all()
        client_id = None
        for client in clients:
            if client[1] == client_text:
                client_id = client[0]
                break

        if not client_id:
            messagebox.showerror("Error", "Invalid client selected")
            return

        try:
            start_date = datetime.strptime(self.invoice_start_date.get(), "%m/%d/%y")
            end_date = datetime.strptime(self.invoice_end_date.get(), "%m/%d/%y")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use MM/DD/YY")
            return

        # Generate invoice data
        self.current_invoice_data = self.generate_invoice_data(client_id, start_date, end_date)
        self.display_invoice_preview()

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

    def display_invoice_preview(self):
        # Clear existing items
        for item in self.invoice_tree.get_children():
            self.invoice_tree.delete(item)

        # Check if invoice data exists
        if not self.current_invoice_data:
            self.invoice_total_label.config(text="Total: $0.00")
            return

        # Add invoice items
        for item in self.current_invoice_data['items']:
            self.invoice_tree.insert('', 'end', values=(
                item['description'],
                item['quantity'],
                item['rate'],
                f"${item['amount']:.2f}"
            ))

        # Update total
        self.invoice_total_label.config(text=f"Total: ${self.current_invoice_data['total']:.2f}")

    def save_invoice_pdf(self):
        if not hasattr(self, 'current_invoice_data'):
            messagebox.showerror("Error", "Please generate an invoice first")
            return

        if not self.current_invoice_data:
            messagebox.showerror("Error", "No invoice data available")
            return

        # Generate invoice number based on date
        invoice_date = datetime.now()
        invoice_number = f"INV-{invoice_date.strftime('%Y%m%d-%H%M%S')}"

        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"Invoice_{invoice_number}.pdf"
        )

        if filename:
            try:
                from invoice_generator import InvoiceGenerator
                generator = InvoiceGenerator(self.db)
                generator.generate_pdf(self.current_invoice_data, filename, invoice_number)

                # Mark time entries as billed
                if hasattr(self, 'pending_entry_ids') and self.pending_entry_ids:
                    self.db.mark_entries_billed(self.pending_entry_ids, invoice_number)

                    # Save to billing history
                    self.db.save_billing_history(self.current_invoice_data, invoice_number, filename)

                    # Clear pending entries
                    self.pending_entry_ids = []

                    messagebox.showinfo("Success",
                                        f"Invoice saved as {filename}\n\n"
                                        f"Time entries have been marked as billed and will not appear in future invoices.")
                else:
                    messagebox.showinfo("Success", f"Invoice saved as {filename}")

                # Clear current invoice data
                self.current_invoice_data = None

                # Clear the preview
                for item in self.invoice_tree.get_children():
                    self.invoice_tree.delete(item)
                self.invoice_total_label.config(text="Total: $0.00")

                # Refresh time entries to show billed status
                self.refresh_time_entries()

            except Exception as e:
                messagebox.showerror("Error", f"Failed to save invoice: {str(e)}")

    def edit_invoice_item(self):
        selection = self.invoice_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select an item to edit")
            return

        item_values = self.invoice_tree.item(selection[0])['values']
        self.open_edit_invoice_item_dialog(selection[0], item_values)

    def open_edit_invoice_item_dialog(self, item_id, item_values):
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Invoice Item")
        edit_window.geometry("400x200")

        form_frame = ttk.Frame(edit_window)
        form_frame.pack(fill='both', expand=True, padx=10, pady=10)

        ttk.Label(form_frame, text="Description:").grid(row=0, column=0, sticky='w', pady=2)
        desc_entry = ttk.Entry(form_frame, width=40)
        desc_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=2)
        desc_entry.insert(0, item_values[0])

        ttk.Label(form_frame, text="Quantity:").grid(row=1, column=0, sticky='w', pady=2)
        qty_entry = ttk.Entry(form_frame)
        qty_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=2)
        qty_entry.insert(0, item_values[1])

        ttk.Label(form_frame, text="Rate:").grid(row=2, column=0, sticky='w', pady=2)
        rate_entry = ttk.Entry(form_frame)
        rate_entry.grid(row=2, column=1, sticky='ew', padx=5, pady=2)
        rate_entry.insert(0, item_values[2])

        form_frame.columnconfigure(1, weight=1)

        button_frame = ttk.Frame(edit_window)
        button_frame.pack(fill='x', padx=10, pady=10)

        def save_changes():
            # Update the tree item
            self.invoice_tree.item(item_id, values=(
                desc_entry.get(),
                qty_entry.get(),
                rate_entry.get(),
                item_values[3]
            ))

            # Recalculate if needed
            if hasattr(self, 'current_invoice_data'):
                for item in self.current_invoice_data['items']:
                    if item['description'] == item_values[0]:
                        item['description'] = desc_entry.get()
                        item['quantity'] = qty_entry.get()
                        item['rate'] = rate_entry.get()
                        break

            edit_window.destroy()

        ttk.Button(button_frame, text="Save", command=save_changes).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Cancel", command=edit_window.destroy).pack(side='right')

    def remove_invoice_item(self):
        selection = self.invoice_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select an item to remove")
            return

        # Get item description before removing
        item_values = self.invoice_tree.item(selection[0])['values']

        # Remove from tree
        self.invoice_tree.delete(selection[0])

        # Update invoice data if it exists
        if hasattr(self, 'current_invoice_data'):
            self.current_invoice_data['items'] = [
                item for item in self.current_invoice_data['items']
                if item['description'] != item_values[0]
            ]

            # Recalculate total
            self.current_invoice_data['total'] = sum(
                item['amount'] for item in self.current_invoice_data['items']
            )
            self.invoice_total_label.config(
                text=f"Total: ${self.current_invoice_data['total']:.2f}"
            )

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
                tags=('client',))
            
            for project_name in sorted(hierarchy[client_name].keys()):
                # Insert project node
                project_id = self.task_tree.insert(client_id, 'end',
                    text=f"  📂 {project_name}",
                    values=('Project', '', '', '', ''),
                    tags=('project',))
                
                # Insert tasks under project
                for task in hierarchy[client_name][project_name]:
                    billing_type = "Lump Sum" if task[5] else "Hourly"
                    rate = f"${task[6]:.2f}" if task[5] else f"${task[4]:.2f}/hr"
                    
                    self.task_tree.insert(project_id, 'end',
                        text=f"    ⚙️ {task[2]}",
                        values=('Task', task[0], '', billing_type, rate),
                        tags=('task', f'task_id_{task[0]}'))
        
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


    def refresh_time_entries(self):
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
                tags=('client',))
            
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
                    tags=('project',))
                
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
                        tags=('task',))
                    
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
                        entry_id = self.entries_tree.insert(task_id, 'end',
                            text=f"      ⏱️ Entry",
                            values=('Entry' + entry_billed, '', start_display, f"{duration_hours:.2f} hrs", entry[7] or ''),
                            tags=('entry', f'entry_id_{entry[0]}'))
        
        # Configure tag colors
        self.entries_tree.tag_configure('client', font=('Arial', 10, 'bold'))
        self.entries_tree.tag_configure('project', font=('Arial', 9, 'bold'))
        self.entries_tree.tag_configure('task', font=('Arial', 9))
        self.entries_tree.tag_configure('entry', font=('Arial', 8))

    def refresh_combos(self):
        # Refresh timer combos
        clients = self.client_model.get_all()
        client_names = [c[1] for c in clients]
        self.timer_client_combo['values'] = client_names

        # Refresh project combo
        self.project_client_combo['values'] = client_names

        # Refresh task client combo
        self.task_client_combo['values'] = client_names

        # Refresh task combo for manual entry
        tasks = self.task_model.get_all()
        task_displays = []
        for task in tasks:
            client_name = task[9] if len(task) > 9 else "Unknown"
            project_name = task[8] if len(task) > 8 else "Unknown"
            task_displays.append(f"{client_name} - {project_name} - {task[2]}")
        self.manual_task_combo['values'] = task_displays

        # Refresh invoice client combo
        self.invoice_client_combo['values'] = client_names

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

    def refresh_all_data(self):
        self.refresh_clients()
        self.refresh_projects()
        self.refresh_tasks()
        self.refresh_time_entries()
        self.refresh_combos()
        self.load_company_info()
        self.update_daily_totals_display()  # Initialize daily totals display
        if hasattr(self, 'billed_invoices_tree'):
            self.refresh_billed_invoices()  # Refresh billed invoices if tab exists
    
    # NEW INVOICE TAB METHODS
    def on_invoice_client_select(self, event):
        """When client is selected, populate projects for that client"""
        client_name = self.invoice_client_combo.get()
        if client_name:
            # Get client ID
            clients = self.client_model.get_all()
            client_id = None
            for client in clients:
                if client[1] == client_name:
                    client_id = client[0]
                    break
            
            if client_id:
                # Load projects for this client
                projects = self.project_model.get_by_client(client_id)
                project_names = [p[2] for p in projects]
                self.invoice_project_combo['values'] = ['All Projects'] + project_names
                self.invoice_project_combo.set('All Projects')
            else:
                self.invoice_project_combo['values'] = []
                self.invoice_project_combo.set('')
    
    def on_invoice_project_select(self, event):
        """Project selection changed - just for filtering later"""
        pass  # Filtering happens when Load button is clicked
    
    def toggle_invoice_date_filter(self):
        """Show or hide date range inputs based on filter selection"""
        if self.invoice_filter_var.get() == "date_range":
            self.date_range_frame.pack(side='left', padx=20)
        else:
            self.date_range_frame.pack_forget()
    
    def refresh_invoice_combos(self):
        """Refresh client and project dropdowns"""
        clients = self.client_model.get_all()
        client_names = [c[1] for c in clients]
        self.invoice_client_combo['values'] = client_names
        self.invoice_project_combo['values'] = []
        self.invoice_project_combo.set('')
        messagebox.showinfo("Refreshed", "Client and project lists updated.")
    
    def load_invoiceable_entries(self):
        """Load unbilled time entries based on selected client/project/date filter"""
        client_name = self.invoice_client_combo.get()
        if not client_name:
            messagebox.showerror("Error", "Please select a client first")
            return
        
        # Get client ID
        clients = self.client_model.get_all()
        client_id = None
        for client in clients:
            if client[1] == client_name:
                client_id = client[0]
                break
        
        if not client_id:
            messagebox.showerror("Error", "Invalid client selected")
            return
        
        # Get project filter
        project_name = self.invoice_project_combo.get()
        project_id = None
        if project_name and project_name != 'All Projects':
            projects = self.project_model.get_by_client(client_id)
            for project in projects:
                if project[2] == project_name:
                    project_id = project[0]
                    break
        
        # Build query based on filter
        conn = self.db.conn  # Use direct connection, not context manager
        cursor = conn.cursor()
        
        if self.invoice_filter_var.get() == "all_uninvoiced":
            # All unbilled entries for client
            if project_id:
                cursor.execute('''
                    SELECT te.id, te.start_time, te.description, te.duration_minutes,
                           p.name as project_name, t.name as task_name
                    FROM time_entries te
                    JOIN tasks t ON te.task_id = t.id
                    JOIN projects p ON t.project_id = p.id
                    WHERE p.client_id = ? AND p.id = ? AND (te.is_billed = 0 OR te.is_billed IS NULL)
                    ORDER BY te.start_time DESC
                ''', (client_id, project_id))
            else:
                cursor.execute('''
                    SELECT te.id, te.start_time, te.description, te.duration_minutes,
                           p.name as project_name, t.name as task_name
                    FROM time_entries te
                    JOIN tasks t ON te.task_id = t.id
                    JOIN projects p ON t.project_id = p.id
                    WHERE p.client_id = ? AND (te.is_billed = 0 OR te.is_billed IS NULL)
                    ORDER BY te.start_time DESC
                ''', (client_id,))
        else:
            # Date range filter
            try:
                start_date = datetime.strptime(self.invoice_start_date.get(), "%m/%d/%y")
                end_date = datetime.strptime(self.invoice_end_date.get(), "%m/%d/%y")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use MM/DD/YY")
                return
            
            if project_id:
                cursor.execute('''
                    SELECT te.id, te.start_time, te.description, te.duration_minutes,
                           p.name as project_name, t.name as task_name
                    FROM time_entries te
                    JOIN tasks t ON te.task_id = t.id
                    JOIN projects p ON t.project_id = p.id
                    WHERE p.client_id = ? AND p.id = ? 
                          AND DATE(te.start_time) BETWEEN ? AND ?
                          AND (te.is_billed = 0 OR te.is_billed IS NULL)
                    ORDER BY te.start_time DESC
                ''', (client_id, project_id, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
            else:
                cursor.execute('''
                    SELECT te.id, te.start_time, te.description, te.duration_minutes,
                           p.name as project_name, t.name as task_name
                    FROM time_entries te
                    JOIN tasks t ON te.task_id = t.id
                    JOIN projects p ON t.project_id = p.id
                    WHERE p.client_id = ? 
                          AND DATE(te.start_time) BETWEEN ? AND ?
                          AND (te.is_billed = 0 OR te.is_billed IS NULL)
                    ORDER BY te.start_time DESC
                ''', (client_id, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
        
        entries = cursor.fetchall()
        
        # Clear existing entries
        for item in self.invoice_entries_tree.get_children():
            self.invoice_entries_tree.delete(item)
        
        # Populate tree
        total_hours = 0
        for entry in entries:
            entry_id, start_time, description, duration_minutes, project_name, task_name = entry
            
            # Format date
            try:
                dt = datetime.fromisoformat(start_time)
                date_display = dt.strftime("%m/%d/%y")
            except:
                date_display = start_time[:10]
            
            # Calculate hours
            hours = (duration_minutes or 0) / 60.0
            total_hours += hours
            
            # Insert into tree
            self.invoice_entries_tree.insert('', 'end', 
                text='☐',
                values=(date_display, project_name, task_name, f"{hours:.2f} hrs", description or ''),
                tags=(f'entry_id_{entry_id}',))
        
        # Update summary
        self.invoice_summary_label.config(
            text=f"📊 {len(entries)} unbilled entries found | Total: {total_hours:.2f} hours")
    
    def select_all_invoice_entries(self):
        """Select all entries in the invoice tree"""
        for item in self.invoice_entries_tree.get_children():
            self.invoice_entries_tree.selection_add(item)
    
    def deselect_all_invoice_entries(self):
        """Deselect all entries in the invoice tree"""
        self.invoice_entries_tree.selection_remove(*self.invoice_entries_tree.get_children())
    
    def preview_invoice(self):
        """Generate and show invoice preview dialog"""
        selection = self.invoice_entries_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select at least one time entry to invoice")
            return
        
        # Get selected entry IDs
        entry_ids = []
        for item in selection:
            tags = self.invoice_entries_tree.item(item)['tags']
            for tag in tags:
                if tag.startswith('entry_id_'):
                    entry_ids.append(int(tag.replace('entry_id_', '')))
                    break
        
        if not entry_ids:
            messagebox.showerror("Error", "Could not find selected entries")
            return
        
        # Get client info
        client_name = self.invoice_client_combo.get()
        clients = self.client_model.get_all()
        client_id = None
        for client in clients:
            if client[1] == client_name:
                client_id = client[0]
                break
        
        # Generate invoice data from selected entries
        self.show_invoice_preview_dialog(client_id, client_name, entry_ids)
    
    def show_invoice_preview_dialog(self, client_id, client_name, entry_ids):
        """Show invoice preview dialog with EDIT and CREATE buttons"""
        import sqlite3
        
        # Create dialog
        preview_dialog = tk.Toplevel(self.root)
        preview_dialog.title(f"Invoice Preview - {client_name}")
        preview_dialog.geometry("800x600")
        
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
            JOIN projects p ON t.project_id = p.id
            WHERE te.id IN ({placeholders})
        ''', entry_ids)
        
        entries = cursor.fetchall()
        conn.row_factory = None
        
        # Group by task and calculate totals
        task_groups = {}
        for entry in entries:
            key = f"{entry['project_name']} - {entry['task_name']}"
            if key not in task_groups:
                task_groups[key] = {
                    'minutes': 0,
                    'rate': entry['task_rate'] or entry['project_rate'],
                    'is_lump_sum': entry['task_lump_sum'] or entry['project_lump_sum'],
                    'lump_sum_amount': entry['task_lump_amount'] or entry['project_lump_amount']
                }
            task_groups[key]['minutes'] += entry['duration_minutes'] or 0
        
        # Build invoice items
        invoice_items = []
        total_amount = 0
        
        for task_name, data in task_groups.items():
            hours = data['minutes'] / 60.0
            
            if data['is_lump_sum']:
                amount = data['lump_sum_amount']
                invoice_items.append({
                    'description': task_name,
                    'quantity': '1',
                    'rate': f"${amount:.2f}",
                    'amount': amount
                })
            else:
                amount = hours * data['rate']
                invoice_items.append({
                    'description': task_name,
                    'quantity': f"{hours:.2f} hrs",
                    'rate': f"${data['rate']:.2f}/hr",
                    'amount': amount
                })
            
            total_amount += amount
        
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
            items_tree.insert('', 'end', values=(
                item['description'],
                item['quantity'],
                item['rate'],
                f"${item['amount']:.2f}"
            ))
        
        items_tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Total
        total_frame = ttk.Frame(preview_dialog)
        total_frame.pack(fill='x', padx=20, pady=10)
        
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
        
        ttk.Button(button_frame, text="✏️ Edit Items", 
                  command=lambda: messagebox.showinfo("Edit", "Edit functionality coming soon!")).pack(side='left', padx=5)
        ttk.Button(button_frame, text="✅ CREATE INVOICE", 
                  command=create_invoice,
                  style='Accent.TButton').pack(side='right', padx=5)
        ttk.Button(button_frame, text="Cancel", 
                  command=preview_dialog.destroy).pack(side='right', padx=5)
