from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from themes import AVAILABLE_THEMES


class CompanyTabMixin:
    def create_company_tab(self):
        # Company info tab
        company_frame = ttk.Frame(self.notebook)
        self.notebook.add(company_frame, text="Company Info")

        # Company form
        company_form = ttk.LabelFrame(company_frame, text="Company Information (For Invoices)")
        company_form.pack(fill="both", expand=True, padx=10, pady=10)

        form_frame = ttk.Frame(company_form)
        form_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(form_frame, text="Company Name:").grid(row=0, column=0, sticky="w", pady=2)
        self.company_name_entry = ttk.Entry(form_frame)
        self.company_name_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(form_frame, text="Address:").grid(row=1, column=0, sticky="nw", pady=2)
        self.company_address_text = tk.Text(form_frame, height=3)
        self.company_address_text.grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(form_frame, text="Phone:").grid(row=2, column=0, sticky="w", pady=2)
        self.company_phone_entry = ttk.Entry(form_frame)
        self.company_phone_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(form_frame, text="Email:").grid(row=3, column=0, sticky="w", pady=2)
        self.company_email_entry = ttk.Entry(form_frame)
        self.company_email_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(form_frame, text="Logo:").grid(row=4, column=0, sticky="w", pady=2)
        logo_frame = ttk.Frame(form_frame)
        logo_frame.grid(row=4, column=1, sticky="ew", padx=5, pady=2)

        self.logo_path_var = tk.StringVar()
        ttk.Entry(logo_frame, textvariable=self.logo_path_var, state="readonly").pack(
            side="left", fill="x", expand=True
        )
        ttk.Button(logo_frame, text="Browse", command=self.browse_logo).pack(side="left", padx=5)

        # Website
        ttk.Label(form_frame, text="Website:").grid(row=5, column=0, sticky="w", pady=2)
        self.company_website_entry = ttk.Entry(form_frame)
        self.company_website_entry.grid(row=5, column=1, sticky="ew", padx=5, pady=2)

        # Payment Terms
        ttk.Label(form_frame, text="Payment Terms:").grid(row=6, column=0, sticky="w", pady=2)
        self.company_payment_terms_entry = ttk.Entry(form_frame, width=50)
        self.company_payment_terms_entry.grid(row=6, column=1, sticky="ew", padx=5, pady=2)

        # Thank You Message
        ttk.Label(form_frame, text="Thank You Message:").grid(row=7, column=0, sticky="w", pady=2)
        self.company_thank_you_entry = ttk.Entry(form_frame, width=50)
        self.company_thank_you_entry.grid(row=7, column=1, sticky="ew", padx=5, pady=2)

        form_frame.columnconfigure(1, weight=1)

        # Company buttons
        button_frame = ttk.Frame(company_form)
        button_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(button_frame, text="Save Company Info", command=self.save_company_info).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Load Current Info", command=self.load_company_info).pack(side="left", padx=5)

        # Theme selector
        theme_frame = ttk.LabelFrame(company_form, text="🎨 Appearance")
        theme_frame.pack(fill="x", padx=10, pady=10)

        theme_inner = ttk.Frame(theme_frame)
        theme_inner.pack(fill="x", padx=10, pady=10)

        ttk.Label(theme_inner, text="Theme:").pack(side="left", padx=5)

        self.theme_combo = ttk.Combobox(theme_inner, state="readonly", width=25)
        self.theme_combo["values"] = list(AVAILABLE_THEMES.keys())
        # Set to current theme
        current_theme_name = [name for name, module in AVAILABLE_THEMES.items() if module == self.current_theme]
        self.theme_combo.set(current_theme_name[0] if current_theme_name else "Professional Gray")
        self.theme_combo.pack(side="left", padx=5)

        ttk.Button(
            theme_inner,
            text="Apply Theme",
            command=lambda: self.switch_theme(self.theme_combo.get()),
        ).pack(side="left", padx=5)
