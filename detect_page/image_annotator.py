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
        self.btn_load = QPushButton("Load Image")
        self.btn_save = QPushButton("Save Annotation")
        self.btn_save.setEnabled(False)

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.btn_load)
        layout.addWidget(self.btn_save)
        self.setLayout(layout)

        self.btn_load.clicked.connect(self.load_image)
        self.btn_save.clicked.connect(self.save_annotation)

        self.current_image = None
        self.current_detections = []

    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image File",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff *.webp)",
        )
        if file_path:
            img = cv2.imread(file_path)
            if img is None:
                self.image_label.setText("Failed to load image.")
                self.btn_save.setEnabled(False)
                return

            img_resized = cv2.resize(img, (640, 640))
            results = model.predict(img_resized)
            detection_data = []
            for result in results:
                for box in result.boxes:
                    x0, y0, x1, y1 = map(int, box.xyxy[0].tolist())
                    class_id = int(box.cls[0])
                    class_name = model.names[class_id]
                    confidence = float(box.conf[0]) * 100

                    cv2.rectangle(
                        img_resized,
                        (x0, y0),
                        (x1, y1),
                        (0, 255, 0),
                        2,
                    )
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

            # Show image with bounding boxes
            img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
            h, w, ch = img_rgb.shape
            bytes_per_line = ch * w
            q_img = QImage(img_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.image_label.setPixmap(QPixmap.fromImage(q_img))
            self.current_image = img_resized
            self.current_detections = detection_data
            self.btn_save.setEnabled(True)
            self.loaded_file_path = file_path

    def save_annotation(self):
        if self.current_image is None or not self.current_detections:
            return

        # Save annotation in YOLO format
        base_name = os.path.splitext(os.path.basename(self.loaded_file_path))[0]
        screenshot_dir = "screenshots"
        os.makedirs(screenshot_dir, exist_ok=True)
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename_base = os.path.join(screenshot_dir, f"{base_name}_{timestamp}")

        # Save image
        image_path = f"{filename_base}.png"
        cv2.imwrite(image_path, self.current_image)
        print(f"[INFO] Image saved as {image_path}")

        # Save annotation
        txt_path = f"{filename_base}.txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            for det in self.current_detections:
                class_id = det["class_id"]
                x_center = (det["x0"] + det["x1"]) / 2 / 640
                y_center = (det["y0"] + det["y1"]) / 2 / 640
                width = (det["x1"] - det["x0"]) / 640
                height = (det["y1"] - det["y0"]) / 640
                f.write(
                    f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n"
                )
        print(f"[INFO] Annotation saved as {txt_path}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageAnnotator()
    window.resize(700, 700)
    window.show()
    sys.exit(app.exec())
