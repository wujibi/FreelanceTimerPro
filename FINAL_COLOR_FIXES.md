# 🎨 Final Color Fixes Needed

## Issues Identified

### 1. Active Tab Text is White (Hard to Read)
**Problem:** Active tab has orange background with white text
**Fix:** Change to dark text on orange background

### 2. Individual Entry Rows Have Light/White Text
**Problem:** Entry rows under tasks show very light gray text (hard to read)
**Fix:** These rows should have dark text, NOT the alternating row colors

## Solutions

### Fix #1: Active Tab Text Color

**Files to Edit:** All 3 burnt orange theme files

**In each file, find this line (around line 75):**
```python
foreground=[('selected', 'white'),
```

**Change to:**
```python
foreground=[('selected', colors['text']),  # Dark text on orange tab
```

**This affects:**
- `themes/burnt_orange_pro.py`
- `themes/burnt_orange_pro_v2.py`
- `themes/burnt_orange_pro_v3.py`

---

### Fix #2: Entry Row Text Color

**Problem:** The alternating row logic is applying to ALL rows, including individual entries

**File:** `gui.py` around line 3730-3750

**Current logic:**
```python
# Determine row tag based on index
if idx % 2 != 0:
    row_tag = 'oddrow'
else:
    row_tag = 'evenrow'

self.entries_tree.insert(task_id, 'end',
    text=f"      {entry_icon} Entry",
    values=(...),
    tags=(f'entry_id_{entry[0]}', row_tag))  # ← PROBLEM: Uses oddrow/evenrow
```

**The issue:** Individual entries are getting oddrow/evenrow tags which have the alternating colors. We need to ONLY apply alternating colors to group headings, NOT individual entries.

**Solution Options:**

**Option A (Simple):** Remove alternating rows entirely from individual entries
```python
self.entries_tree.insert(task_id, 'end',
    text=f"      {entry_icon} Entry",
    values=(...),
    tags=(f'entry_id_{entry[0]}',))  # Remove row_tag
```

**Option B (Better):** Create a separate 'entry_row' tag with normal colors
```python
# In tag configuration section (around line 815)
self.entries_tree.tag_configure('entry_row', 
    background='white', 
    foreground=colors['text'])  # Dark text on white

# Then when inserting entries:
self.entries_tree.insert(task_id, 'end',
    text=f"      {entry_icon} Entry",
    values=(...),
    tags=(f'entry_id_{entry[0]}', 'entry_row'))
```

---

## Recommended Approach

**I suggest Option B** because it gives us explicit control:

1. **Group headings** (Client/Project/Task) = Theme `group_heading` color
2. **Individual entries** = White background with dark text (always readable)
3. **Selected rows** = Orange with white text (highlight)

This creates clear visual hierarchy:
- Colored groups stand out
- Entries are neutral/readable
- Selections pop

---

## Quick Test

After making these fixes, you should see:
- ✅ Active tab text is **dark and readable**
- ✅ Entry rows have **dark text on white** (not alternating colors)
- ✅ Group rows (V2) have **light peach background**
- ✅ Group rows (V3) have **teal background**
- ✅ Selected rows turn **orange with white text**

---

**Want me to make these edits, or do you want to take a break?** This is definitely a lot of work for color changes - you're right about that! 😅
