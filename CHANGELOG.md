# Changelog - Freelance Timer Pro

All notable changes to Freelance Timer Pro will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [2.0.11] - 2026-02-21

### Fixed - CASCADE DELETE BUG 🔥
- **CASCADE Delete Behavior**: Fixed critical bug where deleting Clients, Projects, or Tasks left orphaned data
  - **Bug**: Deleting projects didn't cascade delete tasks and time entries despite warning dialogs promising data would be removed
  - **Root Cause**: `Task.delete()` method (models.py line 244) was missing CASCADE logic for time_entries
  - **Fix 1**: Added CASCADE logic to `Task.delete()` (models.py lines 249-251) - deletes time_entries before task
  - **Fix 2**: Re-enabled foreign keys in theme preference methods (gui.py lines 137, 153)
  - **Testing**: Verified with Project 3 deletion test - task 4 CASCADE deleted successfully ✅
  - **GUI Test**: Deleted "Test Project DELETE" with 2 tasks and 2 time entries - all CASCADE deleted ✅

### Known Issues ⚠️
- **UI Refresh Delay**: After deletions, tabs don't auto-refresh. Users must manually switch tabs or click refresh to see changes. Data IS correctly deleted - this is purely cosmetic UX issue.
- **Orphaned Data Cleanup**: Pre-fix orphaned data (3 tasks, 1 time entry) will be manually cleaned via SQL

### Technical Details
- **Files Modified**: `models.py` (Task.delete method), `gui.py` (theme preference methods)
- **Impact**: Data integrity restored - CASCADE deletes now work correctly across entire hierarchy
- **Previous Session**: v2.0.10 fixed schema bugs earlier same day

---

## [2.0.10] - 2026-02-15

### Fixed - PRE-LAUNCH SCHEMA BUGS 🐛
- **Missing Schema Columns in Fresh Databases**: Fixed critical bugs that would crash app for new users
  - **`is_global` column**: Tasks table now includes `is_global` column on database creation
    - Bug: New databases missing column caused immediate crash
    - Fix: Added to `create_tasks_table()` (line 213) and `fix_tasks_table()` (line 359)
  - **`project_id` NULL constraint**: Removed NOT NULL constraint to allow global tasks
    - Bug: Global tasks couldn't be created (passed `project_id=None` but schema required NOT NULL)
    - Fix: Changed line 197 to allow NULL values for `project_id` when `is_global=True`
  - **`payment_terms` + `thank_you_message`**: Company info table now includes invoice fields
    - Bug: Saving company info failed with "no column named payment_terms" error
    - Fix: Added to `create_company_info_table()` (lines 251-252) and `fix_company_info_table()` (lines 397-398)
  - **Foreign Key Constraints**: Enabled CASCADE deletes for data integrity
    - Bug: Deleting clients left orphaned projects/tasks in database
    - Fix: Added `PRAGMA foreign_keys = ON` on connection (lines 27-29)
    - Note: Cascade delete behavior still needs testing/debugging

### Technical Details
- **Files Modified**: `db_manager.py` (4 critical schema fixes)
- **Impact**: These bugs would have caused immediate crashes for ANY new user on launch day
- **Testing**: Discovered during pre-launch screenshot database creation
- **Migration**: Schema fixes apply automatically via `fix_*()` methods on startup

### Known Issues
- 🔴 **Cascade Delete Not Working Reliably**: Client deletion may not remove associated projects/tasks
  - Foreign keys are now enabled (foundation is correct)
  - Something else blocking CASCADE behavior (needs investigation)
  - Workaround: Users can manually delete projects/tasks individually
  - Priority: Medium (not launch-blocking)

---

## [2.0.9] - 2026-02-10

### Added - BRANDING & UX ✨
- **Burnt Orange Professional Theme Family**: New default theme matching FreelanceTimer.pro website branding
  - `burnt_orange_pro.py` - Full burnt orange (groups + selections)
  - `burnt_orange_pro_v2.py` - Light peach groups, orange selections (two-tone hierarchy)
  - `burnt_orange_pro_v3.py` - Muted teal groups, orange selections (RECOMMENDED - strong visual contrast)
  - Warm taupe background (#dad2cd) with burnt orange accent (#ce6427)
  - Dark brown text (#13100f) for excellent readability
  - Replaces blue-based themes with warm, professional branding

- **Total Hours Display**: Invoice preview now shows total billable hours
  - "Total Hours: XX.XX hrs" displays on left side of total bar
  - "TOTAL: $XXX.XX" remains on right side
  - Helps clients understand time invested at a glance

- **Group Heading Color System**: Hierarchical treeview styling
  - Client/Project/Task rows now have distinct background colors
  - Individual time entries have white background with dark text
  - Configurable via theme `group_heading` and `group_text` colors
  - Dramatically improves visual hierarchy in Time Entries and Invoices tabs

### Fixed - CRITICAL BUGS 🐛
- **Dialog Centering**: All popup dialogs now center properly on main window
  - Fixed 718px offset bug affecting all dialogs
  - Created `center_dialog()` helper method
  - Fixed: Invoice Preview, Edit Entry, Mark as Paid, Edit Time Entries, Edit Invoice Item dialogs
  - Consistent UX across all modal windows

- **Button Text Visibility**: Fixed invisible text on accent buttons
  - **CRITICAL FIX**: "CREATE INVOICE" button now readable (was white on orange)
  - "Preview Invoice" button text now visible
  - Changed Accent.TButton from white text to dark text on orange background
  - Prevents accidental invoice creation due to unreadable button labels

- **Active Tab Text**: Tab navigation now readable
  - Fixed white-on-orange text issue (changed to dark text)
  - Active tab clearly shows which section user is in

- **Entry Row Text Colors**: Individual time entries now have proper contrast
  - Fixed alternating row colors interfering with entry readability
  - Entry rows: white background, dark text (always readable)
  - Group rows: themed background colors
  - Selected rows: orange background, white text

### Improved - UX POLISH 💎
- **Edit Workflow**: Fixed confusing auto-refresh behavior
  - Removed premature "Time entry updated" alert that appeared before editing
  - Edit Time Entries dialog no longer crashes/closes unexpectedly
  - Added clear instruction: "Click REFRESH to update the invoice data below."
  - User has explicit control over when to refresh invoice preview

- **Theme Cleanup**: Reduced from 7 experimental themes to 3 production-ready themes
  - Professional Gray (original default)
  - Dark Mode (low-light environments)
  - Burnt Orange Pro V3 (NEW DEFAULT - teal groups, best hierarchy)
  - Removed: Balanced Navy, Deep Navy Pro, Light Navy Pro, Sage Professional, Warm Professional, old Burnt Orange

### Technical
- **New Helper Method**: `center_dialog(dialog, width, height)` in gui.py
- **Tag System**: Added `client_row`, `project_row`, `task_row`, `entry_row` tags for treeview styling
- **Theme Files**: 3 new burnt orange theme variants in themes/ folder
- **Color Reference**: Created BURNT_ORANGE_COLOR_MAP.html (visual guide for all UI component colors)

### Known Issues
- PDF Invoice: Total hours not yet added to generated PDF (preview only)
- PDF Invoice: Blue banner needs to be changed to burnt orange (cosmetic)
- Theme Customizer UI: Planned as post-launch PAID feature

---

## [2.0.8] - 2026-02-04

### Added - NEW FEATURES ✨
- **Theme System**: Modular theme/stylesheet system implemented
  - Separated colors and fonts from gui.py into theme modules
  - Created `themes/` folder with pluggable theme architecture
  - Two starter themes: Professional Gray (default), Dark Mode
  - Easy to create custom themes by copying existing theme file
  
- **Live Theme Switcher**: Frontend theme selector in Company Info tab
  - Dropdown menu in "🎨 Appearance" section
  - Apply themes without restarting app (most changes instant)
  - Theme preference persists across sessions (saved to database)
  - New `settings` table stores user preferences

### Changed - REBRANDING 🎯
- **Application Name**: Renamed from "Time Tracker Pro" to "Freelance Timer Pro"
  - Window title updated
  - Documentation updated (CHANGELOG, README, guides)
  - Prepared for public release with new brand identity
  - Internal database files unchanged (no data migration needed)

### Documentation 📚
- **THEME_SWITCHER_GUIDE.md**: Complete guide to using and creating themes
  - How to switch themes via frontend
  - Step-by-step theme creation instructions
  - Example color palettes (Corporate Blue, Sunset Orange, Ocean Teal, Forest Green)
  - Testing checklist and troubleshooting
  
- **APP_RENAME_GUIDE.md**: Guide for future name changes
  - PyCharm Find/Replace strategy
  - Database migration considerations
  - Testing checklist

### Technical Details
- **New Files**: 
  - `themes/__init__.py` - Theme registry
  - `themes/professional_gray.py` - Default theme (extracted from gui.py)
  - `themes/dark_mode.py` - Dark theme for reduced eye strain
  - `themes/README.md` - Full theme system documentation
  
- **Database Schema**: Added `settings` table
  ```sql
  CREATE TABLE settings (
      key TEXT PRIMARY KEY,
      value TEXT
  )
  ```
  
- **New Functions in gui.py**:
  - `load_theme_preference()` - Loads saved theme from database
  - `save_theme_preference()` - Saves theme choice to database
  - `switch_theme()` - Applies new theme and saves preference
  
- **Initialization Order**: Database now initializes BEFORE theme loading (required for loading saved preference)

---

## [2.0.7] - 2026-02-03

### Fixed - CRITICAL BUG FIXES 🐛
- **Email Template Save Bug**: Custom email template edits now persist correctly
  - Root cause: Duplicate `load_selected_template()` function at end of gui.py
  - Second function was overriding first and only loading from built-in defaults
  - Fixed to check database first, then fall back to defaults
  - Template customizations now save and load properly
  - Users can now customize invoice email templates successfully

- **Task Deletion Bug**: Tasks now delete correctly from Tasks tab
  - Root cause: Attempting to extract task_id from `values[0]` which contained "Task" string
  - Fixed to extract task_id from item tags (`task_id_123` format)
  - Deletion now works reliably for all task types (regular and global)

### Improved
- **Email Template Preview**: HTML now renders as readable text
  - Strips HTML tags for clean preview
  - Converts `<br>` and `</p>` to newlines
  - Decodes HTML entities (&nbsp;, etc.)
  - Removes excessive whitespace
  - Note: Styling preview (colors, borders) not shown - planned for future enhancement

- **Code Cleanup**: Removed debug print statements
  - Cleaned up version banner prints
  - Removed template save/load debug messages
  - Cleaner console output

### Technical Details
- **Files Modified**: `gui.py` (2 bug fixes, 1 enhancement)
- **Functions Fixed**:
  - `load_selected_template()` - Now checks database before defaults
  - `delete_task()` - Now extracts task_id from tags correctly
  - `update_template_preview()` - Added HTML stripping for readable preview

---

## [2.0.6] - 2026-01-30

### Changed - UI REORGANIZATION 🎨
- **Tab Bar Cleanup**: Reduced main tab count from 9 to 7 tabs
  - Moved "Billed Invoices" into Invoices tab as submenu item
  - Moved "Email Settings" and "Email Templates" into single Email tab with submenus
  - Added dropdown navigation at top of Invoices and Email tabs
  - Invoices submenu: "📄 Create Invoice" | "💰 Paid/Unpaid Invoices"
  - Email submenu: "⚙️ Settings" | "📝 Templates"
  - Less cluttered interface, better organization

- **Tab Appearance**: Fixed selected tab visual style
  - Changed theme from 'clam' to 'alt' to remove raised tab effect
  - Selected tab now stays same height as other tabs
  - Blue highlight indicates active tab clearly
  - Cleaner, more professional look

### Added
- **Git Helper Scripts**: Created reusable git workflow tools
  - `git_push.bat` - Generic script for committing/pushing changes
  - `GIT_USAGE.md` - Complete usage guide and troubleshooting
  - Prompts for version number, title, and detailed changes
  - Replaces hardcoded version-specific scripts

### Removed
- **Obsolete Documentation**: Cleaned up 13 temporary/old files
  - Session-specific docs (COMPLETE_VERIFICATION_TEST.md, etc.)
  - Old git scripts (GIT_COMMANDS_TODAY.bat, etc.)
  - Bug fix docs (INVOICE_BUG_FIX.md, etc.)
  - Backup files (gui.py.backup_invoice_bug)

### Technical Details
- **Files Modified**: `gui.py` (~800 lines refactored)
- **New Methods**:
  - `create_email_tab()` - Combined email views with submenu
  - `show_email_view()` - Switch between Settings/Templates
  - `create_email_settings_view()` - Settings subview
  - `create_email_templates_view()` - Templates subview
  - `create_invoice_create_view()` - Create invoice subview
  - `create_invoice_billed_view()` - Paid/Unpaid invoices subview
  - `show_invoice_view()` - Switch between invoice views
- **Theme Change**: `style.theme_use('alt')` instead of 'clam'
- **All Functionality Preserved**: Email and invoice features work identically

---

## [2.0.5] - 2026-01-29

### Added - EMAIL INVOICE FEATURE 🎉
- **Complete Email Invoice System**: Send invoices directly from the app with PDF attachments
  - New "📧 Email Invoice" button in invoice preview dialog
  - Auto-generates PDF invoice in temp folder, attaches to email, then cleans up
  - Optional: Mark time entries as billed after sending
  - Shows success/failure messages with details

- **Email Settings Tab**: Full SMTP configuration interface
  - Provider presets (Gmail, Outlook, Custom) with auto-fill
  - SMTP server, port, email address, app password fields
  - "From Name" field for professional sender display
  - Password visibility toggle
  - Test connection button with detailed error messages
  - Settings persist to database and auto-load on startup
  - Gmail App Password instructions built-in

- **Email Templates Tab**: Manage email templates with live preview
  - 5 built-in templates: Professional, Friendly, Formal, Reminder, Thank You
  - Template editor with subject and HTML body
  - Variable insertion buttons (Client Name, Invoice #, Total, Date, Company)
  - Live preview with sample data
  - Save custom templates to database
  - Reset to default functionality
  - Send test email button

- **Email Sender Module** (`email_sender.py`):
  - `EmailSender` class: Handles SMTP connection and sending
  - `EmailTemplate` class: Template management and variable substitution
  - Support for CC/BCC addresses
  - HTML email body support
  - PDF attachment handling
  - Connection testing with helpful error messages
  - 13 template variables available: client info, invoice details, company info

- **Database Tables**:
  - `email_settings` - Stores SMTP configuration
  - `email_templates` - Stores custom email templates
  - Added email tracking columns to `billing_history` table

### Fixed
- **Task Edit Bug**: Fixed critical bug where updating task rates didn't persist to database
  - Issue: `update_task()` extracted task_id from wrong tree column (values vs tags)
  - Solution: Extract task_id from tags (`task_id_123`) instead of values column
  - All task updates (rate changes, name changes) now work correctly

- **Tree Collapse Issue**: Fixed annoying UX bug where trees collapsed after every edit
  - Added `save_tree_state()` and `restore_tree_state()` helper methods
  - All three tabs maintain expansion state: Tasks, Time Entries, Invoice
  - Trees now default to fully expanded on load
  - No more clicking through folders after every update!

- **Edit Time Entries from Invoice Tab**: Can now edit entries before creating invoice
  - Added "✏️ Edit Entry" button to Invoice tab main screen
  - Added "✏️ Edit Entries" button to invoice preview dialog
  - Edit dialog appears in front (not hidden behind main window)
  - Modal dialog with proper positioning (transient, lift, focus_force, grab_set)
  - Auto-refreshes invoice list after editing
  - No premature refresh alerts

- **Dialog Positioning**: Fixed edit dialogs appearing behind main window
  - Applied proper modal behavior: transient, grab_set, lift, focus_force
  - Dialogs center on parent window
  - Callback-based refresh (no immediate refresh on open)

- **Whitespace on Startup**: Removed 292px blank area on right side of window
  - Removed Timer tab scrollbar completely
  - Cleaner, more professional appearance

- **ReportLab Installation**: Fixed missing dependency for PDF generation
  - Added to requirements.txt
  - Required for email invoice feature

- **Email Settings Persistence**: Settings now auto-load on app startup
  - Added `load_email_settings_silent()` method (no popup)
  - Called automatically in `refresh_all_data()`
  - Auto-detects provider (Gmail/Outlook/Custom) from SMTP server
  - Settings saved and restored correctly across app restarts

### Changed
- **Import Statements**: Added `tempfile` and `os` imports for email feature
- **Email Settings Auto-Load**: Settings now load silently on startup (no popup)
- **Template Dropdown**: Auto-populates with 5 built-in templates on startup

### Technical Details
- **Files Modified**: 
  - `gui.py` - Added email dialog, settings methods, template methods (~260 new lines)
  - `email_sender.py` - New file (~350 lines)
  - `db_manager.py` - Email settings/templates methods already existed
  - `requirements.txt` - Added reportlab>=3.6.0

- **New Methods in gui.py**:
  - `show_email_invoice_dialog()` - Main email dialog with template rendering
  - `save_email_settings()` - Save SMTP config to database
  - `load_email_settings()` - Load SMTP config (with popup)
  - `load_email_settings_silent()` - Load SMTP config (silent)
  - `_populate_email_settings()` - Helper to fill form fields
  - `test_email_connection()` - Test SMTP connection
  - `on_email_provider_select()` - Auto-fill SMTP details
  - `toggle_password_visibility()` - Show/hide password
  - `save_current_template()` - Save template to database
  - `load_selected_template()` - Load template from dropdown
  - `reset_template_to_default()` - Reset to built-in template
  - `insert_variable()` - Insert variable at cursor
  - `update_template_preview()` - Render preview with sample data
  - `send_test_template_email()` - Send test email to self
  - `refresh_email_templates()` - Populate template dropdown
  - `save_tree_state()` - Save expanded tree items
  - `restore_tree_state()` - Restore expanded tree items

- **Database Methods** (in db_manager.py):
  - `get_email_settings()` - Retrieve SMTP config
  - `save_email_settings()` - Save SMTP config
  - `get_email_templates()` - Get all templates
  - `get_email_template()` - Get specific template
  - `save_email_template()` - Save/update template
  - `delete_email_template()` - Delete template

### Session Highlights
- **Major UX Improvements**: Tree expansion state, edit from invoice tab, dialog positioning
- **Complete Email System**: From SMTP config to template rendering to PDF attachment
- **Production Tested**: Successfully sent real invoice via email with PDF attachment
- **Token Efficient**: Completed in ~116k tokens with surgical code edits

---

## [2.0.4] - 2026-01-21

### Added
- **Invoice Tab Hierarchical Grouping**: Invoice tab now displays time entries grouped by Project → Task → Individual Entries
  - Matches the hierarchy used in Time Entries tab and invoice preview/PDF
  - Shows subtotals for each project and task
  - Individual time entries are expandable under their parent task
  - Visual indicators: 📁 Projects, 📋 Tasks, ⏱️ Individual Entries
  - Date format includes time: `01/21/26 2:30 PM`
  - Makes it much easier to see what you're about to bill

### Fixed
- **Time Entry Edit Bug**: Fixed critical bug where certain time entries couldn't be edited
  - Root cause: `edit_time_entry()` used complex JOINs that failed on global tasks (where `project_id = NULL`)
  - Solution: Simplified to query directly from `time_entries` table which contains denormalized data
  - Fixed column indices to match actual schema
  - Improved error messages to include entry ID for debugging
  - All time entries can now be edited regardless of task type
- **Invoice Tab Select/Deselect Buttons**: Fixed buttons to work with hierarchical structure
  - Select All now recursively finds and selects only actual time entries (not headers)
  - Auto-expands all projects/tasks when Select All is clicked (no manual expanding needed)
  - Deselect All properly clears current selection
  - Buttons now work correctly with grouped display

### Changed
- **Invoice Tab Layout**: Completely redesigned entry selection interface
  - Changed from flat list to hierarchical tree structure
  - Only individual entries are selectable (not project/task headers)
  - Entry selection logic updated to handle nested structure
  - Summary label now shows accurate count of actual entries (not including headers)

### Technical Details
- **Files Modified**: `gui.py`
- **Methods Updated**:
  - `load_invoiceable_entries()` - Added project/task grouping logic with subtotals
  - `edit_time_entry()` - Simplified query to use denormalized columns
  - `select_all_invoice_entries()` - Added recursive selection with auto-expand
  - `deselect_all_invoice_entries()` - Fixed to clear actual selection
- **No Database Changes**: Uses existing schema with denormalized columns
- **Lines Modified**: ~1115 (edit fix), ~3467-3543 (invoice grouping), ~3543-3565 (select buttons)

### Removed
- Cleaned up temporary patch files and update scripts:
  - `gui_invoice_grouped.patch`
  - `gui_load_invoiceable_backup.py`
  - `update_load_invoiceable.py`

---

## [2.0.3] - 2026-01-15

### Fixed
- **Invoice Tab Loading Bug**: Fixed critical bug where Invoice tab was not loading time entries that used global tasks
  - Changed SQL JOIN from `tasks.project_id` to `time_entries.project_id` in 5 queries
  - Global tasks have `tasks.project_id = NULL`, causing JOIN failures and missing entries
  - Affected methods: `load_invoiceable_entries()` and `show_invoice_preview_dialog()`
  - All unbilled entries now appear in Invoice tab regardless of task type
  - Fixes issue where only some entries would load when selecting a client
  - Invoice generation now works correctly for all task types

### Technical Details
- **Root Cause**: Global tasks store NULL in `tasks.project_id`, but time entries always store a valid `project_id`
- **Solution**: Join through `time_entries.project_id` instead of `tasks.project_id`
- **Files Modified**: `gui.py` (lines ~3424, ~3434, ~3453, ~3465, ~3568)
- **Queries Updated**: 4 in `load_invoiceable_entries()`, 1 in `show_invoice_preview_dialog()`
- **Impact**: Invoice tab, invoice preview, and PDF generation all work with global task entries

### Removed
- Cleaned up temporary utility scripts and documentation from development
- Removed backup files and one-time troubleshooting documents

---

## [2.0.2] - 2026-01-13

### Fixed
- **Manual Entry with Global Tasks**: Fixed critical bug preventing manual time entries when using global tasks
  - Added Client and Project dropdowns to manual entry form (matching Timer section layout)
  - Added `project_id_override` parameter to `TimeEntry.add_manual_entry()` method
  - Manual entry form now properly passes project context for global tasks
  - Fixed `ValueError: Global tasks require a project context` error
- **Daily Totals Display**: Manual entries now correctly update "Today's Time by Client" section
  - Rewrote daily totals update logic to read from form dropdowns instead of parsing task text
  - Works for both global and project-specific tasks
  - Displays time grouped by Client → Project as expected
- **Manual Entry Combo Population**: Client dropdown now populates on app startup
  - Added `self.manual_client_combo['values']` to `refresh_combos()` method
  - Matches pattern used for Timer and Invoice dropdowns

### Added
- New event handlers for manual entry form:
  - `on_manual_client_select()` - Populates projects when client selected
  - `on_manual_project_select()` - Populates tasks when project selected
  - `get_manual_entry_project_id()` - Helper to get project ID for global task context
- **Documentation**: Added `TIMETRACKER_CONTEXT.md` for AI assistant handoff
- **Documentation**: Added `MANUAL_ENTRY_FIX_COMPLETE.md` with detailed fix explanation
- **Utility**: Added `cleanup_junk_files.py` to remove temporary files from failed debugging session
- **Utility**: Added `git_push_instructions.md` for Git workflow reference

### Changed
- Manual entry form layout updated (rows 6-9):
  - Row 6: Client dropdown (new)
  - Row 7: Project dropdown (new)
  - Row 8: Task dropdown (moved from row 6)
  - Row 9: Description (moved from row 7)
- `models.py`: `add_manual_entry()` signature updated with `project_id_override` parameter
- `gui.py`: Lines modified:
  - ~350-365: Added Client/Project dropdowns to form
  - ~1535: Updated `add_manual_entry()` call with project context
  - ~1610: Updated `clear_manual_entry_form()` to clear new dropdowns
  - ~1600-1665: Added three new helper methods
  - ~1552-1595: Rewrote daily totals update logic
  - ~3267: Added manual client combo to `refresh_combos()`

### Removed
- Deleted 15 temporary files from previous failed debugging session:
  - `Backup_GUI.txt`, `FINAL_FIX.txt`, `FIX_INSTRUCTIONS.txt`
  - `GUI_FIX_INSTRUCTIONS.md`, `FIXES_SUMMARY.md`, `README_FIXES.md`
  - `QUICKFIX_gui_syntax.md`, `add_time_entries_filter.p.py`
  - Various temporary `.py` scripts

### Technical
- Files modified: `gui.py` (4,702 lines), `models.py`
- Database schema: No changes required
- Dependencies: No new dependencies
- Git commit: `d24d943`

---

## [2.0.1] - 2026-01-10

### Added
- **Excel Export Feature**: Export time entries to .xlsx spreadsheet files
  - Export all entries based on current filter (Unbilled/Billed/All)
  - Export selected entries only (multi-select support)
  - Professional formatting with blue headers and auto-sized columns
  - Columns: Date, Client, Project, Task, Start Time, End Time, Duration (hrs), Description, Billed Status, Invoice #
  - Option to open file immediately after export
  - Automatic filename generation with date stamp
- Added `openpyxl` library dependency for Excel file generation

### Changed
- Updated app title to "Time Tracker Pro v2.0"
- Improved time entries selection UX messaging

### Fixed
- PyCharm virtual environment configuration for consistent package installation
- Cache invalidation for reliable code updates during development

---

## [2.0.0] - 2026-01-10

### Added
- **New Clock Icon**: Updated application icon from feather to clock design
  - Applied to desktop shortcut, start menu, taskbar, and title bar
- **Time Entries Filter**: Radio button filters for time entries view
  - ✅ Unbilled Only (default) - Hide invoiced entries
  - 💰 Billed Only - Show only invoiced entries
  - 📋 All Entries - Show everything
  - Filter persists when refreshing entries

### Changed
- Version number bumped to v2.0 to reflect major feature additions
- Icon asset updated in `assets/icon.ico`

---

## [1.1.1] - 2026-01-08

### Added
- **Hierarchical Task Display**: Tasks tab now shows tasks grouped by Client → Project → Task
  - Collapsible tree structure similar to Time Entries tab
  - Global tasks displayed in separate [GLOBAL TASKS] section
  - Visual indicators: 📁 Clients, 📂 Projects, ⚙️ Tasks

### Changed
- Improved task list readability with hierarchical organization
- Global tasks now clearly separated at bottom of list

---

## [1.1.0] - 2026-01-07

### Added
- **Global Tasks Feature**: Tasks can now be marked as global and will appear for all projects
  - Added "Global Task" checkbox in Tasks tab
  - Global tasks show with [GLOBAL] prefix in timer dropdown
  - Database migration to add `is_global` column to tasks table
  - Client/Project fields automatically disable when creating global tasks

### Changed
- Updated Task model to support nullable `project_id`
- Enhanced timer task dropdown to show both project-specific and global tasks
- Modified task creation workflow to handle global vs project-specific tasks

### Fixed
- Task creation validation for global tasks
- Timer dropdown now properly combines global and project tasks

### Technical
- Migration script: `add_global_tasks.py`
- Database schema: Added `is_global` BOOLEAN column to `tasks` table
- Updated `Task.get_global_tasks()` and `Task.get_all_for_project()` methods

---

## [1.0.0] - 2025-12-10

### Major Release - Google Drive Sync Edition

### Added
- **Google Drive Sync** - Automatic database synchronization across multiple computers
- **Configuration System** - Centralized config.py for easy path management
- Complete time tracking functionality
- Client, Project, and Task management
- Manual and automatic time entry
- Invoice generation with PDF export
- Company information management
- Billing history tracking

### Changed
- **BREAKING:** Renamed database.py to db_manager.py
- **BREAKING:** DatabaseManager.__init__() now requires db_path parameter
- Updated all imports from database to db_manager

### Fixed
- Fixed nested class declarations causing initialization failures
- Fixed duplicate method definitions
- Fixed context manager protocol implementation
- Fixed database path handling with spaces

---

## Contributors
- Brian Hood (@wujibi) - Lead Developer

## License
Proprietary - All Rights Reserved
