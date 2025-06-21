from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, QSize, Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)


class Ui_detectWidget(object):
    def __init__(self):
        # Define widget attributes
        self.detection_image_label = None
        self.duration_label = None
        self.processing_time_label = None
        self.fps_label = None
        self.select_and_detect_video = None
        self.pause_button = None
        self.stop_button = None
        self.table_widget = None
        self.main_horizontal_layout = None
        self.left_panel_layout = None
        self.horizontal_frame = None
        self.button_layout = None

        self.fixed_width_no = 40
        self.fixed_width_box_id = 220
        self.fixed_width_class = 80
        self.fixed_width_conf = 80
        self.fixed_width_coord = 70

        self._coordinates_table_width = (
            self.fixed_width_no
            + self.fixed_width_box_id
            + self.fixed_width_class
            + self.fixed_width_conf
            + 4 * self.fixed_width_coord
            + 2
        )

        self._coordinates_table_height = 500

    def setupUi(self, detectWidget):
        if not detectWidget.objectName():
            detectWidget.setObjectName("detectWidget")
        detectWidget.resize(1000, 720)

        # --- Create and Setup Layouts ---
        self._create_layouts(detectWidget)

        # --- Create Widgets ---
        self._create_widgets(detectWidget)

        # --- Configure Widgets ---
        self._configure_widgets()

        # --- Configure Table ---
        self._configure_table()

        # --- Add Widgets to Layouts ---
        self._setup_layout_hierarchy()

        self.retranslate_ui(detectWidget)
        QMetaObject.connectSlotsByName(detectWidget)

    def _create_layouts(self, detectWidget):
        """Creates the main layouts."""
        self.main_horizontal_layout = QHBoxLayout(detectWidget)
        self.main_horizontal_layout.setObjectName("mainHorizontalLayout")

        self.left_panel_layout = QVBoxLayout()
        self.left_panel_layout.setObjectName("leftPanelLayout")

        self.horizontal_frame = QFrame(detectWidget)
        self.horizontal_frame.setObjectName("horizontalFrame")
        self.button_layout = QHBoxLayout(self.horizontal_frame)
        self.button_layout.setObjectName("horizontalLayout")

    def _create_widgets(self, detectWidget):
        """Creates all widgets."""
        # Create Image Label
        self.detection_image_label = QLabel(detectWidget)
        self.detection_image_label.setObjectName("detectionImageLabel")

        # Create Status Labels
        self.duration_label = QLabel(detectWidget)
        self.duration_label.setObjectName("label")
        self.processing_time_label = QLabel(detectWidget)
        self.processing_time_label.setObjectName("processingTimeLabel")
        self.fps_label = QLabel(detectWidget)
        self.fps_label.setObjectName("fpsLabel")

        # Create Buttons
        self.select_and_detect_video = QPushButton(self.horizontal_frame)
        self.select_and_detect_video.setObjectName("selectAndDetectVideo")
        self.pause_button = QPushButton(self.horizontal_frame)
        self.pause_button.setObjectName("pauseButton")
        self.stop_button = QPushButton(self.horizontal_frame)
        self.stop_button.setObjectName("stopButton")

        # Create Table
        self.table_widget = QTableWidget(detectWidget)
        self.table_widget.setObjectName("tableWidget")

    def _configure_widgets(self):
        """Configures widget properties."""
        # Configure Image Label
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.detection_image_label.setSizePolicy(size_policy)
        self.detection_image_label.setAlignment(Qt.AlignCenter)

        # Configure Duration Label
        self.duration_label.setMinimumSize(QSize(0, 40))
        self.duration_label.setAlignment(Qt.AlignCenter)

        # Configure Status Labels
        self.processing_time_label.setAlignment(Qt.AlignCenter)
        self.fps_label.setAlignment(Qt.AlignCenter)

        # Configure Table
        self.table_widget.setMinimumSize(QSize(320, 0))

    def _configure_table(self):
        """Configures the table widget."""
        self.table_widget.setColumnCount(8)
        header_labels = ["No.", "Box Id", "Class", "Confidence", "x-center", "y-center", "width", "height"]

        for i, label in enumerate(header_labels):
            item = QTableWidgetItem()
            self.table_widget.setHorizontalHeaderItem(i, item)
            item.setText(QCoreApplication.translate("detectWidget", label, None))

        self.table_widget.setColumnWidth(0, self.fixed_width_no)
        self.table_widget.setColumnWidth(1, self.fixed_width_box_id)
        self.table_widget.setColumnWidth(2, self.fixed_width_class)
        self.table_widget.setColumnWidth(3, self.fixed_width_conf)
        self.table_widget.setColumnWidth(4, self.fixed_width_coord)
        self.table_widget.setColumnWidth(5, self.fixed_width_coord)
        self.table_widget.setColumnWidth(6, self.fixed_width_coord)
        self.table_widget.setColumnWidth(7, self.fixed_width_coord)

    def _setup_layout_hierarchy(self):
        """Sets up the hierarchy of layouts and widgets."""
        # Add widgets to left panel
        self.left_panel_layout.addWidget(self.detection_image_label)
        self.left_panel_layout.addWidget(self.duration_label)
        self.left_panel_layout.addWidget(self.processing_time_label)
        self.left_panel_layout.addWidget(self.fps_label)

        # Add buttons to button layout
        self.button_layout.addWidget(self.select_and_detect_video)
        self.button_layout.addWidget(self.pause_button)
        self.button_layout.addWidget(self.stop_button)

        # Add button frame to left panel
        self.left_panel_layout.addWidget(self.horizontal_frame, 0, Qt.AlignHCenter)

        # Add main layouts to horizontal layout
        self.main_horizontal_layout.addLayout(self.left_panel_layout)
        self.main_horizontal_layout.addWidget(self.table_widget)

    def retranslate_ui(self, detectWidget):
        """Sets up all the UI text."""
        detectWidget.setWindowTitle(
            QCoreApplication.translate("detectWidget", "YOLO Video Viewer", None)
        )
        self.detection_image_label.setText(
            QCoreApplication.translate("detectWidget", "No video loaded", None)
        )
        self.duration_label.setText(
            QCoreApplication.translate("detectWidget", "Video Duration: 00:00", None)
        )
        self.processing_time_label.setText(
            QCoreApplication.translate("detectWidget", "Processing Time: N/A", None)
        )
        self.fps_label.setText(
            QCoreApplication.translate("detectWidget", "FPS: N/A", None)
        )
        self.select_and_detect_video.setText(
            QCoreApplication.translate("detectWidget", "Select and Detect Video", None)
        )
        self.pause_button.setText(
            QCoreApplication.translate("detectWidget", "Pause", None)
        )
        self.stop_button.setText(
            QCoreApplication.translate("detectWidget", "Stop", None)
        )
