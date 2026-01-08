with open('models.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the start_timer method to handle global tasks
old_start_timer = '''    def start_timer(self, task_id, description=""):
        # Stop any existing timer first
        if self.current_entry:
            self.stop_timer()

        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # Get task, project, and client info for the entry
            cursor.execute(\'\'\'
                           SELECT t.name, p.id, p.name, c.id, c.name
                           FROM tasks t
                                    JOIN projects p ON t.project_id = p.id
                                    JOIN clients c ON p.client_id = c.id
                           WHERE t.id = ?
                           \'\'\', (task_id,))

            task_info = cursor.fetchone()
            if not task_info:
                raise ValueError("Task not found")

            task_name, project_id, project_name, client_id, client_name = task_info
            start_time = datetime.now()
            date_str = start_time.strftime('%Y-%m-%d')

            cursor.execute(\'\'\'
                           INSERT INTO time_entries (task_id, task_name, project_id, project_name,
                                                     client_id, client_name, date, start_time,
                                                     description, is_manual, is_billed)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0)
                           \'\'\', (task_id, task_name, project_id, project_name,
                                 client_id, client_name, date_str, start_time.isoformat(), description))
            conn.commit()  # ADDED
            self.current_entry = cursor.lastrowid
            return self.current_entry'''

new_start_timer = '''    def start_timer(self, task_id, description="", project_id_override=None):
        """Start a timer for a task. Handles both project-specific and global tasks."""
        # Stop any existing timer first
        if self.current_entry:
            self.stop_timer()

        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # First check if task is global
            cursor.execute('SELECT is_global FROM tasks WHERE id = ?', (task_id,))
            task_result = cursor.fetchone()
            if not task_result:
                raise ValueError("Task not found")

            is_global = task_result[0]

            if is_global:
                # For global tasks, use the provided project_id_override
                if not project_id_override:
                    raise ValueError("Global tasks require a project context")

                cursor.execute(\'\'\'
                               SELECT t.name, p.id, p.name, c.id, c.name
                               FROM tasks t, projects p
                               JOIN clients c ON p.client_id = c.id
                               WHERE t.id = ? AND p.id = ?
                               \'\'\', (task_id, project_id_override))
            else:
                # Regular project-specific task
                cursor.execute(\'\'\'
                               SELECT t.name, p.id, p.name, c.id, c.name
                               FROM tasks t
                               JOIN projects p ON t.project_id = p.id
                               JOIN clients c ON p.client_id = c.id
                               WHERE t.id = ?
                               \'\'\', (task_id,))

            task_info = cursor.fetchone()
            if not task_info:
                raise ValueError("Task not found")

            task_name, project_id, project_name, client_id, client_name = task_info
            start_time = datetime.now()
            date_str = start_time.strftime('%Y-%m-%d')

            cursor.execute(\'\'\'
                           INSERT INTO time_entries (task_id, task_name, project_id, project_name,
                                                     client_id, client_name, date, start_time,
                                                     description, is_manual, is_billed)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0)
                           \'\'\', (task_id, task_name, project_id, project_name,
                                 client_id, client_name, date_str, start_time.isoformat(), description))
            conn.commit()
            self.current_entry = cursor.lastrowid
            return self.current_entry'''

content = content.replace(old_start_timer, new_start_timer)

with open('models.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Updated start_timer() in models.py to handle global tasks")

# Now update gui.py to pass project_id when starting timer
with open('gui.py', 'r', encoding='utf-8') as f:
    gui_content = f.read()

# Find and update the timer start call
old_timer_start = '''            # Start the timer
            self.timer_running = True
            self.timer_start_time = datetime.now()
            self.time_entry_model.start_timer(self.current_task_id)'''

new_timer_start = '''            # Start the timer
            self.timer_running = True
            self.timer_start_time = datetime.now()

            # Get current project ID for global tasks
            project_id = self.get_current_timer_project_id()
            self.time_entry_model.start_timer(self.current_task_id, project_id_override=project_id)'''

gui_content = gui_content.replace(old_timer_start, new_timer_start)

with open('gui.py', 'w', encoding='utf-8') as f:
    f.write(gui_content)

print("✅ Updated start_timer() call in gui.py to pass project_id")
print("\nGlobal tasks should now work with the timer!")
