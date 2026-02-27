"""
camera_test.py — Quick camera diagnostics.
Shows a live stream for each camera.  Press 'q' to close a window.

Usage:
    python src/utils/camera_test.py
    python src/utils/camera_test.py --cameras 0 1 2
"""

import argparse
import cv2


def test_camera(idx: int, window_name: str = ""):
    name = window_name or f"Camera {idx}"
    cap = cv2.VideoCapture(idx)

    if not cap.isOpened():
        print(f"FAIL  [{name}] — cannot open index {idx}")
        return

    ret, frame = cap.read()
    if not ret:
        print(f"FAIL  [{name}] — opened but cannot read frame")
        cap.release()
        return

    h, w = frame.shape[:2]
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"OK    [{name}] — {w}x{h} @ {fps:.1f} fps")

    print(f"  Showing live stream. Press 'q' to close {name}.")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.putText(frame, name, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.imshow(name, frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyWindow(name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cameras", type=int, nargs="+", default=[0, 1],
                        help="Camera indices to test")
    args = parser.parse_args()

    labels = {0: "Gripper Camera", 1: "Base Camera"}
    for idx in args.cameras:
        test_camera(idx, labels.get(idx, f"Camera {idx}"))
