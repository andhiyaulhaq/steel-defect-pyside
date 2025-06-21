"""Login page implementation and event handling for the application."""

from functools import partial

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtWidgets import QMainWindow, QMessageBox

from login_page.query import (
    auth,
    get_id_operation,
    get_user_id,
    get_role,
    log_in_session,
)
from login_page.ui_login import UiMainWindow
from menu_page.menu_page import menu_page


class LoginPage:
    """Main login page class handling login functionality."""

    def __init__(self):
        """Initialize login page attributes."""
        self.central_widget = None
        self.username = None
        self.password = None
        self.user_id = None
        self.role = None
        self.id_operation = None
        self.enter_filter = None


class EnterEventFilter(QObject):
    """Event filter for handling Enter key press events."""

    def __init__(self, parent, ui):
        """Initialize enter event filter.

        Args:
            parent: Parent widget
            ui: UI instance
        """
        super().__init__()
        self.parent = parent
        self.ui = ui

    def eventFilter(self, _obj, event):
        """Filter events to handle Enter key press.

        Args:
            obj: Object being filtered
            event: Event to filter

        Returns:
            bool: True if event handled, False otherwise
        """
        if event.type() == QEvent.KeyPress and event.key() in (
            Qt.Key_Return,
            Qt.Key_Enter,
        ):
            handle_login(self.parent, self.ui)
            return True
        return False


def setup_login_page(self):
    """Set up the login page UI and event handlers."""
    ui = UiMainWindow()
    window = QMainWindow()
    ui.setup_ui(window)
    self.central_widget.addWidget(window)
    self.central_widget.setCurrentWidget(window)

    login_button = ui.login_button
    login_button.clicked.connect(partial(handle_login, self, ui))

    # Install event filters for username and password inputs
    username_input = ui.username_input
    password_input = ui.password_input

    self.enter_filter = EnterEventFilter(self, ui)
    username_input.installEventFilter(self.enter_filter)
    password_input.installEventFilter(self.enter_filter)


def handle_login(self, ui):
    """Handle login button click and Enter key press.

    Args:
        self: Parent instance
        ui: UI instance
    """
    self.username = ui.username_input.text()
    self.password = ui.password_input.text()
    username = self.username
    password = self.password

    if username and len(username) >= 8:
        if password and len(password) >= 8:
            auth_ = auth(username, password)
            if auth_ is True:
                self.user_id = get_user_id(username)
                user_id = self.user_id
                self.role = get_role(user_id)
                log_in_session(user_id)
                self.operation_id = get_id_operation(user_id)
                menu_page(self)
            else:
                QMessageBox.warning(
                    ui.central_widget,
                    "Fail",
                    "Please enter a correct username and password.",
                )
        else:
            QMessageBox.warning(
                ui.central_widget, "Fail", "Please enter a valid password"
            )
    else:
        QMessageBox.warning(ui.central_widget, "Fail", "Please enter a valid username")
