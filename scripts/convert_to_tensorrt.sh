#!/usr/bin/env bash
# ============================================================
# convert_to_tensorrt.sh
# Convert a PyTorch checkpoint to TensorRT for faster inference
# on the Jetson Orin Nano.
# Prerequisites: torch2trt or trtexec (comes with TensorRT on JetPack)
# Usage: bash scripts/convert_to_tensorrt.sh models/best_checkpoint.pt
# ============================================================
set -euo pipefail
source ~/lerobot_env/bin/activate

CHECKPOINT=${1:-models/best_checkpoint.pt}

echo "=== Converting $CHECKPOINT to TensorRT ==="
python3 - <<EOF
import torch
from pathlib import Path

ckpt_path = Path("$CHECKPOINT")
engine_path = ckpt_path.with_suffix(".engine")

print(f"Source: {ckpt_path}")
print(f"Target: {engine_path}")

try:
    from torch2trt import torch2trt
    model = torch.load(ckpt_path, map_location="cuda")
    model.eval().cuda()

    # Dummy input — adjust shape to match your policy's observation spec
    dummy_img  = torch.zeros(1, 3, 224, 224).cuda()
    dummy_state = torch.zeros(1, 14).cuda()       # 14 = 6 joints * 2 (pos+vel) + 2 gripper

    model_trt = torch2trt(model, [dummy_img, dummy_state])
    torch.save(model_trt.state_dict(), engine_path)
    print(f"TensorRT engine saved to {engine_path}")

except ImportError:
    print("torch2trt not available — install it from: https://github.com/NVIDIA-AI-IOT/torch2trt")
    print("Alternatively use trtexec after exporting to ONNX.")
EOF
