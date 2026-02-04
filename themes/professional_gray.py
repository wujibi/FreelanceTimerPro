"""
Professional Gray Theme
Clean, neutral gray theme with blue accents
Based on the original Time Tracker Pro design
"""

def get_colors():
    """Return color palette for Professional Gray theme"""
    return {
        'primary': '#2563eb',      # Professional Blue (accent)
        'secondary': '#64748b',    # Slate Gray  
        'accent': '#10b981',       # Success Green
        'background': '#f8fafc',   # Light Gray
        'text': '#1e293b',         # Dark Slate
        'border': '#e2e8f0',       # Light Border
        'hover': '#3b82f6',        # Lighter Blue
        'error': '#ef4444',        # Red
        'success': '#22c55e'       # Green
    }


def get_fonts():
    """Return font definitions for Professional Gray theme"""
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
    Apply Professional Gray theme to ttk.Style object
    
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
    
    # Configure Notebook (tabs) - flat style, no raising
    style.configure('TNotebook', 
                   background=colors['background'],
                   borderwidth=0,
                   relief='flat')
    style.configure('TNotebook.Tab',
                   padding=[20, 10],
                   font=fonts['subheading'],
                   relief='flat',
                   borderwidth=1)
    style.map('TNotebook.Tab',
             background=[('selected', colors['primary'])],
             foreground=[('selected', 'white')],
             relief=[('selected', 'flat')])
    
    # Configure Buttons
    style.configure('TButton',
                   font=fonts['body'],
                   padding=[10, 5],
                   borderwidth=1)
    style.map('TButton',
             background=[('active', colors['hover'])],
             foreground=[('active', 'white')])
    
    # Accent button style (for primary actions)
    style.configure('Accent.TButton',
                   font=fonts['subheading'],
                   background=colors['primary'],
                   foreground='white',
                   padding=[15, 8])
    
    # Configure Labels
    style.configure('TLabel',
                   font=fonts['body'],
                   background=colors['background'])
    
    style.configure('Title.TLabel',
                   font=fonts['title'])
    
    # Configure Entry
    style.configure('TEntry',
                   font=fonts['body'],
                   fieldbackground='white',
                   borderwidth=1)
    
    # Configure Treeview (tables)
    style.configure('Treeview',
                   font=fonts['body'],
                   rowheight=25,
                   borderwidth=1)
    style.configure('Treeview.Heading',
                   font=fonts['subheading'],
                   background=colors['secondary'],
                   foreground='white',
                   borderwidth=1)
    style.map('Treeview',
             background=[('selected', colors['primary'])],
             foreground=[('selected', 'white')])
    
    # Configure LabelFrame
    style.configure('TLabelframe',
                   borderwidth=2,
                   relief='solid',
                   background=colors['background'])
    style.configure('TLabelframe.Label',
                   font=fonts['subheading'],
                   foreground=colors['text'])
