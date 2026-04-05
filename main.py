"""
Time Tracker Pro - Main Application Entry Point
"""
import sys
import os
from config import DB_PATH
from ui.tk import run_tk_app


def _ui_backend() -> str:
    """CustomTkinter is the default UI. Classic Tk: --tk / --ui=tk or FREELANCETIMERPRO_UI=tk."""
    for arg in sys.argv[1:]:
        a = arg.strip().lower()
        if a in ("--ctk", "--customtkinter"):
            return "ctk"
        if a in ("--tk", "--classic"):
            return "tk"
        if a.startswith("--ui="):
            v = a.split("=", 1)[1].strip()
            if v in ("ctk", "customtkinter"):
                return "ctk"
            if v in ("tk", "classic", "tkinter"):
                return "tk"
    raw = os.environ.get("FREELANCETIMERPRO_UI", "").strip().lower()
    if raw in ("tk", "classic", "tkinter"):
        return "tk"
    if raw in ("ctk", "customtkinter"):
        return "ctk"
    return "ctk"


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
        print(f"[DEBUG] UI backend: {backend} (use --tk or FREELANCETIMERPRO_UI=tk for classic Tk)")
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
