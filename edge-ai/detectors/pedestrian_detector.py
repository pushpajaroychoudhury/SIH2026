"""
Pedestrian detection for the safety module. Reuses the general-purpose
YOLOv8 model filtered to COCO's 'person' class, and flags pedestrians
found outside marked crossing zones as at-risk.
"""

from ultralytics import YOLO

PERSON_CLASS_ID = 0


class PedestrianDetector:
    def __init__(self, model_path: str, confidence_threshold: float = 0.45, device: str = "cpu"):
        self.model = YOLO(model_path)
        self.conf_threshold = confidence_threshold
        self.device = device

    def detect(self, frame) -> list[dict]:
        results = self.model.predict(
            frame,
            conf=self.conf_threshold,
            device=self.device,
            classes=[PERSON_CLASS_ID],
            verbose=False,
        )[0]

        detections = []
        for box in results.boxes:
            detections.append(
                {
                    "label": "pedestrian",
                    "confidence": round(float(box.conf[0]), 3),
                    "bbox": [round(v, 1) for v in box.xyxy[0].tolist()],
                }
            )
        return detections

    def flag_at_risk(self, pedestrians: list[dict], crossing_zones: list[list[float]]) -> list[dict]:
        """
        crossing_zones: list of [x1,y1,x2,y2] boxes marking legal crossing areas
        (from VehicleDetector.detect_infrastructure -> 'pedestrian_crossing').
        A pedestrian whose bbox center falls outside every crossing zone,
        while standing in the carriageway, is flagged as at-risk jaywalking.
        """
        flagged = []
        for p in pedestrians:
            cx = (p["bbox"][0] + p["bbox"][2]) / 2
            cy = (p["bbox"][1] + p["bbox"][3]) / 2
            inside_any_zone = any(
                zx1 <= cx <= zx2 and zy1 <= cy <= zy2 for zx1, zy1, zx2, zy2 in crossing_zones
            )
            if not inside_any_zone:
                flagged.append({**p, "risk": "outside_marked_crossing"})
        return flagged
