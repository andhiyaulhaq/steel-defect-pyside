import ulid

from general_function.utils_dialog import show_warning_popup


class BoxOperations:
    def __init__(self, annotator):
        self.annotator = annotator

    def start_drawing(self, pos):
        self.annotator.start_point = pos
        self.annotator.drawing = True
        self.annotator.box_manager.selected_box_index = -1
        self.annotator.draw_boxes()

    def handle_drawing_move(self, pos):
        self.annotator.end_point = pos
        self.annotator.draw_boxes()

    def finish_drawing(self, pos):
        self.annotator.end_point = pos
        if self.annotator.start_point and self.annotator.end_point:
            x1, y1 = self.annotator.start_point
            x2, y2 = self.annotator.end_point
            x1, x2 = sorted((int(x1), int(x2)))
            y1, y2 = sorted((int(y1), int(y2)))

            if abs(x2 - x1) < 2 or abs(y2 - y1) < 2:
                show_warning_popup("Bounding box is too small. Please draw a larger box.")
            else:
                img_height, img_width = self.annotator.cv_image.shape[:2]
                # Convert to normalized center coordinates
                x_center = (x1 + x2) / (2 * img_width)
                y_center = (y1 + y2) / (2 * img_height)
                width = (x2 - x1) / img_width
                height = (y2 - y1) / img_height

                # Convert back to pixel coordinates for storage
                box_coords = self.annotator.box_manager.convert_from_normalized_center(
                    (x_center, y_center, width, height), img_width, img_height
                )

                box_id = str(ulid.new())
                self.annotator.box_manager.boxes.append((box_coords, box_id, "Anomaly"))
                self.annotator.box_manager.selected_box_index = len(self.annotator.box_manager.boxes) - 1
                self.annotator.table_manager.update_table()

        self.annotator.drawing = False
        self.annotator.start_point = None
        self.annotator.end_point = None
        self.annotator.draw_boxes()

    def start_resizing(self, index, edge):
        self.annotator.resizing = True
        self.annotator.resize_box_index = index
        self.annotator.resize_edge = edge
        self.annotator.box_manager.selected_box_index = index
        self.annotator.draw_boxes()

    def handle_resizing_move(self, pos):
        self.annotator.resize_box(pos)
        self.annotator.draw_boxes()

    def finish_resizing(self):
        self.annotator.resizing = False
        self.annotator.resize_box_index = None
        self.annotator.resize_edge = None
        self.annotator.table_manager.update_table()
        # --- Tambahan: update DB ---
        idx = self.annotator.box_manager.selected_box_index
        if 0 <= idx < len(self.annotator.box_manager.boxes):
            box, box_id, class_label = self.annotator.box_manager.boxes[idx]
            self.annotator.update_box_in_db(box_id, box, class_label)

    def start_dragging(self, index, pos):
        self.annotator.box_manager.selected_box_index = index
        self.annotator.dragging = True
        self.annotator.drag_box_index = index
        self.annotator.drag_start_pos = pos
        self.annotator.draw_boxes()

    def handle_dragging_move(self, pos):
        dx = pos[0] - self.annotator.drag_start_pos[0]
        dy = pos[1] - self.annotator.drag_start_pos[1]

        if not 0 <= self.annotator.drag_box_index < len(self.annotator.box_manager.boxes):
            return

        box, box_id, label = self.annotator.box_manager.boxes[self.annotator.drag_box_index]
        x1, y1, x2, y2 = box

        image_width = self.annotator.cv_image.shape[1] if self.annotator.cv_image is not None else 0
        image_height = self.annotator.cv_image.shape[0] if self.annotator.cv_image is not None else 0

        box_width = x2 - x1
        box_height = y2 - y1

        new_x1 = max(0, min(x1 + dx, image_width - box_width))
        new_y1 = max(0, min(y1 + dy, image_height - box_height))
        new_x2 = new_x1 + box_width
        new_y2 = new_y1 + box_height

        self.annotator.box_manager.boxes[self.annotator.drag_box_index] = ((new_x1, new_y1, new_x2, new_y2), box_id, label)
        self.annotator.drag_start_pos = pos
        self.annotator.draw_boxes()
        self.annotator.table_manager.update_table()

    def finish_dragging(self):
        self.annotator.dragging = False
        self.annotator.drag_box_index = None
        self.annotator.drag_start_pos = None
        self.annotator.table_manager.update_table()
        # --- Tambahan: update DB ---
        idx = self.annotator.box_manager.selected_box_index
        if 0 <= idx < len(self.annotator.box_manager.boxes):
            box, box_id, class_label = self.annotator.box_manager.boxes[idx]
            self.annotator.update_box_in_db(box_id, box, class_label)
