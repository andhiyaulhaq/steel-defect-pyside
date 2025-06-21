import os
import sys
import time

import cv2
import torch
import ulid
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QLayout,
    QMainWindow,
    QPushButton,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from ultralytics import YOLO
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

from detect_page.ui_detect import Ui_detectWidget

# Set the device to GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"[INFO] Using device: {device}")

# Load the YOLO model
model = YOLO("../weights/weight-merged.pt").to(device)

load_dotenv()
DATABASE_URL = os.getenv("DB_URL")
engine = create_engine(DATABASE_URL)


class VideoDetectionWidget(QMainWindow):
    """
    A widget for video detection using YOLO model.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main grid layout
        main_layout = QGridLayout(central_widget)

        # Create left sidebar
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setSizeConstraint(QLayout.SetFixedSize)

        # Add combo box to sidebar
        self.combo_box = QComboBox()
        self.combo_box.addItems(["Main", "Detect", "Label", "Train", "Report", "Admin"])
        self.combo_box.setCurrentText("Detect")
        sidebar_layout.addWidget(self.combo_box, 0, Qt.AlignLeft | Qt.AlignTop)

        # Add logout button to sidebar
        self.logout_button = QPushButton("LOGOUT")
        sidebar_layout.addWidget(self.logout_button, 0, Qt.AlignLeft | Qt.AlignBottom)

        # Add sidebar to main layout
        main_layout.addLayout(sidebar_layout, 0, 0, 1, 1)

        # Add vertical line separator
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line, 0, 1, 1, 1)

        # Create widget for detection content
        detection_widget = QWidget()
        self.ui = Ui_detectWidget()
        self.ui.setupUi(detection_widget)

        # Add detection widget to main layout
        main_layout.addWidget(detection_widget, 0, 2, 1, 1)

        # Initialize other attributes
        self.video_capture = None
        self.is_playing = False
        self.start_time = 0
        self.frame_rate = 0
        self.frame_duration = 0
        self.last_frame_display = None
        self.last_detections = []

        # Set up timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.process_video)

        # Connect buttons
        self.ui.select_and_detect_video.clicked.connect(self.open_and_detect_video)
        self.ui.pause_button.clicked.connect(self.pause_video)
        self.ui.stop_button.clicked.connect(self.stop_video)

        self.capture_state = "wait_defect_center"
        self.capture_delay_until = 0
        self.last_saved_fps = 0
        self.defect_first_seen_time = None
        self.defect_first_seen_x0 = None

    def open_and_detect_video(self):
        """Open a video file and start processing it."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video File",
            "",
            "Video Files (*.mp4 *.avi *.mov *.mkv *.wmv)",
        )
        if file_path:
            self.video_capture = cv2.VideoCapture(file_path)
            self.frame_rate = self.video_capture.get(cv2.CAP_PROP_FPS)
            self.frame_duration = (
                1.0 / self.frame_rate if self.frame_rate > 0 else 0.033
            )
            self.is_playing = True
            self.start_time = time.time()
            self.ui.detection_image_label.setText("Processing video...")
            self.last_frame_display = None
            self.last_detections = []
            self.timer.start(max(1, int(self.frame_duration * 1000)))

    def process_video(self):
        """Process the video frame by frame."""
        if self.video_capture is None or not self.is_playing:
            self.timer.stop()
            return

        elapsed_time = time.time() - self.start_time
        expected_frame_index = int(elapsed_time / self.frame_duration)
        current_frame_index = self.video_capture.get(cv2.CAP_PROP_POS_FRAMES)
        if expected_frame_index > current_frame_index:
            self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, expected_frame_index)

        ret, frame = self.video_capture.read()
        if not ret:
            self.video_capture.release()
            self.video_capture = None
            self.is_playing = False
            self.timer.stop()

            minutes = int(elapsed_time // 60)
            seconds = int(elapsed_time % 60)
            self.ui.duration_label.setText(
                f"Video Duration: {minutes:02d}:{seconds:02d}"
            )

            if self.last_frame_display is not None:
                frame_rgb = cv2.cvtColor(self.last_frame_display, cv2.COLOR_BGR2RGB)
                h, w, _ch = frame_rgb.shape  # Get channels
                bytes_per_line = frame_rgb.strides[0]  # Use strides for robustness
                q_image = QImage(
                    frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888
                )
                pixmap = QPixmap.fromImage(q_image)
                self.ui.detection_image_label.setPixmap(pixmap)
                self.update_detection_table(self.last_detections)
            return

        frame_yolo = cv2.resize(frame, (640, 640))
        results = model.predict(frame_yolo)

        frame_display = cv2.resize(
            frame,
            (
                self.ui.detection_image_label.width(),
                self.ui.detection_image_label.height(),
            ),
        )
        scale_x = frame_display.shape[1] / 640
        scale_y = frame_display.shape[0] / 640

        # Add this line to keep the clean frame for screenshot
        frame_display_clean = frame_display.copy()

        # Extract speed information from the first result
        if results and hasattr(results[0], "speed"):
            speed = results[0].speed
            total_time = speed["preprocess"] + speed["inference"] + speed["postprocess"]
            fps = 1000.0 / total_time if total_time > 0 else 0
            self.ui.processing_time_label.setText(
                f"Processing Time: {total_time:.1f} ms"
            )
            self.ui.fps_label.setText(f"FPS: {fps:.2f}")
        else:
            self.ui.processing_time_label.setText("Processing Time: N/A")
            self.ui.fps_label.setText("FPS: N/A")
            fps = 0

        detection_data = []
        for result in results:
            for box in result.boxes:
                x0, y0, x1, y1 = map(int, box.xyxy[0].tolist())
                class_id = int(box.cls[0])
                class_name = model.names[class_id]
                confidence = float(box.conf[0]) * 100

                x0_display = int(x0 * scale_x)
                y0_display = int(y0 * scale_y)
                x1_display = int(x1 * scale_x)
                y1_display = int(y1 * scale_y)

                cv2.rectangle(
                    frame_display,
                    (x0_display, y0_display),
                    (x1_display, y1_display),
                    (0, 255, 0),
                    2,
                )
                label_text = f"{class_name} {confidence:.1f}%"
                cv2.putText(
                    frame_display,
                    label_text,
                    (x0_display, y0_display - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 0, 0),
                    1,
                )

                detection_data.append(
                    {
                        "class_id": class_id,  # tambahkan ini
                        "class": class_name,
                        "confidence": confidence,
                        "x0": x0,
                        "y0": y0,
                        "x1": x1,
                        "y1": y1,
                    }
                )

        self.last_frame_display = frame_display.copy()
        self.last_detections = detection_data.copy()

        self.update_detection_table(detection_data)

        # Screenshot logic with custom delay
        img_w = self.ui.detection_image_label.width()
        center_x = img_w // 2
        center_threshold = img_w * 0.05  # 5% of width

        defect = min(detection_data, key=lambda d: d["x0"]) if detection_data else None

        now = time.time()
        if self.capture_state == "wait_defect_center":
            if defect is not None:
                x_center = int((defect["x0"] + defect["x1"]) / 2 * scale_x)
                if self.defect_first_seen_time is None:
                    self.defect_first_seen_time = now
                if abs(x_center - center_x) < center_threshold:
                    time_to_center = now - self.defect_first_seen_time
                    delay_duration = 2 * time_to_center
                    self.save_screenshot(frame_display_clean, detection_data)
                    self.capture_delay_until = now + delay_duration
                    self.capture_state = "wait_delay"
                    self.defect_first_seen_time = None
            else:
                self.defect_first_seen_time = None

        elif self.capture_state == "wait_delay":
            if now >= self.capture_delay_until:
                if defect:
                    self.save_screenshot(frame_display_clean, detection_data)
                    self.capture_state = "wait_defect_center"
                else:
                    self.capture_state = "wait_defect_center"

        # Display frame
        frame_rgb = cv2.cvtColor(frame_display, cv2.COLOR_BGR2RGB)
        h, w, _ch = frame_rgb.shape  # Get channels
        bytes_per_line = frame_rgb.strides[0]  # Use strides for robustness
        q_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.ui.detection_image_label.setPixmap(pixmap)

        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        self.ui.duration_label.setText(f"Video Duration: {minutes:02d}:{seconds:02d}")

    def update_detection_table(self, detections):
        """Update the detection table with new detections."""
        self.ui.table_widget.clearContents()
        if not detections:
            self.ui.table_widget.setRowCount(0)
        else:
            for det in detections:
                det["x_center"] = (det["x0"] + det["x1"]) / (2 * 640)
                det["y_center"] = (det["y0"] + det["y1"]) / (2 * 640)
                det["width"] = (det["x1"] - det["x0"]) / 640
                det["height"] = (det["y1"] - det["y0"]) / 640

            sorted_detections = sorted(detections, key=lambda det: det["x_center"])

            self.ui.table_widget.setRowCount(len(sorted_detections))
            for row, det in enumerate(sorted_detections):
                box_id = str(ulid.new())

                self.ui.table_widget.setItem(row, 0, QTableWidgetItem(str(row + 1)))
                self.ui.table_widget.setItem(row, 1, QTableWidgetItem(box_id))
                self.ui.table_widget.setItem(row, 2, QTableWidgetItem(det["class"]))
                self.ui.table_widget.setItem(
                    row, 3, QTableWidgetItem(f"{det['confidence']:.2f}%")
                )
                self.ui.table_widget.setItem(
                    row, 4, QTableWidgetItem(f"{det['x_center']:.5f}")
                )
                self.ui.table_widget.setItem(
                    row, 5, QTableWidgetItem(f"{det['y_center']:.5f}")
                )
                self.ui.table_widget.setItem(
                    row, 6, QTableWidgetItem(f"{det['width']:.5f}")
                )
                self.ui.table_widget.setItem(
                    row, 7, QTableWidgetItem(f"{det['height']:.5f}")
                )

        self.ui.table_widget.resizeRowsToContents()
        self.ui.table_widget.verticalHeader().setVisible(False)

    def stop_video(self):
        """Stop the video playback and reset the UI."""
        self.is_playing = False
        if self.video_capture:
            self.video_capture.release()
            self.video_capture = None
        self.timer.stop()

        if self.last_frame_display is not None:
            # FIX THIS PART:
            frame_rgb = cv2.cvtColor(self.last_frame_display, cv2.COLOR_BGR2RGB)
            h, w, _ch = frame_rgb.shape  # Get channels
            bytes_per_line = frame_rgb.strides[0]  # Use strides for robustness
            q_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            self.ui.detection_image_label.setPixmap(pixmap)
            self.update_detection_table(self.last_detections)

        self.ui.duration_label.setText("Video Stopped")
        self.ui.pause_button.setText("Pause")

    def pause_video(self):
        """Pause or resume the video playback."""
        if self.is_playing:
            self.is_playing = False
            self.ui.pause_button.setText("Resume")
        else:
            if self.video_capture and self.video_capture.isOpened():
                self.is_playing = True
                self.ui.pause_button.setText("Pause")
                self.start_time = (
                    time.time()
                    - self.video_capture.get(cv2.CAP_PROP_POS_FRAMES)
                    * self.frame_duration
                )
                self.timer.start(max(1, int(self.frame_duration * 1000)))

    def save_screenshot(self, frame, detections):
        """Save the current frame (without bounding boxes) and its annotation, and insert to DB."""
        screenshot_dir = "screenshots"
        os.makedirs(screenshot_dir, exist_ok=True)
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename_base = os.path.join(screenshot_dir, f"{timestamp}")

        # Save image
        image_path = f"{filename_base}.png"
        cv2.imwrite(image_path, frame)
        print(f"[INFO] Screenshot saved as {image_path}")

        # Ubah image_path untuk DB
        db_image_path = f"/steel-defect-pyside/screenshots/{os.path.basename(image_path)}"

        # Simpan langsung ke database tanpa membuat file .txt
        with engine.begin() as conn:
            for det in detections:
                class_id = det["class_id"]
                class_name = det["class"]
                confidence = det["confidence"]
                x_center = (det["x0"] + det["x1"]) / 2 / 640
                y_center = (det["y0"] + det["y1"]) / 2 / 640
                width = (det["x1"] - det["x0"]) / 640
                height = (det["y1"] - det["y0"]) / 640

                # Tentukan tabel tujuan
                if class_name.lower() == "dents":
                    class_name = "Dent"
                    table = "defect"
                elif class_name.lower() == "anomaly":
                    table = "anomaly"
                else:
                    continue  # skip jika bukan defect/anomaly

                # Generate ULID untuk primary key
                box_id = str(ulid.new())

                # Insert ke tabel
                query = text(f"""
                    INSERT INTO {table} 
                    ({table}_id, class_id, image_path, xcenter, ycenter, width, height, cl)
                    VALUES
                    (:box_id, :class_id, :image_path, :xcenter, :ycenter, :width, :height, :cl)
                """)
                conn.execute(query, {
                    "box_id": box_id,
                    "class_id": class_id,
                    "image_path": db_image_path,
                    "xcenter": x_center,
                    "ycenter": y_center,
                    "width": width,
                    "height": height,
                    "cl": confidence / 100.0
                })
        print(f"[INFO] Annotation disimpan ke database dengan image_path {db_image_path}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = VideoDetectionWidget()
    widget.showMaximized()
    sys.exit(app.exec())
