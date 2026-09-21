"""
Quick setup check - run this FIRST, before pipeline.py.

Unlike pipeline.py, this doesn't need the custom-trained pothole or
number-plate models (which don't exist yet - see models/README.md).
It only uses yolov8n.pt, which downloads automatically the first time
you run this, so it proves your whole setup (Python, packages, camera/video
access) works before you touch the more complex full pipeline.

Usage:
    python test_setup.py                  # uses your laptop webcam
    python test_setup.py --video path.mp4 # uses a video file instead

Press "q" in the video window to quit.
"""

import argparse

import cv2
from ultralytics import YOLO

VEHICLE_AND_PERSON_CLASSES = {0: "person", 2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", default=0, help="Path to a video file, or omit to use the webcam")
    args = parser.parse_args()

    print("Loading YOLOv8n (downloads automatically the first time, ~6MB)...")
    model = YOLO("yolov8n.pt")
    print("Model loaded. Opening video source...")

    source = args.video if args.video != 0 else 0
    cap = cv2.VideoCapture(source)

    if not cap.isOpened():
        print("Could not open the video source. If you passed --video, check the file path.")
        print("If using the webcam, check another app isn't already using it.")
        return

    print("Running. A window should open showing detections. Press 'q' to quit.")

    while True:
        ok, frame = cap.read()
        if not ok:
            print("Stream ended.")
            break

        results = model.predict(
            frame, conf=0.4, classes=list(VEHICLE_AND_PERSON_CLASSES.keys()), verbose=False
        )[0]

        for box in results.boxes:
            x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
            label = VEHICLE_AND_PERSON_CLASSES.get(int(box.cls[0]), "object")
            conf = float(box.conf[0])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 200, 255), 2)
            cv2.putText(
                frame, f"{label} {conf:.2f}", (x1, max(y1 - 8, 0)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 255), 2,
            )

        cv2.imshow("SIH26124 - Setup Check (press q to quit)", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Done. If you saw boxes around cars/people, your setup works.")


if __name__ == "__main__":
    main()
