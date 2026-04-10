"""CustomTkinter Invoices tab — create + paid/unpaid views (parity with ui/tk/invoice_tab)."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta
from tkinter import messagebox, ttk
from typing import Any

import tkinter as tk

import customtkinter as ctk

from models import Client, CompanyInfo, Project
from ui.ctk import style_tokens as st
from ui.ctk.invoice_dialogs import show_invoice_preview_dialog_ctk
from ui.ctk.ttk_theme import get_tree_ui_font, get_tree_ui_font_bold
from ui_helpers import center_dialog, restore_tree_state, save_tree_state


class CtkInvoicesTab:
    _TREE_COLORS = {
        "group_heading": "#e8f4f8",
        "group_text": "#13100f",
        "text": "#13100f",
        "text_secondary": "#666666",
    }

    def __init__(
        self,
        parent: Any,
        root: Any,
        db,
        entries_tab: Any,
        on_data_changed: Callable[[], None] | None = None,
    ) -> None:
        self.parent = parent
        self.root = root
        self.db = db
        self.entries_tab = entries_tab
        self.on_data_changed = on_data_changed or (lambda: None)
        self.client_model = Client(self.db)
        self.project_model = Project(self.db)
        self.company_model = CompanyInfo(self.db)

        self.invoice_filter_var = tk.StringVar(value="all_uninvoiced")
        self.invoice_view_var = tk.StringVar(value="unpaid")

        self._build_ui()
        self.show_invoice_view("create")

    def on_data_changed_external(self) -> None:
        """Call after billing data changes elsewhere (e.g. Timer)."""
        self.refresh_invoice_combos()
        self.refresh_billed_invoices()

    def _build_ui(self) -> None:
        top = ctk.CTkFrame(self.parent, fg_color="transparent")
        top.pack(fill="x", padx=st.PANEL_PAD_X, pady=st.SPACE_8)
        ctk.CTkLabel(top, text="View:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=6)
        ctk.CTkButton(top, text="Create Invoice", width=140, command=lambda: self.show_invoice_view("create")).pack(
            side="left", padx=4
        )
        ctk.CTkButton(top, text="Paid / Unpaid Invoices", width=180, command=lambda: self.show_invoice_view("billed")).pack(
            side="left", padx=4
        )

        self.invoice_view_container = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.invoice_view_container.pack(fill="both", expand=True)

        self._build_create_view()
        self._build_billed_view()

    def show_invoice_view(self, view_type: str) -> None:
        for w in self.invoice_view_container.winfo_children():
            w.pack_forget()

        if view_type == "create":
            self.invoice_create_frame.pack(fill="both", expand=True)
        else:
            self.invoice_billed_frame.pack(fill="both", expand=True)
            self.refresh_billed_invoices()

    def _build_create_view(self) -> None:
        self.invoice_create_frame = ctk.CTkFrame(self.invoice_view_container, fg_color="transparent")

        sel = ctk.CTkFrame(self.invoice_create_frame, fg_color="transparent")
        sel.pack(fill="x", padx=st.PANEL_PAD_X, pady=st.SPACE_8)
        ctk.CTkLabel(sel, text="Invoice selection", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", pady=(0, st.SECTION_TITLE_BOTTOM_PAD)
        )

        grid = ctk.CTkFrame(sel, fg_color="transparent")
        grid.pack(fill="x")

        ctk.CTkLabel(grid, text="Client:").grid(row=0, column=0, sticky="w", pady=4)
        self.invoice_client_combo = ctk.CTkComboBox(grid, values=[], width=260, state="readonly", command=self._on_invoice_client_combo)
        self.invoice_client_combo.grid(row=0, column=1, sticky="w", padx=8, pady=4)

        ctk.CTkLabel(grid, text="Project (optional):").grid(row=0, column=2, sticky="w", padx=(16, 0), pady=4)
        self.invoice_project_combo = ctk.CTkComboBox(grid, values=[], width=260, state="readonly")
        self.invoice_project_combo.grid(row=0, column=3, sticky="w", padx=8, pady=4)

        filt_row = ctk.CTkFrame(sel, fg_color="transparent")
        filt_row.pack(fill="x", pady=(8, 0))
        ctk.CTkLabel(filt_row, text="Filter:").pack(side="left", padx=(0, 8))

        self._filter_frame_inner = ctk.CTkFrame(filt_row, fg_color="transparent")
        self._filter_frame_inner.pack(side="left", fill="x", expand=True)

        ctk.CTkRadioButton(
            self._filter_frame_inner,
            text="All uninvoiced",
            variable=self.invoice_filter_var,
            value="all_uninvoiced",
            command=self.toggle_invoice_date_filter,
        ).pack(side="left", padx=8)
        ctk.CTkRadioButton(
            self._filter_frame_inner,
            text="Date range",
            variable=self.invoice_filter_var,
            value="date_range",
            command=self.toggle_invoice_date_filter,
        ).pack(side="left", padx=8)

        self.date_range_frame = ctk.CTkFrame(self._filter_frame_inner, fg_color="transparent")
        self.invoice_start_date = ctk.CTkEntry(self.date_range_frame, width=100)
        self.invoice_start_date.pack(side="left", padx=4)
        self.invoice_start_date.insert(0, (datetime.now() - timedelta(days=30)).strftime("%m/%d/%y"))
        ctk.CTkLabel(self.date_range_frame, text="to").pack(side="left", padx=4)
        self.invoice_end_date = ctk.CTkEntry(self.date_range_frame, width=100)
        self.invoice_end_date.pack(side="left", padx=4)
        self.invoice_end_date.insert(0, datetime.now().strftime("%m/%d/%y"))
        self.date_range_frame.pack_forget()

        btn_row = ctk.CTkFrame(sel, fg_color="transparent")
        btn_row.pack(fill="x", pady=(st.SPACE_10, 0))
        ctk.CTkButton(btn_row, text="Load time entries", command=self.load_invoiceable_entries).pack(
            side="left", padx=st.BUTTON_PAD_X
        )
        ctk.CTkButton(btn_row, text="Refresh lists", command=self.refresh_invoice_combos).pack(
            side="left", padx=st.BUTTON_PAD_X
        )

        ctk.CTkLabel(
            self.invoice_create_frame,
            text="Select time entries, then Preview invoice",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", padx=st.PANEL_PAD_X, pady=(st.SECTION_GAP, st.SPACE_4))

        self.tree_wrap = tk.Frame(self.invoice_create_frame)
        self.tree_wrap.pack(fill="both", expand=True, padx=st.PANEL_PAD_X, pady=st.SPACE_4)

        self.invoice_entries_tree = ttk.Treeview(
            self.tree_wrap,
            columns=("Date", "Project", "Task", "Duration", "Description"),
            selectmode="extended",
        )
        self.invoice_entries_tree.heading("#0", text="Select")
        self.invoice_entries_tree.heading("Date", text="Date")
        self.invoice_entries_tree.heading("Project", text="Project")
        self.invoice_entries_tree.heading("Task", text="Task")
        self.invoice_entries_tree.heading("Duration", text="Duration")
        self.invoice_entries_tree.heading("Description", text="Description")
        self.invoice_entries_tree.column("#0", width=50)
        self.invoice_entries_tree.column("Date", width=100)
        self.invoice_entries_tree.column("Project", width=150)
        self.invoice_entries_tree.column("Task", width=150)
        self.invoice_entries_tree.column("Duration", width=100)
        self.invoice_entries_tree.column("Description", width=250)
        ys = ttk.Scrollbar(self.tree_wrap, orient="vertical", command=self.invoice_entries_tree.yview)
        self.invoice_entries_tree.configure(yscrollcommand=ys.set)
        self.invoice_entries_tree.pack(side="left", fill="both", expand=True)
        ys.pack(side="right", fill="y")

        sum_fr = ctk.CTkFrame(self.invoice_create_frame, fg_color="transparent")
        sum_fr.pack(fill="x", padx=st.PANEL_PAD_X, pady=st.SPACE_8)
        self.invoice_summary_label = ctk.CTkLabel(
            sum_fr,
            text="No entries loaded. Select a client and click Load time entries.",
            font=ctk.CTkFont(size=12),
        )
        self.invoice_summary_label.pack(side="left", padx=st.BUTTON_PAD_X)
        ctk.CTkButton(sum_fr, text="Deselect all", width=100, command=self.deselect_all_invoice_entries).pack(
            side="right", padx=st.BUTTON_PAD_X
        )
        ctk.CTkButton(sum_fr, text="Select all", width=100, command=self.select_all_invoice_entries).pack(
            side="right", padx=st.BUTTON_PAD_X
        )
        ctk.CTkButton(sum_fr, text="Edit entry", width=100, command=self.edit_invoice_entry).pack(
            side="right", padx=st.BUTTON_PAD_X
        )
        ctk.CTkButton(sum_fr, text="Preview invoice", width=120, command=self.preview_invoice).pack(
            side="right", padx=st.BUTTON_PAD_X
        )

        self._populate_invoice_client_combo()

    def _on_invoice_client_combo(self, _choice: str) -> None:
        self.on_invoice_client_select()

    def _populate_invoice_client_combo(self) -> None:
        current = self.invoice_client_combo.get().strip()
        names = [c[1] for c in self.client_model.get_all()]
        self.invoice_client_combo.configure(values=names or [""])
        if current and current in names:
            self.invoice_client_combo.set(current)
            self.on_invoice_client_select()
        elif names:
            self.invoice_client_combo.set(names[0])
            self.on_invoice_client_select()
        else:
            self.invoice_client_combo.set("")
            self.invoice_project_combo.configure(values=[])
            self.invoice_project_combo.set("")

    def _build_billed_view(self) -> None:
        self.invoice_billed_frame = ctk.CTkFrame(self.invoice_view_container, fg_color="transparent")

        ctl = ctk.CTkFrame(self.invoice_billed_frame, fg_color="transparent")
        ctl.pack(fill="x", padx=st.PANEL_PAD_X, pady=st.SPACE_8)
        vf = ctk.CTkFrame(ctl, fg_color="transparent")
        vf.pack(side="left")
        ctk.CTkLabel(vf, text="Filter:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=6)
        ctk.CTkRadioButton(
            vf, text="Unpaid", variable=self.invoice_view_var, value="unpaid", command=self.refresh_billed_invoices
        ).pack(side="left", padx=6)
        ctk.CTkRadioButton(
            vf, text="Paid", variable=self.invoice_view_var, value="paid", command=self.refresh_billed_invoices
        ).pack(side="left", padx=6)
        ctk.CTkRadioButton(
            vf, text="All", variable=self.invoice_view_var, value="all", command=self.refresh_billed_invoices
        ).pack(side="left", padx=6)
        ctk.CTkButton(ctl, text="Refresh", command=self.refresh_billed_invoices).pack(side="right", padx=4)

        self.list_fr = tk.Frame(self.invoice_billed_frame)
        self.list_fr.pack(fill="both", expand=True, padx=st.PANEL_PAD_X, pady=st.SPACE_4)
        self.billed_invoices_tree = ttk.Treeview(
            self.list_fr,
            columns=("Invoice", "Client", "Date", "Amount", "Status", "Paid Date"),
            show="headings",
            selectmode="extended",
        )
        for col, w in (
            ("Invoice", 150),
            ("Client", 150),
            ("Date", 100),
            ("Amount", 100),
            ("Status", 80),
            ("Paid Date", 100),
        ):
            self.billed_invoices_tree.heading(col, text=col if col != "Invoice" else "Invoice #")
            self.billed_invoices_tree.column(col, width=w)
        vsb = ttk.Scrollbar(self.list_fr, orient="vertical", command=self.billed_invoices_tree.yview)
        self.billed_invoices_tree.configure(yscrollcommand=vsb.set)
        self.billed_invoices_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        act = ctk.CTkFrame(self.invoice_billed_frame, fg_color="transparent")
        act.pack(fill="x", padx=st.PANEL_PAD_X, pady=st.SPACE_8)
        ctk.CTkButton(act, text="Mark as PAID", command=self.mark_invoices_paid_dialog).pack(side="left", padx=st.BUTTON_PAD_X)
        ctk.CTkButton(act, text="Mark as UNPAID", command=self.mark_invoices_unpaid).pack(side="left", padx=st.BUTTON_PAD_X)
        ctk.CTkButton(act, text="Delete Invoice(s)", command=self.delete_invoices, fg_color="#b91c1c").pack(
            side="left", padx=st.BUTTON_PAD_X
        )
        self.billed_summary_label = ctk.CTkLabel(act, text="")
        self.billed_summary_label.pack(side="right", padx=st.GRID_PAD_X)

    def refresh_billed_invoices(self) -> None:
        for item in self.billed_invoices_tree.get_children():
            self.billed_invoices_tree.delete(item)

        view = self.invoice_view_var.get()
        paid_status = 1 if view == "paid" else (0 if view == "unpaid" else None)

        invoices = self.db.get_billing_history(paid_status=paid_status)

        self.billed_invoices_tree.tag_configure("paid", background="#d4edda")
        self.billed_invoices_tree.tag_configure("unpaid", background="#fff3cd")

        total = 0.0
        for inv in invoices:
            inv_num = inv[1]
            client = inv[3]
            date = inv[4][:10]
            amount = inv[7]
            is_paid = inv[12]
            date_paid = inv[13] if inv[13] else ""
            status = "PAID" if is_paid else "UNPAID"

            tag = "paid" if is_paid else "unpaid"
            self.billed_invoices_tree.insert(
                "",
                "end",
                values=(inv_num, client, date, f"${amount:.2f}", status, date_paid),
                tags=(tag,),
            )
            total += amount

        count = len(invoices)
        self.billed_summary_label.configure(text=f"{count} invoices | Total: ${total:.2f}")

    def mark_invoices_paid_dialog(self) -> None:
        selection = self.billed_invoices_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select invoices to mark as paid")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Mark Invoices as Paid")
        center_dialog(self.root, dialog, 300, 150)

        ttk.Label(dialog, text=f"Mark {len(selection)} invoice(s) as PAID?").pack(pady=10)
        ttk.Label(dialog, text="Date Paid (YYYY-MM-DD):").pack(pady=5)

        date_entry = ttk.Entry(dialog)
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        date_entry.pack(pady=5)

        def confirm():
            date_paid = date_entry.get().strip()
            if not date_paid:
                messagebox.showerror("Error", "Date is required")
                return

            for item in selection:
                values = self.billed_invoices_tree.item(item)["values"]
                invoice_num = values[0]
                self.db.mark_invoice_paid(invoice_num, date_paid)

            dialog.destroy()
            self.refresh_billed_invoices()
            self.on_data_changed()
            messagebox.showinfo("Success", f"{len(selection)} invoice(s) marked as PAID")

        ttk.Button(dialog, text="Confirm", command=confirm).pack(side="left", padx=20, pady=10)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).pack(side="right", padx=20, pady=10)

    def mark_invoices_unpaid(self) -> None:
        selection = self.billed_invoices_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select invoices to mark as unpaid")
            return

        if messagebox.askyesno("Confirm", f"Mark {len(selection)} invoice(s) as UNPAID?"):
            for item in selection:
                values = self.billed_invoices_tree.item(item)["values"]
                invoice_num = values[0]
                self.db.mark_invoice_unpaid(invoice_num)

            self.refresh_billed_invoices()
            self.on_data_changed()
            messagebox.showinfo("Success", f"{len(selection)} invoice(s) marked as UNPAID")

    def delete_invoices(self) -> None:
        selection = self.billed_invoices_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select invoice(s) to delete")
            return

        invoice_numbers = []
        for item in selection:
            values = self.billed_invoices_tree.item(item)["values"]
            if values:
                invoice_numbers.append(values[0])

        if not invoice_numbers:
            messagebox.showerror("Error", "Could not determine selected invoice numbers")
            return

        total_linked_entries = 0
        for invoice_number in invoice_numbers:
            total_linked_entries += self.db.get_invoice_linked_entry_count(invoice_number)

        confirm = messagebox.askyesno(
            "Confirm Invoice Deletion",
            f"Delete {len(invoice_numbers)} invoice(s)?\n\n"
            f"This will set {total_linked_entries} linked time entr"
            f"{'y' if total_linked_entries == 1 else 'ies'} back to UNBILLED and remove invoice history records.",
        )
        if not confirm:
            return

        failed = []
        for invoice_number in invoice_numbers:
            if not self.db.delete_invoice(invoice_number):
                failed.append(invoice_number)

        self.refresh_billed_invoices()
        self.on_data_changed()

        if failed:
            messagebox.showerror(
                "Partial Delete",
                "Some invoices could not be deleted:\n\n" + "\n".join(str(n) for n in failed),
            )
            return

        messagebox.showinfo("Success", f"Deleted {len(invoice_numbers)} invoice(s)")

    def on_invoice_client_select(self) -> None:
        client_name = self.invoice_client_combo.get()
        if not client_name:
            return

        client_id = None
        for client in self.client_model.get_all():
            if client[1] == client_name:
                client_id = client[0]
                break

        if client_id:
            projects = self.project_model.get_by_client(client_id)
            project_names = [p[2] for p in projects]
            vals = ["All Projects"] + project_names
            self.invoice_project_combo.configure(values=vals)
            self.invoice_project_combo.set("All Projects")
        else:
            self.invoice_project_combo.configure(values=[])
            self.invoice_project_combo.set("")

    def on_invoice_project_select(self) -> None:
        pass

    def toggle_invoice_date_filter(self) -> None:
        if self.invoice_filter_var.get() == "date_range":
            self.date_range_frame.pack(side="left", padx=20)
        else:
            self.date_range_frame.pack_forget()

    def refresh_invoice_combos(self) -> None:
        current_client = self.invoice_client_combo.get()
        client_names = [c[1] for c in self.client_model.get_all()]
        self.invoice_client_combo.configure(values=client_names or [""])

        if current_client in client_names:
            self.invoice_client_combo.set(current_client)
            self.on_invoice_client_select()
            self.load_invoiceable_entries()
        elif client_names:
            self.invoice_client_combo.set(client_names[0])
            self.on_invoice_client_select()
            self.load_invoiceable_entries()
        else:
            self.invoice_client_combo.set("")
            self.invoice_project_combo.configure(values=[])
            self.invoice_project_combo.set("")

    def load_invoiceable_entries(self) -> None:
        client_name = self.invoice_client_combo.get()
        if not client_name:
            messagebox.showerror("Error", "Please select a client first")
            return

        client_id = None
        for client in self.client_model.get_all():
            if client[1] == client_name:
                client_id = client[0]
                break
        if not client_id:
            messagebox.showerror("Error", "Invalid client selected")
            return

        project_name = self.invoice_project_combo.get()
        project_id = None
        if project_name and project_name != "All Projects":
            projects = self.project_model.get_by_client(client_id)
            for project in projects:
                if project[2] == project_name:
                    project_id = project[0]
                    break

        conn = self.db.conn
        cursor = conn.cursor()

        if self.invoice_filter_var.get() == "all_uninvoiced":
            if project_id:
                cursor.execute(
                    """
                    SELECT te.id, te.start_time, te.description, te.duration_minutes,
                           p.name as project_name, t.name as task_name
                    FROM time_entries te
                    JOIN tasks t ON te.task_id = t.id
                    JOIN projects p ON te.project_id = p.id
                    WHERE p.client_id = ? AND p.id = ? AND (te.is_billed = 0 OR te.is_billed IS NULL)
                    ORDER BY te.start_time DESC
                """,
                    (client_id, project_id),
                )
            else:
                cursor.execute(
                    """
                    SELECT te.id, te.start_time, te.description, te.duration_minutes,
                           p.name as project_name, t.name as task_name
                    FROM time_entries te
                    JOIN tasks t ON te.task_id = t.id
                    JOIN projects p ON te.project_id = p.id
                    WHERE p.client_id = ? AND (te.is_billed = 0 OR te.is_billed IS NULL)
                    ORDER BY te.start_time DESC
                """,
                    (client_id,),
                )
        else:
            try:
                start_date = datetime.strptime(self.invoice_start_date.get(), "%m/%d/%y")
                end_date = datetime.strptime(self.invoice_end_date.get(), "%m/%d/%y")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use MM/DD/YY")
                return

            if project_id:
                cursor.execute(
                    """
                    SELECT te.id, te.start_time, te.description, te.duration_minutes,
                           p.name as project_name, t.name as task_name
                    FROM time_entries te
                    JOIN tasks t ON te.task_id = t.id
                    JOIN projects p ON te.project_id = p.id
                    WHERE p.client_id = ? AND p.id = ?
                          AND DATE(te.start_time) BETWEEN ? AND ?
                          AND (te.is_billed = 0 OR te.is_billed IS NULL)
                    ORDER BY te.start_time DESC
                """,
                    (client_id, project_id, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")),
                )
            else:
                cursor.execute(
                    """
                    SELECT te.id, te.start_time, te.description, te.duration_minutes,
                           p.name as project_name, t.name as task_name
                    FROM time_entries te
                    JOIN tasks t ON te.task_id = t.id
                    JOIN projects p ON te.project_id = p.id
                    WHERE p.client_id = ?
                          AND DATE(te.start_time) BETWEEN ? AND ?
                          AND (te.is_billed = 0 OR te.is_billed IS NULL)
                    ORDER BY te.start_time DESC
                """,
                    (client_id, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")),
                )

        entries = cursor.fetchall()
        for item in self.invoice_entries_tree.get_children():
            self.invoice_entries_tree.delete(item)

        project_groups: dict = {}
        for entry in entries:
            entry_id, start_time, description, duration_minutes, p_name, t_name = entry
            if p_name not in project_groups:
                project_groups[p_name] = {}
            if t_name not in project_groups[p_name]:
                project_groups[p_name][t_name] = []
            project_groups[p_name][t_name].append(entry)

        total_hours = 0.0
        total_entries = 0
        for p_name in sorted(project_groups.keys()):
            project_hours = 0.0
            project_entry_count = 0
            for t_name in project_groups[p_name]:
                for entry in project_groups[p_name][t_name]:
                    project_hours += (entry[3] or 0) / 60.0
                    project_entry_count += 1

            project_node = self.invoice_entries_tree.insert(
                "",
                "end",
                text=f"{p_name}",
                values=("", "", "", f"{project_hours:.2f} hrs", f"{project_entry_count} entries"),
                tags=("project", "project_row"),
            )

            for t_name in sorted(project_groups[p_name].keys()):
                task_entries = project_groups[p_name][t_name]
                task_hours = sum((e[3] or 0) / 60.0 for e in task_entries)
                task_node = self.invoice_entries_tree.insert(
                    project_node,
                    "end",
                    text=f"  {t_name}",
                    values=("", "", "", f"{task_hours:.2f} hrs", f"{len(task_entries)} entries"),
                    tags=("task", "task_row"),
                )

                for entry in task_entries:
                    eid, start_time, description, duration_minutes, _, _ = entry
                    try:
                        dt = datetime.fromisoformat(start_time)
                        date_display = dt.strftime("%m/%d/%y %I:%M %p")
                    except Exception:
                        date_display = start_time[:10]

                    hours = (duration_minutes or 0) / 60.0
                    total_hours += hours
                    total_entries += 1
                    self.invoice_entries_tree.insert(
                        task_node,
                        "end",
                        text="",
                        values=(date_display, "", "", f"{hours:.2f} hrs", description or ""),
                        tags=(f"entry_id_{eid}", "entry", "entry_row"),
                    )

        expanded_items: set = set()
        try:
            expanded_items = save_tree_state(self.invoice_entries_tree)
        except Exception:
            pass

        self.invoice_entries_tree.tag_configure("project", font=get_tree_ui_font_bold(self.root))
        self.invoice_entries_tree.tag_configure("task", font=get_tree_ui_font_bold(self.root))
        self.invoice_entries_tree.tag_configure("entry", font=get_tree_ui_font(self.root))
        self.invoice_entries_tree.tag_configure(
            "project_row",
            background=self._TREE_COLORS["group_heading"],
            foreground=self._TREE_COLORS["group_text"],
            font=get_tree_ui_font_bold(self.root),
        )
        self.invoice_entries_tree.tag_configure(
            "task_row",
            background=self._TREE_COLORS["group_heading"],
            foreground=self._TREE_COLORS["group_text"],
            font=get_tree_ui_font_bold(self.root),
        )
        self.invoice_entries_tree.tag_configure(
            "entry_row",
            background="white",
            foreground=self._TREE_COLORS["text"],
            font=get_tree_ui_font(self.root),
        )
        restore_tree_state(self.invoice_entries_tree, expanded_items, expand_all=True)
        self.invoice_summary_label.configure(
            text=f"{total_entries} unbilled entries found | Total: {total_hours:.2f} hours"
        )

    def select_all_invoice_entries(self) -> None:
        def expand_all(parent: str) -> None:
            for item in self.invoice_entries_tree.get_children(parent):
                self.invoice_entries_tree.item(item, open=True)
                expand_all(item)

        expand_all("")

        def select_entries_recursive(parent: str) -> None:
            for item in self.invoice_entries_tree.get_children(parent):
                tags = self.invoice_entries_tree.item(item)["tags"]
                if any(tag.startswith("entry_id_") for tag in tags):
                    self.invoice_entries_tree.selection_add(item)
                select_entries_recursive(item)

        select_entries_recursive("")

    def deselect_all_invoice_entries(self) -> None:
        selected = self.invoice_entries_tree.selection()
        if selected:
            self.invoice_entries_tree.selection_remove(*selected)

    def edit_invoice_entry(self) -> None:
        selection = self.invoice_entries_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select ONE time entry to edit")
            return
        if len(selection) > 1:
            messagebox.showwarning(
                "Multiple Selection",
                "Please select only ONE entry at a time to edit.\n\n"
                f"You selected {len(selection)} entries.\n"
                "Click OK to close this message. No changes were made.",
            )
            return

        item = selection[0]
        tags = self.invoice_entries_tree.item(item)["tags"]
        if "entry" not in tags:
            messagebox.showerror("Error", "Please select an individual time entry (not a project/task group)")
            return

        entry_id = None
        for tag in tags:
            if tag.startswith("entry_id_"):
                entry_id = int(tag.replace("entry_id_", ""))
                break
        if not entry_id:
            messagebox.showerror("Error", "Could not find entry ID")
            return

        self.entries_tab.open_edit_entry_dialog(entry_id, after_save=self.load_invoiceable_entries)

    def preview_invoice(self) -> None:
        selection = self.invoice_entries_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select at least one time entry to invoice")
            return

        entry_ids: list[int] = []
        for item in selection:
            tags = self.invoice_entries_tree.item(item)["tags"]
            for tag in tags:
                if tag.startswith("entry_id_"):
                    entry_ids.append(int(tag.replace("entry_id_", "")))
                    break
        if not entry_ids:
            messagebox.showerror("Error", "Could not find selected entries")
            return

        client_name = self.invoice_client_combo.get()
        client_id = None
        for client in self.client_model.get_all():
            if client[1] == client_name:
                client_id = client[0]
                break

        show_invoice_preview_dialog_ctk(
            self.root,
            self.db,
            self.client_model,
            self.company_model,
            client_id,
            client_name,
            entry_ids,
            colors=self._TREE_COLORS,
            refresh_time_entries=self.entries_tab.refresh,
            load_invoiceable_entries=self.load_invoiceable_entries,
            open_edit_time_entry=lambda eid: self.entries_tab.open_edit_entry_dialog(eid),
            on_billing_updated=self.on_data_changed,
        )

    def sync_embedded_tk_widgets(self) -> None:
        from ui.ctk.ttk_theme import embedded_tk_frame_bg

        bg = embedded_tk_frame_bg()
        self.tree_wrap.configure(bg=bg, highlightthickness=0)
        self.list_fr.configure(bg=bg, highlightthickness=0)
