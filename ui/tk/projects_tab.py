from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class ProjectsTabMixin:
    def create_projects_tab(self):
        # Projects tab
        projects_frame = ttk.Frame(self.notebook)
        self.notebook.add(projects_frame, text="Projects")

        # Project form
        project_form = ttk.LabelFrame(projects_frame, text="Project Information")
        project_form.pack(fill="x", padx=10, pady=10)

        form_frame = ttk.Frame(project_form)
        form_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(form_frame, text="Client:").grid(row=0, column=0, sticky="w", pady=2)
        self.project_client_combo = ttk.Combobox(form_frame, state="readonly")
        self.project_client_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(form_frame, text="Name:").grid(row=1, column=0, sticky="w", pady=2)
        self.project_name_entry = ttk.Entry(form_frame)
        self.project_name_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(form_frame, text="Description:").grid(row=2, column=0, sticky="nw", pady=2)
        self.project_desc_text = tk.Text(form_frame, height=3)
        self.project_desc_text.grid(row=2, column=1, sticky="ew", padx=5, pady=2)

        # Project billing options
        billing_frame = ttk.Frame(form_frame)
        billing_frame.grid(row=3, column=1, sticky="ew", padx=5, pady=2)

        self.project_billing_var = tk.StringVar(value="hourly")
        ttk.Radiobutton(
            billing_frame,
            text="Hourly Rate",
            variable=self.project_billing_var,
            value="hourly",
            command=self.toggle_project_billing,
        ).pack(side="left")
        ttk.Radiobutton(
            billing_frame,
            text="Lump Sum",
            variable=self.project_billing_var,
            value="lump_sum",
            command=self.toggle_project_billing,
        ).pack(side="left", padx=10)

        ttk.Label(form_frame, text="Rate/Amount:").grid(row=4, column=0, sticky="w", pady=2)
        self.project_rate_entry = ttk.Entry(form_frame)
        self.project_rate_entry.grid(row=4, column=1, sticky="ew", padx=5, pady=2)

        form_frame.columnconfigure(1, weight=1)

        # Project buttons
        button_frame = ttk.Frame(project_form)
        button_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(button_frame, text="Add Project", command=self.add_project).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Update Project", command=self.update_project).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_project_form).pack(side="left", padx=5)

        # Project list
        list_frame = ttk.LabelFrame(projects_frame, text="Projects")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.project_tree = ttk.Treeview(
            list_frame,
            columns=("ID", "Client", "Name", "Type", "Rate"),
            show="headings",
        )
        self.project_tree.heading("ID", text="ID")
        self.project_tree.heading("Client", text="Client")
        self.project_tree.heading("Name", text="Project")
        self.project_tree.heading("Type", text="Billing Type")
        self.project_tree.heading("Rate", text="Rate/Amount")

        self.project_tree.column("ID", width=50)
        self.project_tree.column("Client", width=150)
        self.project_tree.column("Name", width=200)
        self.project_tree.column("Type", width=100)
        self.project_tree.column("Rate", width=100)

        self.project_tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.project_tree.bind("<<TreeviewSelect>>", self.on_project_select)

        # Project buttons
        project_button_frame = ttk.Frame(list_frame)
        project_button_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(project_button_frame, text="Delete Project", command=self.delete_project).pack(side="left", padx=5)

