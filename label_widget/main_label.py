"""
Main module for the Annotator application.
"""

import sys

from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .annotator import Annotator
from .ui_label import Ui_AnnotatorWidget

# --- Main execution block ---
if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)

        # 1. Create the main window/widget instance
        window = QWidget()

        # Create main horizontal layout
        main_layout = QHBoxLayout(window)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create left sidebar container widget
        sidebar_widget = QWidget()
        sidebar_widget.setFixedWidth(200)
        sidebar_widget.setStyleSheet("background-color: #f0f0f0;")

        # Create left sidebar layout
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        sidebar_layout.setSpacing(10)

        # Add combo box to sidebar
        combo_box = QComboBox()
        combo_box.addItems(["Main", "Detect", "Label", "Train", "Report", "Admin"])
        combo_box.setCurrentText("Label")
        sidebar_layout.addWidget(combo_box)

        # Add stretch to push logout button to bottom
        sidebar_layout.addStretch()

        # Add logout button to sidebar
        logout_button = QPushButton("LOGOUT")
        sidebar_layout.addWidget(logout_button)

        # Add vertical line separator
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("QFrame{color: #cccccc;}")

        # Create container for main content
        content_widget = QWidget()

        # Remove this line that creates the conflicting layout
        # content_layout = QHBoxLayout(content_widget)
        # content_layout.setContentsMargins(0, 0, 0, 0)

        # 2. Create an instance of the generated UI class
        ui = Ui_AnnotatorWidget()

        # 3. Set up the UI on the content widget
        ui.setupUi(content_widget)

        # Add widgets to main layout
        main_layout.addWidget(sidebar_widget)
        main_layout.addWidget(line)
        main_layout.addWidget(content_widget)

        # Create annotator instance with content_widget
        annotator = Annotator(content_widget, ui)

        # Show the main window maximized
        window.showMaximized()

        # Start the application event loop
        sys.exit(app.exec())
    except Exception as e:
        # Catch any unhandled exceptions and show a critical error message
        QMessageBox.critical(None, "Fatal Error", f"An error occurred: {str(e)}")
        sys.exit(1)
