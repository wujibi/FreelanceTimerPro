# Changelog - Time Tracker Pro

All notable changes to Time Tracker Pro will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

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
