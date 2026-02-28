# €5000 Physical AI Hackathon — Master Plan
>
> **Team repo:** <https://github.com/ireshh/physical-ai-hackathon>  
> **Last updated:** 2026-02-27  
> Track everything here. Check boxes as you go. Never skip a phase.

---

## Roles (fill in)

| Role | Person |
|------|--------|
| Hardware lead | |
| Software lead | |
| ML lead | |
| Demo lead | |

---

## Phase 0 — Pre-Hackathon Prep

- [ ] Read LeRobot SO-101 docs: <https://github.com/huggingface/lerobot>
- [ ] Read LeKiwi docs: <https://github.com/SIGRobotics-UIUC/LeKiwi>
- [ ] Confirm team roles above
- [ ] Confirm task: **Object Fetch and Sort** (robot navigates to a coloured cube, picks it up, drops it in a bin)
- [ ] Pre-download large model weights (see `scripts/prefetch_models.sh`) on fast WiFi
- [ ] Claim GPU credits with code `ROBOTICS-NATION-HACKATHON` (max 2 per team) — **verify with organisers which provider** (Vercel is frontend-only; it's likely a partner GPU provider)
- [ ] Prepare fallback demo video slot — record one during Phase 8

---

## Phase 1 — Hardware Setup & Verification

- [ ] Physically inspect SO-101 leader arm (7.5V) — note any broken plastic
- [ ] Physically inspect SO-101 follower arm + gripper camera (12V)
- [ ] Inspect LeKiwi base + base camera (12V)
- [ ] Jetson Orin Nano boots correctly (JetPack installed per organisers)
- [ ] Verify all Dynamixel IDs on follower arm (re-ID if needed per LeRobot docs)
- [ ] Label each motor with its ID (tape + marker)
- [ ] Confirm correct voltages with multimeter before powering (7.5V / 12V / 12V)
- [ ] All LEDs show normal state on power-up
- [ ] Gripper camera detected by OS (`ls /dev/video*`)
- [ ] Base camera detected by OS

---

## Phase 2 — Software Environment on Jetson

- [ ] SSH into Jetson: `ssh jetsonlX@192.168.55.1` (replace X)
- [ ] `sudo apt update && sudo apt upgrade -y`
- [ ] Install deps: `sudo apt install python3-pip python3-venv git cmake build-essential`
- [ ] Create venv: `python3 -m venv lerobot_env && source lerobot_env/bin/activate`
- [ ] Clone LeRobot: `git clone https://github.com/huggingface/lerobot.git`
- [ ] Clone LeKiwi: `git clone https://github.com/SIGRobotics-UIUC/LeKiwi.git ~/lekiwi`
- [ ] `cd lerobot && pip install -e ".[dynamixel]"` (include extras for hardware)
- [ ] Install LeKiwi deps (per its README)
- [ ] Clone **this repo** on Jetson and install project deps: `pip install -r requirements.txt`
- [ ] Run `scripts/test_motors.sh` — all motors respond
- [ ] Run `scripts/test_cameras.sh` — both cameras stream
- [ ] Verify base moves with a short manual test command
- [ ] `git commit` all config/env files to this repo

---

## Phase 3 — Calibration

- [ ] Calibrate leader arm: `python lerobot/scripts/calibrate.py --robot so101`
- [ ] Calibrate follower arm
- [ ] Save calibration JSON to `data/` and commit
- [ ] Calibrate LeKiwi wheels/odometry (see LeKiwi docs)
- [ ] Test gripper camera focus/exposure in `src/utils/camera_test.py`
- [ ] Verify joint limits are respected (no motor stalling)

---

## Phase 4 — Data Collection

- [ ] Set up fixed task arena (consistent lighting, cube + bin positions)
- [ ] Run teleoperation: `python lerobot/scripts/teleoperate.py --robot so101`
- [ ] Dry-run 5 episodes to feel out the task
- [ ] Collect **≥50 successful episodes** with varied object placement
  - [ ] 10 episodes collected
  - [ ] 25 episodes collected
  - [ ] 50 episodes collected
- [ ] Spot-check recordings (play back 5 random episodes)
- [ ] Remove failed/bad episodes
- [ ] Backup dataset: copy to Google Drive / USB / cloud
- [ ] Note dataset stats in `docs/dataset_notes.md`

---

## Phase 5 — Training (Cloud GPU)

- [ ] Launch GPU instance via Vercel (or confirmed alternative provider)
- [ ] Copy dataset to cloud instance with `rsync` or `scp`
- [ ] Set up Python venv + LeRobot on cloud (same steps as Phase 2)
- [ ] Install PyTorch with CUDA: `pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121`
- [ ] Choose policy — **ACT** (Action Chunking Transformer) recommended for visual manipulation
- [ ] First training run (quick 50-epoch smoke test to catch bugs)
- [ ] Full training run (200+ epochs); monitor loss in TensorBoard / W&B
- [ ] Validate on held-out episodes — success rate ≥ 70% target
- [ ] If success rate low: collect more data (go to Phase 4) or tune hyperparameters
- [ ] Download best checkpoint to `models/` and commit hash to `docs/training_notes.md`
- [ ] Backup checkpoint to USB/Drive

---

## Phase 6 — Deployment on Jetson

- [ ] Transfer model checkpoint to Jetson (`scp` or USB)
- [ ] Convert to TensorRT for faster inference: `scripts/convert_to_tensorrt.sh`
- [ ] Run `src/inference/run_policy.py` — arm only, base locked
- [ ] Verify arm tracks policy correctly for 5 runs
- [ ] Enable base: run full integrated policy
- [ ] Confirm dead-man switch works (see `src/inference/run_policy.py`)
- [ ] Confirm emergency stop (keyboard `q` or hardware kill) works
- [ ] Watchdog timer tested — motors stop if script crashes

---

## Phase 7 — Base + Arm Integration

- [ ] Test end-to-end policy (base + arm in one policy) — preferred if data included base motion
- [ ] If separate: navigation to object via `src/navigation/navigate.py`, then arm policy
- [ ] Object detection working (YOLO or colour segmentation via `src/navigation/detect_object.py`)
- [ ] PID approach controller moves base to within arm reach
- [ ] Arm stowed during navigation (no collision)
- [ ] Grasp, return to bin, release — full sequence works ≥3/5 times
- [ ] Full pipeline stress test: 10 runs, log success/fail in `docs/test_log.md`

---

## Phase 8 — Polish & Testing

- [ ] Test under varied lighting conditions
- [ ] Test with object at 5 different positions
- [ ] Implement and test fallback (retry if grasp fails)
- [ ] **Record a clean backup video** of a successful run (save to `docs/backup_demo.mp4`)
- [ ] Profile inference loop — target < 100 ms per step
- [ ] TensorRT optimisation applied if needed
- [ ] README.md updated with setup and run instructions
- [ ] Final `git push` — all code committed and pushed

---

## Phase 9 — Presentation & Demo

- [ ] Presentation slides created (see structure below)
- [ ] Live demo rehearsed ≥ 3 times
- [ ] Backup video ready to play if live demo fails
- [ ] Arena set up with good lighting + screen showing camera feed
- [ ] Team knows answers to likely judge questions (see `docs/judge_prep.md`)

### Slide structure (7 min total)

1. **Problem** (1 min) — what task, why impressive
2. **Approach** (2 min) — imitation learning with LeRobot, data pipeline, ACT policy, Jetson deployment
3. **Live Demo** (2 min)
4. **Challenges** (1 min) — calibration, data quality, inference speed
5. **Next Steps** (1 min) — RL fine-tuning, more objects, generalisation

---

## Best Practices Checklist

- [ ] All code in git from day 1
- [ ] `README.md` updated with how to run everything
- [ ] Virtual environment used on all machines
- [ ] Data backed up in ≥2 locations
- [ ] Each component tested in isolation before integration
- [ ] Safety features implemented (e-stop, velocity limits, watchdog)
- [ ] Backup demo video recorded

---

## Common Pitfalls — Read Before You Start

| Pitfall | Mitigation |
|---------|-----------|
| Wrong voltages | Check with multimeter; leader = 7.5V, rest = 12V |
| Motor IDs wrong | Re-run ID assignment; label each motor |
| Poor grasp data | Review episodes after every 10; delete bad ones |
| Slow inference on Jetson | Use TensorRT; profile before the demo |
| Last-minute integration | Start integration in Phase 6, not Phase 8 |
| Live demo failure | Have backup video; practice 3+ times |
| Internet down during training | Pre-download weights in Phase 0 |

---

## Key Commands Reference

```bash
# SSH into Jetson
ssh jetsonlX@192.168.55.1

# Activate venv
source lerobot_env/bin/activate

# Teleoperate
python lerobot/scripts/teleoperate.py --robot so101

# Record data
python lerobot/scripts/record.py --robot so101 --fps 30 --episodes 50

# Train (on cloud)
python lerobot/scripts/train.py \
  --policy.type=act \
  --dataset.root=data/processed/dataset_v1 \
  --train.batch_size=16 \
  --train.epochs=200 \
  --device=cuda

# Run inference on Jetson
python src/inference/run_policy.py --checkpoint models/best_checkpoint.pt

# Navigate to object
python src/navigation/navigate.py --target cube --color red
```
