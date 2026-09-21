"""
Waterlogging detection.

No labeled dataset needed for a first version: standing water on asphalt
has a distinctive visual signature - a large, flat, highly reflective
region (sky/streetlight reflections) with low texture variance, sitting
in the lower half of the frame (road surface). This heuristic pipeline
flags candidate regions; swap in a trained segmentation model
(e.g. a U-Net on a flood-segmentation dataset) later for higher precision.
"""

import cv2
import numpy as np


class WaterloggingDetector:
    def __init__(self, reflectivity_threshold: float = 0.62, min_region_area_px: int = 4000):
        self.reflectivity_threshold = reflectivity_threshold
        self.min_region_area_px = min_region_area_px

    def detect(self, frame) -> list[dict]:
        h, w = frame.shape[:2]
        road_region = frame[h // 2 :, :]  # assume road occupies lower half

        gray = cv2.cvtColor(road_region, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(road_region, cv2.COLOR_BGR2HSV)

        # Reflective/wet surfaces: high value (brightness), low saturation
        value_channel = hsv[:, :, 2].astype(np.float32) / 255.0
        sat_channel = hsv[:, :, 1].astype(np.float32) / 255.0
        reflectivity_map = value_channel * (1 - sat_channel)

        # Low local texture variance = smooth/flat = candidate water surface
        blurred = cv2.GaussianBlur(gray, (15, 15), 0)
        texture_variance = cv2.Laplacian(blurred, cv2.CV_64F)
        texture_variance = np.abs(texture_variance)
        low_texture_mask = (texture_variance < texture_variance.mean() * 0.5).astype(np.uint8)

        candidate_mask = (
            (reflectivity_map > self.reflectivity_threshold).astype(np.uint8) & low_texture_mask
        ) * 255

        contours, _ = cv2.findContours(
            candidate_mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        detections = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < self.min_region_area_px:
                continue
            x, y, bw, bh = cv2.boundingRect(cnt)
            # offset y back into full-frame coordinates
            y_full = y + h // 2
            confidence = min(0.95, 0.5 + (area / (w * h)) * 2)
            detections.append(
                {
                    "label": "waterlogging",
                    "confidence": round(confidence, 3),
                    "bbox": [x, y_full, x + bw, y_full + bh],
                    "area_px": int(area),
                }
            )
        return detections
