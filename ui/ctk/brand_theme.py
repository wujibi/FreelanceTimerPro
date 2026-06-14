"""Burnt Orange Pro V3 branding for the CustomTkinter shell."""

from __future__ import annotations

import os
from typing import Any

import customtkinter as ctk
import tkinter.font as tkfont
from tkinter import ttk

from themes.burnt_orange_pro_v3 import get_colors as _get_light_colors
from ui.ctk.style_tokens import TREE_FONT_BODY_PT

BRAND_THEME_FILENAME = "ctk_burnt_orange_pro_v3.json"
BRAND_THEME_KEY = "burnt_orange_pro_v3"

LIGHT: dict[str, str] = _get_light_colors()
LIGHT["entry_bg"] = "#ffffff"
LIGHT["tree_bg"] = "#ffffff"
LIGHT["subtotal_bg"] = LIGHT["alt_row"]
LIGHT["preview_bg"] = "#f5f5f5"
LIGHT["paid_row"] = "#d4edda"
LIGHT["unpaid_row"] = "#fff3cd"

DARK: dict[str, str] = {
    "background": "#2a2826",
    "surface": "#353230",
    "primary": "#ce6427",
    "secondary": "#5c656e",
    "text": "#e8e4e0",
    "text_secondary": "#a8a099",
    "border": "#4a4644",
    "hover": "#3d3a38",
    "selected": "#ce6427",
    "alt_row": "#32302e",
    "accent_dark": "#181c20",
    "success": "#6aaf6a",
    "warning": "#ce6427",
    "danger": "#c46a66",
    "orange_hover": "#b85520",
    "group_heading": "#5a8f8f",
    "group_text": "white",
    "entry_bg": "#2e2c2a",
    "tree_bg": "#2e2c2a",
    "subtotal_bg": "#32302e",
    "preview_bg": "#252526",
    "paid_row": "#2d4a32",
    "unpaid_row": "#4a4228",
}


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


def _tree_font(_master: Any = None) -> tuple[str, int]:
    try:
        family = tkfont.nametofont("TkDefaultFont").actual("family")
    except tk.TclError:
        family = "Segoe UI"
    return (family, TREE_FONT_BODY_PT)


def _tree_font_bold(master: Any = None) -> tuple[str, int, str]:
    f = _tree_font(master)
    return (f[0], f[1], "bold")


def _project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def brand_theme_json_path() -> str:
    return os.path.join(_project_root(), "themes", BRAND_THEME_FILENAME)


def apply_brand_color_theme() -> None:
    ctk.set_default_color_theme(brand_theme_json_path())


def get_palette() -> dict[str, str]:
    return dict(DARK if effective_appearance_is_dark() else LIGHT)


def embedded_frame_bg() -> str:
    return get_palette()["background"]


def hint_text_color() -> tuple[str, str]:
    return (LIGHT["text_secondary"], DARK["text_secondary"])


def warning_hint_color() -> tuple[str, str]:
    return (LIGHT["primary"], "#ffb366")


def delete_button_colors() -> tuple[tuple[str, str], tuple[str, str]]:
    fg = (LIGHT["secondary"], DARK["secondary"])
    hover = (LIGHT["border"], DARK["hover"])
    return fg, hover


def danger_button_color() -> tuple[str, str]:
    return (LIGHT["danger"], DARK["danger"])


def timer_running_color() -> tuple[str, str]:
    return (LIGHT["success"], DARK["success"])


def timer_idle_color() -> tuple[str, str]:
    return (LIGHT["text"], DARK["text"])


def timer_paused_color() -> tuple[str, str]:
    return (LIGHT["text_secondary"], DARK["text_secondary"])


def primary_button_disabled_text_color() -> tuple[str, str]:
    """Readable label on dimmed orange primary buttons (Start/Stop while inactive)."""
    return ("#ffffff", "#d8d0ca")


def configure_group_row_tags(
    tree: ttk.Treeview,
    root: Any,
    *,
    client: bool = True,
    project: bool = True,
    task: bool = True,
) -> None:
    palette = get_palette()
    if client:
        tree.tag_configure(
            "client_row",
            background=palette["group_heading"],
            foreground=palette["group_text"],
            font=_tree_font_bold(root),
        )
    if project:
        tree.tag_configure(
            "project_row",
            background=palette["group_heading"],
            foreground=palette["group_text"],
            font=_tree_font_bold(root),
        )
    if task:
        tree.tag_configure(
            "task_row",
            background=palette["group_heading"],
            foreground=palette["group_text"],
            font=_tree_font(root),
        )


def configure_entry_row_tag(tree: ttk.Treeview, root: Any, tag: str = "entry_row") -> None:
    palette = get_palette()
    tree.tag_configure(
        tag,
        background=palette["entry_bg"],
        foreground=palette["text"],
        font=_tree_font(root),
    )


def configure_invoice_preview_tree_tags(tree: ttk.Treeview, root: Any) -> None:
    palette = get_palette()
    tree.tag_configure(
        "header",
        font=_tree_font_bold(root),
        background=palette["group_heading"],
        foreground=palette["group_text"],
    )
    tree.tag_configure(
        "subtotal",
        font=_tree_font_bold(root),
        background=palette["subtotal_bg"],
        foreground=palette["text"],
    )
