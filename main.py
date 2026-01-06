"""
Time Tracker Pro - Main Application Entry Point
"""
import sys
import os
import tkinter as tk
from pathlib import Path
from gui import TimeTrackerApp


def get_database_path():
    """Determine the database path (Google Drive or local)"""
    # Try multiple common Google Drive paths
    possible_paths = [
        Path.home() / "My Drive" / "TimeTrackerApp" / "data" / "time_tracker.db",
        Path("C:/Users/briah/My Drive/TimeTrackerApp/data/time_tracker.db"),
        Path.home() / "Google Drive" / "TimeTrackerApp" / "data" / "time_tracker.db",
        Path("G:/My Drive/TimeTrackerApp/data/time_tracker.db"),
    ]
    
    print("[DEBUG] Searching for Google Drive database...")
    for path in possible_paths:
        print(f"[DEBUG] Checking: {path}")
        if path.parent.exists():
            print(f"[CONFIG] ✓ Found Google Drive database: {path}")
            # Create directory if needed
            path.parent.mkdir(parents=True, exist_ok=True)
            return str(path)
        else:
            print(f"[CONFIG] ✗ Path not found: {path}")
    
    # Fallback to local data directory
    local_path = Path("data") / "time_tracker.db"
    print(f"[CONFIG] Using local database: {local_path}")
    local_path.parent.mkdir(parents=True, exist_ok=True)
    return str(local_path)


def main():
    """Main application entry point"""
    # Print current working directory for debugging
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script location: {os.path.dirname(os.path.abspath(__file__))}")
    
    # Get database path (Google Drive or local)
    db_path = get_database_path()
    print(f"[DEBUG] Using database: {db_path}")
    
    # Create the main window
    root = tk.Tk()
    
    try:
        # Initialize the application with the database path
        app = TimeTrackerApp(root, db_path=db_path)
        
        # Start the GUI event loop
        root.mainloop()
        
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)


if __name__ == '__main__':
    main()
