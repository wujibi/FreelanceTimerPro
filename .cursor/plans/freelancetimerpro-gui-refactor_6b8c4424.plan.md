---
name: freelancetimerpro-gui-refactor
overview: Refactor the monolithic Tkinter GUI into a smaller, modular architecture and then introduce a parallel PyQt6 UI layer while preserving core behavior.
todos:
  - id: analyze-current-gui
    content: Analyze the existing gui.py and entrypoint to identify responsibilities and current architecture
    status: completed
  - id: design-target-structure
    content: Design the concrete Python package/module structure for core logic, Tkinter UI, and utilities
    status: completed
  - id: refactor-gui-phase1
    content: Refactor gui.py into smaller modules (core, config, persistence, Tkinter UI) while keeping behavior stable
    status: in_progress
  - id: stabilize-and-package
    content: Run tests/manual QA and ensure the Tkinter version still builds and runs correctly as an .exe
    status: pending
  - id: implement-pyqt6-layer
    content: Create the PyQt6 UI package that reuses the refactored core logic and supports all main workflows
    status: pending
  - id: switch-primary-frontend
    content: Update packaging and entrypoints so the PyQt6 UI becomes the primary frontend once stable
    status: pending
isProject: false
---

# FreelanceTimerPro GUI Refactor and PyQt6 Migration

## Goals

- **Phase 1**: Reduce the size and complexity of `gui.py` by extracting responsibilities into focused modules, improving testability and long-term maintainability while keeping core behavior intact.
- **Phase 2**: Introduce a new PyQt6-based UI that reuses the refactored core logic and can eventually replace the Tkinter frontend.

## Current-State Assessment

- **Inspect `gui.py`**: Identify concerns mixed into the file:
  - UI composition (window, frames, widgets, dialogs, menus).
  - Event wiring and callbacks.
  - Business logic (time tracking, billing calculations, report/export logic).
  - Persistence and configuration (settings, paths, user preferences).
  - Background work (timers, scheduling, any threads or `after` callbacks).
- **Identify entrypoint and packaging**:
  - Confirm how the app is started (e.g. `main.py` or directly running `gui.py`).
  - Note how the existing `.exe` is built so the new structure keeps packaging simple.

## Target Architecture for the Tkinter Version (Phase 1)

We move from a single large `gui.py` to a small set of cohesive modules, for example:

- **Application entrypoint**
  - `[app/main.py](app/main.py)` (or your existing entry module): creates the application object, sets up logging/config, and launches the Tkinter UI.
- **Core/domain logic (UI-independent)**
  - `[app/core/timer.py](app/core/timer.py)`: time tracking, start/stop/pause/resume, elapsed calculations.
  - `[app/core/projects.py](app/core/projects.py)`: projects/clients/tasks and billing rules.
  - `[app/core/reports.py](app/core/reports.py)`: aggregation and export-friendly data structures.
  - `[app/core/persistence.py](app/core/persistence.py)`: loading/saving sessions, basic database or file access abstractions.
- **Configuration and utilities**
  - `[app/config.py](app/config.py)`: constants, default settings, paths, feature flags.
  - `[app/utils/formatting.py](app/utils/formatting.py)`: formatting durations, money, date/time.
  - `[app/utils/threads.py](app/utils/threads.py)` or `[app/utils/scheduling.py](app/utils/scheduling.py)`: timer/scheduler helpers if needed.
- **Tkinter UI layer**
  - `[app/ui/tk/__init__.py](app/ui/tk/__init__.py)`: exports the Tkinter `App` class.
  - `[app/ui/tk/app.py](app/ui/tk/app.py)`: main window, high-level layout, menu/toolbar.
  - `[app/ui/tk/widgets.py](app/ui/tk/widgets.py)` or a widgets package for reusable custom controls.
  - `[app/ui/tk/dialogs.py](app/ui/tk/dialogs.py)`: settings dialogs, confirmation prompts, file pickers.
  - `[app/ui/tk/theme.py](app/ui/tk/theme.py)`: color palette, fonts, styling helpers.

Conceptually, the layering looks like this:

```mermaid
flowchart TD
  user[User] --> tkUi[TkUiLayer]
  tkUi --> coreLogic[CoreDomainLogic]
  coreLogic --> persistence[Persistence]
  coreLogic --> utils[Utilities]

  user --> qtUi[QtUiLayer (Phase2)]
  qtUi --> coreLogic
```



## Phase 1: Step-by-Step Refactor of `gui.py`

- **1. Introduce a minimal `App` class and entrypoint**
  - If `gui.py` currently runs code at module import (`if __name__ == "__main__"` block or top-level widget creation), move that into `[app/main.py](app/main.py)` or a new entry file.
  - Wrap the main Tkinter window and top-level UI wiring in an `App` class in `[app/ui/tk/app.py](app/ui/tk/app.py)` and have the entrypoint simply instantiate and `run()` it.
- **2. Extract configuration and constants**
  - Move all hardcoded strings, colors, font definitions, default paths, and magic numbers from `gui.py` into `[app/config.py](app/config.py)` and `[app/ui/tk/theme.py](app/ui/tk/theme.py)`.
  - Keep UI-agnostic config (e.g. default workday length) in `config.py` and visual details (colors/fonts) in `theme.py`.
- **3. Extract core business logic out of the GUI**
  - Identify pure logic currently inside callbacks (e.g. computing billable hours, building CSV rows, summarizing sessions).
  - Move this into `[app/core/timer.py](app/core/timer.py)`, `[app/core/projects.py](app/core/projects.py)`, and `[app/core/reports.py](app/core/reports.py)` as appropriate.
  - Change GUI callbacks so they call these core functions/classes instead of containing calculations inline.
- **4. Extract persistence and I/O**
  - If `gui.py` reads/writes files, touches SQLite, or does any network calls, relocate that code into `[app/core/persistence.py](app/core/persistence.py)` or a dedicated persistence module.
  - Define clean, UI-agnostic interfaces, e.g. `load_sessions()`, `save_sessions(sessions)`, `export_report(data, path)`.
- **5. Organize dialogs and custom widgets**
  - Find any repeated dialog patterns or custom composite widgets in `gui.py` (e.g. settings dialog, project editor, confirmation prompts).
  - Move these into `[app/ui/tk/dialogs.py](app/ui/tk/dialogs.py)` and `[app/ui/tk/widgets.py](app/ui/tk/widgets.py)` as separate classes.
  - Update the main `App` class to construct and show them via methods (e.g. `self.show_settings_dialog()`), so `app.py` is the single place orchestrating UI flow.
- **6. Centralize event handling and commands**
  - Where possible, replace many free functions or lambdas with methods on the `App` class or dedicated controller classes.
  - Optionally introduce a thin command layer (e.g. methods like `start_timer()`, `stop_timer()`, `add_project()`) in `app.py` that call into core logic; UI widgets only call these commands.
- **7. Adjust tests and manual QA**
  - If there are tests, update imports to match the new module structure.
  - Add unit tests around the new core modules (e.g. timer behavior, report calculations) to lock in behavior before Phase 2.
  - Do a manual pass of the existing UX to confirm all key flows still work (start/stop timer, switching tasks, exporting, loading previous sessions, etc.).
- **8. Keep packaging working**
  - Ensure the entry script used for your `.exe` (e.g. the target in PyInstaller spec) now points at `[app/main.py](app/main.py)` or whichever module owns the `if __name__ == "__main__"` block.
  - Perform a test build to ensure there are no missing imports or path issues after the refactor.

## Phase 2: PyQt6 Migration Plan

- **1. Introduce a parallel PyQt6 UI package**
  - Create a new package, for example:
    - `[app/ui/qt/__init__.py](app/ui/qt/__init__.py)`
    - `[app/ui/qt/app.py](app/ui/qt/app.py)` – main `QApplication` and main window.
    - `[app/ui/qt/widgets.py](app/ui/qt/widgets.py)` – reusable PyQt widgets.
    - `[app/ui/qt/dialogs.py](app/ui/qt/dialogs.py)` – settings and other dialogs.
  - Reuse the same core logic modules (`app/core/`*) so the behavior stays consistent between Tkinter and PyQt6 frontends.
- **2. Map existing flows to PyQt6 screens**
  - For each major workflow in the current app (e.g. starting/stopping timers, managing projects/clients, viewing reports), design corresponding PyQt6 windows/dialogs.
  - Use Qt layouts and modern widgets (toolbars, status bar, dockable panels if useful) to improve UX while keeping concepts familiar.
- **3. Abstract shared UI-agnostic operations**
  - Where Tkinter and PyQt6 both need the same behavior (e.g. showing validation errors, confirming destructive actions), consider adding a small abstraction layer:
    - e.g. `app/ui/common/messages.py` exposing functions like `confirm_delete(ui_backend, text)` that delegate to Tk or Qt implementations.
  - This keeps business logic and high-level flows from depending on a specific toolkit.
- **4. Introduce a runtime UI selector (optional)**
  - Optionally allow choosing UI backend (Tkinter vs PyQt6) via a config setting or command-line flag so you can ship and test both versions during migration.
  - The entrypoint (e.g. `[app/main.py](app/main.py)`) reads the preference and instantiates either `TkApp` or `QtApp`.
- **5. Update packaging for PyQt6**
  - Adjust your PyInstaller (or equivalent) configuration to include Qt resources and any `.qss` stylesheets.
  - Create a separate PyQt6-based executable initially (e.g. `FreelanceTimerPro-qt.exe`) for side-by-side testing.
  - Once stable, you can switch the primary `.exe` to the PyQt6 frontend and optionally keep a Tkinter build as a fallback.
- **6. Visual/UX polish and cleanup**
  - Apply a consistent modern theme using Qt stylesheets, icon sets, and improved layout spacing.
  - Iterate on UX improvements enabled by Qt (e.g. better dialogs, non-blocking notifications, richer tables/views).

## How We'll Work Through This

- **Start with Phase 1** to carve `gui.py` into the core, UI, and utility modules while keeping the Tkinter UI functional.
- **Stabilize and test** the refactored Tkinter version (including packaging) so the core logic is reliable and toolkit-independent.
- **Implement Phase 2** by building the PyQt6 UI layer on top of the shared core, then iterating on UX and gradually promoting the PyQt6 build to the default.

## Session Progress Log (2026-03-30)

- Introduced `ui/tk/app.py` with `TkApp` + `run_tk_app`, and switched `main.py` to launch the Tk UI through this boundary.
- Extracted Tk bootstrap/theme defaults into `config.py` (`APP_TITLE`, window sizing, icon asset constants, default theme name).
- Added `core` helpers for repeated lookup/format logic:
  - `core/task_resolution.py` for task-id resolution and task display formatting.
  - `core/project_resolution.py` for project-id lookup by client/project names.
  - `core/client_resolution.py` for client-id lookup by name.
  - `core/task_list_builders.py` for building project-context task display lists.
- Rewired key `gui.py` flows to use core helpers:
  - `start_timer` and `add_manual_entry` task resolution.
  - Timer/manual project-select handlers task list building.
  - Multiple client/project ID resolution paths.
- Extracted shared GUI helper methods in `gui.py` to reduce callback complexity:
  - `_populate_projects_for_client(...)`
  - `_update_daily_totals_from_manual_entry(...)`

