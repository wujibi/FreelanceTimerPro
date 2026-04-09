from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
import sqlite3


class ProjectsRuntimeMixin:
    """Project CRUD and form runtime behavior."""

    def add_project(self):
        client_text = self.project_client_combo.get()
        name = self.project_name_entry.get().strip()
        description = self.project_desc_text.get("1.0", tk.END).strip()

        if not client_text or not name:
            messagebox.showerror("Error", "Client and project name are required")
            return

        clients = self.client_model.get_all()
        client_id = None
        for client in clients:
            if client[1] == client_text:
                client_id = client[0]
                break

        if not client_id:
            messagebox.showerror("Error", "Invalid client selected")
            return

        existing_projects = self.project_model.get_by_client(client_id)
        for project in existing_projects:
            if project[2].lower() == name.lower():
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

        project_id = self.project_tree.item(selection[0])["values"][0]
        client_text = self.project_client_combo.get()
        name = self.project_name_entry.get().strip()
        description = self.project_desc_text.get("1.0", tk.END).strip()

        if not client_text or not name:
            messagebox.showerror("Error", "Client and project name are required")
            return

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

        if messagebox.askyesno(
            "Confirm",
            "Delete this project? This will also delete all associated tasks and time entries.",
        ):
            project_id = self.project_tree.item(selection[0])["values"][0]
            try:
                self.project_model.delete(project_id)
                self.refresh_projects()
                self.refresh_combos()
                messagebox.showinfo("Success", "Project deleted successfully")
            except sqlite3.IntegrityError as exc:
                messagebox.showerror(
                    "Delete Blocked",
                    "Could not delete this project due to linked billing/invoice records.\n\n"
                    f"Details: {exc}",
                )
            except Exception as exc:
                messagebox.showerror("Delete Failed", f"Unexpected error deleting project:\n\n{exc}")

    def clear_project_form(self):
        self.project_client_combo.set("")
        self.project_name_entry.delete(0, tk.END)
        self.project_desc_text.delete("1.0", tk.END)
        self.project_rate_entry.delete(0, tk.END)
        self.project_billing_var.set("hourly")

    def on_project_select(self, event):
        selection = self.project_tree.selection()
        if selection:
            project_id = self.project_tree.item(selection[0])["values"][0]
            project = self.project_model.get_by_id(project_id)
            if project:
                client = self.client_model.get_by_id(project[1])
                if client:
                    self.project_client_combo.set(client[1])

                self.project_name_entry.delete(0, tk.END)
                self.project_name_entry.insert(0, project[2])

                self.project_desc_text.delete("1.0", tk.END)
                self.project_desc_text.insert("1.0", project[3] or "")

                if project[5]:
                    self.project_billing_var.set("lump_sum")
                    self.project_rate_entry.delete(0, tk.END)
                    self.project_rate_entry.insert(0, str(project[6]))
                else:
                    self.project_billing_var.set("hourly")
                    self.project_rate_entry.delete(0, tk.END)
                    self.project_rate_entry.insert(0, str(project[4]))

    def toggle_project_billing(self):
        pass
