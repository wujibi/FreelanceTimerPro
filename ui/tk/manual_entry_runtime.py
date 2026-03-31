from __future__ import annotations

from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox

from core.client_resolution import resolve_client_id_by_name
from core.project_resolution import resolve_project_id_by_names
from core.task_list_builders import build_task_displays_for_project
from core.task_resolution import GLOBAL_TASK_PREFIX, resolve_task_id_for_timer


class ManualEntryRuntimeMixin:
    """Manual time-entry behavior for the main app."""

    def toggle_manual_entry_mode(self):
        """Toggle between time range and decimal hour entry modes."""
        mode = self.manual_entry_mode.get()

        if mode == "time_range":
            self.manual_start_entry.grid()
            self.manual_end_entry.grid()

            self.manual_decimal_label.grid_remove()
            self.manual_decimal_entry.grid_remove()
            self.manual_decimal_help.grid_remove()
        else:
            self.manual_start_entry.grid_remove()
            self.manual_end_entry.grid_remove()

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
            date_obj = datetime.strptime(date_str, "%m/%d/%y")

            if mode == "time_range":
                start_str = self.manual_start_entry.get().strip()
                end_str = self.manual_end_entry.get().strip()

                start_time_obj = datetime.strptime(f"{date_str} {start_str}", "%m/%d/%y %I:%M %p")
                end_time_obj = datetime.strptime(f"{date_str} {end_str}", "%m/%d/%y %I:%M %p")

                if end_time_obj <= start_time_obj:
                    messagebox.showerror("Error", "End time must be after start time")
                    return

            else:
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
                    messagebox.showerror(
                        "Error",
                        f"Invalid decimal format: '{decimal_str}'\n\nExamples: 1.5, 0.75, 2.25",
                    )
                    return

                start_time_obj = datetime.strptime(f"{date_str} 09:00 AM", "%m/%d/%y %I:%M %p")
                duration = timedelta(hours=decimal_hours)
                end_time_obj = start_time_obj + duration

        except ValueError as e:
            messagebox.showerror(
                "Error",
                (
                    "Invalid date/time format.\n"
                    "Use MM/DD/YY for date and HH:MM AM/PM for time.\n"
                    f"Error: {str(e)}"
                ),
            )
            return

        task_id, _, resolution_error = resolve_task_id_for_timer(
            task_text=task_text,
            client_name=self.manual_client_combo.get(),
            project_name=self.manual_project_combo.get(),
            all_tasks=self.task_model.get_all(),
            global_tasks=self.task_model.get_global_tasks(),
        )
        if resolution_error:
            messagebox.showerror("Error", "Invalid task selected")
            return

        project_id_override = None
        if task_text.startswith(GLOBAL_TASK_PREFIX):
            project_id_override = self.get_manual_entry_project_id()

        self.time_entry_model.add_manual_entry(
            task_id,
            start_time_obj,
            end_time_obj,
            description,
            project_id_override=project_id_override,
        )
        self.refresh_time_entries()

        duration = end_time_obj - start_time_obj
        hours = duration.total_seconds() / 3600
        duration_seconds = duration.total_seconds()

        entry_date = start_time_obj.date()
        today = datetime.now().date()
        if entry_date == today:
            self._update_daily_totals_from_manual_entry(duration_seconds)

        if mode == "decimal":
            messagebox.showinfo(
                "Success",
                (
                    "Time entry added successfully\n\n"
                    f"Duration: {decimal_hours} hours\n"
                    f"Date: {date_obj.strftime('%m/%d/%y')}"
                ),
            )
        else:
            messagebox.showinfo(
                "Success",
                (
                    "Time entry added successfully\n\n"
                    f"Duration: {hours:.2f} hours\n"
                    f"From: {start_time_obj.strftime('%I:%M %p')} "
                    f"to {end_time_obj.strftime('%I:%M %p')}"
                ),
            )

        self.clear_manual_entry_form()

    def on_manual_client_select(self, event):
        """When client is selected in manual entry, populate projects."""
        client_name = self.manual_client_combo.get()
        if client_name:
            self._populate_projects_for_client(
                client_name=client_name,
                project_combo=self.manual_project_combo,
                task_combo=self.manual_task_combo,
            )

    def _populate_projects_for_client(self, client_name, project_combo, task_combo=None):
        """Load projects for a selected client and reset dependent controls."""
        clients = self.client_model.get_all()
        client_id = resolve_client_id_by_name(clients, client_name)
        if not client_id:
            project_combo["values"] = []
            project_combo.set("")
            if task_combo is not None:
                task_combo.set("")
            return

        projects = self.project_model.get_by_client(client_id)
        project_combo["values"] = [p[2] for p in projects]
        project_combo.set("")
        if task_combo is not None:
            task_combo.set("")

    def _update_daily_totals_from_manual_entry(self, duration_seconds):
        """Update session daily totals using manual-entry form selections."""
        client_id = None
        project_id = None

        client_name = self.manual_client_combo.get()
        if client_name:
            clients = self.client_model.get_all()
            client_id = resolve_client_id_by_name(clients, client_name)

        project_name = self.manual_project_combo.get()
        if project_name and client_id:
            projects = self.project_model.get_by_client(client_id)
            for project in projects:
                if project[2] == project_name:
                    project_id = project[0]
                    break

        if client_id and project_id:
            if client_id not in self.daily_client_totals:
                self.daily_client_totals[client_id] = 0
            self.daily_client_totals[client_id] += duration_seconds

            key = (client_id, project_id)
            if key not in self.daily_project_totals:
                self.daily_project_totals[key] = 0
            self.daily_project_totals[key] += duration_seconds

        self.update_daily_totals_display()

    def on_manual_project_select(self, event):
        """When project is selected in manual entry, populate tasks."""
        project_name = self.manual_project_combo.get()
        client_name = self.manual_client_combo.get()

        if project_name and client_name:
            projects = self.project_model.get_all()
            project_id = resolve_project_id_by_names(projects, client_name, project_name)

            if project_id:
                project_tasks = self.task_model.get_by_project(project_id)
                global_tasks = self.task_model.get_global_tasks()
                task_displays = build_task_displays_for_project(
                    project_tasks=project_tasks,
                    global_tasks=global_tasks,
                    client_name=client_name,
                    project_name=project_name,
                )

                self.manual_task_combo["values"] = task_displays
                self.manual_task_combo.set("")

    def get_manual_entry_project_id(self):
        """Get the project ID from manual entry form."""
        try:
            client_name = self.manual_client_combo.get()
            project_name = self.manual_project_combo.get()

            if not client_name or not project_name:
                return None

            projects = self.project_model.get_all()
            return resolve_project_id_by_names(projects, client_name, project_name)
        except Exception:
            return None

    def clear_manual_entry_form(self):
        self.manual_date_entry.delete(0, tk.END)
        self.manual_date_entry.insert(0, datetime.now().strftime("%m/%d/%y"))
        self.manual_start_entry.delete(0, tk.END)
        self.manual_start_entry.insert(0, "09:00 AM")
        self.manual_client_combo.set("")
        self.manual_project_combo.set("")
        self.manual_end_entry.delete(0, tk.END)
        self.manual_end_entry.insert(0, "05:00 PM")
        self.manual_decimal_entry.delete(0, tk.END)
        self.manual_task_combo.set("")
        self.manual_desc_text.delete("1.0", tk.END)
