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
