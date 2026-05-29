# TurtleBot3 DRL Navigation

This project is about using Deep Reinforcement Learning to help a robot successfully navigate an unknown environment. The robot gradually learns to reach specific goals while avoiding collisions with walls.

The project uses ROS 2 Jazzy with Gazebo Harmonic, and it is all implemented inside a containerized environment using Docker.

---

## Implementation

We started from an existing TurtleBot3 DRL navigation baseline and adapted it for our course project. The main focus was not to build a perfect robot navigation system, but to create a reproducible setup where different DRL algorithms can be trained and compared fairly.

In this project we:

- use ROS 2 Jazzy and Gazebo Harmonic
- use Docker with WSL2 as backend
- implement both GUI mode and headless mode
- use the TurtleBot3 Burger robot in a custom navigation world
- use LiDAR, goal distance, goal angle, and previous actions as the agent state
- train and test continuous-control DRL algorithms
- compare DDPG, TD3, and REDQ under the same environment
- save model checkpoints, replay buffers, logs, and result plots for each algo

The key idea is that the environment, reward function, robot, and world stay the same, while only the algorithm changes.

---

## Algorithms

We worked with three off-policy actor-critic algorithms:

| Algorithm | Role in the project |
|---|---|
| DDPG | Basic continuous-control baseline |
| TD3 | More stable version of DDPG with twin critics and delayed actor updates |
| REDQ | More sample-efficient method using multiple critics and more updates per step |

All three algorithms use the same robot environment and reward function, so the comparison is easier to understand.

---

## System overview

The project runs as a 4 ROS 2 processes working together:

1. **Gazebo simulation** runs the TurtleBot3 world.
2. **Goal manager** creates and updates navigation goals.
3. **Environment node** reads sensor data, builds the state, computes reward, and detects episode endings.
4. **DRL agent** chooses actions and trains the neural networks.

The agent outputs continuous velocity commands, specifically: linear velocity and angular velocity.

---

## Training setup

For training, we use headless mode because it is faster and does not waste resources on the Gazebo GUI or RViz.

Each training run saves useful files, such as:

- actor weights
- critic weights
- target network weights
- replay buffer
- reward / outcome plot
- training log

The main folders we use are:

```text
models/
├── ddpg/
├── td3/
└── redq/

results/
├── ddpg/
├── td3/
└── redq/
```

This keeps the outputs from different algorithms separate.

---

## Basic run commands

Build the Docker image:

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

Inside the container, source the ROS environment:

```bash
source /workspace/scripts/ros_env.sh
```

Then run the simulation in four terminals.

Terminal 1:

```bash
ros2 launch turtlebot3_drl_gazebo turtlebot3_drl_stage9.launch.py headless:=true
```

Terminal 2:

```bash
ros2 run turtlebot3_drl gazebo_goals
```

Terminal 3:

```bash
ros2 run turtlebot3_drl environment
```

Terminal 4:

```bash
ros2 run turtlebot3_drl train_agent td3
```

Replace `td3` with `ddpg` or `redq` to train another algorithm.

---

## Evaluation

For the final comparison, we look at simple metrics:

- average reward
- success rate
- collision rate
- timeout rate
- episode length
- training time
- reward curve over episodes

These metrics are enough to show whether the robot is improving and whether one algorithm is more stable or efficient than another.

---

## Notes

The goal is to show a working DRL pipeline for robot navigation and compare algorithms in a controlled way. Some parts can still be improved, such as longer training, better hyperparameter tuning, more worlds, and a possible federated learning extension.

---

## Acknowledgements

This is a ROS 2 Jazzy / Gazebo Harmonic port of **[tomasvr/turtlebot3_drlnav](https://github.com/tomasvr/turtlebot3_drlnav)** (ROS 2 Foxy + Gazebo Classic). The reward function, stage layout, and pretrained model
(`examples/ddpg_0_stage9`, `examples/td3_0_stage9`) are from that repo. TurtleBot3 meshes and
base SDFs come from [ROBOTIS-GIT/turtlebot3](https://github.com/ROBOTIS-GIT/turtlebot3)
and [ROBOTIS-GIT/turtlebot3_simulations](https://github.com/ROBOTIS-GIT/turtlebot3_simulations).
