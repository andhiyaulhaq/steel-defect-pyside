"""
Annotator class for a Qt-based image annotation tool.
"""

import cv2
from PySide6.QtCore import QObject, QSize, Qt
from PySide6.QtWidgets import QFileDialog, QLabel, QPushButton, QTableWidget, QWidget

from general_function.utils_dialog import show_warning_popup

from .bounding_box_manager import BoundingBoxManager
from .event_handlers import AnnotatorEventHandler
from .handlers.image_handler import ImageHandler
from .table_manager import TableManager
from .ui_label import Ui_AnnotatorWidget

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from dotenv import load_dotenv
import os


class Annotator(QObject):
    """
    Annotator class for annotating images with bounding boxes.
    Handles image loading, drawing, creating, selecting, moving,
    resizing, and deleting bounding boxes.
    It also synchronizes the bounding box data with a QTableWidget.
    """

    def __init__(self, main_window: QWidget, ui: Ui_AnnotatorWidget):
        """
        Constructor for the Annotator class.
        :param main_window: The main QWidget window.
        :param ui: An instance of the generated Ui_AnnotatorWidget class.
        """
        super().__init__()

        self.main_window = main_window
        self.ui = ui
        self.image_label: QLabel = ui.imageLabel
        self.image_label.setMouseTracking(True)
        self.open_button: QPushButton = ui.openButton
        self.coordinates_table: QTableWidget = ui.coordinatesTable
        # Initialize TableManager
        self.table_manager = TableManager(self, ui.coordinatesTable)
        self.table_manager.set_annotator(self)  # Set reference to this annotator instance

        # Basic check to ensure UI elements are found
        if self.open_button is None or self.image_label is None or self.coordinates_table is None:
            print("Error: UI elements not found. Check object names in .ui file.")
            return

        # Connect UI signals to slots (event handlers)
        self.open_button.clicked.connect(self.open_image)

        # Internal state variables for image and bounding boxes
        self.cv_image = None  # Stores the original OpenCV image
        self.original_pixmap = None  # Stores the original QPixmap
        self.display_image = None  # Stores the image with drawn boxes for display
        self.drawing = False  # Flag for new box drawing mode
        self.start_point = None  # Start point for drawing a new box
        self.end_point = None  # End point for drawing a new box

        # State variables for resizing bounding boxes
        self.resizing = False
        self.resize_box_index = None
        self.resize_edge = None  # 'left', 'right', 'top', 'bottom', 'top-left', etc.
        self.edge_threshold = 10  # Pixel threshold for detecting mouse near box edge/corner

        # State variables for dragging (moving) bounding boxes
        self.dragging = False
        self.drag_start_pos = None  # Mouse position when drag started
        self.drag_box_index = None  # Index of the box being dragged

        # Variables for scaling image coordinates to actual image pixels
        self.scale_ratio = 1.0
        self.offset_x = 0
        self.offset_y = 0

        self.event_handler = AnnotatorEventHandler(self)
        self.box_manager = BoundingBoxManager()  # Initialize the bounding box manager
        self.box_table_map = []  # <-- Tambahkan ini

        # Install event filters to capture mouse and keyboard events on relevant widgets
        self.main_window.installEventFilter(self)
        self.image_label.installEventFilter(self)
        self.coordinates_table.installEventFilter(self)

        self.image_file_path = None  # Tambahkan ini

    def eventFilter(self, source, event):
        # return event_filter_impl(self, source, event)
        return self.event_handler.event_filter(source, event)

    def open_image(self):
        """
        Opens an image file selected by the user and loads it into the image label.
        Resets existing bounding boxes.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            None, "Open Image", "", "Images (*.png *.jpg *.bmp *.jpeg)"
        )
        if file_path:
            self.image_file_path = file_path  # Simpan path file di sini
            self.cv_image = cv2.imread(file_path)
            if self.cv_image is None:
                show_warning_popup(
                    "Failed to load the selected image. Please choose a valid image file."
                )
                return

            self.original_pixmap = ImageHandler.load_image(file_path)
            if self.original_pixmap is None:
                show_warning_popup(
                    "Failed to load the selected image. Please choose a valid image file."
                )
                return

            self.display_image = self.cv_image.copy()
            # --- Tambahan: Query database berdasarkan path ---
            image_path_db = self._convert_to_db_path(file_path)
            boxes_from_db = self._load_boxes_from_db(image_path_db)
            self.box_manager.boxes = boxes_from_db  # Isi dari database
            self.box_manager.selected_box_index = -1
            self._adjust_ui_layout(self.original_pixmap.size())
            self.image_label.setPixmap(self.original_pixmap)
            self.draw_boxes()
            self.table_manager.update_table()

    def _convert_to_db_path(self, file_path):
        import os
        # Ganti path ini sesuai root project Anda
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        rel_path = os.path.relpath(file_path, start=project_root)
        db_path = '/' + rel_path.replace('\\', '/')
        print(f"DEBUG: file_path={file_path}")
        print(f"DEBUG: db_path={db_path}")
        return db_path

    def _load_boxes_from_db(self, image_path_db):
        from sqlalchemy import create_engine, text
        from dotenv import load_dotenv
        import os

        load_dotenv()
        DB_URL = os.getenv("DB_URL")

        if not DB_URL:
            print("DB_URL environment variable is missing!")
            return []

        boxes = []
        self.box_table_map = []  # Reset mapping setiap load gambar baru
        try:
            engine = create_engine(DB_URL)
            with engine.connect() as conn:
                for DB_TABLE in ["anomaly", "defect"]:
                    print(f"DEBUG: Querying DB for image_path = {image_path_db} on table {DB_TABLE}")
                    result = conn.execute(
                        text(f"""
                            SELECT {DB_TABLE}_id, class_name, xcenter, ycenter, width, height
                            FROM {DB_TABLE}
                            JOIN class USING (class_id)
                            WHERE image_path = :image_path
                        """),
                        {"image_path": image_path_db}
                    )
                    rows = result.fetchall()
                    print(f"DEBUG: Rows fetched from {DB_TABLE} = {len(rows)}")
                    for row in rows:
                        anomaly_id, class_id, xcenter, ycenter, width, height = row
                        img_h, img_w = self.cv_image.shape[:2]
                        box = self.box_manager.convert_from_normalized_center(
                            (xcenter, ycenter, width, height), img_w, img_h
                        )
                        boxes.append((box, anomaly_id, str(class_id)))
                        self.box_table_map.append((anomaly_id, DB_TABLE))  # <-- Simpan mapping
        except Exception as e:
            print(f"DB error: {e}")
        return boxes

    def convert_to_db_path(self, file_path):
        import os
        rel_path = os.path.relpath(file_path, start=os.path.dirname(os.path.dirname(file_path)))
        return '/' + rel_path.replace('\\', '/')
    def _adjust_ui_layout(self, image_size: QSize):
        """
        Adjusts the size and position of the image label and coordinates table
        to fit the main window, maintaining aspect ratio.
        """
        available_width = self.main_window.width()
        available_height = self.main_window.height()

        if image_size.height() == 0: # Avoid division by zero
            return

        image_aspect = image_size.width() / image_size.height()

        # Calculate maximum image height leaving space for buttons/margins
        max_image_height = available_height - 100
        scaled_image_height = min(image_size.height(), max_image_height)
        scaled_image_width = int(scaled_image_height * image_aspect)

        # If the scaled width is too large, adjust based on available width
        if scaled_image_width > 0.7 * available_width: # Use 70% of available width for image
            scaled_image_width = int(0.7 * available_width)
            if image_aspect > 0: # Avoid division by zero
                scaled_image_height = int(scaled_image_width / image_aspect)

        # Set geometry for image label
        image_x = 20
        image_y = 70
        self.image_label.setGeometry(image_x, image_y, scaled_image_width, scaled_image_height)

    def update_display(self):
        """
        Converts the OpenCV image with drawn boxes to a QPixmap and displays it on the QLabel.
        Calculates scaling and offsets for accurate mouse event handling.
        """
        if self.display_image is None or self.original_pixmap is None:
            return

        rgb_image = cv2.cvtColor(self.display_image, cv2.COLOR_BGR2RGB)
        original_height, original_width, _ = rgb_image.shape

        label_width = self.image_label.width()
        label_height = self.image_label.height()

        if label_width > 0 and label_height > 0:
            # Calculate scale ratio to fit image within the label while maintaining aspect ratio
            scale_w = label_width / original_width
            scale_h = label_height / original_height
            self.scale_ratio = min(scale_w, scale_h)

            display_width = int(original_width * self.scale_ratio)
            display_height = int(original_height * self.scale_ratio)

            # Calculate offsets for centering the image within the label
            self.offset_x = (label_width - display_width) // 2
            self.offset_y = (label_height - display_height) // 2

            # Resize the OpenCV image for display
            resized_image = cv2.resize(
                rgb_image, (display_width, display_height), interpolation=cv2.INTER_AREA
            )
            # Convert the resized OpenCV image to QImage and then to QPixmap
            pixmap = ImageHandler.cv_to_qpixmap(resized_image)
            self.image_label.setPixmap(pixmap)
        else:
            # Handle case where label has zero dimensions (e.g., before layout is stable)
            pass

    def draw_boxes(self):
        """
        Draws all stored bounding boxes onto the display image.
        The currently selected box is highlighted with a different color and corner circles.
        """
        if self.cv_image is not None:
            self.display_image = self.box_manager.draw_boxes(
                self.cv_image,
                self.drawing,
                self.start_point,
                self.end_point
            )

            self.update_display() # Refresh the QImage in the QLabel

    def delete_box(self, index_to_delete: int):
        """
        Deletes a box at the specified index from the `self.boxes` list
        and updates the UI accordingly.
        Crucially, it correctly adjusts `self.selected_box_index` to
        maintain synchronization after deletion.
        """
        if self.box_manager.delete_box(index_to_delete):
            self.draw_boxes()
            self.table_manager.update_table()  # Update the table to reflect the deletion
            # Reset cursor to default after deletion
            self.image_label.setCursor(Qt.ArrowCursor)

    def get_box_containing(self, pos):
        """
        Returns the index of the box containing the given position (in image coordinates).
        Iterates in reverse to prioritize selecting overlapping boxes that were drawn later.
        """
        return self.box_manager.get_box_containing(pos)

    def resize_box(self, pos):
        """
        Resizes the selected bounding box based on the current mouse position and resize edge.
        Clamps coordinates to image boundaries and ensures minimum box size.
        """
        if self.box_manager.resize_box(
            pos, self.resize_box_index, self.resize_edge, self.cv_image.shape[:2]
        ):
            # If resizing was successful, redraw the boxes and update the table
            self.draw_boxes()
            self.table_manager.update_table()

    def update_box_in_db(self, box_id, box, class_label):
        # Cari table_name dari mapping
        table_name = None
        for _id, _table in self.box_table_map:
            if str(_id) == str(box_id):
                table_name = _table
                break
        if table_name is None:
            print(f"Table name for box_id {box_id} not found!")
            return

        from sqlalchemy import create_engine, text
        from dotenv import load_dotenv
        import os

        load_dotenv()
        DB_URL = os.getenv("DB_URL")
        DB_TABLE = table_name  # Gunakan table_name hasil mapping

        if not DB_URL:
            print("DB_URL environment variable is missing!")
            return

        img_h, img_w = self.cv_image.shape[:2]
        x_center, y_center, width, height = self.box_manager.convert_to_normalized_center(box, img_w, img_h)
        
        try:
            engine = create_engine(DB_URL) 
            with engine.connect() as conn:
                class_id = conn.execute(
                    text("SELECT class_id FROM class WHERE class_name = :class_name"),
                    {"class_name": class_label}
                ).fetchone()[0]
                if class_id is None:
                    print(f"Class '{class_label}' not found in database!")
                    return
                conn.execute(
                    text(f"""
                        UPDATE {DB_TABLE}
                        SET class_id = :class_id,
                            xcenter = :xcenter,
                            ycenter = :ycenter,
                            width = :width,
                            height = :height
                        WHERE {DB_TABLE}_id = :box_id
                    """),
                    {
                        "class_id": class_id,
                        "xcenter": x_center,
                        "ycenter": y_center,
                        "width": width,
                        "height": height,
                        "box_id": box_id
                    }
                )
                conn.commit()
                print(f"DEBUG: Updated box {box_id} in table {DB_TABLE}")
        except Exception as e:
            print(f"DB update error: {e}")
