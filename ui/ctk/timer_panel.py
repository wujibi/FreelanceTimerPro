"""CustomTkinter Timer tab: active timer, manual entry, and daily totals (Tk parity)."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from datetime import datetime, timedelta
from tkinter import messagebox
from typing import Any

import customtkinter as ctk

from core.client_resolution import resolve_client_id_by_name
from core.project_resolution import resolve_project_id_by_names
from core.task_list_builders import build_task_displays_for_project
from core.task_resolution import GLOBAL_TASK_PREFIX, resolve_task_id_for_timer
from models import Client, Project, Task, TimeEntry


class CtkTimerTab:
    """Timer + manual entry UI backed by the same models and rules as the Tk app."""

    def __init__(
        self,
        parent: Any,
        root: ctk.CTk,
        db,
        refresh_time_entries: Callable[[], None] | None = None,
    ) -> None:
        self.parent = parent
        self.root = root
        self.db = db
        self.refresh_time_entries = refresh_time_entries or (lambda: None)

        self.client_model = Client(self.db)
        self.project_model = Project(self.db)
        self.task_model = Task(self.db)
        self.time_entry_model = TimeEntry(self.db)

        self.timer_running = False
        self.timer_start_time = None
        self.current_task_id = None
        self.session_date = datetime.now().date()
        self.daily_client_totals = {}
        self.daily_project_totals = {}
        self.last_timer_elapsed = 0
        self.last_timer_client_id = None
        self.last_timer_project_id = None

        self._large_font = ctk.CTkFont(size=32, weight="bold")

        self._build_shell()
        self._load_client_combos()

    def _build_shell(self) -> None:
        self._no_clients_hint = ctk.CTkLabel(
            self.parent,
            text="",
            wraplength=880,
            justify="left",
            text_color=("brown", "#ffb366"),
            font=ctk.CTkFont(size=12),
        )

        top = ctk.CTkFrame(self.parent, fg_color="transparent")
        top.pack(fill="x", padx=8, pady=(4, 8))

        ctk.CTkLabel(top, text="View:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(0, 8))
        self._segment = ctk.CTkSegmentedButton(
            top,
            values=["Active Timer", "Manual Entry"],
            command=self._on_segment,
        )
        self._segment.pack(side="left")
        self._segment.set("Active Timer")

        self._no_clients_hint.pack(fill="x", padx=8, pady=(0, 4))

        self._view_host = ctk.CTkFrame(self.parent, fg_color="transparent")
        self._view_host.pack(fill="both", expand=True)

        self._build_active_view()
        self._build_manual_view()
        self._show_view("active")

    def _on_segment(self, value: str) -> None:
        if value == "Active Timer":
            self._show_view("active")
        else:
            self._show_view("manual")

    def _show_view(self, which: str) -> None:
        self._active_outer.pack_forget()
        self._manual_outer.pack_forget()
        if which == "active":
            self._active_outer.pack(fill="both", expand=True)
        else:
            self._manual_outer.pack(fill="both", expand=True)

    def _build_active_view(self) -> None:
        self._active_outer = ctk.CTkFrame(self._view_host, fg_color="transparent")

        disp = ctk.CTkFrame(self._active_outer)
        disp.pack(fill="x", padx=4, pady=8)

        ctk.CTkLabel(disp, text="Active Timer", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=10, pady=(8, 0)
        )
        self.timer_label = ctk.CTkLabel(disp, text="00:00:00", font=self._large_font)
        self.timer_label.pack(pady=8)

        grid = ctk.CTkFrame(disp, fg_color="transparent")
        grid.pack(fill="x", padx=10, pady=4)

        ctk.CTkLabel(grid, text="Client:").grid(row=0, column=0, sticky="w", pady=4)
        self.timer_client_combo = ctk.CTkComboBox(
            grid,
            values=[],
            state="readonly",
            width=360,
            command=self._on_timer_client_selected,
        )
        self.timer_client_combo.grid(row=0, column=1, sticky="ew", padx=8, pady=4)

        ctk.CTkLabel(grid, text="Project:").grid(row=1, column=0, sticky="w", pady=4)
        self.timer_project_combo = ctk.CTkComboBox(
            grid,
            values=[],
            state="readonly",
            width=360,
            command=self._on_timer_project_selected,
        )
        self.timer_project_combo.grid(row=1, column=1, sticky="ew", padx=8, pady=4)

        ctk.CTkLabel(grid, text="Task:").grid(row=2, column=0, sticky="w", pady=4)
        self.timer_task_combo = ctk.CTkComboBox(grid, values=[], state="readonly", width=360)
        self.timer_task_combo.grid(row=2, column=1, sticky="ew", padx=8, pady=4)
        grid.columnconfigure(1, weight=1)

        btns = ctk.CTkFrame(disp, fg_color="transparent")
        btns.pack(pady=10)
        self.start_button = ctk.CTkButton(btns, text="Start Timer", command=self.start_timer)
        self.start_button.pack(side="left", padx=6)
        self.stop_button = ctk.CTkButton(btns, text="Stop Timer", command=self.stop_timer, state="disabled")
        self.stop_button.pack(side="left", padx=6)

        daily = ctk.CTkFrame(self._active_outer)
        daily.pack(fill="both", expand=True, padx=4, pady=8)
        ctk.CTkLabel(daily, text="Today's Time by Client", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=10, pady=(8, 4)
        )
        self.daily_totals_text = ctk.CTkTextbox(daily, height=180, font=ctk.CTkFont(family="Consolas", size=14))
        self.daily_totals_text.pack(fill="both", expand=True, padx=10, pady=4)
        self.daily_totals_text.configure(state="disabled")

        dbtns = ctk.CTkFrame(daily, fg_color="transparent")
        dbtns.pack(fill="x", padx=10, pady=(0, 8))
        ctk.CTkButton(dbtns, text="Refresh Totals", command=self.update_daily_totals_display).pack(
            side="left", padx=4
        )
        ctk.CTkButton(dbtns, text="Reset Daily Totals", command=self.reset_daily_totals).pack(side="left", padx=4)

    def _build_manual_view(self) -> None:
        self._manual_outer = ctk.CTkFrame(self._view_host, fg_color="transparent")

        manual = ctk.CTkFrame(self._manual_outer)
        manual.pack(fill="both", expand=True, padx=4, pady=8)

        ctk.CTkLabel(manual, text="Manual Time Entry", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=10, pady=(8, 4)
        )

        form = ctk.CTkScrollableFrame(manual, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=6, pady=4)

        ctk.CTkLabel(form, text="Date (MM/DD/YY):").grid(row=0, column=0, sticky="w", pady=4)
        self.manual_date_entry = ctk.CTkEntry(form, width=200)
        self.manual_date_entry.grid(row=0, column=1, sticky="w", padx=8, pady=4)
        self.manual_date_entry.insert(0, datetime.now().strftime("%m/%d/%y"))

        ctk.CTkLabel(form, text="Entry Mode:").grid(row=1, column=0, sticky="w", pady=4)
        mode_row = ctk.CTkFrame(form, fg_color="transparent")
        mode_row.grid(row=1, column=1, sticky="w", padx=8, pady=4)
        self.manual_entry_mode = tk.StringVar(value="time_range")
        ctk.CTkRadioButton(
            mode_row,
            text="Start/End Time",
            variable=self.manual_entry_mode,
            value="time_range",
            command=self.toggle_manual_entry_mode,
        ).pack(side="left", padx=(0, 12))
        ctk.CTkRadioButton(
            mode_row,
            text="Decimal Hours",
            variable=self.manual_entry_mode,
            value="decimal",
            command=self.toggle_manual_entry_mode,
        ).pack(side="left")

        self._manual_time_frame = ctk.CTkFrame(form, fg_color="transparent")
        self._manual_time_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=4)
        ctk.CTkLabel(self._manual_time_frame, text="Start Time (HH:MM AM/PM):").grid(row=0, column=0, sticky="w", pady=2)
        self.manual_start_entry = ctk.CTkEntry(self._manual_time_frame, width=200)
        self.manual_start_entry.grid(row=0, column=1, sticky="w", padx=8, pady=2)
        self.manual_start_entry.insert(0, "09:00 AM")
        ctk.CTkLabel(self._manual_time_frame, text="End Time (HH:MM AM/PM):").grid(row=1, column=0, sticky="w", pady=2)
        self.manual_end_entry = ctk.CTkEntry(self._manual_time_frame, width=200)
        self.manual_end_entry.grid(row=1, column=1, sticky="w", padx=8, pady=2)
        self.manual_end_entry.insert(0, "05:00 PM")

        self._manual_decimal_frame = ctk.CTkFrame(form, fg_color="transparent")
        self._manual_decimal_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=4)
        ctk.CTkLabel(self._manual_decimal_frame, text="Hours (decimal):").grid(row=0, column=0, sticky="w", pady=2)
        self.manual_decimal_entry = ctk.CTkEntry(self._manual_decimal_frame, width=200)
        self.manual_decimal_entry.grid(row=0, column=1, sticky="w", padx=8, pady=2)
        self.manual_decimal_help = ctk.CTkLabel(
            self._manual_decimal_frame,
            text="Examples: 1.5, 0.75, 2.25",
            text_color="gray",
            font=ctk.CTkFont(size=11),
        )
        self.manual_decimal_help.grid(row=1, column=1, sticky="w", padx=8)
        self._manual_decimal_frame.grid_remove()

        ctk.CTkLabel(form, text="Client:").grid(row=4, column=0, sticky="w", pady=4)
        self.manual_client_combo = ctk.CTkComboBox(
            form,
            values=[],
            state="readonly",
            width=320,
            command=self._on_manual_client_selected,
        )
        self.manual_client_combo.grid(row=4, column=1, sticky="w", padx=8, pady=4)

        ctk.CTkLabel(form, text="Project:").grid(row=5, column=0, sticky="w", pady=4)
        self.manual_project_combo = ctk.CTkComboBox(
            form,
            values=[],
            state="readonly",
            width=320,
            command=self._on_manual_project_selected,
        )
        self.manual_project_combo.grid(row=5, column=1, sticky="w", padx=8, pady=4)

        ctk.CTkLabel(form, text="Task:").grid(row=6, column=0, sticky="w", pady=4)
        self.manual_task_combo = ctk.CTkComboBox(form, values=[], state="readonly", width=320)
        self.manual_task_combo.grid(row=6, column=1, sticky="w", padx=8, pady=4)

        ctk.CTkLabel(form, text="Description:").grid(row=7, column=0, sticky="nw", pady=4)
        self.manual_desc_text = ctk.CTkTextbox(form, height=72, width=320)
        self.manual_desc_text.grid(row=7, column=1, sticky="ew", padx=8, pady=4)

        form.columnconfigure(1, weight=1)

        mbtns = ctk.CTkFrame(manual, fg_color="transparent")
        mbtns.pack(fill="x", padx=10, pady=8)
        ctk.CTkButton(mbtns, text="Add Entry", command=self.add_manual_entry).pack(side="left", padx=4)
        ctk.CTkButton(mbtns, text="Clear", command=self.clear_manual_entry_form).pack(side="left", padx=4)

        mdaily = ctk.CTkFrame(self._manual_outer)
        mdaily.pack(fill="both", expand=True, padx=4, pady=8)
        ctk.CTkLabel(mdaily, text="Today's Time by Client", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=10, pady=(8, 4)
        )
        self.manual_daily_totals_text = ctk.CTkTextbox(mdaily, height=140, font=ctk.CTkFont(family="Consolas", size=14))
        self.manual_daily_totals_text.pack(fill="both", expand=True, padx=10, pady=4)
        self.manual_daily_totals_text.configure(state="disabled")

        mdbtns = ctk.CTkFrame(mdaily, fg_color="transparent")
        mdbtns.pack(fill="x", padx=10, pady=(0, 8))
        ctk.CTkButton(mdbtns, text="Refresh Totals", command=self.update_daily_totals_display).pack(
            side="left", padx=4
        )
        ctk.CTkButton(mdbtns, text="Reset Daily Totals", command=self.reset_daily_totals).pack(side="left", padx=4)

    def _load_client_combos(self) -> None:
        names = [c[1] for c in self.client_model.get_all()]
        self.timer_client_combo.configure(values=names)
        self.timer_client_combo.set("")
        self.manual_project_combo.configure(values=[])
        self.timer_project_combo.configure(values=[])
        self.manual_task_combo.configure(values=[])
        self.timer_task_combo.configure(values=[])
        self.manual_client_combo.configure(values=names)
        self.manual_client_combo.set("")
        self.manual_project_combo.set("")
        self.manual_task_combo.set("")

        if not names:
            self._no_clients_hint.configure(
                text=(
                    "No clients in this database — dropdowns stay empty. "
                    "Add Clients (then Projects and Tasks) in the classic Tk app: "
                    "run with --tk or FREELANCETIMERPRO_UI=tk, then come back here."
                )
            )
        else:
            self._no_clients_hint.configure(text="")

        self.update_daily_totals_display()

    def _populate_projects_for_client(self, client_name: str, project_combo: ctk.CTkComboBox, task_combo) -> None:
        clients = self.client_model.get_all()
        client_id = resolve_client_id_by_name(clients, client_name)
        if not client_id:
            project_combo.configure(values=[])
            project_combo.set("")
            task_combo.set("")
            return
        projects = self.project_model.get_by_client(client_id)
        project_combo.configure(values=[p[2] for p in projects])
        project_combo.set("")
        task_combo.set("")

    def _on_timer_client_selected(self, _choice: str | None = None) -> None:
        client_name = self.timer_client_combo.get()
        if client_name:
            self._populate_projects_for_client(
                client_name,
                self.timer_project_combo,
                self.timer_task_combo,
            )

    def _on_timer_project_selected(self, _choice: str | None = None) -> None:
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
                self.timer_task_combo.configure(values=task_displays)
                self.timer_task_combo.set("")
            else:
                self.timer_task_combo.configure(values=[])
                self.timer_task_combo.set("")

    def _on_manual_client_selected(self, _choice: str | None = None) -> None:
        client_name = self.manual_client_combo.get()
        if client_name:
            self._populate_projects_for_client(
                client_name,
                self.manual_project_combo,
                self.manual_task_combo,
            )

    def _on_manual_project_selected(self, _choice: str | None = None) -> None:
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
                self.manual_task_combo.configure(values=task_displays)
                self.manual_task_combo.set("")
            else:
                self.manual_task_combo.configure(values=[])
                self.manual_task_combo.set("")

    def toggle_manual_entry_mode(self) -> None:
        mode = self.manual_entry_mode.get()
        if mode == "time_range":
            self._manual_time_frame.grid()
            self._manual_decimal_frame.grid_remove()
        else:
            self._manual_time_frame.grid_remove()
            self._manual_decimal_frame.grid()

    def start_timer(self) -> None:
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

            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            self.timer_label.configure(text="00:00:00", text_color=("green", "#2fa572"))

            self.update_timer_display()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start timer: {str(e)}")
            self.timer_running = False

    def stop_timer(self) -> None:
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

            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
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

    def update_timer_display(self) -> None:
        if self.timer_running and self.timer_start_time:
            elapsed = datetime.now() - self.timer_start_time
            hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            self.timer_label.configure(
                text=f"{hours:02d}:{minutes:02d}:{seconds:02d}",
                text_color=("green", "#2fa572"),
            )
            self.root.after(1000, self.update_timer_display)

    def update_timer_display_final(self) -> None:
        if self.last_timer_elapsed > 0:
            hours = int(self.last_timer_elapsed // 3600)
            minutes = int((self.last_timer_elapsed % 3600) // 60)
            seconds = int(self.last_timer_elapsed % 60)
            self.timer_label.configure(
                text=f"Last: {hours:02d}:{minutes:02d}:{seconds:02d}",
                text_color=("gray50", "gray60"),
            )
        else:
            self.timer_label.configure(text="00:00:00", text_color=("gray10", "gray90"))

    def get_current_timer_client_id(self):
        try:
            client_name = self.timer_client_combo.get()
            if not client_name:
                return None
            clients = self.client_model.get_all()
            return resolve_client_id_by_name(clients, client_name)
        except Exception:
            return None

    def get_current_timer_project_id(self):
        try:
            client_name = self.timer_client_combo.get()
            project_name = self.timer_project_combo.get()
            if not client_name or not project_name:
                return None
            projects = self.project_model.get_all()
            return resolve_project_id_by_names(projects, client_name, project_name)
        except Exception:
            return None

    def _set_textbox_text(self, widget: ctk.CTkTextbox, text: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        widget.configure(state="disabled")

    def update_daily_totals_display(self) -> None:
        current_date = datetime.now().date()
        if current_date != self.session_date:
            self.daily_client_totals = {}
            self.daily_project_totals = {}
            self.session_date = current_date

        if not self.daily_client_totals:
            text = (
                f"📊 Daily Time Tracker - {self.session_date.strftime('%B %d, %Y')}\n\n"
                "No time tracked yet today.\n\n"
                "Start a timer to begin tracking!"
            )
            self._set_textbox_text(self.daily_totals_text, text)
            self._set_textbox_text(self.manual_daily_totals_text, text)
            return

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

        for client_id, total_seconds in sorted(self.daily_client_totals.items(), key=lambda x: x[1], reverse=True):
            client_name = client_dict.get(client_id, f"Client #{client_id}")
            hours = total_seconds / 3600
            h = int(total_seconds // 3600)
            m = int((total_seconds % 3600) // 60)
            s = int(total_seconds % 60)
            text += f"📌 {client_name}:  {h:02d}:{m:02d}:{s:02d}  ({hours:.2f} hrs)\n"

            if client_id in client_projects:
                sorted_projects = sorted(client_projects[client_id], key=lambda x: x[1], reverse=True)
                for project_id, proj_seconds in sorted_projects:
                    project_name = project_dict.get(project_id, f"Project #{project_id}")
                    proj_hours = proj_seconds / 3600
                    ph = int(proj_seconds // 3600)
                    pm = int((proj_seconds % 3600) // 60)
                    ps = int(proj_seconds % 60)
                    text += f"    └─ {project_name}:  {ph:02d}:{pm:02d}:{ps:02d}  ({proj_hours:.2f} hrs)\n"
            text += "\n"

        text += "=" * 50 + "\n"
        h = int(grand_total_seconds // 3600)
        m = int((grand_total_seconds % 3600) // 60)
        s = int(grand_total_seconds % 60)
        text += f"  TOTAL TODAY:  {h:02d}:{m:02d}:{s:02d}  ({grand_total_hours:.2f} hrs)"

        self._set_textbox_text(self.daily_totals_text, text)
        self._set_textbox_text(self.manual_daily_totals_text, text)

    def reset_daily_totals(self) -> None:
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
            self.timer_label.configure(text="00:00:00", text_color=("gray10", "gray90"))
            messagebox.showinfo("Reset Complete", "Daily totals have been reset.")

    def get_manual_entry_project_id(self):
        try:
            client_name = self.manual_client_combo.get()
            project_name = self.manual_project_combo.get()
            if not client_name or not project_name:
                return None
            projects = self.project_model.get_all()
            return resolve_project_id_by_names(projects, client_name, project_name)
        except Exception:
            return None

    def _update_daily_totals_from_manual_entry(self, duration_seconds: float) -> None:
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

    def add_manual_entry(self) -> None:
        task_text = self.manual_task_combo.get()
        date_str = self.manual_date_entry.get().strip()
        description = self.manual_desc_text.get("1.0", "end-1c").strip()
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

    def clear_manual_entry_form(self) -> None:
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
        self.manual_desc_text.delete("1.0", "end")

    def reload_clients_if_needed(self) -> None:
        """Call after clients/projects change elsewhere (e.g. future CTk tabs)."""
        self._load_client_combos()
