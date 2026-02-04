"""
Dark Mode Theme
Modern dark theme with reduced eye strain
"""

def get_colors():
    """Return color palette for Dark Mode theme"""
    return {
        'primary': '#60a5fa',      # Light Blue (accent)
        'secondary': '#475569',    # Dark Slate
        'accent': '#34d399',       # Success Green
        'background': '#1e293b',   # Dark Blue-Gray
        'text': '#f1f5f9',         # Light Gray (text)
        'border': '#334155',       # Medium Slate
        'hover': '#3b82f6',        # Brighter Blue
        'error': '#f87171',        # Light Red
        'success': '#4ade80'       # Light Green
    }


def get_fonts():
    """Return font definitions for Dark Mode theme"""
    return {
        'heading': ('Segoe UI', 12, 'bold'),
        'subheading': ('Segoe UI', 10, 'bold'),
        'body': ('Segoe UI', 10),
        'small': ('Segoe UI', 9),
        'title': ('Segoe UI', 14, 'bold'),
        'large_display': ('Segoe UI', 24)
    }


def apply_theme(style, colors, fonts):
    """
    Apply Dark Mode theme to ttk.Style object
    
    Args:
        style: ttk.Style() instance
        colors: Color palette dict from get_colors()
        fonts: Font definitions dict from get_fonts()
    """
    
    # Use 'alt' theme as base
    try:
        style.theme_use('alt')
    except:
        try:
            style.theme_use('clam')
        except:
            pass
    
    # Configure Notebook (tabs)
    style.configure('TNotebook', 
                   background=colors['background'],
                   borderwidth=0,
                   relief='flat')
    style.configure('TNotebook.Tab',
                   padding=[20, 10],
                   font=fonts['subheading'],
                   relief='flat',
                   borderwidth=1,
                   background=colors['secondary'],
                   foreground=colors['text'])
    style.map('TNotebook.Tab',
             background=[('selected', colors['primary'])],
             foreground=[('selected', colors['background'])],
             relief=[('selected', 'flat')])
    
    # Configure Buttons
    style.configure('TButton',
                   font=fonts['body'],
                   padding=[10, 5],
                   borderwidth=1,
                   background=colors['secondary'],
                   foreground=colors['text'])
    style.map('TButton',
             background=[('active', colors['hover'])],
             foreground=[('active', 'white')])
    
    # Accent button style
    style.configure('Accent.TButton',
                   font=fonts['subheading'],
                   background=colors['primary'],
                   foreground=colors['background'],
                   padding=[15, 8])
    
    # Configure Labels
    style.configure('TLabel',
                   font=fonts['body'],
                   background=colors['background'],
                   foreground=colors['text'])
    
    style.configure('Title.TLabel',
                   font=fonts['title'],
                   foreground=colors['text'])
    
    # Configure Entry - use lighter background for input fields
    style.configure('TEntry',
                   font=fonts['body'],
                   fieldbackground=colors['secondary'],
                   foreground=colors['text'],
                   borderwidth=1)
    
    # Configure Treeview
    style.configure('Treeview',
                   font=fonts['body'],
                   rowheight=25,
                   borderwidth=1,
                   background=colors['secondary'],
                   foreground=colors['text'],
                   fieldbackground=colors['secondary'])
    style.configure('Treeview.Heading',
                   font=fonts['subheading'],
                   background=colors['background'],
                   foreground=colors['text'],
                   borderwidth=1)
    style.map('Treeview',
             background=[('selected', colors['primary'])],
             foreground=[('selected', colors['background'])])
    
    # Configure LabelFrame
    style.configure('TLabelframe',
                   borderwidth=2,
                   relief='solid',
                   background=colors['background'])
    style.configure('TLabelframe.Label',
                   font=fonts['subheading'],
                   foreground=colors['text'],
                   background=colors['background'])
