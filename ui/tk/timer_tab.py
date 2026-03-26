from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from datetime import datetime


class TimerTabMixin:
    def create_timer_tab(self):
        """Create Timer tab with Active Timer and Manual Entry subviews"""
        timer_frame = ttk.Frame(self.notebook)
        self.notebook.add(timer_frame, text="Timer")

        # Submenu bar at top
        submenu_frame = ttk.Frame(timer_frame)
        submenu_frame.pack(fill="x", padx=10, pady=(10, 0))

        ttk.Label(submenu_frame, text="View:", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        ttk.Button(
            submenu_frame,
            text="⏱️ Active Timer",
            command=lambda: self.show_timer_view("active"),
        ).pack(side="left", padx=2)
        ttk.Button(
            submenu_frame,
            text="📝 Manual Entry",
            command=lambda: self.show_timer_view("manual"),
        ).pack(side="left", padx=2)

        # Container for switching views
        self.timer_view_container = ttk.Frame(timer_frame)
        self.timer_view_container.pack(fill="both", expand=True)

        # Create both views
        self.create_active_timer_view()
        self.create_manual_entry_view()

        # Show active timer by default
        self.show_timer_view("active")

    def show_timer_view(self, view_type):
        """Switch between timer views"""
        for widget in self.timer_view_container.winfo_children():
            widget.pack_forget()

        if view_type == "active":
            self.active_timer_frame.pack(fill="both", expand=True)
        else:
            self.manual_entry_frame.pack(fill="both", expand=True)

    def create_active_timer_view(self):
        """Create Active Timer view"""
        self.active_timer_frame = ttk.Frame(self.timer_view_container)

        # Timer display
        timer_display_frame = ttk.LabelFrame(self.active_timer_frame, text="Active Timer")
        timer_display_frame.pack(fill="x", padx=10, pady=10)

        self.timer_label = ttk.Label(timer_display_frame, text="00:00:00", font=self.fonts["large_display"])
        self.timer_label.pack(pady=10)

        # Client, Project, and Task selection
        selection_frame = ttk.Frame(timer_display_frame)
        selection_frame.pack(fill="x", padx=10, pady=5)

        # Client selection
        client_frame = ttk.Frame(selection_frame)
        client_frame.pack(fill="x", pady=2)

        ttk.Label(client_frame, text="Client:").pack(side="left")
        self.timer_client_combo = ttk.Combobox(client_frame, state="readonly")
        self.timer_client_combo.pack(side="left", fill="x", expand=True, padx=5)
        self.timer_client_combo.bind("<<ComboboxSelected>>", self.on_timer_client_select)

        # Project selection
        project_frame = ttk.Frame(selection_frame)
        project_frame.pack(fill="x", pady=2)

        ttk.Label(project_frame, text="Project:").pack(side="left")
        self.timer_project_combo = ttk.Combobox(project_frame, state="readonly")
        self.timer_project_combo.pack(side="left", fill="x", expand=True, padx=5)
        self.timer_project_combo.bind("<<ComboboxSelected>>", self.on_timer_project_select)

        # Task selection
        task_frame = ttk.Frame(selection_frame)
        task_frame.pack(fill="x", pady=2)

        ttk.Label(task_frame, text="Task:").pack(side="left")
        self.timer_task_combo = ttk.Combobox(task_frame, state="readonly")
        self.timer_task_combo.pack(side="left", fill="x", expand=True, padx=5)

        # Timer buttons
        button_frame = ttk.Frame(timer_display_frame)
        button_frame.pack(pady=10)

        self.start_button = ttk.Button(button_frame, text="Start Timer", command=self.start_timer)
        self.start_button.pack(side="left", padx=5)

        self.stop_button = ttk.Button(
            button_frame,
            text="Stop Timer",
            command=self.stop_timer,
            state="disabled",
        )
        self.stop_button.pack(side="left", padx=5)

        # Daily Totals Section (moved up for better visibility)
        daily_frame = ttk.LabelFrame(self.active_timer_frame, text="Today's Time by Client")
        daily_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Text widget for displaying daily totals
        daily_text_frame = ttk.Frame(daily_frame)
        daily_text_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.daily_totals_text = tk.Text(
            daily_text_frame,
            height=12,
            wrap="word",
            font=("Courier", 10),
            state="disabled",
        )
        self.daily_totals_text.pack(side="left", fill="both", expand=True)

        # Scrollbar for daily totals
        daily_scrollbar = ttk.Scrollbar(daily_text_frame, command=self.daily_totals_text.yview)
        daily_scrollbar.pack(side="right", fill="y")
        self.daily_totals_text.config(yscrollcommand=daily_scrollbar.set)

        # Buttons for daily totals
        daily_button_frame = ttk.Frame(daily_frame)
        daily_button_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(daily_button_frame, text="Refresh Totals", command=self.update_daily_totals_display).pack(
            side="left", padx=5
        )
        ttk.Button(daily_button_frame, text="Reset Daily Totals", command=self.reset_daily_totals).pack(
            side="left", padx=5
        )

    def create_manual_entry_view(self):
        """Create Manual Entry view"""
        self.manual_entry_frame = ttk.Frame(self.timer_view_container)

        # Manual time entry section
        manual_frame = ttk.LabelFrame(self.manual_entry_frame, text="Manual Time Entry")
        manual_frame.pack(fill="both", expand=True, padx=10, pady=10)

        form_frame = ttk.Frame(manual_frame)
        form_frame.pack(fill="x", padx=10, pady=10)

        # Date
        ttk.Label(form_frame, text="Date (MM/DD/YY):").grid(row=0, column=0, sticky="w", pady=2)
        self.manual_date_entry = ttk.Entry(form_frame)
        self.manual_date_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        self.manual_date_entry.insert(0, datetime.now().strftime("%m/%d/%y"))

        # Entry mode selection (Start/End Time OR Decimal Hours)
        ttk.Label(form_frame, text="Entry Mode:").grid(row=1, column=0, sticky="w", pady=2)
        mode_frame = ttk.Frame(form_frame)
        mode_frame.grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        self.manual_entry_mode = tk.StringVar(value="time_range")
        ttk.Radiobutton(
            mode_frame,
            text="Start/End Time",
            variable=self.manual_entry_mode,
            value="time_range",
            command=self.toggle_manual_entry_mode,
        ).pack(side="left")
        ttk.Radiobutton(
            mode_frame,
            text="Decimal Hours",
            variable=self.manual_entry_mode,
            value="decimal",
            command=self.toggle_manual_entry_mode,
        ).pack(side="left", padx=10)

        # Start Time
        ttk.Label(form_frame, text="Start Time (HH:MM AM/PM):").grid(row=2, column=0, sticky="w", pady=2)
        self.manual_start_entry = ttk.Entry(form_frame)
        self.manual_start_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        self.manual_start_entry.insert(0, "09:00 AM")

        # End Time
        ttk.Label(form_frame, text="End Time (HH:MM AM/PM):").grid(row=3, column=0, sticky="w", pady=2)
        self.manual_end_entry = ttk.Entry(form_frame)
        self.manual_end_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=2)
        self.manual_end_entry.insert(0, "05:00 PM")

        # Decimal Hours (hidden by default)
        self.manual_decimal_label = ttk.Label(form_frame, text="Hours (decimal):")
        self.manual_decimal_label.grid(row=4, column=0, sticky="w", pady=2)
        self.manual_decimal_label.grid_remove()  # Hide initially

        self.manual_decimal_entry = ttk.Entry(form_frame)
        self.manual_decimal_entry.grid(row=4, column=1, sticky="ew", padx=5, pady=2)
        self.manual_decimal_entry.grid_remove()  # Hide initially

        # Helper text for decimal entry
        self.manual_decimal_help = ttk.Label(
            form_frame,
            text="Examples: 1.5, 0.75, 2.25",
            font=("Arial", 8),
            foreground="gray",
        )
        self.manual_decimal_help.grid(row=5, column=1, sticky="w", padx=5)
        self.manual_decimal_help.grid_remove()  # Hide initially

        # CLIENT SELECTION (for global tasks)
        ttk.Label(form_frame, text="Client:").grid(row=6, column=0, sticky="w", pady=2)
        self.manual_client_combo = ttk.Combobox(form_frame, state="readonly")
        self.manual_client_combo.grid(row=6, column=1, sticky="ew", padx=5, pady=2)
        self.manual_client_combo.bind("<<ComboboxSelected>>", self.on_manual_client_select)

        # PROJECT SELECTION (for global tasks)
        ttk.Label(form_frame, text="Project:").grid(row=7, column=0, sticky="w", pady=2)
        self.manual_project_combo = ttk.Combobox(form_frame, state="readonly")
        self.manual_project_combo.grid(row=7, column=1, sticky="ew", padx=5, pady=2)
        self.manual_project_combo.bind("<<ComboboxSelected>>", self.on_manual_project_select)

        # Task
        ttk.Label(form_frame, text="Task:").grid(row=8, column=0, sticky="w", pady=2)
        self.manual_task_combo = ttk.Combobox(form_frame, state="readonly")
        self.manual_task_combo.grid(row=8, column=1, sticky="ew", padx=5, pady=2)

        # Description
        ttk.Label(form_frame, text="Description:").grid(row=9, column=0, sticky="nw", pady=2)
        self.manual_desc_text = tk.Text(form_frame, height=3)
        self.manual_desc_text.grid(row=9, column=1, sticky="ew", padx=5, pady=2)

        form_frame.columnconfigure(1, weight=1)

        # Manual entry buttons
        manual_button_frame = ttk.Frame(manual_frame)
        manual_button_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(manual_button_frame, text="Add Entry", command=self.add_manual_entry).pack(side="left", padx=5)
        ttk.Button(manual_button_frame, text="Clear", command=self.clear_manual_entry_form).pack(side="left", padx=5)

        # Daily Totals Section (replicated for convenience)
        manual_daily_frame = ttk.LabelFrame(self.manual_entry_frame, text="Today's Time by Client")
        manual_daily_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Text widget for displaying daily totals
        manual_daily_text_frame = ttk.Frame(manual_daily_frame)
        manual_daily_text_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.manual_daily_totals_text = tk.Text(
            manual_daily_text_frame,
            height=10,
            wrap="word",
            font=("Courier", 10),
            state="disabled",
        )
        self.manual_daily_totals_text.pack(side="left", fill="both", expand=True)

        # Scrollbar for daily totals
        manual_daily_scrollbar = ttk.Scrollbar(manual_daily_text_frame, command=self.manual_daily_totals_text.yview)
        manual_daily_scrollbar.pack(side="right", fill="y")
        self.manual_daily_totals_text.config(yscrollcommand=manual_daily_scrollbar.set)

        # Buttons for daily totals
        manual_daily_button_frame = ttk.Frame(manual_daily_frame)
        manual_daily_button_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(
            manual_daily_button_frame,
            text="Refresh Totals",
            command=self.update_daily_totals_display,
        ).pack(side="left", padx=5)
        ttk.Button(
            manual_daily_button_frame,
            text="Reset Daily Totals",
            command=self.reset_daily_totals,
        ).pack(side="left", padx=5)

