"""CustomTkinter Company tab — invoice header fields + CTk appearance prefs."""

from __future__ import annotations

from collections.abc import Callable
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk

from models import CompanyInfo
from ui_helpers import load_ctk_ui_preferences, save_ctk_ui_preferences

_APPEARANCE_LABELS = ("System", "Light", "Dark")
_APPEARANCE_VALUES = ("system", "light", "dark")
_COLOR_THEMES = ("blue", "green", "dark-blue")


class CtkCompanyTab:
    def __init__(
        self,
        parent,
        root,
        db,
        on_appearance_applied: Callable[[], None] | None = None,
    ) -> None:
        self.parent = parent
        self.root = root
        self.db = db
        self.on_appearance_applied = on_appearance_applied
        self.company_model = CompanyInfo(self.db)

        self._build_ui()
        self.load_company_info()
        self._sync_appearance_controls()

    def _build_ui(self) -> None:
        scroll = ctk.CTkScrollableFrame(self.parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=8, pady=8)

        ctk.CTkLabel(
            scroll,
            text="Company information (for invoices)",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", pady=(0, 8))

        form = ctk.CTkFrame(scroll, fg_color="transparent")
        form.pack(fill="x")

        ctk.CTkLabel(form, text="Company name:").grid(row=0, column=0, sticky="w", pady=4)
        self.company_name_entry = ctk.CTkEntry(form, width=420)
        self.company_name_entry.grid(row=0, column=1, sticky="ew", padx=8, pady=4)

        ctk.CTkLabel(form, text="Address:").grid(row=1, column=0, sticky="nw", pady=4)
        self.company_address_text = ctk.CTkTextbox(form, width=420, height=88)
        self.company_address_text.grid(row=1, column=1, sticky="ew", padx=8, pady=4)

        ctk.CTkLabel(form, text="Phone:").grid(row=2, column=0, sticky="w", pady=4)
        self.company_phone_entry = ctk.CTkEntry(form, width=420)
        self.company_phone_entry.grid(row=2, column=1, sticky="ew", padx=8, pady=4)

        ctk.CTkLabel(form, text="Email:").grid(row=3, column=0, sticky="w", pady=4)
        self.company_email_entry = ctk.CTkEntry(form, width=420)
        self.company_email_entry.grid(row=3, column=1, sticky="ew", padx=8, pady=4)

        ctk.CTkLabel(form, text="Logo:").grid(row=4, column=0, sticky="w", pady=4)
        logo_row = ctk.CTkFrame(form, fg_color="transparent")
        logo_row.grid(row=4, column=1, sticky="ew", padx=8, pady=4)
        self.logo_path_var = tk.StringVar()
        self.logo_entry = ctk.CTkEntry(logo_row, textvariable=self.logo_path_var, width=320, state="readonly")
        self.logo_entry.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(logo_row, text="Browse", width=88, command=self.browse_logo).pack(side="left", padx=(8, 0))

        ctk.CTkLabel(form, text="Website:").grid(row=5, column=0, sticky="w", pady=4)
        self.company_website_entry = ctk.CTkEntry(form, width=420)
        self.company_website_entry.grid(row=5, column=1, sticky="ew", padx=8, pady=4)

        ctk.CTkLabel(form, text="Payment terms:").grid(row=6, column=0, sticky="w", pady=4)
        self.company_payment_terms_entry = ctk.CTkEntry(form, width=420)
        self.company_payment_terms_entry.grid(row=6, column=1, sticky="ew", padx=8, pady=4)

        ctk.CTkLabel(form, text="Thank you message:").grid(row=7, column=0, sticky="w", pady=4)
        self.company_thank_you_entry = ctk.CTkEntry(form, width=420)
        self.company_thank_you_entry.grid(row=7, column=1, sticky="ew", padx=8, pady=4)

        form.columnconfigure(1, weight=1)

        actions = ctk.CTkFrame(scroll, fg_color="transparent")
        actions.pack(fill="x", pady=(12, 0))
        ctk.CTkButton(actions, text="Save company info", command=self.save_company_info).pack(side="left", padx=4)
        ctk.CTkButton(actions, text="Load current info", command=self.load_company_info).pack(side="left", padx=4)

        ctk.CTkLabel(
            scroll,
            text="Appearance",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", pady=(20, 8))
        ctk.CTkLabel(
            scroll,
            text="Light or dark mode and accent theme for this window.",
            wraplength=640,
            justify="left",
            text_color=("gray35", "gray65"),
            font=ctk.CTkFont(size=12),
        ).pack(anchor="w", pady=(0, 8))

        theme_row = ctk.CTkFrame(scroll, fg_color="transparent")
        theme_row.pack(fill="x")

        ctk.CTkLabel(theme_row, text="Mode:").pack(side="left", padx=(0, 8))
        self.appearance_combo = ctk.CTkComboBox(
            theme_row,
            values=list(_APPEARANCE_LABELS),
            width=140,
            state="readonly",
        )
        self.appearance_combo.pack(side="left", padx=4)

        ctk.CTkLabel(theme_row, text="Color theme:").pack(side="left", padx=(16, 8))
        self.color_theme_combo = ctk.CTkComboBox(
            theme_row,
            values=list(_COLOR_THEMES),
            width=140,
            state="readonly",
        )
        self.color_theme_combo.pack(side="left", padx=4)

        ctk.CTkButton(theme_row, text="Apply", width=100, command=self.apply_ctk_appearance).pack(side="left", padx=12)

    def _sync_appearance_controls(self) -> None:
        mode, color_theme = load_ctk_ui_preferences(self.db.db_path)
        mode_label = _APPEARANCE_LABELS[_APPEARANCE_VALUES.index(mode)] if mode in _APPEARANCE_VALUES else "System"
        self.appearance_combo.set(mode_label)
        self.color_theme_combo.set(color_theme if color_theme in _COLOR_THEMES else "blue")

    def browse_logo(self) -> None:
        filename = filedialog.askopenfilename(
            title="Select logo image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")],
        )
        if filename:
            self.logo_path_var.set(filename)

    def save_company_info(self) -> None:
        name = self.company_name_entry.get().strip()
        address = self.company_address_text.get("1.0", "end-1c").strip()
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
            messagebox.showerror("Error", f"Failed to save company info: {e}")

    def load_company_info(self) -> None:
        company = self.company_model.get()
        if not company:
            return

        self.company_name_entry.delete(0, "end")
        self.company_name_entry.insert(0, company[1])

        self.company_address_text.delete("1.0", "end")
        self.company_address_text.insert("1.0", company[2] or "")

        self.company_phone_entry.delete(0, "end")
        self.company_phone_entry.insert(0, company[3] or "")

        self.company_email_entry.delete(0, "end")
        self.company_email_entry.insert(0, company[4] or "")

        if len(company) > 5 and company[5]:
            self.logo_path_var.set(company[5])
        else:
            self.logo_path_var.set("")

        if len(company) > 6 and company[6]:
            self.company_website_entry.delete(0, "end")
            self.company_website_entry.insert(0, company[6])
        else:
            self.company_website_entry.delete(0, "end")

        if len(company) > 7 and company[7]:
            self.company_payment_terms_entry.delete(0, "end")
            self.company_payment_terms_entry.insert(0, company[7])
        else:
            self.company_payment_terms_entry.delete(0, "end")
            self.company_payment_terms_entry.insert(0, "Payment is due within 30 days")

        if len(company) > 8 and company[8]:
            self.company_thank_you_entry.delete(0, "end")
            self.company_thank_you_entry.insert(0, company[8])
        else:
            self.company_thank_you_entry.delete(0, "end")
            self.company_thank_you_entry.insert(0, "Thank you for your business!")

    def apply_ctk_appearance(self) -> None:
        label = self.appearance_combo.get()
        try:
            idx = list(_APPEARANCE_LABELS).index(label)
            mode = _APPEARANCE_VALUES[idx]
        except ValueError:
            mode = "system"

        color_theme = self.color_theme_combo.get()
        if color_theme not in _COLOR_THEMES:
            color_theme = "blue"

        ctk.set_appearance_mode(mode)
        ctk.set_default_color_theme(color_theme)
        save_ctk_ui_preferences(self.db.db_path, mode, color_theme)
        if self.on_appearance_applied:
            self.on_appearance_applied()
        messagebox.showinfo(
            "Appearance",
            "Settings saved.\n"
            "If colors look off, restart the app once for a full theme refresh.",
        )
