"""
Time Tracker Pro - Main Application Entry Point
"""
import sys
import os
import tkinter as tk
from gui import TimeTrackerApp
from config import DB_PATH


def main():
    """Main application entry point"""
    # Print current working directory for debugging
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script location: {os.path.dirname(os.path.abspath(__file__))}")
    
    # Get database path (supports FREELANCETIMERPRO_DB_PATH override)
    db_path = DB_PATH
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
