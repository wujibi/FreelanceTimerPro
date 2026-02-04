# Renaming App: "Time Tracker Pro" → "Freelance Timer Pro"

## Overview
This guide covers renaming the application from "Time Tracker Pro" to "Freelance Timer Pro" across all files.

**Method:** PyCharm Find/Replace in Files (safest, most thorough)

---

## Step 1: PyCharm Find & Replace

### Open PyCharm
1. Open the project in PyCharm
2. Press **Ctrl+Shift+R** (Replace in Files)

### Search #1: "Time Tracker Pro"
- **Find:** `Time Tracker Pro`
- **Replace:** `Freelance Timer Pro`
- **Scope:** Whole project
- **File mask:** `*.*` (all files)
- **Click "Find"** - Review each match before replacing
- **Expected files:**
  - gui.py (window title, about text)
  - README.md
  - CHANGELOG.md
  - CURRENT_STATUS.md
  - Documentation files

### Search #2: "TimeTrackerPro" (no spaces)
- **Find:** `TimeTrackerPro`
- **Replace:** `FreelanceTimerPro`
- **Expected:** Rare, possibly in comments or old code

### Search #3: "time_tracker" (database/file references)
- **Find:** `time_tracker`
- **Replace:** `freelance_timer`
- **⚠️ CAREFUL:** This affects:
  - Database filename: `time_tracker.db` → `freelance_timer.db`
  - Module imports
  - File paths in code
- **Review EVERY match carefully!**

### Search #4: "TimeTracker" (class names, if any)
- **Find:** `TimeTracker`
- **Replace:** `FreelanceTimer`
- **Expected:** Class names, possibly in models or older code

---

## Step 2: Critical Files to Check Manually

### gui.py
```python
# Line ~22: Window title
self.root.title("Freelance Timer Pro")

# Line ~33-35: Icon path (if references app name)
icon_path = os.path.join(app_dir, 'freelance_timer_icon.ico')

# Search for any remaining "Time Tracker" in comments
```

### main.py
```python
# Check window title, app initialization
# Should reference "Freelance Timer Pro"
```

### README.md
```markdown
# Freelance Timer Pro

Professional time tracking and invoicing application...
```

### CHANGELOG.md
```markdown
# Freelance Timer Pro - Changelog

## Version 2.0.8 - 2026-02-04
- Renamed application from "Time Tracker Pro" to "Freelance Timer Pro"
...
```

### Database Path (IMPORTANT!)
Check `main.py` and `gui.py` for database path references:
```python
# OLD:
default_db_path = os.path.join(app_data_dir, 'time_tracker.db')

# NEW:
default_db_path = os.path.join(app_data_dir, 'freelance_timer.db')
```

**⚠️ WARNING:** Changing database filename means existing data won't load!

---

## Step 3: Database Migration Strategy

### Option A: Keep Existing Database Name (RECOMMENDED)
**Pros:** Existing data works immediately, no migration needed  
**Cons:** Database file doesn't match app name

```python
# In main.py - keep this:
default_db_path = os.path.join(
    os.path.expanduser('~\\My Drive\\TimeTrackerApp\\data'),
    'time_tracker.db'  # KEEP OLD NAME
)
```

### Option B: Rename Database (Requires Migration)
**Pros:** Clean, consistent naming  
**Cons:** Must copy/rename existing database file

**Steps:**
1. Find existing database:
   ```
   C:\Users\briah\My Drive\TimeTrackerApp\data\time_tracker.db
   ```

2. Copy (don't move) to new name:
   ```
   C:\Users\briah\My Drive\TimeTrackerApp\data\freelance_timer.db
   ```

3. Update code to use new name

4. Test thoroughly

5. Delete old file once confirmed working

**RECOMMENDATION:** Use **Option A** for now. Rename database later if needed.

---

## Step 4: Files/Folders to Rename

### Icon Files
```
time_tracker_icon.ico → freelance_timer_icon.ico
time_tracker_icon.png → freelance_timer_icon.png
```

### Folder Structure (Optional)
```
TimeTrackerProV2 → FreelanceTimerProV2
```
**Note:** Requires updating file paths, Git remote. Do this last if at all.

### Batch Scripts (Update references)
```
launcher.bat
git_commit_v2.0.8.bat
git_push.bat
```
Check these files for any "Time Tracker" references.

---

## Step 5: Testing Checklist

After renaming, test thoroughly:

- [ ] App launches without errors
- [ ] Window title shows "Freelance Timer Pro"
- [ ] Database loads correctly (all data present)
- [ ] All tabs and features work
- [ ] Icons display correctly (if renamed)
- [ ] About/Help text shows correct name
- [ ] Email templates reference correct name
- [ ] Invoice templates show correct name
- [ ] Company info displays correctly

---

## PyCharm Find/Replace Tips

### How to Use Safely
1. **Ctrl+Shift+R** opens Replace in Files
2. **Set scope** to "Project Files"
3. **Click "Find"** first (don't click "Replace All" immediately!)
4. **Review each match** in preview panel
5. **Exclude matches** you don't want to change (right-click → Exclude)
6. **Replace selectively** or "Replace All" after review

### Preview Changes
- PyCharm shows **before/after** preview
- Each file shows **context** around match
- Can **exclude specific files** from replacement
- Changes are **undoable** (Ctrl+Z)

### Common Pitfalls
- Don't replace in:
  - `.git` folder (usually auto-excluded)
  - Binary files
  - Third-party libraries
  - Log files

---

## Rollback Plan

### If Something Breaks
1. **Ctrl+Z** in PyCharm (undo changes)
2. **Git reset:**
   ```bash
   git checkout .
   ```
3. **Restore from backup** (if you made one)

### Before Starting
**Create backup:**
```bash
git add .
git commit -m "Backup before rename"
```

---

## Recommended Order

1. ✅ **Commit current work** to Git (backup point)
2. ✅ **Use PyCharm Find/Replace** (search terms above)
3. ✅ **Keep database name** unchanged (avoid migration hassle)
4. ✅ **Test app** thoroughly
5. ✅ **Update documentation** (README, CHANGELOG)
6. ✅ **Commit changes** with clear message
7. ⏸️ **Rename icons/folders** later (separate task)

---

## Search Summary (Copy/Paste)

```
Search 1: "Time Tracker Pro" → "Freelance Timer Pro"
Search 2: "TimeTrackerPro" → "FreelanceTimerPro"
Search 3: "TimeTracker" → "FreelanceTimer"
Search 4: "time_tracker" → "freelance_timer" (BE CAREFUL!)
```

**⚠️ SKIP DATABASE PATH:** Leave `time_tracker.db` unchanged to avoid data migration.

---

## After Renaming

### Update Git
```bash
git add .
git commit -m "Rename app: Time Tracker Pro → Freelance Timer Pro (v2.0.8)"
git push
```

### Update External References
- Website (if exists)
- Documentation sites
- Marketing materials
- Domain DNS (freelancetimer.pro)

---

**Estimated Time:** 15-30 minutes  
**Difficulty:** Easy (with PyCharm)  
**Risk Level:** Low (if database path unchanged)

**Ready to start?** Open PyCharm and press **Ctrl+Shift+R**!
