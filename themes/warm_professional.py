"""
Warm Professional Theme - Comfortable, sophisticated, easy on the eyes
Warm beige background like quality paper, muted teal accents
Perfect for long work sessions, professional appearance
Works well for both app and website branding
"""

def get_colors():
    """Return the color palette for Warm Professional theme"""
    return {
        'background': '#ede8e0',           # Warm cream/beige (like quality paper)
        'surface': '#dfd9d0',              # Slightly darker warm tan
        'primary': '#4a7c7a',              # Muted teal (sophisticated, not harsh)
        'secondary': '#5d6d6a',            # Warm gray-teal
        'text': '#2a2a2a',                 # Charcoal (not pure black)
        'text_secondary': '#6a6563',       # Warm medium gray
        'border': '#c4beb5',               # Soft warm border
        'hover': '#e0dcd5',                # Very subtle warm hover
        'selected': '#4a7c7a',             # Muted teal (same as primary)
        'alt_row': '#e5e0d8',              # Light warm gray for alternating rows
        'success': '#5a8f5a',              # Muted green (not neon)
        'warning': '#c68642',              # Warm amber/bronze
        'danger': '#b85450'                # Muted red/terracotta
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
    """Apply the Warm Professional theme to ttk widgets"""
    
    # ============================================================================
    # GENERAL WIDGET DEFAULTS
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
    # NOTEBOOK (Tab Container)
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
             background=[('selected', colors['primary']),
                        ('active', colors['hover'])],
             foreground=[('selected', 'white'),
                        ('active', colors['text'])],
             expand=[('selected', [1, 1, 1, 0])])
    
    # ============================================================================
    # BUTTONS
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
    
    # Accent button style
    style.configure('Accent.TButton',
                   background=colors['primary'],
                   foreground='white',
                   font=fonts['button'])
    
    style.map('Accent.TButton',
             background=[('active', colors['secondary']),
                        ('pressed', '#3d6360')],
             foreground=[('active', 'white'),
                        ('pressed', 'white')])
    
    # ============================================================================
    # LABELS
    # ============================================================================
    style.configure('TLabel',
                   background=colors['background'],
                   foreground=colors['text'],
                   font=fonts['body'])
    
    # ============================================================================
    # ENTRIES (Text Input)
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
    # COMBOBOX (Dropdown)
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
    # CHECKBUTTON
    # ============================================================================
    style.configure('TCheckbutton',
                   background=colors['background'],
                   foreground=colors['text'],
                   font=fonts['body'])
    
    style.map('TCheckbutton',
             background=[('active', colors['background'])],
             foreground=[('selected', colors['primary'])])
    
    # ============================================================================
    # RADIOBUTTON
    # ============================================================================
    style.configure('TRadiobutton',
                   background=colors['background'],
                   foreground=colors['text'],
                   font=fonts['body'])
    
    style.map('TRadiobutton',
             background=[('active', colors['background'])],
             foreground=[('selected', colors['primary'])])
    
    # ============================================================================
    # LABELFRAME
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
    # SCROLLBAR
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
    # TREEVIEW - Subtle alternating rows
    # ============================================================================
    style.configure('Treeview',
                   font=fonts['body'],
                   rowheight=25,
                   borderwidth=1,
                   background='white',
                   foreground=colors['text'],
                   fieldbackground='white')
    
    # Muted teal headers (not screaming blue!)
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
    # PROGRESSBAR
    # ============================================================================
    style.configure('TProgressbar',
                   background=colors['primary'],
                   troughcolor=colors['surface'],
                   bordercolor=colors['border'],
                   lightcolor=colors['primary'],
                   darkcolor=colors['primary'])
    
    # ============================================================================
    # SEPARATOR
    # ============================================================================
    style.configure('TSeparator',
                   background=colors['border'])
    
    # ============================================================================
    # SIZEGRIP
    # ============================================================================
    style.configure('TSizegrip',
                   background=colors['background'])

    print(f"[THEME] Warm Professional theme applied successfully")
