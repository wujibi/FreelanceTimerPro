#!/usr/bin/env python3
"""
Cleanup script to remove junk files from failed Claude session
Created: January 13, 2026
"""

import os
from pathlib import Path

# Files to delete (confirmed junk from failed session)
JUNK_FILES = [
    "Backup_GUI.txt",
    "FINAL_FIX.txt",
    "FIX_INSTRUCTIONS.txt",
    "GUI_FIX_INSTRUCTIONS.md",
    "FIXES_SUMMARY.md",
    "README_FIXES.md",
    "QUICKFIX_gui_syntax.md",
    "add_time_entries_filter.p.py",
    "check_syntax.py",
    "emergency_fix.py",
    "find_and_show_method.py",
    "find_syntax_error.py",
    "fix_add_manual_entry.py",
    "show_lines.py",
    "WORKING_add_manual_entry.py",
]

def main():
    base_path = Path(__file__).parent
    deleted = []
    not_found = []
    errors = []
    
    print("=" * 60)
    print("CLEANUP SCRIPT - Removing Junk Files from Failed Session")
    print("=" * 60)
    print()
    
    for filename in JUNK_FILES:
        filepath = base_path / filename
        try:
            if filepath.exists():
                filepath.unlink()
                deleted.append(filename)
                print(f"✅ Deleted: {filename}")
            else:
                not_found.append(filename)
                print(f"⚠️  Not found: {filename}")
        except Exception as e:
            errors.append((filename, str(e)))
            print(f"❌ Error deleting {filename}: {e}")
    
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"✅ Successfully deleted: {len(deleted)} files")
    print(f"⚠️  Not found: {len(not_found)} files")
    print(f"❌ Errors: {len(errors)} files")
    print()
    
    if deleted:
        print("Deleted files:")
        for f in deleted:
            print(f"  - {f}")
    
    if errors:
        print()
        print("Errors encountered:")
        for f, err in errors:
            print(f"  - {f}: {err}")
    
    print()
    print("✅ Cleanup complete!")
    print()
    print("KEPT (important files):")
    print("  ✅ gui.py (your main app)")
    print("  ✅ gui.py.backup_manual_entry_fix (backup)")
    print("  ✅ MANUAL_ENTRY_FIX_COMPLETE.md (documentation)")
    print()

if __name__ == "__main__":
    main()
