from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta


class InvoiceTabMixin:
    def create_invoice_tab(self):
        # Invoice tab - COMPLETELY REDESIGNED
        invoice_frame = ttk.Frame(self.notebook)
        self.notebook.add(invoice_frame, text="Invoices")

        # Submenu bar at top
        submenu_frame = ttk.Frame(invoice_frame)
        submenu_frame.pack(fill="x", padx=10, pady=(10, 0))

        ttk.Label(submenu_frame, text="View:", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        ttk.Button(
            submenu_frame,
            text="📄 Create Invoice",
            command=lambda: self.show_invoice_view("create"),
        ).pack(side="left", padx=2)
        ttk.Button(
            submenu_frame,
            text="💰 Paid/Unpaid Invoices",
            command=lambda: self.show_invoice_view("billed"),
        ).pack(side="left", padx=2)

        # Container for switching views
        self.invoice_view_container = ttk.Frame(invoice_frame)
        self.invoice_view_container.pack(fill="both", expand=True)

        # Create both views
        self.create_invoice_create_view()
        self.create_invoice_billed_view()

        # Show create view by default
        self.show_invoice_view("create")

    def show_invoice_view(self, view_type):
        """Switch between invoice views"""
        for widget in self.invoice_view_container.winfo_children():
            widget.pack_forget()

        if view_type == "create":
            self.invoice_create_frame.pack(fill="both", expand=True)
        else:
            self.invoice_billed_frame.pack(fill="both", expand=True)
            self.refresh_billed_invoices()

    def create_invoice_create_view(self):
        """Create the invoice creation view"""
        self.invoice_create_frame = ttk.Frame(self.invoice_view_container)

        # Selection section at top
        selection_frame = ttk.LabelFrame(self.invoice_create_frame, text="📋 Invoice Selection")
        selection_frame.pack(fill="x", padx=10, pady=10)

        form_frame = ttk.Frame(selection_frame)
        form_frame.pack(fill="x", padx=10, pady=10)

        # Client selection
        ttk.Label(form_frame, text="Client:").grid(row=0, column=0, sticky="w", pady=5)
        self.invoice_client_combo = ttk.Combobox(form_frame, state="readonly", width=30)
        self.invoice_client_combo.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.invoice_client_combo.bind("<<ComboboxSelected>>", self.on_invoice_client_select)

        # Project selection (optional)
        ttk.Label(form_frame, text="Project (optional):").grid(row=0, column=2, sticky="w", pady=5, padx=(20, 0))
        self.invoice_project_combo = ttk.Combobox(form_frame, state="readonly", width=30)
        self.invoice_project_combo.grid(row=0, column=3, sticky="w", padx=5, pady=5)
        self.invoice_project_combo.bind("<<ComboboxSelected>>", self.on_invoice_project_select)

        # Date filter options
        ttk.Label(form_frame, text="Filter:").grid(row=1, column=0, sticky="w", pady=5)
        filter_options_frame = ttk.Frame(form_frame)
        filter_options_frame.grid(row=1, column=1, columnspan=3, sticky="w", padx=5, pady=5)

        self.invoice_filter_var = tk.StringVar(value="all_uninvoiced")
        ttk.Radiobutton(
            filter_options_frame,
            text="All Uninvoiced",
            variable=self.invoice_filter_var,
            value="all_uninvoiced",
            command=self.toggle_invoice_date_filter,
        ).pack(side="left", padx=5)
        ttk.Radiobutton(
            filter_options_frame,
            text="Date Range",
            variable=self.invoice_filter_var,
            value="date_range",
            command=self.toggle_invoice_date_filter,
        ).pack(side="left", padx=5)

        # Date range inputs (hidden by default)
        self.date_range_frame = ttk.Frame(filter_options_frame)
        self.date_range_frame.pack(side="left", padx=20)

        self.invoice_start_date = ttk.Entry(self.date_range_frame, width=12)
        self.invoice_start_date.pack(side="left")
        self.invoice_start_date.insert(0, (datetime.now() - timedelta(days=30)).strftime("%m/%d/%y"))

        ttk.Label(self.date_range_frame, text=" to ").pack(side="left", padx=2)

        self.invoice_end_date = ttk.Entry(self.date_range_frame, width=12)
        self.invoice_end_date.pack(side="left")
        self.invoice_end_date.insert(0, datetime.now().strftime("%m/%d/%y"))

        # Hide date range by default
        self.date_range_frame.pack_forget()

        # Load entries button AND email config buttons
        button_row = ttk.Frame(selection_frame)
        button_row.pack(fill="x", padx=10, pady=(0, 10))

        ttk.Button(button_row, text="🔍 Load Time Entries", command=self.load_invoiceable_entries).pack(
            side="left", padx=5
        )
        ttk.Button(button_row, text="🔄 Refresh", command=self.refresh_invoice_combos).pack(side="left", padx=5)

        # Time entries display section
        entries_frame = ttk.LabelFrame(self.invoice_create_frame, text="⏱️ Select Time Entries to Invoice")
        entries_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Info label
        info_label = ttk.Label(
            entries_frame,
            text="💡 Select individual time entries below, then click 'Preview Invoice' to generate",
            font=("Arial", 9, "italic"),
            foreground="#666",
        )
        info_label.pack(anchor="w", padx=10, pady=(5, 0))

        # Tree for selectable time entries
        tree_container = ttk.Frame(entries_frame)
        tree_container.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        self.invoice_entries_tree = ttk.Treeview(
            tree_container,
            columns=("Date", "Task", "Duration", "Description"),
            selectmode="extended",
        )

        self.invoice_entries_tree.heading("#0", text="Select")
        self.invoice_entries_tree.heading("Date", text="Date")
        self.invoice_entries_tree.heading("Task", text="Task")
        self.invoice_entries_tree.heading("Duration", text="Duration")
        self.invoice_entries_tree.heading("Description", text="Description")

        self.invoice_entries_tree.column("#0", width=72)
        self.invoice_entries_tree.column("Date", width=118)
        self.invoice_entries_tree.column("Task", width=168)
        self.invoice_entries_tree.column("Duration", width=108)
        self.invoice_entries_tree.column("Description", width=400)

        tree_scroll = ttk.Scrollbar(tree_container, orient="vertical", command=self.invoice_entries_tree.yview)
        self.invoice_entries_tree.configure(yscrollcommand=tree_scroll.set)

        self.invoice_entries_tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")

        # Summary and action buttons
        summary_frame = ttk.Frame(entries_frame)
        summary_frame.pack(fill="x", padx=10, pady=10)

        self.invoice_summary_label = ttk.Label(
            summary_frame,
            text="No entries loaded. Select a client and click 'Load Time Entries'.",
            font=("Arial", 10),
        )
        self.invoice_summary_label.pack(side="left", padx=10)

        ttk.Button(
            summary_frame,
            text="📄 Preview Invoice",
            command=self.preview_invoice,
            style="Accent.TButton",
        ).pack(side="right", padx=5)
        ttk.Button(summary_frame, text="✏️ Edit Entry", command=self.edit_invoice_entry).pack(side="right", padx=5)
        ttk.Button(summary_frame, text="Select All", command=self.select_all_invoice_entries).pack(
            side="right", padx=5
        )
        ttk.Button(summary_frame, text="Deselect All", command=self.deselect_all_invoice_entries).pack(
            side="right", padx=5
        )

    def create_invoice_billed_view(self):
        """Create the billed invoices view"""
        self.invoice_billed_frame = ttk.Frame(self.invoice_view_container)

        # Top control frame
        control_frame = ttk.Frame(self.invoice_billed_frame)
        control_frame.pack(fill="x", padx=10, pady=10)

        # View selector
        view_label_frame = ttk.LabelFrame(control_frame, text="View")
        view_label_frame.pack(side="left", padx=5)

        self.invoice_view_var = tk.StringVar(value="unpaid")
        ttk.Radiobutton(
            view_label_frame,
            text="Unpaid",
            variable=self.invoice_view_var,
            value="unpaid",
            command=self.refresh_billed_invoices,
        ).pack(side="left", padx=5, pady=5)
        ttk.Radiobutton(
            view_label_frame,
            text="Paid",
            variable=self.invoice_view_var,
            value="paid",
            command=self.refresh_billed_invoices,
        ).pack(side="left", padx=5, pady=5)
        ttk.Radiobutton(
            view_label_frame,
            text="All",
            variable=self.invoice_view_var,
            value="all",
            command=self.refresh_billed_invoices,
        ).pack(side="left", padx=5, pady=5)

        ttk.Button(control_frame, text="Refresh", command=self.refresh_billed_invoices).pack(side="right", padx=5)

        # Invoice list
        list_frame = ttk.LabelFrame(self.invoice_billed_frame, text="Invoices")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        tree_frame = ttk.Frame(list_frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.billed_invoices_tree = ttk.Treeview(
            tree_frame,
            columns=("Invoice", "Client", "Date", "Amount", "Status", "Paid Date"),
            show="headings",
            selectmode="extended",
        )

        self.billed_invoices_tree.heading("Invoice", text="Invoice #")
        self.billed_invoices_tree.heading("Client", text="Client")
        self.billed_invoices_tree.heading("Date", text="Invoice Date")
        self.billed_invoices_tree.heading("Amount", text="Amount")
        self.billed_invoices_tree.heading("Status", text="Status")
        self.billed_invoices_tree.heading("Paid Date", text="Date Paid")

        self.billed_invoices_tree.column("Invoice", width=150)
        self.billed_invoices_tree.column("Client", width=150)
        self.billed_invoices_tree.column("Date", width=100)
        self.billed_invoices_tree.column("Amount", width=100)
        self.billed_invoices_tree.column("Status", width=80)
        self.billed_invoices_tree.column("Paid Date", width=100)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.billed_invoices_tree.yview)
        self.billed_invoices_tree.configure(yscrollcommand=vsb.set)
        self.billed_invoices_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # Action buttons
        action_frame = ttk.Frame(self.invoice_billed_frame)
        action_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(action_frame, text="Mark as PAID", command=self.mark_invoices_paid_dialog).pack(
            side="left", padx=5
        )
        ttk.Button(action_frame, text="Mark as UNPAID", command=self.mark_invoices_unpaid).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Delete Invoice(s)", command=self.delete_invoices).pack(side="left", padx=5)

        self.billed_summary_label = ttk.Label(action_frame, text="")
        self.billed_summary_label.pack(side="right", padx=10)

    def refresh_billed_invoices(self):
        """Refresh the billed invoices list"""
        for item in self.billed_invoices_tree.get_children():
            self.billed_invoices_tree.delete(item)

        view = self.invoice_view_var.get()
        paid_status = 1 if view == "paid" else (0 if view == "unpaid" else None)

        invoices = self.db.get_billing_history(paid_status=paid_status)

        self.billed_invoices_tree.tag_configure("paid", background="#d4edda")
        self.billed_invoices_tree.tag_configure("unpaid", background="#fff3cd")

        total = 0
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
        self.billed_summary_label.config(text=f"{count} invoices | Total: ${total:.2f}")

    def mark_invoices_paid_dialog(self):
        """Show dialog to mark invoices as paid"""
        selection = self.billed_invoices_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select invoices to mark as paid")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Mark Invoices as Paid")
        self.center_dialog(dialog, 300, 150)

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
            messagebox.showinfo("Success", f"{len(selection)} invoice(s) marked as PAID")

        ttk.Button(dialog, text="Confirm", command=confirm).pack(side="left", padx=20, pady=10)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).pack(side="right", padx=20, pady=10)

    def mark_invoices_unpaid(self):
        """Mark selected invoices as unpaid"""
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
            messagebox.showinfo("Success", f"{len(selection)} invoice(s) marked as UNPAID")

    def delete_invoices(self):
        """Delete selected invoices and un-bill linked entries."""
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
        for invoice_num in invoice_numbers:
            total_linked_entries += self.db.get_invoice_linked_entry_count(invoice_num)

        if not messagebox.askyesno(
            "Confirm Invoice Deletion",
            f"Delete {len(invoice_numbers)} invoice(s)?\n\n"
            f"This will set {total_linked_entries} linked time entr"
            f"{'y' if total_linked_entries == 1 else 'ies'} back to UNBILLED and remove invoice history records.",
        ):
            return

        failed = []
        for invoice_num in invoice_numbers:
            if not self.db.delete_invoice(invoice_num):
                failed.append(invoice_num)

        self.refresh_billed_invoices()

        if failed:
            messagebox.showerror(
                "Partial Delete",
                "Some invoices could not be deleted:\n\n" + "\n".join(str(n) for n in failed),
            )
            return

        messagebox.showinfo("Success", f"Deleted {len(invoice_numbers)} invoice(s)")

    def on_invoice_client_select(self, event):
        del event
        client_name = self.invoice_client_combo.get()
        if not client_name:
            return

        clients = self.client_model.get_all()
        client_id = None
        for client in clients:
            if client[1] == client_name:
                client_id = client[0]
                break

        if client_id:
            projects = self.project_model.get_by_client(client_id)
            project_names = [p[2] for p in projects]
            self.invoice_project_combo["values"] = ["All Projects"] + project_names
            self.invoice_project_combo.set("All Projects")
        else:
            self.invoice_project_combo["values"] = []
            self.invoice_project_combo.set("")

    def on_invoice_project_select(self, event):
        del event

    def toggle_invoice_date_filter(self):
        if self.invoice_filter_var.get() == "date_range":
            self.date_range_frame.pack(side="left", padx=20)
        else:
            self.date_range_frame.pack_forget()

    def refresh_invoice_combos(self):
        current_client = self.invoice_client_combo.get()
        clients = self.client_model.get_all()
        client_names = [c[1] for c in clients]
        self.invoice_client_combo["values"] = client_names

        if current_client in client_names:
            self.invoice_client_combo.set(current_client)
            self.load_invoiceable_entries()
        else:
            self.invoice_project_combo["values"] = []
            self.invoice_project_combo.set("")
            messagebox.showinfo("Refreshed", "Client list updated.")

    def load_invoiceable_entries(self):
        client_name = self.invoice_client_combo.get()
        if not client_name:
            messagebox.showerror("Error", "Please select a client first")
            return

        clients = self.client_model.get_all()
        client_id = None
        for client in clients:
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
                          AND COALESCE(te.duration_minutes, 0) > 0
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
                          AND COALESCE(te.duration_minutes, 0) > 0
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
                          AND COALESCE(te.duration_minutes, 0) > 0
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
                          AND COALESCE(te.duration_minutes, 0) > 0
                    ORDER BY te.start_time DESC
                """,
                    (client_id, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")),
                )

        entries = cursor.fetchall()
        for item in self.invoice_entries_tree.get_children():
            self.invoice_entries_tree.delete(item)

        project_groups = {}
        for entry in entries:
            entry_id, start_time, description, duration_minutes, project_name, task_name = entry
            if project_name not in project_groups:
                project_groups[project_name] = {}
            if task_name not in project_groups[project_name]:
                project_groups[project_name][task_name] = []
            project_groups[project_name][task_name].append(entry)

        total_hours = 0
        total_entries = 0
        for project_name in sorted(project_groups.keys()):
            project_hours = 0
            project_entry_count = 0
            for task_name in project_groups[project_name]:
                for entry in project_groups[project_name][task_name]:
                    project_hours += (entry[3] or 0) / 60.0
                    project_entry_count += 1

            project_node = self.invoice_entries_tree.insert(
                "",
                "end",
                text=f"📁 {project_name}",
                values=("", "", f"{project_hours:.2f} hrs", f"{project_entry_count} entries"),
                tags=("project", "project_row"),
            )

            for task_name in sorted(project_groups[project_name].keys()):
                task_entries = project_groups[project_name][task_name]
                task_hours = sum((e[3] or 0) / 60.0 for e in task_entries)
                task_node = self.invoice_entries_tree.insert(
                    project_node,
                    "end",
                    text=f"  📋 {task_name}",
                    values=("", "", f"{task_hours:.2f} hrs", f"{len(task_entries)} entries"),
                    tags=("task", "task_row"),
                )

                for entry in task_entries:
                    entry_id, start_time, description, duration_minutes, _, _ = entry
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
                        text="    ⏱️",
                        values=(date_display, "", f"{hours:.2f} hrs", description or ""),
                        tags=(f"entry_id_{entry_id}", "entry", "entry_row"),
                    )

        expanded_items = set()
        if hasattr(self, "invoice_entries_tree"):
            try:
                expanded_items = self.save_tree_state(self.invoice_entries_tree)
            except Exception:
                pass

        self.invoice_entries_tree.tag_configure("project", font=("Arial", 10, "bold"))
        self.invoice_entries_tree.tag_configure("task", font=("Arial", 9, "bold"))
        self.invoice_entries_tree.tag_configure("entry", font=("Arial", 9))

        if "group_heading" in self.colors:
            self.invoice_entries_tree.tag_configure(
                "project_row",
                background=self.colors["group_heading"],
                foreground=self.colors.get("group_text", "white"),
                font=("Arial", 10, "bold"),
            )
            self.invoice_entries_tree.tag_configure(
                "task_row",
                background=self.colors["group_heading"],
                foreground=self.colors.get("group_text", "white"),
                font=("Arial", 9, "bold"),
            )
        else:
            self.invoice_entries_tree.tag_configure(
                "project_row",
                background="#e8f4f8",
                foreground="#13100f",
                font=("Arial", 10, "bold"),
            )
            self.invoice_entries_tree.tag_configure(
                "task_row",
                background="#e8f4f8",
                foreground="#13100f",
                font=("Arial", 9, "bold"),
            )

        self.invoice_entries_tree.tag_configure(
            "entry_row",
            background="white",
            foreground=self.colors["text"],
            font=("Arial", 9),
        )
        self.restore_tree_state(self.invoice_entries_tree, expanded_items, expand_all=True)
        self.invoice_summary_label.config(
            text=f"📊 {total_entries} unbilled entries found | Total: {total_hours:.2f} hours"
        )

    def select_all_invoice_entries(self):
        def expand_all(parent):
            for item in self.invoice_entries_tree.get_children(parent):
                self.invoice_entries_tree.item(item, open=True)
                expand_all(item)

        expand_all("")

        def select_entries_recursive(parent):
            for item in self.invoice_entries_tree.get_children(parent):
                tags = self.invoice_entries_tree.item(item)["tags"]
                if any(tag.startswith("entry_id_") for tag in tags):
                    self.invoice_entries_tree.selection_add(item)
                select_entries_recursive(item)

        select_entries_recursive("")

    def deselect_all_invoice_entries(self):
        selected = self.invoice_entries_tree.selection()
        if selected:
            self.invoice_entries_tree.selection_remove(*selected)

    def edit_invoice_entry(self):
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

        self.open_edit_time_entry_dialog_and_refresh(entry_id)

    def preview_invoice(self):
        selection = self.invoice_entries_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select at least one time entry to invoice")
            return

        entry_ids = []
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
        clients = self.client_model.get_all()
        client_id = None
        for client in clients:
            if client[1] == client_name:
                client_id = client[0]
                break

        self.show_invoice_preview_dialog(client_id, client_name, entry_ids)
