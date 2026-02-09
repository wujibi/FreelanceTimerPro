"""
Burnt Orange Theme - Based on user's website color scheme
Warm taupe background with burnt orange accents
Sophisticated, distinctive, professional
"""

def get_colors():
    """Return the color palette for Burnt Orange theme"""
    return {
        'background': '#dad2cd',           # Warm taupe background
        'surface': '#cdc4be',              # Slightly darker taupe
        'primary': '#ce6427',              # Burnt orange (PRIMARY accent)
        'secondary': '#454f59',            # Cool gray-blue
        'text': '#13100f',                 # Very dark brown (almost black)
        'text_secondary': '#5a534f',       # Medium brown-gray
        'border': '#b8aea8',               # Medium taupe border
        'hover': '#e8e0db',                # Light taupe hover
        'selected': '#ce6427',             # Burnt orange for selections
        'alt_row': '#e5ded9',              # Light warm gray for alternating rows
        'accent_dark': '#181c20',          # Very dark blue-black (for special use)
        'success': '#5a8f5a',              # Muted green
        'warning': '#ce6427',              # Use burnt orange for warnings too
        'danger': '#b85450'                # Muted red
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
    """Apply the Burnt Orange theme to ttk widgets"""
    
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
    
    # BURNT ORANGE active tab with WHITE text
    style.map('TNotebook.Tab',
             background=[('selected', colors['primary']),      # Burnt orange active tab
                        ('active', colors['hover'])],
             foreground=[('selected', 'white'),                # WHITE TEXT on active tab
                        ('active', colors['text'])],           # Dark text on hover
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
    
    # Accent button style - BURNT ORANGE
    style.configure('Accent.TButton',
                   background=colors['primary'],
                   foreground='white',
                   font=fonts['button'])
    
    style.map('Accent.TButton',
             background=[('active', '#b85620'),                # Darker orange on hover
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
             bordercolor=[('focus', colors['primary'])],       # Orange focus border
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
    # TREEVIEW - Burnt orange headers!
    # ============================================================================
    style.configure('Treeview',
                   font=fonts['body'],
                   rowheight=25,
                   borderwidth=1,
                   background='white',
                   foreground=colors['text'],
                   fieldbackground='white')
    
    # BURNT ORANGE headers with white text
    style.configure('Treeview.Heading',
                   font=fonts['subheading'],
                   background=colors['primary'],              # BURNT ORANGE header
                   foreground='white',                        # WHITE TEXT
                   borderwidth=1,
                   relief='flat')
    
    style.map('Treeview',
             background=[('selected', colors['primary'])],   # Orange selection
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

    print(f"[THEME] Burnt Orange theme applied successfully")
