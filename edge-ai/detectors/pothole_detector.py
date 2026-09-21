"""
Detects road surface defects: potholes, cracks, faded lane markings.

Uses a YOLOv8 model fine-tuned on a pothole dataset (e.g. RDD2022 / a
custom-labeled set). Swap `models/pothole_yolov8n.pt` for your trained
weights - a COCO-pretrained model has no notion of "pothole".
"""

from ultralytics import YOLO

DEFECT_CLASSES = {
    0: "pothole",
    1: "crack",
    2: "faded_marking",
}


class PotholeDetector:
    def __init__(self, model_path: str, confidence_threshold: float = 0.45, device: str = "cpu"):
        self.model = YOLO(model_path)
        self.conf_threshold = confidence_threshold
        self.device = device

    def detect(self, frame) -> list[dict]:
        """
        Args:
            frame: BGR numpy array (single video frame)
        Returns:
            list of {label, confidence, bbox: [x1,y1,x2,y2]}
        """
        results = self.model.predict(
            frame, conf=self.conf_threshold, device=self.device, verbose=False
        )[0]

        detections = []
        for box in results.boxes:
            cls_id = int(box.cls[0])
            label = DEFECT_CLASSES.get(cls_id, f"class_{cls_id}")
            detections.append(
                {
                    "label": label,
                    "confidence": round(float(box.conf[0]), 3),
                    "bbox": [round(v, 1) for v in box.xyxy[0].tolist()],
                }
            )
        return detections
