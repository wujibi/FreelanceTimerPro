# Changelog - Time Tracker Pro

All notable changes to Time Tracker Pro will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

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
