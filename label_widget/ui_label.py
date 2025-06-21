from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)


class Ui_AnnotatorWidget(object):
    def __init__(self):
        self.fixed_width_no = 40
        self.fixed_width_box_id = 220
        self.fixed_width_class = 80
        self.fixed_width_coord = 70
        self._coordinates_table_y_offset = 70
        self._coordinates_table_width = (
            self.fixed_width_no
            + self.fixed_width_box_id
            + self.fixed_width_class
            + 4 * self.fixed_width_coord
            + 2
        )
        self._coordinates_table_height = 500

        self.openButton = None
        self.imageLabel = None
        self.coordinatesTable = None
        self.content_layout = None

    @property
    def coordinates_table_y_offset(self):
        """Returns the y-coordinate for the coordinates table."""
        return self._coordinates_table_y_offset

    @property
    def coordinates_table_width(self):
        """Returns the width of the coordinates table."""
        return self._coordinates_table_width

    @property
    def coordinates_table_height(self):
        """Returns the height of the coordinates table."""
        return self._coordinates_table_height

    def setupUi(self, annotator_widget):
        if not annotator_widget.objectName():
            annotator_widget.setObjectName("AnnotatorWidget")
        translated_title = QCoreApplication.translate(
            "AnnotatorWidget", "Image Annotator", None
        )
        annotator_widget.setWindowTitle(translated_title)

        # Create content layout only if it doesn't exist
        if self.content_layout is None:
            self.content_layout = QVBoxLayout(annotator_widget)
            self.content_layout.setContentsMargins(20, 20, 20, 20)
            self.content_layout.setSpacing(10)

        # --- Widgets Creation ---
        self._create_widgets(annotator_widget)

        # --- Layout Configuration ---
        self.content_layout.addWidget(self.openButton)
        self.content_layout.addWidget(self.imageLabel, 1)
        self.content_layout.addWidget(self.coordinatesTable)

        # --- Table Specific Configuration ---
        self._configure_coordinates_table()

        # --- Image Label Specific Configuration ---
        self._configure_image_label()

        self.retranslate_ui(annotator_widget)

        QMetaObject.connectSlotsByName(annotator_widget)

    def _create_widgets(self, annotator_widget):
        """Creates all the UI widgets."""
        self.openButton = QPushButton(annotator_widget)
        self.openButton.setObjectName("openButton")

        self.imageLabel = QLabel(annotator_widget)
        self.imageLabel.setObjectName("imageLabel")
        self.imageLabel.setFrameShape(QFrame.Box)

        self.coordinatesTable = QTableWidget(annotator_widget)
        self.coordinatesTable.setObjectName("coordinatesTable")

    def _configure_coordinates_table(self):
        """Configures the coordinates table including headers and column widths."""
        self.coordinatesTable.setColumnCount(7)
        self.coordinatesTable.setRowCount(0)

        # Set horizontal header items
        header_labels = [
            "No.",
            "Box Id",
            "Class",
            "x-center",
            "y-center",
            "width",
            "height",
        ]
        for i, label in enumerate(header_labels):
            item = QTableWidgetItem()
            self.coordinatesTable.setHorizontalHeaderItem(i, item)
            item.setText(QCoreApplication.translate("AnnotatorWidget", label, None))

        self.coordinatesTable.setColumnWidth(0, self.fixed_width_no)
        self.coordinatesTable.setColumnWidth(1, self.fixed_width_box_id)
        self.coordinatesTable.setColumnWidth(2, self.fixed_width_class)
        self.coordinatesTable.setColumnWidth(3, self.fixed_width_coord)
        self.coordinatesTable.setColumnWidth(4, self.fixed_width_coord)
        self.coordinatesTable.setColumnWidth(5, self.fixed_width_coord)
        self.coordinatesTable.setColumnWidth(6, self.fixed_width_coord)

        self.coordinatesTable.setMinimumWidth(self._coordinates_table_width)
        self.coordinatesTable.setMaximumWidth(self._coordinates_table_width)
        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.coordinatesTable.setSizePolicy(size_policy)

    def _configure_image_label(self):
        """Configures the image label's scaling and size policy."""
        # Modify the size policy to maintain aspect ratio
        self.imageLabel.setScaledContents(
            False
        )  # Change to False to prevent stretching
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        size_policy.setHeightForWidth(True)
        self.imageLabel.setSizePolicy(size_policy)
        # Set minimum size to prevent collapsing
        self.imageLabel.setMinimumSize(600, 400)

    def retranslate_ui(self, _annotator_widget):
        """Translates UI text. This function is typically auto-generated."""
        # Widget text is set here, separated from layout configuration
        self.openButton.setText(
            QCoreApplication.translate("AnnotatorWidget", "Open Image", None)
        )
