# Git Push Commands - Invoice Bug Fix

## 🧹 STEP 1: Clean Up Unnecessary Files

Run the cleanup script:

```bash
cd C:\Users\briah\OneDrive\TypingMind\ClaudeWorkspace\AppProjects\TimeTrackerProV2
python cleanup_before_push.py
```

This will delete:
- Temporary utility scripts (cleanup, create_icon, fix_pycharm, etc.)
- Temporary documentation files
- Backup files
- Old fix documentation
- Shortcut files

Then manually delete the cleanup script itself:
```bash
del cleanup_before_push.py
```

---

## 📝 STEP 2: Update Documentation

**Before committing, let's update the key docs:**

### Update CHANGELOG.md

Add this at the top (after the header):

```markdown
## [2.0.3] - 2026-01-15

### Fixed
- **Invoice Tab Loading Bug**: Fixed critical bug where Invoice tab was not loading time entries that used global tasks
  - Changed SQL JOIN from `tasks.project_id` to `time_entries.project_id` 
  - Affected methods: `load_invoiceable_entries()` and `show_invoice_preview_dialog()`
  - 5 SQL queries updated to properly join through time_entries table
  - All unbilled entries now appear in Invoice tab regardless of task type
  - Fixes issue where only some entries would load when selecting a client
  
### Technical Details
- Root cause: Global tasks have `tasks.project_id = NULL`, causing JOIN to fail
- Solution: Use `time_entries.project_id` which always has a value (even for global tasks)
- Files modified: `gui.py` (lines ~3424, ~3434, ~3453, ~3465, ~3568)
- Impact: Invoice generation now works correctly for all task types

---
```

### Update CURRENT_STATUS.md

Change status from "FULLY OPERATIONAL" to reflect the new fix.

---

## 🔍 STEP 3: Check Git Status

```bash
git status
```

**Expected output:**
- Modified: `gui.py`, `CHANGELOG.md`, `CURRENT_STATUS.md`
- Deleted: ~13 temporary files
- Untracked: Maybe some new docs you want to keep

---

## ➕ STEP 4: Stage All Changes

```bash
git add .
```

This stages:
- Modified files (gui.py, documentation)
- Deleted files (cleanup scripts, temp docs)

---

## 📋 STEP 5: Verify Staged Changes

```bash
git status
```

**Make sure you see:**
- ✅ gui.py (modified)
- ✅ CHANGELOG.md (modified)
- ✅ CURRENT_STATUS.md (modified)
- ✅ Deleted temporary files

**Should NOT see:**
- ❌ .venv/ (should be ignored)
- ❌ __pycache__/ (should be ignored)
- ❌ data/ (should be ignored)
- ❌ .idea/ (should be ignored)

If you see those, they should already be in .gitignore. Double-check:
```bash
cat .gitignore
```

---

## 💬 STEP 6: Commit with Clear Message

```bash
git commit -m "Fix: Invoice tab now loads all entries including global tasks

- Fixed SQL JOIN bug in load_invoiceable_entries() method
- Changed from tasks.project_id to time_entries.project_id
- Global tasks with NULL project_id were being excluded from queries
- Updated 5 SQL queries across 2 methods
- Resolves issue where Invoice tab showed incomplete entry list
- Version bump to 2.0.3"
```

---

## 🚀 STEP 7: Push to GitHub

```bash
git push origin master
```

**Or if your branch is named "main":**
```bash
git push origin main
```

---

## ✅ STEP 8: Verify on GitHub

1. Go to: https://github.com/wujibi/TimeTrackerApp
2. Check that commit appears
3. Click on commit to see changes
4. Verify gui.py changes are correct
5. Check CHANGELOG.md updated

---

## 🔄 STEP 9: Pull on Other Machine (Laptop)

On your laptop, pull the changes:

```bash
cd C:\Users\briah\OneDrive\TypingMind\ClaudeWorkspace\AppProjects\TimeTrackerProV2
git pull origin master
```

Then test the app to confirm fix works on both machines.

---

## 📊 Summary of Changes

**Fixed:**
- Invoice tab SQL queries (5 queries updated)

**Updated:**
- CHANGELOG.md (added v2.0.3 entry)
- CURRENT_STATUS.md (updated status)

**Deleted:**
- 13 temporary/utility files
- 1 backup directory

**Version:** 2.0.2 → 2.0.3

---

## ⚠️ If Git Push Fails

### "Repository not found" or "Authentication failed"

Re-authenticate:
```bash
git config --global user.name "wujibi"
git config --global user.email "your-email@example.com"
```

Or use GitHub Desktop if you have it installed.

### "Updates were rejected"

Pull first, then push:
```bash
git pull origin master --rebase
git push origin master
```

### "Nothing to commit"

You might have already committed locally. Just push:
```bash
git push origin master
```

---

## 🎯 Quick Command Summary

```bash
# 1. Cleanup
python cleanup_before_push.py
del cleanup_before_push.py

# 2. Update CHANGELOG.md and CURRENT_STATUS.md (manually)

# 3. Stage and commit
git add .
git status
git commit -m "Fix: Invoice tab now loads all entries including global tasks"

# 4. Push
git push origin master

# 5. Verify on GitHub
# Visit: https://github.com/wujibi/TimeTrackerApp
```

---

**Ready to push?** Just copy and paste the commands! 🚀
