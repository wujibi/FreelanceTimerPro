"""
Light Navy Pro Theme - Lighter variant with white background and subtle accents
Uses the same navy blue but as an accent instead of dominant background color
Perfect for long work sessions - easier on the eyes
"""

def get_colors():
    """Return the color palette for Light Navy Pro theme"""
    return {
        'background': '#ffffff',           # White background (main change!)
        'surface': '#f8f9fa',              # Very light gray for surfaces
        'primary': '#1a73e8',              # Medium Blue (same accent color)
        'secondary': '#0b1d3d',            # Deep Navy (used sparingly)
        'text': '#2c3e50',                 # Dark gray text (not pure black)
        'text_secondary': '#6c757d',       # Medium gray for secondary text
        'border': '#dee2e6',               # Light border
        'hover': '#e7f3ff',                # Very light blue hover
        'selected': '#1a73e8',             # Medium Blue for selections
        'alt_row': '#f0f4ff',              # Very light blue tint for alternating rows
        'success': '#10b981',              # Green for success
        'warning': '#f59e0b',              # Orange for warnings
        'danger': '#ef4444'                # Red for errors/danger
    }

def get_fonts():
    """Return font configurations"""
    return {
        'heading': ('Segoe UI', 12, 'bold'),
        'subheading': ('Segoe UI', 10, 'bold'),
        'body': ('Segoe UI', 10),
        'small': ('Segoe UI', 9),
        'large_display': ('Segoe UI', 36, 'bold'),
        'button': ('Segoe UI', 10)
    }

def apply_theme(style, colors, fonts):
    """Apply the Light Navy Pro theme to ttk widgets"""
    
    # ============================================================================
    # GENERAL WIDGET DEFAULTS - White background, dark text
    # ============================================================================
    style.configure('.',
                   background=colors['background'],
                   foreground=colors['text'],
                   bordercolor=colors['border'],
                   darkcolor=colors['surface'],
                   lightcolor=colors['background'],
                   troughcolor=colors['surface'],
                   selectbackground=colors['selected'],
                   selectforeground='white',
                   fieldbackground='white',
                   font=fonts['body'],
                   borderwidth=1)
    
    # ============================================================================
    # NOTEBOOK (Tab Container) - Navy header strip
    # ============================================================================
    style.configure('TNotebook',
                   background=colors['background'],
                   borderwidth=0)
    
    style.configure('TNotebook.Tab',
                   background=colors['surface'],
                   foreground=colors['text'],
                   padding=[20, 10],
                   font=fonts['subheading'],
                   borderwidth=0)
    
    style.map('TNotebook.Tab',
             background=[('selected', colors['secondary']),  # Deep navy for active tab
                        ('active', colors['hover'])],
             foreground=[('selected', 'white'),
                        ('active', colors['primary'])],
             expand=[('selected', [1, 1, 1, 0])])
    
    # ============================================================================
    # BUTTONS - Blue accent buttons with white background default
    # ============================================================================
    style.configure('TButton',
                   font=fonts['button'],
                   padding=[15, 8],
                   background=colors['surface'],
                   foreground=colors['text'],
                   borderwidth=1,
                   focuscolor=colors['primary'],
                   relief='flat')
    
    style.map('TButton',
             background=[('active', colors['hover']),
                        ('pressed', colors['primary'])],
             foreground=[('active', colors['primary']),
                        ('pressed', 'white')],
             relief=[('pressed', 'flat')])
    
    # Accent button style (primary actions)
    style.configure('Accent.TButton',
                   background=colors['primary'],
                   foreground='white',
                   font=fonts['button'])
    
    style.map('Accent.TButton',
             background=[('active', '#1557b0'),
                        ('pressed', colors['secondary'])],
             foreground=[('active', 'white'),
                        ('pressed', 'white')])
    
    # ============================================================================
    # LABELS - Dark text on white
    # ============================================================================
    style.configure('TLabel',
                   background=colors['background'],
                   foreground=colors['text'],
                   font=fonts['body'])
    
    # ============================================================================
    # ENTRIES (Text Input) - White with border
    # ============================================================================
    style.configure('TEntry',
                   fieldbackground='white',
                   foreground=colors['text'],
                   bordercolor=colors['border'],
                   lightcolor=colors['border'],
                   darkcolor=colors['border'],
                   insertcolor=colors['text'],
                   relief='solid',
                   borderwidth=1)
    
    style.map('TEntry',
             fieldbackground=[('focus', 'white')],
             bordercolor=[('focus', colors['primary'])],
             lightcolor=[('focus', colors['primary'])],
             darkcolor=[('focus', colors['primary'])])
    
    # ============================================================================
    # COMBOBOX (Dropdown) - White with border
    # ============================================================================
    style.configure('TCombobox',
                   fieldbackground='white',
                   background='white',
                   foreground=colors['text'],
                   arrowcolor=colors['text'],
                   bordercolor=colors['border'],
                   lightcolor=colors['border'],
                   darkcolor=colors['border'],
                   selectbackground=colors['selected'],
                   selectforeground='white',
                   relief='solid',
                   borderwidth=1)
    
    style.map('TCombobox',
             fieldbackground=[('readonly', 'white'),
                            ('focus', 'white')],
             background=[('readonly', 'white')],
             bordercolor=[('focus', colors['primary'])],
             lightcolor=[('focus', colors['primary'])],
             darkcolor=[('focus', colors['primary'])],
             foreground=[('readonly', colors['text'])])
    
    # ============================================================================
    # CHECKBUTTON - Blue accent when checked
    # ============================================================================
    style.configure('TCheckbutton',
                   background=colors['background'],
                   foreground=colors['text'],
                   font=fonts['body'])
    
    style.map('TCheckbutton',
             background=[('active', colors['background'])],
             foreground=[('selected', colors['primary'])])
    
    # ============================================================================
    # RADIOBUTTON - Blue accent when selected
    # ============================================================================
    style.configure('TRadiobutton',
                   background=colors['background'],
                   foreground=colors['text'],
                   font=fonts['body'])
    
    style.map('TRadiobutton',
             background=[('active', colors['background'])],
             foreground=[('selected', colors['primary'])])
    
    # ============================================================================
    # LABELFRAME - Light gray box with dark text
    # ============================================================================
    style.configure('TLabelframe',
                   background=colors['background'],
                   foreground=colors['text'],
                   bordercolor=colors['border'],
                   relief='solid',
                   borderwidth=1)
    
    style.configure('TLabelframe.Label',
                   background=colors['background'],
                   foreground=colors['text'],
                   font=fonts['subheading'])
    
    # ============================================================================
    # SCROLLBAR - Subtle gray
    # ============================================================================
    style.configure('Vertical.TScrollbar',
                   background=colors['surface'],
                   troughcolor=colors['background'],
                   bordercolor=colors['border'],
                   arrowcolor=colors['text'])
    
    style.map('Vertical.TScrollbar',
             background=[('active', colors['border'])])
    
    style.configure('Horizontal.TScrollbar',
                   background=colors['surface'],
                   troughcolor=colors['background'],
                   bordercolor=colors['border'],
                   arrowcolor=colors['text'])
    
    style.map('Horizontal.TScrollbar',
             background=[('active', colors['border'])])
    
    # ============================================================================
    # TREEVIEW (Data Tables) - White/light blue alternating rows
    # ============================================================================
    style.configure('Treeview',
                   font=fonts['body'],
                   rowheight=25,
                   borderwidth=1,
                   background='white',
                   foreground=colors['text'],
                   fieldbackground='white')
    
    # Medium Blue headers
    style.configure('Treeview.Heading',
                   font=fonts['subheading'],
                   background=colors['primary'],
                   foreground='white',
                   borderwidth=1,
                   relief='flat')
    
    style.map('Treeview',
             background=[('selected', colors['primary'])],
             foreground=[('selected', 'white')])
    
    # ============================================================================
    # FRAMES & CONTAINERS
    # ============================================================================
    style.configure('TFrame',
                   background=colors['background'])
    
    # ============================================================================
    # PROGRESSBAR - Blue progress bar
    # ============================================================================
    style.configure('TProgressbar',
                   background=colors['primary'],
                   troughcolor=colors['surface'],
                   bordercolor=colors['border'],
                   lightcolor=colors['primary'],
                   darkcolor=colors['primary'])
    
    # ============================================================================
    # SEPARATOR - Subtle divider
    # ============================================================================
    style.configure('TSeparator',
                   background=colors['border'])
    
    # ============================================================================
    # SIZEGRIP - Subtle corner grip
    # ============================================================================
    style.configure('TSizegrip',
                   background=colors['background'])

    print(f"[THEME] Light Navy Pro theme applied successfully")
