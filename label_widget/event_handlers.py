"""
Event handler class for mouse and keyboard interactions in the image annotation tool.
"""

from PySide6.QtCore import QEvent, QObject, Qt

# from .handlers.box_operations import BoxOperations
# from .handlers.cursor_handler import CursorHandler
from .handlers.mouse_handler import MouseHandler


class AnnotatorEventHandler(QObject):
    def __init__(self, annotator):
        super().__init__()
        self.annotator = annotator
        self.mouse_handler = MouseHandler(annotator)

    def event_filter(self, source, event: QEvent):
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Delete:
            return self._handle_delete_key(source)

        if source is self.annotator.image_label and self.annotator.cv_image is not None:
            if event.type() in (QEvent.MouseMove, QEvent.MouseButtonPress, QEvent.MouseButtonRelease):
                return self._handle_mouse_event_on_image_label(event)

        if source == self.annotator.main_window and event.type() == QEvent.Type.Resize:
            return self._handle_window_resize()

        return False

    def _handle_delete_key(self, source):
        idx_to_delete = -1
        
        if source is self.annotator.coordinates_table:
            current_row = self.annotator.coordinates_table.currentRow()
            if current_row != -1:
                idx_to_delete = current_row
        elif source in (self.annotator.image_label, self.annotator.main_window):
            if self.annotator.box_manager.selected_box_index != -1:
                idx_to_delete = self.annotator.box_manager.selected_box_index

        if idx_to_delete != -1:
            self.annotator.delete_box(idx_to_delete)
            return True
        return False

    def _handle_mouse_event_on_image_label(self, event):
        scaled_pos = self._get_scaled_position(event)
        
        if event.type() == QEvent.MouseMove:
            return self.mouse_handler.handle_move(scaled_pos)
        elif event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
            return self.mouse_handler.handle_press(scaled_pos)
        elif event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
            return self.mouse_handler.handle_release(scaled_pos)
        return False

    def _get_scaled_position(self, event):
        pos = event.position()
        x = int((pos.x() - self.annotator.offset_x) / self.annotator.scale_ratio)
        y = int((pos.y() - self.annotator.offset_y) / self.annotator.scale_ratio)
        
        if self.annotator.cv_image is not None:
            x = max(0, min(x, self.annotator.cv_image.shape[1] - 1))
            y = max(0, min(y, self.annotator.cv_image.shape[0] - 1))
        
        return (x, y)

    def _handle_window_resize(self):
        current_size = self.annotator.main_window.size()
        table_width = self.annotator.ui.coordinates_table_width
        table_height = self.annotator.ui.coordinates_table_height
        table_x = current_size.width() - table_width - 20
        table_y = self.annotator.ui.coordinates_table_y_offset
        self.annotator.coordinates_table.setGeometry(table_x, table_y, table_width, table_height)
        return True