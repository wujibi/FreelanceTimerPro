"""
Code to add to gui.py for global tasks

STEP 1: Find create_tasks_tab() method
STEP 2: Find the task creation form (look for task_name_entry, task_desc_entry)
STEP 3: Add this code AFTER the description field
"""

# ADD THIS CODE IN create_tasks_tab() after description field:
"""
        # Global task checkbox
        global_frame = ttk.Frame(form_frame)
        global_frame.grid(row=3, column=0, columnspan=2, sticky='w', pady=10)
        
        self.task_global_var = tk.BooleanVar(value=False)
        global_check = ttk.Checkbutton(
            global_frame,
            text="[GLOBAL] Make this available for all projects",
            variable=self.task_global_var,
            command=self.toggle_task_project_field
        )
        global_check.pack(side='left')
"""

# ADD THIS NEW METHOD anywhere in the TimeTrackerApp class:
"""
    def toggle_task_project_field(self):
        '''Enable/disable project selection based on global checkbox'''
        is_global = self.task_global_var.get()
        if is_global:
            self.task_project_combo.set('')
            self.task_project_combo.config(state='disabled')
        else:
            self.task_project_combo.config(state='readonly')
"""

print(__doc__)
