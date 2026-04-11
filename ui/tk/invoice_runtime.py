from __future__ import annotations

from datetime import datetime, timedelta
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class InvoiceRuntimeMixin:
    """Invoice generation and invoice-item editing runtime behavior."""

    def generate_invoice_from_entries(self, client_id, client_name, entry_ids):
        import sqlite3

        conn = self.db.conn
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        placeholders = ",".join(["?" for _ in entry_ids])
        cursor.execute(
            f"""
            SELECT * FROM invoice_view
            WHERE entry_id IN ({placeholders})
            AND (is_billed = 0 OR is_billed IS NULL)
            AND COALESCE(duration_minutes, 0) > 0
        """,
            entry_ids,
        )
        entries = cursor.fetchall()
        conn.row_factory = None

        if not entries:
            messagebox.showinfo("No Entries", "Selected entries are already billed or not found.")
            return

        self.pending_entry_ids = [row["entry_id"] for row in entries]
        invoice_items = []
        tasks = {}
        for row in entries:
            key = f"{row['project_name']} - {row['task_name']}"
            if key not in tasks:
                if row["task_lump_sum"]:
                    tasks[key] = {"minutes": 0, "rate": 0, "is_lump_sum": True, "lump_sum_amount": row["task_lump_amount"]}
                elif row["project_lump_sum"]:
                    tasks[key] = {"minutes": 0, "rate": 0, "is_lump_sum": True, "lump_sum_amount": row["project_lump_amount"]}
                else:
                    tasks[key] = {"minutes": 0, "rate": row["task_rate"] or row["project_rate"], "is_lump_sum": False, "lump_sum_amount": 0}
            tasks[key]["minutes"] += row["duration_minutes"] or 0

        total_hours_all = 0.0
        for task_name, data in tasks.items():
            hours_exact = data["minutes"] / 60.0
            if data["is_lump_sum"]:
                amt = round(float(data["lump_sum_amount"] or 0), 2)
                invoice_items.append(
                    {"description": task_name, "quantity": "1", "rate": f"${amt:.2f}", "amount": amt}
                )
            else:
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

        start_date = None
        end_date = None
        for row in entries:
            entry_date = datetime.fromisoformat(row["start_time"]).date()
            if start_date is None or entry_date < start_date:
                start_date = entry_date
            if end_date is None or entry_date > end_date:
                end_date = entry_date

        self.current_invoice_data = {
            "client_id": client_id,
            "start_date": datetime.combine(start_date, datetime.min.time()),
            "end_date": datetime.combine(end_date, datetime.max.time()),
            "items": invoice_items,
            "total": round(sum(item["amount"] for item in invoice_items), 2),
            "total_hours": round(total_hours_all, 2),
        }

        self.notebook.select(6)
        self.display_invoice_preview()
        messagebox.showinfo(
            "Invoice Generated",
            f"Invoice preview ready for {client_name}\nTotal: ${self.current_invoice_data['total']:.2f}\n\nReview and click 'Save as PDF' to finalize.",
        )

    def generate_invoice(self):
        client_text = self.invoice_client_combo.get()
        if not client_text:
            messagebox.showerror("Error", "Please select a client")
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

        try:
            start_date = datetime.strptime(self.invoice_start_date.get(), "%m/%d/%y")
            end_date = datetime.strptime(self.invoice_end_date.get(), "%m/%d/%y")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use MM/DD/YY")
            return

        self.current_invoice_data = self.generate_invoice_data(client_id, start_date, end_date)
        self.display_invoice_preview()

    def display_invoice_preview(self):
        for item in self.invoice_tree.get_children():
            self.invoice_tree.delete(item)
        if not self.current_invoice_data:
            self.invoice_total_label.config(text="Total: $0.00")
            return
        for item in self.current_invoice_data["items"]:
            self.invoice_tree.insert("", "end", values=(item["description"], item["quantity"], item["rate"], f"${item['amount']:.2f}"))
        self.invoice_total_label.config(text=f"Total: ${self.current_invoice_data['total']:.2f}")

    def save_invoice_pdf(self):
        if not hasattr(self, "current_invoice_data"):
            messagebox.showerror("Error", "Please generate an invoice first")
            return
        if not self.current_invoice_data:
            messagebox.showerror("Error", "No invoice data available")
            return

        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        filename = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")], initialfile=f"Invoice_{invoice_number}.pdf")
        if not filename:
            return

        try:
            from invoice_generator import InvoiceGenerator

            generator = InvoiceGenerator(self.db)
            generator.generate_pdf(self.current_invoice_data, filename, invoice_number)

            if hasattr(self, "pending_entry_ids") and self.pending_entry_ids:
                self.db.mark_entries_billed(self.pending_entry_ids, invoice_number)
                self.db.save_billing_history(self.current_invoice_data, invoice_number, filename)
                self.pending_entry_ids = []
                messagebox.showinfo("Success", f"Invoice saved as {filename}\n\nTime entries have been marked as billed and will not appear in future invoices.")
            else:
                messagebox.showinfo("Success", f"Invoice saved as {filename}")

            self.current_invoice_data = None
            for item in self.invoice_tree.get_children():
                self.invoice_tree.delete(item)
            self.invoice_total_label.config(text="Total: $0.00")
            self.refresh_time_entries()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save invoice: {str(e)}")

    def edit_invoice_item(self):
        selection = self.invoice_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select an item to edit")
            return
        item_values = self.invoice_tree.item(selection[0])["values"]
        self.open_edit_invoice_item_dialog(selection[0], item_values)

    def open_edit_invoice_item_dialog(self, item_id, item_values):
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Invoice Item")
        self.center_dialog(edit_window, 400, 200)

        form_frame = ttk.Frame(edit_window)
        form_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(form_frame, text="Description:").grid(row=0, column=0, sticky="w", pady=2)
        desc_entry = ttk.Entry(form_frame, width=40)
        desc_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        desc_entry.insert(0, item_values[0])

        ttk.Label(form_frame, text="Quantity:").grid(row=1, column=0, sticky="w", pady=2)
        qty_entry = ttk.Entry(form_frame)
        qty_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        qty_entry.insert(0, item_values[1])

        ttk.Label(form_frame, text="Rate:").grid(row=2, column=0, sticky="w", pady=2)
        rate_entry = ttk.Entry(form_frame)
        rate_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        rate_entry.insert(0, item_values[2])

        form_frame.columnconfigure(1, weight=1)
        button_frame = ttk.Frame(edit_window)
        button_frame.pack(fill="x", padx=10, pady=10)

        def save_changes():
            self.invoice_tree.item(item_id, values=(desc_entry.get(), qty_entry.get(), rate_entry.get(), item_values[3]))
            if hasattr(self, "current_invoice_data"):
                for item in self.current_invoice_data["items"]:
                    if item["description"] == item_values[0]:
                        item["description"] = desc_entry.get()
                        item["quantity"] = qty_entry.get()
                        item["rate"] = rate_entry.get()
                        break
            edit_window.destroy()

        ttk.Button(button_frame, text="Save", command=save_changes).pack(side="right", padx=5)
        ttk.Button(button_frame, text="Cancel", command=edit_window.destroy).pack(side="right")

    def remove_invoice_item(self):
        selection = self.invoice_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select an item to remove")
            return

        item_values = self.invoice_tree.item(selection[0])["values"]
        self.invoice_tree.delete(selection[0])

        if hasattr(self, "current_invoice_data"):
            self.current_invoice_data["items"] = [item for item in self.current_invoice_data["items"] if item["description"] != item_values[0]]
            self.current_invoice_data["total"] = sum(item["amount"] for item in self.current_invoice_data["items"])
            self.invoice_total_label.config(text=f"Total: ${self.current_invoice_data['total']:.2f}")

    def show_invoice_preview_dialog(self, client_id, client_name, entry_ids):
        """Show invoice preview dialog with EDIT and CREATE buttons."""
        import sqlite3

        preview_dialog = tk.Toplevel(self.root)
        preview_dialog.title(f"Invoice Preview - {client_name}")
        self.center_dialog(preview_dialog, 800, 600)

        conn = self.db.conn
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        placeholders = ",".join(["?" for _ in entry_ids])
        cursor.execute(
            f"""
            SELECT te.id as entry_id, te.start_time, te.duration_minutes, te.description,
                   p.name as project_name, p.hourly_rate as project_rate, p.is_lump_sum as project_lump_sum,
                   p.lump_sum_amount as project_lump_amount,
                   t.name as task_name, t.hourly_rate as task_rate, t.is_lump_sum as task_lump_sum,
                   t.lump_sum_amount as task_lump_amount
            FROM time_entries te
            JOIN tasks t ON te.task_id = t.id
            JOIN projects p ON te.project_id = p.id
            WHERE te.id IN ({placeholders})
              AND COALESCE(te.duration_minutes, 0) > 0
        """,
            entry_ids,
        )

        entries = cursor.fetchall()
        conn.row_factory = None

        if not entries:
            messagebox.showinfo(
                "No billable time",
                "None of the selected entries have billable time (all are zero hours).\n\n"
                "Edit those entries to add duration, or choose entries with time logged.",
            )
            preview_dialog.destroy()
            return

        billable_entry_ids = [int(entry["entry_id"]) for entry in entries]

        project_groups = {}
        for entry in entries:
            project_name = entry["project_name"]
            task_name = entry["task_name"]

            if project_name not in project_groups:
                project_groups[project_name] = {"tasks": {}, "subtotal": 0}

            if task_name not in project_groups[project_name]["tasks"]:
                project_groups[project_name]["tasks"][task_name] = {
                    "minutes": 0,
                    "rate": entry["task_rate"] or entry["project_rate"],
                    "is_lump_sum": entry["task_lump_sum"] or entry["project_lump_sum"],
                    "lump_sum_amount": entry["task_lump_amount"] or entry["project_lump_amount"],
                }

            project_groups[project_name]["tasks"][task_name]["minutes"] += entry["duration_minutes"] or 0

        invoice_items = []
        total_amount = 0
        total_hours = 0.0

        for project_name, project_data in project_groups.items():
            invoice_items.append(
                {
                    "description": f"**{project_name}**",
                    "quantity": "",
                    "rate": "",
                    "amount": "",
                    "is_header": True,
                }
            )

            project_subtotal = 0
            for task_name, task_data in project_data["tasks"].items():
                hours_exact = task_data["minutes"] / 60.0

                if task_data["is_lump_sum"]:
                    amount = round(float(task_data["lump_sum_amount"] or 0), 2)
                    invoice_items.append(
                        {
                            "description": f"  • {task_name}",
                            "quantity": "1",
                            "rate": f"${amount:.2f}",
                            "amount": amount,
                            "is_task": True,
                        }
                    )
                else:
                    rate = task_data["rate"] or 0
                    qty_hrs = round(hours_exact, 2)
                    amount = round(qty_hrs * rate, 2)
                    total_hours += qty_hrs
                    invoice_items.append(
                        {
                            "description": f"  • {task_name}",
                            "quantity": f"{qty_hrs:.2f} hrs",
                            "rate": f"${rate:.2f}/hr",
                            "amount": amount,
                            "is_task": True,
                        }
                    )

                project_subtotal += amount

            sub_rounded = round(project_subtotal, 2)
            invoice_items.append(
                {
                    "description": f"  {project_name} Subtotal",
                    "quantity": "",
                    "rate": "",
                    "amount": sub_rounded,
                    "is_subtotal": True,
                }
            )
            total_amount += sub_rounded

        total_amount = round(total_amount, 2)
        total_hours = round(total_hours, 2)

        start_dates = [datetime.fromisoformat(e["start_time"]) for e in entries]
        start_date = min(start_dates) if start_dates else datetime.now()
        end_date = max(start_dates) if start_dates else datetime.now()

        self.current_invoice_data = {
            "client_id": client_id,
            "client_name": client_name,
            "entry_ids": billable_entry_ids,
            "items": invoice_items,
            "total": total_amount,
            "total_hours": total_hours,
            "start_date": start_date,
            "end_date": end_date,
        }

        header_frame = ttk.Frame(preview_dialog)
        header_frame.pack(fill="x", padx=20, pady=20)

        ttk.Label(header_frame, text="INVOICE PREVIEW", font=("Arial", 16, "bold")).pack()
        ttk.Label(header_frame, text=f"Client: {client_name}", font=("Arial", 12)).pack(pady=5)
        ttk.Label(header_frame, text=f"Date: {datetime.now().strftime('%B %d, %Y')}", font=("Arial", 10)).pack()

        items_frame = ttk.LabelFrame(preview_dialog, text="Invoice Items")
        items_frame.pack(fill="both", expand=True, padx=20, pady=10)

        items_tree = ttk.Treeview(items_frame, columns=("Description", "Quantity", "Rate", "Amount"), show="headings")
        items_tree.heading("Description", text="Description")
        items_tree.heading("Quantity", text="Quantity")
        items_tree.heading("Rate", text="Rate")
        items_tree.heading("Amount", text="Amount")
        items_tree.column("Description", width=350)
        items_tree.column("Quantity", width=100)
        items_tree.column("Rate", width=100)
        items_tree.column("Amount", width=100)

        for item in invoice_items:
            if item.get("is_header"):
                items_tree.insert("", "end", values=(item["description"].replace("**", ""), "", "", ""), tags=("header",))
            elif item.get("is_subtotal"):
                items_tree.insert("", "end", values=(item["description"], "", "", f"${item['amount']:.2f}"), tags=("subtotal",))
            else:
                amount_display = f"${item['amount']:.2f}" if isinstance(item["amount"], (int, float)) else ""
                items_tree.insert("", "end", values=(item["description"], item["quantity"], item["rate"], amount_display))

        items_tree.tag_configure("header", font=("Arial", 10, "bold"), background="#e8f4f8")
        items_tree.tag_configure("subtotal", font=("Arial", 9, "bold"), background="#f0f0f0")
        items_tree.pack(fill="both", expand=True, padx=10, pady=10)

        total_frame = ttk.Frame(preview_dialog)
        total_frame.pack(fill="x", padx=20, pady=10)
        ttk.Label(
            total_frame,
            text=f"Total Hours: {total_hours:.2f} hrs",
            font=("Arial", 12, "bold"),
            foreground=self.colors["text_secondary"],
        ).pack(side="left")
        ttk.Label(total_frame, text=f"TOTAL: ${total_amount:.2f}", font=("Arial", 14, "bold")).pack(side="right")

        button_frame = ttk.Frame(preview_dialog)
        button_frame.pack(fill="x", padx=20, pady=20)

        def create_invoice():
            if messagebox.askyesno(
                "Confirm",
                f"Create invoice for ${total_amount:.2f}?\n\n"
                f"This will mark {len(billable_entry_ids)} billable time entr"
                f"{'y' if len(billable_entry_ids) == 1 else 'ies'} as BILLED.",
            ):
                invoice_date = datetime.now()
                invoice_number = f"INV-{invoice_date.strftime('%Y%m%d-%H%M%S')}"

                filename = filedialog.asksaveasfilename(
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf")],
                    initialfile=f"Invoice_{client_name.replace(' ', '_')}_{invoice_number}.pdf",
                )

                if filename:
                    try:
                        from invoice_generator import InvoiceGenerator

                        generator = InvoiceGenerator(self.db)
                        generator.generate_pdf(self.current_invoice_data, filename, invoice_number)

                        update_placeholders = ",".join(["?" for _ in billable_entry_ids])
                        cursor = self.db.conn.cursor()
                        cursor.execute(
                            f"""
                            UPDATE time_entries
                            SET is_billed = 1,
                                invoice_number = ?,
                                billing_date = ?
                            WHERE id IN ({update_placeholders})
                        """,
                            [invoice_number, invoice_date.strftime("%Y-%m-%d")] + billable_entry_ids,
                        )
                        self.db.conn.commit()
                        self.db.save_billing_history(self.current_invoice_data, invoice_number, filename)

                        self.refresh_time_entries()
                        self.load_invoiceable_entries()
                        preview_dialog.destroy()
                        messagebox.showinfo(
                            "Success",
                            "Invoice created successfully!\n\n"
                            f"File: {filename}\n"
                            f"Invoice #: {invoice_number}\n"
                            f"Total: ${total_amount:.2f}\n\n"
                            f"{len(billable_entry_ids)} time entries marked as billed.",
                        )
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to create invoice:\n\n{e}\n\nCheck console for details.")

        def edit_time_entries_from_preview():
            edit_window = tk.Toplevel(preview_dialog)
            edit_window.title("Edit Time Entries")
            self.center_dialog(edit_window, 700, 500)
            ttk.Label(edit_window, text="Select a time entry to edit:", font=("Arial", 12, "bold")).pack(padx=20, pady=10)

            tree_frame = ttk.Frame(edit_window)
            tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
            edit_tree = ttk.Treeview(
                tree_frame,
                columns=("Date", "Project", "Task", "Hours", "Description"),
                show="headings",
                selectmode="browse",
            )
            edit_tree.heading("Date", text="Date")
            edit_tree.heading("Project", text="Project")
            edit_tree.heading("Task", text="Task")
            edit_tree.heading("Hours", text="Hours")
            edit_tree.heading("Description", text="Description")
            edit_tree.column("Date", width=120)
            edit_tree.column("Project", width=120)
            edit_tree.column("Task", width=120)
            edit_tree.column("Hours", width=80)
            edit_tree.column("Description", width=200)

            scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=edit_tree.yview)
            edit_tree.configure(yscrollcommand=scrollbar.set)
            edit_tree.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            entry_placeholders = ",".join(["?" for _ in entry_ids])
            self.db.conn.row_factory = sqlite3.Row
            cursor = self.db.conn.cursor()
            cursor.execute(
                f"""
                SELECT te.id as entry_id, te.start_time, te.end_time, te.duration_minutes,
                       te.description, p.name as project_name, t.name as task_name
                FROM time_entries te
                JOIN tasks t ON te.task_id = t.id
                JOIN projects p ON te.project_id = p.id
                WHERE te.id IN ({entry_placeholders})
                ORDER BY te.start_time
            """,
                entry_ids,
            )
            time_entries = cursor.fetchall()
            self.db.conn.row_factory = None

            for entry in time_entries:
                try:
                    dt = datetime.fromisoformat(entry["start_time"])
                    date_display = dt.strftime("%m/%d/%y %I:%M %p")
                except Exception:
                    date_display = entry["start_time"][:10]

                hours = (entry["duration_minutes"] or 0) / 60.0
                edit_tree.insert(
                    "",
                    "end",
                    values=(date_display, entry["project_name"], entry["task_name"], f"{hours:.2f}", entry["description"] or ""),
                    tags=(f"entry_id_{entry['entry_id']}",),
                )

            btn_frame = ttk.Frame(edit_window)
            btn_frame.pack(fill="x", padx=20, pady=20)

            def edit_selected_entry():
                selection = edit_tree.selection()
                if not selection:
                    messagebox.showerror("Error", "Please select a time entry to edit")
                    return

                entry_id = None
                for tag in edit_tree.item(selection[0])["tags"]:
                    if tag.startswith("entry_id_"):
                        entry_id = int(tag.replace("entry_id_", ""))
                        break

                if not entry_id:
                    messagebox.showerror("Error", "Could not find entry ID")
                    return

                edit_window.destroy()
                self.open_edit_time_entry_dialog(entry_id)

            def refresh_invoice_preview():
                edit_window.destroy()
                preview_dialog.destroy()
                self.load_invoiceable_entries()
                messagebox.showinfo("Refreshed", "Invoice data refreshed. Select entries and preview again to see changes.")

            ttk.Button(btn_frame, text="✏️ Edit Selected Entry", command=edit_selected_entry).pack(side="left", padx=5)
            ttk.Button(btn_frame, text="🔄 Refresh & Close", command=refresh_invoice_preview).pack(side="left", padx=5)
            ttk.Button(btn_frame, text="Cancel", command=edit_window.destroy).pack(side="right", padx=5)

        def email_invoice():
            email_settings = self.db.get_email_settings()
            if not email_settings:
                if messagebox.askyesno(
                    "Email Not Configured",
                    "Email settings haven't been configured yet.\n\nWould you like to set them up now?",
                ):
                    self.notebook.select(6)
                    preview_dialog.destroy()
                return

            client = self.client_model.get_by_id(client_id)
            if not client or not client[3]:
                messagebox.showerror(
                    "No Email Address",
                    f"Client '{client_name}' doesn't have an email address on file.\n\nPlease add their email in the Clients tab first.",
                )
                return

            client_email = client[3]
            self.show_email_invoice_dialog(
                preview_dialog,
                client_name,
                client_email,
                client_id,
                billable_entry_ids,
                invoice_items,
                total_amount,
                start_date,
                end_date,
            )

        ttk.Button(button_frame, text="✏️ Edit Entries", command=edit_time_entries_from_preview).pack(side="left", padx=5)
        ttk.Button(button_frame, text="📧 Email Invoice", command=email_invoice).pack(side="right", padx=5)
        ttk.Button(button_frame, text="✅ CREATE INVOICE", command=create_invoice, style="Accent.TButton").pack(side="right", padx=5)
        ttk.Button(button_frame, text="Cancel", command=preview_dialog.destroy).pack(side="right", padx=5)

    def show_email_invoice_dialog(
        self,
        parent_dialog,
        client_name,
        client_email,
        client_id,
        entry_ids,
        invoice_items,
        total_amount,
        start_date,
        end_date,
    ):
        """Show dialog to send invoice via email."""
        import os
        import tempfile
        from email_sender import EmailSender, EmailTemplate

        email_dialog = tk.Toplevel(parent_dialog)
        email_dialog.title("Email Invoice")
        email_dialog.geometry("600x700")
        email_dialog.transient(parent_dialog)
        email_dialog.grab_set()

        header_frame = ttk.Frame(email_dialog)
        header_frame.pack(fill="x", padx=20, pady=20)
        ttk.Label(header_frame, text="📧 Email Invoice", font=("Arial", 16, "bold")).pack()
        ttk.Label(header_frame, text=f"To: {client_name} ({client_email})", font=("Arial", 10)).pack(pady=5)

        form_frame = ttk.LabelFrame(email_dialog, text="Email Details")
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)

        ttk.Label(form_frame, text="Template:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        template_var = tk.StringVar(value="Professional")
        template_combo = ttk.Combobox(
            form_frame,
            textvariable=template_var,
            values=EmailTemplate.get_template_names(),
            state="readonly",
        )
        template_combo.grid(row=0, column=1, sticky="ew", padx=10, pady=5)

        ttk.Label(form_frame, text="Subject:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        subject_entry = ttk.Entry(form_frame, width=50)
        subject_entry.grid(row=1, column=1, sticky="ew", padx=10, pady=5)

        ttk.Label(form_frame, text="CC (optional):").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        cc_entry = ttk.Entry(form_frame, width=50)
        cc_entry.grid(row=2, column=1, sticky="ew", padx=10, pady=5)
        ttk.Label(form_frame, text="Separate multiple emails with commas", font=("Arial", 8), foreground="gray").grid(
            row=3, column=1, sticky="w", padx=10
        )

        ttk.Label(form_frame, text="Message:").grid(row=4, column=0, sticky="nw", padx=10, pady=5)
        message_text = tk.Text(form_frame, height=15, wrap="word")
        message_text.grid(row=4, column=1, sticky="ew", padx=10, pady=5)
        message_scroll = ttk.Scrollbar(form_frame, orient="vertical", command=message_text.yview)
        message_text.configure(yscrollcommand=message_scroll.set)
        message_scroll.grid(row=4, column=2, sticky="ns", pady=5)
        form_frame.columnconfigure(1, weight=1)

        def update_template(*args):
            template_name = template_var.get()
            template = EmailTemplate.get_template(template_name)
            if template:
                company = self.company_model.get()
                invoice_number = f"INV-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                date_range = f"{start_date.strftime('%m/%d/%y')} - {end_date.strftime('%m/%d/%y')}"
                variables = {
                    "client_name": client_name,
                    "client_email": client_email,
                    "invoice_number": invoice_number,
                    "invoice_date": datetime.now().strftime("%B %d, %Y"),
                    "invoice_total": f"${total_amount:.2f}",
                    "payment_terms": company[7] if company and len(company) > 7 else "Net 30",
                    "due_date": (datetime.now() + timedelta(days=30)).strftime("%B %d, %Y"),
                    "date_range": date_range,
                    "company_name": company[1] if company else "Your Company",
                    "company_email": company[4] if company and len(company) > 4 else "",
                    "company_phone": company[3] if company and len(company) > 3 else "",
                    "company_website": company[6] if company and len(company) > 6 else "",
                }
                subject = EmailTemplate.render_template(template["subject"], variables)
                body = EmailTemplate.render_template(template["body"], variables)
                subject_entry.delete(0, tk.END)
                subject_entry.insert(0, subject)
                message_text.delete("1.0", tk.END)
                message_text.insert("1.0", body)

        template_combo.bind("<<ComboboxSelected>>", update_template)
        update_template()

        button_frame = ttk.Frame(email_dialog)
        button_frame.pack(fill="x", padx=20, pady=20)

        def send_email():
            try:
                email_settings = self.db.get_email_settings()
                if not email_settings:
                    messagebox.showerror("Error", "Email settings not found")
                    return

                smtp_server = email_settings[1]
                smtp_port = email_settings[2]
                email_address = email_settings[3]
                email_password = email_settings[4]
                from_name = email_settings[5] if len(email_settings) > 5 else None
                sender = EmailSender(smtp_server, smtp_port, email_address, email_password)

                invoice_number = f"INV-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                temp_dir = tempfile.gettempdir()
                pdf_path = os.path.join(temp_dir, f"{invoice_number}.pdf")

                invoice_data = {
                    "client_id": client_id,
                    "client_name": client_name,
                    "entry_ids": entry_ids,
                    "items": invoice_items,
                    "total": total_amount,
                    "start_date": start_date,
                    "end_date": end_date,
                }

                from invoice_generator import InvoiceGenerator

                generator = InvoiceGenerator(self.db)
                generator.generate_pdf(invoice_data, pdf_path, invoice_number)
                subject = subject_entry.get().strip()
                body_html = message_text.get("1.0", tk.END).strip()

                cc_addresses = None
                cc_text = cc_entry.get().strip()
                if cc_text:
                    cc_addresses = [email.strip() for email in cc_text.split(",")]

                success, message = sender.send_email(
                    to_address=client_email,
                    subject=subject,
                    body_html=body_html,
                    attachment_path=pdf_path,
                    cc_addresses=cc_addresses,
                    from_name=from_name,
                )

                try:
                    os.remove(pdf_path)
                except Exception:
                    pass

                if success:
                    if messagebox.askyesno(
                        "Email Sent!",
                        f"Invoice emailed successfully to {client_email}!\n\nWould you like to mark these time entries as BILLED now?",
                    ):
                        invoice_date = datetime.now()
                        cursor = self.db.conn.cursor()
                        placeholders = ",".join(["?" for _ in entry_ids])
                        cursor.execute(
                            f"""
                            UPDATE time_entries
                            SET is_billed = 1,
                                invoice_number = ?,
                                billing_date = ?
                            WHERE id IN ({placeholders})
                        """,
                            [invoice_number, invoice_date.strftime("%Y-%m-%d")] + entry_ids,
                        )
                        self.db.conn.commit()
                        self.db.save_billing_history(invoice_data, invoice_number, None)
                        self.refresh_time_entries()
                        self.load_invoiceable_entries()
                        messagebox.showinfo(
                            "Success",
                            f"Invoice #{invoice_number} sent and {len(entry_ids)} entries marked as billed!",
                        )

                    email_dialog.destroy()
                    parent_dialog.destroy()
                else:
                    messagebox.showerror("Send Failed", message)

            except Exception as e:
                import traceback

                traceback.print_exc()
                messagebox.showerror("Error", f"Failed to send email:\n\n{str(e)}")

        ttk.Button(button_frame, text="📧 Send Invoice", command=send_email, style="Accent.TButton").pack(side="right", padx=5)
        ttk.Button(button_frame, text="Cancel", command=email_dialog.destroy).pack(side="right", padx=5)
