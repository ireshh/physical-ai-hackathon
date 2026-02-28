#!/usr/bin/env bash
# ============================================================
# setup_jetson.sh
# Run this ONCE on the Jetson Orin Nano after SSH-ing in.
# Usage: bash scripts/setup_jetson.sh
# ============================================================
set -euo pipefail

echo "=== [1/6] System update ==="
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv git cmake build-essential \
    libopencv-dev python3-opencv v4l-utils

echo "=== [2/6] Create virtual environment ==="
python3 -m venv ~/lerobot_env
source ~/lerobot_env/bin/activate

echo "=== [3/6] Clone LeRobot ==="
if [ ! -d ~/lerobot ]; then
    git clone https://github.com/huggingface/lerobot.git ~/lerobot
fi
cd ~/lerobot
pip install -e ".[dynamixel]"

echo "=== [4/6] Clone LeKiwi ==="
# Official repo: https://github.com/SIGRobotics-UIUC/LeKiwi
if [ ! -d ~/lekiwi ]; then
    git clone https://github.com/SIGRobotics-UIUC/LeKiwi.git ~/lekiwi
fi

echo "=== [5/6] Install project requirements ==="
cd ~/physical-ai-hackathon  # adjust if cloned elsewhere
pip install -r requirements.txt

echo "=== [6/6] Done ==="
echo "Activate venv with: source ~/lerobot_env/bin/activate"
