# Git Push Helper - Usage Guide

## Quick Start

Double-click `git_push.bat` to commit and push your changes to GitHub.

## What It Does

1. **Shows current status** - Lists all modified/new files
2. **Stages changes** - Runs `git add .` to stage everything
3. **Prompts for commit info** - Asks for:
   - Version number (e.g., `2.0.6`)
   - Brief title (e.g., `UI improvements`)
   - Up to 3 detail lines (e.g., `- Fixed tab highlighting`)
4. **Commits changes** - Creates a formatted commit message
5. **Pushes to GitHub** - Uploads to `origin master`

## Example Session

```
Enter version: 2.0.6
Enter brief title: Tab UI improvements
- Removed Email/Invoice tabs from main bar
- Added dropdown submenus
- Fixed selected tab height issue
```

Creates commit:
```
Version 2.0.6 - Tab UI improvements
- Removed Email/Invoice tabs from main bar
- Added dropdown submenus
- Fixed selected tab height issue
```

## When to Use

- After making code changes you want to save
- Before closing a work session
- After completing a feature or bug fix

## Safety Notes

- You can review files before staging (Step 1)
- You can cancel at any prompt (type `n`)
- Commit happens before push (can cancel push separately)

## Common Git Commands (Manual)

If you need to do something manually:

```bash
git status              # See what changed
git add filename.py     # Stage specific file
git commit -m "message" # Commit with message
git push origin master  # Push to GitHub
git pull origin master  # Get latest from GitHub
git log --oneline       # View commit history
```

## Troubleshooting

**"fatal: not a git repository"**
- Run from TimeTrackerProV2 folder

**"Permission denied"**
- Check GitHub credentials
- May need to authenticate

**"Failed to push"**
- Run `git pull origin master` first
- Resolve any conflicts
- Then try `git_push.bat` again
