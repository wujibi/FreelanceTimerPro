"""
Script to update the load_invoiceable_entries function in gui.py
This adds Project -> Task grouping to the Invoice tab entry list
"""

def update_gui_file():
    # Read the original file
    with open('gui.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the function start
    func_start = content.find('    def load_invoiceable_entries(self):')
    if func_start == -1:
        print("ERROR: Could not find load_invoiceable_entries function")
        return False
    
    # Find the next function after this one (it starts with "    def ")
    search_from = func_start + 100  # Skip past the function definition line
    next_func = content.find('\n    def ', search_from)
    
    if next_func == -1:
        print("ERROR: Could not find end of function")
        return False
    
    print(f"Found function at position {func_start}")
    print(f"Next function starts at position {next_func}")
    
    # The new function implementation
    new_function = '''    def load_invoiceable_entries(self):
        """Load unbilled time entries based on selected client/project/date filter"""
        client_name = self.invoice_client_combo.get()
        if not client_name:
            messagebox.showerror("Error", "Please select a client first")
            return
        
        # Get client ID
        clients = self.client_model.get_all()
        client_id = None
        for client in clients:
            if client[1] == client_name:
                client_id = client[0]
                break
        
        if not client_id:
            messagebox.showerror("Error", "Invalid client selected")
            return
        
        # Get project filter
        project_name = self.invoice_project_combo.get()
        project_id = None
        if project_name and project_name != 'All Projects':
            projects = self.project_model.get_by_client(client_id)
            for project in projects:
                if project[2] == project_name:
                    project_id = project[0]
                    break
        
        # Build query based on filter
        conn = self.db.conn  # Use direct connection, not context manager
        cursor = conn.cursor()
        
        if self.invoice_filter_var.get() == "all_uninvoiced":
            # All unbilled entries for client
            if project_id:
                cursor.execute(\'\'\'
                    SELECT te.id, te.start_time, te.description, te.duration_minutes,
                           p.name as project_name, t.name as task_name
                    FROM time_entries te
                    JOIN tasks t ON te.task_id = t.id
                    JOIN projects p ON te.project_id = p.id
                    WHERE p.client_id = ? AND p.id = ? AND (te.is_billed = 0 OR te.is_billed IS NULL)
                    ORDER BY te.start_time DESC
                \'\'\', (client_id, project_id))
            else:
                cursor.execute(\'\'\'
                    SELECT te.id, te.start_time, te.description, te.duration_minutes,
                           p.name as project_name, t.name as task_name
                    FROM time_entries te
                    JOIN tasks t ON te.task_id = t.id
                    JOIN projects p ON te.project_id = p.id
                    WHERE p.client_id = ? AND (te.is_billed = 0 OR te.is_billed IS NULL)
                    ORDER BY te.start_time DESC
                \'\'\', (client_id,))
        else:
            # Date range filter
            try:
                start_date = datetime.strptime(self.invoice_start_date.get(), "%m/%d/%y")
                end_date = datetime.strptime(self.invoice_end_date.get(), "%m/%d/%y")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use MM/DD/YY")
                return
            
            if project_id:
                cursor.execute(\'\'\'
                    SELECT te.id, te.start_time, te.description, te.duration_minutes,
                           p.name as project_name, t.name as task_name
                    FROM time_entries te
                    JOIN tasks t ON te.task_id = t.id
                    JOIN projects p ON te.project_id = p.id
                    WHERE p.client_id = ? AND p.id = ? 
                          AND DATE(te.start_time) BETWEEN ? AND ?
                          AND (te.is_billed = 0 OR te.is_billed IS NULL)
                    ORDER BY te.start_time DESC
                \'\'\', (client_id, project_id, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
            else:
                cursor.execute(\'\'\'
                    SELECT te.id, te.start_time, te.description, te.duration_minutes,
                           p.name as project_name, t.name as task_name
                    FROM time_entries te
                    JOIN tasks t ON te.task_id = t.id
                    JOIN projects p ON te.project_id = p.id
                    WHERE p.client_id = ? 
                          AND DATE(te.start_time) BETWEEN ? AND ?
                          AND (te.is_billed = 0 OR te.is_billed IS NULL)
                    ORDER BY te.start_time DESC
                \'\'\', (client_id, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
        
        entries = cursor.fetchall()
        
        # Clear existing entries
        for item in self.invoice_entries_tree.get_children():
            self.invoice_entries_tree.delete(item)
        
        # Group by Project -> Task for better organization
        project_groups = {}  # {project_name: {task_name: [entries]}}
        
        for entry in entries:
            entry_id, start_time, description, duration_minutes, project_name, task_name = entry
            
            if project_name not in project_groups:
                project_groups[project_name] = {}
            if task_name not in project_groups[project_name]:
                project_groups[project_name][task_name] = []
            
            project_groups[project_name][task_name].append(entry)
        
        # Populate tree with hierarchy
        total_hours = 0
        total_entries = 0
        
        for project_name in sorted(project_groups.keys()):
            # Calculate project totals
            project_hours = 0
            project_entry_count = 0
            for task_name in project_groups[project_name]:
                for entry in project_groups[project_name][task_name]:
                    project_hours += (entry[3] or 0) / 60.0
                    project_entry_count += 1
            
            # Insert project header
            project_node = self.invoice_entries_tree.insert('', 'end',
                text=f'📁 {project_name}',
                values=('', '', '', f'{project_hours:.2f} hrs', f'{project_entry_count} entries'),
                tags=('project',))
            
            # Add tasks under project
            for task_name in sorted(project_groups[project_name].keys()):
                task_entries = project_groups[project_name][task_name]
                
                # Calculate task total
                task_hours = sum((e[3] or 0) / 60.0 for e in task_entries)
                
                # Insert task header
                task_node = self.invoice_entries_tree.insert(project_node, 'end',
                    text=f'  📋 {task_name}',
                    values=('', '', '', f'{task_hours:.2f} hrs', f'{len(task_entries)} entries'),
                    tags=('task',))
                
                # Add individual entries under task
                for entry in task_entries:
                    entry_id, start_time, description, duration_minutes, _, _ = entry
                    
                    # Format date
                    try:
                        dt = datetime.fromisoformat(start_time)
                        date_display = dt.strftime("%m/%d/%y %I:%M %p")
                    except:
                        date_display = start_time[:10]
                    
                    hours = (duration_minutes or 0) / 60.0
                    total_hours += hours
                    total_entries += 1
                    
                    # Insert entry (selectable)
                    self.invoice_entries_tree.insert(task_node, 'end',
                        text='    ⏱️',
                        values=(date_display, '', '', f'{hours:.2f} hrs', description or ''),
                        tags=(f'entry_id_{entry_id}', 'entry'))
        
        # Configure tag styles
        self.invoice_entries_tree.tag_configure('project', font=('Arial', 10, 'bold'))
        self.invoice_entries_tree.tag_configure('task', font=('Arial', 9, 'bold'))
        self.invoice_entries_tree.tag_configure('entry', font=('Arial', 9))
        
        # Update summary
        self.invoice_summary_label.config(
            text=f"📊 {total_entries} unbilled entries found | Total: {total_hours:.2f} hours")

'''
    
    # Replace the old function with the new one
    new_content = content[:func_start] + new_function + content[next_func:]
    
    # Create backup
    with open('gui.py.backup_invoice_grouped', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✓ Backup created: gui.py.backup_invoice_grouped")
    
    # Write the updated file
    with open('gui.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("✓ gui.py updated successfully")
    
    return True

if __name__ == '__main__':
    print("Updating load_invoiceable_entries function in gui.py...")
    print("-" * 60)
    
    success = update_gui_file()
    
    if success:
        print("-" * 60)
        print("✓ Update complete!")
        print("\nChanges made:")
        print("  • Invoice tab now shows entries grouped by Project → Task")
        print("  • Matches the hierarchy in Time Entries tab and invoice preview")
        print("  • Shows totals for each project and task")
        print("\nBackup saved as: gui.py.backup_invoice_grouped")
    else:
        print("-" * 60)
        print("✗ Update failed - check error messages above")
