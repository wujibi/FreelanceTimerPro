"""
Burnt Orange Professional Theme - DEFAULT THEME
Warm, sophisticated, matches FreelanceTimer.pro website branding
Based on the color scheme: #ce6427 (burnt orange) + #dad2cd (warm taupe)
"""

def get_colors():
    """Return the color palette for Burnt Orange Professional theme"""
    return {
        'background': '#dad2cd',           # Warm taupe background (like website)
        'surface': '#cdc4be',              # Slightly darker taupe for panels
        'primary': '#ce6427',              # BURNT ORANGE (brand color!)
        'secondary': '#454f59',            # Cool gray-blue for subtle elements
        'text': '#13100f',                 # Very dark brown (almost black)
        'text_secondary': '#5a534f',       # Medium brown-gray for secondary text
        'border': '#b8aea8',               # Medium taupe border
        'hover': '#e8ded9',                # Light taupe hover (barely visible, subtle)
        'selected': '#ce6427',             # Burnt orange for selections
        'alt_row': '#e5ded9',              # Light warm gray for alternating rows
        'accent_dark': '#181c20',          # Very dark blue-black (special use)
        'success': '#5a8f5a',              # Muted green
        'warning': '#ce6427',              # Use burnt orange for warnings
        'danger': '#b85450',               # Muted red
        'orange_hover': '#b85520',         # Darker orange for button hover
        'group_heading': '#ce6427',        # Burnt orange for group headings (same as primary)
        'group_text': 'white',             # White text on orange headings
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
    """Apply the Burnt Orange Professional theme to ttk widgets"""
    
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
    # NOTEBOOK (Tab Container) - ORANGE ACTIVE TABS!
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
    
    # BURNT ORANGE active tab with WHITE text - THIS IS THE FIX!
    style.map('TNotebook.Tab',
             background=[('selected', colors['primary']),      # BURNT ORANGE active tab
                        ('active', colors['hover'])],           # Light hover
             foreground=[('selected', colors['text']),                # WHITE TEXT on orange (FIX!)
                        ('active', colors['primary'])],         # Orange text on hover
             expand=[('selected', [1, 1, 1, 0])])
    
    # ============================================================================
    # BUTTONS - Orange accent buttons!
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
    
    # Accent button style - BURNT ORANGE primary actions
    style.configure('Accent.TButton',
                   background=colors['primary'],
                   foreground='white',
                   font=fonts['button'])
    
    style.map('Accent.TButton',
             background=[('active', colors['orange_hover']),    # Darker orange on hover
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
    # ENTRIES (Text Input) - Orange focus border!
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
             bordercolor=[('focus', colors['primary'])],        # ORANGE focus border!
             lightcolor=[('focus', colors['primary'])],
             darkcolor=[('focus', colors['primary'])])
    
    # ============================================================================
    # COMBOBOX (Dropdown) - Orange focus!
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
             bordercolor=[('focus', colors['primary'])],        # ORANGE focus!
             lightcolor=[('focus', colors['primary'])],
             darkcolor=[('focus', colors['primary'])],
             foreground=[('readonly', colors['text'])])
    
    # ============================================================================
    # CHECKBUTTON - Orange when selected
    # ============================================================================
    style.configure('TCheckbutton',
                   background=colors['background'],
                   foreground=colors['text'],
                   font=fonts['body'])
    
    style.map('TCheckbutton',
             background=[('active', colors['background'])],
             foreground=[('selected', colors['primary'])])
    
    # ============================================================================
    # RADIOBUTTON - Orange when selected
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
    # TREEVIEW - BURNT ORANGE headers with white text!
    # ============================================================================
    style.configure('Treeview',
                   font=fonts['body'],
                   rowheight=25,
                   borderwidth=1,
                   background='white',
                   foreground=colors['text'],
                   fieldbackground='white')
    
    # BURNT ORANGE headers with white text (matches website!)
    style.configure('Treeview.Heading',
                   font=fonts['subheading'],
                   background=colors['primary'],              # BURNT ORANGE header!
                   foreground='white',                        # WHITE TEXT
                   borderwidth=1,
                   relief='flat')
    
    style.map('Treeview',
             background=[('selected', colors['primary'])],   # Orange selection
             foreground=[('selected', 'white')])
    
    style.map('Treeview.Heading',
             background=[('active', colors['orange_hover'])],  # Darker orange on hover
             foreground=[('active', 'white')])
    
    # ============================================================================
    # FRAMES & CONTAINERS
    # ============================================================================
    style.configure('TFrame',
                   background=colors['background'])
    
    # ============================================================================
    # PROGRESSBAR - Orange progress bars!
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

    print(f"[THEME] Burnt Orange Professional theme applied successfully")
