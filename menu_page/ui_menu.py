"""Qt UI implementation for the menu page."""

from PySide6.QtCore import QMetaObject, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QLabel,
    QLayout,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)


class UiMainWindow:
    """Main window UI class for the menu page."""

    def __init__(self):
        """Initialize UI attributes."""
        self.central_widget = None
        self.grid_layout = None
        self.horizontal_spacer = None
        self.vertical_layout = None
        self.combo_box = None
        self.logout_button = None
        self.line = None
        self.vertical_layout_2 = None
        self.vertical_spacer_2 = None
        self.title_text = None
        self.label = None
        self.vertical_spacer = None
        self.horizontal_spacer_2 = None

    def setup_ui(self, main_window):
        """Set up the user interface elements.

        Args:
            main_window: The main window instance to set up
        """
        if not main_window.objectName():
            main_window.setObjectName("MainWindow")
        main_window.resize(640, 480)

        # Setup central widget
        self.central_widget = QWidget(main_window)
        self.central_widget.setObjectName("central_widget")

        # Setup layouts
        self.grid_layout = QGridLayout(self.central_widget)
        self.grid_layout.setObjectName("grid_layout")

        self.horizontal_spacer = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )
        self.grid_layout.addItem(self.horizontal_spacer, 0, 4, 1, 1)

        # Setup vertical layout
        self.vertical_layout = QVBoxLayout()
        self.vertical_layout.setObjectName("vertical_layout")
        self.vertical_layout.setSizeConstraint(QLayout.SetFixedSize)

        # Setup combo box
        self.combo_box = QComboBox(self.central_widget)
        self.combo_box.setObjectName("combo_box")
        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.combo_box.sizePolicy().hasHeightForWidth())
        self.combo_box.setSizePolicy(size_policy)

        self.combo_box.setEditable(False)
        for item in ["Main", "Detect", "Label", "Train", "Report", "Admin"]:
            self.combo_box.addItem(item)

        self.vertical_layout.addWidget(self.combo_box, 0, Qt.AlignLeft | Qt.AlignTop)

        # Setup logout button
        self.logout_button = QPushButton(self.central_widget)
        self.logout_button.setObjectName("logout_button")
        self.logout_button.setEnabled(True)

        size_policy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(1)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(
            self.logout_button.sizePolicy().hasHeightForWidth()
        )
        self.logout_button.setSizePolicy(size_policy)

        self.vertical_layout.addWidget(
            self.logout_button, 0, Qt.AlignLeft | Qt.AlignBottom
        )
        self.grid_layout.addLayout(self.vertical_layout, 0, 0, 1, 1)

        # Setup separator line
        self.line = QFrame(self.central_widget)
        self.line.setObjectName("line")
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.grid_layout.addWidget(self.line, 0, 1, 1, 1)

        # Setup second vertical layout
        self.vertical_layout_2 = QVBoxLayout()
        self.vertical_layout_2.setObjectName("vertical_layout_2")
        self.vertical_spacer_2 = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding
        )
        self.vertical_layout_2.addItem(self.vertical_spacer_2)

        # Setup title text
        self.title_text = QLabel(self.central_widget)
        self.title_text.setObjectName("title_text")
        self.vertical_layout_2.addWidget(self.title_text, 0, Qt.AlignLeft | Qt.AlignTop)

        # Setup description label
        self.label = QLabel(self.central_widget)
        self.label.setObjectName("label")
        self.vertical_layout_2.addWidget(self.label, 0, Qt.AlignLeft | Qt.AlignTop)

        self.vertical_spacer = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding
        )
        self.vertical_layout_2.addItem(self.vertical_spacer)
        self.grid_layout.addLayout(self.vertical_layout_2, 0, 3, 1, 1)

        self.horizontal_spacer_2 = QSpacerItem(
            40, 20, QSizePolicy.Minimum, QSizePolicy.Minimum
        )
        self.grid_layout.addItem(self.horizontal_spacer_2, 0, 2, 1, 1)

        main_window.setCentralWidget(self.central_widget)
        self.retranslate_ui(main_window)
        QMetaObject.connectSlotsByName(main_window)

    def retranslate_ui(self, main_window):
        """Set up the UI text elements.

        Args:
            main_window: The main window instance to set up text for
        """
        main_window.setWindowTitle("MainWindow")
        self.logout_button.setText("LOGOUT")
        self.title_text.setText("Welcome, {username}!")
        self.label.setText("Steel Surface Defect Detection App")
