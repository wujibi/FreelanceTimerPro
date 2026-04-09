"""CustomTkinter Projects tab — CRUD parity with ui/tk/projects_* ."""

from __future__ import annotations

from collections.abc import Callable
import sqlite3
from tkinter import messagebox, ttk

import tkinter as tk

import customtkinter as ctk

from models import Client, Project
from ui.ctk import style_tokens as st


class CtkProjectsTab:
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

        self.project_billing_var = tk.StringVar(value="hourly")

        self._build_ui()
        self.refresh_all()

    def refresh_all(self) -> None:
        self._refresh_client_combo()
        self.refresh_tree()

    def _refresh_client_combo(self) -> None:
        current = self.project_client_combo.get().strip()
        names = [c[1] for c in self.client_model.get_all()]
        self.project_client_combo.configure(values=names or [""])
        if current and current in names:
            self.project_client_combo.set(current)
        elif names:
            self.project_client_combo.set(names[0])
        else:
            self.project_client_combo.set("")

    def _build_ui(self) -> None:
        form = ctk.CTkFrame(self.parent, fg_color="transparent")
        form.pack(fill="x", padx=st.PANEL_INNER_PAD_X, pady=st.SPACE_8)

        ctk.CTkLabel(form, text="Project information", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, st.SECTION_TITLE_BOTTOM_PAD)
        )

        ctk.CTkLabel(form, text="Client:").grid(row=1, column=0, sticky="w", pady=4)
        self.project_client_combo = ctk.CTkComboBox(form, values=[], width=st.COMBO_WIDTH, state="readonly")
        self.project_client_combo.grid(row=1, column=1, sticky="ew", padx=8, pady=4)

        ctk.CTkLabel(form, text="Name:").grid(row=2, column=0, sticky="w", pady=4)
        self.project_name_entry = ctk.CTkEntry(form, width=st.COMBO_WIDTH)
        self.project_name_entry.grid(row=2, column=1, sticky="ew", padx=8, pady=4)

        ctk.CTkLabel(form, text="Description:").grid(row=3, column=0, sticky="nw", pady=4)
        self.project_desc_text = ctk.CTkTextbox(form, width=st.COMBO_WIDTH, height=st.TEXTBOX_SHORT_HEIGHT)
        self.project_desc_text.grid(row=3, column=1, sticky="ew", padx=8, pady=4)

        br = ctk.CTkFrame(form, fg_color="transparent")
        br.grid(row=4, column=1, sticky="w", padx=8, pady=4)
        ctk.CTkRadioButton(
            br,
            text="Hourly rate",
            variable=self.project_billing_var,
            value="hourly",
        ).pack(side="left", padx=(0, 12))
        ctk.CTkRadioButton(
            br,
            text="Lump sum",
            variable=self.project_billing_var,
            value="lump_sum",
        ).pack(side="left")

        ctk.CTkLabel(form, text="Rate / amount:").grid(row=5, column=0, sticky="w", pady=4)
        self.project_rate_entry = ctk.CTkEntry(form, width=200)
        self.project_rate_entry.grid(row=5, column=1, sticky="w", padx=8, pady=4)

        form.columnconfigure(1, weight=1)

        bf = ctk.CTkFrame(self.parent, fg_color="transparent")
        bf.pack(fill="x", padx=st.PANEL_INNER_PAD_X, pady=st.BUTTON_ROW_PAD_Y)
        ctk.CTkButton(bf, text="Add Project", command=self.add_project).pack(side="left", padx=4)
        ctk.CTkButton(bf, text="Update Project", command=self.update_project).pack(side="left", padx=4)
        ctk.CTkButton(bf, text="Clear Form", command=self.clear_project_form).pack(side="left", padx=4)

        ctk.CTkLabel(self.parent, text="Projects", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=st.PANEL_INNER_PAD_X, pady=(st.SECTION_GAP, st.SPACE_4)
        )

        list_section = ctk.CTkFrame(self.parent, fg_color="transparent")
        list_section.pack(fill="both", expand=True, padx=st.PANEL_PAD_X, pady=st.SPACE_4)

        dbf = ctk.CTkFrame(list_section, fg_color="transparent")
        dbf.pack(side="bottom", fill="x", pady=st.BUTTON_ROW_BOTTOM_PAD)
        ctk.CTkButton(dbf, text="Delete Project", command=self.delete_project, fg_color="gray40").pack(
            side="left", padx=st.BUTTON_PAD_X
        )

        self._tree_host = tk.Frame(list_section)
        self._tree_host.pack(side="top", fill="both", expand=True)

        self.project_tree = ttk.Treeview(
            self._tree_host,
            columns=("ID", "Client", "Name", "Type", "Rate"),
            show="headings",
        )
        cols = ("ID", "Client", "Name", "Type", "Rate")
        widths = (48, 130, 180, 100, 100)
        for col, w in zip(cols, widths):
            self.project_tree.heading(col, text=col)
            self.project_tree.column(col, width=w)

        ys = ttk.Scrollbar(self._tree_host, orient="vertical", command=self.project_tree.yview)
        self.project_tree.configure(yscrollcommand=ys.set)
        self.project_tree.pack(side="left", fill="both", expand=True)
        ys.pack(side="right", fill="y")

        self.project_tree.bind("<<TreeviewSelect>>", self.on_project_select)

        

    def refresh_tree(self) -> None:
        for item in self.project_tree.get_children():
            self.project_tree.delete(item)
        for project in self.project_model.get_all():
            billing_type = "Lump Sum" if project[5] else "Hourly"
            rate = f"${project[6]:.2f}" if project[5] else f"${project[4]:.2f}/hr"
            client_name = project[9] if len(project) > 9 else "Unknown Client"
            self.project_tree.insert(
                "",
                "end",
                values=(project[0], client_name, project[2], billing_type, rate),
            )

    def add_project(self) -> None:
        client_text = self.project_client_combo.get()
        name = self.project_name_entry.get().strip()
        description = self.project_desc_text.get("1.0", "end-1c").strip()

        if not client_text or not name:
            messagebox.showerror("Error", "Client and project name are required")
            return

        client_id = None
        for client in self.client_model.get_all():
            if client[1] == client_text:
                client_id = client[0]
                break

        if not client_id:
            messagebox.showerror("Error", "Invalid client selected")
            return

        for project in self.project_model.get_by_client(client_id):
            if project[2].lower() == name.lower():
                messagebox.showerror("Error", f"Project '{name}' already exists for this client")
                return

        try:
            rate = float(self.project_rate_entry.get() or 0)
        except ValueError:
            messagebox.showerror("Error", "Invalid rate/amount")
            return

        is_lump_sum = self.project_billing_var.get() == "lump_sum"
        if is_lump_sum:
            self.project_model.create(client_id, name, description, 0, True, rate)
        else:
            self.project_model.create(client_id, name, description, rate, False, 0)

        self.clear_project_form()
        self.refresh_all()
        self.on_data_changed()
        messagebox.showinfo("Success", "Project added successfully")

    def update_project(self) -> None:
        selection = self.project_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a project to update")
            return

        project_id = self.project_tree.item(selection[0])["values"][0]
        client_text = self.project_client_combo.get()
        name = self.project_name_entry.get().strip()
        description = self.project_desc_text.get("1.0", "end-1c").strip()

        if not client_text or not name:
            messagebox.showerror("Error", "Client and project name are required")
            return

        client_id = None
        for client in self.client_model.get_all():
            if client[1] == client_text:
                client_id = client[0]
                break

        if not client_id:
            messagebox.showerror("Error", "Invalid client selected")
            return

        try:
            rate = float(self.project_rate_entry.get() or 0)
        except ValueError:
            messagebox.showerror("Error", "Invalid rate/amount")
            return

        is_lump_sum = self.project_billing_var.get() == "lump_sum"
        if is_lump_sum:
            self.project_model.update(project_id, client_id, name, description, 0, True, rate)
        else:
            self.project_model.update(project_id, client_id, name, description, rate, False, 0)

        self.clear_project_form()
        self.refresh_all()
        self.on_data_changed()
        messagebox.showinfo("Success", "Project updated successfully")

    def delete_project(self) -> None:
        selection = self.project_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a project to delete")
            return

        project_id = self.project_tree.item(selection[0])["values"][0]
        impact = self.project_model.get_delete_impact_counts(project_id)
        confirm_msg = (
            "Delete this project?\n\n"
            f"This will delete {impact['tasks']} task{'s' if impact['tasks'] != 1 else ''} and "
            f"{impact['time_entries']} time entr{'y' if impact['time_entries'] == 1 else 'ies'}."
        )
        if impact["billed_entries"] > 0:
            confirm_msg += (
                f"\nIncludes {impact['billed_entries']} billed/invoiced entr"
                f"{'y' if impact['billed_entries'] == 1 else 'ies'}."
            )

        if messagebox.askyesno("Confirm", confirm_msg):
            try:
                self.project_model.delete(project_id)
                self.refresh_all()
                self.on_data_changed()
                messagebox.showinfo("Success", "Project deleted successfully")
            except sqlite3.IntegrityError as exc:
                messagebox.showerror(
                    "Delete Blocked",
                    "Could not delete this project due to linked billing/invoice records.\n\n"
                    f"Details: {exc}",
                )
            except Exception as exc:
                messagebox.showerror("Delete Failed", f"Unexpected error deleting project:\n\n{exc}")

    def clear_project_form(self) -> None:
        self.project_client_combo.set("")
        self.project_name_entry.delete(0, tk.END)
        self.project_desc_text.delete("1.0", "end")
        self.project_rate_entry.delete(0, tk.END)
        self.project_billing_var.set("hourly")

    def on_project_select(self, _event=None) -> None:
        selection = self.project_tree.selection()
        if not selection:
            return
        project_id = self.project_tree.item(selection[0])["values"][0]
        project = self.project_model.get_by_id(project_id)
        if not project:
            return
        client = self.client_model.get_by_id(project[1])
        if client:
            self.project_client_combo.set(client[1])
        self.project_name_entry.delete(0, tk.END)
        self.project_name_entry.insert(0, project[2])
        self.project_desc_text.delete("1.0", "end")
        self.project_desc_text.insert("1.0", project[3] or "")
        if project[5]:
            self.project_billing_var.set("lump_sum")
            self.project_rate_entry.delete(0, tk.END)
            self.project_rate_entry.insert(0, str(project[6]))
        else:
            self.project_billing_var.set("hourly")
            self.project_rate_entry.delete(0, tk.END)
            self.project_rate_entry.insert(0, str(project[4]))

    def sync_embedded_tk_widgets(self) -> None:
        from ui.ctk.ttk_theme import embedded_tk_frame_bg

        self._tree_host.configure(bg=embedded_tk_frame_bg(), highlightthickness=0)
