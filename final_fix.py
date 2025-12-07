"""Complete fix for invoice generation"""
import sqlite3

conn = sqlite3.connect("data/time_tracker.db")
cursor = conn.cursor()

# First, let's see what we're actually getting
cursor.execute('''
    SELECT te.*, t.hourly_rate, p.hourly_rate
    FROM time_entries te
    JOIN tasks t ON te.task_id = t.id
    JOIN projects p ON t.project_id = p.id
    LIMIT 1
''')

row = cursor.fetchone()
if row:
    print(f"Total columns: {len(row)}")
    # The issue is we have too many columns in time_entries
    # Let's use named access instead

# Fix: Update generate_invoice_data to use dict cursor
print("Creating view for simpler invoice queries...")
cursor.execute('''
    CREATE VIEW IF NOT EXISTS invoice_view AS
    SELECT 
        te.id             as entry_id,
        te.task_id,
        te.duration_minutes,
        te.is_billed,
        c.id              as client_id,
        c.name            as client_name,
        p.id              as project_id,
        p.name            as project_name,
        p.hourly_rate     as project_rate,
        p.is_lump_sum     as project_lump_sum,
        p.lump_sum_amount as project_lump_amount,
        t.name as task_name,
        t.hourly_rate as task_rate,
        t.is_lump_sum as task_lump_sum,
        t.lump_sum_amount as task_lump_amount,
        te.start_time,
        te.end_time
    FROM time_entries te
    JOIN tasks t ON te.task_id = t.id
    JOIN projects p ON t.project_id = p.id
    JOIN clients c ON p.client_id = c.id
''')

conn.commit()
print("✓ View created")

# Now update gui.py with this simpler query
print("""
Now replace generate_invoice_data method in gui.py with this simpler version:

def generate_invoice_data(self, client_id, start_date, end_date):
    conn = self.db.get_connection()
    conn.row_factory = sqlite3.Row  # Use Row factory for named access
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM invoice_view
        WHERE client_id = ? 
        AND DATE(start_time) BETWEEN ? AND ?
        AND (is_billed = 0 OR is_billed IS NULL)
    ''', (client_id, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
    
    entries = cursor.fetchall()
    conn.row_factory = None  # Reset
    
    if not entries:
        from tkinter import messagebox
        messagebox.showinfo("No Unbilled Hours", "No unbilled hours found.")
        return None
    
    self.pending_entry_ids = [row['entry_id'] for row in entries]
    invoice_items = []
    
    # Simple task grouping
    tasks = {}
    for row in entries:
        key = f"{row['project_name']} - {row['task_name']}"
        if key not in tasks:
            tasks[key] = {'minutes': 0, 'rate': row['task_rate'] or row['project_rate']}
        tasks[key]['minutes'] += row['duration_minutes'] or 0
    
    for task_name, data in tasks.items():
        hours = data['minutes'] / 60.0
        invoice_items.append({
            'description': task_name,
            'quantity': f"{hours:.2f} hrs",
            'rate': f"${data['rate']:.2f}/hr",
            'amount': hours * data['rate']
        })
    
    return {
        'client_id': client_id,
        'start_date': start_date,
        'end_date': end_date,
        'items': invoice_items,
        'total': sum(item['amount'] for item in invoice_items)
    }
""")
