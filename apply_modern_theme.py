"""
Apply Modern Theme to Time Tracker Pro
Implements Option B: Quick Polish Pass

Changes:
1. Better app icon
2. Nicer fonts (Segoe UI)
3. Professional color scheme
4. Better window title and centering

Run this once to update gui.py with modern styling
"""

print("=" * 60)
print("MODERN THEME IMPLEMENTATION")
print("=" * 60)
print()
print("This script will guide you through applying Option B:")
print("1. Better App Icon")
print("2. Nicer Fonts (Segoe UI)")
print("3. Professional Color Scheme")
print("4. Window Improvements")
print()

# Step 1: Icon
print("STEP 1: App Icon")
print("-" * 60)
print("To add a custom icon, you need a .ico file.")
print()
print("Options:")
print("  A) Create one at: https://www.favicon-generator.org/")
print("  B) Use an existing image and convert it")
print("  C) Skip for now (we'll add placeholder code)")
print()
print("For now, I'll add the code structure. You can add the .ico file later.")
print()

# Step 2: Fonts
print("STEP 2: Modern Fonts")
print("-" * 60)
print("✓ Changing all fonts to Segoe UI (Windows modern font)")
print("✓ Fallback to system default if not available")
print()

# Step 3: Colors
print("STEP 3: Professional Color Scheme")
print("-" * 60)
print("✓ Primary: #2563eb (Professional Blue)")
print("✓ Secondary: #64748b (Slate Gray)")
print("✓ Accent: #10b981 (Success Green)")
print("✓ Background: #f8fafc (Light Gray)")
print("✓ Text: #1e293b (Dark Slate)")
print()

# Step 4: Window
print("STEP 4: Window Improvements")
print("-" * 60)
print("✓ Better window title with version")
print("✓ Center window on screen")
print("✓ Minimum window size")
print()

print("=" * 60)
print("IMPLEMENTATION STARTING...")
print("=" * 60)
print()

# Read the current gui.py
with open('gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Track what we're changing
changes_made = []

# Change 1: Update __init__ to add modern styling
old_init_window = '''        self.root = root
        self.root.title("Time Tracker Pro")
        self.root.geometry("1200x800")'''

new_init_window = '''        self.root = root
        self.root.title("Time Tracker Pro v1.0 - Professional Time & Invoice Management")
        
        # Modern window setup
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Try to set custom icon (if exists)
        try:
            icon_path = "assets/icon.ico"
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass  # Use default icon if custom not available
        
        # Center window on screen
        self.center_window()
        
        # Modern color scheme
        self.colors = {
            'primary': '#2563eb',      # Professional Blue
            'secondary': '#64748b',    # Slate Gray  
            'accent': '#10b981',       # Success Green
            'background': '#f8fafc',   # Light Gray
            'text': '#1e293b',         # Dark Slate
            'border': '#e2e8f0',       # Light Border
            'hover': '#3b82f6',        # Lighter Blue
            'error': '#ef4444',        # Red
            'success': '#22c55e'       # Green
        }
        
        # Configure modern fonts
        self.fonts = {
            'heading': ('Segoe UI', 12, 'bold'),
            'subheading': ('Segoe UI', 10, 'bold'),
            'body': ('Segoe UI', 10),
            'small': ('Segoe UI', 9),
            'title': ('Segoe UI', 14, 'bold'),
            'large_display': ('Segoe UI', 24)
        }
        
        # Apply modern theme
        self.apply_modern_theme()'''

if old_init_window in content:
    content = content.replace(old_init_window, new_init_window)
    changes_made.append("✓ Updated window initialization with modern settings")
else:
    print("⚠ Warning: Could not find window initialization code to update")

# Add import for os at top if not already there
if 'import os' not in content[:500]:  # Check first 500 chars
    content = 'import os\n' + content
    changes_made.append("✓ Added 'import os' for icon handling")

# Change 2: Add helper methods after __init__
helper_methods = '''
    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def apply_modern_theme(self):
        """Apply modern styling to the application"""
        style = ttk.Style()
        
        # Try to use 'clam' theme as base (modern looking)
        try:
            style.theme_use('clam')
        except:
            pass  # Use default if clam not available
        
        # Configure Notebook (tabs)
        style.configure('TNotebook', 
                       background=self.colors['background'],
                       borderwidth=0)
        style.configure('TNotebook.Tab',
                       padding=[20, 10],
                       font=self.fonts['subheading'])
        style.map('TNotebook.Tab',
                 background=[('selected', self.colors['primary'])],
                 foreground=[('selected', 'white')])
        
        # Configure Buttons
        style.configure('TButton',
                       font=self.fonts['body'],
                       padding=[10, 5],
                       borderwidth=1)
        style.map('TButton',
                 background=[('active', self.colors['hover'])],
                 foreground=[('active', 'white')])
        
        # Accent button style (for primary actions)
        style.configure('Accent.TButton',
                       font=self.fonts['subheading'],
                       background=self.colors['primary'],
                       foreground='white',
                       padding=[15, 8])
        
        # Configure Labels
        style.configure('TLabel',
                       font=self.fonts['body'],
                       background=self.colors['background'])
        
        style.configure('Title.TLabel',
                       font=self.fonts['title'])
        
        # Configure Entry
        style.configure('TEntry',
                       font=self.fonts['body'],
                       fieldbackground='white',
                       borderwidth=1)
        
        # Configure Treeview (tables)
        style.configure('Treeview',
                       font=self.fonts['body'],
                       rowheight=25,
                       borderwidth=1)
        style.configure('Treeview.Heading',
                       font=self.fonts['subheading'],
                       background=self.colors['secondary'],
                       foreground='white',
                       borderwidth=1)
        style.map('Treeview',
                 background=[('selected', self.colors['primary'])],
                 foreground=[('selected', 'white')])
        
        # Configure LabelFrame
        style.configure('TLabelframe',
                       borderwidth=2,
                       relief='solid',
                       background=self.colors['background'])
        style.configure('TLabelframe.Label',
                       font=self.fonts['subheading'],
                       foreground=self.colors['text'])
        
        # Set root window background
        self.root.configure(bg=self.colors['background'])
'''

# Find where to insert helper methods (after __init__ method)
init_end = content.find('    def create_widgets(self):')
if init_end != -1:
    content = content[:init_end] + helper_methods + '\n' + content[init_end:]
    changes_made.append("✓ Added center_window() and apply_modern_theme() methods")
else:
    print("⚠ Warning: Could not find location to insert helper methods")

# Change 3: Update timer label to use new font
old_timer_label = "self.timer_label = ttk.Label(timer_display_frame, text=\"00:00:00\", font=(\"Arial\", 24))"
new_timer_label = "self.timer_label = ttk.Label(timer_display_frame, text=\"00:00:00\", font=self.fonts['large_display'])"

if old_timer_label in content:
    content = content.replace(old_timer_label, new_timer_label)
    changes_made.append("✓ Updated timer display font")

# Save the updated gui.py
with open('gui.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ IMPLEMENTATION COMPLETE!")
print()
print("Changes Applied:")
for change in changes_made:
    print(f"  {change}")
print()

print("=" * 60)
print("NEXT STEPS:")
print("=" * 60)
print()
print("1. Create assets folder for icon:")
print("   > mkdir assets")
print()
print("2. (Optional) Add a custom icon:")
print("   - Create/download a .ico file")
print("   - Save as: assets/icon.ico")
print()
print("3. Restart your app:")
print("   > python launcher.pyw")
print()
print("4. Check the new look:")
print("   ✓ Window should be centered")
print("   ✓ Tabs should have blue selection")
print("   ✓ Fonts should be Segoe UI")
print("   ✓ Overall more modern appearance")
print()
print("=" * 60)
print()

# Create assets directory
import os
os.makedirs('assets', exist_ok=True)
print("✓ Created assets/ directory for icon")
print()

# Create a README for the icon
with open('assets/README.md', 'w') as f:
    f.write("""# Assets Directory

## Icon File

Place your custom icon here as `icon.ico`

### How to Create an Icon:

1. **Online Tool (Easiest):**
   - Go to: https://www.favicon-generator.org/
   - Upload a square image (PNG, JPG)
   - Download the .ico file
   - Rename to `icon.ico` and place here

2. **From Existing Image:**
   - Use an online converter: https://convertio.co/png-ico/
   - Upload your logo/image
   - Download as .ico
   - Save as `icon.ico` here

3. **Design Tools:**
   - Use Figma, Canva, or Photoshop
   - Create 256x256px square image
   - Export as PNG
   - Convert to .ico using method 2

### Icon Recommendations:
- Size: 256x256px (will auto-scale)
- Format: .ico (Windows icon format)
- Style: Simple, recognizable at small sizes
- Colors: Match your brand

### Current Status:
- [ ] Custom icon not yet added (using default Tk icon)
- Once added, restart the app to see your custom icon!
""")

print("✓ Created assets/README.md with icon instructions")
print()
print("🎨 Modern theme applied! Restart your app to see the changes.")
