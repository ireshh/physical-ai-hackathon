#!/usr/bin/env bash
# ============================================================
# test_cameras.sh — Verify gripper + base cameras stream video
# Usage: bash scripts/test_cameras.sh
# ============================================================
set -euo pipefail
source ~/lerobot_env/bin/activate

echo "=== Detected video devices ==="
ls /dev/video* 2>/dev/null || echo "No /dev/video* devices found!"

echo ""
echo "=== Testing camera streams (press q to quit each) ==="
python3 - <<'EOF'
import cv2
import sys

cameras = {
    "gripper": 0,   # adjust index if needed
    "base":    1,
}

for name, idx in cameras.items():
    cap = cv2.VideoCapture(idx)
    if not cap.isOpened():
        print(f"FAIL — {name} camera (index {idx}) not accessible")
        continue
    ret, frame = cap.read()
    if ret:
        print(f"OK   — {name} camera (index {idx}): {frame.shape}")
    else:
        print(f"FAIL — {name} camera (index {idx}): could not read frame")
    cap.release()
EOF
