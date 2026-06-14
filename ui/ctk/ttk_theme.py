"""Align embedded ttk widgets (Treeview, scrollbars) with Burnt Orange Pro V3 branding."""

from __future__ import annotations

import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk

from ui.ctk.brand_theme import get_palette
from ui.ctk.style_tokens import TREE_FONT_BODY_PT, TREE_ROW_HEIGHT


def embedded_tk_frame_bg() -> str:
    """Background for tk.Frame wrappers around ttk.Treeview."""
    return get_palette()["background"]


def get_tree_ui_font(_master: tk.Misc | None = None) -> tuple[str, int]:
    """Font tuple for Treeview cells (family from OS default; size from style_tokens)."""
    try:
        family = tkfont.nametofont("TkDefaultFont").actual("family")
    except tk.TclError:
        family = "Segoe UI"
    return (family, TREE_FONT_BODY_PT)


def get_tree_ui_font_bold(master: tk.Misc | None = None) -> tuple[str, int, str]:
    f = get_tree_ui_font(master)
    return (f[0], f[1], "bold")


def apply_ctk_aligned_ttk_theme(master: tk.Misc) -> ttk.Style:
    """
    Configure global ttk styles for embedded trees — Burnt Orange Pro V3 parity with classic Tk.
    """
    style = ttk.Style(master)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    colors = get_palette()
    tree_bg = colors["tree_bg"]
    tree_fg = colors["text"]
    heading_bg = colors["primary"]
    heading_active_bg = colors["orange_hover"]
    heading_fg = colors["text"]
    select_bg = colors["selected"]
    select_fg = colors["group_text"]
    trough = colors["background"]
    scroll_bg = colors["surface"]
    scroll_active = colors["border"]
    border = colors["border"]
    heading_divider = colors["border"]
    heading_light = colors["hover"]
    heading_dark = colors["border"]

    body_font = get_tree_ui_font(master)
    heading_font = get_tree_ui_font_bold(master)

    style.configure(
        "Treeview",
        background=tree_bg,
        fieldbackground=tree_bg,
        foreground=tree_fg,
        borderwidth=0,
        bordercolor=border,
        lightcolor=border,
        darkcolor=border,
        rowheight=TREE_ROW_HEIGHT,
        font=body_font,
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
        bordercolor=heading_divider,
        lightcolor=heading_light,
        darkcolor=heading_dark,
        padding=4,
        font=heading_font,
    )
    style.map(
        "Treeview.Heading",
        background=[("active", heading_active_bg)],
        foreground=[("active", heading_fg)],
    )

    for sb in ("Vertical.TScrollbar", "Horizontal.TScrollbar"):
        style.configure(
            sb,
            troughcolor=trough,
            background=scroll_bg,
            bordercolor=border,
            arrowcolor=tree_fg,
            darkcolor=scroll_bg,
            lightcolor=scroll_bg,
        )
        style.map(sb, background=[("active", scroll_active), ("pressed", scroll_active)])

    style.configure("TFrame", background=embedded_tk_frame_bg())

    return style
