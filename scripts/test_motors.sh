#!/usr/bin/env bash
# ============================================================
# test_motors.sh — Verify all Dynamixel motors are detected
# Usage: bash scripts/test_motors.sh
# ============================================================
set -euo pipefail
source ~/lerobot_env/bin/activate

echo "=== Testing leader arm motors ==="
python3 - <<'EOF'
from dynamixel_sdk import PortHandler, PacketHandler

PORT = "/dev/ttyUSB0"       # adjust if needed
BAUDRATE = 1_000_000
PROTOCOL = 2.0
EXPECTED_IDS = [1, 2, 3, 4, 5, 6]   # update to your actual IDs

port = PortHandler(PORT)
pkt = PacketHandler(PROTOCOL)

if not port.openPort():
    raise RuntimeError(f"Cannot open port {PORT}")
port.setBaudRate(BAUDRATE)

found = []
for mid in range(1, 20):
    model, err, _ = pkt.ping(port, mid)
    if err == 0:
        found.append(mid)
        print(f"  Motor ID {mid}: OK  (model={model})")

port.closePort()
missing = set(EXPECTED_IDS) - set(found)
if missing:
    print(f"\nWARNING: Missing motors: {missing}")
    exit(1)
else:
    print(f"\nAll {len(found)} motors found.")
EOF
