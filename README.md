# TurtleBot3 DRL Navigation

This repository is our course project for Deep Reinforcement Learning based autonomous navigation with TurtleBot3 in Gazebo.

## Project goal

The goal is to compare three continuous-control deep reinforcement learning algorithms:

- DDPG
- TD3
- REDQ

The final comparison should use the same robot, environment, reward function, training setup, and evaluation method for all algorithms.

## Setup and usage

For installation, Docker setup, GUI/headless mode, and demo commands, see:

```text
README_SETUP.md
```

## Current status

Working so far:

- Docker Compose setup
- noVNC GUI mode
- Headless mode
- ROS 2 workspace build
- TD3 pretrained demo
- GPU support inside Docker

## Repository structure

Important folders:

```text
src/turtlebot3_drl/          DRL agents, environment, reward, utilities
src/turtlebot3_drl_gazebo/   Gazebo world, launch files, bridges, RViz setup
src/turtlebot3_msgs/         Custom ROS 2 messages and services

models/                      Our saved trained models
results/                     Our experiment logs and results
scripts/                     Helper scripts
```

## Models and results

Our own training outputs should be saved in:

```text
models/ddpg/
models/td3/
models/sac/

results/ddpg/
results/td3/
results/sac/
```

Generated training and test files from the baseline should not be committed unless they are selected final results.

## Project plan

1. Keep the baseline running.
2. Test TD3 baseline behavior.
3. Train DDPG from scratch.
4. Train TD3 from scratch.
5. Add REDQ.
6. Train REDQ from scratch.
7. Add cleaner result logging.
8. Compare DDPG, TD3, and REDQ under the same evaluation setup.

## Project rules

- Do not rename ROS 2 packages yet.
- Keep the baseline working before making major changes.
- Use Docker for all team members.
- Use headless mode for training.
- Use GUI mode for testing, visualization, and demo recording.
- Save project models in `models/`.
- Save project results in `results/`.

## Acknowledgements

This is a ROS 2 Jazzy / Gazebo Harmonic port of **[tomasvr/turtlebot3_drlnav](https://github.com/tomasvr/turtlebot3_drlnav)** (ROS 2 Foxy + Gazebo Classic). The reward function, stage layout, and pretrained model
(`examples/ddpg_0_stage9`, `examples/td3_0_stage9`) are from that repo. TurtleBot3 meshes and
base SDFs come from [ROBOTIS-GIT/turtlebot3](https://github.com/ROBOTIS-GIT/turtlebot3)
and [ROBOTIS-GIT/turtlebot3_simulations](https://github.com/ROBOTIS-GIT/turtlebot3_simulations).