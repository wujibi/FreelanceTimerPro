"""CustomTkinter application bootstrap — shell + Timer / Time Entries placeholders."""

import os

import customtkinter as ctk

from config import (
    APP_ICON_FILENAME,
    APP_TITLE,
    ASSETS_DIRNAME,
    DEFAULT_MIN_WINDOW_SIZE,
    DEFAULT_WINDOW_GEOMETRY,
)
from db_manager import DatabaseManager

from ui.ctk.clients_panel import CtkClientsTab
from ui.ctk.projects_panel import CtkProjectsTab
from ui.ctk.tasks_panel import CtkTasksTab
from ui.ctk.time_entries_panel import CtkTimeEntriesTab
from ui.ctk.timer_panel import CtkTimerTab


def _apply_icon(root: ctk.CTk) -> None:
    # ui/ctk/app.py → project root is two levels above this package
    ctk_pkg = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(ctk_pkg))
    icon_path = os.path.join(project_root, ASSETS_DIRNAME, APP_ICON_FILENAME)
    if not os.path.exists(icon_path):
        return
    try:
        root.iconbitmap(icon_path)
    except Exception as exc:
        print(f"[DEBUG] CTk could not set icon: {exc}")


class CtkApp:
    """Minimal CustomTkinter shell for phased migration from Tk."""

    def __init__(self, db_path=None):
        self.db_path = db_path
        self.root = None
        self.db = None

    def _notify_data_changed(self) -> None:
        """Keep Timer combos, Time Entries list, and Projects/Tasks tabs in sync after CRUD."""
        self.entries_tab.refresh()
        self.timer_tab.reload_clients_if_needed()
        self.projects_tab.refresh_all()
        self.tasks_tab.refresh_all()

    def run(self) -> None:
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title(APP_TITLE)
        self.root.geometry(DEFAULT_WINDOW_GEOMETRY)
        self.root.minsize(*DEFAULT_MIN_WINDOW_SIZE)
        _apply_icon(self.root)

        if self.db_path:
            print(f"[DEBUG] CTk initializing DatabaseManager with path: {self.db_path}")
            self.db = DatabaseManager(self.db_path)
        else:
            print("[DEBUG] CTk initializing DatabaseManager with default path")
            self.db = DatabaseManager()

        banner = ctk.CTkFrame(self.root, fg_color=("gray85", "gray20"))
        banner.pack(fill="x", padx=12, pady=(12, 0))
        ctk.CTkLabel(
            banner,
            text=(
                "V4 CustomTkinter preview — Timer, Clients, Projects, Tasks, and Time Entries are in CTk. "
                "Company, Invoices, and Email remain in classic Tk (same database)."
            ),
            wraplength=920,
            justify="left",
            font=ctk.CTkFont(size=12),
            anchor="w",
        ).pack(fill="x", padx=10, pady=8)

        tabview = ctk.CTkTabview(self.root)
        tabview.pack(fill="both", expand=True, padx=12, pady=12)

        tab_timer = tabview.add("Timer")
        tab_clients = tabview.add("Clients")
        tab_projects = tabview.add("Projects")
        tab_tasks = tabview.add("Tasks")
        tab_entries = tabview.add("Time Entries")

        self.entries_tab = CtkTimeEntriesTab(tab_entries, self.root, self.db)
        self.timer_tab = CtkTimerTab(
            tab_timer,
            self.root,
            self.db,
            refresh_time_entries=self.entries_tab.refresh,
        )
        self.clients_tab = CtkClientsTab(
            tab_clients,
            self.root,
            self.db,
            on_data_changed=self._notify_data_changed,
        )
        self.projects_tab = CtkProjectsTab(
            tab_projects,
            self.root,
            self.db,
            on_data_changed=self._notify_data_changed,
        )
        self.tasks_tab = CtkTasksTab(
            tab_tasks,
            self.root,
            self.db,
            on_data_changed=self._notify_data_changed,
        )

        footer = ctk.CTkLabel(
            self.root,
            text=f"DB: {self.db_path or '(default)'}  ·  unset FREELANCETIMERPRO_UI to use classic Tk",
            text_color=("gray30", "gray70"),
            font=ctk.CTkFont(size=12),
        )
        footer.pack(side="bottom", fill="x", padx=12, pady=(0, 8))

        self.root.mainloop()


def run_ctk_app(db_path=None) -> None:
    """Run the CustomTkinter frontend."""
    CtkApp(db_path=db_path).run()
