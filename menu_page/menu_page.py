from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QPushButton, QLabel, QComboBox
import os
from functools import partial
from general_function.move_page import move_page
from general_function.handle_logout import handle_logout

def menu_page(self):
    loader = QUiLoader()
    ui_path = os.path.join(os.path.dirname(__file__), "menu_page.ui")
    ui = loader.load(ui_path)
    stack_widget = self.central_widget
    stack_widget.addWidget(ui)
    stack_widget.setCurrentWidget(ui) 

    username = self.username
    titleText = ui.findChild(QLabel, 'titleText')
    text = titleText.text().replace("{username}", username)
    titleText.setText(text) 

    page_select = ui.findChild(QComboBox, 'comboBox')
    page_select.currentIndexChanged.connect(partial(move_page, self, page_select))

    logoutButton = ui.findChild(QPushButton, 'logoutButton')
    logoutButton.clicked.connect(partial(handle_logout, self))   