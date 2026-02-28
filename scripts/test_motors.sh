#!/usr/bin/env bash
# ============================================================
# test_motors.sh — Verify all Feetech STS3215 motors respond
#
# SO-101 uses Feetech STS3215 servos, NOT Dynamixel.
# Motor IDs:
#   Arm (follower): 1=shoulder_pan, 2=shoulder_lift, 3=elbow_flex,
#                   4=wrist_flex, 5=wrist_roll, 6=gripper
#   Base wheels:    7=left, 8=right, 9=back
#
# Usage: bash scripts/test_motors.sh
# Must run on the Jetson (or device the motor board is connected to).
# Find port first with: lerobot-find-port
# ============================================================
set -euo pipefail
source ~/lerobot_env/bin/activate

echo "=== Testing Feetech STS3215 motors ==="
echo "(Finding port — alternatively run 'lerobot-find-port' manually)"
echo ""

python3 - <<'EOF'
import sys

try:
    from lerobot.common.motors.feetech import FeetechMotorsBus
except ImportError:
    print("ERROR: LeRobot feetech SDK not found.")
    print("Run inside ~/lerobot:  pip install -e '.[feetech,lekiwi]'")
    sys.exit(1)

# ── adjust PORT if your board appears elsewhere ───────────────────────────────
PORT = "/dev/ttyUSB0"   # find with: lerobot-find-port
# ─────────────────────────────────────────────────────────────────────────────

ALL_MOTORS = {
    # arm
    "shoulder_pan":  (1, "sts3215"),
    "shoulder_lift": (2, "sts3215"),
    "elbow_flex":    (3, "sts3215"),
    "wrist_flex":    (4, "sts3215"),
    "wrist_roll":    (5, "sts3215"),
    "gripper":       (6, "sts3215"),
    # base wheels
    "wheel_left":    (7, "sts3215"),
    "wheel_right":   (8, "sts3215"),
    "wheel_back":    (9, "sts3215"),
}

print(f"Connecting to {PORT} ...")
try:
    bus = FeetechMotorsBus(port=PORT, motors=ALL_MOTORS)
    bus.connect()
except Exception as e:
    print(f"FAIL — Cannot open {PORT}: {e}")
    print("Is the USB cable connected and power on?")
    sys.exit(1)

ok, fail = [], []
for name, (mid, _) in ALL_MOTORS.items():
    try:
        pos = bus.read("Present_Position", name)
        print(f"  OK   {name:20s} id={mid}  pos={pos}")
        ok.append(name)
    except Exception as e:
        print(f"  FAIL {name:20s} id={mid}  {e}")
        fail.append(name)

bus.disconnect()

print(f"\nResult: {len(ok)}/{len(ALL_MOTORS)} motors OK")
if fail:
    print(f"Missing: {fail}")
    print("\nTroubleshooting:")
    print("  1. IDs not set yet? Run 'lerobot-setup-motors' (see PLAN.md Phase 1.5)")
    print("  2. Check daisy-chain cabling — motor 1 must connect to controller board")
    print("  3. Verify power supply is on at correct voltage")
    sys.exit(1)
else:
    print("\nAll motors OK — ready to calibrate.")
EOF

