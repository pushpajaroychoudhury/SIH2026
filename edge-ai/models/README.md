# Model weights (not included)

Place the following weight files here before running `pipeline.py`:

| File | Purpose | Where to get it |
|---|---|---|
| `yolov8n.pt` | Vehicle + pedestrian detection | Auto-downloads via `ultralytics` on first run (COCO-pretrained) — no training needed |
| `pothole_yolov8n.pt` | Pothole/crack/faded-marking detection | Fine-tune YOLOv8n on a pothole dataset (e.g. RDD2022, or a custom-labeled set from your city's footage) |
| `plate_yolov8n.pt` | Number-plate localization | Fine-tune YOLOv8n on an Indian license-plate dataset (e.g. from Roboflow Universe) |

## Quick start for the vehicle/pedestrian path
`yolov8n.pt` needs no training — it's COCO-pretrained and already knows
`car`, `bus`, `truck`, `motorcycle`, `person`. You can get vehicle counting,
tracking, and pedestrian detection running immediately.

## What needs training
`pothole_yolov8n.pt` and `plate_yolov8n.pt` need your own labeled data —
there's no off-the-shelf pretrained model for these. Budget time for:
1. Collecting ~500-1000 labeled images per model (Roboflow makes labeling fast)
2. Fine-tuning: `yolo train model=yolov8n.pt data=your_dataset.yaml epochs=100`
3. Exporting the best.pt into this folder under the name config.yaml expects

Until then, `pothole_detector.py` and `plate_extractor.py` will run but
return no detections against un-fine-tuned weights.
