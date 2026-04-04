"""CustomTkinter Email tab — SMTP settings and templates (parity with ui/tk/email_tab)."""

from __future__ import annotations

import html
import re
from typing import Any

import tkinter as tk
from tkinter import messagebox, ttk

import customtkinter as ctk


class CtkEmailTab:
    def __init__(self, parent: Any, root: Any, db) -> None:
        self.parent = parent
        self.root = root
        self.db = db

        self.email_provider_var = tk.StringVar(value="custom")
        self.show_password_var = tk.BooleanVar(value=False)
        self.send_copy_to_self_var = tk.BooleanVar(value=True)
        self.show_preview_var = tk.BooleanVar(value=True)

        self._build_ui()
        self.show_email_view("settings")

    def _build_ui(self) -> None:
        top = ctk.CTkFrame(self.parent, fg_color="transparent")
        top.pack(fill="x", padx=8, pady=8)
        ctk.CTkLabel(top, text="View:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=6)
        ctk.CTkButton(top, text="Settings", width=120, command=lambda: self.show_email_view("settings")).pack(
            side="left", padx=4
        )
        ctk.CTkButton(top, text="Templates", width=120, command=lambda: self.show_email_view("templates")).pack(
            side="left", padx=4
        )

        self.email_view_container = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.email_view_container.pack(fill="both", expand=True)

        self._build_settings_view()
        self._build_templates_view()

    def show_email_view(self, view_type: str) -> None:
        for w in self.email_view_container.winfo_children():
            w.pack_forget()

        if view_type == "settings":
            self.email_settings_frame.pack(fill="both", expand=True)
            self.load_email_settings_silent()
        else:
            self.email_templates_frame.pack(fill="both", expand=True)
            self.refresh_email_templates()

    def _build_settings_view(self) -> None:
        self.email_settings_frame = ctk.CTkScrollableFrame(self.email_view_container, fg_color="transparent")

        ctk.CTkLabel(
            self.email_settings_frame,
            text="SMTP configuration",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", pady=(0, 8))

        ctk.CTkLabel(self.email_settings_frame, text="Provider:").pack(anchor="w")
        pf = ctk.CTkFrame(self.email_settings_frame, fg_color="transparent")
        pf.pack(fill="x", pady=4)
        ctk.CTkRadioButton(
            pf,
            text="Gmail",
            variable=self.email_provider_var,
            value="gmail",
            command=self.on_email_provider_select,
        ).pack(side="left", padx=8)
        ctk.CTkRadioButton(
            pf,
            text="Outlook",
            variable=self.email_provider_var,
            value="outlook",
            command=self.on_email_provider_select,
        ).pack(side="left", padx=8)
        ctk.CTkRadioButton(
            pf,
            text="Custom",
            variable=self.email_provider_var,
            value="custom",
            command=self.on_email_provider_select,
        ).pack(side="left", padx=8)

        ctk.CTkLabel(self.email_settings_frame, text="SMTP server:").pack(anchor="w", pady=(8, 0))
        self.smtp_server_entry = ctk.CTkEntry(self.email_settings_frame, width=420)
        self.smtp_server_entry.pack(anchor="w", pady=4)

        ctk.CTkLabel(self.email_settings_frame, text="SMTP port:").pack(anchor="w")
        self.smtp_port_entry = ctk.CTkEntry(self.email_settings_frame, width=120)
        self.smtp_port_entry.pack(anchor="w", pady=4)
        self.smtp_port_entry.insert(0, "587")

        ctk.CTkLabel(self.email_settings_frame, text="Your email:").pack(anchor="w", pady=(8, 0))
        self.email_address_entry = ctk.CTkEntry(self.email_settings_frame, width=420)
        self.email_address_entry.pack(anchor="w", pady=4)

        ctk.CTkLabel(self.email_settings_frame, text="App password:").pack(anchor="w")
        pw_row = ctk.CTkFrame(self.email_settings_frame, fg_color="transparent")
        pw_row.pack(fill="x", pady=4)
        self.email_password_entry = ctk.CTkEntry(pw_row, width=320, show="*")
        self.email_password_entry.pack(side="left", padx=(0, 8))
        ctk.CTkCheckBox(
            pw_row,
            text="Show",
            variable=self.show_password_var,
            command=self.toggle_password_visibility,
        ).pack(side="left")

        ctk.CTkLabel(
            self.email_settings_frame,
            text="Gmail: enable 2-Step Verification, then create an App Password at myaccount.google.com/security",
            font=ctk.CTkFont(size=11),
            text_color=("gray35", "gray65"),
            wraplength=640,
            justify="left",
        ).pack(anchor="w", pady=8)

        ctk.CTkLabel(self.email_settings_frame, text="From name (optional):").pack(anchor="w")
        self.email_from_name_entry = ctk.CTkEntry(self.email_settings_frame, width=420)
        self.email_from_name_entry.pack(anchor="w", pady=4)

        ctk.CTkLabel(
            self.email_settings_frame,
            text="Default behavior",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", pady=(16, 8))
        ctk.CTkCheckBox(
            self.email_settings_frame,
            text="Always send copy to me",
            variable=self.send_copy_to_self_var,
        ).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(
            self.email_settings_frame,
            text="Show preview before sending",
            variable=self.show_preview_var,
        ).pack(anchor="w", pady=2)

        bf = ctk.CTkFrame(self.email_settings_frame, fg_color="transparent")
        bf.pack(fill="x", pady=16)
        ctk.CTkButton(bf, text="Save settings", command=self.save_email_settings).pack(side="left", padx=4)
        ctk.CTkButton(bf, text="Load settings", command=self.load_email_settings).pack(side="left", padx=4)
        ctk.CTkButton(bf, text="Test connection", command=self.test_email_connection).pack(side="right", padx=4)

    def _build_templates_view(self) -> None:
        self.email_templates_frame = ctk.CTkFrame(self.email_view_container, fg_color="transparent")

        sel = ctk.CTkFrame(self.email_templates_frame, fg_color="transparent")
        sel.pack(fill="x", padx=8, pady=8)
        ctk.CTkLabel(sel, text="Template:").pack(side="left", padx=4)
        self.template_combo = ctk.CTkComboBox(sel, values=[], width=200, state="readonly")
        self.template_combo.pack(side="left", padx=4)
        ctk.CTkButton(sel, text="Load", width=80, command=self.load_selected_template).pack(side="left", padx=4)
        ctk.CTkButton(sel, text="Reset to default", width=120, command=self.reset_template_to_default).pack(
            side="left", padx=4
        )

        editor_wrap = ctk.CTkFrame(self.email_templates_frame, fg_color="transparent")
        editor_wrap.pack(fill="both", expand=True, padx=8, pady=4)

        left = ctk.CTkFrame(editor_wrap, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=(0, 6))
        ctk.CTkLabel(left, text="Template editor", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w")

        subj_row = ctk.CTkFrame(left, fg_color="transparent")
        subj_row.pack(fill="x", pady=6)
        ctk.CTkLabel(subj_row, text="Subject:").pack(side="left", padx=(0, 8))
        self.template_subject_entry = ctk.CTkEntry(subj_row, width=400)
        self.template_subject_entry.pack(side="left", fill="x", expand=True)

        vars_fr = ctk.CTkFrame(left, fg_color="transparent")
        vars_fr.pack(fill="x", pady=6)
        ctk.CTkLabel(vars_fr, text="Insert:").pack(side="left", padx=(0, 8))
        for label, var in [
            ("Client", "{{client_name}}"),
            ("Invoice #", "{{invoice_number}}"),
            ("Total", "{{invoice_total}}"),
            ("Date", "{{invoice_date}}"),
            ("Company", "{{company_name}}"),
        ]:
            ctk.CTkButton(
                vars_fr,
                text=label,
                width=88,
                command=lambda v=var: self.insert_variable(v),
            ).pack(side="left", padx=2)

        ctk.CTkLabel(left, text="Body (HTML):").pack(anchor="w", pady=(8, 0))
        body_host = tk.Frame(left)
        body_host.pack(fill="both", expand=True, pady=4)
        self.template_body_text = tk.Text(body_host, height=14, wrap="word")
        self.template_body_text.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(body_host, command=self.template_body_text.yview)
        self.template_body_text.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")

        right = ctk.CTkFrame(editor_wrap, fg_color="transparent")
        right.pack(side="right", fill="both", expand=True, padx=(6, 0))
        ctk.CTkLabel(right, text="Live preview", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(
            right,
            text="Sample data — click Update preview",
            font=ctk.CTkFont(size=11),
            text_color=("gray35", "gray65"),
        ).pack(anchor="w", pady=4)
        prv_host = tk.Frame(right)
        prv_host.pack(fill="both", expand=True, pady=4)
        self.template_preview_text = tk.Text(
            prv_host,
            height=14,
            wrap="word",
            state="disabled",
            background="#f5f5f5",
        )
        self.template_preview_text.pack(side="left", fill="both", expand=True)
        psb = ttk.Scrollbar(prv_host, command=self.template_preview_text.yview)
        self.template_preview_text.configure(yscrollcommand=psb.set)
        psb.pack(side="right", fill="y")

        ctk.CTkButton(right, text="Update preview", command=self.update_template_preview).pack(pady=6)

        bot = ctk.CTkFrame(self.email_templates_frame, fg_color="transparent")
        bot.pack(fill="x", padx=8, pady=8)
        ctk.CTkButton(bot, text="Save template", command=self.save_current_template).pack(side="left", padx=4)
        ctk.CTkButton(bot, text="Send test email", command=self.send_test_template_email).pack(side="right", padx=4)

    def on_email_provider_select(self) -> None:
        provider = self.email_provider_var.get()
        if provider == "gmail":
            self.smtp_server_entry.delete(0, "end")
            self.smtp_server_entry.insert(0, "smtp.gmail.com")
            self.smtp_port_entry.delete(0, "end")
            self.smtp_port_entry.insert(0, "587")
        elif provider == "outlook":
            self.smtp_server_entry.delete(0, "end")
            self.smtp_server_entry.insert(0, "smtp-mail.outlook.com")
            self.smtp_port_entry.delete(0, "end")
            self.smtp_port_entry.insert(0, "587")

    def toggle_password_visibility(self) -> None:
        self.email_password_entry.configure(show="" if self.show_password_var.get() else "*")

    def save_email_settings(self) -> None:
        smtp_server = self.smtp_server_entry.get().strip()
        smtp_port = self.smtp_port_entry.get().strip()
        email_address = self.email_address_entry.get().strip()
        email_password = self.email_password_entry.get().strip()
        from_name = self.email_from_name_entry.get().strip()

        if not smtp_server or not smtp_port or not email_address or not email_password:
            messagebox.showerror("Error", "Please fill in all required fields")
            return

        try:
            port = int(smtp_port)
        except ValueError:
            messagebox.showerror("Error", "SMTP port must be a number")
            return

        success = self.db.save_email_settings(
            smtp_server=smtp_server,
            smtp_port=port,
            email_address=email_address,
            email_password=email_password,
            from_name=from_name if from_name else None,
            send_copy_to_self=self.send_copy_to_self_var.get(),
            show_preview_before_send=self.show_preview_var.get(),
        )

        if success:
            messagebox.showinfo("Success", "Email settings saved successfully!")
        else:
            messagebox.showerror("Error", "Failed to save email settings")

    def load_email_settings(self) -> None:
        settings = self.db.get_email_settings()
        if not settings:
            messagebox.showinfo("No settings", "No email settings found. Please configure your email.")
            return
        self._populate_email_settings(settings)
        messagebox.showinfo("Success", "Email settings loaded successfully!")

    def load_email_settings_silent(self) -> None:
        settings = self.db.get_email_settings()
        if not settings:
            return
        self._populate_email_settings(settings)

    def _populate_email_settings(self, settings) -> None:
        self.smtp_server_entry.delete(0, "end")
        self.smtp_port_entry.delete(0, "end")
        self.email_address_entry.delete(0, "end")
        self.email_password_entry.delete(0, "end")
        self.email_from_name_entry.delete(0, "end")

        self.smtp_server_entry.insert(0, settings[1])
        self.smtp_port_entry.insert(0, str(settings[2]))
        self.email_address_entry.insert(0, settings[3])
        self.email_password_entry.insert(0, settings[4])
        if settings[5]:
            self.email_from_name_entry.insert(0, settings[5])

        if len(settings) > 6:
            self.send_copy_to_self_var.set(bool(settings[6]))
        if len(settings) > 7:
            self.show_preview_var.set(bool(settings[7]))

        smtp_server = settings[1].lower()
        if "gmail" in smtp_server:
            self.email_provider_var.set("gmail")
        elif "outlook" in smtp_server:
            self.email_provider_var.set("outlook")
        else:
            self.email_provider_var.set("custom")

    def test_email_connection(self) -> None:
        smtp_server = self.smtp_server_entry.get().strip()
        smtp_port = self.smtp_port_entry.get().strip()
        email_address = self.email_address_entry.get().strip()
        email_password = self.email_password_entry.get().strip()
        if not smtp_server or not smtp_port or not email_address or not email_password:
            messagebox.showerror("Error", "Please fill in all required fields before testing")
            return

        try:
            port = int(smtp_port)
        except ValueError:
            messagebox.showerror("Error", "SMTP port must be a number")
            return

        from email_sender import EmailSender

        sender = EmailSender(smtp_server, port, email_address, email_password)
        success, msg = sender.test_connection()
        if success:
            messagebox.showinfo("Connection successful", msg)
        else:
            messagebox.showerror("Connection failed", msg)

    def load_selected_template(self) -> None:
        from email_sender import EmailTemplate

        template_name = self.template_combo.get()
        if not template_name:
            messagebox.showerror("Error", "Please select a template")
            return

        db_template = self.db.get_email_template(template_name=template_name)
        if db_template:
            self.template_subject_entry.delete(0, "end")
            self.template_subject_entry.insert(0, db_template[2])
            self.template_body_text.delete("1.0", tk.END)
            self.template_body_text.insert("1.0", db_template[3])
            self.update_template_preview()
            messagebox.showinfo("Loaded", f"Template '{template_name}' loaded (custom version)")
        else:
            template = EmailTemplate.get_template(template_name)
            if not template:
                messagebox.showerror("Error", f"Template '{template_name}' not found")
                return
            self.template_subject_entry.delete(0, "end")
            self.template_subject_entry.insert(0, template["subject"])
            self.template_body_text.delete("1.0", tk.END)
            self.template_body_text.insert("1.0", template["body"])
            self.update_template_preview()
            messagebox.showinfo("Loaded", f"Template '{template_name}' loaded (default version)")

    def reset_template_to_default(self) -> None:
        template_name = self.template_combo.get()
        if not template_name:
            messagebox.showerror("Error", "Please select a template first")
            return
        if messagebox.askyesno(
            "Confirm reset",
            f"Reset '{template_name}' template to default?\n\nAny custom changes will be lost.",
        ):
            self.load_selected_template()

    def insert_variable(self, variable: str) -> None:
        try:
            self.template_body_text.focus_set()
            self.template_body_text.insert(tk.INSERT, variable)
        except tk.TclError:
            pass

    def update_template_preview(self) -> None:
        from email_sender import EmailTemplate

        subject = self.template_subject_entry.get()
        body = self.template_body_text.get("1.0", tk.END)

        variables = {
            "client_name": "John Smith",
            "client_company": "Smith Industries",
            "client_email": "john@example.com",
            "invoice_number": "INV-20260129-123456",
            "invoice_date": "January 29, 2026",
            "invoice_total": "$1,234.56",
            "payment_terms": "Net 30",
            "due_date": "February 28, 2026",
            "date_range": "01/01/26 - 01/29/26",
            "company_name": "Your Company",
            "company_email": "billing@yourcompany.com",
            "company_phone": "(555) 123-4567",
            "company_website": "www.yourcompany.com",
        }

        preview_subject = EmailTemplate.render_template(subject, variables)
        preview_body = EmailTemplate.render_template(body, variables)
        preview_body = preview_body.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
        preview_body = preview_body.replace("</p>", "\n\n")
        preview_body = re.sub("<[^<]+?>", "", preview_body)
        preview_body = html.unescape(preview_body)
        preview_body = "\n".join(line.strip() for line in preview_body.split("\n"))
        preview_body = re.sub("\n{3,}", "\n\n", preview_body)

        self.template_preview_text.configure(state="normal")
        self.template_preview_text.delete("1.0", tk.END)
        self.template_preview_text.insert("1.0", f"Subject: {preview_subject}\n\n{preview_body.strip()}")
        self.template_preview_text.configure(state="disabled")

    def save_current_template(self) -> None:
        template_name = self.template_combo.get()
        if not template_name:
            messagebox.showerror("Error", "Please select a template to save")
            return

        subject = self.template_subject_entry.get().strip()
        body = self.template_body_text.get("1.0", tk.END).strip()
        if not subject or not body:
            messagebox.showerror("Error", "Subject and body cannot be empty")
            return

        success = self.db.save_email_template(template_name, subject, body, is_default=False)
        if success:
            messagebox.showinfo("Success", f"Template '{template_name}' saved successfully!")
        else:
            messagebox.showerror("Error", "Failed to save template")

    def send_test_template_email(self) -> None:
        settings = self.db.get_email_settings()
        if not settings:
            messagebox.showerror(
                "Error",
                "Email settings not configured.\n\nConfigure SMTP under Email → Settings first.",
            )
            return

        subject = self.template_subject_entry.get().strip()
        body = self.template_body_text.get("1.0", tk.END).strip()
        if not subject or not body:
            messagebox.showerror("Error", "Subject and body cannot be empty")
            return

        from email_sender import EmailSender, EmailTemplate

        variables = {
            "client_name": "Test Client",
            "invoice_number": "INV-TEST-123",
            "invoice_total": "$100.00",
            "company_name": "Your Company",
        }

        rendered_subject = EmailTemplate.render_template(subject, variables)
        rendered_body = EmailTemplate.render_template(body, variables)
        sender = EmailSender(settings[1], settings[2], settings[3], settings[4])
        success, msg = sender.send_email(
            to_address=settings[3],
            subject=f"TEST: {rendered_subject}",
            body_html=rendered_body,
            from_name=settings[5] if len(settings) > 5 else None,
        )
        if success:
            messagebox.showinfo("Test sent", f"Test email sent to {settings[3]}!\n\nCheck your inbox.")
        else:
            messagebox.showerror("Send failed", msg)

    def refresh_email_templates(self) -> None:
        from email_sender import EmailTemplate

        template_names = EmailTemplate.get_template_names()
        self.template_combo.configure(values=template_names or [""])
        if template_names:
            self.template_combo.set(template_names[0])
