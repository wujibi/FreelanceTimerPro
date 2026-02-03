# Time Tracker Pro V2 - Theme/Stylesheet System Implementation

## Context
Working on Time Tracker Pro app. Full context in `TIMETRACKER_CONTEXT.md`.

**Current Version:** 2.0.6  
**Main File:** `gui.py` (4,702 lines)  
**Framework:** Python tkinter/ttk  
**Current Theme:** Uses `ttk.Style()` with 'alt' theme (line ~207 in gui.py)  
**Project Path:** `C:\Users\briah\OneDrive\TypingMind\ClaudeWorkspace\AppProjects\TimeTrackerProV2`

---

## Goal
Implement a CSS-like stylesheet system for Time Tracker Pro that allows easy theme experimentation and export to other versions.

**Requirements:**
- Separate presentation (colors/fonts) from logic (gui.py)
- Create reusable theme files (similar to CSS stylesheets)
- Easy to swap themes without code changes
- Export themes to other app versions

---

## Requested Implementation

### 1. Create Theme Module Structure
```
TimeTrackerProV2/
├── themes/
│   ├── __init__.py
│   ├── professional_blue.py  (starter theme)
│   └── README.md  (theme documentation)
```

### 2. Starter Theme File (`themes/professional_blue.py`)
Create a theme module with:
- Color palette (bg_primary, bg_secondary, accent, text colors, etc.)
- Font definitions (default, heading, large, small)
- Widget styles for all ttk widgets used in app:
  - TLabel, TButton, TEntry, TCombobox
  - TNotebook, TNotebook.Tab
  - Treeview, Treeview.Heading
  - TFrame
- Custom style variants (Header.TLabel, Accent.TButton, Card.TFrame, etc.)
- Return colors and fonts dict for use in custom widgets

**Style:** Modern, professional, clean - similar to Tailwind CSS aesthetic

### 3. Integrate Theme into gui.py
- Add `setup_theme()` method to TimeTrackerApp class
- Import and apply theme in `__init__()`
- Store `self.colors` and `self.fonts` for use throughout app
- Replace current `style.theme_use('alt')` call with theme system

### 4. Documentation
Create `themes/README.md` explaining:
- How to create new themes
- How to switch between themes
- Widget style naming conventions
- Color/font variable usage

---

## Implementation Notes

**Current Theme Setup (gui.py ~line 207):**
```python
style = ttk.Style()
style.theme_use('alt')  # Currently using 'alt' theme
```

**This should become:**
```python
def setup_theme(self):
    from themes import professional_blue
    self.style = ttk.Style()
    self.colors, self.fonts = professional_blue.apply_theme(self.style)
```

---

## Branching Strategy Question

**DECISION NEEDED:** Should we fork/branch the app first or apply to current version?

### Option A: Apply to Current Version (Recommended)
- Implement theme system in main branch
- Theme infrastructure is non-breaking (just wraps existing styles)
- Can always create experimental branch later for wild theme experiments
- Keeps codebase simple

### Option B: Create Branch First
- Create `theme-experiments` branch
- Implement theme system there
- Test thoroughly before merging to main
- More Git overhead but safer

**Recommendation:** **Apply to current version** because:
- Theme system is additive (not destructive)
- You're already using ttk.Style() - just organizing it better
- Easy to revert if needed (you have git backups)
- Once theme infrastructure exists, THEN branch for experimental themes

---

## Preferences
- ✅ Use surgical edits with `edit_file` tool
- ✅ Create theme files first, then integrate into gui.py
- ✅ Test that existing UI still works after theme applied
- ✅ Keep current functionality identical (just styled differently)
- ✅ Make colors/fonts easily tweakable for experimentation

---

## Deliverables
1. `themes/__init__.py` (empty or with theme imports)
2. `themes/professional_blue.py` (complete starter theme)
3. `themes/README.md` (theme creation guide)
4. Updated `gui.py` with `setup_theme()` method
5. Brief explanation of how to create additional themes

---

## Questions to Answer First
1. **Should we branch first or apply to current version?**
2. Should we extract current widget configurations from gui.py to understand existing styles?
3. Do you want a theme preview/switcher UI, or just file-based swapping for now?
4. Any specific color preferences for the starter theme? (Or use modern blue/gray palette?)

---

Let's start by deciding on branching strategy, then create the theme infrastructure and apply it to gui.py.

---

## My Recommendation: Apply to Current Version First

**Why:**
- Theme system infrastructure = stable foundation
- Once you have theme files, create branch for wild experiments
- Main branch stays clean with professional default theme
- Experimental branch can have dark mode, neon colors, etc.

**Workflow:**
```bash
# 1. Apply theme system to main (this session)
# - Creates themes/ folder
# - Implements professional_blue.py
# - Integrates into gui.py

# 2. Later: Create experimental branch
git checkout -b theme-experiments
# - Copy professional_blue.py to dark_mode.py
# - Tweak colors wildly
# - Test without affecting main

# 3. When you find winner:
git checkout main
git checkout theme-experiments -- themes/dark_mode.py
git commit -m "Add dark mode theme"
```

**Decision: Apply to current version now?** (Yes/No)