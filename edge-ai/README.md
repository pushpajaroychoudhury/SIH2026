# SIH26124 — Edge AI Module

Runs on each roadside camera / bus-mounted camera. Pulls a video stream,
runs all detection models on sampled frames, tracks vehicles across frames,
evaluates incidents, geotags everything, and pushes structured JSON events
to the backend over MQTT (or HTTP as a fallback).

## Folder contents

```
edge-ai/
├── config.yaml              # per-device settings (camera URI, GPS, thresholds)
├── requirements.txt
├── pipeline.py               # entry point — run this
├── geotag.py
├── detectors/
│   ├── pothole_detector.py       # potholes, cracks, faded markings
│   ├── vehicle_detector.py       # vehicle counting + infra (dividers/crossings/signs)
│   ├── waterlogging_detector.py  # heuristic, no training data needed
│   ├── pedestrian_detector.py    # pedestrian + at-risk/jaywalking flag
│   └── incident_detector.py      # rash driving, stalls, possible hit-and-run
├── tracking/
│   └── vehicle_tracker.py        # DeepSORT-based multi-object tracking
├── anpr/
│   └── plate_extractor.py        # plate localization + OCR + confidence scoring
├── utils/
│   ├── publisher.py               # MQTT/HTTP push with offline buffering
│   └── logger.py
└── models/                        # put trained weights here (see models/README.md)
```

## Setup

```bash
cd edge-ai
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

Edit `config.yaml`:
- `video_source.uri` — RTSP URL of the camera, or a video file path for local testing
- `device.latitude` / `device.longitude` / `device.location_name` — for static cameras
- `transport.mode` — `mqtt` (for the live dashboard) or `http` (simpler for a demo)

## Run

```bash
python pipeline.py --config config.yaml
```

For a quick local demo without a real camera, point `video_source.uri` at
any `.mp4` file of road/traffic footage.

## What each frame produces

One **detection event** (potholes, vehicle counts, infrastructure,
waterlogging, at-risk pedestrians, tracked vehicle positions, ANPR reads)
published to `sih26124/detections`, plus zero or more **incident events**
(rash driving / stalled vehicle / possible hit-and-run) published to
`sih26124/incidents` — both timestamped and geotagged, ready for the
FastAPI ingestion service to write into MongoDB and the dashboard to render
on the live map.

## Known gaps to fill before a real deployment
1. **Pothole and ANPR models are untrained placeholders** — see `models/README.md`.
2. **Speed estimation uses a rough pixel-to-meter guess** (`pixels_per_meter` in
   `incident_detector.py`) — needs a real camera calibration (homography from
   known reference points in the frame) for accurate rash-driving detection.
3. **Waterlogging is a heuristic**, not a trained model — good enough for a
   working demo; a segmentation model trained on flood imagery gets more precise.
4. **Live GPS for bus-mounted cameras** is stubbed in `geotag.py` (`_read_live_gps`)
   — wire up your GPS module's serial output for the fleet-monitoring use case.
