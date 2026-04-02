"""
Configuration file for Freelance Timer Pro
"""
import os
from pathlib import Path


def get_db_path():
    """
    Determine database path.
    Checks common Google Drive locations first, falls back to local data folder.
    """
    override = os.environ.get("FREELANCETIMERPRO_DB_PATH")
    if override:
        override_path = Path(override)
        override_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"[CONFIG] Using overridden database path: {override_path}")
        return str(override_path)

    possible_google_drive_paths = [
        Path.home() / "My Drive" / "FreelanceTimerPro" / "data" / "time_tracker.db",
        Path.home() / "Google Drive" / "FreelanceTimerPro" / "data" / "time_tracker.db",
        Path("G:/My Drive/FreelanceTimerPro/data/time_tracker.db"),
    ]

    for path in possible_google_drive_paths:
        if path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            print(f"[CONFIG] Using Google Drive database: {path}")
            return str(path)

    # Default: store alongside the app in a local data folder
    if getattr(__import__('sys'), 'frozen', False):
        # Running as a PyInstaller .exe
        app_dir = Path(os.path.dirname(__import__('sys').executable))
    else:
        # Running as normal Python script
        app_dir = Path(__file__).parent

    local_path = app_dir / "data" / "time_tracker.db"
    local_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"[CONFIG] Using local database: {local_path}")
    return str(local_path)


DB_PATH = get_db_path()

# UI bootstrap constants (used by Tkinter frontend)
APP_TITLE = "Freelance Timer Pro V3 - Professional Time & Invoice Management"
DEFAULT_WINDOW_GEOMETRY = "1200x800"
DEFAULT_MIN_WINDOW_SIZE = (600, 400)
ASSETS_DIRNAME = "assets"
APP_ICON_FILENAME = "icon.ico"
DEFAULT_THEME_NAME = "Burnt Orange Pro V3"
