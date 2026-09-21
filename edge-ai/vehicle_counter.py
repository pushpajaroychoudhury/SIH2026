"""
Vehicle counting v3 - fixes double-counting caused by tracker ID switches.

The problem v2 had: DeepSort gives each vehicle a track ID, but if a
vehicle is briefly occluded, exits/re-enters frame, or has a couple of
missed detections, the tracker can "lose" it and assign a NEW ID when it
reappears. Since counting is keyed by ID, that looked like a second car.

Two fixes:
  1. `max_age` raised (tracker waits longer before giving up on a track,
     so brief gaps don't cause a hard loss).
  2. A re-identification safety net: whenever a track ID appears for the
     FIRST time, check whether a same-type vehicle recently "went missing"
     nearby. If so, treat it as the same physical vehicle - don't count it
     again, and don't let it double up in future frames either.

Usage:
    python vehicle_counter.py --video traffic.mp4
    python vehicle_counter.py --video traffic.mp4 --conf 0.25
    python vehicle_counter.py --video traffic.mp4 --reid-distance-px 150
    python vehicle_counter.py                       # webcam

Press "q" to quit early. Full summary prints when the video ends or you quit.
"""

import argparse
import math

import cv2
import requests
from deep_sort_realtime.deepsort_tracker import DeepSort
from ultralytics import YOLO

VEHICLE_CLASSES = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}


def _send_to_backend(backend_url: str, label: str):
    """Fire-and-forget POST to the bridge backend. Never crashes the
    counter if the backend isn't running - it just skips that update."""
    if not backend_url:
        return
    try:
        requests.post(
            f"{backend_url}/api/edge/vehicle-count",
            json={"label": label, "count": 1},
            timeout=1,
        )
    except requests.exceptions.RequestException:
        pass  # backend not reachable - counting still works locally


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", default=0, help="Path to a video file, or omit to use the webcam")
    parser.add_argument(
        "--line-y-pct", type=float, default=0.5,
        help="Counting line position as a fraction of frame height (0-1).",
    )
    parser.add_argument(
        "--conf", type=float, default=0.25,
        help="Detection confidence threshold (0-1).",
    )
    parser.add_argument(
        "--reid-distance-px", type=float, default=120,
        help="How close (pixels) a reappearing vehicle must be to a recently-lost one to be treated as the same vehicle.",
    )
    parser.add_argument(
        "--reid-window-frames", type=int, default=45,
        help="How many frames back to still consider a lost vehicle 'recent' for re-identification.",
    )
    parser.add_argument("--no-display", action="store_true")
    parser.add_argument(
        "--backend-url", default="http://localhost:8000",
        help="Bridge backend URL to send live counts to. Pass '' to disable.",
    )
    args = parser.parse_args()

    print("Loading YOLOv8n...")
    model = YOLO("yolov8n.pt")
    # max_age raised from 20 -> 40: tracker tolerates ~1.5x longer gaps
    # before declaring a track lost, which is the main cause of ID switches.
    tracker = DeepSort(max_age=40, n_init=2)

    source = args.video if args.video != 0 else 0
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print(f"Could not open video source: {source}")
        return

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 480
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 640
    line_y = int(frame_height * args.line_y_pct)

    print(f"Video: {frame_width}x{frame_height}, {total_frames} frames")
    print(f"Re-ID: within {args.reid_distance_px}px and {args.reid_window_frames} frames of going missing")
    print("-" * 60)

    counts_by_type = {v: 0 for v in VEHICLE_CLASSES.values()}
    line_crossing_counts = {v: 0 for v in VEHICLE_CLASSES.values()}
    counted_crossing_ids = set()
    prev_side = {}

    seen_track_ids = set()          # track IDs we've already made a counting decision for
    active_last_frame = {}          # track_id -> (cx, cy, label) as of the previous frame
    lost_tracks = []                # list of {label, cx, cy, frame_lost} - candidates for re-ID

    frame_idx = 0
    frames_with_zero_detections = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame_idx += 1

        results = model.predict(
            frame, conf=args.conf, classes=list(VEHICLE_CLASSES.keys()), verbose=False
        )[0]

        raw_count = len(results.boxes)
        if raw_count == 0:
            frames_with_zero_detections += 1
        if frame_idx % 30 == 0 or frame_idx == 1:
            print(f"  frame {frame_idx}/{total_frames}: {raw_count} raw detection(s), "
                  f"{len(counts_by_type)} type(s) tracked so far")

        detections = []
        for box in results.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            detections.append(([x1, y1, x2 - x1, y2 - y1], conf, VEHICLE_CLASSES[cls_id]))

        tracks = tracker.update_tracks(detections, frame=frame)
        confirmed_ids_this_frame = set()

        if not args.no_display:
            cv2.line(frame, (0, line_y), (frame.shape[1], line_y), (0, 255, 255), 2)

        for track in tracks:
            if not track.is_confirmed():
                continue

            track_id = track.track_id
            label = track.get_det_class() or "vehicle"
            x1, y1, x2, y2 = [int(v) for v in track.to_ltrb()]
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            confirmed_ids_this_frame.add(track_id)

            # --- counting decision, made ONCE per track_id, the first time we see it ---
            if track_id not in seen_track_ids:
                seen_track_ids.add(track_id)
                match_idx = _find_reid_match(lost_tracks, label, cx, cy, frame_idx, args)
                if match_idx is not None:
                    # same physical vehicle reappearing under a new ID - don't recount
                    lost_tracks.pop(match_idx)
                else:
                    counts_by_type[label] = counts_by_type.get(label, 0) + 1
                    _send_to_backend(args.backend_url, label)

            active_last_frame[track_id] = (cx, cy, label)

            # --- line crossing (unaffected logic, still guarded per track_id) ---
            side = "below" if cy > line_y else "above"
            if track_id in prev_side and prev_side[track_id] != side and track_id not in counted_crossing_ids:
                line_crossing_counts[label] = line_crossing_counts.get(label, 0) + 1
                counted_crossing_ids.add(track_id)
            prev_side[track_id] = side

            if not args.no_display:
                color = (0, 255, 0) if track_id in counted_crossing_ids else (0, 200, 255)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(
                    frame, f"{label} #{track_id}", (x1, max(y1 - 8, 0)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2,
                )

        # any track that was active last frame but isn't confirmed this frame -> "lost"
        for track_id, (cx, cy, label) in active_last_frame.items():
            if track_id not in confirmed_ids_this_frame:
                lost_tracks.append({"label": label, "cx": cx, "cy": cy, "frame_lost": frame_idx})
        active_last_frame = {
            tid: pos for tid, pos in active_last_frame.items() if tid in confirmed_ids_this_frame
        }
        # prune old candidates
        lost_tracks = [
            lt for lt in lost_tracks if frame_idx - lt["frame_lost"] <= args.reid_window_frames
        ]

        if not args.no_display:
            y_off = 30
            cv2.putText(frame, f"Total vehicles: {sum(counts_by_type.values())}", (10, y_off),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
            y_off += 25
            cv2.putText(frame, f"Line crossings: {sum(line_crossing_counts.values())}", (10, y_off),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)

            cv2.imshow("SIH26124 - Vehicle Counter v3 (press q to quit)", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    if not args.no_display:
        cv2.destroyAllWindows()

    print("-" * 60)
    if frames_with_zero_detections == frame_idx and frame_idx > 0:
        print("EVERY frame had 0 detections - see earlier troubleshooting notes.")
    else:
        print(f"Frames with zero detections: {frames_with_zero_detections}/{frame_idx}")

    print("\nVehicle counts (re-identification applied, most reliable):")
    for label, count in counts_by_type.items():
        print(f"  {label}: {count}")
    print(f"  TOTAL: {sum(counts_by_type.values())}")

    print("\nLine crossings:")
    for label, count in line_crossing_counts.items():
        print(f"  {label}: {count}")
    print(f"  TOTAL: {sum(line_crossing_counts.values())}")


def _find_reid_match(lost_tracks, label, cx, cy, frame_idx, args):
    """Return the index of a lost_tracks entry that plausibly is this same
    vehicle reappearing, or None if nothing matches closely enough."""
    best_idx, best_dist = None, args.reid_distance_px
    for i, lt in enumerate(lost_tracks):
        if lt["label"] != label:
            continue
        if frame_idx - lt["frame_lost"] > args.reid_window_frames:
            continue
        dist = math.hypot(cx - lt["cx"], cy - lt["cy"])
        if dist <= best_dist:
            best_dist = dist
            best_idx = i
    return best_idx


if __name__ == "__main__":
    main()
