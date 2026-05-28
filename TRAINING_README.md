# Training Guide — TurtleBot3 DRL Models

This guide explains the agreed training setup for our project and how each team member should train their assigned algorithm.

We train three algorithms:

- DDPG
- TD3
- REDQ

All models should be trained from scratch using the same environment and settings.

---

## 1. Training settings

The current real-training configuration in `settings.py` is:

```python
MODEL_STORE_INTERVAL     = 100
GRAPH_DRAW_INTERVAL      = 10

EPISODE_TIMEOUT_SECONDS  = 40

HIDDEN_SIZE              = 256
BATCH_SIZE               = 64
OBSERVE_STEPS            = 2000

REDQ_BATCH_SIZE          = 128
REDQ_ENSEMBLE_SIZE       = 5
REDQ_UTD_RATIO           = 5

MAX_TRAINING_EPISODES    = 1000
```

### Meaning of the main settings

| Setting | Meaning |
|---|---|
| `MODEL_STORE_INTERVAL = 100` | Save model checkpoints every 100 episodes. |
| `GRAPH_DRAW_INTERVAL = 10` | Update training graph every 10 episodes. |
| `EPISODE_TIMEOUT_SECONDS = 40` | End an episode if it lasts longer than 40 seconds. |
| `HIDDEN_SIZE = 256` | Use smaller neural networks for lower hardware requirements. |
| `BATCH_SIZE = 64` | Use smaller batches for DDPG/TD3 training. |
| `OBSERVE_STEPS = 2000` | Collect 2000 random environment steps before counted training episodes begin. |
| `REDQ_BATCH_SIZE = 128` | Use a lighter REDQ batch size. |
| `REDQ_ENSEMBLE_SIZE = 5` | Use a smaller REDQ critic ensemble. |
| `REDQ_UTD_RATIO = 5` | Use fewer REDQ gradient updates per environment step. |
| `MAX_TRAINING_EPISODES = 1000` | Stop training automatically after 1000 counted episodes. |

The observe phase happens first and does not count toward the 1000 training episodes.

---

## 2. Output folders

Training outputs are saved into the project folders:

```text
models/<algorithm>/<run_name>/
results/<algorithm>/<run_name>/
```

Example for TD3:

```text
models/td3/td3_0_stage_9/
results/td3/td3_0_stage_9/train_log.csv
```

The model folder contains checkpoint files such as actor/critic weights and replay buffer files.

The results folder contains the CSV log and run metadata.

---

## 3. Before training

From WSL, go to the project folder:

```bash
cd ~/projects/robot-navigation-drl
```

Pull the latest version:

```bash
git pull origin main
```

Build or rebuild the Docker image if needed:

```bash
docker compose build
```

Start the headless container:

```bash
docker compose up -d headless
```

Enter the container:

```bash
docker exec -it tb3-drl-headless bash
```

Inside the container, build the ROS package:

```bash
cd /workspace
source /workspace/scripts/ros_env.sh
colcon build --packages-select turtlebot3_drl --symlink-install
source /workspace/scripts/ros_env.sh
```

---

## 4. Training workflow

Training needs four container terminals.

Open four WSL terminals. In each one, enter the container:

```bash
cd ~/projects/robot-navigation-drl
docker exec -it tb3-drl-headless bash
cd /workspace
source /workspace/scripts/ros_env.sh
```

### Terminal 1 — simulation

```bash
ros2 launch turtlebot3_drl_gazebo turtlebot3_drl_stage9.launch.py headless:=true
```

### Terminal 2 — goal publisher

```bash
ros2 run turtlebot3_drl gazebo_goals
```

### Terminal 3 — DRL environment

```bash
ros2 run turtlebot3_drl environment
```

### Terminal 4 — training command

Run only one algorithm per machine.

For DDPG:

```bash
ros2 run turtlebot3_drl train_agent ddpg
```

For TD3:

```bash
ros2 run turtlebot3_drl train_agent td3
```

For REDQ:

```bash
ros2 run turtlebot3_drl train_agent redq
```

Training stops automatically after `MAX_TRAINING_EPISODES = 1000` counted episodes.

Optional safety timeout:

```bash
timeout 4h ros2 run turtlebot3_drl train_agent td3
```

Replace `td3` with `ddpg` or `redq` as needed.

---

## 5. Check saved outputs

After training, check the model folder:

```bash
find models -maxdepth 3 -type d | sort
find models -type f | sort | tail -40
```

Check the CSV log:

```bash
find results -name "train_log.csv" -type f | sort
```

Example:

```bash
CSV_FILE=$(find results/td3 -name "train_log.csv" -type f | sort | tail -1)
echo "$CSV_FILE"
tail -5 "$CSV_FILE"
```

The CSV contains per-episode data, including:

- episode
- total steps
- reward
- outcome
- success/collision/timeout flags
- episode duration
- actor loss
- critic loss
- checkpoint flag

Summary metrics such as success rate, collision rate, timeout rate, average reward, total training time, and final episode count will be computed later from this CSV.

---

## 6. Resuming training

To resume from a saved checkpoint, use:

```bash
ros2 run turtlebot3_drl train_agent <algorithm> <run_name> <episode_number>
```

Example:

```bash
ros2 run turtlebot3_drl train_agent td3 td3_0_stage_9 1000
```

Important: if resuming from episode 1000, increase `MAX_TRAINING_EPISODES` first. Otherwise training will stop immediately.

---

## 7. Rules for fair comparison

Use the same setup for all algorithms:

- Same Docker image
- Same Gazebo world/stage
- Same TurtleBot3 model
- Same reward function
- Same episode timeout
- Same observe steps
- Same maximum training episodes
- Same evaluation procedure later

Only the algorithm should change.
