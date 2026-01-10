# Changelog - Time Tracker Pro

All notable changes to Time Tracker Pro will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

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
