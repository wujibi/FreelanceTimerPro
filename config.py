"""
Configuration file for Time Tracker App
"""
import os

# Database path - Using Google Drive for sync between computers
# The r"..." prefix handles the spaces in "My Drive" correctly
DB_PATH = r"C:\Users\briah\My Drive\TimeTrackerApp\data\time_tracker.db"

# Verify the directory exists
db_dir = os.path.dirname(DB_PATH)
if not os.path.exists(db_dir):
    print(f"[CONFIG] WARNING: Google Drive directory not found: {db_dir}")
    print(f"[CONFIG] Falling back to local database")
    DB_PATH = os.path.abspath("data/time_tracker.db")
else:
    print(f"[CONFIG] Using Google Drive database: {DB_PATH}")
