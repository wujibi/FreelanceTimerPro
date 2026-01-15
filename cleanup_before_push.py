#!/usr/bin/env python3
"""
Cleanup unnecessary files before Git push
Run this once, then delete this script too
"""

import os
from pathlib import Path

# Files to delete
files_to_delete = [
    'cleanup_junk_files.py',
    'create_icon.py',
    'fix_pycharm.bat',
    'create_desktop_shortcut.vbs',
    'create_start_menu_shortcut.vbs',
    'git_push_instructions.md',
    'MANUAL_ENTRY_FIX_COMPLETE.md',
    'COMPLETE_VERIFICATION_TEST.md',
    'QUICK_TEST_INVOICE_FIX.md',
    'FIX_LAPTOP_SHORTCUT.md',
    'INVOICE_BUG_FIX.md',
    'gui.py.backup_invoice_bug',
    'launch_timetracker.bat - Shortcut.lnk',
    'FILES_TO_DELETE.md'
]

# Directories to delete
dirs_to_delete = [
    '.idea_backup'
]

def main():
    script_dir = Path(__file__).parent
    deleted_files = []
    deleted_dirs = []
    not_found = []
    
    print("=" * 60)
    print("CLEANUP BEFORE GIT PUSH")
    print("=" * 60)
    print()
    
    # Delete files
    print("Deleting unnecessary files...")
    for filename in files_to_delete:
        filepath = script_dir / filename
        if filepath.exists():
            try:
                filepath.unlink()
                deleted_files.append(filename)
                print(f"  ✓ Deleted: {filename}")
            except Exception as e:
                print(f"  ✗ Error deleting {filename}: {e}")
        else:
            not_found.append(filename)
            print(f"  - Not found: {filename}")
    
    print()
    
    # Delete directories
    print("Deleting unnecessary directories...")
    for dirname in dirs_to_delete:
        dirpath = script_dir / dirname
        if dirpath.exists():
            try:
                import shutil
                shutil.rmtree(dirpath)
                deleted_dirs.append(dirname)
                print(f"  ✓ Deleted: {dirname}/")
            except Exception as e:
                print(f"  ✗ Error deleting {dirname}: {e}")
        else:
            not_found.append(dirname)
            print(f"  - Not found: {dirname}/")
    
    print()
    print("=" * 60)
    print("CLEANUP SUMMARY")
    print("=" * 60)
    print(f"Files deleted: {len(deleted_files)}")
    print(f"Directories deleted: {len(deleted_dirs)}")
    print(f"Not found (already deleted): {len(not_found)}")
    print()
    
    if deleted_files or deleted_dirs:
        print("✅ Cleanup complete!")
        print()
        print("Next steps:")
        print("1. Delete this cleanup script: cleanup_before_push.py")
        print("2. Run: git status")
        print("3. Run: git add .")
        print("4. Run: git commit -m \"Fix: Invoice tab now loads all entries including global tasks\"")
        print("5. Run: git push")
    else:
        print("✓ Nothing to clean up - already done!")
    
    print()

if __name__ == "__main__":
    main()
