"""CustomTkinter application bootstrap — main window and tabs."""

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
from ui_helpers import load_ctk_ui_preferences

from ui.ctk.clients_panel import CtkClientsTab
from ui.ctk.company_panel import CtkCompanyTab
from ui.ctk.email_panel import CtkEmailTab
from ui.ctk.ttk_theme import apply_ctk_aligned_ttk_theme
from ui.ctk.invoices_panel import CtkInvoicesTab
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
    """CustomTkinter main window: tabbed Timer, CRM, entries, invoicing, and settings."""

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
        if hasattr(self, "invoices_tab"):
            self.invoices_tab.on_data_changed_external()

    def _apply_ttk_tree_theme(self) -> None:
        """Keep embedded ttk trees/scrollbars in sync with CTk light/dark."""
        apply_ctk_aligned_ttk_theme(self.root)
        for tab in (
            self.clients_tab,
            self.projects_tab,
            self.tasks_tab,
            self.entries_tab,
            self.invoices_tab,
            self.email_tab,
        ):
            if hasattr(tab, "sync_embedded_tk_widgets"):
                tab.sync_embedded_tk_widgets()

    def run(self) -> None:
        if self.db_path:
            print(f"[DEBUG] CTk initializing DatabaseManager with path: {self.db_path}")
            self.db = DatabaseManager(self.db_path)
        else:
            print("[DEBUG] CTk initializing DatabaseManager with default path")
            self.db = DatabaseManager()

        _mode, _theme = load_ctk_ui_preferences(self.db.db_path)
        ctk.set_appearance_mode(_mode)
        ctk.set_default_color_theme(_theme)

        self.root = ctk.CTk()
        self.root.title(APP_TITLE)
        self.root.geometry(DEFAULT_WINDOW_GEOMETRY)
        self.root.minsize(*DEFAULT_MIN_WINDOW_SIZE)
        _apply_icon(self.root)

        tabview = ctk.CTkTabview(self.root)
        tabview.pack(fill="both", expand=True, padx=12, pady=12)

        tab_timer = tabview.add("Timer")
        tab_clients = tabview.add("Clients")
        tab_projects = tabview.add("Projects")
        tab_tasks = tabview.add("Tasks")
        tab_entries = tabview.add("Time Entries")
        tab_company = tabview.add("Company")
        tab_invoices = tabview.add("Invoices")
        tab_email = tabview.add("Email")

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
        self.company_tab = CtkCompanyTab(
            tab_company,
            self.root,
            self.db,
            on_appearance_applied=self._apply_ttk_tree_theme,
        )
        self.invoices_tab = CtkInvoicesTab(
            tab_invoices,
            self.root,
            self.db,
            self.entries_tab,
            on_data_changed=self._notify_data_changed,
        )
        self.email_tab = CtkEmailTab(tab_email, self.root, self.db)

        self._apply_ttk_tree_theme()

        self.root.mainloop()


def run_ctk_app(db_path=None) -> None:
    """Run the CustomTkinter frontend."""
    CtkApp(db_path=db_path).run()
