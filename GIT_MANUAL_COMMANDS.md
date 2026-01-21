# Git Commands for v2.0.4 Push

## Option 1: Use the Batch File (Easiest)

1. Open the project folder in Explorer
2. Double-click `GIT_COMMANDS_TODAY.bat`
3. Follow the prompts (press any key to continue through each step)

---

## Option 2: Manual Commands in CMD

Open Command Prompt and run these commands one at a time:

### Step 1: Navigate to project directory
```cmd
cd /d "C:\Users\briah\OneDrive\TypingMind\ClaudeWorkspace\AppProjects\TimeTrackerProV2"
```

### Step 2: Check what files changed
```cmd
git status
```

**Expected output:**
- Modified: `gui.py`
- Modified: `CHANGELOG.md`
- Modified: `CURRENT_STATUS.md`
- Modified: `TIMETRACKER_CONTEXT.md`
- New file: `SESSION_SUMMARY_2026-01-21.md`
- Untracked: 3 temp files (can ignore or delete)

### Step 3: Stage all changes
```cmd
git add .
```

### Step 4: Commit with message
```cmd
git commit -m "Version 2.0.4 - Fixed time entry edit + Invoice tab grouping" -m "- Fixed: Time entry edit bug with global tasks (simplified query)" -m "- Added: Invoice tab hierarchical grouping (Project -> Task -> Entry)" -m "- Fixed: Select/Deselect All buttons work with hierarchy" -m "- Updated: Documentation (CHANGELOG, CURRENT_STATUS, TIMETRACKER_CONTEXT)"
```

### Step 5: Push to GitHub
```cmd
git push origin master
```

---

## Option 3: Short Version (If you're confident)

```cmd
cd /d "C:\Users\briah\OneDrive\TypingMind\ClaudeWorkspace\AppProjects\TimeTrackerProV2"
git add .
git commit -m "Version 2.0.4 - Fixed time entry edit + Invoice tab grouping"
git push origin master
```

---

## Troubleshooting

### If you get "not a git repository" error:
```cmd
cd /d "C:\Users\briah\OneDrive\TypingMind\ClaudeWorkspace\AppProjects\TimeTrackerProV2"
git status
```
Make sure you're in the right directory.

### If you get authentication error:
You may need to authenticate with GitHub. Follow the prompts.

### If you want to see what will be pushed:
```cmd
git diff HEAD
```

### If you want to undo the last commit (before pushing):
```cmd
git reset --soft HEAD~1
```

---

## After Pushing

1. Visit your GitHub repository to confirm changes
2. Delete the 3 temporary files:
   - `gui_invoice_grouped.patch`
   - `gui_load_invoiceable_backup.py`
   - `update_load_invoiceable.py`
3. Optionally delete these instruction files:
   - `GIT_COMMANDS_TODAY.bat`
   - `GIT_MANUAL_COMMANDS.md`

---

**Quick Reference:**
- `git status` - See what changed
- `git add .` - Stage all changes
- `git commit -m "message"` - Commit with message
- `git push origin master` - Push to GitHub
- `git log` - See commit history
