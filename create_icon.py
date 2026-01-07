"""
Create a custom icon for TimeTracker Pro
Generates a simple clock/stopwatch icon as .ico file
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_timetracker_icon():
    # Create icon at multiple sizes for Windows
    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    images = []
    
    for size in sizes:
        # Create image with transparent background
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Calculate dimensions
        width, height = size
        center_x, center_y = width // 2, height // 2
        radius = min(width, height) // 2 - 4
        
        # Draw outer circle (blue)
        draw.ellipse(
            [(center_x - radius, center_y - radius), 
             (center_x + radius, center_y + radius)],
            fill='#2196F3',
            outline='#1976D2',
            width=max(2, width // 64)
        )
        
        # Draw clock hands (white)
        hand_width = max(2, width // 32)
        # Hour hand (pointing to 10)
        draw.line(
            [(center_x, center_y), (center_x - radius // 3, center_y - radius // 2)],
            fill='white',
            width=hand_width
        )
        # Minute hand (pointing to 2)
        draw.line(
            [(center_x, center_y), (center_x + radius // 2, center_y - radius // 3)],
            fill='white',
            width=hand_width
        )
        
        # Draw center dot
        dot_size = max(4, width // 16)
        draw.ellipse(
            [(center_x - dot_size, center_y - dot_size),
             (center_x + dot_size, center_y + dot_size)],
            fill='white'
        )
        
        images.append(img)
    
    # Save as .ico
    icon_path = os.path.join(os.path.dirname(__file__), 'timetracker.ico')
    images[0].save(icon_path, format='ICO', sizes=[img.size for img in images])
    print(f"✓ Icon created: {icon_path}")
    return icon_path

if __name__ == "__main__":
    try:
        create_timetracker_icon()
        print("\nIcon ready! Update your shortcut:")
        print("1. Right-click shortcut → Properties → Change Icon")
        print("2. Browse to: timetracker.ico")
    except ImportError:
        print("ERROR: Pillow library required")
        print("Install: pip install Pillow")
    except Exception as e:
        print(f"ERROR: {e}")
