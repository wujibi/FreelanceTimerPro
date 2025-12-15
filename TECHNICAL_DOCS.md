# Time Tracker Pro - Technical Documentation

**Last Updated:** December 10, 2025 

**Status:** ✅ Fully Functional with Google Drive Sync

---

## 📋 Table of Contents

1\. [Current Setup](#current-setup)

2\. [Recent Changes & Fixes](#recent-changes--fixes)

3\. [File Structure](#file-structure)

4\. [Google Drive Sync](#google-drive-sync)

5\. [Known Issues & Solutions](#known-issues--solutions)

6\. [Future Enhancements](#future-enhancements)

7\. [Troubleshooting Guide](#troubleshooting-guide)

---

## 🔧 Current Setup

### System Information

- **Python Version:** 3.13.9

- **Primary Location:** `C:\Users\briah\Custom Apps\TimetrackerAppV1\`

- **Database Location:** `C:\Users\briah\My Drive\TimeTrackerApp\data\time_tracker.db`

- **Sync Method:** Google Drive Desktop (automatic background sync)

### Key Dependencies

tkinter (built-in)  
sqlite3 (built-in)  
reportlab (for PDF invoice generation)

### Installation on New Machine

```bash

# 1\. Clone/copy the project folder

# 2\. Install Python 3.6+

# 3\. Install dependencies

pip install reportlab

# 4\. Run the app

python launcher.py

**🔄 Recent Changes & Fixes**

**Major Issue Resolved (Dec 10, 2025)**

**Problem:** App wouldn't launch after attempting Google Drive sync implementation.

**Root Causes Found:**

1.  **Duplicate database.py files** -      Project file conflicted with pip's internal database.py

1.  **Nested      class declarations** - class DatabaseManager was declared      twice (nested)

1.  **Duplicate      methods** - Two get_connection() and setup_database() methods

1.  **Missing @contextmanager implementation** -      Context manager protocol not properly implemented

**Solutions Applied:**

1.  ✅      Renamed database.py → db_manager.py to avoid naming      conflicts

1.  ✅      Updated all imports: from database import → from db_manager      import

1.  ✅      Fixed DatabaseManager.__init__ to accept db_path parameter

1.  ✅      Implemented proper @contextmanager with try/finally block

1.  ✅      Removed duplicate method declarations

1.  ✅      Created config.py for centralized database path management

**Files Modified**

*   ✅ database.py →      renamed to db_manager.py

*   ✅ gui.py -      Updated imports and added db_path parameter

*   ✅ main.py -      Simplified to use config.py

*   ✅ models.py -      Updated imports

*   ✅ config.py -      Created new (replaces broken version)

**📁 File Structure**

TimetrackerAppV1/

├── launcher.py # App entry point with pre-flight checks

├── main.py # Main application launcher

├── config.py # Database path configuration ⭐ NEW

├── db_manager.py # Database operations (was database.py)

├── gui.py # Main GUI application

├── models.py # Data models (Client, Project, Task, etc.)

├── invoice_generator.py # PDF invoice generation

├── data/ # Local backup folder

│ └── time_tracker.db # Local database backup

└── .venv/ # Virtual environment

**Google Drive Structure**

C:\Users\briah\My Drive\

└── TimeTrackerApp/

└── data/

└── time_tracker.db # Synced database

**☁️ Google Drive Sync**

**How It Works**

The app uses Google Drive Desktop's automatic background sync by storing the database in a monitored folder.

**Configuration (config.py)**

# Database path points to Google Drive folder

DB_PATH = r"C:\Users\briah\My Drive\TimeTrackerApp\data\time_tracker.db"

# Automatic fallback to local if Google Drive unavailable

if not os.path.exists(db_dir):

DB_PATH = os.path.abspath("data/time_tracker.db")

**Usage Rules ⚠️**

1.  **Close      app on Machine A before opening on Machine B**

1.  **Wait      30-60 seconds** after closing for sync to complete

1.  **Never      run simultaneously** on multiple computers

1.  Verify      Google Drive sync icon shows complete before switching

**Setting Up Second Computer**

1.  Install      Google Drive Desktop

1.  Copy      entire project folder to second computer

1.  Ensure config.py points      to same Google Drive path

1.  Run python      launcher.py

1.  Database      will automatically sync via Google Drive

**❗ Known Issues & Solutions**

**Issue: "DatabaseManager() takes no arguments"**

**Cause:** Cached .pyc files or nested class declarations  
**Solution:**

# Clear cache

del /s /q __pycache__

del /s /q *.pyc

# Verify db_manager.py has single class declaration

# Check line 14: should be "class DatabaseManager:" (only once)

**Issue: "generator object does not support context manager protocol"**

**Cause:** @contextmanager decorator not properly implemented  
**Solution:** Ensure get_connection() has try/finally block:

@contextmanager

def get_connection(self):

try:

yield self.conn

finally:

pass

**Issue: Blank window on launch**

**Cause:** Silent exception in GUI initialization  
**Solution:** Check console output for traceback, ensure all imports use db_manager

**Issue: Database locked error**

**Cause:** App running on multiple machines simultaneously  
**Solution:** Close app on one machine, wait for sync, then open on other

**🚀 Future Enhancements**

**Priority 1 - Safety Features**

*   **Auto-backup      before sync** - Create local backup before using synced database

*   **Conflict      detection** - Warn if database modified on both machines

*   **Sync      status indicator** - Visual indicator showing sync state

*   **Read-only      mode** - Option to open database in read-only mode for viewing

**Priority 2 - Sync Improvements**

*   **Export/Import      feature** - Manual export for extra safety

*   **Last-modified      timestamp** - Track which machine last modified database

*   **Sync      log** - Record sync events and conflicts

*   **Multi-user      support** - Allow simultaneous use (requires major architecture      change)

**Priority 3 - Features**

*   **Dark      mode** - UI theme option

*   **Reports      dashboard** - Visual analytics for time tracking

*   **CSV      export** - Export time entries to spreadsheet

*   **Custom      invoice templates** - User-defined invoice layouts

*   **Automated      reminders** - Remind to stop timer or submit invoices

**Priority 4 - Advanced Sync**

*   **Google      Drive API integration** - True multi-user sync

*   **Cloud      database** - PostgreSQL/MySQL hosted solution

*   **Conflict      resolution UI** - Visual merge tool for conflicts

*   **Version      history** - Browse previous database versions

**🔍 Troubleshooting Guide**

**App Won't Launch**

**Step 1:** Check console output

python launcher.py

# Look for error messages in red

**Step 2:** Verify imports

# Search for old import statements

findstr /s "from database import" *.py

# Should only find references in comments, not actual imports

**Step 3:** Clear cache

del /s /q __pycache__

del /s /q *.pyc

**Step 4:** Verify database path

# Check if database file exists

dir "C:\Users\briah\My Drive\TimeTrackerApp\data\time_tracker.db"

# Check if database file exists

dir "C:\Users\briah\My Drive\TimeTrackerApp\data\time_tracker.db"

**Database Issues**

**Corrupted Database:**

# Restore from local backup

copy "C:\Users\briah\Custom Apps\TimetrackerAppV1\data\time_tracker.db" ^

"C:\Users\briah\My Drive\TimeTrackerApp\data\"

**Sync Conflicts:**

1.  Close      app on both machines

1.  Choose      most recent version (check file modified date)

1.  Delete      older version

1.  Wait      for sync to complete

1.  Open      app on one machine to verify

**Import Errors**

**Module not found:**

# Check which database module is being imported

python -c "import db_manager; print(db_manager.__file__)"

# Should show your project path, not site-packages

**📝 Development Notes**

**Critical Code Sections**

**Database Initialization** (db_manager.py lines 14-49):

*   Must      have single class declaration

*   __init__ must      accept db_path parameter with default value

*   Connection      must be initialized before use

**Context Manager** (db_manager.py lines 50-55):

*   Requires @contextmanager decorator

*   Must      use try/finally pattern

*   Should      yield self.conn

**GUI Initialization** (gui.py lines 14-60):

*   Must      accept db_path parameter

*   Should      have error handling with traceback

*   Models      must be initialized after database

**Testing Checklist**

Before committing changes:

*   App      launches without errors

*   All      tabs display correctly

*   Timer      starts/stops successfully

*   Can      add clients/projects/tasks

*   Can      generate invoices

*   Database      syncs to Google Drive

*   No      duplicate class/method declarations

*   All      imports use db_manager (not database)

**🆘 Emergency Recovery**

If app is completely broken:

**Step 1: Backup current state**

bash

xcopy /E /I "C:\Users\briah\Custom Apps\TimetrackerAppV1" ^

"C:\Users\briah\Custom Apps\TimetrackerAppV1_BACKUP"

**Step 2: Reset to working state**

1.  Delete config.py if      exists

1.  Verify db_manager.py has      single class declaration (line 14)

1.  Clear      all cache: del /s /q __pycache__ *.pyc

1.  Use      local database temporarily:

python

# In main.py

db_path = os.path.abspath('data/time_tracker.db')

**Step 3: Test basic functionality**

bash

python launcher.py

# Verify app loads with local database

**Step 4: Re-enable Google Drive sync**

1.  Verify      database copied to Google Drive

1.  Recreate config.py from      template above

1.  Update main.py to      import from config

1.  Test      thoroughly before using on second machine

**📞 Support Information**

**When Starting New Chat Session**

Provide this context:

1.  "Working      on Time Tracker Pro app"

1.  "Using      Python 3.13.9 with tkinter"

1.  "Database:      SQLite synced via Google Drive"

1.  "Main      file: db_manager.py (NOT database.py)"

1.  "Last      working version: Dec 10, 2025"

**Key Files to Share**

*   db_manager.py -      Database operations

*   config.py -      Configuration

*   main.py -      Entry point

*   Console      output showing error messages

**Important Constraints**

*   ⚠️      Never have duplicate class declarations

*   ⚠️      Always use db_manager for imports (not database)

*   ⚠️      Database path must be string, not Path object

*   ⚠️      Context manager must have try/finally block

*   ⚠️      Only one machine should run app at a time

**📄 License & Credits**

**Developer:** Brian (briah)  
**AI Assistant:** Claude (Anthropic)  
**Development Date:** December 2025  
**Version:** 1.0 (Google Drive Sync Edition)

**Document Version:** 1.0  
**Last Updated:** December 10, 2025, 1:30 PM EST

---

Save this as `TECHNICAL_DOCS.md` in your repository root. This document contains everything needed to:

1\. Understand the current state of the app

2\. Troubleshoot common issues

3\. Set up on a second machine

4\. Continue development in future sessions

5\. Recover from breaking changes