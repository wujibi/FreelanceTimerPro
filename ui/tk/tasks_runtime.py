from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from core.project_resolution import resolve_project_id_by_names


class TasksRuntimeMixin:
    """Task CRUD and related UI runtime behavior."""

    def on_task_client_select(self, event):
        """When client is selected in tasks tab, populate projects."""
        client_name = self.task_client_combo.get()
        if client_name:
            clients = self.client_model.get_all()
            client_id = None
            for client in clients:
                if client[1] == client_name:
                    client_id = client[0]
                    break

            if client_id:
                projects = self.project_model.get_by_client(client_id)
                self.task_project_combo["values"] = [p[2] for p in projects]
                self.task_project_combo.set("")

    def add_task(self):
        name = self.task_name_entry.get().strip()
        description = self.task_desc_text.get("1.0", tk.END).strip()
        is_global = self.task_global_var.get()

        if not name:
            messagebox.showerror("Error", "Please enter a task name")
            return

        if is_global:
            rate = float(self.task_rate_entry.get() or 0)
            is_lump_sum_flag = self.task_billing_var.get() == "lump_sum"

            if is_lump_sum_flag:
                self.task_model.create(name, description, 0, True, rate, None, True)
            else:
                self.task_model.create(name, description, rate, False, 0, None, True)

            messagebox.showinfo("Success", f"Global task '{name}' created!")
        else:
            client_text = self.task_client_combo.get()
            project_text = self.task_project_combo.get()

            if not client_text or not project_text:
                messagebox.showerror("Error", "Please select a client and project for non-global tasks")
                return

            projects = self.project_model.get_all()
            project_id = resolve_project_id_by_names(projects, client_text, project_text)

            if not project_id:
                messagebox.showerror("Error", "Invalid project selected")
                return

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

        item = selection[0]
        item_tags = self.task_tree.item(item)["tags"]
        item_values = self.task_tree.item(item)["values"]

        if "task" not in item_tags:
            messagebox.showerror("Error", "Please select an actual task (not a client/project group)")
            return

        task_id = None
        for tag in item_tags:
            if tag.startswith("task_id_"):
                task_id = int(tag.replace("task_id_", ""))
                break

        if not task_id and len(item_values) > 1:
            try:
                task_id = int(item_values[1])
            except Exception:
                pass

        if not task_id:
            messagebox.showerror("Error", "Could not determine task ID")
            return

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

        item_tags = self.task_tree.item(selection[0])["tags"]
        if "task" not in item_tags:
            messagebox.showerror("Error", "Please select an actual task (not a client/project header)")
            return

        task_id = None
        for tag in item_tags:
            if tag.startswith("task_id_"):
                task_id = int(tag.replace("task_id_", ""))
                break

        if not task_id:
            messagebox.showerror("Error", "Could not determine task ID")
            return

        if messagebox.askyesno("Confirm", "Delete this task? This will also delete all associated time entries."):
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
        if not selection:
            return

        item = selection[0]
        item_tags = self.task_tree.item(item)["tags"]
        item_values = self.task_tree.item(item)["values"]

        if "task" not in item_tags:
            return

        task_id = None
        for tag in item_tags:
            if tag.startswith("task_id_"):
                task_id = int(tag.replace("task_id_", ""))
                break

        if not task_id and len(item_values) > 1:
            try:
                task_id = int(item_values[1])
            except Exception:
                pass

        if not task_id:
            return

        task = self.task_model.get_by_id(task_id)
        if not task:
            return

        is_global = task[1] is None
        if is_global:
            self.task_global_var.set(True)
            self.toggle_task_project_field()
        else:
            self.task_global_var.set(False)
            self.toggle_task_project_field()

            project = self.project_model.get_by_id(task[1])
            if project:
                client = self.client_model.get_by_id(project[1])
                if client:
                    self.task_client_combo.set(client[1])
                    projects = self.project_model.get_by_client(client[0])
                    self.task_project_combo["values"] = [p[2] for p in projects]
                    self.task_project_combo.set(project[2])

        self.task_name_entry.delete(0, tk.END)
        self.task_name_entry.insert(0, task[2])

        self.task_desc_text.delete("1.0", tk.END)
        self.task_desc_text.insert("1.0", task[3] or "")

        if task[5]:
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
        """Enable or disable project selection based on global checkbox."""
        is_global = self.task_global_var.get()
        if is_global:
            self.task_client_combo.set("")
            self.task_client_combo.config(state="disabled")
            self.task_project_combo.set("")
            self.task_project_combo.config(state="disabled")
        else:
            self.task_client_combo.config(state="readonly")
            self.task_project_combo.config(state="readonly")
