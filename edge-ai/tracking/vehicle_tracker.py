"""
Multi-object tracking for vehicles, using deep-sort-realtime (a maintained
pip package wrapping DeepSORT). Gives each vehicle a stable track_id across
frames so we can compute speed, direction, dwell time, and feed the
incident detector and ANPR module with consistent per-vehicle identities.
"""

from deep_sort_realtime.deepsort_tracker import DeepSort


class VehicleTracker:
    def __init__(self, config: dict):
        tcfg = config["tracking"]
        self.tracker = DeepSort(
            max_age=tcfg["max_age"],
            n_init=tcfg["n_init"],
            max_cosine_distance=tcfg["max_cosine_distance"],
        )
        self._prev_centers: dict[int, tuple[float, float]] = {}

    def update(self, frame, detections: list[dict]) -> list[dict]:
        """
        Args:
            frame: current BGR frame (deep-sort-realtime uses this for its
                   embedder to re-identify vehicles across brief occlusions)
            detections: vehicle detections from VehicleDetector.detect_vehicles(),
                        each {label, confidence, bbox: [x1,y1,x2,y2]}
        Returns:
            list of {track_id, label, bbox, velocity_px_per_frame}
        """
        ds_input = [
            ([d["bbox"][0], d["bbox"][1], d["bbox"][2] - d["bbox"][0], d["bbox"][3] - d["bbox"][1]],
             d["confidence"], d["label"])
            for d in detections
        ]

        tracks = self.tracker.update_tracks(ds_input, frame=frame)

        results = []
        for track in tracks:
            if not track.is_confirmed():
                continue

            track_id = int(track.track_id)
            x1, y1, x2, y2 = track.to_ltrb()
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2

            prev_cx, prev_cy = self._prev_centers.get(track_id, (cx, cy))
            velocity = (cx - prev_cx, cy - prev_cy)
            self._prev_centers[track_id] = (cx, cy)

            results.append(
                {
                    "track_id": track_id,
                    "label": track.get_det_class() or "vehicle",
                    "bbox": [round(v, 1) for v in (x1, y1, x2, y2)],
                    "velocity_px_per_frame": velocity,
                }
            )

        # drop centers for tracks that disappeared to avoid unbounded growth
        live_ids = {r["track_id"] for r in results}
        for stale_id in list(self._prev_centers):
            if stale_id not in live_ids:
                self._prev_centers.pop(stale_id, None)

        return results
