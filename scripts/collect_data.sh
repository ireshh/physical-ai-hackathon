#!/usr/bin/env bash
# ============================================================
# collect_data.sh — Record teleoperated demonstrations
# Usage: bash scripts/collect_data.sh --episodes 50
# ============================================================
set -euo pipefail
source ~/lerobot_env/bin/activate

EPISODES=${1:-50}
REPO_ROOT=$(dirname "$(dirname "$(realpath "$0")")")
OUTPUT_DIR="$REPO_ROOT/data/raw/dataset_v1"

mkdir -p "$OUTPUT_DIR"

echo "=== Starting data collection: $EPISODES episodes ==="
echo "Output: $OUTPUT_DIR"
echo ""
echo "Controls:"
echo "  Move leader arm  -> follower mirrors it"
echo "  Press SPACE      -> save episode"
echo "  Press ESC        -> discard episode"
echo "  Press q          -> quit"
echo ""

python ~/lerobot/lerobot/scripts/record.py \
    --robot so101 \
    --fps 30 \
    --episodes "$EPISODES" \
    --out_dir "$OUTPUT_DIR"

echo ""
echo "=== Data collection complete ==="
echo "Episodes saved to: $OUTPUT_DIR"
echo "NEXT STEP: Review episodes, then back up the data."
