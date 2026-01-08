# Global Tasks Implementation - COMPLETE

## ✅ Files Modified

### 1. add_global_tasks.py (NEW)
Migration script to add `is_global` column to tasks table.

**Run this first:** `python add_global_tasks.py`

### 2. models.py - Task class (UPDATED)
- ✅ `create()` - Now accepts `is_global` parameter, `project_id` optional
- ✅ `get_global_tasks()` - NEW method to get all global tasks
- ✅ `get_all_for_project()` - NEW method to get global + project tasks
- ✅ `get_all()` - Updated to LEFT JOIN projects (handles NULL)
- ✅ `get_by_project()` - Filters out global tasks

## 📋 NEXT STEPS - GUI Updates Needed

### Step 1: Update create_tasks_tab() in gui.py

Add checkbox for global tasks:

```python
# Add after description field in task form:
self.task_global_var = tk.BooleanVar()
global_check = ttk.Checkbutton(
    form_frame,
    text="🌍 Global Task (available for all projects)",
    variable=self.task_global_var,
    command=self.toggle_project_selection
)
global_check.grid(row=2, column=0, columnspan=2, sticky='w', pady=5)
```

### Step 2: Add toggle_project_selection() method

```python
def toggle_project_selection(self):
    is_global = self.task_global_var.get()
    if is_global:
        self.task_project_combo.set('')
        self.task_project_combo.config(state='disabled')
    else:
        self.task_project_combo.config(state='readonly')
```

### Step 3: Update create_task() method

```python
def create_task(self):
    # ... existing code ...
    is_global = self.task_global_var.get()
    
    if is_global:
        # Create global task
        self.task_model.create(
            name=name,
            description=description,
            is_global=True
        )
    else:
        # Create project task
        project_id = self.projects[project_idx][0]
        self.task_model.create(
            name=name,
            description=description,
            project_id=project_id,
            is_global=False
        )
```

### Step 4: Update Timer Tab task dropdown

In `refresh_timer_combos()` or wherever tasks are loaded for timer:

```python
# Get selected project
if project_idx >= 0:
    project_id = self.projects[project_idx][0]
    # Get global + project tasks
    tasks = self.task_model.get_all_for_project(project_id)
else:
    tasks = []
```

### Step 5: Update refresh_tasks() display

Tasks treeview should show "[GLOBAL]" for global tasks in project column.

## 🧪 Testing Checklist

- [ ] Run migration script
- [ ] Create a global task (e.g., "Meeting")
- [ ] Verify it shows "[GLOBAL]" in tasks list
- [ ] Select Project A in timer
- [ ] Verify global task appears in task dropdown
- [ ] Select Project B in timer
- [ ] Verify same global task appears
- [ ] Log time to global task
- [ ] Generate invoice - verify global task entries included
- [ ] Create project-specific task
- [ ] Verify it only shows for that project

## 💡 Benefits

✅ Create common tasks once (Meeting, Email, Planning)
✅ Available across all projects
✅ Reduces duplicate task creation
✅ Cleaner task management
✅ Maintains backward compatibility

## 🔄 Migration Safe

- Existing tasks get `is_global=0` (project-specific)
- No data loss
- Backward compatible
