#!/usr/bin/env bash
# ============================================================
# prefetch_models.sh — Pre-download model weights before event
# Run on a fast internet connection. 
# Usage: bash scripts/prefetch_models.sh
# ============================================================
set -euo pipefail
source ~/lerobot_env/bin/activate

REPO_ROOT=$(dirname "$(dirname "$(realpath "$0")")")
MODELS_DIR="$REPO_ROOT/models"
mkdir -p "$MODELS_DIR"

echo "=== Downloading YOLO weights for object detection ==="
python3 - <<'EOF'
from pathlib import Path
import urllib.request

# YOLOv8 nano — lightweight, fast on Jetson
url = "https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt"
dest = Path("models/yolov8n.pt")
if not dest.exists():
    print(f"Downloading {url} ...")
    urllib.request.urlretrieve(url, dest)
    print(f"Saved to {dest}")
else:
    print("yolov8n.pt already present — skipping")
EOF

echo ""
echo "=== Done prefetching models ==="
