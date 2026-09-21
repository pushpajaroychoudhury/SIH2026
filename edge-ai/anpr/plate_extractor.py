"""
Automatic Number Plate Recognition.

Two-stage: a YOLOv8 model localizes plate regions, then EasyOCR reads the
text out of each cropped plate. Returns a confidence score combining both
stages so the dashboard can surface low-confidence reads for manual review
rather than silently trusting a bad OCR result.
"""

import re

import cv2
import easyocr
from ultralytics import YOLO

# Indian plate format, roughly: SS NN LL NNNN  (state code, district code,
# series letters, number) - used to sanity-check / clean OCR output.
PLATE_PATTERN = re.compile(r"^[A-Z]{2}\d{1,2}[A-Z]{0,3}\d{3,4}$")


class PlateExtractor:
    def __init__(self, model_path: str, min_confidence: float = 0.55, languages: list[str] = None):
        self.detector = YOLO(model_path)
        self.reader = easyocr.Reader(languages or ["en"], gpu=False)
        self.min_confidence = min_confidence

    def extract(self, frame, vehicle_bbox: list[float] | None = None) -> list[dict]:
        """
        Args:
            frame: BGR full frame
            vehicle_bbox: optional [x1,y1,x2,y2] to restrict plate search to
                          a single already-tracked vehicle's region
        Returns:
            list of {plate_text, ocr_confidence, detection_confidence,
                      overall_confidence, bbox, valid_format}
        """
        search_region = frame
        offset_x, offset_y = 0, 0
        if vehicle_bbox:
            x1, y1, x2, y2 = [int(v) for v in vehicle_bbox]
            x1, y1 = max(0, x1), max(0, y1)
            search_region = frame[y1:y2, x1:x2]
            offset_x, offset_y = x1, y1
            if search_region.size == 0:
                return []

        det_results = self.detector.predict(search_region, conf=0.4, verbose=False)[0]

        plates = []
        for box in det_results.boxes:
            px1, py1, px2, py2 = [int(v) for v in box.xyxy[0].tolist()]
            det_conf = float(box.conf[0])

            crop = search_region[py1:py2, px1:px2]
            if crop.size == 0:
                continue

            text, ocr_conf = self._read_plate(crop)
            if text is None:
                continue

            overall_conf = round((det_conf + ocr_conf) / 2, 3)
            if overall_conf < self.min_confidence:
                continue

            plates.append(
                {
                    "plate_text": text,
                    "detection_confidence": round(det_conf, 3),
                    "ocr_confidence": round(ocr_conf, 3),
                    "overall_confidence": overall_conf,
                    "bbox": [
                        px1 + offset_x,
                        py1 + offset_y,
                        px2 + offset_x,
                        py2 + offset_y,
                    ],
                    "valid_format": bool(PLATE_PATTERN.match(text)),
                }
            )
        return plates

    def _read_plate(self, plate_crop) -> tuple[str | None, float]:
        gray = cv2.cvtColor(plate_crop, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray, 11, 17, 17)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        ocr_results = self.reader.readtext(thresh)
        if not ocr_results:
            return None, 0.0

        # concatenate all text segments found on the plate, keep best confidence
        text = "".join(seg[1] for seg in ocr_results).upper().replace(" ", "")
        text = re.sub(r"[^A-Z0-9]", "", text)
        avg_conf = sum(seg[2] for seg in ocr_results) / len(ocr_results)

        if not text:
            return None, 0.0
        return text, avg_conf
