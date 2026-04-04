"""
Time Tracker Pro - Main Application Entry Point
"""
import sys
import os
from config import DB_PATH
from ui.tk import run_tk_app


def _ui_backend() -> str:
    """Tk remains default; set FREELANCETIMERPRO_UI=ctk for the CTk scaffold."""
    raw = os.environ.get("FREELANCETIMERPRO_UI", "").strip().lower()
    if raw in ("ctk", "customtkinter"):
        return "ctk"
    return "tk"


def main():
    """Main application entry point"""
    # Print current working directory for debugging
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script location: {os.path.dirname(os.path.abspath(__file__))}")
    
    # Get database path (supports FREELANCETIMERPRO_DB_PATH override)
    db_path = DB_PATH
    print(f"[DEBUG] Using database: {db_path}")
    
    try:
        backend = _ui_backend()
        if backend == "ctk":
            try:
                from ui.ctk import run_ctk_app
            except ImportError as exc:
                print(
                    "[WARN] FREELANCETIMERPRO_UI=ctk but CustomTkinter is not available "
                    f"({exc!r}); falling back to Tk. Install: pip install customtkinter"
                )
                run_tk_app(db_path=db_path)
            else:
                run_ctk_app(db_path=db_path)
        else:
            run_tk_app(db_path=db_path)
        
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)


if __name__ == '__main__':
    main()
