"""
navigate.py — Visual-servoing PID controller that drives the LeKiwi base
toward a detected object.

Pipeline:
  1. Detect object in base camera (colour or YOLO)
  2. Compute pixel error from image centre
  3. PID → (forward velocity, turn velocity)
  4. Send commands to LeKiwi base
  5. Stop when object is "close enough" (area threshold)

Usage:
    python src/navigation/navigate.py --target cube --color red
    python src/navigation/navigate.py --target cup   --mode yolo
"""

import argparse
import time
from dataclasses import dataclass, field
from typing import Optional

import cv2
import numpy as np

from detect_object import detect_by_color, detect_by_yolo, draw_detection, Detection


# ── PID controller ─────────────────────────────────────────────────────────--
@dataclass
class PID:
    kp: float
    ki: float
    kd: float
    _integral: float = field(default=0.0, init=False)
    _prev_error: float = field(default=0.0, init=False)
    _last_t: float = field(default=0.0, init=False)

    def reset(self):
        self._integral = 0.0
        self._prev_error = 0.0
        self._last_t = time.time()

    def step(self, error: float) -> float:
        now = time.time()
        dt = max(now - self._last_t, 1e-4)
        self._last_t = now
        self._integral += error * dt
        derivative = (error - self._prev_error) / dt
        self._prev_error = error
        return self.kp * error + self.ki * self._integral + self.kd * derivative


# ── Navigation state machine ──────────────────────────────────────────────────
class NavigatorState:
    SEARCHING  = "SEARCHING"
    APPROACHING = "APPROACHING"
    ARRIVED    = "ARRIVED"


class Navigator:
    """
    Drive the LeKiwi base toward the detected object.

    Coordinate convention (image space):
      - cx error: positive = object is to the RIGHT  → turn right
      - area:     large = object is CLOSE            → stop
    """

    ARRIVE_AREA_THRESHOLD = 20_000   # px² — tune for your object size / distance
    IMAGE_WIDTH  = 640
    IMAGE_HEIGHT = 480
    MAX_FWD_VEL  = 0.15   # m/s
    MAX_TURN_VEL = 0.8    # rad/s

    def __init__(self):
        self.pid_turn = PID(kp=0.004, ki=0.0001, kd=0.001)
        self.pid_fwd  = PID(kp=0.00001, ki=0.0, kd=0.0)
        self.state = NavigatorState.SEARCHING
        self.pid_turn.reset()
        self.pid_fwd.reset()

    def compute_cmd(self, det: Detection) -> tuple[float, float]:
        """Return (forward_vel, turn_vel) given a detection."""
        if not det.found:
            self.state = NavigatorState.SEARCHING
            # Spin slowly to search
            return 0.0, 0.3

        if det.area >= self.ARRIVE_AREA_THRESHOLD:
            self.state = NavigatorState.ARRIVED
            return 0.0, 0.0

        self.state = NavigatorState.APPROACHING

        cx_error = det.cx - self.IMAGE_WIDTH / 2    # pixels (+ = right)
        area_error = self.ARRIVE_AREA_THRESHOLD - det.area  # + = too far

        turn_cmd = -self.pid_turn.step(cx_error)    # negative = turn toward target
        fwd_cmd  =  self.pid_fwd.step(area_error)

        # Clamp
        fwd_cmd  = float(np.clip(fwd_cmd,  0.0, self.MAX_FWD_VEL))
        turn_cmd = float(np.clip(turn_cmd, -self.MAX_TURN_VEL, self.MAX_TURN_VEL))

        return fwd_cmd, turn_cmd

    def arrived(self) -> bool:
        return self.state == NavigatorState.ARRIVED


def send_base_command(fwd_vel: float, turn_vel: float):
    """
    Send velocity commands to the LeKiwi base.
    TODO: replace with actual LeKiwi SDK call, e.g.:
        robot.base.set_velocity(fwd=fwd_vel, turn=turn_vel)
    """
    # PLACEHOLDER
    print(f"[BASE CMD] fwd={fwd_vel:+.3f} m/s  turn={turn_vel:+.3f} rad/s")


def run(args):
    cap = cv2.VideoCapture(args.cam)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera {args.cam}")

    nav = Navigator()

    print(f"Navigating to {args.target!r} ({args.mode} mode). Press 'q' to abort.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Camera read error.")
            break

        # Detection
        if args.mode == "color":
            det = detect_by_color(frame, args.color)
        else:
            det = detect_by_yolo(frame, args.target)

        # Navigation command
        fwd, turn = nav.compute_cmd(det)
        send_base_command(fwd, turn)

        # Visualise
        vis = draw_detection(frame, det, args.target)
        cv2.putText(vis, f"State: {nav.state}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        cv2.imshow("navigate", vis)

        if nav.arrived():
            print("[ARRIVED] Object reached — handing off to grasping policy.")
            send_base_command(0.0, 0.0)
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            send_base_command(0.0, 0.0)
            print("[ABORT] Navigation cancelled by user.")
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=str, default="cube",
                        help="Object name / label to navigate toward")
    parser.add_argument("--mode",   choices=["color", "yolo"], default="color")
    parser.add_argument("--color",  type=str, default="red",
                        help="(color mode) colour of the object")
    parser.add_argument("--cam",    type=int, default=1,
                        help="Base camera index")
    args = parser.parse_args()
    run(args)
