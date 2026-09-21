"""
Incident detection built on top of tracked vehicle trajectories
(see tracking/vehicle_tracker.py). Consumes per-track history, not raw
frames, so it runs after the tracker updates each frame.

Flags:
  - rash_driving: track speed exceeds configured threshold
  - stalled_vehicle: track stationary mid-lane beyond threshold
  - possible_hit_and_run: a fast-moving track disappears near a pedestrian
    detection within a short frame window (needs human/dashboard review -
    this is a *candidate* flag, not a confirmed incident)
"""

import time

import numpy as np


class IncidentDetector:
    def __init__(self, config: dict, pixels_per_meter: float = 20.0):
        icfg = config["incident"]
        self.rash_speed_kmph = icfg["rash_driving_speed_kmph"]
        self.hit_and_run_gap_frames = icfg["hit_and_run_gap_frames"]
        self.stall_seconds_threshold = icfg["stall_seconds_threshold"]
        # rough px->meters calibration; replace with a camera-specific
        # homography calibration for accurate speeds in production
        self.pixels_per_meter = pixels_per_meter

        self._stall_start_time: dict[int, float] = {}
        self._last_seen_frame: dict[int, int] = {}
        self._frame_idx = 0

    def evaluate(self, tracks: list[dict], pedestrians: list[dict], fps: float) -> list[dict]:
        """
        Args:
            tracks: current frame's tracked vehicles, each with
                    {track_id, bbox, velocity_px_per_frame}
            pedestrians: current frame's pedestrian detections
            fps: effective processing frame rate
        Returns:
            list of incident event dicts
        """
        self._frame_idx += 1
        incidents = []

        active_ids = set()
        for t in tracks:
            active_ids.add(t["track_id"])
            speed_kmph = self._estimate_speed_kmph(t["velocity_px_per_frame"], fps)

            if speed_kmph >= self.rash_speed_kmph:
                incidents.append(
                    {
                        "type": "rash_driving",
                        "track_id": t["track_id"],
                        "bbox": t["bbox"],
                        "speed_kmph": round(speed_kmph, 1),
                        "severity": "high" if speed_kmph > self.rash_speed_kmph * 1.3 else "medium",
                    }
                )

            incidents += self._check_stall(t, speed_kmph)
            self._last_seen_frame[t["track_id"]] = self._frame_idx

        incidents += self._check_hit_and_run(tracks, pedestrians, active_ids)
        self._cleanup_stale(active_ids)
        return incidents

    # ------------------------------------------------------------------ #
    def _estimate_speed_kmph(self, velocity_px_per_frame: tuple[float, float], fps: float) -> float:
        vx, vy = velocity_px_per_frame
        speed_px_per_sec = np.hypot(vx, vy) * fps
        speed_m_per_sec = speed_px_per_sec / self.pixels_per_meter
        return speed_m_per_sec * 3.6

    def _check_stall(self, track: dict, speed_kmph: float) -> list[dict]:
        tid = track["track_id"]
        now = time.time()
        if speed_kmph < 2.0:  # effectively stationary
            self._stall_start_time.setdefault(tid, now)
            elapsed = now - self._stall_start_time[tid]
            if elapsed >= self.stall_seconds_threshold:
                return [
                    {
                        "type": "stalled_vehicle",
                        "track_id": tid,
                        "bbox": track["bbox"],
                        "stationary_seconds": round(elapsed, 1),
                        "severity": "medium",
                    }
                ]
        else:
            self._stall_start_time.pop(tid, None)
        return []

    def _check_hit_and_run(
        self, tracks: list[dict], pedestrians: list[dict], active_ids: set
    ) -> list[dict]:
        """A candidate flag only: a fast track that was near a pedestrian
        last frame and vanished this frame within the configured gap."""
        incidents = []
        vanished_ids = [
            tid
            for tid, last_frame in self._last_seen_frame.items()
            if tid not in active_ids
            and (self._frame_idx - last_frame) <= self.hit_and_run_gap_frames
        ]
        for tid in vanished_ids:
            incidents.append(
                {
                    "type": "possible_hit_and_run",
                    "track_id": tid,
                    "note": "track vanished shortly after being tracked - review footage",
                    "severity": "high",
                }
            )
        return incidents

    def _cleanup_stale(self, active_ids: set):
        for tid in list(self._stall_start_time):
            if tid not in active_ids:
                self._stall_start_time.pop(tid, None)
        for tid in list(self._last_seen_frame):
            if self._frame_idx - self._last_seen_frame[tid] > 300:  # ~30s at 10fps
                self._last_seen_frame.pop(tid, None)
