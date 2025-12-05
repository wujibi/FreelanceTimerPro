import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
from database import DatabaseManager
from models import Client, Project, Task, TimeEntry, CompanyInfo
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
        self.task_combo = ttk.Combobox(task_frame, state='readonly')
        self.task_combo.pack(side='left', fill='x', expand=True, padx=5)

        # Timer buttons
        button_frame = ttk.Frame(timer_display_frame)
        button_frame.pack(pady=10)

        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_timer)
        self.start_button.pack(side='left', padx=5)

        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_timer, state='disabled')
        self.stop_button.pack(side='left', padx=5)

        # Description
        desc_frame = ttk.Frame(timer_display_frame)
        desc_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(desc_frame, text="Description:").pack(side='left')
        self.timer_desc_entry = ttk.Entry(desc_frame)
        self.timer_desc_entry.pack(side='left', fill='x', expand=True, padx=5)

        # Manual entry section
        manual_frame = ttk.LabelFrame(timer_frame, text="Manual Time Entry")
        manual_frame.pack(fill='x', padx=10, pady=10)

        # Manual entry form
        form_frame = ttk.Frame(manual_frame)
        form_frame.pack(fill='x', padx=10, pady=10)

        # Client selection for manual entry
        ttk.Label(form_frame, text="Client:").grid(row=0, column=0, sticky='w', pady=2)
        self.manual_client_combo = ttk.Combobox(form_frame, state='readonly')
        self.manual_client_combo.grid(row=0, column=1, sticky='ew', padx=5, pady=2)
        self.manual_client_combo.bind('<<ComboboxSelected>>', self.on_manual_client_select)

        # Project selection for manual entry
        ttk.Label(form_frame, text="Project:").grid(row=1, column=0, sticky='w', pady=2)
        self.manual_project_combo = ttk.Combobox(form_frame, state='readonly')
        self.manual_project_combo.grid(row=1, column=1, sticky='ew', padx=5, pady=2)
        self.manual_project_combo.bind('<<ComboboxSelected>>', self.on_manual_project_select)

        # Task selection for manual entry
        ttk.Label(form_frame, text="Task:").grid(row=2, column=0, sticky='w', pady=2)
        self.manual_task_combo = ttk.Combobox(form_frame, state='readonly')
        self.manual_task_combo.grid(row=2, column=1, sticky='ew', padx=5, pady=2)

        # Start time
        ttk.Label(form_frame, text="Start Time:").grid(row=3, column=0, sticky='w', pady=2)
        self.start_time_entry = ttk.Entry(form_frame)
        self.start_time_entry.grid(row=3, column=1, sticky='ew', padx=5, pady=2)
        self.start_time_entry.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # End time
        ttk.Label(form_frame, text="End Time:").grid(row=4, column=0, sticky='w', pady=2)
        self.end_time_entry = ttk.Entry(form_frame)
        self.end_time_entry.grid(row=4, column=1, sticky='ew', padx=5, pady=2)
        self.end_time_entry.insert(0, (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"))

        # Description
        ttk.Label(form_frame, text="Description:").grid(row=5, column=0, sticky='w', pady=2)
        self.manual_desc_entry = ttk.Entry(form_frame)
        self.manual_desc_entry.grid(row=5, column=1, sticky='ew', padx=5, pady=2)

        form_frame.columnconfigure(1, weight=1)

        # Add manual entry button
        ttk.Button(manual_frame, text="Add Manual Entry", command=self.add_manual_entry).pack(pady=10)

        # Start timer update thread
        self.update_timer_display()

    def create_clients_tab(self):
        # Clients tab
        clients_frame = ttk.Frame(self.notebook)
        self.notebook.add(clients_frame, text="Clients")

        # Client form
        client_form = ttk.LabelFrame(clients_frame, text="Add/Edit Client")
        client_form.pack(fill='x', padx=10, pady=10)

        form_frame = ttk.Frame(client_form)
        form_frame.pack(fill='x', padx=10, pady=10)

        # Client form fields
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

        ttk.Label(form_frame, text="Address:").grid(row=4, column=0, sticky='w', pady=2)
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

        # Treeview for clients
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
        self.client_tree.column('Phone', width=150)

        self.client_tree.pack(fill='both', expand=True, padx=10, pady=10)
        self.client_tree.bind('<<TreeviewSelect>>', self.on_client_select)

        # Client list buttons
        client_button_frame = ttk.Frame(list_frame)
        client_button_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(client_button_frame, text="Delete Client", command=self.delete_client).pack(side='left', padx=5)

    def create_projects_tab(self):
        # Projects tab
        projects_frame = ttk.Frame(self.notebook)
        self.notebook.add(projects_frame, text="Projects")

        # Project form
        project_form = ttk.LabelFrame(projects_frame, text="Add/Edit Project")
        project_form.pack(fill='x', padx=10, pady=10)

        form_frame = ttk.Frame(project_form)
        form_frame.pack(fill='x', padx=10, pady=10)

        # Project form fields
        ttk.Label(form_frame, text="Client:").grid(row=0, column=0, sticky='w', pady=2)
        self.project_client_combo = ttk.Combobox(form_frame, state='readonly')
        self.project_client_combo.grid(row=0, column=1, sticky='ew', padx=5, pady=2)

        ttk.Label(form_frame, text="Project Name:").grid(row=1, column=0, sticky='w', pady=2)
        self.project_name_entry = ttk.Entry(form_frame)
        self.project_name_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=2)

        ttk.Label(form_frame, text="Description:").grid(row=2, column=0, sticky='w', pady=2)
        self.project_desc_text = tk.Text(form_frame, height=3)
        self.project_desc_text.grid(row=2, column=1, sticky='ew', padx=5, pady=2)

        # Billing options
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

        self.project_tree = ttk.Treeview(list_frame, columns=('ID', 'Client', 'Name', 'Type', 'Rate'), show='headings')
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
        # Tasks tab (similar structure to projects)
        tasks_frame = ttk.Frame(self.notebook)
        self.notebook.add(tasks_frame, text="Tasks")

        # Task form
        task_form = ttk.LabelFrame(tasks_frame, text="Add/Edit Task")
        task_form.pack(fill='x', padx=10, pady=10)

        form_frame = ttk.Frame(task_form)
        form_frame.pack(fill='x', padx=10, pady=10)

        # Task form fields
        ttk.Label(form_frame, text="Project:").grid(row=0, column=0, sticky='w', pady=2)
        self.task_project_combo = ttk.Combobox(form_frame, state='readonly')
        self.task_project_combo.grid(row=0, column=1, sticky='ew', padx=5, pady=2)

        ttk.Label(form_frame, text="Task Name:").grid(row=1, column=0, sticky='w', pady=2)
        self.task_name_entry = ttk.Entry(form_frame)
        self.task_name_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=2)

        ttk.Label(form_frame, text="Description:").grid(row=2, column=0, sticky='w', pady=2)
        self.task_desc_text = tk.Text(form_frame, height=3)
        self.task_desc_text.grid(row=2, column=1, sticky='ew', padx=5, pady=2)

        # Task billing options
        billing_frame = ttk.Frame(form_frame)
        billing_frame.grid(row=3, column=1, sticky='ew', padx=5, pady=2)

        self.task_billing_var = tk.StringVar(value="hourly")
        ttk.Radiobutton(billing_frame, text="Hourly Rate", variable=self.task_billing_var,
                        value="hourly", command=self.toggle_task_billing).pack(side='left')
        ttk.Radiobutton(billing_frame, text="Lump Sum", variable=self.task_billing_var,
                        value="lump_sum", command=self.toggle_task_billing).pack(side='left', padx=10)

        ttk.Label(form_frame, text="Rate/Amount:").grid(row=4, column=0, sticky='w', pady=2)
        self.task_rate_entry = ttk.Entry(form_frame)
        self.task_rate_entry.grid(row=4, column=1, sticky='ew', padx=5, pady=2)

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
                                                              'Description'), show='headings')
        self.entries_tree.heading('ID', text='ID')
        self.entries_tree.heading('Client', text='Client')
        self.entries_tree.heading('Project', text='Project')
        self.entries_tree.heading('Task', text='Task')
        self.entries_tree.heading('Start', text='Start Time')
        self.entries_tree.heading('Duration', text='Duration (min)')
        self.entries_tree.heading('Description', text='Description')

        self.entries_tree.column('ID', width=50)
        self.entries_tree.column('Client', width=100)
        self.entries_tree.column('Project', width=100)
        self.entries_tree.column('Task', width=100)
        self.entries_tree.column('Start', width=150)
        self.entries_tree.column('Duration', width=100)
        self.entries_tree.column('Description', width=200)

        self.entries_tree.pack(fill='both', expand=True, padx=10, pady=10)
        self.entries_tree.bind('<<TreeviewSelect>>', self.on_entry_select)

        # Entry buttons
        entry_button_frame = ttk.Frame(list_frame)
        entry_button_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(entry_button_frame, text="Edit Entry", command=self.edit_entry).pack(side='left', padx=5)
        ttk.Button(entry_button_frame, text="Delete Entry", command=self.delete_entry).pack(side='left', padx=5)

    def create_company_tab(self):
        # Company info tab
        company_frame = ttk.Frame(self.notebook)
        self.notebook.add(company_frame, text="Company Info")

        # Company form
        company_form = ttk.LabelFrame(company_frame, text="Company Information")
        company_form.pack(fill='x', padx=10, pady=10)

        form_frame = ttk.Frame(company_form)
        form_frame.pack(fill='x', padx=10, pady=10)

        # Company form fields
        ttk.Label(form_frame, text="Company Name:").grid(row=0, column=0, sticky='w', pady=2)
        self.company_name_entry = ttk.Entry(form_frame)
        self.company_name_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=2)

        ttk.Label(form_frame, text="Address:").grid(row=1, column=0, sticky='w', pady=2)
        self.company_address_text = tk.Text(form_frame, height=3)
        self.company_address_text.grid(row=1, column=1, sticky='ew', padx=5, pady=2)

        ttk.Label(form_frame, text="Phone:").grid(row=2, column=0, sticky='w', pady=2)
        self.company_phone_entry = ttk.Entry(form_frame)
        self.company_phone_entry.grid(row=2, column=1, sticky='ew', padx=5, pady=2)

        ttk.Label(form_frame, text="Email:").grid(row=3, column=0, sticky='w', pady=2)
        self.company_email_entry = ttk.Entry(form_frame)
        self.company_email_entry.grid(row=3, column=1, sticky='ew', padx=5, pady=2)

        # Logo selection
        logo_frame = ttk.Frame(form_frame)
        logo_frame.grid(row=4, column=1, sticky='ew', padx=5, pady=2)

        self.logo_path_var = tk.StringVar()
        ttk.Label(logo_frame, textvariable=self.logo_path_var).pack(side='left', fill='x', expand=True)
        ttk.Button(logo_frame, text="Browse Logo", command=self.browse_logo).pack(side='right')

        form_frame.columnconfigure(1, weight=1)

        # Save button
        ttk.Button(company_form, text="Save Company Info", command=self.save_company_info).pack(pady=10)

        # Load existing company info
        self.load_company_info()

    def create_invoice_tab(self):
        # Invoice tab
        invoice_frame = ttk.Frame(self.notebook)
        self.notebook.add(invoice_frame, text="Invoicing")

        # Invoice generation section
        invoice_gen_frame = ttk.LabelFrame(invoice_frame, text="Generate Invoice")
        invoice_gen_frame.pack(fill='x', padx=10, pady=10)

        form_frame = ttk.Frame(invoice_gen_frame)
        form_frame.pack(fill='x', padx=10, pady=10)

        # Invoice form fields
        ttk.Label(form_frame, text="Client:").grid(row=0, column=0, sticky='w', pady=2)
        self.invoice_client_combo = ttk.Combobox(form_frame, state='readonly')
        self.invoice_client_combo.grid(row=0, column=1, sticky='ew', padx=5, pady=2)
        self.invoice_client_combo.bind('<<ComboboxSelected>>', self.on_invoice_client_select)

        ttk.Label(form_frame, text="Date Range:").grid(row=1, column=0, sticky='w', pady=2)
        date_frame = ttk.Frame(form_frame)
        date_frame.grid(row=1, column=1, sticky='ew', padx=5, pady=2)

        self.invoice_start_date = ttk.Entry(date_frame, width=12)
        self.invoice_start_date.pack(side='left')
        self.invoice_start_date.insert(0, (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))

        ttk.Label(date_frame, text=" to ").pack(side='left')

        self.invoice_end_date = ttk.Entry(date_frame, width=12)
        self.invoice_end_date.pack(side='left')
        self.invoice_end_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

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
            messagebox.showerror("Error", "Please select a project")
            return

        if not self.task_combo.get():
            messagebox.showerror("Error", "Please select a task")
            return

        task_id = self.get_selected_task_id()
        if task_id:
            self.timer_running = True
            self.timer_start_time = datetime.now()
            self.current_task_id = task_id

            # Create time entry in database
            self.time_entry_model.start_timer(task_id, self.timer_desc_entry.get())

            # Update UI
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.timer_client_combo.config(state='disabled')
            self.timer_project_combo.config(state='disabled')
            self.task_combo.config(state='disabled')

    def stop_timer(self):
        if self.timer_running:
            self.timer_running = False
            self.time_entry_model.stop_timer()

            # Update UI
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            self.timer_client_combo.config(state='readonly')
            self.timer_project_combo.config(state='readonly')
            self.task_combo.config(state='readonly')

            # Clear fields
            self.timer_desc_entry.delete(0, 'end')

            # Refresh data
            self.refresh_time_entries()

    def update_timer_display(self):
        if self.timer_running and self.timer_start_time:
            elapsed = datetime.now() - self.timer_start_time
            hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            self.timer_label.config(text=time_str)

        # Schedule next update
        self.root.after(1000, self.update_timer_display)

    def add_manual_entry(self):
        try:
            task_id = self.get_selected_manual_task_id()
            if not task_id:
                messagebox.showerror("Error", "Please select a client, project, and task")
                return

            start_time = datetime.strptime(self.start_time_entry.get(), "%Y-%m-%d %H:%M:%S")
            end_time = datetime.strptime(self.end_time_entry.get(), "%Y-%m-%d %H:%M:%S")
            description = self.manual_desc_entry.get()

            if end_time <= start_time:
                messagebox.showerror("Error", "End time must be after start time")
                return

            self.time_entry_model.add_manual_entry(task_id, start_time, end_time, description)

            # Clear form
            self.manual_desc_entry.delete(0, 'end')

            # Refresh data
            self.refresh_time_entries()

            messagebox.showinfo("Success", "Manual time entry added successfully")

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid date format. Use YYYY-MM-DD HH:MM:SS\n{str(e)}")

    # New timer selection methods
    def on_timer_client_select(self, event):
        """When client is selected in timer, populate projects for that client"""
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
                # Get projects for this client
                self.populate_projects_for_client(client_id, self.timer_project_combo)

            # Clear project and task selections when client changes
            self.timer_project_combo.set("")
            self.task_combo.set("")
            self.task_combo['values'] = []

    def on_timer_project_select(self, event):
        """When project is selected in timer, populate tasks for that project"""
        project_name = self.timer_project_combo.get()
        if project_name:
            # Get project ID
            projects = self.project_model.get_all()
            project_id = None
            for project in projects:
                if project[2] == project_name:  # project name is at index 2
                    project_id = project[0]
                    break

            if project_id:
                # Get tasks for this project
                self.populate_tasks_for_project(project_id, self.task_combo)

            # Clear task selection when project changes
            self.task_combo.set("")

    def on_manual_client_select(self, event):
        """When client is selected in manual entry, populate projects for that client"""
        client_name = self.manual_client_combo.get()
        if client_name:
            # Get client ID
            clients = self.client_model.get_all()
            client_id = None
            for client in clients:
                if client[1] == client_name:
                    client_id = client[0]
                    break

            if client_id:
                # Get projects for this client
                self.populate_projects_for_client(client_id, self.manual_project_combo)

            # Clear project and task selections when client changes
            self.manual_project_combo.set("")
            self.manual_task_combo.set("")
            self.manual_task_combo['values'] = []

    def on_manual_project_select(self, event):
        """When project is selected in manual entry, populate tasks for that project"""
        project_name = self.manual_project_combo.get()
        if project_name:
            # Get project ID
            projects = self.project_model.get_all()
            project_id = None
            for project in projects:
                if project[2] == project_name:  # project name is at index 2
                    project_id = project[0]
                    break

            if project_id:
                # Get tasks for this project
                self.populate_tasks_for_project(project_id, self.manual_task_combo)

            # Clear task selection when project changes
            self.manual_task_combo.set("")

    def populate_projects_for_client(self, client_id, project_combo):
        """Populate project combo with projects for the specified client"""
        projects = self.project_model.get_by_client(client_id)
        project_names = [project[2] for project in projects]  # project name is at index 2
        project_combo['values'] = project_names

    def populate_tasks_for_project(self, project_id, task_combo):
        """Populate task combo with tasks for the specified project"""
        tasks = self.task_model.get_by_project(project_id)
        task_names = [task[2] for task in tasks]  # task name is at index 2
        task_combo['values'] = task_names

    # Helper methods
    def get_selected_task_id(self):
        task_name = self.task_combo.get()
        project_name = self.timer_project_combo.get()

        if task_name and project_name:
            # Get project ID first
            projects = self.project_model.get_all()
            project_id = None
            for project in projects:
                if project[2] == project_name:
                    project_id = project[0]
                    break

            if project_id:
                # Get task ID for this project
                tasks = self.task_model.get_by_project(project_id)
                for task in tasks:
                    if task[2] == task_name:  # task name is at index 2
                        return task[0]  # return task ID
        return None

    def get_selected_manual_task_id(self):
        task_name = self.manual_task_combo.get()
        project_name = self.manual_project_combo.get()

        if task_name and project_name:
            # Get project ID first
            projects = self.project_model.get_all()
            project_id = None
            for project in projects:
                if project[2] == project_name:
                    project_id = project[0]
                    break

            if project_id:
                # Get task ID for this project
                tasks = self.task_model.get_by_project(project_id)
                for task in tasks:
                    if task[2] == task_name:  # task name is at index 2
                        return task[0]  # return task ID
        return None

    # Client methods
    def add_client(self):
        name = self.client_name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Client name is required")
            return

        company = self.client_company_entry.get().strip()
        email = self.client_email_entry.get().strip()
        phone = self.client_phone_entry.get().strip()
        address = self.client_address_text.get("1.0", tk.END).strip()

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

        if not name:
            messagebox.showerror("Error", "Client name is required")
            return

        company = self.client_company_entry.get().strip()
        email = self.client_email_entry.get().strip()
        phone = self.client_phone_entry.get().strip()
        address = self.client_address_text.get("1.0", tk.END).strip()

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

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this client?"):
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

        if not client_text or not name:
            messagebox.showerror("Error", "Client and project name are required")
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

        description = self.project_desc_text.get("1.0", tk.END).strip()
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
        name = self.project_name_entry.get().strip()

        if not name:
            messagebox.showerror("Error", "Project name is required")
            return

        description = self.project_desc_text.get("1.0", tk.END).strip()
        rate = float(self.project_rate_entry.get() or 0)
        is_lump_sum = self.project_billing_var.get() == "lump_sum"

        if is_lump_sum:
            self.project_model.update(project_id, name, description, 0, True, rate)
        else:
            self.project_model.update(project_id, name, description, rate, False, 0)

        self.clear_project_form()
        self.refresh_projects()
        self.refresh_combos()
        messagebox.showinfo("Success", "Project updated successfully")

    def delete_project(self):
        selection = self.project_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a project to delete")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this project?"):
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
        project_text = self.task_project_combo.get()
        name = self.task_name_entry.get().strip()

        if not project_text or not name:
            messagebox.showerror("Error", "Project and task name are required")
            return

        # Get project ID
        projects = self.project_model.get_all()
        project_id = None
        for project in projects:
            project_display = f"{project[8]} - {project[2]}"  # client - project
            if project_display == project_text:
                project_id = project[0]
                break

        if not project_id:
            messagebox.showerror("Error", "Invalid project selected")
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

        if not name:
            messagebox.showerror("Error", "Task name is required")
            return

        description = self.task_desc_text.get("1.0", tk.END).strip()
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

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this task?"):
            task_id = self.task_tree.item(selection[0])['values'][0]
            self.task_model.delete(task_id)
            self.refresh_tasks()
            self.refresh_combos()
            messagebox.showinfo("Success", "Task deleted successfully")

    def clear_task_form(self):
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
                # Set project
                project = self.project_model.get_by_id(task[1])
                if project:
                    client = self.client_model.get_by_id(project[1])
                    if client:
                        project_display = f"{client[1]} - {project[2]}"
                        self.task_project_combo.set(project_display)

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

    # Time entry methods
    def edit_entry(self):
        selection = self.entries_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a time entry to edit")
            return

        entry_id = self.entries_tree.item(selection[0])['values'][0]
        self.open_edit_entry_dialog(entry_id)

    def delete_entry(self):
        selection = self.entries_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a time entry to delete")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this time entry?"):
            entry_id = self.entries_tree.item(selection[0])['values'][0]
            self.time_entry_model.delete(entry_id)
            self.refresh_time_entries()
            messagebox.showinfo("Success", "Time entry deleted successfully")

    def on_entry_select(self, event):
        pass

    def open_edit_entry_dialog(self, entry_id):
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Time Entry")
        edit_window.geometry("400x300")

        # Get current entry data
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                           SELECT te.*, t.name as task_name, p.name as project_name, c.name as client_name
                           FROM time_entries te
                                    JOIN tasks t ON te.task_id = t.id
                                    JOIN projects p ON t.project_id = p.id
                                    JOIN clients c ON p.client_id = c.id
                           WHERE te.id = ?
                           ''', (entry_id,))
            entry = cursor.fetchone()

        if not entry:
            messagebox.showerror("Error", "Time entry not found")
            edit_window.destroy()
            return

        # Create form
        form_frame = ttk.Frame(edit_window)
        form_frame.pack(fill='both', expand=True, padx=10, pady=10)

        ttk.Label(form_frame, text=f"Task: {entry[10]} - {entry[9]} - {entry[8]}").grid(row=0, column=0, columnspan=2,
                                                                                        sticky='w', pady=5)

        ttk.Label(form_frame, text="Start Time:").grid(row=1, column=0, sticky='w', pady=2)
        start_entry = ttk.Entry(form_frame, width=20)
        start_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=2)
        start_entry.insert(0, entry[2] if entry[2] else "")

        ttk.Label(form_frame, text="End Time:").grid(row=2, column=0, sticky='w', pady=2)
        end_entry = ttk.Entry(form_frame, width=20)
        end_entry.grid(row=2, column=1, sticky='ew', padx=5, pady=2)
        end_entry.insert(0, entry[3] if entry[3] else "")

        ttk.Label(form_frame, text="Description:").grid(row=3, column=0, sticky='w', pady=2)
        desc_entry = ttk.Entry(form_frame)
        desc_entry.grid(row=3, column=1, sticky='ew', padx=5, pady=2)
        desc_entry.insert(0, entry[5] if entry[5] else "")

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
        if not name:
            messagebox.showerror("Error", "Company name is required")
            return

        address = self.company_address_text.get("1.0", tk.END).strip()
        phone = self.company_phone_entry.get().strip()
        email = self.company_email_entry.get().strip()
        logo_path = self.logo_path_var.get()

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

            self.logo_path_var.set(company[5] or "")

    # Invoice methods
    def on_invoice_client_select(self, event):
        pass

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
            start_date = datetime.strptime(self.invoice_start_date.get(), "%Y-%m-%d")
            end_date = datetime.strptime(self.invoice_end_date.get(), "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
            return

        # Generate invoice data
        self.current_invoice_data = self.generate_invoice_data(client_id, start_date, end_date)
        self.display_invoice_preview()

    def generate_invoice_data(self, client_id, start_date, end_date):
        # Get time entries for the client within date range
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                           SELECT te.*,
                                  t.name            as task_name,
                                  t.hourly_rate     as task_rate,
                                  t.is_lump_sum     as task_lump_sum,
                                  t.lump_sum_amount as task_lump_sum_amount,
                                  p.name            as project_name,
                                  p.hourly_rate     as project_rate,
                                  p.is_lump_sum     as project_lump_sum,
                                  p.lump_sum_amount as project_lump_sum_amount,
                                  c.name            as client_name
                           FROM time_entries te
                                    JOIN tasks t ON te.task_id = t.id
                                    JOIN projects p ON t.project_id = p.id
                                    JOIN clients c ON p.client_id = c.id
                           WHERE c.id = ? AND DATE (te.start_time) BETWEEN ? AND ?
                           ORDER BY te.start_time
                           ''', (client_id, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
            entries = cursor.fetchall()

        # Group entries based on user preference
        invoice_items = []
        group_by = self.invoice_group_var.get()

        if group_by == "project":
            # Group by project
            project_groups = {}
            for entry in entries:
                project_name = entry[12]
                if project_name not in project_groups:
                    project_groups[project_name] = {
                        'entries': [],
                        'total_minutes': 0,
                        'project_rate': entry[13],
                        'is_lump_sum': entry[14],
                        'lump_sum_amount': entry[15]
                    }
                project_groups[project_name]['entries'].append(entry)
                project_groups[project_name]['total_minutes'] += entry[4] or 0

            for project_name, data in project_groups.items():
                total_hours = data['total_minutes'] / 60.0
                if data['is_lump_sum']:
                    amount = data['lump_sum_amount']
                    rate_display = f"${amount:.2f}"
                    qty_display = "1"
                else:
                    rate = data['project_rate']
                    amount = total_hours * rate
                    rate_display = f"${rate:.2f}/hr"
                    qty_display = f"{total_hours:.2f}"

                invoice_items.append({
                    'description': f"Project: {project_name}",
                    'quantity': qty_display,
                    'rate': rate_display,
                    'amount': amount
                })

        else:  # Group by task
            task_groups = {}
            for entry in entries:
                task_name = entry[7]
                if task_name not in task_groups:
                    task_groups[task_name] = {
                        'entries': [],
                        'total_minutes': 0,
                        'task_rate': entry[8],
                        'is_lump_sum': entry[9],
                        'lump_sum_amount': entry[10],
                        'project_name': entry[12]
                    }
                task_groups[task_name]['entries'].append(entry)
                task_groups[task_name]['total_minutes'] += entry[4] or 0

            for task_name, data in task_groups.items():
                total_hours = data['total_minutes'] / 60.0
                if data['is_lump_sum']:
                    amount = data['lump_sum_amount']
                    rate_display = f"${amount:.2f}"
                    qty_display = "1"
                else:
                    rate = data['task_rate']
                    amount = total_hours * rate
                    rate_display = f"${rate:.2f}/hr"
                    qty_display = f"{total_hours:.2f}"

                invoice_items.append({
                    'description': f"{data['project_name']} - {task_name}",
                    'quantity': qty_display,
                    'rate': rate_display,
                    'amount': amount
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

        # Generate invoice number based on date
        invoice_date = datetime.now()
        invoice_number = invoice_date.strftime("%Y%m%d")

        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"Invoice_{invoice_number}.pdf"
        )

        if filename:
            from invoice_generator import InvoiceGenerator
            generator = InvoiceGenerator(self.db)
            generator.generate_pdf(self.current_invoice_data, filename, invoice_number)
            messagebox.showinfo("Success", f"Invoice saved as {filename}")

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

        def save_item_changes():
            desc = desc_entry.get()
            qty = qty_entry.get()
            rate = rate_entry.get()

            try:
                qty_num = float(qty)
                rate_num = float(rate.replace('$', '').replace('/hr', ''))
                amount = qty_num * rate_num

                self.invoice_tree.item(item_id, values=(desc, qty, rate, f"${amount:.2f}"))

                item_index = self.invoice_tree.index(item_id)
                self.current_invoice_data['items'][item_index] = {
                    'description': desc,
                    'quantity': qty,
                    'rate': rate,
                    'amount': amount
                }

                total = sum(item['amount'] for item in self.current_invoice_data['items'])
                self.current_invoice_data['total'] = total
                self.invoice_total_label.config(text=f"Total: ${total:.2f}")

                edit_window.destroy()

            except ValueError:
                messagebox.showerror("Error", "Invalid quantity or rate format")

        ttk.Button(button_frame, text="Save", command=save_item_changes).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Cancel", command=edit_window.destroy).pack(side='right')

    def remove_invoice_item(self):
        selection = self.invoice_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select an item to remove")
            return

        if messagebox.askyesno("Confirm", "Remove this item from the invoice?"):
            item_index = self.invoice_tree.index(selection[0])
            self.invoice_tree.delete(selection[0])

            del self.current_invoice_data['items'][item_index]

            total = sum(item['amount'] for item in self.current_invoice_data['items'])
            self.current_invoice_data['total'] = total
            self.invoice_total_label.config(text=f"Total: ${total:.2f}")

    # Data refresh methods
    def refresh_all_data(self):
        self.refresh_clients()
        self.refresh_projects()
        self.refresh_tasks()
        self.refresh_time_entries()
        self.refresh_combos()

    def refresh_clients(self):
        for item in self.client_tree.get_children():
            self.client_tree.delete(item)

        clients = self.client_model.get_all()
        for client in clients:
            self.client_tree.insert('', 'end', values=(
                client[0], client[1], client[2] or '', client[3] or '', client[4] or ''
            ))

    def refresh_projects(self):
        for item in self.project_tree.get_children():
            self.project_tree.delete(item)

        projects = self.project_model.get_all()
        for project in projects:
            billing_type = "Lump Sum" if project[5] else "Hourly"
            rate_amount = project[6] if project[5] else project[4]
            client_name = project[8] if len(project) > 8 else "Unknown Client"

            self.project_tree.insert('', 'end', values=(
                project[0], client_name, project[2], billing_type, f"${rate_amount:.2f}"
            ))

    def refresh_tasks(self):
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)

        tasks = self.task_model.get_all()
        for task in tasks:
            billing_type = "Lump Sum" if task[5] else "Hourly"
            rate_amount = task[6] if task[5] else task[4]
            project_name = task[7] if len(task) > 7 else "Unknown Project"
            client_name = task[8] if len(task) > 8 else "Unknown Client"

            self.task_tree.insert('', 'end', values=(
                task[0], project_name, client_name, task[2], billing_type, f"${rate_amount:.2f}"
            ))

    def refresh_time_entries(self):
        for item in self.entries_tree.get_children():
            self.entries_tree.delete(item)

        entries = self.time_entry_model.get_all()
        for entry in entries:
            duration_display = f"{entry[4] or 0} min" if entry[4] else "N/A"
            start_time_display = entry[2][:16] if entry[2] else "N/A"
            client_name = entry[10] if len(entry) > 10 else "Unknown"
            project_name = entry[9] if len(entry) > 9 else "Unknown"
            task_name = entry[8] if len(entry) > 8 else "Unknown"

            self.entries_tree.insert('', 'end', values=(
                entry[0], client_name, project_name, task_name, start_time_display, duration_display, entry[5] or ''
            ))

    def refresh_combos(self):
        # Refresh client combos
        clients = self.client_model.get_all()
        client_names = [client[1] for client in clients]

        self.project_client_combo['values'] = client_names
        self.invoice_client_combo['values'] = client_names
        self.timer_client_combo['values'] = client_names
        self.manual_client_combo['values'] = client_names

        # Clear the dependent combos since they now depend on selections
        self.timer_project_combo['values'] = []
        self.manual_project_combo['values'] = []
        self.task_combo['values'] = []
        self.manual_task_combo['values'] = []

        # Refresh project combos for the Tasks tab (unchanged)
        projects = self.project_model.get_all()
        if projects:
            project_displays = [f"{project[8]} - {project[2]}" for project in projects if len(project) > 8]
            self.task_project_combo['values'] = project_displays
