from __future__ import annotations

import sqlite3
from typing import Iterable, Set

import tkinter as tk
from tkinter import ttk


def center_window(root: tk.Tk) -> None:
    """Center the main window on the screen."""
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")


def center_dialog(root: tk.Tk, dialog: tk.Toplevel, width: int, height: int) -> None:
    """Center a dialog relative to the main window."""
    dialog.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() // 2) - (width // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (height // 2)
    dialog.geometry(f"{width}x{height}+{x}+{y}")


def center_dialog_clamped(
    root: tk.Misc,
    dialog: tk.Toplevel,
    width: int,
    height: int,
    *,
    margin: int = 48,
) -> None:
    """
    Center a dialog relative to the main window; shrink size if it would exceed the screen
    (helps 13–14 inch laptops and scaled displays). Position is clamped so the window stays on-screen.
    """
    root.update_idletasks()
    dialog.update_idletasks()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    w = min(width, max(520, sw - 2 * margin))
    h = min(height, max(400, sh - 2 * margin))
    x = root.winfo_x() + (root.winfo_width() // 2) - (w // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (h // 2)
    x = max(margin, min(x, sw - w - margin))
    y = max(margin, min(y, sh - h - margin))
    dialog.geometry(f"{w}x{h}+{x}+{y}")


def load_theme_preference(db_path: str, default_theme: str = "Burnt Orange Pro V3") -> str:
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = 'theme'")
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else default_theme
    except Exception:
        return default_theme


def save_theme_preference(db_path: str, theme_name: str) -> None:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """
    )
    cursor.execute(
        """
        INSERT OR REPLACE INTO settings (key, value)
        VALUES ('theme', ?)
        """,
        (theme_name,),
    )
    conn.commit()
    conn.close()


def load_ctk_ui_preferences(db_path: str | None) -> tuple[str, str]:
    """Load CustomTkinter appearance mode and color theme from settings (CTk UI only)."""
    defaults = ("system", "blue")
    if not db_path:
        return defaults
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = 'ctk_appearance_mode'")
        row_m = cursor.fetchone()
        cursor.execute("SELECT value FROM settings WHERE key = 'ctk_color_theme'")
        row_t = cursor.fetchone()
        conn.close()
        mode = (row_m[0] if row_m else defaults[0]).strip().lower()
        theme = (row_t[0] if row_t else defaults[1]).strip().lower()
        if mode not in ("system", "light", "dark"):
            mode = defaults[0]
        if theme not in ("blue", "green", "dark-blue"):
            theme = defaults[1]
        return (mode, theme)
    except Exception:
        return defaults


def save_ctk_ui_preferences(db_path: str, appearance_mode: str, color_theme: str) -> None:
    """Persist CustomTkinter UI preferences alongside other settings."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """
    )
    cursor.execute(
        """
        INSERT OR REPLACE INTO settings (key, value)
        VALUES ('ctk_appearance_mode', ?)
        """,
        (appearance_mode.strip().lower(),),
    )
    cursor.execute(
        """
        INSERT OR REPLACE INTO settings (key, value)
        VALUES ('ctk_color_theme', ?)
        """,
        (color_theme.strip().lower(),),
    )
    conn.commit()
    conn.close()


def save_tree_state(tree: ttk.Treeview) -> Set[str]:
    expanded: Set[str] = set()

    def collect_expanded(parent: str = "") -> None:
        for item in tree.get_children(parent):
            if tree.item(item, "open"):
                expanded.add(tree.item(item, "text"))
            collect_expanded(item)

    collect_expanded()
    return expanded


def restore_tree_state(tree: ttk.Treeview, expanded_items: Iterable[str], expand_all: bool = False) -> None:
    expanded = set(expanded_items)

    def expand_items(parent: str = "") -> None:
        for item in tree.get_children(parent):
            item_text = tree.item(item, "text")
            if expand_all or item_text in expanded:
                tree.item(item, open=True)
            expand_items(item)

    expand_items()

