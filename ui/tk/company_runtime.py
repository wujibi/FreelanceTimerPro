from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox


class CompanyRuntimeMixin:
    """Company information runtime behavior."""

    def browse_logo(self):
        filename = filedialog.askopenfilename(
            title="Select Logo Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")],
        )
        if filename:
            self.logo_path_var.set(filename)

    def save_company_info(self):
        name = self.company_name_entry.get().strip()
        address = self.company_address_text.get("1.0", tk.END).strip()
        phone = self.company_phone_entry.get().strip()
        email = self.company_email_entry.get().strip()
        logo_path = self.logo_path_var.get()
        website = self.company_website_entry.get().strip()
        payment_terms = self.company_payment_terms_entry.get().strip()
        thank_you_message = self.company_thank_you_entry.get().strip()

        if not name:
            messagebox.showerror("Error", "Company name is required")
            return

        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO company_info
                    (id, name, address, phone, email, logo_path, website, payment_terms, thank_you_message)
                    VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (name, address, phone, email, logo_path, website, payment_terms, thank_you_message),
                )
                conn.commit()
            messagebox.showinfo("Success", "Company information saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save company info: {str(e)}")

    def load_company_info(self):
        company = self.company_model.get()
        if company:
            self.company_name_entry.delete(0, tk.END)
            self.company_name_entry.insert(0, company[1])

            self.company_address_text.delete("1.0", tk.END)
            self.company_address_text.insert("1.0", company[2] or "")

            self.company_phone_entry.delete(0, tk.END)
            self.company_phone_entry.insert(0, company[3] or "")

            self.company_email_entry.delete(0, tk.END)
            self.company_email_entry.insert(0, company[4] or "")

            if len(company) > 5 and company[5]:
                self.logo_path_var.set(company[5])

            if len(company) > 6 and company[6]:
                self.company_website_entry.delete(0, tk.END)
                self.company_website_entry.insert(0, company[6])

            if len(company) > 7 and company[7]:
                self.company_payment_terms_entry.delete(0, tk.END)
                self.company_payment_terms_entry.insert(0, company[7])
            else:
                self.company_payment_terms_entry.delete(0, tk.END)
                self.company_payment_terms_entry.insert(0, "Payment is due within 30 days")

            if len(company) > 8 and company[8]:
                self.company_thank_you_entry.delete(0, tk.END)
                self.company_thank_you_entry.insert(0, company[8])
            else:
                self.company_thank_you_entry.delete(0, tk.END)
                self.company_thank_you_entry.insert(0, "Thank you for your business!")
