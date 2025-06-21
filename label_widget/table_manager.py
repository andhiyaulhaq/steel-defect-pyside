from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem

from general_function.utils_dialog import show_warning_popup


class TableManager:
    def __init__(self, annotator, table_widget: QTableWidget):
        self.annotator = annotator
        self.table_widget = table_widget
        self.table_widget.itemChanged.connect(self.handle_item_changed)
        self.table_widget.cellChanged.connect(self.on_table_cell_changed)
        self.table_widget.itemSelectionChanged.connect(self.on_table_selection_changed)

        # Reference to annotator - will be set after initialization
        self.annotator = None

    def set_annotator(self, annotator):
        """Set reference to parent annotator instance"""
        self.annotator = annotator

    def update_table(self):
        """
        Updates the QTableWidget with the current bounding box data,
        displaying normalized center coordinates.
        """
        print(f"DEBUG: update_table called, boxes = {len(self.annotator.box_manager.boxes)}")
        if self.table_widget is None or self.annotator.cv_image is None:
            return

        img_height, img_width = self.annotator.cv_image.shape[:2]

        # Temporarily save existing class labels
        existing_labels = {}
        for row in range(self.table_widget.rowCount()):
            if row < len(self.annotator.box_manager.boxes):
                item = self.table_widget.item(row, 2)  # Class label is at column 2
                if item:
                    # Assuming box_id is at column 1 and is unique for mapping
                    box_id_item = self.table_widget.item(row, 1)
                    if box_id_item:
                        existing_labels[box_id_item.text()] = item.text()

        self.table_widget.blockSignals(True)

        # We are no longer setting column headers here as they are handled in the UI file.
        # self.coordinates_table.setColumnCount(len(header_labels)) # This line is also removed.

        self.table_widget.setRowCount(len(self.annotator.box_manager.boxes))

        for row, (box, box_id, current_label) in enumerate(self.annotator.box_manager.boxes):
            # Convert to normalized center coordinates
            x_center, y_center, width, height = self.annotator.box_manager.convert_to_normalized_center(
                box, img_width, img_height
            )

            # Use existing label if available, otherwise use current_label
            label_to_use = existing_labels.get(str(box_id), current_label)

            no_item = QTableWidgetItem(str(row + 1))
            no_item.setFlags(no_item.flags() & ~Qt.ItemIsEditable)
            self.table_widget.setItem(row, 0, no_item)

            box_id_item = QTableWidgetItem(str(box_id))
            box_id_item.setFlags(box_id_item.flags() & ~Qt.ItemIsEditable)
            self.table_widget.setItem(row, 1, box_id_item)

            class_item = QTableWidgetItem(label_to_use)
            class_item.setFlags(class_item.flags() | Qt.ItemIsEditable)
            self.table_widget.setItem(row, 2, class_item)

            # Update table with normalized values, formatted to 4 decimal places
            self.table_widget.setItem(row, 3, QTableWidgetItem(f"{x_center:.4f}"))
            self.table_widget.setItem(row, 4, QTableWidgetItem(f"{y_center:.4f}"))
            self.table_widget.setItem(row, 5, QTableWidgetItem(f"{width:.4f}"))
            self.table_widget.setItem(row, 6, QTableWidgetItem(f"{height:.4f}"))

        self.table_widget.verticalHeader().setVisible(False)

        if 0 <= self.annotator.box_manager.selected_box_index < len(self.annotator.box_manager.boxes):
            self.table_widget.selectRow(self.annotator.box_manager.selected_box_index)
            table_model = self.table_widget.model()
            index_to_scroll_to = table_model.index(self.annotator.box_manager.selected_box_index, 0)
            self.table_widget.setCurrentIndex(index_to_scroll_to)
        else:
            self.table_widget.clearSelection()

        self.table_widget.blockSignals(False)

    def on_table_cell_changed(self, row, column):
        """Handles changes to cells in the coordinates table with normalized coordinates"""
        if not (0 <= row < len(self.annotator.box_manager.boxes) and column in [2, 3, 4, 5, 6]):
            return

        try:
            self.table_widget.blockSignals(True)

            if self.annotator.cv_image is None:
                return

            img_height, img_width = self.annotator.cv_image.shape[:2]
            box, box_id, current_label = self.annotator.box_manager.boxes[row]

            if column == 2:
                # Handle class label change
                new_label = self.table_widget.item(row, 2).text()
                self.annotator.box_manager.boxes[row] = (box, box_id, new_label)
            else:
                # Handle coordinate changes
                try:
                    x_center = float(self.table_widget.item(row, 3).text())
                    y_center = float(self.table_widget.item(row, 4).text())
                    width = float(self.table_widget.item(row, 5).text())
                    height = float(self.table_widget.item(row, 6).text())

                    # Clamp values between 0 and 1
                    x_center = max(0.0, min(1.0, x_center))
                    y_center = max(0.0, min(1.0, y_center))
                    width = max(0.01, min(1.0, width))
                    height = max(0.01, min(1.0, height))

                    # Convert back to pixel coordinates
                    new_box = self.annotator.box_manager.convert_from_normalized_center(
                        (x_center, y_center, width, height), img_width, img_height
                    )

                    self.annotator.box_manager.boxes[row] = (new_box, box_id, current_label)

                    # Update table with clamped values
                    self.table_widget.setItem(row, 3, QTableWidgetItem(f"{x_center:.4f}"))
                    self.table_widget.setItem(row, 4, QTableWidgetItem(f"{y_center:.4f}"))
                    self.table_widget.setItem(row, 5, QTableWidgetItem(f"{width:.4f}"))
                    self.table_widget.setItem(row, 6, QTableWidgetItem(f"{height:.4f}"))

                except ValueError:
                    show_warning_popup(
                        "Invalid input: Please enter valid numbers between 0 and 1 for coordinates."
                    )
                    self.update_table()  # Reset to previous values

            self.annotator.draw_boxes()
        finally:
            self.table_widget.blockSignals(False)

    def on_table_selection_changed(self):
        """Updates image selection when table selection changes"""
        selected_ranges = self.table_widget.selectedRanges()
        if selected_ranges:
            selected_row = selected_ranges[0].topRow()
            if 0 <= selected_row < len(self.annotator.box_manager.boxes):
                if self.annotator.box_manager.selected_box_index != selected_row:
                    self.annotator.box_manager.selected_box_index = selected_row
                    self.annotator.draw_boxes()  # <-- Perbaikan di sini
        else:
            if self.annotator.box_manager.selected_box_index != -1:
                self.annotator.box_manager.selected_box_index = -1
                self.annotator.draw_boxes()  # <-- Perbaikan di sini

    def handle_item_changed(self, item):
        row = item.row()
        col = item.column()
        if col < 2:
            return

        box_id = self.table_widget.item(row, 1).text()
        class_label = self.table_widget.item(row, 2).text()
        x_center = float(self.table_widget.item(row, 3).text())
        y_center = float(self.table_widget.item(row, 4).text())
        width = float(self.table_widget.item(row, 5).text())
        height = float(self.table_widget.item(row, 6).text())

        img_h, img_w = self.annotator.cv_image.shape[:2]
        box = self.annotator.box_manager.convert_from_normalized_center(
            (x_center, y_center, width, height), img_w, img_h
        )

        # Cek perpindahan tabel
        # Cari table_name asal dari mapping
        table_name = None
        for _id, _table in self.annotator.box_table_map:
            if str(_id) == str(box_id):
                table_name = _table
                break

        # Tentukan table tujuan
        if class_label.lower() == "anomaly":
            new_table = "anomaly"
        else:
            new_table = "defect"

        if table_name != new_table:
            # Perlu pindah tabel di DB
            from sqlalchemy import create_engine, text
            from dotenv import load_dotenv
            import os

            load_dotenv()
            DB_URL = os.getenv("DB_URL")
            if not DB_URL:
                print("DB_URL environment variable is missing!")
                return

            x_center, y_center, width, height = self.annotator.box_manager.convert_to_normalized_center(box, img_w, img_h)
            try:
                engine = create_engine(DB_URL)
                with engine.connect() as conn:
                    # Ambil nilai CL dari tabel asal
                    cl_row = conn.execute(
                        text(f"SELECT cl FROM {table_name} WHERE {table_name}_id = :box_id"),
                        {"box_id": box_id}
                    ).fetchone()
                    cl_value = cl_row[0] if cl_row else None

                    # Dapatkan class_id baru
                    class_id = conn.execute(
                        text("SELECT class_id FROM class WHERE class_name = :class_name"),
                        {"class_name": class_label}
                    ).fetchone()
                    if not class_id:
                        show_warning_popup(f"Class '{class_label}' not found in database!")
                        return
                    class_id = class_id[0]

                    # Hapus dari tabel asal
                    conn.execute(
                        text(f"DELETE FROM {table_name} WHERE {table_name}_id = :box_id"),
                        {"box_id": box_id}
                    )

                    # Insert ke tabel tujuan, gunakan id lama sebagai id baru, sertakan CL
                    result = conn.execute(
                        text(f"""
                            INSERT INTO {new_table} ({new_table}_id, class_id, image_path, xcenter, ycenter, width, height, CL)
                            VALUES (:box_id, :class_id, :image_path, :xcenter, :ycenter, :width, :height, :cl)
                        """),
                        {
                            "box_id": box_id,  # gunakan id lama
                            "class_id": class_id,
                            "image_path": self.annotator._convert_to_db_path(self.annotator.image_file_path),
                            "xcenter": x_center,
                            "ycenter": y_center,
                            "width": width,
                            "height": height,
                            "cl": cl_value
                        }
                    )
                    new_id = box_id  # id tetap sama
                    conn.commit()

                    # Update mapping box_table_map
                    for idx, (_id, _table) in enumerate(self.annotator.box_table_map):
                        if str(_id) == str(box_id):
                            self.annotator.box_table_map[idx] = (new_id, new_table)
                            break

                    # Update box_id di box_manager
                    self.annotator.box_manager.boxes[row] = (box, new_id, class_label)
            except Exception as e:
                show_warning_popup(f"DB error: {e}")
                return
        else:
            # Tidak pindah tabel, hanya update
            self.annotator.box_manager.boxes[row] = (box, box_id, class_label)
            self.annotator.update_box_in_db(box_id, box, class_label)

        self.annotator.draw_boxes()
