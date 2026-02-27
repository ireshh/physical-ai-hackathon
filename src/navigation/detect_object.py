"""
detect_object.py — Detect and localise target objects in camera frames.

Two modes:
  1. Colour segmentation (HSV) — fast, no model needed, good for coloured cubes
  2. YOLOv8 detection — more robust, requires ultralytics + yolov8n.pt

Usage:
    python src/navigation/detect_object.py --mode color --color red --cam 1
    python src/navigation/detect_object.py --mode yolo  --label cube  --cam 1
"""

import argparse
from dataclasses import dataclass
from typing import Optional, Tuple

import cv2
import numpy as np


@dataclass
class Detection:
    """Result of an object detection."""
    found: bool
    cx: float = 0.0     # image-space centre x (pixels)
    cy: float = 0.0     # image-space centre y (pixels)
    area: float = 0.0   # bounding-box area (pixels²)
    bbox: Optional[Tuple[int, int, int, int]] = None  # (x, y, w, h)


# ── Colour segmentation ───────────────────────────────────────────────────────
# HSV ranges for common object colours.  Tune these for your lighting!
COLOR_RANGES = {
    "red":    [(np.array([0,   120,  70]), np.array([10,  255, 255])),
               (np.array([170, 120,  70]), np.array([180, 255, 255]))],
    "green":  [(np.array([36,  100,  70]), np.array([86,  255, 255]))],
    "blue":   [(np.array([100, 150,  70]), np.array([140, 255, 255]))],
    "yellow": [(np.array([20,  100,  70]), np.array([35,  255, 255]))],
}


def detect_by_color(frame: np.ndarray, color: str,
                    min_area: int = 500) -> Detection:
    """Return the largest blob of the given colour in *frame*."""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    ranges = COLOR_RANGES.get(color.lower())
    if ranges is None:
        raise ValueError(f"Unknown color: {color}. Options: {list(COLOR_RANGES)}")

    mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
    for lo, hi in ranges:
        mask |= cv2.inRange(hsv, lo, hi)

    # Remove noise
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel, iterations=1)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return Detection(found=False)

    largest = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(largest)
    if area < min_area:
        return Detection(found=False)

    x, y, w, h = cv2.boundingRect(largest)
    return Detection(found=True, cx=x + w / 2, cy=y + h / 2,
                     area=area, bbox=(x, y, w, h))


# ── YOLO detection ────────────────────────────────────────────────────────────
_yolo_model = None

def _load_yolo(weights: str = "models/yolov8n.pt"):
    global _yolo_model
    if _yolo_model is None:
        try:
            from ultralytics import YOLO
            _yolo_model = YOLO(weights)
        except ImportError:
            raise ImportError("ultralytics not installed. Run: pip install ultralytics")
    return _yolo_model


def detect_by_yolo(frame: np.ndarray, label: str = "cup",
                   conf_threshold: float = 0.4,
                   weights: str = "models/yolov8n.pt") -> Detection:
    """Return the highest-confidence YOLO detection matching *label*."""
    model = _load_yolo(weights)
    results = model(frame, verbose=False)[0]

    best = None
    best_conf = 0.0
    for box in results.boxes:
        cls_name = model.names[int(box.cls[0])]
        conf = float(box.conf[0])
        if cls_name.lower() == label.lower() and conf > conf_threshold:
            if conf > best_conf:
                best_conf = conf
                best = box

    if best is None:
        return Detection(found=False)

    x1, y1, x2, y2 = map(int, best.xyxy[0])
    w, h = x2 - x1, y2 - y1
    return Detection(found=True, cx=(x1 + x2) / 2, cy=(y1 + y2) / 2,
                     area=w * h, bbox=(x1, y1, w, h))


# ── Visualisation helper ──────────────────────────────────────────────────────
def draw_detection(frame: np.ndarray, det: Detection, label: str = "") -> np.ndarray:
    vis = frame.copy()
    if det.found and det.bbox:
        x, y, w, h = det.bbox
        cv2.rectangle(vis, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.circle(vis, (int(det.cx), int(det.cy)), 5, (0, 0, 255), -1)
        cv2.putText(vis, f"{label} a={det.area:.0f}",
                    (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    return vis


# ── CLI demo ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode",  choices=["color", "yolo"], default="color")
    parser.add_argument("--color", default="red",
                        help="(color mode) colour to detect")
    parser.add_argument("--label", default="cup",
                        help="(yolo mode) COCO class label")
    parser.add_argument("--cam",   type=int, default=1,
                        help="Camera index (base camera = 1 typically)")
    args = parser.parse_args()

    cap = cv2.VideoCapture(args.cam)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera {args.cam}")

    print("Press 'q' to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if args.mode == "color":
            det = detect_by_color(frame, args.color)
            vis = draw_detection(frame, det, args.color)
        else:
            det = detect_by_yolo(frame, args.label)
            vis = draw_detection(frame, det, args.label)

        status = f"FOUND cx={det.cx:.0f} cy={det.cy:.0f}" if det.found else "NOT FOUND"
        cv2.putText(vis, status, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                    (0, 255, 0) if det.found else (0, 0, 255), 2)
        cv2.imshow("detect_object", vis)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
