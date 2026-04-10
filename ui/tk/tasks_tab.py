from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class TasksTabMixin:
    def create_tasks_tab(self):
        # Tasks tab
        tasks_frame = ttk.Frame(self.notebook)
        self.notebook.add(tasks_frame, text="Tasks")

        # Task form
        task_form = ttk.LabelFrame(tasks_frame, text="Task Information")
        task_form.pack(fill="x", padx=10, pady=10)

        form_frame = ttk.Frame(task_form)
        form_frame.pack(fill="x", padx=10, pady=10)

        # Client selector
        ttk.Label(form_frame, text="Client:").grid(row=0, column=0, sticky="w", pady=2)
        self.task_client_combo = ttk.Combobox(form_frame, state="readonly")
        self.task_client_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        self.task_client_combo.bind("<<ComboboxSelected>>", self.on_task_client_select)

        # Project selector
        ttk.Label(form_frame, text="Project:").grid(row=1, column=0, sticky="w", pady=2)
        self.task_project_combo = ttk.Combobox(form_frame, state="readonly")
        self.task_project_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(form_frame, text="Name:").grid(row=2, column=0, sticky="w", pady=2)
        self.task_name_entry = ttk.Entry(form_frame)
        self.task_name_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(form_frame, text="Description:").grid(row=3, column=0, sticky="nw", pady=2)
        self.task_desc_text = tk.Text(form_frame, height=3)
        self.task_desc_text.grid(row=3, column=1, sticky="ew", padx=5, pady=2)

        # Global task checkbox
        global_frame = ttk.Frame(form_frame)
        global_frame.grid(row=4, column=0, columnspan=2, sticky="w", pady=10)

        self.task_global_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            global_frame,
            text="[GLOBAL] Make this available for all projects",
            variable=self.task_global_var,
            command=self.toggle_task_project_field,
        ).pack(side="left")

        # Task billing options
        billing_frame = ttk.Frame(form_frame)
        billing_frame.grid(row=5, column=1, sticky="ew", padx=5, pady=2)

        self.task_billing_var = tk.StringVar(value="hourly")
        ttk.Radiobutton(
            billing_frame,
            text="Hourly Rate",
            variable=self.task_billing_var,
            value="hourly",
            command=self.toggle_task_billing,
        ).pack(side="left")
        ttk.Radiobutton(
            billing_frame,
            text="Lump Sum",
            variable=self.task_billing_var,
            value="lump_sum",
            command=self.toggle_task_billing,
        ).pack(side="left", padx=10)

        ttk.Label(form_frame, text="Rate/Amount:").grid(row=6, column=0, sticky="w", pady=2)
        self.task_rate_entry = ttk.Entry(form_frame)
        self.task_rate_entry.grid(row=6, column=1, sticky="ew", padx=5, pady=2)

        form_frame.columnconfigure(1, weight=1)

        # Task buttons
        button_frame = ttk.Frame(task_form)
        button_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(button_frame, text="Add Task", command=self.add_task).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Update Task", command=self.update_task).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_task_form).pack(side="left", padx=5)

        # Task list
        list_frame = ttk.LabelFrame(tasks_frame, text="Tasks")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.task_tree = ttk.Treeview(list_frame, columns=("Type", "ID", "Extra", "Billing", "Rate"))
        self.task_tree.heading("#0", text="Hierarchy")
        self.task_tree.heading("Type", text="Type")
        self.task_tree.heading("ID", text="")
        self.task_tree.heading("Extra", text="")
        self.task_tree.heading("Billing", text="Billing Type")
        self.task_tree.heading("Rate", text="Rate/Amount")

        self.task_tree.column("#0", width=300)
        self.task_tree.column("Type", width=100)
        self.task_tree.column("ID", width=0, minwidth=0, stretch=False)
        self.task_tree.column("Extra", width=100)
        self.task_tree.column("Billing", width=100)
        self.task_tree.column("Rate", width=100)

        self.task_tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.task_tree.bind("<<TreeviewSelect>>", self.on_task_select)

        # Task buttons
        task_button_frame = ttk.Frame(list_frame)
        task_button_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(task_button_frame, text="Delete Task", command=self.delete_task).pack(side="left", padx=5)

