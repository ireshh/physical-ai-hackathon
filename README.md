# €5000 Physical AI Hackathon — ireshh/physical-ai-hackathon

> Physical Robotics Hackathon by LUMI at Illusian  
> Stack: LeRobot SO-101 arm · LeKiwi base · Jetson Orin Nano · ACT policy

---

## Project structure
```
.
├── PLAN.md                  ← Master plan & progress tracking (start here)
├── requirements.txt
├── src/
│   ├── inference/
│   │   └── run_policy.py    ← Run trained policy on real robot
│   ├── navigation/
│   │   ├── detect_object.py ← Colour + YOLO object detection
│   │   └── navigate.py      ← PID visual-servoing to approach object
│   ├── teleoperation/
│   └── utils/
│       └── camera_test.py   ← Quick camera diagnostics
├── data/                    ← gitignored — back up separately
│   ├── raw/
│   ├── processed/
│   └── checkpoints/
├── models/                  ← gitignored — back up separately
├── scripts/
│   ├── setup_jetson.sh      ← One-time Jetson environment setup
│   ├── test_motors.sh       ← Verify all Dynamixel motors
│   ├── test_cameras.sh      ← Verify cameras stream
│   ├── collect_data.sh      ← Record teleoperated demonstrations
│   ├── prefetch_models.sh   ← Pre-download weights before the event
│   └── convert_to_tensorrt.sh ← Optimise model for Jetson
└── docs/
    ├── dataset_notes.md
    ├── training_notes.md
    ├── test_log.md
    └── judge_prep.md
```

## Quick start (on Jetson)
```bash
# 1. SSH in
ssh jetsonlX@192.168.55.1

# 2. Clone repo
git clone https://github.com/ireshh/physical-ai-hackathon.git
cd physical-ai-hackathon

# 3. Set up environment (once)
bash scripts/setup_jetson.sh

# 4. Activate venv
source ~/lerobot_env/bin/activate

# 5. Verify hardware
bash scripts/test_motors.sh
bash scripts/test_cameras.sh

# 6. Run inference (after training)
python src/inference/run_policy.py --checkpoint models/best_checkpoint.pt
```

## See [PLAN.md](PLAN.md) for the full step-by-step hackathon plan.
