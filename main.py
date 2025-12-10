import os
print(f"Current working directory: {os.getcwd()}")
print(f"Script location: {os.path.dirname(os.path.abspath(__file__))}")

# Import database path from config
from config import DB_PATH

import tkinter as tk
from gui import TimeTrackerApp

def main():
    print(f"[DEBUG] Using database: {DB_PATH}")
    root = tk.Tk()
    app = TimeTrackerApp(root, db_path=DB_PATH)
    root.mainloop()

if __name__ == "__main__":
    main()
