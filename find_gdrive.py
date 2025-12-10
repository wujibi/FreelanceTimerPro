"""Find Google Drive path on this computer"""
import os
from pathlib import Path


def find_google_drive():
    print("Searching for Google Drive...")
    print()

    # Common Google Drive locations on Windows
    possible_paths = [
        Path.home() / "Google Drive",
        Path.home() / "GoogleDrive",
        Path("G:/My Drive"),
        Path("G:/"),
        Path(os.environ.get('USERPROFILE', '')) / "Google Drive",
    ]

    # Check all drives for Google Drive
    for drive in ['C:', 'D:', 'E:', 'F:', 'G:', 'H:']:
        possible_paths.extend([
            Path(f"{drive}/Google Drive"),
            Path(f"{drive}/GoogleDrive"),
            Path(f"{drive}/My Drive"),
        ])

    print("Checking these locations:")
    found_paths = []

    for path in possible_paths:
        print(f"  Checking: {path}")
        if path.exists():
            print(f"    ✓ FOUND!")
            found_paths.append(path)
            # List contents
            try:
                contents = list(path.iterdir())[:5]  # First 5 items
                print(f"    Contents: {[p.name for p in contents]}")
            except:
                pass

    print()
    if found_paths:
        print("=" * 60)
        print("FOUND GOOGLE DRIVE LOCATIONS:")
        for i, path in enumerate(found_paths, 1):
            print(f"{i}. {path}")
        print("=" * 60)
    else:
        print("❌ Google Drive not found on this computer")
        print()
        print("Please manually navigate to your Google Drive folder and copy the path")
        print("In File Explorer, click the address bar and copy the path")

    return found_paths


if __name__ == "__main__":
    find_google_drive()
    input("\nPress Enter to exit...")
