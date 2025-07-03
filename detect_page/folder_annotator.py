import csv
import os
import sys
import time

import cv2
import torch
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from ultralytics import YOLO

# Load YOLO model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "..", "weights", "training2-100-defect.pt"
)
model = YOLO(MODEL_PATH).to(device)


class ImageAnnotator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Annotator")
        self.image_label = QLabel("No image loaded")
        self.image_label.setScaledContents(True)
        self.btn_load = QPushButton("Load Folder")
        self.btn_save = QPushButton("Save Annotations")
        self.btn_save.setEnabled(False)

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.btn_load)
        layout.addWidget(self.btn_save)
        self.setLayout(layout)

        self.btn_load.clicked.connect(self.load_folder)
        self.btn_save.clicked.connect(self.save_annotations)

        self.images_info = []  # List of dicts: {img_path, detections, drawn_img}
        self.folder_path = None

    def load_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder", "")
        if not folder_path:
            return

        self.folder_path = folder_path
        self.images_info = []
        image_exts = (".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp")
        img_files = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if f.lower().endswith(image_exts)
        ]
        if not img_files:
            self.image_label.setText("No images found in folder.")
            self.btn_save.setEnabled(False)
            return

        for idx, img_path in enumerate(sorted(img_files)):
            img = cv2.imread(img_path)
            if img is None:
                continue
            img_resized = cv2.resize(img, (640, 640))
            results = model.predict(img_resized)
            detection_data = []
            for result in results:
                for box in result.boxes:
                    x0, y0, x1, y1 = map(int, box.xyxy[0].tolist())
                    class_id = int(box.cls[0])
                    class_name = model.names[class_id]
                    confidence = float(box.conf[0]) * 100

                    cv2.rectangle(img_resized, (x0, y0), (x1, y1), (0, 255, 0), 2)
                    label_text = f"{class_name} {confidence:.1f}%"
                    cv2.putText(
                        img_resized,
                        label_text,
                        (x0, y0 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (255, 0, 0),
                        1,
                    )
                    detection_data.append(
                        {
                            "class_id": class_id,
                            "class": class_name,
                            "confidence": confidence,
                            "x0": x0,
                            "y0": y0,
                            "x1": x1,
                            "y1": y1,
                        }
                    )
            self.images_info.append(
                {
                    "img_path": img_path,
                    "detections": detection_data,
                    "drawn_img": img_resized.copy(),
                }
            )
            # Display only the first image
            if idx == 0:
                img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
                h, w, ch = img_rgb.shape
                bytes_per_line = ch * w
                q_img = QImage(img_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.image_label.setPixmap(QPixmap.fromImage(q_img))

        if self.images_info:
            self.btn_save.setEnabled(True)
        else:
            self.image_label.setText("No valid images detected.")
            self.btn_save.setEnabled(False)

    def save_annotations(self):
        if not self.images_info:
            return

        screenshot_dir = "screenshots"
        os.makedirs(screenshot_dir, exist_ok=True)
        detect_output_dir = "detect_output"
        os.makedirs(detect_output_dir, exist_ok=True)
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        csv_path = os.path.join(
            detect_output_dir, f"folder_{timestamp}_annotations.csv"
        )
        write_header = not os.path.exists(csv_path)

        with open(csv_path, "a", newline="", encoding="utf-8") as csvfile:
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
            for info in self.images_info:
                base_name = os.path.splitext(os.path.basename(info["img_path"]))[0]
                img_save_path = os.path.join(
                    screenshot_dir, f"{base_name}_{timestamp}.png"
                )
                cv2.imwrite(img_save_path, info["drawn_img"])
                for det in info["detections"]:
                    class_id = det["class_id"]
                    class_name = det["class"]
                    confidence = det["confidence"]
                    x_center = (det["x0"] + det["x1"]) / 2 / 640
                    y_center = (det["y0"] + det["y1"]) / 2 / 640
                    width = (det["x1"] - det["x0"]) / 640
                    height = (det["y1"] - det["y0"]) / 640
                    writer.writerow(
                        [
                            img_save_path,
                            class_id,
                            class_name,
                            confidence,
                            x_center,
                            y_center,
                            width,
                            height,
                        ]
                    )
        print(f"[INFO] All annotations saved as {csv_path}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageAnnotator()
    window.resize(700, 700)
    window.show()
    sys.exit(app.exec())
