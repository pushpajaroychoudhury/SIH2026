"""
Handles pushing detection/incident events from the edge device to the
backend (FastAPI ingestion service), over MQTT or HTTP.

If the device is offline, events are appended to a local JSONL buffer file
and flushed on the next successful connection - edge nodes should never
lose data just because connectivity dropped.
"""

import json
import os
import time
from datetime import datetime, timezone

from utils.logger import get_logger


class EventPublisher:
    def __init__(self, config: dict):
        self.config = config
        self.mode = config["transport"]["mode"]
        self.buffer_dir = config["output"]["local_buffer_dir"]
        os.makedirs(self.buffer_dir, exist_ok=True)
        self.buffer_path = os.path.join(self.buffer_dir, "unsent_events.jsonl")

        self.log = get_logger(
            "publisher", config["logging"]["log_dir"], config["logging"]["level"]
        )

        self._mqtt_client = None
        if self.mode == "mqtt":
            self._init_mqtt()

    # ------------------------------------------------------------------ #
    # setup
    # ------------------------------------------------------------------ #
    def _init_mqtt(self):
        import paho.mqtt.client as mqtt

        mqtt_cfg = self.config["transport"]["mqtt"]
        self._mqtt_client = mqtt.Client(client_id=self.config["device"]["id"])
        try:
            self._mqtt_client.connect(mqtt_cfg["broker_host"], mqtt_cfg["broker_port"])
            self._mqtt_client.loop_start()
            self.log.info("Connected to MQTT broker %s", mqtt_cfg["broker_host"])
        except Exception as exc:  # noqa: BLE001
            self.log.warning("MQTT connect failed (%s) - will buffer locally", exc)
            self._mqtt_client = None

    # ------------------------------------------------------------------ #
    # public API
    # ------------------------------------------------------------------ #
    def publish_detection(self, event: dict):
        self._publish(event, self.config["transport"]["mqtt"]["topic_detections"])

    def publish_incident(self, event: dict):
        self._publish(event, self.config["transport"]["mqtt"]["topic_incidents"])

    def flush_buffer(self):
        """Attempt to resend anything queued while offline."""
        if not os.path.exists(self.buffer_path):
            return
        remaining = []
        with open(self.buffer_path, "r") as f:
            lines = f.readlines()

        for line in lines:
            try:
                record = json.loads(line)
                if not self._send(record["event"], record["topic"]):
                    remaining.append(line)
            except Exception:  # noqa: BLE001
                continue

        with open(self.buffer_path, "w") as f:
            f.writelines(remaining)

        if lines:
            self.log.info(
                "Flushed offline buffer: %d sent, %d still pending",
                len(lines) - len(remaining),
                len(remaining),
            )

    # ------------------------------------------------------------------ #
    # internals
    # ------------------------------------------------------------------ #
    def _publish(self, event: dict, topic: str):
        event.setdefault("device_id", self.config["device"]["id"])
        event.setdefault("timestamp", datetime.now(timezone.utc).isoformat())

        sent = self._send(event, topic)
        if not sent:
            self._buffer(event, topic)

    def _send(self, event: dict, topic: str) -> bool:
        try:
            if self.mode == "mqtt" and self._mqtt_client:
                payload = json.dumps(event)
                result = self._mqtt_client.publish(topic, payload, qos=1)
                return result.rc == 0
            elif self.mode == "http":
                import requests

                api_key = os.environ.get(
                    self.config["transport"]["http"]["api_key_env_var"], ""
                )
                resp = requests.post(
                    self.config["transport"]["http"]["ingest_url"],
                    json=event,
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=3,
                )
                return resp.status_code < 300
        except Exception as exc:  # noqa: BLE001
            self.log.warning("Send failed (%s): %s", topic, exc)
        return False

    def _buffer(self, event: dict, topic: str):
        with open(self.buffer_path, "a") as f:
            f.write(json.dumps({"topic": topic, "event": event}) + "\n")
