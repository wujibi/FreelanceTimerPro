"""CustomTkinter Clients tab — CRUD parity with ui/tk/clients_* ."""

from __future__ import annotations

from collections.abc import Callable
from tkinter import messagebox, ttk

import tkinter as tk

import customtkinter as ctk

from models import Client


class CtkClientsTab:
    def __init__(
        self,
        parent,
        root,
        db,
        on_data_changed: Callable[[], None] | None = None,
    ) -> None:
        self.parent = parent
        self.root = root
        self.db = db
        self.on_data_changed = on_data_changed or (lambda: None)
        self.client_model = Client(self.db)

        self._build_ui()
        self.refresh_tree()

    def _build_ui(self) -> None:
        form = ctk.CTkFrame(self.parent, fg_color="transparent")
        form.pack(fill="x", padx=10, pady=8)

        ctk.CTkLabel(form, text="Client information", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 8)
        )

        ctk.CTkLabel(form, text="Name:").grid(row=1, column=0, sticky="w", pady=4)
        self.client_name_entry = ctk.CTkEntry(form, width=360)
        self.client_name_entry.grid(row=1, column=1, sticky="ew", padx=8, pady=4)

        ctk.CTkLabel(form, text="Company:").grid(row=2, column=0, sticky="w", pady=4)
        self.client_company_entry = ctk.CTkEntry(form, width=360)
        self.client_company_entry.grid(row=2, column=1, sticky="ew", padx=8, pady=4)

        ctk.CTkLabel(form, text="Email:").grid(row=3, column=0, sticky="w", pady=4)
        self.client_email_entry = ctk.CTkEntry(form, width=360)
        self.client_email_entry.grid(row=3, column=1, sticky="ew", padx=8, pady=4)

        ctk.CTkLabel(form, text="Phone:").grid(row=4, column=0, sticky="w", pady=4)
        self.client_phone_entry = ctk.CTkEntry(form, width=360)
        self.client_phone_entry.grid(row=4, column=1, sticky="ew", padx=8, pady=4)

        ctk.CTkLabel(form, text="Address:").grid(row=5, column=0, sticky="nw", pady=4)
        self.client_address_text = ctk.CTkTextbox(form, width=360, height=72)
        self.client_address_text.grid(row=5, column=1, sticky="ew", padx=8, pady=4)

        form.columnconfigure(1, weight=1)

        bf = ctk.CTkFrame(self.parent, fg_color="transparent")
        bf.pack(fill="x", padx=10, pady=4)
        ctk.CTkButton(bf, text="Add Client", command=self.add_client).pack(side="left", padx=4)
        ctk.CTkButton(bf, text="Update Client", command=self.update_client).pack(side="left", padx=4)
        ctk.CTkButton(bf, text="Clear Form", command=self.clear_client_form).pack(side="left", padx=4)

        ctk.CTkLabel(self.parent, text="Clients", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=10, pady=(12, 4)
        )

        self._tree_host = tk.Frame(self.parent)
        self._tree_host.pack(fill="both", expand=True, padx=8, pady=4)

        self.client_tree = ttk.Treeview(
            self._tree_host,
            columns=("ID", "Name", "Company", "Email", "Phone"),
            show="headings",
        )
        for col, w in (("ID", 48), ("Name", 140), ("Company", 130), ("Email", 180), ("Phone", 100)):
            self.client_tree.heading(col, text=col if col != "ID" else "ID")
            self.client_tree.column(col, width=w)

        ys = ttk.Scrollbar(self._tree_host, orient="vertical", command=self.client_tree.yview)
        self.client_tree.configure(yscrollcommand=ys.set)
        self.client_tree.pack(side="left", fill="both", expand=True)
        ys.pack(side="right", fill="y")

        self.client_tree.bind("<<TreeviewSelect>>", self.on_client_select)

        dbf = ctk.CTkFrame(self.parent, fg_color="transparent")
        dbf.pack(fill="x", padx=10, pady=8)
        ctk.CTkButton(dbf, text="Delete Client", command=self.delete_client, fg_color="gray40").pack(
            side="left", padx=4
        )

    def refresh_tree(self) -> None:
        for item in self.client_tree.get_children():
            self.client_tree.delete(item)
        for client in self.client_model.get_all():
            self.client_tree.insert(
                "",
                "end",
                values=(client[0], client[1], client[2] or "", client[3] or "", client[4] or ""),
            )

    def add_client(self) -> None:
        name = self.client_name_entry.get().strip()
        company = self.client_company_entry.get().strip()
        email = self.client_email_entry.get().strip()
        phone = self.client_phone_entry.get().strip()
        address = self.client_address_text.get("1.0", "end-1c").strip()

        if not name:
            messagebox.showerror("Error", "Client name is required")
            return

        for client in self.client_model.get_all():
            if client[1].lower() == name.lower():
                messagebox.showerror("Error", f"Client '{name}' already exists")
                return

        self.client_model.create(name, company, email, phone, address)
        self.clear_client_form()
        self.refresh_tree()
        self.on_data_changed()
        messagebox.showinfo("Success", "Client added successfully")

    def update_client(self) -> None:
        selection = self.client_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a client to update")
            return

        client_id = self.client_tree.item(selection[0])["values"][0]
        name = self.client_name_entry.get().strip()
        company = self.client_company_entry.get().strip()
        email = self.client_email_entry.get().strip()
        phone = self.client_phone_entry.get().strip()
        address = self.client_address_text.get("1.0", "end-1c").strip()

        if not name:
            messagebox.showerror("Error", "Client name is required")
            return

        self.client_model.update(client_id, name, company, email, phone, address)
        self.clear_client_form()
        self.refresh_tree()
        self.on_data_changed()
        messagebox.showinfo("Success", "Client updated successfully")

    def delete_client(self) -> None:
        selection = self.client_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a client to delete")
            return

        if messagebox.askyesno(
            "Confirm",
            "Delete this client? This will also delete all associated projects, tasks, and time entries.",
        ):
            client_id = self.client_tree.item(selection[0])["values"][0]
            self.client_model.delete(client_id)
            self.refresh_tree()
            self.on_data_changed()
            messagebox.showinfo("Success", "Client deleted successfully")

    def clear_client_form(self) -> None:
        self.client_name_entry.delete(0, tk.END)
        self.client_company_entry.delete(0, tk.END)
        self.client_email_entry.delete(0, tk.END)
        self.client_phone_entry.delete(0, tk.END)
        self.client_address_text.delete("1.0", "end")

    def on_client_select(self, _event=None) -> None:
        selection = self.client_tree.selection()
        if not selection:
            return
        client_id = self.client_tree.item(selection[0])["values"][0]
        client = self.client_model.get_by_id(client_id)
        if not client:
            return
        self.client_name_entry.delete(0, tk.END)
        self.client_name_entry.insert(0, client[1])
        self.client_company_entry.delete(0, tk.END)
        self.client_company_entry.insert(0, client[2] or "")
        self.client_email_entry.delete(0, tk.END)
        self.client_email_entry.insert(0, client[3] or "")
        self.client_phone_entry.delete(0, tk.END)
        self.client_phone_entry.insert(0, client[4] or "")
        self.client_address_text.delete("1.0", "end")
        self.client_address_text.insert("1.0", client[5] or "")
