import cv2
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap


class ImageHandler:
    @staticmethod
    def load_image(image_path: str) -> QPixmap:
        """Optimized image loading with error handling."""
        try:
            image = cv2.imread(image_path)
            if image is None:
                return None
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            return ImageHandler.cv_to_qpixmap(image_rgb)
        except Exception as e:
            print(f"Error loading image: {e}")
            return None

    @staticmethod
    def cv_to_qpixmap(cv_img: np.ndarray) -> QPixmap:
        """Convert OpenCV image to QPixmap"""
        height, width, channel = cv_img.shape
        bytes_per_line = channel * width
        # Convert BGR to RGB
        qt_img = QImage(cv_img.data, width, height, bytes_per_line, QImage.Format_RGB888)
        return QPixmap.fromImage(qt_img)

    @staticmethod
    def resize_pixmap(pixmap, width, height, keep_aspect=True) -> QPixmap:
        """Resize QPixmap to specified dimensions"""
        if keep_aspect:
            return pixmap.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        return pixmap.scaled(width, height, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

    @staticmethod
    def qpixmap_to_cv(pixmap):
        """Convert QPixmap to OpenCV image"""
        qimage = pixmap.toImage()
        width = qimage.width()
        height = qimage.height()
        ptr = qimage.bits()
        ptr.setsize(height * width * 4)
        arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))
        return cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
