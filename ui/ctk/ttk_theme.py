"""Align embedded ttk widgets (Treeview, scrollbars) with CustomTkinter light/dark appearance."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

import customtkinter as ctk

# Approximate CTk surface colors so plain tk.Frame hosts sit flush with the tree.
_LIGHT_HOST = "#ebebeb"
_DARK_HOST = "#2b2b2b"


def effective_appearance_is_dark() -> bool:
    """Match CustomTkinter logic: Light / Dark / System (+ OS via darkdetect when available)."""
    mode = ctk.get_appearance_mode()
    if mode == "Dark":
        return True
    if mode == "Light":
        return False
    try:
        import darkdetect

        return bool(darkdetect.isDark())
    except Exception:
        return False


def embedded_tk_frame_bg() -> str:
    """Background for tk.Frame wrappers around ttk.Treeview."""
    return _DARK_HOST if effective_appearance_is_dark() else _LIGHT_HOST


def apply_ctk_aligned_ttk_theme(master: tk.Misc) -> ttk.Style:
    """
    Configure global ttk styles for this app. Prefer 'clam' so foreground/background stick on Windows.
    """
    style = ttk.Style(master)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    dark = effective_appearance_is_dark()
    if dark:
        tree_bg = "#2b2b2b"
        tree_fg = "#dce4ee"
        heading_bg = "#3d3d3d"
        heading_fg = "#e8e8e8"
        select_bg = "#1f538d"
        select_fg = "#ffffff"
        trough = "#333333"
        scroll_bg = "#4a4a4a"
        scroll_active = "#5c5c5c"
        border = "#555555"
    else:
        tree_bg = "#ffffff"
        tree_fg = "#1a1a1a"
        heading_bg = "#e8e8e8"
        heading_fg = "#1a1a1a"
        select_bg = "#3b8ed0"
        select_fg = "#ffffff"
        trough = "#e0e0e0"
        scroll_bg = "#c4c4c4"
        scroll_active = "#a0a0a0"
        border = "#b0b0b0"

    style.configure(
        "Treeview",
        background=tree_bg,
        fieldbackground=tree_bg,
        foreground=tree_fg,
        borderwidth=0,
        rowheight=26,
    )
    style.map(
        "Treeview",
        background=[("selected", select_bg)],
        foreground=[("selected", select_fg)],
    )
    style.configure(
        "Treeview.Heading",
        background=heading_bg,
        foreground=heading_fg,
        relief="flat",
        borderwidth=1,
        padding=4,
    )
    style.map("Treeview.Heading", background=[("active", heading_bg)])

    for sb in ("Vertical.TScrollbar", "Horizontal.TScrollbar"):
        style.configure(
            sb,
            troughcolor=trough,
            background=scroll_bg,
            bordercolor=border,
            arrowcolor=tree_fg if dark else "#333333",
            darkcolor=scroll_bg,
            lightcolor=scroll_bg,
        )
        style.map(sb, background=[("active", scroll_active), ("pressed", scroll_active)])

    style.configure("TFrame", background=embedded_tk_frame_bg())

    return style
