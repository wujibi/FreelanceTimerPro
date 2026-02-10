"""
Burnt Orange Professional V3 - Orange + Teal Hierarchy
Uses muted teal for group headings, burnt orange for selections
Creates strong visual hierarchy with complementary colors
"""

def get_colors():
    """Return the color palette for Burnt Orange Professional V3 theme"""
    return {
        'background': '#dad2cd',           # Warm taupe background
        'surface': '#cdc4be',              # Slightly darker taupe for panels
        'primary': '#ce6427',              # BURNT ORANGE (main brand color)
        'secondary': '#454f59',            # Cool gray-blue for subtle elements
        'text': '#13100f',                 # Very dark brown (almost black)
        'text_secondary': '#5a534f',       # Medium brown-gray
        'border': '#b8aea8',               # Medium taupe border
        'hover': '#e8ded9',                # Light taupe hover
        'selected': '#ce6427',             # Burnt orange for selections
        'alt_row': '#e5ded9',              # Light warm gray for alternating rows
        'accent_dark': '#181c20',          # Very dark blue-black
        'success': '#5a8f5a',              # Muted green
        'warning': '#ce6427',              # Burnt orange
        'danger': '#b85450',               # Muted red
        'orange_hover': '#b85520',         # Darker orange for hover
        'group_heading': '#5a8f8f',        # MUTED TEAL for group headings
        'group_text': 'white',             # White text on teal
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
    """Apply the Burnt Orange Professional V3 theme to ttk widgets"""
    
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
             foreground=[('selected', colors['text']),
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
             background=[('pressed', colors['primary']),
                        ('active', colors['hover'])],
             foreground=[('pressed', 'white'),
                        ('active', colors['text'])],
             relief=[('pressed', 'flat')])
    
    style.configure('Accent.TButton',
                   background=colors['primary'],
                   foreground=colors['text'],              # DARK TEXT on orange (readable!)
                   font=fonts['button'])
    
    style.map('Accent.TButton',
             background=[('active', colors['orange_hover']),
                        ('pressed', colors['secondary'])],
             foreground=[('active', colors['text']),      # Dark text on hover
                        ('pressed', colors['text'])])     # Dark text when pressed
    
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
    # TREEVIEW - BURNT ORANGE headers!
    # ============================================================================
    style.configure('Treeview',
                   font=fonts['body'],
                   rowheight=25,
                   borderwidth=1,
                   background='white',
                   foreground=colors['text'],
                   fieldbackground='white')
    
    style.configure('Treeview.Heading',
                   font=fonts['subheading'],
                   background=colors['primary'],              # BURNT ORANGE header
                   foreground='white',
                   borderwidth=1,
                   relief='flat')
    
    style.map('Treeview',
             background=[('selected', colors['primary'])],   # Full orange for selected entries
             foreground=[('selected', 'white')])
    
    style.map('Treeview.Heading',
             background=[('active', colors['orange_hover'])],
             foreground=[('active', 'white')])
    
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

    print(f"[THEME] Burnt Orange Professional V3 (Orange + Teal) theme applied successfully")
