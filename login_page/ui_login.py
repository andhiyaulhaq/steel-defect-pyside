"""UI implementation for the login page of the application."""

from menu_page.menu_page import menu_page
from PySide6.QtCore import QCoreApplication, QEvent, QMetaObject, QObject, Qt
from PySide6.QtWidgets import (
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from .query import auth, get_id_operation, get_id_user, get_role, log_in_session


class EnterEventFilter(QObject):
    """Event filter for handling Enter key press events."""

    def __init__(self, parent, ui):
        """Initialize EnterEventFilter.

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
            self.ui.handle_login(self.parent)
            return True
        return False


class UiMainWindow:
    """Main window UI class for the login page."""

    def __init__(self):
        """Initialize UI attributes."""
        self.central_widget = None
        self.vertical_layout = None
        self.vertical_spacer = None
        self.title_text = None
        self.vertical_spacer_3 = None
        self.username_text = None
        self.username_input = None
        self.password_label = None
        self.password_input = None
        self.vertical_spacer_4 = None
        self.login_button = None
        self.vertical_spacer_2 = None
        self.enter_filter = None

    def setup_ui(self, main_window):
        """Set up the UI elements.

        Args:
            main_window: Main window instance
        """
        if not main_window.objectName():
            main_window.setObjectName("MainWindow")
        main_window.resize(667, 416)

        self.central_widget = QWidget(main_window)
        self.central_widget.setObjectName("centralwidget")

        self.vertical_layout = QVBoxLayout(self.central_widget)
        self.vertical_layout.setObjectName("verticalLayout")

        self.vertical_spacer = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed
        )
        self.vertical_layout.addItem(self.vertical_spacer)

        self.title_text = QLabel(self.central_widget)
        self.title_text.setObjectName("titleText")
        self.vertical_layout.addWidget(
            self.title_text, 0, Qt.AlignmentFlag.AlignHCenter
        )

        self.vertical_spacer_3 = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed
        )
        self.vertical_layout.addItem(self.vertical_spacer_3)

        self.username_text = QLabel(self.central_widget)
        self.username_text.setObjectName("usernameText")
        self.vertical_layout.addWidget(
            self.username_text, 0, Qt.AlignmentFlag.AlignHCenter
        )

        self.username_input = QLineEdit(self.central_widget)
        self.username_input.setObjectName("usernameInput")
        self.vertical_layout.addWidget(
            self.username_input, 0, Qt.AlignmentFlag.AlignHCenter
        )

        self.password_label = QLabel(self.central_widget)
        self.password_label.setObjectName("label")
        self.vertical_layout.addWidget(
            self.password_label, 0, Qt.AlignmentFlag.AlignHCenter
        )

        self.password_input = QLineEdit(self.central_widget)
        self.password_input.setObjectName("passwordInput")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.vertical_layout.addWidget(
            self.password_input, 0, Qt.AlignmentFlag.AlignHCenter
        )

        self.vertical_spacer_4 = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed
        )
        self.vertical_layout.addItem(self.vertical_spacer_4)

        self.login_button = QPushButton(self.central_widget)
        self.login_button.setObjectName("loginButton")
        self.vertical_layout.addWidget(
            self.login_button,
            0,
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom,
        )

        self.vertical_spacer_2 = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )
        self.vertical_layout.addItem(self.vertical_spacer_2)

        main_window.setCentralWidget(self.central_widget)

        self.retranslate_ui(main_window)
        QMetaObject.connectSlotsByName(main_window)

    def retranslate_ui(self, main_window):
        """Set up text translations for UI elements.

        Args:
            main_window: Main window instance
        """
        main_window.setWindowTitle(
            QCoreApplication.translate("MainWindow", "MainWindow", None)
        )
        self.title_text.setText(
            QCoreApplication.translate("MainWindow", "Login Page", None)
        )
        self.username_text.setText(
            QCoreApplication.translate("MainWindow", "Username", None)
        )
        self.password_label.setText(
            QCoreApplication.translate("MainWindow", "Password", None)
        )
        self.login_button.setText(
            QCoreApplication.translate("MainWindow", "LOGIN", None)
        )

    def setup_login_page(self, parent, window):
        """Set up login page with event handlers.

        Args:
            parent: Parent widget
            window: Window instance
        """
        self.setup_ui(window)

        # Setup login button
        self.login_button.clicked.connect(lambda: self.handle_login(parent))

        # Setup enter key event filters
        self.enter_filter = EnterEventFilter(parent, self)
        self.username_input.installEventFilter(self.enter_filter)
        self.password_input.installEventFilter(self.enter_filter)

    def handle_login(self, parent):
        """Handle login button click and Enter key press.

        Args:
            parent: Parent widget
        """
        username = self.username_input.text()
        password = self.password_input.text()

        if username and len(username) >= 8:
            if password and len(password) >= 8:
                auth_ = auth(username, password)
                if auth_ is True:
                    parent.username = username
                    parent.password = password
                    parent.id_user = get_id_user(username)
                    parent.role = get_role(parent.id_user)
                    log_in_session(parent.id_user)
                    parent.id_operation = get_id_operation(parent.id_user)
                    menu_page(parent)
                else:
                    QMessageBox.warning(
                        self.central_widget,
                        "Fail",
                        "Please enter a correct username and password.",
                    )
            else:
                QMessageBox.warning(
                    self.central_widget, "Fail", "Please enter a valid password"
                )
        else:
            QMessageBox.warning(
                self.central_widget, "Fail", "Please enter a valid username"
            )
