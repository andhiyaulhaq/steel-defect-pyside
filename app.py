"""Main application entry point for the PySide6 application."""

from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget

from login_page.login_page import setup_login_page


class MainWindow(QMainWindow):
    """Main window class for the application."""

    def __init__(self):
        super().__init__()
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        # Tambahkan halaman login
        setup_login_page(self)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.showMaximized()
    app.exec()
