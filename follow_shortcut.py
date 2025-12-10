"""Follow the My Drive shortcut to find real path"""
import os
import win32com.client

try:
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(r"G:\My Drive.lnk")
    target = shortcut.Targetpath
    print(f"Shortcut points to: {target}")

    # Check if target exists
    if os.path.exists(target):
        print(f"✓ Target exists!")
        print(f"\nContents:")
        for item in os.listdir(target)[:10]:
            print(f"  {item}")
    else:
        print(f"✗ Target does not exist")

except ImportError:
    print("Installing required package...")
    print("Run: pip install pywin32")
    print("\nOR manually:")
    print("1. Right-click 'My Drive.lnk' in G:\\")
    print("2. Click Properties")
    print("3. Copy the 'Target' path")
    print("4. Share that path with me")
except Exception as e:
    print(f"Error: {e}")
    print("\nManual method:")
    print("1. Navigate to G:\\ in File Explorer")
    print("2. Right-click 'My Drive.lnk'")
    print("3. Click Properties")
    print("4. Copy the 'Target' field")
    print("5. Paste it here")
