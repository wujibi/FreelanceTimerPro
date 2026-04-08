from __future__ import annotations

from datetime import datetime
from tkinter import messagebox

from core.client_resolution import resolve_client_id_by_name
from core.project_resolution import resolve_project_id_by_names
from core.task_list_builders import build_task_display_id_map_for_project, build_task_displays_for_project
from core.task_resolution import resolve_task_id_for_timer


class TimerRuntimeMixin:
    """Runtime timer behavior for the main app."""

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

        task_text = self.timer_task_combo.get()
        client_name = self.timer_client_combo.get()
        project_name = self.timer_project_combo.get()

        task_id_map = getattr(self, "_timer_task_id_map", {})
        self.current_task_id = task_id_map.get(task_text)
        resolution_error = None
        if not self.current_task_id:
            self.current_task_id, _, resolution_error = resolve_task_id_for_timer(
                task_text=task_text,
                client_name=client_name,
                project_name=project_name,
                all_tasks=self.task_model.get_all(),
                global_tasks=self.task_model.get_global_tasks(),
            )
        if resolution_error:
            messagebox.showerror("Error", resolution_error)
            return

        try:
            self.timer_running = True
            self.timer_start_time = datetime.now()

            project_id = self.get_current_timer_project_id()
            self.time_entry_model.start_timer(self.current_task_id, project_id_override=project_id)

            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            self.timer_label.config(text="00:00:00", foreground="green")

            self.update_timer_display()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start timer: {str(e)}")
            self.timer_running = False

    def stop_timer(self):
        if self.timer_running:
            elapsed_seconds = (datetime.now() - self.timer_start_time).total_seconds()

            client_id = self.get_current_timer_client_id()
            project_id = self.get_current_timer_project_id()

            self.timer_running = False
            self.time_entry_model.stop_timer()

            if client_id:
                if client_id not in self.daily_client_totals:
                    self.daily_client_totals[client_id] = 0
                self.daily_client_totals[client_id] += elapsed_seconds
                self.last_timer_client_id = client_id

                if project_id:
                    key = (client_id, project_id)
                    if key not in self.daily_project_totals:
                        self.daily_project_totals[key] = 0
                    self.daily_project_totals[key] += elapsed_seconds
                    self.last_timer_project_id = project_id

            self.last_timer_elapsed = elapsed_seconds

            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
            self.update_timer_display_final()
            self.update_daily_totals_display()

            self.refresh_time_entries()

            hours = int(elapsed_seconds // 3600)
            minutes = int((elapsed_seconds % 3600) // 60)
            seconds = int(elapsed_seconds % 60)
            messagebox.showinfo(
                "Success",
                f"Timer stopped and time entry saved\n\n"
                f"Time recorded: {hours:02d}:{minutes:02d}:{seconds:02d}",
            )

    def update_timer_display(self):
        if self.timer_running and self.timer_start_time:
            elapsed = datetime.now() - self.timer_start_time
            hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            self.timer_label.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}", foreground="green")
            self.root.after(1000, self.update_timer_display)

    def update_timer_display_final(self):
        """Display final elapsed time after stopping (don't reset to zero)."""
        if self.last_timer_elapsed > 0:
            hours = int(self.last_timer_elapsed // 3600)
            minutes = int((self.last_timer_elapsed % 3600) // 60)
            seconds = int(self.last_timer_elapsed % 60)

            self.timer_label.config(
                text=f"Last: {hours:02d}:{minutes:02d}:{seconds:02d}",
                foreground="gray",
            )
        else:
            self.timer_label.config(text="00:00:00", foreground="black")

    def on_timer_client_select(self, event):
        client_name = self.timer_client_combo.get()
        if client_name:
            self._populate_projects_for_client(
                client_name=client_name,
                project_combo=self.timer_project_combo,
                task_combo=self.timer_task_combo,
            )

    def on_timer_project_select(self, event):
        project_name = self.timer_project_combo.get()
        client_name = self.timer_client_combo.get()

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
                self._timer_task_id_map = build_task_display_id_map_for_project(
                    project_tasks=project_tasks,
                    global_tasks=global_tasks,
                    client_name=client_name,
                    project_name=project_name,
                )

                self.timer_task_combo["values"] = task_displays
                self.timer_task_combo.set("")
            else:
                self._timer_task_id_map = {}
                self.timer_task_combo["values"] = []
                self.timer_task_combo.set("")

    def get_current_timer_client_id(self):
        """Get the client ID for the currently selected timer task."""
        try:
            client_name = self.timer_client_combo.get()
            if not client_name:
                return None

            clients = self.client_model.get_all()
            return resolve_client_id_by_name(clients, client_name)
        except Exception:
            return None

    def get_current_timer_project_id(self):
        """Get the project ID for the currently selected timer project."""
        try:
            client_name = self.timer_client_combo.get()
            project_name = self.timer_project_combo.get()

            if not client_name or not project_name:
                return None

            projects = self.project_model.get_all()
            return resolve_project_id_by_names(projects, client_name, project_name)
        except Exception:
            return None

    def update_daily_totals_display(self):
        """Update daily totals display with per-client and per-project time."""
        current_date = datetime.now().date()
        if current_date != self.session_date:
            self.daily_client_totals = {}
            self.daily_project_totals = {}
            self.session_date = current_date

        self.daily_totals_text.config(state="normal")
        self.daily_totals_text.delete("1.0", "end")
        self.manual_daily_totals_text.config(state="normal")
        self.manual_daily_totals_text.delete("1.0", "end")

        if not self.daily_client_totals:
            text = (
                f"📊 Daily Time Tracker - {self.session_date.strftime('%B %d, %Y')}\n\n"
                "No time tracked yet today.\n\n"
                "Start a timer to begin tracking!"
            )
            self.daily_totals_text.insert("1.0", text)
            self.manual_daily_totals_text.insert("1.0", text)
        else:
            text = f"📊 Daily Time Tracker - {self.session_date.strftime('%B %d, %Y')}\n"
            text += "=" * 50 + "\n\n"

            grand_total_seconds = sum(self.daily_client_totals.values())
            grand_total_hours = grand_total_seconds / 3600

            clients = self.client_model.get_all()
            client_dict = {c[0]: c[1] for c in clients}

            projects = self.project_model.get_all()
            project_dict = {p[0]: p[2] for p in projects}

            client_projects = {}
            for (client_id, project_id), seconds in self.daily_project_totals.items():
                if client_id not in client_projects:
                    client_projects[client_id] = []
                client_projects[client_id].append((project_id, seconds))

            for client_id, total_seconds in sorted(
                self.daily_client_totals.items(),
                key=lambda x: x[1],
                reverse=True,
            ):
                client_name = client_dict.get(client_id, f"Client #{client_id}")
                hours = total_seconds / 3600

                h = int(total_seconds // 3600)
                m = int((total_seconds % 3600) // 60)
                s = int(total_seconds % 60)

                text += f"📌 {client_name}:  {h:02d}:{m:02d}:{s:02d}  ({hours:.2f} hrs)\n"

                if client_id in client_projects:
                    sorted_projects = sorted(
                        client_projects[client_id],
                        key=lambda x: x[1],
                        reverse=True,
                    )

                    for project_id, proj_seconds in sorted_projects:
                        project_name = project_dict.get(project_id, f"Project #{project_id}")
                        proj_hours = proj_seconds / 3600

                        ph = int(proj_seconds // 3600)
                        pm = int((proj_seconds % 3600) // 60)
                        ps = int(proj_seconds % 60)

                        text += (
                            f"    └─ {project_name}:  {ph:02d}:{pm:02d}:{ps:02d}  ({proj_hours:.2f} hrs)\n"
                        )

                text += "\n"

            text += "=" * 50 + "\n"
            h = int(grand_total_seconds // 3600)
            m = int((grand_total_seconds % 3600) // 60)
            s = int(grand_total_seconds % 60)
            text += f"  TOTAL TODAY:  {h:02d}:{m:02d}:{s:02d}  ({grand_total_hours:.2f} hrs)"

            self.daily_totals_text.insert("1.0", text)
            self.manual_daily_totals_text.insert("1.0", text)

        self.daily_totals_text.config(state="disabled")
        self.manual_daily_totals_text.config(state="disabled")

    def reset_daily_totals(self):
        """Manually reset daily totals."""
        if not self.daily_client_totals:
            messagebox.showinfo("Nothing to Reset", "No daily totals to reset.")
            return

        response = messagebox.askyesno(
            "Reset Daily Totals",
            "Are you sure you want to reset today's accumulated time?\n\n"
            "This will only reset the daily display tracker.\n"
            "Saved time entries will not be affected.",
        )

        if response:
            self.daily_client_totals = {}
            self.daily_project_totals = {}
            self.last_timer_elapsed = 0
            self.update_daily_totals_display()
            self.timer_label.config(text="00:00:00", foreground="black")
            messagebox.showinfo("Reset Complete", "Daily totals have been reset.")
