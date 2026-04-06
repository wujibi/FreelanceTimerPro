"""CustomTkinter Tasks tab — CRUD + hierarchy tree (Tk parity)."""

from __future__ import annotations

from collections.abc import Callable
from tkinter import messagebox, ttk

import tkinter as tk

import customtkinter as ctk

from core.project_resolution import resolve_project_id_by_names
from models import Client, Project, Task
from ui.ctk import style_tokens as st
from ui.ctk.ttk_theme import get_tree_ui_font, get_tree_ui_font_bold
from ui_helpers import restore_tree_state, save_tree_state


class CtkTasksTab:
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
        self.project_model = Project(self.db)
        self.task_model = Task(self.db)

        self.task_billing_var = tk.StringVar(value="hourly")
        self.task_global_var = tk.BooleanVar(value=False)

        self._build_ui()
        self.refresh_all()

    def refresh_all(self) -> None:
        self._refresh_client_combo()
        self.refresh_tree()

    def _refresh_client_combo(self) -> None:
        names = [c[1] for c in self.client_model.get_all()]
        self.task_client_combo.configure(values=names or [""])

    def _build_ui(self) -> None:
        form = ctk.CTkFrame(self.parent, fg_color="transparent")
        form.pack(fill="x", padx=st.PANEL_INNER_PAD_X, pady=st.SPACE_8)

        ctk.CTkLabel(form, text="Task information", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, st.SECTION_TITLE_BOTTOM_PAD)
        )

        ctk.CTkLabel(form, text="Client:").grid(row=1, column=0, sticky="w", pady=4)
        self.task_client_combo = ctk.CTkComboBox(
            form,
            values=[],
            width=st.COMBO_WIDTH,
            state="readonly",
            command=self._on_task_client_selected,
        )
        self.task_client_combo.grid(row=1, column=1, sticky="ew", padx=8, pady=4)

        ctk.CTkLabel(form, text="Project:").grid(row=2, column=0, sticky="w", pady=4)
        self.task_project_combo = ctk.CTkComboBox(form, values=[], width=st.COMBO_WIDTH, state="readonly")
        self.task_project_combo.grid(row=2, column=1, sticky="ew", padx=8, pady=4)

        ctk.CTkLabel(form, text="Name:").grid(row=3, column=0, sticky="w", pady=4)
        self.task_name_entry = ctk.CTkEntry(form, width=st.COMBO_WIDTH)
        self.task_name_entry.grid(row=3, column=1, sticky="ew", padx=8, pady=4)

        ctk.CTkLabel(form, text="Description:").grid(row=4, column=0, sticky="nw", pady=4)
        self.task_desc_text = ctk.CTkTextbox(form, width=st.COMBO_WIDTH, height=st.TEXTBOX_SHORT_HEIGHT)
        self.task_desc_text.grid(row=4, column=1, sticky="ew", padx=8, pady=4)

        ctk.CTkCheckBox(
            form,
            text="[GLOBAL] Available for all projects",
            variable=self.task_global_var,
            command=self.toggle_task_project_field,
        ).grid(row=5, column=0, columnspan=2, sticky="w", padx=8, pady=8)

        br = ctk.CTkFrame(form, fg_color="transparent")
        br.grid(row=6, column=1, sticky="w", padx=8, pady=4)
        ctk.CTkRadioButton(br, text="Hourly rate", variable=self.task_billing_var, value="hourly").pack(
            side="left", padx=(0, 12)
        )
        ctk.CTkRadioButton(br, text="Lump sum", variable=self.task_billing_var, value="lump_sum").pack(side="left")

        ctk.CTkLabel(form, text="Rate / amount:").grid(row=7, column=0, sticky="w", pady=4)
        self.task_rate_entry = ctk.CTkEntry(form, width=200)
        self.task_rate_entry.grid(row=7, column=1, sticky="w", padx=8, pady=4)

        form.columnconfigure(1, weight=1)

        bf = ctk.CTkFrame(self.parent, fg_color="transparent")
        bf.pack(fill="x", padx=st.PANEL_INNER_PAD_X, pady=st.BUTTON_ROW_PAD_Y)
        ctk.CTkButton(bf, text="Add Task", command=self.add_task).pack(side="left", padx=4)
        ctk.CTkButton(bf, text="Update Task", command=self.update_task).pack(side="left", padx=4)
        ctk.CTkButton(bf, text="Clear Form", command=self.clear_task_form).pack(side="left", padx=4)

        ctk.CTkLabel(self.parent, text="Tasks", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=st.PANEL_INNER_PAD_X, pady=(st.SECTION_GAP, st.SPACE_4)
        )

        list_section = ctk.CTkFrame(self.parent, fg_color="transparent")
        list_section.pack(fill="both", expand=True, padx=st.PANEL_PAD_X, pady=st.SPACE_4)

        dbf = ctk.CTkFrame(list_section, fg_color="transparent")
        dbf.pack(side="bottom", fill="x", pady=st.BUTTON_ROW_BOTTOM_PAD)
        ctk.CTkButton(dbf, text="Delete Task", command=self.delete_task, fg_color="gray40").pack(
            side="left", padx=st.BUTTON_PAD_X
        )

        self._tree_host = tk.Frame(list_section)
        self._tree_host.pack(side="top", fill="both", expand=True)

        self.task_tree = ttk.Treeview(self._tree_host, columns=("Type", "ID", "Extra", "Billing", "Rate"))
        self.task_tree.heading("#0", text="Hierarchy")
        self.task_tree.heading("Type", text="Type")
        self.task_tree.heading("ID", text="ID")
        self.task_tree.heading("Extra", text="")
        self.task_tree.heading("Billing", text="Billing")
        self.task_tree.heading("Rate", text="Rate")
        self.task_tree.column("#0", width=280)
        self.task_tree.column("Type", width=90)
        self.task_tree.column("ID", width=48)
        self.task_tree.column("Extra", width=80)
        self.task_tree.column("Billing", width=90)
        self.task_tree.column("Rate", width=90)

        ys = ttk.Scrollbar(self._tree_host, orient="vertical", command=self.task_tree.yview)
        self.task_tree.configure(yscrollcommand=ys.set)
        self.task_tree.pack(side="left", fill="both", expand=True)
        ys.pack(side="right", fill="y")

        self.task_tree.bind("<<TreeviewSelect>>", self.on_task_select)

        

    def _on_task_client_selected(self, _choice: str | None = None) -> None:
        client_name = self.task_client_combo.get()
        if not client_name:
            return
        client_id = None
        for client in self.client_model.get_all():
            if client[1] == client_name:
                client_id = client[0]
                break
        if client_id:
            projects = self.project_model.get_by_client(client_id)
            self.task_project_combo.configure(values=[p[2] for p in projects])
            self.task_project_combo.set("")

    def refresh_tree(self) -> None:
        expanded_items = save_tree_state(self.task_tree)

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
            cid = self.task_tree.insert(
                "",
                "end",
                text=f"📁 {client_name}",
                values=("Client", "", "", "", ""),
                tags=("client", "client_row"),
            )

            for project_name in sorted(hierarchy[client_name].keys()):
                pid = self.task_tree.insert(
                    cid,
                    "end",
                    text=f"  📂 {project_name}",
                    values=("Project", "", "", "", ""),
                    tags=("project", "project_row"),
                )

                for task in hierarchy[client_name][project_name]:
                    billing_type = "Lump Sum" if task[5] else "Hourly"
                    rate = f"${task[6]:.2f}" if task[5] else f"${task[4]:.2f}/hr"
                    self.task_tree.insert(
                        pid,
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

        self.task_tree.tag_configure("client", font=get_tree_ui_font_bold(self.root))
        self.task_tree.tag_configure("project", font=get_tree_ui_font_bold(self.root))
        self.task_tree.tag_configure("task", font=get_tree_ui_font(self.root))
        self.task_tree.tag_configure("global", font=get_tree_ui_font_bold(self.root), foreground="#10b981")
        restore_tree_state(self.task_tree, expanded_items, expand_all=True)

    def toggle_task_project_field(self) -> None:
        is_global = self.task_global_var.get()
        if is_global:
            self.task_client_combo.set("")
            self.task_project_combo.set("")
            self.task_client_combo.configure(state="disabled")
            self.task_project_combo.configure(state="disabled")
        else:
            self.task_client_combo.configure(state="readonly")
            self.task_project_combo.configure(state="readonly")
            self._refresh_client_combo()

    def add_task(self) -> None:
        name = self.task_name_entry.get().strip()
        description = self.task_desc_text.get("1.0", "end-1c").strip()
        is_global = self.task_global_var.get()

        if not name:
            messagebox.showerror("Error", "Please enter a task name")
            return

        try:
            rate = float(self.task_rate_entry.get() or 0)
        except ValueError:
            messagebox.showerror("Error", "Invalid rate/amount")
            return

        is_lump_sum_flag = self.task_billing_var.get() == "lump_sum"

        if is_global:
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

            for task in self.task_model.get_by_project(project_id):
                if task[2].lower() == name.lower():
                    messagebox.showerror("Error", f"Task '{name}' already exists for this project")
                    return

            if is_lump_sum_flag:
                self.task_model.create(name, description, 0, True, rate, project_id, False)
            else:
                self.task_model.create(name, description, rate, False, 0, project_id, False)
            messagebox.showinfo("Success", f"Task '{name}' created!")

        self.clear_task_form()
        self.refresh_all()
        self.on_data_changed()

    def update_task(self) -> None:
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
        description = self.task_desc_text.get("1.0", "end-1c").strip()
        if not name:
            messagebox.showerror("Error", "Task name is required")
            return

        try:
            rate = float(self.task_rate_entry.get() or 0)
        except ValueError:
            messagebox.showerror("Error", "Invalid rate/amount")
            return

        is_lump_sum = self.task_billing_var.get() == "lump_sum"
        if is_lump_sum:
            self.task_model.update(task_id, name, description, 0, True, rate)
        else:
            self.task_model.update(task_id, name, description, rate, False, 0)

        self.clear_task_form()
        self.refresh_all()
        self.on_data_changed()
        messagebox.showinfo("Success", "Task updated successfully")

    def delete_task(self) -> None:
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
            self.refresh_all()
            self.on_data_changed()
            messagebox.showinfo("Success", "Task deleted successfully")

    def clear_task_form(self) -> None:
        self.task_global_var.set(False)
        self.task_client_combo.set("")
        self.task_project_combo.set("")
        self.task_project_combo.configure(values=[])
        self.task_name_entry.delete(0, tk.END)
        self.task_desc_text.delete("1.0", "end")
        self.task_rate_entry.delete(0, tk.END)
        self.task_billing_var.set("hourly")
        self.toggle_task_project_field()

    def on_task_select(self, _event=None) -> None:
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
                    self.task_project_combo.configure(values=[p[2] for p in projects])
                    self.task_project_combo.set(project[2])

        self.task_name_entry.delete(0, tk.END)
        self.task_name_entry.insert(0, task[2])
        self.task_desc_text.delete("1.0", "end")
        self.task_desc_text.insert("1.0", task[3] or "")
        if task[5]:
            self.task_billing_var.set("lump_sum")
            self.task_rate_entry.delete(0, tk.END)
            self.task_rate_entry.insert(0, str(task[6]))
        else:
            self.task_billing_var.set("hourly")
            self.task_rate_entry.delete(0, tk.END)
            self.task_rate_entry.insert(0, str(task[4]))

    def sync_embedded_tk_widgets(self) -> None:
        from ui.ctk.ttk_theme import embedded_tk_frame_bg

        self._tree_host.configure(bg=embedded_tk_frame_bg(), highlightthickness=0)
