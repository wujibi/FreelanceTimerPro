"""
Time Tracker Pro - Main Application Entry Point
"""
import sys
import os
from config import DB_PATH
from ui.tk import run_tk_app


def _ui_backend() -> str:
    """Tk remains default. Use CTk via env FREELANCETIMERPRO_UI=ctk or args --ctk / --ui=ctk."""
    for arg in sys.argv[1:]:
        a = arg.strip().lower()
        if a in ("--ctk", "--customtkinter"):
            return "ctk"
        if a == "--tk":
            return "tk"
        if a.startswith("--ui="):
            v = a.split("=", 1)[1].strip()
            if v in ("ctk", "customtkinter"):
                return "ctk"
            if v == "tk":
                return "tk"
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
        print(f"[DEBUG] UI backend: {backend} (use --ctk or FREELANCETIMERPRO_UI=ctk for CustomTkinter)")
        if backend == "ctk":
            try:
                from ui.ctk import run_ctk_app
            except ImportError as exc:
                print()
                print("*" * 72)
                print("  CustomTkinter UI was requested but the package is not installed.")
                print("  Install it in THIS Python, then run again:")
                print("    python -m pip install customtkinter")
                print(f"  Import error: {exc!r}")
                print("*" * 72)
                print()
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
