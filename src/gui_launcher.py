"""Launcher for the optional PySide6 GUI."""

import sys


def launch_gui() -> int:
    """Start the CacheVis-RV desktop GUI if PySide6 is installed."""
    try:
        from PySide6.QtWidgets import QApplication
        from app_window import CacheVisMainWindow
    except ImportError as exc:
        print("PySide6 is required to start the GUI.")
        print("Install dependencies with: pip install -r requirements.txt")
        print(f"Import error: {exc}")
        return 1

    app = QApplication(sys.argv)
    window = CacheVisMainWindow()
    window.show()
    return app.exec()
