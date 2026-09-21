"""
Attaches GPS coordinates to a detection event.

Static-camera edge nodes just stamp the fixed device location from config.
Bus-mounted / mobile nodes should instead read live coordinates off a GPS
receiver (e.g. a USB/serial NMEA module) - swap `get_coordinates()`'s body
for that when deploying on the fleet-monitoring buses.
"""

from datetime import datetime, timezone


class GeoTagger:
    def __init__(self, config: dict):
        self.device_cfg = config["device"]
        self.mobile = False          # set True for bus-mounted nodes
        self._gps_serial = None      # placeholder for a live GPS handle

    def get_coordinates(self) -> tuple[float, float]:
        if self.mobile and self._gps_serial:
            return self._read_live_gps()
        # static node: fixed install location from config.yaml
        return self.device_cfg["latitude"], self.device_cfg["longitude"]

    def tag(self, event: dict) -> dict:
        lat, lon = self.get_coordinates()
        event["location"] = {
            "lat": lat,
            "lon": lon,
            "name": self.device_cfg["location_name"],
            "route_id": self.device_cfg.get("route_id"),
        }
        event.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
        return event

    def _read_live_gps(self) -> tuple[float, float]:
        # TODO: parse NMEA sentences from self._gps_serial (e.g. via pynmea2)
        # for bus-mounted fleet-monitoring cameras.
        raise NotImplementedError("Live GPS not wired up yet - static fallback in use")
