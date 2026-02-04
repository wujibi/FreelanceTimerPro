# Time Tracker Pro - Theme System

## Overview
The theme system separates presentation (colors/fonts) from application logic, making it easy to customize the app's appearance without modifying `gui.py`.

## How Themes Work

Each theme is a Python module in the `themes/` folder with three functions:

1. **`get_colors()`** - Returns color palette dict
2. **`get_fonts()`** - Returns font definitions dict  
3. **`apply_theme(style, colors, fonts)`** - Applies theme to ttk widgets

---

## Creating a New Theme

### 1. Copy an Existing Theme
```bash
cp themes/professional_gray.py themes/my_theme.py
```

### 2. Edit Color Palette
Open `my_theme.py` and modify the `get_colors()` function:

```python
def get_colors():
    return {
        'primary': '#your_color',      # Main accent color (buttons, tabs)
        'secondary': '#your_color',    # Secondary elements (headers)
        'accent': '#your_color',       # Success/positive actions
        'background': '#your_color',   # Window background
        'text': '#your_color',         # Default text color
        'border': '#your_color',       # Widget borders
        'hover': '#your_color',        # Hover state
        'error': '#your_color',        # Error messages
        'success': '#your_color'       # Success messages
    }
```

### 3. Edit Fonts (Optional)
Modify the `get_fonts()` function:

```python
def get_fonts():
    return {
        'heading': ('Font Name', 12, 'bold'),
        'subheading': ('Font Name', 10, 'bold'),
        'body': ('Font Name', 10),
        'small': ('Font Name', 9),
        'title': ('Font Name', 14, 'bold'),
        'large_display': ('Font Name', 24)
    }
```

### 4. Register Theme
Add your theme to `themes/__init__.py`:

```python
from . import professional_gray
from . import my_theme  # Add this line

__all__ = ['professional_gray', 'my_theme']
```

### 5. Switch to Your Theme
Edit `gui.py` line ~60 to import your theme:

```python
from themes import my_theme  # Change this import
```

---

## Color Usage Guide

### Primary Color
- **Used for:** Selected tabs, primary buttons, tree selection
- **Should be:** Bold, high contrast
- **Example:** `#2563eb` (blue)

### Secondary Color
- **Used for:** Table headers, secondary UI elements
- **Should be:** Muted, professional
- **Example:** `#64748b` (slate gray)

### Background Color
- **Used for:** Window background, frame backgrounds
- **Should be:** Light, easy on eyes
- **Example:** `#f8fafc` (light gray)

### Text Color
- **Used for:** Default text throughout app
- **Should be:** High contrast with background
- **Example:** `#1e293b` (dark slate)

### Accent Color
- **Used for:** Success messages, positive actions
- **Should be:** Distinct from primary
- **Example:** `#10b981` (green)

---

## Widget Styles Reference

### Standard Widgets
All ttk widgets use theme colors automatically:
- `TButton` - Standard buttons
- `TLabel` - Text labels
- `TEntry` - Text input fields
- `TCombobox` - Dropdown menus
- `TNotebook` - Tab container
- `TNotebook.Tab` - Individual tabs
- `Treeview` - Tables/lists
- `TLabelframe` - Grouped sections

### Custom Styles
Special widget variants defined in themes:
- `Accent.TButton` - Primary action buttons (larger, bold)
- `Title.TLabel` - Section titles (larger font)

---

## Font Guidelines

### Recommended Fonts
- **Windows:** Segoe UI (default)
- **Mac:** SF Pro, Helvetica Neue
- **Linux:** Liberation Sans, DejaVu Sans

### Font Sizes
- `large_display` (24pt) - Timer display, large numbers
- `title` (14pt bold) - Section headings
- `heading` (12pt bold) - Widget group labels
- `subheading` (10pt bold) - Tab labels, buttons
- `body` (10pt) - Default text, entries
- `small` (9pt) - Helper text, metadata

---

## Testing Your Theme

1. **Load the app** - Check overall appearance
2. **Navigate all tabs** - Ensure consistency
3. **Test interactions:**
   - Click buttons (check hover states)
   - Select tree items (check highlight color)
   - Switch tabs (check active tab color)
4. **Check readability:**
   - Text on background (sufficient contrast?)
   - Button text on button color (readable?)
   - Selected items (clearly visible?)

---

## Theme Examples

### Professional Gray (Default)
- **Style:** Clean, neutral, corporate
- **Primary:** Blue (#2563eb)
- **Background:** Light gray (#f8fafc)
- **Use case:** Professional/business settings

### Future Themes (Ideas)
- **Dark Mode** - Dark background, light text
- **High Contrast** - Maximum readability
- **Ocean Blue** - Blue-themed, calming
- **Forest Green** - Green-themed, natural
- **Sunset Orange** - Warm, energetic

---

## Advanced: Custom Widget Styles

You can add custom widget styles in `apply_theme()`:

```python
def apply_theme(style, colors, fonts):
    # ... standard styles ...
    
    # Add custom style variant
    style.configure('Card.TFrame',
                   background='white',
                   borderwidth=1,
                   relief='solid')
    
    style.configure('Header.TLabel',
                   font=fonts['title'],
                   foreground=colors['primary'])
```

Then use in gui.py:
```python
ttk.Frame(parent, style='Card.TFrame')
ttk.Label(parent, text="Header", style='Header.TLabel')
```

---

## Troubleshooting

### Colors Not Applying
- Check that theme is imported in `gui.py`
- Verify `apply_theme()` is called in `__init__`
- Restart app (some changes require restart)

### Fonts Not Changing
- Check font name is correct for your OS
- Use system fonts (avoid requiring font installation)
- Test with fallback fonts

### Contrast Issues
- Use online contrast checkers (WCAG standards)
- Test with colorblind-friendly palettes
- Ensure text/background ratio ≥ 4.5:1

---

## Contributing Themes

If you create a great theme:
1. Save to `themes/your_theme_name.py`
2. Add documentation to this README
3. Share with community (GitHub, etc.)

---

**Last Updated:** February 3, 2026  
**Compatible with:** Time Tracker Pro v2.0.7+
