# Theme Switcher - User Guide

## Overview
Time Tracker Pro now has a **live theme switcher** that lets you change the app's appearance without restarting.

**Location:** Company Info tab → 🎨 Appearance section (bottom)

---

## How to Use

### Switch Themes (Frontend)
1. Open the app
2. Go to **Company Info** tab
3. Scroll to **"🎨 Appearance"** section
4. Select a theme from dropdown:
   - **Professional Gray** (default - neutral gray with blue accents)
   - **Dark Mode** (dark background, light text)
5. Click **"Apply Theme"** button
6. Theme changes instantly!

**Note:** Some elements may require restarting the app for full effect.

---

## Creating Your Own Theme

### Method 1: Quick Copy & Edit

1. **Copy existing theme:**
   ```bash
   copy themes\professional_gray.py themes\my_brand.py
   ```

2. **Edit colors** to match your brand:
   ```python
   def get_colors():
       return {
           'primary': '#YOUR_COLOR',      # Main accent (tabs, buttons)
           'secondary': '#YOUR_COLOR',    # Headers, secondary elements
           'accent': '#YOUR_COLOR',       # Success/positive actions
           'background': '#YOUR_COLOR',   # Window background
           'text': '#YOUR_COLOR',         # Default text color
           'border': '#YOUR_COLOR',       # Widget borders
           'hover': '#YOUR_COLOR',        # Hover state
           'error': '#YOUR_COLOR',        # Error messages
           'success': '#YOUR_COLOR'       # Success messages
       }
   ```

3. **Register your theme** in `themes/__init__.py`:
   ```python
   from . import professional_gray
   from . import dark_mode
   from . import my_brand  # Add this
   
   AVAILABLE_THEMES = {
       'Professional Gray': professional_gray,
       'Dark Mode': dark_mode,
       'My Brand': my_brand  # Add this
   }
   ```

4. **Restart app** - your theme appears in dropdown!

---

## Color Palette Guide

### Primary Color (Most Important)
- **What:** Main brand color, most visible
- **Used for:** Active tabs, selected items, primary buttons
- **Example:** `#2563eb` (blue), `#7c3aed` (purple), `#dc2626` (red)
- **Tip:** Should be bold and eye-catching

### Secondary Color
- **What:** Supporting color for headers/structure
- **Used for:** Table headers, inactive UI elements
- **Example:** `#64748b` (slate), `#6b7280` (gray)
- **Tip:** Should be muted, professional

### Background Color
- **What:** Main window background
- **Used for:** Window, panels, frames
- **Example:** `#f8fafc` (light), `#1e293b` (dark)
- **Tip:** Easy on eyes, not pure white/black

### Text Color
- **What:** Default text throughout app
- **Used for:** Labels, entries, general text
- **Example:** `#1e293b` (dark slate), `#f1f5f9` (light gray)
- **Tip:** High contrast with background (4.5:1 ratio minimum)

### Accent Color
- **What:** Success/positive actions
- **Used for:** Success messages, checkmarks
- **Example:** `#10b981` (green), `#06b6d4` (cyan)
- **Tip:** Should stand out, different from primary

---

## Example Theme Palettes

### Corporate Blue (Professional)
```python
{
    'primary': '#0066cc',      # Corporate blue
    'secondary': '#5c6b7a',    # Steel gray
    'accent': '#00a86b',       # Success green
    'background': '#f5f7fa',   # Light blue-gray
    'text': '#2c3e50',         # Dark blue-gray
    'border': '#d1dce6',       # Light border
    'hover': '#0052a3',        # Darker blue
    'error': '#e74c3c',        # Red
    'success': '#27ae60'       # Green
}
```

### Sunset Orange (Warm)
```python
{
    'primary': '#ff6b35',      # Sunset orange
    'secondary': '#004e89',    # Deep blue
    'accent': '#1a936f',       # Teal
    'background': '#fef9f3',   # Warm white
    'text': '#2d3142',         # Dark gray
    'border': '#e8dfd0',       # Tan
    'hover': '#ff4500',        # Bright orange
    'error': '#c1121f',        # Red
    'success': '#588b8b'       # Teal-gray
}
```

### Ocean Teal (Modern)
```python
{
    'primary': '#06b6d4',      # Cyan
    'secondary': '#0e7490',    # Dark cyan
    'accent': '#14b8a6',       # Teal
    'background': '#f0fdfa',   # Light cyan
    'text': '#164e63',         # Dark teal
    'border': '#ccfbf1',       # Light teal
    'hover': '#0891b2',        # Darker cyan
    'error': '#ef4444',        # Red
    'success': '#10b981'       # Green
}
```

### Forest Green (Natural)
```python
{
    'primary': '#059669',      # Emerald
    'secondary': '#6b7280',    # Gray
    'accent': '#fbbf24',       # Amber
    'background': '#f9fafb',   # Light gray
    'text': '#1f2937',         # Dark gray
    'border': '#e5e7eb',       # Light border
    'hover': '#047857',        # Darker green
    'error': '#dc2626',        # Red
    'success': '#84cc16'       # Lime
}
```

---

## Testing Your Theme

### Checklist
- [ ] Open all tabs - check consistency
- [ ] Click buttons - check hover states
- [ ] Select tree items - check highlight color
- [ ] Read all text - check contrast/readability
- [ ] Check forms - input fields visible?
- [ ] Check tables - headers readable?
- [ ] Test in different lighting conditions

### Contrast Testing
Use online tools to verify text is readable:
- **WebAIM Contrast Checker:** https://webaim.org/resources/contrastchecker/
- **Minimum ratio:** 4.5:1 for normal text
- **Recommended ratio:** 7:1 for better accessibility

---

## Advanced Customization

### Custom Fonts
Edit `get_fonts()` in your theme:
```python
def get_fonts():
    return {
        'heading': ('Arial', 12, 'bold'),      # Change font family
        'subheading': ('Arial', 10, 'bold'),
        'body': ('Arial', 10),
        'small': ('Arial', 9),
        'title': ('Arial', 16, 'bold'),        # Larger titles
        'large_display': ('Courier New', 28)   # Monospace for timer
    }
```

### Custom Widget Styles
Add to `apply_theme()` in your theme file:
```python
def apply_theme(style, colors, fonts):
    # ... standard styles ...
    
    # Add custom styles
    style.configure('Warning.TButton',
                   background=colors['error'],
                   foreground='white',
                   padding=[10, 5])
    
    style.configure('Card.TFrame',
                   background='white',
                   borderwidth=2,
                   relief='ridge')
```

---

## Troubleshooting

### Theme Not Applying
- **Restart app** - some changes need fresh start
- **Check theme file** - syntax errors?
- **Check registration** - added to `AVAILABLE_THEMES`?

### Colors Look Wrong
- **Check hex codes** - should start with #
- **Test contrast** - use contrast checker
- **Try different monitor** - colors vary by screen

### Text Unreadable
- **Increase contrast** - darker text or lighter background
- **Check font size** - may need larger fonts
- **Test with others** - get feedback

---

## Theme File Structure

```
themes/
├── __init__.py                  # Theme registry
├── professional_gray.py         # Default theme
├── dark_mode.py                 # Dark theme
├── my_brand.py                  # Your custom theme
└── README.md                    # Full documentation
```

Each theme file must have:
1. `get_colors()` - Returns color dict
2. `get_fonts()` - Returns font dict
3. `apply_theme(style, colors, fonts)` - Applies styles

---

## Quick Reference: Current Themes

### Professional Gray
- **Style:** Neutral, corporate, clean
- **Primary:** Blue `#2563eb`
- **Background:** Light gray `#f8fafc`
- **Best for:** Professional/business use

### Dark Mode
- **Style:** Dark, low-strain, modern
- **Primary:** Light blue `#60a5fa`
- **Background:** Dark slate `#1e293b`
- **Best for:** Night work, reduced eye strain

---

## Tips for Creating Great Themes

1. **Start with a color palette tool:**
   - Coolors.co
   - Adobe Color
   - Material Design Color Tool

2. **Pick 2-3 main colors:**
   - Primary (brand color)
   - Secondary (structure)
   - Accent (highlights)

3. **Test with real content:**
   - Add actual data to app
   - Use for a full work session
   - Get feedback from others

4. **Consider use case:**
   - Bright office? Use muted colors
   - Dark room? Use dark theme
   - Video calls? Avoid distracting colors

5. **Keep it simple:**
   - Don't use too many colors
   - Maintain consistency
   - Focus on readability

---

**Last Updated:** February 4, 2026  
**Feature Added:** v2.0.8
