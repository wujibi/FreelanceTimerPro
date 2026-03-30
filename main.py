"""
Time Tracker Pro - Main Application Entry Point
"""
import sys
import os
from config import DB_PATH
from ui.tk import run_tk_app


def main():
    """Main application entry point"""
    # Print current working directory for debugging
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script location: {os.path.dirname(os.path.abspath(__file__))}")
    
    # Get database path (supports FREELANCETIMERPRO_DB_PATH override)
    db_path = DB_PATH
    print(f"[DEBUG] Using database: {db_path}")
    
    try:
        # Initialize and run the Tkinter UI with the database path
        run_tk_app(db_path=db_path)
        
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)


if __name__ == '__main__':
    main()
