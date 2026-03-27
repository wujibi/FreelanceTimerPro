from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox


class EmailTabMixin:
    def create_email_tab(self):
        """Create Email tab with Settings and Templates subviews"""
        email_frame = ttk.Frame(self.notebook)
        self.notebook.add(email_frame, text="📧 Email")

        # Submenu bar at top
        submenu_frame = ttk.Frame(email_frame)
        submenu_frame.pack(fill="x", padx=10, pady=(10, 0))

        ttk.Label(submenu_frame, text="View:", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        ttk.Button(
            submenu_frame,
            text="⚙️ Settings",
            command=lambda: self.show_email_view("settings"),
        ).pack(side="left", padx=2)
        ttk.Button(
            submenu_frame,
            text="📝 Templates",
            command=lambda: self.show_email_view("templates"),
        ).pack(side="left", padx=2)

        # Container for switching views
        self.email_view_container = ttk.Frame(email_frame)
        self.email_view_container.pack(fill="both", expand=True)

        # Create both views
        self.create_email_settings_view()
        self.create_email_templates_view()

        # Show settings by default
        self.show_email_view("settings")

    def show_email_view(self, view_type):
        """Switch between email views"""
        for widget in self.email_view_container.winfo_children():
            widget.pack_forget()

        if view_type == "settings":
            self.email_settings_frame.pack(fill="both", expand=True)
            self.load_email_settings_silent()  # Auto-load when viewing
        else:
            self.email_templates_frame.pack(fill="both", expand=True)
            self.refresh_email_templates()  # Auto-refresh when viewing

    def create_email_settings_view(self):
        """Create Email Settings view for SMTP configuration"""
        self.email_settings_frame = ttk.Frame(self.email_view_container)

        # Main settings frame
        settings_frame = ttk.LabelFrame(self.email_settings_frame, text="SMTP Configuration")
        settings_frame.pack(fill="x", padx=10, pady=10)

        form_frame = ttk.Frame(settings_frame)
        form_frame.pack(fill="x", padx=10, pady=10)

        # Provider presets
        ttk.Label(form_frame, text="Provider:").grid(row=0, column=0, sticky="w", pady=5)
        provider_frame = ttk.Frame(form_frame)
        provider_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        self.email_provider_var = tk.StringVar(value="custom")
        ttk.Radiobutton(
            provider_frame,
            text="Gmail",
            variable=self.email_provider_var,
            value="gmail",
            command=self.on_email_provider_select,
        ).pack(side="left", padx=5)
        ttk.Radiobutton(
            provider_frame,
            text="Outlook",
            variable=self.email_provider_var,
            value="outlook",
            command=self.on_email_provider_select,
        ).pack(side="left", padx=5)
        ttk.Radiobutton(
            provider_frame,
            text="Custom",
            variable=self.email_provider_var,
            value="custom",
            command=self.on_email_provider_select,
        ).pack(side="left", padx=5)

        # SMTP Server
        ttk.Label(form_frame, text="SMTP Server:").grid(row=1, column=0, sticky="w", pady=5)
        self.smtp_server_entry = ttk.Entry(form_frame, width=40)
        self.smtp_server_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # SMTP Port
        ttk.Label(form_frame, text="SMTP Port:").grid(row=2, column=0, sticky="w", pady=5)
        self.smtp_port_entry = ttk.Entry(form_frame, width=10)
        self.smtp_port_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        self.smtp_port_entry.insert(0, "587")

        # Email Address
        ttk.Label(form_frame, text="Your Email:").grid(row=3, column=0, sticky="w", pady=5)
        self.email_address_entry = ttk.Entry(form_frame, width=40)
        self.email_address_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        # Email Password
        ttk.Label(form_frame, text="App Password:").grid(row=4, column=0, sticky="w", pady=5)
        password_frame = ttk.Frame(form_frame)
        password_frame.grid(row=4, column=1, sticky="ew", padx=5, pady=5)

        self.email_password_entry = ttk.Entry(password_frame, show="*", width=30)
        self.email_password_entry.pack(side="left", fill="x", expand=True)

        self.show_password_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            password_frame,
            text="Show",
            variable=self.show_password_var,
            command=self.toggle_password_visibility,
        ).pack(side="left", padx=5)

        # Gmail App Password instructions
        gmail_note = ttk.Label(
            form_frame,
            text=(
                "💡 Gmail users: Enable 2-Step Verification, then create an App Password"
                " at myaccount.google.com/security"
            ),
            font=("Arial", 8),
            foreground="#666",
            wraplength=500,
        )
        gmail_note.grid(row=5, column=0, columnspan=2, sticky="w", pady=(0, 10))

        # From Name (optional)
        ttk.Label(form_frame, text="From Name (optional):").grid(row=6, column=0, sticky="w", pady=5)
        self.email_from_name_entry = ttk.Entry(form_frame, width=40)
        self.email_from_name_entry.grid(row=6, column=1, sticky="ew", padx=5, pady=5)

        form_frame.columnconfigure(1, weight=1)

        # Default behavior
        behavior_frame = ttk.LabelFrame(self.email_settings_frame, text="Default Behavior")
        behavior_frame.pack(fill="x", padx=10, pady=10)

        options_frame = ttk.Frame(behavior_frame)
        options_frame.pack(fill="x", padx=10, pady=10)

        self.send_copy_to_self_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="☑️ Always send copy to me",
            variable=self.send_copy_to_self_var,
        ).pack(anchor="w", pady=2)

        self.show_preview_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="☑️ Show preview before sending",
            variable=self.show_preview_var,
        ).pack(anchor="w", pady=2)

        # Buttons
        button_frame = ttk.Frame(self.email_settings_frame)
        button_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(button_frame, text="💾 Save Settings", command=self.save_email_settings).pack(side="left", padx=5)
        ttk.Button(button_frame, text="🔄 Load Settings", command=self.load_email_settings).pack(side="left", padx=5)
        ttk.Button(
            button_frame,
            text="🔧 Test Connection",
            command=self.test_email_connection,
            style="Accent.TButton",
        ).pack(side="right", padx=5)

    def create_email_templates_view(self):
        """Create Email Templates view for managing email templates"""
        self.email_templates_frame = ttk.Frame(self.email_view_container)

        # Template selection
        selection_frame = ttk.Frame(self.email_templates_frame)
        selection_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(selection_frame, text="Template:").pack(side="left", padx=5)

        self.template_combo = ttk.Combobox(selection_frame, state="readonly", width=25)
        self.template_combo.pack(side="left", padx=5)
        self.template_combo.bind("<<ComboboxSelected>>", self.on_template_select)

        ttk.Button(selection_frame, text="Load", command=self.load_selected_template).pack(side="left", padx=5)
        ttk.Button(selection_frame, text="Reset to Default", command=self.reset_template_to_default).pack(
            side="left", padx=5
        )

        # Editor and preview
        editor_frame = ttk.Frame(self.email_templates_frame)
        editor_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Left side - Editor
        left_frame = ttk.LabelFrame(editor_frame, text="✏️ Template Editor")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        # Subject
        subject_frame = ttk.Frame(left_frame)
        subject_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(subject_frame, text="Subject:").pack(side="left")
        self.template_subject_entry = ttk.Entry(subject_frame)
        self.template_subject_entry.pack(side="left", fill="x", expand=True, padx=5)

        # Variable insertion buttons
        vars_frame = ttk.LabelFrame(left_frame, text="Insert Variable")
        vars_frame.pack(fill="x", padx=10, pady=5)

        vars_inner = ttk.Frame(vars_frame)
        vars_inner.pack(fill="x", padx=5, pady=5)

        variables = [
            ("Client Name", "{{client_name}}"),
            ("Invoice #", "{{invoice_number}}"),
            ("Total", "{{invoice_total}}"),
            ("Date", "{{invoice_date}}"),
            ("Company", "{{company_name}}"),
        ]

        for i, (label, var) in enumerate(variables):
            ttk.Button(
                vars_inner,
                text=label,
                command=lambda v=var: self.insert_variable(v),
            ).grid(row=i // 3, column=i % 3, padx=2, pady=2, sticky="ew")

        # Body
        body_label = ttk.Label(left_frame, text="Body (supports HTML):")
        body_label.pack(anchor="w", padx=10, pady=(10, 0))

        body_frame = ttk.Frame(left_frame)
        body_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.template_body_text = tk.Text(body_frame, height=15, wrap="word")
        self.template_body_text.pack(side="left", fill="both", expand=True)

        body_scroll = ttk.Scrollbar(body_frame, command=self.template_body_text.yview)
        body_scroll.pack(side="right", fill="y")
        self.template_body_text.config(yscrollcommand=body_scroll.set)

        # Right side - Preview
        right_frame = ttk.LabelFrame(editor_frame, text="👁️ Live Preview")
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        preview_info = ttk.Label(
            right_frame,
            text="Preview with sample data",
            font=("Arial", 9, "italic"),
            foreground="#666",
        )
        preview_info.pack(anchor="w", padx=10, pady=5)

        preview_text_frame = ttk.Frame(right_frame)
        preview_text_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.template_preview_text = tk.Text(
            preview_text_frame,
            height=15,
            wrap="word",
            state="disabled",
            background="#f8f8f8",
        )
        self.template_preview_text.pack(side="left", fill="both", expand=True)

        preview_scroll = ttk.Scrollbar(preview_text_frame, command=self.template_preview_text.yview)
        preview_scroll.pack(side="right", fill="y")
        self.template_preview_text.config(yscrollcommand=preview_scroll.set)

        ttk.Button(right_frame, text="🔄 Update Preview", command=self.update_template_preview).pack(pady=5)

        # Bottom buttons
        bottom_frame = ttk.Frame(self.email_templates_frame)
        bottom_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(bottom_frame, text="💾 Save Template", command=self.save_current_template).pack(side="left", padx=5)
        ttk.Button(
            bottom_frame,
            text="📧 Send Test Email",
            command=self.send_test_template_email,
            style="Accent.TButton",
        ).pack(side="right", padx=5)

    # Email settings methods
    def on_email_provider_select(self):
        provider = self.email_provider_var.get()
        if provider == "gmail":
            self.smtp_server_entry.delete(0, tk.END)
            self.smtp_server_entry.insert(0, "smtp.gmail.com")
            self.smtp_port_entry.delete(0, tk.END)
            self.smtp_port_entry.insert(0, "587")
        elif provider == "outlook":
            self.smtp_server_entry.delete(0, tk.END)
            self.smtp_server_entry.insert(0, "smtp-mail.outlook.com")
            self.smtp_port_entry.delete(0, tk.END)
            self.smtp_port_entry.insert(0, "587")

    def toggle_password_visibility(self):
        if self.show_password_var.get():
            self.email_password_entry.config(show="")
        else:
            self.email_password_entry.config(show="*")

    def save_email_settings(self):
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

    def load_email_settings(self):
        settings = self.db.get_email_settings()
        if not settings:
            messagebox.showinfo("No Settings", "No email settings found. Please configure your email.")
            return
        self._populate_email_settings(settings)
        messagebox.showinfo("Success", "Email settings loaded successfully!")

    def load_email_settings_silent(self):
        settings = self.db.get_email_settings()
        if not settings:
            return
        self._populate_email_settings(settings)

    def _populate_email_settings(self, settings):
        self.smtp_server_entry.delete(0, tk.END)
        self.smtp_port_entry.delete(0, tk.END)
        self.email_address_entry.delete(0, tk.END)
        self.email_password_entry.delete(0, tk.END)
        self.email_from_name_entry.delete(0, tk.END)

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

    def test_email_connection(self):
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
        success, message = sender.test_connection()
        if success:
            messagebox.showinfo("Connection Successful", message)
        else:
            messagebox.showerror("Connection Failed", message)

    # Email template methods
    def on_template_select(self, event=None):
        del event

    def load_selected_template(self):
        from email_sender import EmailTemplate

        template_name = self.template_combo.get()
        if not template_name:
            messagebox.showerror("Error", "Please select a template")
            return

        db_template = self.db.get_email_template(template_name=template_name)
        if db_template:
            self.template_subject_entry.delete(0, tk.END)
            self.template_subject_entry.insert(0, db_template[2])
            self.template_body_text.delete("1.0", tk.END)
            self.template_body_text.insert("1.0", db_template[3])
            self.update_template_preview()
            messagebox.showinfo("Loaded", f"Template '{template_name}' loaded (CUSTOM VERSION)")
        else:
            template = EmailTemplate.get_template(template_name)
            if not template:
                messagebox.showerror("Error", f"Template '{template_name}' not found")
                return
            self.template_subject_entry.delete(0, tk.END)
            self.template_subject_entry.insert(0, template["subject"])
            self.template_body_text.delete("1.0", tk.END)
            self.template_body_text.insert("1.0", template["body"])
            self.update_template_preview()
            messagebox.showinfo("Loaded", f"Template '{template_name}' loaded (DEFAULT VERSION)")

    def reset_template_to_default(self):
        template_name = self.template_combo.get()
        if not template_name:
            messagebox.showerror("Error", "Please select a template first")
            return
        if messagebox.askyesno(
            "Confirm Reset", f"Reset '{template_name}' template to default?\n\nAny custom changes will be lost."
        ):
            self.load_selected_template()

    def insert_variable(self, variable):
        self.template_body_text.insert(tk.INSERT, variable)

    def update_template_preview(self):
        from email_sender import EmailTemplate
        import html
        import re

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

        self.template_preview_text.config(state="normal")
        self.template_preview_text.delete("1.0", tk.END)
        self.template_preview_text.insert("1.0", f"Subject: {preview_subject}\n\n{preview_body.strip()}")
        self.template_preview_text.config(state="disabled")

    def save_current_template(self):
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

    def send_test_template_email(self):
        settings = self.db.get_email_settings()
        if not settings:
            messagebox.showerror(
                "Error", "Email settings not configured.\n\nPlease configure email settings in the Email Settings tab first."
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
        success, message = sender.send_email(
            to_address=settings[3],
            subject=f"TEST: {rendered_subject}",
            body_html=rendered_body,
            from_name=settings[5] if len(settings) > 5 else None,
        )
        if success:
            messagebox.showinfo("Test Sent", f"Test email sent to {settings[3]}!\n\nCheck your inbox.")
        else:
            messagebox.showerror("Send Failed", message)

    def refresh_email_templates(self):
        if hasattr(self, "template_combo"):
            from email_sender import EmailTemplate

            template_names = EmailTemplate.get_template_names()
            self.template_combo["values"] = template_names
            if template_names:
                self.template_combo.set(template_names[0])
