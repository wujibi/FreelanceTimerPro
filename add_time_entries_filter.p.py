import re

with open('gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the create_time_entries_tab method and add filter controls after the LabelFrame
old_entries_section = r'''        # Time entries list with grouping
        list_frame = ttk\.LabelFrame\(entries_frame, text="Time Entries \(Grouped by Client > Project > Task\)"\)
        list_frame\.pack\(fill='both', expand=True, padx=10, pady=10\)

        # Add instruction label - NO bottom padding
        instruction_label = ttk\.Label\(list_frame,'''

new_entries_section = '''        # Time entries list with grouping
        list_frame = ttk.LabelFrame(entries_frame, text="Time Entries (Grouped by Client > Project > Task)")
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Filter controls
        filter_frame = ttk.Frame(list_frame)
        filter_frame.pack(fill='x', padx=10, pady=(5, 0))

        ttk.Label(filter_frame, text="Show:", font=('Arial', 9, 'bold')).pack(side='left', padx=5)

        self.time_entries_filter_var = tk.StringVar(value="unbilled")
        ttk.Radiobutton(filter_frame, text="Unbilled Only", 
                       variable=self.time_entries_filter_var, value="unbilled",
                       command=self.refresh_time_entries).pack(side='left', padx=5)
        ttk.Radiobutton(filter_frame, text="Billed Only", 
                       variable=self.time_entries_filter_var, value="billed",
                       command=self.refresh_time_entries).pack(side='left', padx=5)
        ttk.Radiobutton(filter_frame, text="All Entries", 
                       variable=self.time_entries_filter_var, value="all",
                       command=self.refresh_time_entries).pack(side='left', padx=5)

        # Add instruction label - NO bottom padding
        instruction_label = ttk.Label(list_frame,'''

content = re.sub(old_entries_section, new_entries_section, content, flags=re.DOTALL)

# Now update refresh_time_entries to use the filter
old_get_entries = '''        # Get all time entries
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(\'\'\'
                SELECT te.id, te.client_name, te.project_name, te.task_name,
                       te.start_time, te.end_time, te.duration_minutes, te.description,
                       te.is_billed, te.invoice_number
                FROM time_entries te
                ORDER BY te.client_name, te.project_name, te.task_name, te.start_time DESC
            \'\'\')
            entries = cursor.fetchall()'''

new_get_entries = '''        # Get filter value
        filter_val = self.time_entries_filter_var.get() if hasattr(self, 'time_entries_filter_var') else 'unbilled'

        # Build WHERE clause based on filter
        where_clause = ""
        if filter_val == "unbilled":
            where_clause = "WHERE te.is_billed = 0"
        elif filter_val == "billed":
            where_clause = "WHERE te.is_billed = 1"

        # Get time entries with filter
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            query = f"""
                SELECT te.id, te.client_name, te.project_name, te.task_name,
                       te.start_time, te.end_time, te.duration_minutes, te.description,
                       te.is_billed, te.invoice_number
                FROM time_entries te
                {where_clause}
                ORDER BY te.client_name, te.project_name, te.task_name, te.start_time DESC
            """
            cursor.execute(query)
            entries = cursor.fetchall()'''

content = content.replace(old_get_entries, new_get_entries)

with open('gui.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Added filter controls to Time Entries tab!")
print("   - Unbilled Only (default)")
print("   - Billed Only")
print("   - All Entries")
