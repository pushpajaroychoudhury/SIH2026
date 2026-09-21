"""
Main entry point for a single edge node. Reads a video stream, runs every
detector, tracks vehicles, extracts plates, evaluates incidents, geotags
everything, and publishes to the backend.

Run:
    python pipeline.py --config config.yaml
"""

import argparse
import time

import cv2
import yaml

from detectors.incident_detector import IncidentDetector
from detectors.pedestrian_detector import PedestrianDetector
from detectors.pothole_detector import PotholeDetector
from detectors.vehicle_detector import VehicleDetector
from detectors.waterlogging_detector import WaterloggingDetector
from anpr.plate_extractor import PlateExtractor
from tracking.vehicle_tracker import VehicleTracker
from geotag import GeoTagger
from utils.logger import get_logger
from utils.publisher import EventPublisher


class EdgePipeline:
    def __init__(self, config_path: str):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        self.log = get_logger(
            "pipeline", self.config["logging"]["log_dir"], self.config["logging"]["level"]
        )

        m = self.config["models"]
        conf = m["confidence_threshold"]
        device = m["device"]

        self.log.info("Loading models on device=%s ...", device)
        self.pothole_detector = PotholeDetector(m["pothole_defect"], conf, device)
        self.vehicle_detector = VehicleDetector(m["vehicle"], conf, device)
        self.pedestrian_detector = PedestrianDetector(m["pedestrian"], conf, device)
        self.waterlogging_detector = WaterloggingDetector(
            self.config["waterlogging"]["reflectivity_threshold"],
            self.config["waterlogging"]["min_region_area_px"],
        )
        self.plate_extractor = PlateExtractor(
            m["anpr_detector"],
            self.config["anpr"]["min_confidence"],
            self.config["anpr"]["languages"],
        )
        self.tracker = VehicleTracker(self.config)
        self.incident_detector = IncidentDetector(self.config)
        self.geotagger = GeoTagger(self.config)
        self.publisher = EventPublisher(self.config)
        self.log.info("All models loaded.")

    def run(self):
        src = self.config["video_source"]
        cap = cv2.VideoCapture(src["uri"])
        if not cap.isOpened():
            self.log.error("Could not open video source: %s", src["uri"])
            return

        source_fps = cap.get(cv2.CAP_PROP_FPS) or 25
        frame_interval = max(1, int(source_fps / src["target_fps"]))
        frame_idx = 0

        self.log.info(
            "Pipeline started. source_fps=%.1f, sampling every %d frames",
            source_fps,
            frame_interval,
        )

        try:
            while True:
                ok, frame = cap.read()
                if not ok:
                    self.log.warning("Stream ended or dropped - attempting reconnect in 5s")
                    time.sleep(5)
                    cap.release()
                    cap = cv2.VideoCapture(src["uri"])
                    continue

                frame_idx += 1
                if frame_idx % frame_interval != 0:
                    continue

                frame = cv2.resize(frame, (src["frame_width"], src["frame_height"]))
                self._process_frame(frame)
                self.publisher.flush_buffer()

        except KeyboardInterrupt:
            self.log.info("Shutdown requested.")
        finally:
            cap.release()

    def _process_frame(self, frame):
        potholes = self.pothole_detector.detect(frame)
        vehicles = self.vehicle_detector.detect_vehicles(frame)
        infra = self.vehicle_detector.detect_infrastructure(frame)
        pedestrians = self.pedestrian_detector.detect(frame)
        waterlogging = self.waterlogging_detector.detect(frame)

        crossing_zones = [i["bbox"] for i in infra if i["label"] == "pedestrian_crossing"]
        at_risk_pedestrians = self.pedestrian_detector.flag_at_risk(pedestrians, crossing_zones)

        tracks = self.tracker.update(frame, vehicles)

        plates = []
        for track in tracks:
            plates += self.plate_extractor.extract(frame, track["bbox"])

        incidents = self.incident_detector.evaluate(
            tracks, pedestrians, fps=self.config["video_source"]["target_fps"]
        )

        # -- assemble + publish detection event -------------------------
        detection_event = self.geotagger.tag(
            {
                "potholes": potholes,
                "vehicle_count": self.vehicle_detector.count_by_type(vehicles),
                "infrastructure": infra,
                "waterlogging": waterlogging,
                "pedestrians_at_risk": at_risk_pedestrians,
                "tracked_vehicles": [
                    {"track_id": t["track_id"], "label": t["label"], "bbox": t["bbox"]}
                    for t in tracks
                ],
                "plates": plates,
            }
        )
        self.publisher.publish_detection(detection_event)

        for incident in incidents:
            incident_event = self.geotagger.tag(incident)
            self.publisher.publish_incident(incident_event)
            self.log.info(
                "INCIDENT: %s (track %s, severity %s)",
                incident["type"],
                incident.get("track_id"),
                incident.get("severity"),
            )

        if potholes or waterlogging:
            self.log.info(
                "Frame flags: %d pothole(s), %d waterlogging region(s)",
                len(potholes),
                len(waterlogging),
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SIH26124 Edge AI pipeline")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    args = parser.parse_args()

    EdgePipeline(args.config).run()
