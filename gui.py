import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
from database import DatabaseManager
from models import Client, Project, Task, TimeEntry, CompanyInfo
import sqlite3
import threading
import time


class TimeTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Time Tracker Pro")
        self.root.geometry("1200x800")

        # Initialize database and models
        self.db = DatabaseManager()
        self.client_model = Client(self.db)
        self.project_model = Project(self.db)
        self.task_model = Task(self.db)
        self.time_entry_model = TimeEntry(self.db)
        self.company_model = CompanyInfo(self.db)

        # Timer variables
        self.timer_running = False
        self.timer_start_time = None
        self.current_task_id = None

        self.create_widgets()
        self.refresh_all_data()

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

    def create_timer_tab(self):
        # Timer tab
        timer_frame = ttk.Frame(self.notebook)
        self.notebook.add(timer_frame, text="Timer")

        # Timer display
        timer_display_frame = ttk.LabelFrame(timer_frame, text="Active Timer")
        timer_display_frame.pack(fill='x', padx=10, pady=10)

        self.timer_label = ttk.Label(timer_display_frame, text="00:00:00", font=("Arial", 24))
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

        # Start Time
        ttk.Label(form_frame, text="Start Time (HH:MM AM/PM):").grid(row=1, column=0, sticky='w', pady=2)
        self.manual_start_entry = ttk.Entry(form_frame)
        self.manual_start_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=2)
        self.manual_start_entry.insert(0, "09:00 AM")

        # End Time
        ttk.Label(form_frame, text="End Time (HH:MM AM/PM):").grid(row=2, column=0, sticky='w', pady=2)
        self.manual_end_entry = ttk.Entry(form_frame)
        self.manual_end_entry.grid(row=2, column=1, sticky='ew', padx=5, pady=2)
        self.manual_end_entry.insert(0, "05:00 PM")

        # Task
        ttk.Label(form_frame, text="Task:").grid(row=3, column=0, sticky='w', pady=2)
        self.manual_task_combo = ttk.Combobox(form_frame, state='readonly')
        self.manual_task_combo.grid(row=3, column=1, sticky='ew', padx=5, pady=2)

        # Description
        ttk.Label(form_frame, text="Description:").grid(row=4, column=0, sticky='nw', pady=2)
        self.manual_desc_text = tk.Text(form_frame, height=3)
        self.manual_desc_text.grid(row=4, column=1, sticky='ew', padx=5, pady=2)

        form_frame.columnconfigure(1, weight=1)

        # Manual entry buttons
        manual_button_frame = ttk.Frame(manual_frame)
        manual_button_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(manual_button_frame, text="Add Entry", command=self.add_manual_entry).pack(side='left', padx=5)
        ttk.Button(manual_button_frame, text="Clear", command=self.clear_manual_entry_form).pack(side='left', padx=5)

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

        # Task billing options
        billing_frame = ttk.Frame(form_frame)
        billing_frame.grid(row=4, column=1, sticky='ew', padx=5, pady=2)

        self.task_billing_var = tk.StringVar(value="hourly")
        ttk.Radiobutton(billing_frame, text="Hourly Rate", variable=self.task_billing_var,
                        value="hourly", command=self.toggle_task_billing).pack(side='left')
        ttk.Radiobutton(billing_frame, text="Lump Sum", variable=self.task_billing_var,
                        value="lump_sum", command=self.toggle_task_billing).pack(side='left', padx=10)

        ttk.Label(form_frame, text="Rate/Amount:").grid(row=5, column=0, sticky='w', pady=2)
        self.task_rate_entry = ttk.Entry(form_frame)
        self.task_rate_entry.grid(row=5, column=1, sticky='ew', padx=5, pady=2)

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

        self.task_tree = ttk.Treeview(list_frame, columns=('ID', 'Project', 'Client', 'Name', 'Type', 'Rate'),
                                      show='headings')
        self.task_tree.heading('ID', text='ID')
        self.task_tree.heading('Project', text='Project')
        self.task_tree.heading('Client', text='Client')
        self.task_tree.heading('Name', text='Task')
        self.task_tree.heading('Type', text='Billing Type')
        self.task_tree.heading('Rate', text='Rate/Amount')

        self.task_tree.column('ID', width=50)
        self.task_tree.column('Project', width=150)
        self.task_tree.column('Client', width=100)
        self.task_tree.column('Name', width=150)
        self.task_tree.column('Type', width=100)
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

        # Time entries list
        list_frame = ttk.LabelFrame(entries_frame, text="Time Entries")
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.entries_tree = ttk.Treeview(list_frame, columns=('ID', 'Client', 'Project', 'Task', 'Start', 'Duration',
                                                              'Description'), show='headings', selectmode='extended')
        self.entries_tree.heading('ID', text='ID')
        self.entries_tree.heading('Client', text='Client')
        self.entries_tree.heading('Project', text='Project')
        self.entries_tree.heading('Task', text='Task')
        self.entries_tree.heading('Start', text='Start Time')
        self.entries_tree.heading('Duration', text='Duration (hrs)')
        self.entries_tree.heading('Description', text='Description')

        self.entries_tree.column('ID', width=50)
        self.entries_tree.column('Client', width=100)
        self.entries_tree.column('Project', width=120)
        self.entries_tree.column('Task', width=120)
        self.entries_tree.column('Start', width=150)
        self.entries_tree.column('Duration', width=100)
        self.entries_tree.column('Description', width=200)

        self.entries_tree.pack(fill='both', expand=True, padx=10, pady=10)

        # Entry buttons
        entry_button_frame = ttk.Frame(list_frame)
        entry_button_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(entry_button_frame, text="Invoice Selected",
                   command=self.invoice_selected_entries).pack(side='left', padx=5)
        ttk.Button(entry_button_frame, text="Edit Entry",
                   command=self.edit_time_entry).pack(side='left', padx=5)
        ttk.Button(entry_button_frame, text="Delete Entry",
                   command=self.delete_time_entry).pack(side='left', padx=5)

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

        form_frame.columnconfigure(1, weight=1)

        # Company buttons
        button_frame = ttk.Frame(company_form)
        button_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(button_frame, text="Save Company Info", command=self.save_company_info).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Load Current Info", command=self.load_company_info).pack(side='left', padx=5)

    def create_invoice_tab(self):
        # Invoice tab
        invoice_frame = ttk.Frame(self.notebook)
        self.notebook.add(invoice_frame, text="Invoices")

        # Invoice generation form
        invoice_gen_frame = ttk.LabelFrame(invoice_frame, text="Generate Invoice")
        invoice_gen_frame.pack(fill='x', padx=10, pady=10)

        form_frame = ttk.Frame(invoice_gen_frame)
        form_frame.pack(fill='x', padx=10, pady=10)

        # Client selection
        ttk.Label(form_frame, text="Client:").grid(row=0, column=0, sticky='w', pady=2)
        self.invoice_client_combo = ttk.Combobox(form_frame, state='readonly')
        self.invoice_client_combo.grid(row=0, column=1, sticky='ew', padx=5, pady=2)

        # Date range
        ttk.Label(form_frame, text="Date Range:").grid(row=1, column=0, sticky='w', pady=2)
        date_frame = ttk.Frame(form_frame)
        date_frame.grid(row=1, column=1, sticky='ew', padx=5, pady=2)

        self.invoice_start_date = ttk.Entry(date_frame, width=12)
        self.invoice_start_date.pack(side='left')
        self.invoice_start_date.insert(0, (datetime.now() - timedelta(days=30)).strftime("%m/%d/%y"))

        ttk.Label(date_frame, text=" to ").pack(side='left')

        self.invoice_end_date = ttk.Entry(date_frame, width=12)
        self.invoice_end_date.pack(side='left')
        self.invoice_end_date.insert(0, datetime.now().strftime("%m/%d/%y"))

        # Grouping option
        ttk.Label(form_frame, text="Group by:").grid(row=2, column=0, sticky='w', pady=2)
        self.invoice_group_var = tk.StringVar(value="task")
        group_frame = ttk.Frame(form_frame)
        group_frame.grid(row=2, column=1, sticky='ew', padx=5, pady=2)

        ttk.Radiobutton(group_frame, text="By Task", variable=self.invoice_group_var, value="task").pack(side='left')
        ttk.Radiobutton(group_frame, text="By Project", variable=self.invoice_group_var, value="project").pack(
            side='left', padx=10)

        form_frame.columnconfigure(1, weight=1)

        # Generate button
        ttk.Button(invoice_gen_frame, text="Generate Invoice", command=self.generate_invoice).pack(pady=10)

        # Invoice preview/edit section
        preview_frame = ttk.LabelFrame(invoice_frame, text="Invoice Preview")
        preview_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Invoice items tree
        self.invoice_tree = ttk.Treeview(preview_frame, columns=('Description', 'Quantity', 'Rate', 'Amount'),
                                         show='headings')
        self.invoice_tree.heading('Description', text='Description')
        self.invoice_tree.heading('Quantity', text='Hours/Qty')
        self.invoice_tree.heading('Rate', text='Rate')
        self.invoice_tree.heading('Amount', text='Amount')

        self.invoice_tree.column('Description', width=300)
        self.invoice_tree.column('Quantity', width=100)
        self.invoice_tree.column('Rate', width=100)
        self.invoice_tree.column('Amount', width=100)

        self.invoice_tree.pack(fill='both', expand=True, padx=10, pady=10)

        # Invoice total
        total_frame = ttk.Frame(preview_frame)
        total_frame.pack(fill='x', padx=10, pady=5)

        self.invoice_total_label = ttk.Label(total_frame, text="Total: $0.00", font=("Arial", 12, "bold"))
        self.invoice_total_label.pack(side='right')

        # Invoice buttons
        invoice_button_frame = ttk.Frame(preview_frame)
        invoice_button_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(invoice_button_frame, text="Save as PDF", command=self.save_invoice_pdf).pack(side='left', padx=5)
        ttk.Button(invoice_button_frame, text="Edit Item", command=self.edit_invoice_item).pack(side='left', padx=5)
        ttk.Button(invoice_button_frame, text="Remove Item", command=self.remove_invoice_item).pack(side='left', padx=5)

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

        # Extract just the task name from "Client - Project - Task" format
        # The format is: client_name - project_name - task_name
        parts = task_text.split(' - ')
        if len(parts) >= 3:
            task_name = ' - '.join(parts[2:])  # In case task name has dashes
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
            self.time_entry_model.start_timer(self.current_task_id)

            # Update UI
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')

            # Start timer thread
            self.update_timer_display()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start timer: {str(e)}")
            self.timer_running = False

    def stop_timer(self):
        if self.timer_running:
            self.timer_running = False
            self.time_entry_model.stop_timer()

            # Update UI
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            self.timer_label.config(text="00:00:00")

            self.refresh_time_entries()
            messagebox.showinfo("Success", "Timer stopped and time entry saved")

    def update_timer_display(self):
        if self.timer_running and self.timer_start_time:
            elapsed = datetime.now() - self.timer_start_time
            hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            self.timer_label.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            self.root.after(1000, self.update_timer_display)

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
                # project structure: [0:id, 1:client_id, 2:name, ..., 9:client_name]
                proj_client_name = project[9] if len(project) > 9 else None
                if proj_client_name == client_name and project[2] == project_name:
                    project_id = project[0]
                    break

            if project_id:
                # Load tasks for this project
                tasks = self.task_model.get_by_project(project_id)
                # Task display format: "Client - Project - Task Name"
                task_displays = [f"{client_name} - {project_name} - {t[2]}" for t in tasks]
                self.timer_task_combo['values'] = task_displays
                self.timer_task_combo.set('')
            else:
                # No project found, clear tasks
                self.timer_task_combo['values'] = []
                self.timer_task_combo.set('')

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

    def add_manual_entry(self):
        task_text = self.manual_task_combo.get()
        date_str = self.manual_date_entry.get().strip()
        start_str = self.manual_start_entry.get().strip()
        end_str = self.manual_end_entry.get().strip()
        description = self.manual_desc_text.get("1.0", tk.END).strip()

        if not task_text:
            messagebox.showerror("Error", "Please select a task")
            return

        try:
            # Parse date MM/DD/YY
            date_obj = datetime.strptime(date_str, "%m/%d/%y")

            # Parse times HH:MM AM/PM
            start_time_obj = datetime.strptime(f"{date_str} {start_str}", "%m/%d/%y %I:%M %p")
            end_time_obj = datetime.strptime(f"{date_str} {end_str}", "%m/%d/%y %I:%M %p")

            if end_time_obj <= start_time_obj:
                messagebox.showerror("Error", "End time must be after start time")
                return

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
        self.clear_manual_entry_form()
        messagebox.showinfo("Success", "Time entry added successfully")

    def clear_manual_entry_form(self):
        self.manual_date_entry.delete(0, tk.END)
        self.manual_date_entry.insert(0, datetime.now().strftime("%m/%d/%y"))
        self.manual_start_entry.delete(0, tk.END)
        self.manual_start_entry.insert(0, "09:00 AM")
        self.manual_end_entry.delete(0, tk.END)
        self.manual_end_entry.insert(0, "05:00 PM")
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
        client_text = self.task_client_combo.get()
        project_text = self.task_project_combo.get()
        name = self.task_name_entry.get().strip()

        if not client_text or not project_text or not name:
            messagebox.showerror("Error", "Client, project, and task name are required")
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
            if task[2].lower() == name.lower():  # Case-insensitive comparison
                messagebox.showerror("Error", f"Task '{name}' already exists for this project")
                return

        description = self.task_desc_text.get("1.0", tk.END).strip()
        rate = float(self.task_rate_entry.get() or 0)
        is_lump_sum = self.task_billing_var.get() == "lump_sum"

        if is_lump_sum:
            self.task_model.create(project_id, name, description, 0, True, rate)
        else:
            self.task_model.create(project_id, name, description, rate, False, 0)

        self.clear_task_form()
        self.refresh_tasks()
        self.refresh_combos()
        messagebox.showinfo("Success", "Task added successfully")

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

    # Time Entry methods
    def edit_time_entry(self):
        selection = self.entries_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a time entry to edit")
            return

        entry_id = self.entries_tree.item(selection[0])['values'][0]
        self.open_edit_time_entry_dialog(entry_id)

    def open_edit_time_entry_dialog(self, entry_id):
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Time Entry")
        edit_window.geometry("400x300")

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
        form_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Try to get task/project/client names from proper positions
        try:
            task_name = entry[-3] if len(entry) > 3 else "Unknown"
            project_name = entry[-2] if len(entry) > 2 else "Unknown"
            client_name = entry[-1] if len(entry) > 1 else "Unknown"
        except:
            task_name = project_name = client_name = "Unknown"

        ttk.Label(form_frame, text=f"Task: {task_name} - {project_name} - {client_name}").grid(row=0, column=0,
                                                                                               columnspan=2,
                                                                                               sticky='w', pady=5)

        ttk.Label(form_frame, text="Start Time:").grid(row=1, column=0, sticky='w', pady=2)
        start_entry = ttk.Entry(form_frame, width=20)
        start_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=2)
        start_entry.insert(0, entry[9] if len(entry) > 9 and entry[9] else "")

        ttk.Label(form_frame, text="End Time:").grid(row=2, column=0, sticky='w', pady=2)
        end_entry = ttk.Entry(form_frame, width=20)
        end_entry.grid(row=2, column=1, sticky='ew', padx=5, pady=2)
        end_entry.insert(0, entry[10] if len(entry) > 10 and entry[10] else "")

        ttk.Label(form_frame, text="Description:").grid(row=3, column=0, sticky='w', pady=2)
        desc_entry = ttk.Entry(form_frame)
        desc_entry.grid(row=3, column=1, sticky='ew', padx=5, pady=2)
        desc_entry.insert(0, entry[13] if len(entry) > 13 and entry[13] else "")

        form_frame.columnconfigure(1, weight=1)

        # Buttons
        button_frame = ttk.Frame(edit_window)
        button_frame.pack(fill='x', padx=10, pady=10)

        def save_changes():
            try:
                start_time = datetime.fromisoformat(start_entry.get())
                end_time = datetime.fromisoformat(end_entry.get())
                description = desc_entry.get()

                if end_time <= start_time:
                    messagebox.showerror("Error", "End time must be after start time")
                    return

                self.time_entry_model.update(entry_id, start_time, end_time, description)
                self.refresh_time_entries()
                edit_window.destroy()
                messagebox.showinfo("Success", "Time entry updated successfully")

            except ValueError as e:
                messagebox.showerror("Error", f"Invalid date format: {str(e)}")

        ttk.Button(button_frame, text="Save", command=save_changes).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Cancel", command=edit_window.destroy).pack(side='right')

    def delete_time_entry(self):
        selection = self.entries_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a time entry to delete")
            return

        if messagebox.askyesno("Confirm", "Delete this time entry?"):
            entry_id = self.entries_tree.item(selection[0])['values'][0]
            self.time_entry_model.delete(entry_id)
            self.refresh_time_entries()
            messagebox.showinfo("Success", "Time entry deleted successfully")

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
            entry_id = self.entries_tree.item(item)['values'][0]
            entry_client = self.entries_tree.item(item)['values'][1]
            entry_task = self.entries_tree.item(item)['values'][3]

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

        if not name:
            messagebox.showerror("Error", "Company name is required")
            return

        self.company_model.save(name, address, phone, email, logo_path)
        messagebox.showinfo("Success", "Company information saved successfully")

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

        # Add tasks
        tasks = self.task_model.get_all()
        for task in tasks:
            # Task structure from models.py get_all():
            # 0: id, 1: project_id, 2: name, 3: description,
            # 4: hourly_rate, 5: is_lump_sum, 6: lump_sum_amount, 7: created_at
            # 8: project_name, 9: client_name

            billing_type = "Lump Sum" if task[5] else "Hourly"
            rate = f"${task[6]:.2f}" if task[5] else f"${task[4]:.2f}/hr"

            # Verify we have project and client names
            project_name = task[8] if len(task) > 8 and task[8] else "Unknown Project"
            client_name = task[9] if len(task) > 9 and task[9] else "Unknown Client"

            self.task_tree.insert('', 'end', values=(
                task[0],  # ID
                project_name,  # Project name
                client_name,  # Client name
                task[2],  # Task name
                billing_type,
                rate
            ))

    def refresh_time_entries(self):
        # Clear tree
        for item in self.entries_tree.get_children():
            self.entries_tree.delete(item)

        # Add time entries
        entries = self.time_entry_model.get_all()
        for entry in entries:
            duration_minutes = entry[6] if entry[6] else 0
            duration_hours = duration_minutes / 60.0

            # Format start time nicely
            start_time = entry[4]
            try:
                dt = datetime.fromisoformat(start_time)
                start_display = dt.strftime("%m/%d/%y %I:%M %p")
            except:
                start_display = start_time

            # Add billed indicator
            is_billed = entry[8]
            billed_indicator = " [BILLED]" if is_billed else ""

            self.entries_tree.insert('', 'end', values=(
                entry[0],  # ID
                entry[1],  # Client name
                entry[2],  # Project name
                entry[3] + billed_indicator,  # Task name with billed indicator
                start_display,  # Start time formatted
                f"{duration_hours:.2f}",  # Duration in hours
                entry[7] or ""  # Description
            ))

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
