# ADD THESE METHODS TO gui.py (at the end, before refresh_all_data)

def refresh_billed_invoices(self):
    """Refresh the billed invoices list"""
    for item in self.billed_invoices_tree.get_children():
        self.billed_invoices_tree.delete(item)
    
    view = self.invoice_view_var.get()
    paid_status = 1 if view == "paid" else (0 if view == "unpaid" else None)
    
    invoices = self.db.get_billing_history(paid_status=paid_status)
    
    total = 0
    for inv in invoices:
        inv_num = inv[1]
        client = inv[3]
        date = inv[4][:10]
        amount = inv[7]
        is_paid = inv[12]
        date_paid = inv[13] if inv[13] else ""
        status = "PAID" if is_paid else "UNPAID"
        
        self.billed_invoices_tree.insert('', 'end', values=(
            inv_num, client, date, f"${amount:.2f}", status, date_paid
        ))
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
    dialog.geometry("300x150")
    
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
            values = self.billed_invoices_tree.item(item)['values']
            invoice_num = values[0]
            self.db.mark_invoice_paid(invoice_num, date_paid)
        
        dialog.destroy()
        self.refresh_billed_invoices()
        messagebox.showinfo("Success", f"{len(selection)} invoice(s) marked as PAID")
    
    ttk.Button(dialog, text="Confirm", command=confirm).pack(side='left', padx=20, pady=10)
    ttk.Button(dialog, text="Cancel", command=dialog.destroy).pack(side='right', padx=20, pady=10)

def mark_invoices_unpaid(self):
    """Mark selected invoices as unpaid (undo)"""
    selection = self.billed_invoices_tree.selection()
    if not selection:
        messagebox.showerror("Error", "Please select invoices to mark as unpaid")
        return
    
    if messagebox.askyesno("Confirm", f"Mark {len(selection)} invoice(s) as UNPAID?"):
        for item in selection:
            values = self.billed_invoices_tree.item(item)['values']
            invoice_num = values[0]
            self.db.mark_invoice_unpaid(invoice_num)
        
        self.refresh_billed_invoices()
        messagebox.showinfo("Success", f"{len(selection)} invoice(s) marked as UNPAID")
