"""
GUI Patch for Global Tasks Support
Run this to add global task functionality to gui.py
"""

def apply_patches():
    print("Applying global tasks patches to gui.py...")
    
    # Read current gui.py
    with open('gui.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    with open('gui.py.backup_global', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✓ Backup created: gui.py.backup_global")
    
    # Patch 1: Add global task checkbox variable in __init__
    if 'self.task_global_var = None' not in content:
        init_patch = '''        # Timer variables
        self.timer_running = False
        self.timer_start_time = None
        self.current_task_id = None
        
        # Daily session tracking
        self.session_date = datetime.now().date()'''
        
        init_replacement = '''        # Timer variables
        self.timer_running = False
        self.timer_start_time = None
        self.current_task_id = None
        
        # Task form variables
        self.task_global_var = None
        
        # Daily session tracking
        self.session_date = datetime.now().date()'''
        
        content = content.replace(init_patch, init_replacement)
        print("✓ Patch 1: Added task_global_var initialization")
    
    # Patch 2: Update create_task method to handle global tasks
    old_create_task = '''    def create_task(self):
        """Create a new task"""
        project_idx = self.task_project_combo.current()
        name = self.task_name_entry.get().strip()
        description = self.task_desc_entry.get().strip()

        if project_idx < 0:
            messagebox.showerror("Error", "Please select a project")
            return
        if not name:
            messagebox.showerror("Error", "Please enter a task name")
            return

        project_id = self.projects[project_idx][0]
        self.task_model.create(project_id, name, description)'''
    
    new_create_task = '''    def create_task(self):
        """Create a new task"""
        name = self.task_name_entry.get().strip()
        description = self.task_desc_entry.get().strip()
        is_global = self.task_global_var.get() if self.task_global_var else False

        if not name:
            messagebox.showerror("Error", "Please enter a task name")
            return

        if is_global:
            # Create global task
            self.task_model.create(
                name=name,
                description=description,
                is_global=True
            )
            messagebox.showinfo("Success", f"Global task '{name}' created!")
        else:
            # Create project-specific task
            project_idx = self.task_project_combo.current()
            if project_idx < 0:
                messagebox.showerror("Error", "Please select a project for non-global tasks")
                return
            
            project_id = self.projects[project_idx][0]
            self.task_model.create(
                name=name,
                description=description,
                project_id=project_id,
                is_global=False
            )
            messagebox.showinfo("Success", f"Task '{name}' created!")'''
    
    if old_create_task in content:
        content = content.replace(old_create_task, new_create_task)
        print("✓ Patch 2: Updated create_task method")
    
    # Write patched file
    with open('gui.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ Patches applied successfully!")
    print("\nNOTE: You still need to manually add the checkbox to create_tasks_tab()")
    print("See MANUAL_GUI_CHANGES.txt for instructions")
    
    # Create manual instructions
    with open('MANUAL_GUI_CHANGES.txt', 'w', encoding='utf-8') as f:
        f.write("""MANUAL GUI CHANGES NEEDED
=========================

In gui.py, find the create_tasks_tab() method.

Look for the task creation form (around line 2600-2700).

Add this code AFTER the description field:

        # Global task checkbox
        global_frame = ttk.Frame(form_frame)
        global_frame.grid(row=3, column=0, columnspan=2, sticky='w', pady=10)
        
        self.task_global_var = tk.BooleanVar(value=False)
        global_check = ttk.Checkbutton(
            global_frame,
            text="🌍 Make this a Global Task (available for all projects)",
            variable=self.task_global_var,
            command=self.toggle_task_project_field
        )
        global_check.pack(side='left')

Then add this new method anywhere in the class:

    def toggle_task_project_field(self):
        \"\"\"Enable/disable project selection based on global checkbox\"\"\"
        is_global = self.task_global_var.get()
        if is_global:
            self.task_project_combo.set('')
            self.task_project_combo.config(state='disabled')
        else:
            self.task_project_combo.config(state='readonly')

TESTING:
1. Launch app
2. Go to Tasks tab
3. Check "Make this a Global Task"
4. Create task without selecting project
5. Verify it works for all projects in Timer
""")
    print("Created MANUAL_GUI_CHANGES.txt")

if __name__ == "__main__":
    apply_patches()
