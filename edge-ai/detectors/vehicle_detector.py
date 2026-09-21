"""
Vehicle detection + counting, and static infrastructure elements
(dividers, pedestrian crossings, signage) using a single YOLOv8 pass.

Uses stock COCO classes for vehicles (works out of the box). Infrastructure
classes (divider/crossing/sign) need a small fine-tuned head appended, or a
second lightweight model - kept as a separate optional model path so the
vehicle path works immediately with off-the-shelf weights.
"""

from ultralytics import YOLO

# COCO class ids relevant to traffic
VEHICLE_COCO_CLASSES = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
}

INFRA_CLASSES = {
    0: "divider",
    1: "pedestrian_crossing",
    2: "traffic_sign",
    3: "traffic_signal",
}


class VehicleDetector:
    def __init__(
        self,
        vehicle_model_path: str,
        confidence_threshold: float = 0.45,
        device: str = "cpu",
        infra_model_path: str | None = None,
    ):
        self.vehicle_model = YOLO(vehicle_model_path)
        self.infra_model = YOLO(infra_model_path) if infra_model_path else None
        self.conf_threshold = confidence_threshold
        self.device = device

    def detect_vehicles(self, frame) -> list[dict]:
        results = self.vehicle_model.predict(
            frame,
            conf=self.conf_threshold,
            device=self.device,
            classes=list(VEHICLE_COCO_CLASSES.keys()),
            verbose=False,
        )[0]

        detections = []
        for box in results.boxes:
            cls_id = int(box.cls[0])
            detections.append(
                {
                    "label": VEHICLE_COCO_CLASSES.get(cls_id, f"class_{cls_id}"),
                    "confidence": round(float(box.conf[0]), 3),
                    "bbox": [round(v, 1) for v in box.xyxy[0].tolist()],
                }
            )
        return detections

    def count_by_type(self, detections: list[dict]) -> dict:
        counts = {v: 0 for v in VEHICLE_COCO_CLASSES.values()}
        for d in detections:
            counts[d["label"]] = counts.get(d["label"], 0) + 1
        counts["total"] = len(detections)
        return counts

    def detect_infrastructure(self, frame) -> list[dict]:
        if self.infra_model is None:
            return []
        results = self.infra_model.predict(
            frame, conf=self.conf_threshold, device=self.device, verbose=False
        )[0]
        detections = []
        for box in results.boxes:
            cls_id = int(box.cls[0])
            detections.append(
                {
                    "label": INFRA_CLASSES.get(cls_id, f"class_{cls_id}"),
                    "confidence": round(float(box.conf[0]), 3),
                    "bbox": [round(v, 1) for v in box.xyxy[0].tolist()],
                }
            )
        return detections
