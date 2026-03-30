"""Tkinter application bootstrap helpers."""

import tkinter as tk

from gui import TimeTrackerApp


class TkApp:
    """Thin Tkinter app runner used by the entrypoint."""

    def __init__(self, db_path=None):
        self.db_path = db_path
        self.root = None
        self.app = None

    def run(self):
        """Create and run the Tkinter application loop."""
        self.root = tk.Tk()
        self.app = TimeTrackerApp(self.root, db_path=self.db_path)
        self.root.mainloop()


def run_tk_app(db_path=None):
    """Compatibility helper for running the Tk frontend."""
    TkApp(db_path=db_path).run()

