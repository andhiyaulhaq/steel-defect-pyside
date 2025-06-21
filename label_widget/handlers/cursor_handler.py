from PySide6.QtCore import Qt


class CursorHandler:
    @staticmethod
    def get_cursor_for_edge(edge):
        cursor_map = {
            'left': Qt.SizeHorCursor,
            'right': Qt.SizeHorCursor,
            'top': Qt.SizeVerCursor,
            'bottom': Qt.SizeVerCursor,
            'top-left': Qt.SizeFDiagCursor,
            'bottom-right': Qt.SizeFDiagCursor,
            'top-right': Qt.SizeBDiagCursor,
            'bottom-left': Qt.SizeBDiagCursor
        }
        return cursor_map.get(edge, Qt.ArrowCursor)