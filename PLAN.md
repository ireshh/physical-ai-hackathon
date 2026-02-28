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
- [ ] Confirm correct voltages with multimeter before powering (leader=7.5V, follower+base=12V)
- [ ] All LEDs show normal state on power-up
- [ ] Gripper camera detected by OS (`ls /dev/video*`)
- [ ] Base camera detected by OS

### Phase 1.5 — Motor ID Configuration (ONE-TIME, do this before anything else)

> The SO-101 uses **Feetech STS3215** servos. Each motor ships with default ID=1.
> You must set unique IDs (1–6 for arm, 7–9 for base wheels) before the robot can work.
> This is written to motor EEPROM — you only do it once per motor set.

**On the Jetson (via SSH) or directly connected laptop:**

1. Connect the motor control board to the computer via USB + power supply
2. Find which USB port the board is on:

   ```bash
   lerobot-find-port
   # Disconnect USB when prompted → note the port printed (e.g. /dev/ttyUSB0)
   ```

3. Set IDs for the **follower arm** (motors 1–6, done one at a time as prompted):

   ```bash
   lerobot-setup-motors \
     --robot.type=so101_follower \
     --robot.port=/dev/ttyUSB0   # ← your port from step 2
   ```

   The script asks you to connect each motor individually in order: gripper(6), wrist_roll(5), wrist_flex(4), elbow_flex(3), shoulder_lift(2), shoulder_pan(1). Connect ONLY the motor being configured each time.

4. Set IDs for the **leader arm** (teleoperator):

   ```bash
   lerobot-setup-motors \
     --teleop.type=so101_leader \
     --teleop.port=/dev/ttyUSB1   # ← your port for leader board
   ```

5. Set IDs for the **LeKiwi base wheels** (7, 8, 9) — this happens as part of the combined lekiwi setup:

   ```bash
   lerobot-setup-motors \
     --robot.type=lekiwi \
     --robot.port=/dev/ttyUSB0   # ← port for the kiwi board
   # Sets arm motors 1–6 first, then wheel motors 7, 8, 9
   ```

6. Label each motor with its ID (tape + marker) — prevents confusion later
7. Daisy-chain all motors in the correct order; connect motor 1 (shoulder_pan) to the controller board

---

## Phase 2 — Software Environment on Jetson

- [ ] SSH into Jetson: `ssh jetsonlX@192.168.55.1` (replace X)
- [ ] `sudo apt update && sudo apt upgrade -y`
- [ ] Install deps: `sudo apt install python3-pip python3-venv git cmake build-essential`
- [ ] Create venv: `python3 -m venv lerobot_env && source lerobot_env/bin/activate`
- [ ] Clone LeRobot: `git clone https://github.com/huggingface/lerobot.git`
- [ ] Clone LeKiwi hardware docs (assembly): `git clone https://github.com/SIGRobotics-UIUC/LeKiwi.git ~/lekiwi`
- [ ] `cd lerobot && pip install -e ".[feetech,lekiwi]"` — **feetech** for arm motors, **lekiwi** adds ZeroMQ for base comms
  - ⚠️ NOT `.[dynamixel]` — SO-101 uses Feetech STS3215, not Dynamixel
- [ ] Clone **this repo** on Jetson and install project deps: `pip install -r requirements.txt`
- [ ] Run `scripts/test_motors.sh` — all motors respond
- [ ] Run `scripts/test_cameras.sh` — both cameras stream
- [ ] Verify base moves with a short manual test command
- [ ] `git commit` all config/env files to this repo

---

## Phase 3 — Calibration

> Calibration maps raw motor encoder values to physical joint angles.
> It's stored in `~/.cache/huggingface/lerobot/calibration/` and must be done once per arm.
> The wheels do **not** need calibration — only arm joints.

- [ ] Calibrate **follower arm on Jetson** (run via SSH on Jetson):

  ```bash
  lerobot-calibrate \
    --robot.type=lekiwi \
    --robot.id=my_kiwi
  ```

  Move robot to middle of all joint ranges → press Enter → sweep every joint through full range
- [ ] Calibrate **leader arm on laptop**:

  ```bash
  lerobot-calibrate \
    --teleop.type=so101_leader \
    --teleop.port=/dev/ttyUSB1 \
    --teleop.id=my_leader
  ```

- [ ] Verify calibration files exist: `ls ~/.cache/huggingface/lerobot/calibration/`
- [ ] Copy calibration files to `data/calibration/` in this repo and commit
- [ ] Test gripper camera focus/exposure in `src/utils/camera_test.py`
- [ ] Verify joint limits are respected (no motor stalling)

---

## Phase 4 — Data Collection

- [ ] Set up fixed task arena (consistent lighting, cube + bin positions)
- [ ] Run teleoperation — on Jetson (via SSH) run the host process:

  ```bash
  python -m lerobot.robots.lekiwi.lekiwi_host --robot.id=my_kiwi
  ```

  Then on laptop run the teleoperation client (set `remote_ip` to Jetson's IP first):

  ```bash
  python ~/lerobot/examples/lekiwi/teleoperate.py
  ```

  Controls: leader arm = follower arm, WASD = base movement, ZX = turn, RF = speed
- [ ] Dry-run 5 episodes to feel out the task
- [ ] Collect **≥50 successful episodes** with varied object placement
  - [ ] 10 episodes collected
  - [ ] 25 episodes collected
  - [ ] 50 episodes collected
- [ ] Record dataset (on laptop, after setting `remote_ip`, `repo_id`, `task` in the script):

  ```bash
  python ~/lerobot/examples/lekiwi/record.py
  # Dataset auto-uploads to your HuggingFace Hub account
  ```

  Pre-requisite: `huggingface-cli login --token YOUR_TOKEN`
- [ ] Spot-check recordings — replay an episode:

  ```bash
  python ~/lerobot/examples/lekiwi/replay.py
  ```

- [ ] Remove failed/bad episodes
- [ ] Backup dataset: it's on HuggingFace Hub automatically; also copy to USB
- [ ] Note dataset stats in `docs/dataset_notes.md`

---

## Phase 5 — Training (Cloud GPU)

- [ ] Launch GPU instance via Vercel (or confirmed alternative provider)
- [ ] Copy dataset to cloud instance with `rsync` or `scp`
- [ ] Set up Python venv + LeRobot on cloud (same steps as Phase 2)
- [ ] Install PyTorch with CUDA: `pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121`
- [ ] Choose policy — **ACT** recommended for visual manipulation (good chunk-size handling)
- [ ] First training run (quick smoke test to catch bugs):

  ```bash
  lerobot-train \
    --policy=act \
    --dataset.repo_id=YOUR_HF_USERNAME/your-dataset-name
  ```

- [ ] Full training run (monitor loss in W&B or TensorBoard):

  ```bash
  lerobot-train \
    --policy=act \
    --dataset.repo_id=YOUR_HF_USERNAME/your-dataset-name \
    --training.num_epochs=200 \
    --device=cuda
  ```

- [ ] Evaluate trained policy in replay mode:

  ```bash
  python ~/lerobot/examples/lekiwi/evaluate.py
  ```

- [ ] Validate — success rate ≥ 70% target
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
| Wrong motor SDK | SO-101 uses **Feetech STS3215**, NOT Dynamixel. Install `.[feetech,lekiwi]` |
| Motor IDs not set | Run `lerobot-setup-motors` before anything else (Phase 1.5 in this plan) |
| Poor grasp data | Review episodes after every 10; delete bad ones |
| Slow inference on Jetson | Use TensorRT; profile before the demo |
| Last-minute integration | Start integration in Phase 6, not Phase 8 |
| Live demo failure | Have backup video; practice 3+ times |
| Internet down during training | Pre-download weights in Phase 0 |
| Writing data to wrong disk | Laptop `/` has only 27 GB free — **always use `/home` (234 GB free)** |

---

## System Info (this laptop)

| Resource | Value | Notes |
|----------|-------|-------|
| CPU | i3-1215U, 6 cores | Fine for code editing |
| RAM | 15 GB | Fine |
| GPU | **None** | Training → Jetson or cloud only |
| Disk `/` | ~27 GB free | Tight — do NOT install large packages here |
| Disk `/home` | ~226 GB free | Use this for conda envs, data, models |
| Python env | conda `lerobot` (3.10) | `conda activate lerobot` |

---

## Key Commands Reference

```bash
# SSH into Jetson
ssh jetsonlX@192.168.55.1

# Activate venv (Jetson)
source ~/lerobot_env/bin/activate
# OR if using conda on laptop
conda activate lerobot

# --- MOTOR SETUP (one-time) ---
lerobot-find-port                      # find USB port of motor board
lerobot-setup-motors \
  --robot.type=lekiwi \
  --robot.port=/dev/ttyUSB0            # set IDs for all arm + base motors

# --- CALIBRATION ---
# On Jetson (follower arm + base):
lerobot-calibrate --robot.type=lekiwi --robot.id=my_kiwi
# On laptop (leader arm):
lerobot-calibrate --teleop.type=so101_leader \
  --teleop.port=/dev/ttyUSB0 --teleop.id=my_leader

# --- TELEOPERATION ---
# Step 1 — on Jetson:
python -m lerobot.robots.lekiwi.lekiwi_host --robot.id=my_kiwi
# Step 2 — on laptop (set remote_ip in script first):
python ~/lerobot/examples/lekiwi/teleoperate.py
# Keys: WASD=drive  ZX=turn  RF=speed  leader-arm=follower-arm

# --- RECORD DATASET (on laptop) ---
# Set remote_ip, repo_id, task in script first:
python ~/lerobot/examples/lekiwi/record.py

# --- REPLAY EPISODE ---
python ~/lerobot/examples/lekiwi/replay.py

# --- TRAIN (on cloud GPU) ---
lerobot-train \
  --policy=act \
  --dataset.repo_id=YOUR_HF_USER/your-dataset \
  --training.num_epochs=200 \
  --device=cuda

# --- EVALUATE POLICY (on Jetson) ---
python ~/lerobot/examples/lekiwi/evaluate.py

# --- NAVIGATE TO OBJECT (custom, this repo) ---
python src/navigation/navigate.py --target cube --color red
```
