from PySide6.QtCore import Qt

from .box_operations import BoxOperations
from .cursor_handler import CursorHandler


class MouseHandler:
    def __init__(self, annotator):
        self.annotator = annotator
        self.edge_threshold = 10
        self.box_ops = BoxOperations(annotator)
        self.cursor = CursorHandler()

    def handle_press(self, scaled_pos):
        hovered_edge, index, edge = self._check_box_edge(scaled_pos)
        if hovered_edge:
            self.box_ops.start_resizing(index, edge)
            return True

        box_index = self.annotator.get_box_containing(scaled_pos)
        if box_index != -1:
            self.box_ops.start_dragging(box_index, scaled_pos)
            return True

        self.box_ops.start_drawing(scaled_pos)
        return True

    def handle_move(self, scaled_pos):
        if self.annotator.drawing:
            self.box_ops.handle_drawing_move(scaled_pos)
        elif self.annotator.resizing:
            self.box_ops.handle_resizing_move(scaled_pos)
        elif self.annotator.dragging:
            self.box_ops.handle_dragging_move(scaled_pos)

        self._update_cursor_style(scaled_pos)
        return True

    def handle_release(self, scaled_pos):
        if self.annotator.resizing:
            self.box_ops.finish_resizing()
        elif self.annotator.dragging:
            self.box_ops.finish_dragging()
        elif self.annotator.drawing:
            self.box_ops.finish_drawing(scaled_pos)
        return True

    def _check_box_edge(self, pos):
        x, y = pos
        for i, (box, _, _) in enumerate(self.annotator.box_manager.boxes):
            x1, y1, x2, y2 = box
            edge_checks = {
                'top-left': (abs(x - x1) <= self.edge_threshold and abs(y - y1) <= self.edge_threshold),
                'top-right': (abs(x - x2) <= self.edge_threshold and abs(y - y1) <= self.edge_threshold),
                'bottom-left': (abs(x - x1) <= self.edge_threshold and abs(y - y2) <= self.edge_threshold),
                'bottom-right': (abs(x - x2) <= self.edge_threshold and abs(y - y2) <= self.edge_threshold),
                'left': (abs(x - x1) <= self.edge_threshold and y1 <= y <= y2),
                'right': (abs(x - x2) <= self.edge_threshold and y1 <= y <= y2),
                'top': (abs(y - y1) <= self.edge_threshold and x1 <= x <= x2),
                'bottom': (abs(y - y2) <= self.edge_threshold and x1 <= x <= x2)
            }

            for edge_type, condition in edge_checks.items():
                if condition:
                    return True, i, edge_type

        return False, None, None

    def _update_cursor_style(self, pos):
        hovered_edge, _, edge = self._check_box_edge(pos)
        if hovered_edge:
            cursor = self.cursor.get_cursor_for_edge(edge)
            self.annotator.image_label.setCursor(cursor)
        else:
            box_index = self.annotator.get_box_containing(pos)
            self.annotator.image_label.setCursor(
                Qt.PointingHandCursor if box_index != -1 else Qt.ArrowCursor
            )
