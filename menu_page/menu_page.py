"""
This module handles the menu page of the application.
"""

from functools import partial

from PySide6.QtWidgets import QMainWindow

from general_function.handle_logout import handle_logout
from general_function.move_page import move_page
from menu_page.ui_menu import UiMainWindow


def menu_page(self):
    """Initialize the menu page of the application."""
    window = QMainWindow()
    ui = UiMainWindow()  # Changed to PascalCase
    ui.setup_ui(window)  # Changed to snake_case

    # Add window to stack widget
    stack_widget = self.central_widget
    stack_widget.addWidget(window)
    stack_widget.setCurrentWidget(window)

    # Set username in title
    username = self.username
    text = ui.title_text.text().replace("{username}", username)
    ui.title_text.setText(text)

    # Connect signals
    ui.combo_box.currentIndexChanged.connect(partial(move_page, self, ui.combo_box))
    ui.logout_button.clicked.connect(lambda: (handle_logout, self))

    # Update window title with username
    if hasattr(self, "username"):
        text = ui.title_text.text().replace("{username}", self.username)
        ui.title_text.setText(text)
