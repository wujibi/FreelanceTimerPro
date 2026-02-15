# TIME TRACKER APP - Quick Context for AI Assistants

## 📍 Project Info

- **Name:** Time Tracker Pro V2.0
- **Location:** `C:\Users\briah\OneDrive\TypingMind\ClaudeWorkspace\AppProjects\TimeTrackerProV2\`
- **Main File:** `gui.py` (4,702 lines)
- **Database:** SQLite at `G:\My Drive\TimeTrackerApp\data\time_tracker.db`
- **Python Version:** 3.12.10
- **IDE:** PyCharm
- **Framework:** Tkinter GUI + SQLite + ReportLab for PDFs

---

## ✅ Current Status (January 2026)

**Working Features:**
- ✅ Timer functionality (start/stop with Client → Project → Task selection)
- ✅ Manual time entry (both time range and decimal hours modes)
- ✅ Global tasks (tasks available across all projects)
- ✅ Client/Project/Task management (full CRUD)
- ✅ Time entries tracking (grouped view by Client → Project → Task)
- ✅ Time entry editing (all entries including global tasks, editable from Invoice tab)
- ✅ Invoice tab with hierarchical grouping (Project → Task → Entries)
- ✅ Invoice generation with PDF export (grouped by project/task)
- ✅ **EMAIL INVOICES** - Send invoices directly with PDF attachments 🎉
- ✅ Daily time totals tracking by client and project
- ✅ Google Drive database sync
- ✅ Company info management for invoices
- ✅ Billing prevention (no double-billing)
- ✅ Excel export of time entries
- ✅ Email settings with SMTP configuration (Gmail, Outlook, Custom)
- ✅ Email templates (5 built-in: Professional, Friendly, Formal, Reminder, Thank You)
- ✅ Tree expansion state preservation (no more collapsing!)

**Recent Fixes (v2.0.5 - January 29, 2026):**
- ✅ **EMAIL INVOICE FEATURE** - Complete implementation from SMTP config to PDF attachment
- ✅ Fixed task edit bug (rates now update correctly)
- ✅ Fixed tree collapse issue (Tasks, Time Entries, Invoice tabs maintain expansion)
- ✅ Added edit from Invoice tab (both main tab and preview dialog)
- ✅ Fixed dialog positioning (modals now appear in front)
- ✅ Fixed whitespace on startup (removed Timer scrollbar)
- ✅ Fixed email settings persistence (auto-load on startup)
- ✅ Added ReportLab dependency for PDF generation

---

## 🗂️ File Structure

**Core Application Files:**
```
gui.py              # Main application (4,702 lines) - THE BIG ONE
models.py           # Data models (Client, Project, Task, TimeEntry, CompanyInfo)
db_manager.py       # Database operations and connection management
invoice_generator.py # PDF invoice generation
launcher.pyw        # Application launcher
main.py             # Entry point
config.py           # Configuration settings
```

**Support Files:**
```
requirements.txt    # Python dependencies
timetracker.ico     # Application icon
launch_timetracker.bat/sh  # Quick launch scripts
```

**Data:**
```
G:\My Drive\TimeTrackerApp\data\time_tracker.db  # Main database (synced to Google Drive)
```

---

## 🚨 When Asking for Help

**Good Request Format:**
```
Issue: [Specific error or behavior]
Tab/Feature: [Which tab - Timer, Manual Entry, Invoices, etc.]
Error Message: [Copy exact error if any]
Steps to Reproduce: [What you did]
Expected: [What should happen]
Actual: [What actually happened]
```

**Example:**
```
Issue: Manual time entry crashes when using global tasks
Tab/Feature: Timer tab → Manual Time Entry section
Error Message: ValueError: Global tasks require a project context (project_id_override)
Steps to Reproduce: Select global task, fill time, click Add Entry
Expected: Entry saves successfully
Actual: App crashes with error
```

---

## 📋 Rules for AI Assistants

### ✅ DO:
1. **Read the actual code first** - Use `read_text_file` to see current implementation
2. **Create backups** - Always backup before making changes
3. **Incremental fixes** - One change at a time, wait for user testing
4. **Use surgical edits** - Use `edit_file` for precise changes to existing code
5. **Explain your approach** - Tell user WHY this will fix the issue
6. **Test logic mentally** - Walk through the code flow before suggesting changes
7. **Follow existing patterns** - Match the coding style already in the file
8. **Document changes** - Update markdown docs when making significant changes

### ❌ DON'T:
1. **Don't create extra files** - No `.txt`, `.backup`, `.fix` files without permission
2. **Don't refactor unrelated code** - Only touch what's broken
3. **Don't guess** - If you need more context, ask questions first
4. **Don't provide incomplete solutions** - Ensure all 5 parts of a fix are included
5. **Don't assume structure** - Verify line numbers and method names first
6. **Don't mix concerns** - Keep fixes focused on the specific issue

---

## 🔧 Common Patterns in gui.py

### Timer Section (~line 1-600):
- Timer display, client/project/task selection
- Start/stop timer functionality
- Manual time entry form (rows 0-9)
- Daily totals display

### Event Handlers:
- `on_timer_client_select()` - Populates project dropdown
- `on_timer_project_select()` - Populates task dropdown (includes global tasks)
- `on_manual_client_select()` - Manual entry client selection
- `on_manual_project_select()` - Manual entry project selection

### Key Methods:
- `add_manual_entry()` (~line 1480) - Processes manual time entries
- `refresh_combos()` (~line 3260) - Populates all dropdowns on startup
- `update_daily_totals_display()` (~line 1400) - Updates today's time tracker
- `get_manual_entry_project_id()` (~line 1665) - Gets project ID for global tasks

### Database Interactions:
- All done through models: `self.client_model`, `self.project_model`, `self.task_model`, `self.time_entry_model`
- Database connection managed by `DatabaseManager` in `db_manager.py`

---

## 💾 Backup Strategy

**Before ANY code changes:**
```python
# Create timestamped backup
backup_name = f"gui.py.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
```

**Current backups in folder:**
- `gui.py.backup_manual_entry_fix` - Backup from January 13, 2026 manual entry fix

---

## 🐛 Known Issues

**Current (February 15, 2026):**
- 🔴 **Cascade Delete Not Working Reliably**: Deleting a client may not remove associated projects/tasks
  - Foreign keys are now enabled (foundation is correct)
  - Something blocking CASCADE behavior (needs investigation)
  - Workaround: Manually delete projects/tasks before deleting client
  - Priority: Medium (not launch-blocking)

**Future Enhancements:**
- PDF Invoice: Change blue banner to burnt orange #ce6427 (cosmetic)
- Theme Customizer UI: Planned as post-launch PAID feature

---

## 📚 For Reference

**User Preferences:**
- Values complete, working solutions over experimental approaches
- Wants direct, actionable fixes (not explanations of how to implement)
- Budget-conscious (previous bad experience cost $20)
- Technical but prefers AI to implement fixes rather than manual coding
- Uses PyCharm for development
- Works across two machines (synced via Google Drive)

**Communication Style:**
- Direct, uses capitals for emphasis when important
- Low tolerance for incomplete solutions or wasted time
- Will test thoroughly and report back with clear feedback
- Appreciates documentation but prefers working code

---

## 🎯 Success Criteria

When helping with this app, success means:

1. ✅ **Bug is completely fixed** - Not partially working
2. ✅ **No extra files created** - Only essential changes
3. ✅ **Backup exists** - User can revert if needed
4. ✅ **User can test immediately** - Clear instructions provided
5. ✅ **Documentation updated** - Changes are documented
6. ✅ **No new bugs introduced** - Existing features still work

---

## 📞 Starting a New Session

**Copy this to new chat:**

```
Working on Time Tracker Pro app. Context in TIMETRACKER_CONTEXT.md (knowledge base).

Current Issue: [describe issue]

Error (if any): [paste error]

[Any other relevant details]
```

---

**Last Updated:** February 15, 2026
**App Version:** V2.0.10
**Status:** ✅ Production Ready - Pre-Launch Schema Bugs Fixed!
**Recent Fixes:** Critical schema bugs for new databases (is_global column, project_id NULL, payment_terms, foreign keys enabled)
**Git Helper:** Use `git_push.bat` for commits (see GIT_USAGE.md)
