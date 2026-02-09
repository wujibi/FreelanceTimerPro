"""
Balanced Navy Theme - The Goldilocks version
Not too dark (like Deep Navy Pro), not too bright (like Light Navy Pro)
Uses a soft gray background with navy accents - easy on the eyes for long sessions
"""

def get_colors():
    """Return the color palette for Balanced Navy theme"""
    return {
        'background': '#f5f7fa',           # Soft light gray (not stark white!)
        'surface': '#e8ecf1',              # Slightly darker gray for contrast
        'primary': '#1a73e8',              # Medium Blue (accent color)
        'secondary': '#2c4a7c',            # Muted navy (less harsh than #0b1d3d)
        'text': '#2c3e50',                 # Dark gray text
        'text_secondary': '#6c757d',       # Medium gray for secondary text
        'border': '#d0d7de',               # Soft border
        'hover': '#e3f2fd',                # Very light blue hover
        'selected': '#1a73e8',             # Medium Blue for selections
        'alt_row': '#edf2f7',              # Light gray-blue for alternating rows
        'success': '#10b981',              # Green
        'warning': '#f59e0b',              # Orange
        'danger': '#ef4444'                # Red
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
    """Apply the Balanced Navy theme to ttk widgets"""
    
    # ============================================================================
    # GENERAL WIDGET DEFAULTS - Soft gray background
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
    # NOTEBOOK (Tab Container) - Muted navy accent
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
             background=[('selected', colors['secondary']),  # Muted navy for active tab
                        ('active', colors['hover'])],
             foreground=[('selected', 'white'),
                        ('active', colors['primary'])],
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
             background=[('active', '#1557b0'),
                        ('pressed', colors['secondary'])],
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
    # ENTRIES (Text Input) - White fields on gray background
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
    # TREEVIEW - Subtle alternating gray rows
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

    print(f"[THEME] Balanced Navy theme applied successfully")
