import csv
import datetime
import os
import sys
import time

import cv2
import torch
import ulid

# from dotenv import load_dotenv
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

# Tambahan untuk database
# from sqlalchemy import create_engine
from ultralytics import YOLO

from detect_page.ui_detect_box import Ui_detectWidget

# Set the device to GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"[INFO] Using device: {device}")

# Load the YOLO model using os.path for portability
ANOMALY_MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "..", "weights", "training1-anomaly.pt"
)
DEFECT_MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "..", "weights", "training1-defect.pt"
)
anomaly_model = YOLO(ANOMALY_MODEL_PATH).to(device)
defect_model = YOLO(DEFECT_MODEL_PATH).to(device)

# Inisialisasi database
# load_dotenv()
# DATABASE_URL = os.getenv("DB_URL")
# engine = create_engine(DATABASE_URL)


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

        # Connect new buttons
        self.ui.select_video_button.clicked.connect(self.select_video)
        self.ui.start_detection_button.clicked.connect(self.start_detection)
        self.ui.pause_button.clicked.connect(self.pause_video)
        self.ui.stop_button.clicked.connect(self.stop_video)

        # Disable start_detection_button initially
        self.ui.start_detection_button.setEnabled(False)
        self.selected_video_path = None

        # Initialize other attributes
        self.last_saved_fps = 0

        self.fps_log_path = None
        self.annotation_csv_path = None
        self.last_screenshot_time = None
        self.first_screenshot_taken = False

        self.screenshot_taken = False  # <-- Add this line

    def select_video(self):
        """Open a file dialog to select a video file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video File",
            "",
            "Video Files (*.mp4 *.avi *.mov *.mkv *.wmv)",
        )
        if file_path:
            self.selected_video_path = file_path
            self.ui.start_detection_button.setEnabled(True)
            self.ui.detection_image_label.setText(
                f"Selected: {os.path.basename(file_path)}"
            )
        else:
            self.selected_video_path = None
            self.ui.start_detection_button.setEnabled(False)
            self.ui.detection_image_label.setText("No video loaded")

    def start_detection(self):
        """Start processing the selected video."""
        if not self.selected_video_path:
            return
        file_path = self.selected_video_path
        self.video_capture = cv2.VideoCapture(file_path)
        self.frame_rate = self.video_capture.get(cv2.CAP_PROP_FPS)
        self.frame_duration = 1.0 / self.frame_rate if self.frame_rate > 0 else 0.033
        self.is_playing = True
        self.start_time = time.time()
        self.ui.detection_image_label.setText("Processing video...")
        self.last_frame_display = None
        self.last_detections = []
        self.timer.start(max(1, int(self.frame_duration * 1000)))

        # --- Create unique fps_history file in history folder ---
        history_dir = "history"
        os.makedirs(history_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        self.fps_log_path = os.path.join(history_dir, f"{base_name}_{timestamp}.csv")
        with open(self.fps_log_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["time", "fps", "status"])  # Add status column
        # -------------------------------------------------------

        # --- Create annotation CSV path for this video ---
        detect_output_dir = "detect_output"
        os.makedirs(detect_output_dir, exist_ok=True)
        self.annotation_csv_path = os.path.join(
            detect_output_dir, f"{base_name}_{timestamp}_annotations.csv"
        )
        # -------------------------------------------------------
        self.last_screenshot_time = None
        self.first_screenshot_taken = False

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
        results = anomaly_model.predict(frame_yolo, verbose=False)

        # Extract detection_data from results
        detection_data = []
        if results and hasattr(results[0], "boxes"):
            for box in results[0].boxes:
                x0, y0, x1, y1 = map(int, box.xyxy[0].tolist())
                class_id = int(box.cls[0])
                class_name = anomaly_model.names[class_id]
                confidence = float(box.conf[0]) * 100
                detection_data.append(
                    {
                        "x0": x0,
                        "y0": y0,
                        "x1": x1,
                        "y1": y1,
                        "class_id": class_id,
                        "class": class_name,
                        "confidence": confidence,
                    }
                )

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

        # Draw bounding boxes for anomaly detections on frame_display (for UI only)
        for det in detection_data:
            x0 = int(det["x0"] * scale_x)
            y0 = int(det["y0"] * scale_y)
            x1 = int(det["x1"] * scale_x)
            y1 = int(det["y1"] * scale_y)
            color = (0, 255, 0)  # Green for anomaly
            cv2.rectangle(frame_display, (x0, y0), (x1, y1), color, 2)
            label = f"{det['class']} {det['confidence']:.1f}%"
            cv2.putText(
                frame_display,
                label,
                (x0, max(y0 - 10, 0)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2,
                cv2.LINE_AA,
            )

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

        # --- Simplified screenshot logic based on time ---
        self.screenshot_taken = False  # <-- Always reset at the start of each frame
        if not self.first_screenshot_taken:
            if elapsed_time >= 4.96:
                self.save_screenshot(
                    frame_display_clean, detection_data, anomaly_total_time=total_time
                )
                self.last_screenshot_time = elapsed_time
                self.first_screenshot_taken = True
                self.screenshot_taken = True
        else:
            if (
                self.last_screenshot_time is not None
                and elapsed_time - self.last_screenshot_time >= 4.9  # cpu1-n
                # and elapsed_time - self.last_screenshot_time >= 4.875 # cpu1-s
            ):
                self.save_screenshot(
                    frame_display_clean, detection_data, anomaly_total_time=total_time
                )
                self.last_screenshot_time = elapsed_time
                self.screenshot_taken = True
        # --- End of simplified screenshot logic ---

        self.last_frame_display = frame_display.copy()
        self.last_detections = detection_data.copy()

        self.update_detection_table(detection_data)

        # --- Modified block to log FPS history ---
        with open(self.fps_log_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [elapsed_time, f"{fps:.2f}", "yes" if self.screenshot_taken else "no"]
            )
        # --- End of modified FPS logging block ---

        # Display frame
        frame_rgb = cv2.cvtColor(frame_display, cv2.COLOR_BGR2RGB)
        h, w, _ch = frame_rgb.shape  # Get channels
        bytes_per_line = frame_rgb.strides[0]  # Use strides for robustness
        q_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.ui.detection_image_label.setPixmap(pixmap)

        # --- Add this block to update the label after the first frame is displayed ---
        if self.ui.detection_image_label.text() == "Processing video...":
            self.ui.detection_image_label.setText("")
        # ------------------------------------------------------------------------------

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

    def save_screenshot(self, frame, detections, anomaly_total_time=None):
        """Save the current frame (with bounding boxes) and its annotation to a CSV file."""
        screenshot_dir = "screenshots"
        os.makedirs(screenshot_dir, exist_ok=True)
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename_base = os.path.join(screenshot_dir, f"{timestamp}")

        # Draw bounding boxes on a copy of the frame
        frame_with_boxes = frame.copy()
        for det in detections:
            x0 = int(det["x0"] * frame_with_boxes.shape[1] / 640)
            y0 = int(det["y0"] * frame_with_boxes.shape[0] / 640)
            x1 = int(det["x1"] * frame_with_boxes.shape[1] / 640)
            y1 = int(det["y1"] * frame_with_boxes.shape[0] / 640)
            color = (0, 255, 0)  # Green for anomaly
            cv2.rectangle(frame_with_boxes, (x0, y0), (x1, y1), color, 2)
            label = f"{det['class']} {det['confidence']:.1f}%"
            cv2.putText(
                frame_with_boxes,
                label,
                (x0, max(y0 - 10, 0)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2,
                cv2.LINE_AA,
            )

        # Save image with bounding boxes
        image_path = f"{filename_base}.png"
        cv2.imwrite(image_path, frame_with_boxes)
        print(f"[INFO] Screenshot saved as {image_path}")

        # Use the annotation CSV path set at video start
        csv_filename = getattr(self, "annotation_csv_path", None)
        if not csv_filename:
            # fallback for safety
            detect_output_dir = "detect_output"
            os.makedirs(detect_output_dir, exist_ok=True)
            csv_filename = os.path.join(
                detect_output_dir, f"screenshot_{timestamp}_annotations.csv"
            )

        # FIX: Define frame_yolo before using it
        frame_yolo = cv2.resize(frame, (640, 640))

        # Run defect model on the screenshot frame (resize to 640x640 for YOLO)
        start_defect = time.time()
        defect_results = defect_model.predict(frame_yolo)
        end_defect = time.time()
        defect_time = (end_defect - start_defect) * 1000  # ms

        # Calculate combined FPS if anomaly_total_time is provided
        if anomaly_total_time is not None:
            combined_total_time = anomaly_total_time + defect_time
            combined_fps = (
                1000.0 / combined_total_time if combined_total_time > 0 else 0
            )
            self.ui.fps_label.setText(f"Combined FPS: {combined_fps:.2f}")
            self.ui.processing_time_label.setText(
                f"Combined Time: {combined_total_time:.1f} ms"
            )

        # Prepare combined detections: anomaly (from argument) + defect (from model)
        combined_detections = []

        # Add anomaly detections (from argument)
        for det in detections:
            class_id = det["class_id"]
            class_name = det["class"]
            confidence = det["confidence"]
            x_center = (det["x0"] + det["x1"]) / 2 / 640
            y_center = (det["y0"] + det["y1"]) / 2 / 640
            width = (det["x1"] - det["x0"]) / 640
            height = (det["y1"] - det["y0"]) / 640
            combined_detections.append(
                [
                    image_path,
                    class_id,
                    class_name,
                    confidence,
                    x_center,
                    y_center,
                    width,
                    height,
                ]
            )

        # Add defect detections (from model)
        for result in defect_results:
            for box in result.boxes:
                x0, y0, x1, y1 = map(int, box.xyxy[0].tolist())
                class_id = int(box.cls[0]) + 1  # Shift defect class_id by 1
                class_name = defect_model.names[
                    class_id - 1
                ]  # Use original index for name
                confidence = float(box.conf[0]) * 100
                x_center = (x0 + x1) / 2 / 640
                y_center = (y0 + y1) / 2 / 640
                width = (x1 - x0) / 640
                height = (y1 - y0) / 640
                combined_detections.append(
                    [
                        image_path,
                        class_id,
                        class_name,
                        confidence,
                        x_center,
                        y_center,
                        width,
                        height,
                    ]
                )

        # Write header if file does not exist
        write_header = not os.path.exists(csv_filename)
        with open(csv_filename, "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            if write_header:
                writer.writerow(
                    [
                        "image_path",
                        "class_id",
                        "class",
                        "confidence",
                        "x_center",
                        "y_center",
                        "width",
                        "height",
                    ]
                )
            for row in combined_detections:
                writer.writerow(row)
        print(f"[INFO] Annotation saved to {csv_filename}")


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        widget = VideoDetectionWidget()
        widget.showMaximized()
        sys.exit(app.exec())
    except Exception as e:
        import traceback

        print("=== ERROR SAAT STARTUP ===")
        print(e)
        traceback.print_exc()
        input("Tekan ENTER untuk keluar...")
