from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
import sqlite3


class ClientsRuntimeMixin:
    """Client CRUD and form runtime behavior."""

    def add_client(self):
        name = self.client_name_entry.get().strip()
        company = self.client_company_entry.get().strip()
        email = self.client_email_entry.get().strip()
        phone = self.client_phone_entry.get().strip()
        address = self.client_address_text.get("1.0", tk.END).strip()

        if not name:
            messagebox.showerror("Error", "Client name is required")
            return

        existing_clients = self.client_model.get_all()
        for client in existing_clients:
            if client[1].lower() == name.lower():
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

        client_id = self.client_tree.item(selection[0])["values"][0]
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

        client_id = self.client_tree.item(selection[0])["values"][0]
        impact = self.client_model.get_delete_impact_counts(client_id)
        confirm_msg = (
            "Delete this client?\n\n"
            f"This will delete {impact['projects']} project{'s' if impact['projects'] != 1 else ''}, "
            f"{impact['tasks']} task{'s' if impact['tasks'] != 1 else ''}, and "
            f"{impact['time_entries']} time entr{'y' if impact['time_entries'] == 1 else 'ies'}."
        )
        if impact["invoices"] > 0:
            confirm_msg += (
                f"\nIt will also remove {impact['invoices']} invoice histor"
                f"{'y' if impact['invoices'] == 1 else 'ies'} for this client."
            )

        if messagebox.askyesno("Confirm", confirm_msg):
            try:
                self.client_model.delete(client_id)
                self.clear_client_form()
                self.refresh_clients()
                self.refresh_combos()
                messagebox.showinfo("Success", "Client deleted successfully")
            except sqlite3.IntegrityError as exc:
                messagebox.showerror(
                    "Delete Blocked",
                    "Could not delete this client due to remaining linked records.\n\n"
                    f"Details: {exc}",
                )
            except Exception as exc:
                messagebox.showerror("Delete Failed", f"Unexpected error deleting client:\n\n{exc}")

    def clear_client_form(self):
        self.client_name_entry.delete(0, tk.END)
        self.client_company_entry.delete(0, tk.END)
        self.client_email_entry.delete(0, tk.END)
        self.client_phone_entry.delete(0, tk.END)
        self.client_address_text.delete("1.0", tk.END)

    def on_client_select(self, event):
        selection = self.client_tree.selection()
        if selection:
            client_id = self.client_tree.item(selection[0])["values"][0]
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
            else:
                self.clear_client_form()
