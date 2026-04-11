"""Shared CTk layout tokens for consistent spacing/sizing across tabs."""

from __future__ import annotations

# Spacing scale
SPACE_4 = 4
SPACE_8 = 8
SPACE_10 = 10
SPACE_12 = 12
SPACE_16 = 16
SPACE_20 = 20

# Horizontal rhythm
PANEL_PAD_X = 8
PANEL_INNER_PAD_X = 10
GRID_PAD_X = 8
BUTTON_PAD_X = 4

# Vertical rhythm
SECTION_TITLE_TOP_PAD = 18
SECTION_TITLE_BOTTOM_PAD = 8
FIELD_PAD_Y = 4
BUTTON_ROW_PAD_Y = 4
BUTTON_ROW_BOTTOM_PAD = 8
SECTION_GAP = 12

# Embedded ttk.Treeview (Clients, Projects, Tasks, Time Entries, Invoices — one knob for all)
# Match CTk form body (~11pt); was 12pt + 30px rows and felt heavy vs labels.
TREE_FONT_BODY_PT = 10
TREE_ROW_HEIGHT = 26

# Control sizing
COMBO_WIDTH = 320
TEXTBOX_SHORT_HEIGHT = 72
TEXTBOX_MEDIUM_HEIGHT = 88
DAILY_TOTALS_ACTIVE_HEIGHT = 130
DAILY_TOTALS_MANUAL_HEIGHT = 96
