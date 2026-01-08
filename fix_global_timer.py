import re

with open('gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace start_timer method to handle global tasks
old_start_timer = r'''        # Extract just the task name from "Client - Project - Task" format
        # The format is: client_name - project_name - task_name
        parts = task_text\.split\(' - '\)
        if len\(parts\) >= 3:
            task_name = ' - '\.join\(parts\[2:\]\)  # In case task name has dashes
        else:
            messagebox\.showerror\("Error", "Invalid task format"\)
            return

        # Find the task by matching client, project, and task names
        tasks = self\.task_model\.get_all\(\)
        self\.current_task_id = None

        for task in tasks:
            if task\[9\] == client_name and task\[8\] == project_name and task\[2\] == task_name:
                self\.current_task_id = task\[0\]
                break'''

new_start_timer = '''        # Check if it's a global task
        if task_text.startswith('[GLOBAL] '):
            # Extract task name from "[GLOBAL] TaskName"
            task_name = task_text.replace('[GLOBAL] ', '')

            # Find the global task
            global_tasks = self.task_model.get_global_tasks()
            self.current_task_id = None

            for task in global_tasks:
                if task[2] == task_name:
                    self.current_task_id = task[0]
                    break
        else:
            # Regular project-specific task
            # Extract task name from "Client - Project - Task" format
            parts = task_text.split(' - ')
            if len(parts) >= 3:
                task_name = ' - '.join(parts[2:])
            else:
                messagebox.showerror("Error", "Invalid task format")
                return

            # Find the task by matching client, project, and task names
            tasks = self.task_model.get_all()
            self.current_task_id = None

            for task in tasks:
                if task[9] == client_name and task[8] == project_name and task[2] == task_name:
                    self.current_task_id = task[0]
                    break'''

content = re.sub(old_start_timer, new_start_timer, content, flags=re.DOTALL)

with open('gui.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed start_timer() to handle global tasks!")
print("Global tasks should now work in the timer.")
