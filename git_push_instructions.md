# Git Push Instructions for Manual Entry Fix

## Step-by-Step Commands

### 1. Open Command Prompt or Terminal
Navigate to your project folder:
```bash
cd "C:\Users\briah\OneDrive\TypingMind\ClaudeWorkspace\AppProjects\TimeTrackerProV2"
```

### 2. Check Current Status
See what files have changed:
```bash
git status
```

**Expected output:** Should show `gui.py` as modified, plus new files:
- `MANUAL_ENTRY_FIX_COMPLETE.md`
- `TIMETRACKER_CONTEXT.md`
- `cleanup_junk_files.py`
- `gui.py.backup_manual_entry_fix`

### 3. Review Changes (Optional but Recommended)
See what actually changed in gui.py:
```bash
git diff gui.py
```
(Press `q` to exit the diff view)

### 4. Stage Your Changes
Add the files you want to commit:

**Option A - Add specific files (RECOMMENDED):**
```bash
git add gui.py
git add MANUAL_ENTRY_FIX_COMPLETE.md
git add TIMETRACKER_CONTEXT.md
git add cleanup_junk_files.py
```

**Option B - Add everything (includes backup file):**
```bash
git add .
```

### 5. Commit with Message
Create a commit with a descriptive message:
```bash
git commit -m "Fix: Manual entry now supports global tasks and updates daily totals

- Added Client/Project dropdowns to manual entry form
- Fixed project_id_override handling for global tasks
- Fixed daily totals update logic to work with manual entries
- Manual entry combos now populated on startup
- Added context documentation for future AI assistance
- Includes cleanup script for removing junk files from failed session"
```

### 6. Push to GitHub
Push your changes to the remote repository:
```bash
git push origin main
```

**Note:** If your main branch is named `master` instead of `main`, use:
```bash
git push origin master
```

### 7. Verify Success
Check that it worked:
```bash
git status
```

Should say: "Your branch is up to date with 'origin/main'"

---

## 🔍 If You Get Errors

### Error: "fatal: not a git repository"
**Solution:** Initialize git first:
```bash
git init
git remote add origin https://github.com/YOUR_USERNAME/TimeTrackerApp.git
```

### Error: "rejected - non-fast-forward"
**Solution:** Pull first, then push:
```bash
git pull origin main --rebase
git push origin main
```

### Error: "Authentication failed"
**Solution:** Need to authenticate with GitHub:
- Use GitHub Desktop (easier), OR
- Set up Personal Access Token: https://github.com/settings/tokens

### Error: "Permission denied (publickey)"
**Solution:** Set up SSH keys:
- Follow: https://docs.github.com/en/authentication/connecting-to-github-with-ssh

---

## 📋 Quick Reference - All Commands in Order

```bash
cd "C:\Users\briah\OneDrive\TypingMind\ClaudeWorkspace\AppProjects\TimeTrackerProV2"
git status
git add gui.py MANUAL_ENTRY_FIX_COMPLETE.md TIMETRACKER_CONTEXT.md cleanup_junk_files.py
git commit -m "Fix: Manual entry now supports global tasks and updates daily totals"
git push origin main
```

---

## 🗑️ Optional: Ignore Backup Files in Future

If you DON'T want to commit backup files, add to `.gitignore`:
```bash
echo "*.backup*" >> .gitignore
git add .gitignore
git commit -m "Update gitignore to exclude backup files"
git push origin main
```

---

## ✅ What Will Be Pushed

**Core Fix:**
- `gui.py` - The actual bug fixes (3 sections modified)

**Documentation:**
- `MANUAL_ENTRY_FIX_COMPLETE.md` - What was fixed and how
- `TIMETRACKER_CONTEXT.md` - Context for future AI sessions

**Utilities:**
- `cleanup_junk_files.py` - Script to remove junk from failed session

**Optional (only if you used `git add .`):**
- `gui.py.backup_manual_entry_fix` - Backup of original

**Will NOT be pushed (in .gitignore):**
- `*.db` files (database)
- `__pycache__/` folders
- `.idea/` folder (PyCharm)
- `.venv/` folder (virtual environment)

---

**Created:** January 13, 2026
**Fix Version:** Manual Entry Global Tasks Support
