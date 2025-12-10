from pathlib import Path

gdrive_root = Path("G:/")
target_folder = gdrive_root / "My Drive" / "App Development Files" / "G Drive DB"

print(f"Checking: {target_folder}")
print(f"Exists: {target_folder.exists()}")

if not target_folder.exists():
    print("\nLet's check what IS in G:/")
    for item in gdrive_root.iterdir():
        print(f"  {item.name}")
        if item.is_dir() and "drive" in item.name.lower():
            print(f"    Checking inside {item.name}:")
            try:
                for subitem in item.iterdir():
                    print(f"      {subitem.name}")
            except:
                pass
