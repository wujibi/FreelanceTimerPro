from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class ClientsTabMixin:
    def create_clients_tab(self):
        # Clients tab
        clients_frame = ttk.Frame(self.notebook)
        self.notebook.add(clients_frame, text="Clients")

        # Client form
        client_form = ttk.LabelFrame(clients_frame, text="Client Information")
        client_form.pack(fill="x", padx=10, pady=10)

        form_frame = ttk.Frame(client_form)
        form_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, sticky="w", pady=2)
        self.client_name_entry = ttk.Entry(form_frame)
        self.client_name_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(form_frame, text="Company:").grid(row=1, column=0, sticky="w", pady=2)
        self.client_company_entry = ttk.Entry(form_frame)
        self.client_company_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(form_frame, text="Email:").grid(row=2, column=0, sticky="w", pady=2)
        self.client_email_entry = ttk.Entry(form_frame)
        self.client_email_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(form_frame, text="Phone:").grid(row=3, column=0, sticky="w", pady=2)
        self.client_phone_entry = ttk.Entry(form_frame)
        self.client_phone_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(form_frame, text="Address:").grid(row=4, column=0, sticky="nw", pady=2)
        self.client_address_text = tk.Text(form_frame, height=3)
        self.client_address_text.grid(row=4, column=1, sticky="ew", padx=5, pady=2)

        form_frame.columnconfigure(1, weight=1)

        # Client buttons
        button_frame = ttk.Frame(client_form)
        button_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(button_frame, text="Add Client", command=self.add_client).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Update Client", command=self.update_client).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_client_form).pack(side="left", padx=5)

        # Client list
        list_frame = ttk.LabelFrame(clients_frame, text="Clients")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.client_tree = ttk.Treeview(
            list_frame,
            columns=("ID", "Name", "Company", "Email", "Phone"),
            show="headings",
        )
        self.client_tree.heading("ID", text="ID")
        self.client_tree.heading("Name", text="Name")
        self.client_tree.heading("Company", text="Company")
        self.client_tree.heading("Email", text="Email")
        self.client_tree.heading("Phone", text="Phone")

        self.client_tree.column("ID", width=50)
        self.client_tree.column("Name", width=150)
        self.client_tree.column("Company", width=150)
        self.client_tree.column("Email", width=200)
        self.client_tree.column("Phone", width=100)

        self.client_tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.client_tree.bind("<<TreeviewSelect>>", self.on_client_select)

        # Client buttons
        client_button_frame = ttk.Frame(list_frame)
        client_button_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(client_button_frame, text="Delete Client", command=self.delete_client).pack(side="left", padx=5)

