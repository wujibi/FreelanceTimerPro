# 🚀 Push Invoice Bug Fix to GitHub

## Step-by-Step Commands

Open Command Prompt or PowerShell in the project folder, then run these commands:

---

### 1️⃣ Clean Up Temporary Files

```bash
python cleanup_before_push.py
```

**Then delete the cleanup script itself:**

```bash
del cleanup_before_push.py
del GIT_PUSH_COMMANDS.md
del PUSH_TO_GITHUB.md
```

---

### 2️⃣ Check What Will Be Committed

```bash
git status
```

**You should see:**
- ✅ Modified: `gui.py`, `CHANGELOG.md`, `CURRENT_STATUS.md`
- ✅ Deleted: ~13 temporary files

---

### 3️⃣ Stage All Changes

```bash
git add .
```

---

### 4️⃣ Commit with Message

```bash
git commit -m "Fix: Invoice tab now loads all entries including global tasks

- Changed SQL JOIN from tasks.project_id to time_entries.project_id
- Fixed 5 queries in load_invoiceable_entries() and show_invoice_preview_dialog()
- Global tasks with NULL project_id were being excluded from Invoice queries
- All unbilled entries now appear correctly
- Version bump to 2.0.3"
```

---

### 5️⃣ Push to GitHub

```bash
git push origin master
```

*Or if your branch is named "main":*
```bash
git push origin main
```

---

### 6️⃣ Verify on GitHub

Visit: **https://github.com/wujibi/TimeTrackerApp**

- Check that the commit appears
- Click on the commit to see the changes
- Verify `gui.py` shows the SQL JOIN changes

---

### 7️⃣ Pull on Laptop

Once pushed, on your laptop run:

```bash
git pull origin master
```

Then restart the app and test!

---

## ✅ Quick Copy-Paste Version

```bash
# Clean up
python cleanup_before_push.py
del cleanup_before_push.py
del GIT_PUSH_COMMANDS.md
del PUSH_TO_GITHUB.md

# Git commands
git add .
git status
git commit -m "Fix: Invoice tab now loads all entries including global tasks"
git push origin master
```

---

## 🆘 If Something Goes Wrong

**"Repository not found"**
- Make sure you're authenticated with GitHub
- Try using GitHub Desktop instead

**"Updates were rejected"**
```bash
git pull origin master --rebase
git push origin master
```

**"Nothing to commit"**
- Check if you already committed
- Just run: `git push origin master`

---

**That's it!** 🎉 Your fix is now on GitHub and ready to pull on the laptop.
