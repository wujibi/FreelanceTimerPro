# Add Alternating Row Colors to Time Entries Tab

## What to Add

After the `create_time_entries_tab()` method creates the tree, add this code to configure alternating row colors:

```python
# In create_time_entries_tab(), after self.entries_tree is created (around line ~1815)
# Add these two lines RIGHT AFTER creating the tree:

# Configure alternating row colors for ledger-style display
self.entries_tree.tag_configure('oddrow', background=self.colors['background'])  # Deep navy
self.entries_tree.tag_configure('evenrow', background='white')  # White
```

## Then in refresh_time_entries()

When inserting rows, alternate the tags. Find where entries are inserted (search for `self.entries_tree.insert`) and add `tags=` parameter:

```python
# Example - when inserting entry rows:
row_num = 0
for entry in entries:
    tag = 'evenrow' if row_num % 2 == 0 else 'oddrow'
    self.entries_tree.insert(parent, 'end', text=name, values=values, tags=(tag, 'entry', f'entry_id_{id}'))
    row_num += 1
```

This will give you alternating navy/white rows like a ledger!

The theme file already sets the colors - you just need to apply the tags when inserting rows.
