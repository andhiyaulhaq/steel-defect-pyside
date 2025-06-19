from PySide6.QtWidgets import QMessageBox


def show_warning_popup(message):
    """
    Shows a warning popup with the given message.
    :param message: The message to display in the popup.
    :return: None
    """
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText(message)
    msg.setWindowTitle("Warning")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec()
    