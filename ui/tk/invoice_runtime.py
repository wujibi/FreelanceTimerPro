from __future__ import annotations

from datetime import datetime
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

        for task_name, data in tasks.items():
            hours = data["minutes"] / 60.0
            if data["is_lump_sum"]:
                invoice_items.append({"description": task_name, "quantity": "1", "rate": f"${data['lump_sum_amount']:.2f}", "amount": data["lump_sum_amount"]})
            else:
                invoice_items.append({"description": task_name, "quantity": f"{hours:.2f} hrs", "rate": f"${data['rate']:.2f}/hr", "amount": hours * data["rate"]})

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
            "total": sum(item["amount"] for item in invoice_items),
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
