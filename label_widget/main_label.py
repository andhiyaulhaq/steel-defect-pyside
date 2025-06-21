"""
Main module for the Annotator application.
"""

import sys

from PySide6.QtWidgets import QApplication, QMessageBox, QWidget

from .annotator import Annotator
from .ui_label import Ui_AnnotatorWidget

# --- Main execution block ---
if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)

        # 1. Create the main window/widget instance
        window = QWidget()

        # 2. Create an instance of the generated UI class
        # (Assuming ui_label.py was generated from a .ui file, e.g., by pyside6-uic)
        ui = Ui_AnnotatorWidget()

        # 3. Set up the UI on your main window
        ui.setupUi(window)

        # Now pass both the main window and the ui instance to your Annotator class
        annotator = Annotator(window, ui)

        # Show the main window maximized
        window.showMaximized()

        # Start the application event loop
        sys.exit(app.exec())
    except Exception as e:
        # Catch any unhandled exceptions and show a critical error message
        QMessageBox.critical(None, "Fatal Error", f"An error occurred: {str(e)}")
        sys.exit(1)
