# 🔧 Group Heading Color Fix - Instructions

## Problem
Group headings (Client/Project/Task rows) in the Time Entries and Invoices tabs are currently **dark navy blue** (old theme color). They need to use the theme's `group_heading` color instead.

---

## What Needs to Change in `gui.py`

### **Step 1: Find Where Treeview Tags Are Configured**

Search for these lines (probably around line 750-850):
```python
self.entries_tree.tag_configure('oddrow', ...)
self.entries_tree.tag_configure('evenrow', ...)
```

**ADD AFTER THOSE LINES:**
```python
# Configure group heading colors
if 'group_heading' in self.colors:
    self.entries_tree.tag_configure('client_row', 
        background=self.colors['group_heading'], 
        foreground=self.colors.get('group_text', 'white'),
        font=self.fonts['subheading'])
    
    self.entries_tree.tag_configure('project_row', 
        background=self.colors['group_heading'], 
        foreground=self.colors.get('group_text', 'white'),
        font=self.fonts['body'])
    
    self.entries_tree.tag_configure('task_row', 
        background=self.colors['group_heading'], 
        foreground=self.colors.get('group_text', 'white'),
        font=self.fonts['body'])
else:
    # Fallback if theme doesn't have group_heading color
    self.entries_tree.tag_configure('client_row', 
        background='#e8f4f8', 
        foreground='#13100f',
        font=self.fonts['subheading'])
    
    self.entries_tree.tag_configure('project_row', 
        background='#e8f4f8', 
        foreground='#13100f',
        font=self.fonts['body'])
    
    self.entries_tree.tag_configure('task_row', 
        background='#e8f4f8', 
        foreground='#13100f',
        font=self.fonts['body'])
```

---

### **Step 2: Find Where Client Rows Are Inserted**

Search for patterns like:
- `tree.insert(` + `'Client'`
- `entries_tree.insert(` + `'Client'`

**LOOK FOR CODE LIKE THIS:**
```python
client_item = self.entries_tree.insert('', 'end', 
    text=client_name,
    values=('Client', ...),
    tags=('client',)  # ← OLD TAG
)
```

**CHANGE TO:**
```python
client_item = self.entries_tree.insert('', 'end', 
    text=client_name,
    values=('Client', ...),
    tags=('client', 'client_row')  # ← ADD 'client_row' TAG
)
```

---

### **Step 3: Find Where Project Rows Are Inserted**

**LOOK FOR:**
```python
project_item = self.entries_tree.insert(client_item, 'end', 
    text=project_name,
    values=('Project', ...),
    tags=('project',)  # ← OLD TAG
)
```

**CHANGE TO:**
```python
project_item = self.entries_tree.insert(client_item, 'end', 
    text=project_name,
    values=('Project', ...),
    tags=('project', 'project_row')  # ← ADD 'project_row' TAG
)
```

---

### **Step 4: Find Where Task Rows Are Inserted**

**LOOK FOR:**
```python
task_item = self.entries_tree.insert(project_item, 'end', 
    text=task_name,
    values=('Task', ...),
    tags=('task',)  # ← OLD TAG
)
```

**CHANGE TO:**
```python
task_item = self.entries_tree.insert(project_item, 'end', 
    text=('task', 'task_row')  # ← ADD 'task_row' TAG
)
```

---

### **Step 5: Repeat for Invoice Tab Tree**

The **Invoices tab** has a similar tree (`invoice_entries_tree`). Find where it configures tags and inserts rows, then apply the same changes.

---

## Functions to Search For

These are the likely function names where the changes need to happen:

1. `create_time_entries_tab()` - Where entries_tree is created
2. `load_time_entries()` or `refresh_time_entries()` - Where rows are inserted
3. `create_invoices_tab()` - Where invoice_entries_tree is created
4. `load_invoiceable_entries()` - Where invoice rows are inserted

---

## Quick Search Commands

If you can search gui.py faster than me, look for:

```
entries_tree.insert
invoice_entries_tree.insert
tag_configure
'Client'
'Project'
'Task'
```

---

## After Making Changes

1. **Restart the app**
2. Go to **Company Info > Appearance**
3. Try **"Burnt Orange Pro V2"** (light peach groups)
4. Try **"Burnt Orange Pro V3"** (teal groups)
5. Check if group rows now have the themed colors!

---

**Need me to do this?** If you can find and share the line numbers for:
1. Where `entries_tree.tag_configure` is called
2. Where client/project/task rows are inserted

I can make the exact edits! Otherwise this document shows what needs to change.
