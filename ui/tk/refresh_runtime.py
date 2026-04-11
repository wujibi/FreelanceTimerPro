from __future__ import annotations

import sqlite3
from datetime import datetime
from tkinter import messagebox

from core.task_resolution import format_task_display


class RefreshRuntimeMixin:
    """Centralized refresh/update methods for list/tree widgets."""

    def refresh_clients(self):
        for item in self.client_tree.get_children():
            self.client_tree.delete(item)

        clients = self.client_model.get_all()
        for client in clients:
            self.client_tree.insert(
                "",
                "end",
                values=(
                    client[0],
                    client[1],
                    client[2] or "",
                    client[3] or "",
                    client[4] or "",
                ),
            )

    def refresh_projects(self):
        for item in self.project_tree.get_children():
            self.project_tree.delete(item)

        projects = self.project_model.get_all()
        for project in projects:
            billing_type = "Lump Sum" if project[5] else "Hourly"
            rate = f"${project[6]:.2f}" if project[5] else f"${project[4]:.2f}/hr"
            client_name = project[9] if len(project) > 9 else "Unknown Client"

            self.project_tree.insert(
                "",
                "end",
                values=(
                    project[0],
                    client_name,
                    project[2],
                    billing_type,
                    rate,
                ),
            )

    def refresh_tasks(self):
        expanded_items = self.save_tree_state(self.task_tree)

        for item in self.task_tree.get_children():
            self.task_tree.delete(item)

        tasks = self.task_model.get_all()
        global_tasks = self.task_model.get_global_tasks()
        hierarchy = {}

        for task in tasks:
            client_name = task[9] if len(task) > 9 and task[9] else "Unknown Client"
            project_name = task[8] if len(task) > 8 and task[8] else "Unknown Project"
            if client_name not in hierarchy:
                hierarchy[client_name] = {}
            if project_name not in hierarchy[client_name]:
                hierarchy[client_name][project_name] = []
            hierarchy[client_name][project_name].append(task)

        for client_name in sorted(hierarchy.keys()):
            client_id = self.task_tree.insert(
                "",
                "end",
                text=f"📁 {client_name}",
                values=("Client", "", "", "", ""),
                tags=("client", "client_row"),
            )

            for project_name in sorted(hierarchy[client_name].keys()):
                project_id = self.task_tree.insert(
                    client_id,
                    "end",
                    text=f"  📂 {project_name}",
                    values=("Project", "", "", "", ""),
                    tags=("project", "project_row"),
                )

                for task in hierarchy[client_name][project_name]:
                    billing_type = "Lump Sum" if task[5] else "Hourly"
                    rate = f"${task[6]:.2f}" if task[5] else f"${task[4]:.2f}/hr"
                    self.task_tree.insert(
                        project_id,
                        "end",
                        text=f"    ⚙️ {task[2]}",
                        values=("Task", task[0], "", billing_type, rate),
                        tags=("task", "task_row", f"task_id_{task[0]}"),
                    )

        if global_tasks:
            global_node = self.task_tree.insert(
                "",
                "end",
                text="📁 [GLOBAL TASKS]",
                values=("Global", "", "", "", ""),
                tags=("global",),
            )

            for task in global_tasks:
                billing_type = "Lump Sum" if task[5] else "Hourly"
                rate = f"${task[6]:.2f}" if task[5] else f"${task[4]:.2f}/hr"
                self.task_tree.insert(
                    global_node,
                    "end",
                    text=f"  ⚙️ {task[2]}",
                    values=("Global Task", task[0], "", billing_type, rate),
                    tags=("task", f"task_id_{task[0]}"),
                )

        self.task_tree.tag_configure("client", font=("Arial", 10, "bold"))
        self.task_tree.tag_configure("project", font=("Arial", 9, "bold"))
        self.task_tree.tag_configure("task", font=("Arial", 9))
        self.task_tree.tag_configure("global", font=("Arial", 10, "bold"), foreground="#10b981")
        self.restore_tree_state(self.task_tree, expanded_items, expand_all=False)
        for client_item in self.task_tree.get_children(""):
            self.task_tree.item(client_item, open=True)

    def refresh_time_entries(self):
        expanded_items = self.save_tree_state(self.entries_tree)

        for item in self.entries_tree.get_children():
            self.entries_tree.delete(item)

        filter_val = self.time_entries_filter_var.get() if hasattr(self, "time_entries_filter_var") else "unbilled"
        where_clause = ""
        if filter_val == "unbilled":
            where_clause = "WHERE te.is_billed = 0"
        elif filter_val == "billed":
            where_clause = "WHERE te.is_billed = 1"

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                SELECT te.id, te.client_name, te.project_name, te.task_name,
                       te.start_time, te.end_time, te.duration_minutes, te.description,
                       te.is_billed, te.invoice_number
                FROM time_entries te
                {where_clause}
                ORDER BY te.client_name, te.project_name, te.task_name, te.start_time DESC
            """
            )
            entries = cursor.fetchall()

        if not entries:
            return

        hierarchy = {}
        for entry in entries:
            client_name = entry[1]
            project_name = entry[2]
            task_name = entry[3]
            if client_name not in hierarchy:
                hierarchy[client_name] = {}
            if project_name not in hierarchy[client_name]:
                hierarchy[client_name][project_name] = {}
            if task_name not in hierarchy[client_name][project_name]:
                hierarchy[client_name][project_name][task_name] = []
            hierarchy[client_name][project_name][task_name].append(entry)

        for client_name in sorted(hierarchy.keys()):
            client_total_minutes = 0
            for project_name in hierarchy[client_name]:
                for task_name in hierarchy[client_name][project_name]:
                    for entry in hierarchy[client_name][project_name][task_name]:
                        client_total_minutes += entry[6] if entry[6] else 0

            client_total_hours = client_total_minutes / 60.0
            client_id = self.entries_tree.insert(
                "",
                "end",
                text=f"📁 {client_name}",
                values=("", f"{client_total_hours:.2f} hrs", ""),
                tags=("client", "client_row"),
            )

            for project_name in sorted(hierarchy[client_name].keys()):
                project_total_minutes = 0
                for task_name in hierarchy[client_name][project_name]:
                    for entry in hierarchy[client_name][project_name][task_name]:
                        project_total_minutes += entry[6] if entry[6] else 0

                project_total_hours = project_total_minutes / 60.0
                project_id = self.entries_tree.insert(
                    client_id,
                    "end",
                    text=f"  📂 {project_name}",
                    values=("", f"{project_total_hours:.2f} hrs", ""),
                    tags=("project", "project_row"),
                )

                for task_name in sorted(hierarchy[client_name][project_name].keys()):
                    task_entries = hierarchy[client_name][project_name][task_name]
                    task_total_minutes = sum(e[6] if e[6] else 0 for e in task_entries)
                    task_total_hours = task_total_minutes / 60.0
                    has_billed = any(e[8] for e in task_entries)
                    billed_indicator = " [BILLED]" if has_billed else ""

                    task_id = self.entries_tree.insert(
                        project_id,
                        "end",
                        text=f"    📋 {task_name}{billed_indicator}",
                        values=(f"{len(task_entries)} entries", f"{task_total_hours:.2f} hrs", ""),
                        tags=("task", "task_row"),
                    )

                    for entry in task_entries:
                        duration_minutes = entry[6] if entry[6] else 0
                        duration_hours = duration_minutes / 60.0
                        start_time = entry[4] or ""
                        try:
                            date_display = datetime.fromisoformat(start_time).strftime("%m/%d/%y")
                        except Exception:
                            date_display = start_time.split("T")[0] if "T" in start_time else start_time

                        self.entries_tree.insert(
                            task_id,
                            "end",
                            text="      ⏱️ Entry",
                            values=(date_display, f"{duration_hours:.2f} hrs", entry[7] or ""),
                            tags=("entry", f"entry_id_{entry[0]}", "entry_row"),
                        )

        self.entries_tree.tag_configure("client", font=("Arial", 10, "bold"))
        self.entries_tree.tag_configure("project", font=("Arial", 9, "bold"))
        self.entries_tree.tag_configure("task", font=("Arial", 9))
        self.entries_tree.tag_configure("entry", font=("Arial", 8))
        self.restore_tree_state(self.entries_tree, expanded_items, expand_all=False)
        for client_item in self.entries_tree.get_children(""):
            self.entries_tree.item(client_item, open=True)

    def refresh_combos(self):
        clients = self.client_model.get_all()
        client_names = [c[1] for c in clients]
        self.timer_client_combo["values"] = client_names
        self.project_client_combo["values"] = client_names
        self.task_client_combo["values"] = client_names

        tasks = self.task_model.get_all()
        global_tasks = self.task_model.get_global_tasks()
        task_displays = [format_task_display(task) for task in global_tasks]
        task_displays.extend(format_task_display(task) for task in tasks)

        self.manual_task_combo["values"] = task_displays
        self.invoice_client_combo["values"] = client_names
        self.manual_client_combo["values"] = client_names

    def generate_invoice_data(self, client_id, start_date, end_date):
        conn = self.db.conn
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM invoice_view
            WHERE client_id = ?
              AND DATE (start_time) BETWEEN ?
              AND ?
              AND (is_billed = 0 OR is_billed IS NULL)
              AND COALESCE(duration_minutes, 0) > 0
            """,
            (client_id, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")),
        )

        entries = cursor.fetchall()
        conn.row_factory = None

        if not entries:
            messagebox.showinfo("No Unbilled Hours", "No unbilled hours found for the selected client and date range.")
            return None

        self.pending_entry_ids = [row["entry_id"] for row in entries]
        invoice_items = []
        tasks = {}
        for row in entries:
            key = f"{row['project_name']} - {row['task_name']}"
            if key not in tasks:
                tasks[key] = {"minutes": 0, "rate": row["task_rate"] or row["project_rate"]}
            tasks[key]["minutes"] += row["duration_minutes"] or 0

        total_hours_all = 0.0
        for task_name, data in tasks.items():
            hours_exact = data["minutes"] / 60.0
            rate = data["rate"] or 0
            qty_hrs = round(hours_exact, 2)
            total_hours_all += qty_hrs
            amt = round(qty_hrs * rate, 2)
            invoice_items.append(
                {
                    "description": task_name,
                    "quantity": f"{qty_hrs:.2f} hrs",
                    "rate": f"${rate:.2f}/hr",
                    "amount": amt,
                }
            )

        return {
            "client_id": client_id,
            "start_date": start_date,
            "end_date": end_date,
            "items": invoice_items,
            "total": round(sum(item["amount"] for item in invoice_items), 2),
            "total_hours": round(total_hours_all, 2),
        }

    def refresh_all_data(self):
        self.refresh_clients()
        self.refresh_projects()
        self.refresh_tasks()
        self.refresh_time_entries()
        self.refresh_combos()
        self.load_company_info()
        self.update_daily_totals_display()
        self.refresh_email_templates()
        self.load_email_settings_silent()

        if hasattr(self, "template_combo"):
            from email_sender import EmailTemplate

            template_names = EmailTemplate.get_template_names()
            self.template_combo["values"] = template_names
            if template_names:
                self.template_combo.set(template_names[0])

        if hasattr(self, "billed_invoices_tree"):
            self.refresh_billed_invoices()
