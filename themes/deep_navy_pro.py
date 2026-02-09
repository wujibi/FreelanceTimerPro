"""
Deep Navy Pro Theme
Professional dark theme with navy blue palette and bright accents
Designed to complement the new stopwatch logo
Based on color specifications from Freelance Time Tracker Pro Color Information.md
"""

def get_colors():
    """Return color palette for Deep Navy Pro theme"""
    return {
        'primary': '#1a73e8',      # Medium Blue (buttons, active states, highlights)
        'secondary': '#2c3e50',    # Shadow Blue (inactive tabs, borders)
        'accent': '#1a73e8',       # Medium Blue (progress bars, links)
        'background': '#0b1d3d',   # Deep Navy (main background, active tabs)
        'text': '#ffffff',         # Pure White (primary text)
        'border': '#2c3e50',       # Shadow Blue (dividers, borders)
        'hover': '#2386f7',        # Lighter blue for hover states
        'error': '#ef4444',        # Red for errors
        'success': '#22c55e',      # Green for success states
        'alt_row': '#152844',      # Slightly lighter navy for alternating table rows
        'card_bg': '#0f2847'       # Card/section backgrounds
    }


def get_fonts():
    """Return font definitions for Deep Navy Pro theme"""
    return {
        'heading': ('Segoe UI', 12, 'bold'),
        'subheading': ('Segoe UI', 10, 'bold'),
        'body': ('Segoe UI', 10),
        'small': ('Segoe UI', 9),
        'title': ('Segoe UI', 14, 'bold'),
        'large_display': ('Segoe UI', 24)  # For timer display - mimics stopwatch glow
    }


def apply_theme(style, colors, fonts):
    """
    Apply Deep Navy Pro theme to ttk.Style object
    
    Args:
        style: ttk.Style() instance
        colors: Color palette dict from get_colors()
        fonts: Font definitions dict from get_fonts()
    """
    
    # Use 'alt' theme as base - it doesn't raise selected tabs
    try:
        style.theme_use('alt')
    except:
        try:
            style.theme_use('clam')
        except:
            pass  # Use default if neither available
    
    # ============================================================================
    # TABS - Deep Navy active tabs, Shadow Blue inactive
    # ============================================================================
    style.configure('TNotebook', 
                   background=colors['background'],
                   borderwidth=0,
                   relief='flat')
    
    style.configure('TNotebook.Tab',
                   padding=[20, 10],
                   font=fonts['subheading'],
                   relief='flat',
                   borderwidth=1,
                   background=colors['secondary'],     # Shadow Blue inactive
                   foreground=colors['text'])          # White text
    
    style.map('TNotebook.Tab',
             background=[('selected', colors['background'])],  # Deep Navy active
             foreground=[('selected', colors['text'])],        # White text
             relief=[('selected', 'flat')])
    
    # ============================================================================
    # BUTTONS - Medium Blue with white text
    # ============================================================================
    style.configure('TButton',
                   font=fonts['body'],
                   padding=[10, 5],
                   borderwidth=1,
                   background=colors['primary'],       # Medium Blue
                   foreground='white')
    
    style.map('TButton',
             background=[('active', colors['hover'])],  # Lighter blue on hover
             foreground=[('active', 'white')])
    
    # Accent button style (for primary actions like Start Timer)
    style.configure('Accent.TButton',
                   font=fonts['subheading'],
                   background=colors['primary'],       # Medium Blue
                   foreground='white',
                   padding=[15, 8])
    
    style.map('Accent.TButton',
             background=[('active', colors['hover'])])
    
    # ============================================================================
    # LABELS
    # ============================================================================
    style.configure('TLabel',
                   font=fonts['body'],
                   background=colors['background'],    # Deep Navy
                   foreground=colors['text'])          # White text
    
    style.configure('Title.TLabel',
                   font=fonts['title'],
                   background=colors['background'],
                   foreground=colors['text'])
    
    # Special style for timer display - mimics stopwatch glow effect
    style.configure('Timer.TLabel',
                   font=fonts['large_display'],
                   background=colors['background'],
                   foreground=colors['text'])          # Bright white like stopwatch
    
    # ============================================================================
    # ENTRY FIELDS - Slightly lighter background for visibility
    # ============================================================================
    style.configure('TEntry',
                   font=fonts['body'],
                   fieldbackground=colors['alt_row'],  # Lighter navy
                   foreground=colors['text'],          # White text
                   borderwidth=1,
                   bordercolor=colors['border'])
    
    style.configure('TCombobox',
                   font=fonts['body'],
                   fieldbackground=colors['alt_row'],
                   foreground=colors['text'],
                   borderwidth=1)
    
    # ============================================================================
    # TREEVIEW (Data Tables) - Medium Blue headers, alternating navy/white rows
    # ============================================================================
    style.configure('Treeview',
                   font=fonts['body'],
                   rowheight=25,
                   borderwidth=1,
                   background='white',                  # White background for even rows
                   foreground=colors['background'],     # Dark text on white
                   fieldbackground='white')
    
    # Medium Blue headers as specified in design doc
    style.configure('Treeview.Heading',
                   font=fonts['subheading'],
                   background=colors['primary'],        # Medium Blue headers
                   foreground='white',
                   borderwidth=1,
                   relief='flat')
    
    style.map('Treeview',
             background=[('selected', colors['primary'])],  # Medium Blue selection
             foreground=[('selected', 'white')])
    
    # Tag configurations for alternating row colors (ledger style)
    # These will be applied in the code when inserting tree items
    # Odd rows: Deep navy background with white text
    # Even rows: White background with dark text (default above)
    
    # ============================================================================
    # FRAMES & CONTAINERS
    # ============================================================================
    style.configure('TFrame',
                   background=colors['background'])    # Deep Navy
    
    style.configure('TLabelframe',
                   borderwidth=2,
                   relief='solid',
                   background=colors['background'],
                   bordercolor=colors['border'])       # Shadow Blue border
    
    style.configure('TLabelframe.Label',
                   font=fonts['subheading'],
                   foreground=colors['text'],          # White text
                   background=colors['background'])
    
    # ============================================================================
    # SCROLLBARS
    # ============================================================================
    style.configure('Vertical.TScrollbar',
                   background=colors['secondary'],
                   troughcolor=colors['background'],
                   borderwidth=0,
                   arrowcolor=colors['text'])
    
    style.configure('Horizontal.TScrollbar',
                   background=colors['secondary'],
                   troughcolor=colors['background'],
                   borderwidth=0,
                   arrowcolor=colors['text'])
