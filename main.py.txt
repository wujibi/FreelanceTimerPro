import os
print(f"Current working directory: {os.getcwd()}")
print(f"Script location: {os.path.dirname(os.path.abspath(__file__))}")
print(f"Database will be at: {os.path.abspath('data/time_tracker.db')}")


import tkinter as tk
from gui import TimeTrackerApp

def main():
    # Create main window
    root = tk.Tk()
    
    # Create and run the application
    app = TimeTrackerApp(root)
    
    # Start the GUI event loop
    root.mainloop()

if __name__ == "__main__":
    main()
