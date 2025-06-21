from PySide6.QtCore import QCoreApplication, QMetaObject, QRect
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
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
        annotator_widget.resize(800, 600)
        translated_title = QCoreApplication.translate(
            "AnnotatorWidget",
            "Image Annotator",
            None
        )
        annotator_widget.setWindowTitle(translated_title)

        # --- Widgets Creation ---
        self._create_widgets(annotator_widget)

        # --- Layout and Geometry Configuration ---
        self._configure_layout_and_geometry()

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

    def _configure_layout_and_geometry(self):
        """Sets the geometry for each widget."""
        self.openButton.setGeometry(QRect(20, 20, 100, 30))
        self.imageLabel.setGeometry(QRect(20, 70, 500, 500))
        # Note: The table geometry is set to a larger width to better accommodate 7 columns
        # Increased width for better visibility
        self.coordinatesTable.setGeometry(QRect(540, 70, self.coordinates_table_width, self.coordinates_table_height))

    def _configure_coordinates_table(self):
        """Configures the coordinates table including headers and column widths."""
        self.coordinatesTable.setColumnCount(7)
        self.coordinatesTable.setRowCount(0) # Start with 0 rows, rows will be added dynamically

        # Set horizontal header items
        header_labels = ["No.", "Box Id", "Class", "x-center", "y-center", "width", "height"]
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

        # Make horizontal header interactive and resizable
        # header = self.coordinatesTable.horizontalHeader()
        # header.setSectionsMovable(True)
        # header.setSectionsClickable(True)
        # header.setStretchLastSection(False)
        # header.setSectionResizeMode(QHeaderView.Interactive)

    def _configure_image_label(self):
        """Configures the image label's scaling and size policy."""
        self.imageLabel.setScaledContents(True)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

    def retranslate_ui(self, _annotator_widget):
        """Translates UI text. This function is typically auto-generated."""
        # Widget text is set here, separated from layout configuration
        self.openButton.setText(QCoreApplication.translate("AnnotatorWidget", "Open Image", None))
