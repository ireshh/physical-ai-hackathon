#!/usr/bin/env bash
# ============================================================
# collect_data.sh — Start the LeKiwi host process on the Jetson
#
# Data recording for LeKiwi uses a client/server split:
#   1. Run THIS script on the Jetson (starts the robot host)
#   2. Run  examples/lekiwi/record.py  on your LAPTOP to record
#
# Usage (on Jetson): bash scripts/collect_data.sh
# Then on laptop:    python ~/lerobot/examples/lekiwi/record.py
#
# Before running:
#   - Set remote_ip, repo_id, and task in examples/lekiwi/record.py
#   - Login to HuggingFace: huggingface-cli login --token YOUR_TOKEN
# ============================================================
set -euo pipefail
source ~/lerobot_env/bin/activate

echo "=== Starting LeKiwi robot host for data collection ==="
echo "NEXT: on your laptop run:"
echo "  python ~/lerobot/examples/lekiwi/record.py"
echo ""
echo "Dataset will auto-upload to your HuggingFace Hub account."
echo "Controls: WASD=drive  ZX=turn  RF=speed  leader-arm=follower-arm"
echo ""

python -m lerobot.robots.lekiwi.lekiwi_host --robot.id=my_kiwi
