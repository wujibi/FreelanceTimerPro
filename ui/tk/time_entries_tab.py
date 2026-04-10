from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox


class TimeEntriesTabMixin:
    def create_time_entries_tab(self):
        # Time entries tab
        entries_frame = ttk.Frame(self.notebook)
        self.notebook.add(entries_frame, text="Time Entries")

        # Time entries list with grouping
        list_frame = ttk.LabelFrame(entries_frame, text="Time Entries (Grouped by Client > Project > Task)")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Filter controls
        filter_frame = ttk.Frame(list_frame)
        filter_frame.pack(fill="x", padx=10, pady=(5, 0))

        ttk.Label(filter_frame, text="Show:", font=("Arial", 9, "bold")).pack(side="left", padx=5)

        self.time_entries_filter_var = tk.StringVar(value="unbilled")
        ttk.Radiobutton(
            filter_frame,
            text="✅ Unbilled Only",
            variable=self.time_entries_filter_var,
            value="unbilled",
            command=self.refresh_time_entries,
        ).pack(side="left", padx=5)
        ttk.Radiobutton(
            filter_frame,
            text="💰 Billed Only",
            variable=self.time_entries_filter_var,
            value="billed",
            command=self.refresh_time_entries,
        ).pack(side="left", padx=5)
        ttk.Radiobutton(
            filter_frame,
            text="📋 All Entries",
            variable=self.time_entries_filter_var,
            value="all",
            command=self.refresh_time_entries,
        ).pack(side="left", padx=5)

        # Add instruction label - NO bottom padding
        instruction_label = ttk.Label(
            list_frame,
            text="💡 Click the ▶ arrows to expand/collapse groups and view individual entries with descriptions",
            font=("Arial", 9, "italic"),
            foreground="#666",
        )
        instruction_label.pack(anchor="w", padx=10, pady=(3, 3))

        # Entry buttons - MINIMAL spacing
        entry_button_frame = ttk.Frame(list_frame)
        entry_button_frame.pack(fill="x", padx=10, pady=(0, 5))

        ttk.Button(
            entry_button_frame,
            text="⚠️ Use Invoices Tab Instead",
            command=lambda: messagebox.showinfo(
                "Use Invoices Tab",
                "Please use the 'Invoices' tab for generating invoices.\n\n"
                + "The new Invoices tab has better filtering and preview features!",
            ),
            state="disabled",
        ).pack(side="left", padx=5)
        ttk.Button(entry_button_frame, text="Edit Entry", command=self.edit_time_entry).pack(side="left", padx=5)
        ttk.Button(entry_button_frame, text="Delete Entry", command=self.delete_time_entry).pack(side="left", padx=5)
        ttk.Button(entry_button_frame, text="📊 Export to Excel", command=self.export_time_entries_to_excel).pack(
            side="left", padx=5
        )

        # Create a frame for tree and scrollbar IMMEDIATELY after buttons
        tree_container = ttk.Frame(list_frame)
        tree_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Create tree with hierarchical display
        self.entries_tree = ttk.Treeview(
            tree_container,
            columns=("Name", "Duration", "Description"),
            selectmode="extended",
        )

        # Configure columns
        self.entries_tree.heading("#0", text="Hierarchy")  # Tree column
        self.entries_tree.heading("Name", text="Details")
        self.entries_tree.heading("Duration", text="Duration")
        self.entries_tree.heading("Description", text="Description")

        self.entries_tree.column("#0", width=250)  # Tree hierarchy column
        self.entries_tree.column("Name", width=220)
        self.entries_tree.column("Duration", width=100)
        self.entries_tree.column("Description", width=360)

        # Add scrollbar
        tree_scroll = ttk.Scrollbar(tree_container, orient="vertical", command=self.entries_tree.yview)
        self.entries_tree.configure(yscrollcommand=tree_scroll.set)

        self.entries_tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")

        # Configure alternating row colors for ledger-style display
        # Check if we're using a dark theme (dark background) or light theme (white background)
        if self.colors["background"] == "#ffffff":  # Light theme
            # Light theme: white and very light blue alternating
            self.entries_tree.tag_configure(
                "oddrow",
                background=self.colors.get("alt_row", "#f0f4ff"),
                foreground=self.colors["text"],
            )  # Light blue tint
            self.entries_tree.tag_configure("evenrow", background="white", foreground=self.colors["text"])  # White
        else:  # Dark theme
            # Dark theme: navy and white alternating
            self.entries_tree.tag_configure("oddrow", background=self.colors["background"], foreground="white")
            self.entries_tree.tag_configure("evenrow", background="white", foreground=self.colors["background"])

        # Configure group heading colors (Client/Project/Task rows)
        if "group_heading" in self.colors:
            # Use theme-specific group heading color
            self.entries_tree.tag_configure(
                "client_row",
                background=self.colors["group_heading"],
                foreground=self.colors.get("group_text", "white"),
                font=self.fonts["subheading"],
            )

            self.entries_tree.tag_configure(
                "project_row",
                background=self.colors["group_heading"],
                foreground=self.colors.get("group_text", "white"),
                font=self.fonts["body"],
            )

            self.entries_tree.tag_configure(
                "task_row",
                background=self.colors["group_heading"],
                foreground=self.colors.get("group_text", "white"),
                font=self.fonts["body"],
            )
        else:
            # Fallback for themes without group_heading color
            self.entries_tree.tag_configure(
                "client_row",
                background="#e8f4f8",
                foreground="#13100f",
                font=self.fonts["subheading"],
            )

            self.entries_tree.tag_configure(
                "project_row",
                background="#e8f4f8",
                foreground="#13100f",
                font=self.fonts["body"],
            )

            self.entries_tree.tag_configure(
                "task_row",
                background="#e8f4f8",
                foreground="#13100f",
                font=self.fonts["body"],
            )

        # Configure entry rows (individual time entries) - always white with dark text
        self.entries_tree.tag_configure(
            "entry_row",
            background="white",
            foreground=self.colors["text"],
            font=self.fonts["body"],
        )

