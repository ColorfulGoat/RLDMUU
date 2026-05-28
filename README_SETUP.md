# Setup Guide

This guide explains how to set up and run the TurtleBot3 DRL project from zero.

The project compares TurtleBot3 navigation with:

- DDPG
- TD3
- SAC

The project uses:

```text
Windows 11
WSL2 Ubuntu 24.04
Docker Desktop
ROS 2 Jazzy
Gazebo Harmonic
noVNC for browser-based GUI
```

---

## 1. Install WSL2 Ubuntu

Run this in **PowerShell as Administrator**:

```powershell
wsl --install -d Ubuntu-24.04
```

If `Ubuntu-24.04` is not available, run this in **PowerShell**:

```powershell
wsl --list --online
```

Then install Ubuntu from the list.

After installation, restart the computer if Windows asks.

Open **Ubuntu** from the Start Menu and create a Linux username and password.

Check WSL version in **PowerShell**:

```powershell
wsl -l -v
```

Ubuntu should show:

```text
VERSION 2
```

If it shows version 1, run this in **PowerShell**:

```powershell
wsl --set-version Ubuntu-24.04 2
```

Update WSL in **PowerShell**:

```powershell
wsl --update
```

---

## 2. Install Docker Desktop

Install Docker Desktop for Windows.

In Docker Desktop:

1. Open **Settings**
2. Go to **General**
3. Enable **Use the WSL 2 based engine**
4. Go to **Resources → WSL Integration**
5. Enable integration for Ubuntu
6. Click **Apply & Restart**

---

## 3. Check Docker

Run this in **Ubuntu/WSL**:

```bash
docker --version
docker run --rm hello-world
```

If `hello-world` runs successfully, Docker works.

---

## 4. Check GPU support

Run this in **Ubuntu/WSL**:

```bash
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
```

If a GPU table appears, Docker can access the GPU.

If this does not work, the project can still run on CPU, but training will be slower.

---

## 5. Install basic tools

Run this in **Ubuntu/WSL**:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl wget nano htop build-essential ca-certificates
```

---

## 6. Clone the repository

Run this in **Ubuntu/WSL**:

```bash
mkdir -p ~/projects
cd ~/projects
git clone https://github.com/ColorfulGoat/RLDMUU.git
cd RLDMUU
```

After this, the project folder is:

```text
~/projects/robot-navigation-drl
```

Most Docker commands below should be run from this folder.

---

## 7. Build the Docker image

Run this in **Ubuntu/WSL**, from the project folder:

```bash
cd ~/projects/robot-navigation-drl
docker compose build
```

The first build can take a while because it downloads and installs ROS 2, Gazebo, Python packages, PyTorch, noVNC, and desktop dependencies.

Later builds are usually faster because Docker reuses the cache.

---

## 8. Two ways to run the project

There are two ways to run the simulation:

```text
GUI mode       = use this when you want to see Gazebo/RViz in the browser
Headless mode  = use this for training without the GUI
```

### Option A: GUI mode

Run this in **Ubuntu/WSL**, from the project folder:

```bash
cd ~/projects/robot-navigation-drl
docker compose up -d gui
```

Open noVNC in the browser:

```text
http://localhost:6080/vnc.html
```

Enter the GUI container from **Ubuntu/WSL**:

```bash
docker exec -it tb3-drl-gui bash
```

Stop GUI mode from **Ubuntu/WSL**:

```bash
cd ~/projects/robot-navigation-drl
docker compose stop gui
```

### Option B: Headless mode

Run this in **Ubuntu/WSL**, from the project folder:

```bash
cd ~/projects/robot-navigation-drl
docker compose up -d headless
```

Enter the headless container from **Ubuntu/WSL**:

```bash
docker exec -it tb3-drl-headless bash
```

Stop headless mode from **Ubuntu/WSL**:

```bash
cd ~/projects/robot-navigation-drl
docker compose stop headless
```

---

## 9. Build the ROS workspace

First start either GUI mode or headless mode.

Then enter the container from **Ubuntu/WSL**.

For GUI mode:

```bash
docker exec -it tb3-drl-gui bash
```

For headless mode:

```bash
docker exec -it tb3-drl-headless bash
```

Then run this **inside the Docker container**:

```bash
cd /workspace
colcon build
```

After the first build, open a new container terminal or run this **inside the Docker container**:

```bash
source /workspace/scripts/ros_env.sh
```

Check that the ROS packages are available. Run this **inside the Docker container**:

```bash
ros2 pkg list | grep turtlebot3_drl
```

Expected output should include:

```text
turtlebot3_drl
turtlebot3_drl_gazebo
```

---

## 10. Run TD3 demo

The demo needs four container terminals.

### Option A: TD3 demo in GUI mode

Start GUI mode from **Ubuntu/WSL**:

```bash
cd ~/projects/robot-navigation-drl
docker compose up -d gui
```

Open noVNC in the browser:

```text
http://localhost:6080/vnc.html
```

Open four Ubuntu/WSL terminals.

In each Ubuntu/WSL terminal, enter the GUI container:

```bash
docker exec -it tb3-drl-gui bash
```

Then run one command per container terminal.

Terminal 1, run **inside the Docker container**:

```bash
ros2 launch turtlebot3_drl_gazebo turtlebot3_drl_stage9.launch.py
```

Terminal 2, run **inside the Docker container**:

```bash
ros2 run turtlebot3_drl gazebo_goals
```

Terminal 3, run **inside the Docker container**:

```bash
ros2 run turtlebot3_drl environment
```

Terminal 4, run **inside the Docker container**:

```bash
ros2 run turtlebot3_drl test_agent td3 "examples/td3_0_stage9" 7400
```

If it works, the robot should move in Gazebo and the terminal should print episode results.

Stop GUI mode from **Ubuntu/WSL**:

```bash
cd ~/projects/robot-navigation-drl
docker compose stop gui
```

### Option B: TD3 demo in headless mode

Start headless mode from **Ubuntu/WSL**:

```bash
cd ~/projects/robot-navigation-drl
docker compose up -d headless
```

Open four Ubuntu/WSL terminals.

In each Ubuntu/WSL terminal, enter the headless container:

```bash
docker exec -it tb3-drl-headless bash
```

Then run one command per container terminal.

Terminal 1, run **inside the Docker container**:

```bash
ros2 launch turtlebot3_drl_gazebo turtlebot3_drl_stage9.launch.py headless:=true
```

Terminal 2, run **inside the Docker container**:

```bash
ros2 run turtlebot3_drl gazebo_goals
```

Terminal 3, run **inside the Docker container**:

```bash
ros2 run turtlebot3_drl environment
```

Terminal 4, run **inside the Docker container**:

```bash
ros2 run turtlebot3_drl test_agent td3 "examples/td3_0_stage9" 7400
```

Stop headless mode from **Ubuntu/WSL**:

```bash
cd ~/projects/robot-navigation-drl
docker compose stop headless
```

---

## 11. Useful Docker commands

Run these in **Ubuntu/WSL**, from the project folder unless stated otherwise.

Stop GUI container:

```bash
docker compose stop gui
```

Stop headless container:

```bash
docker compose stop headless
```

Check running containers:

```bash
docker ps
```

Enter GUI container:

```bash
docker exec -it tb3-drl-gui bash
```

Enter headless container:

```bash
docker exec -it tb3-drl-headless bash
```

Rebuild Docker image after Dockerfile changes:

```bash
docker compose build
```

Recreate GUI container after changes:

```bash
docker compose up -d --force-recreate gui
```

Recreate headless container after changes:

```bash
docker compose up -d --force-recreate headless
```

---

## 12. Project folders

Use these folders for our own training outputs:

```text
models/ddpg/
models/td3/
models/sac/

results/ddpg/
results/td3/
results/sac/
```

---

## 13. Rules

- Do not rename ROS 2 packages yet.
- Keep the baseline working before changing algorithms.
- Save models in `models/`.
- Save logs/results in `results/`.
- Use the same environment settings for DDPG, TD3, and SAC.
- Use GUI mode for testing and visualization.
- Use headless mode for training.

---

## 14. Acknowledgements

This project builds on:
- https://github.com/tomasvr/turtlebot3_drlnav
