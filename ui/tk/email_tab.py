from __future__ import annotations

import tkinter as tk
from tkinter import ttk


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
