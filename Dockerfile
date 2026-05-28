FROM osrf/ros:jazzy-desktop-full

ENV DEBIAN_FRONTEND=noninteractive
ENV TURTLEBOT3_MODEL=burger
ENV ROS_DOMAIN_ID=1
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:1

WORKDIR /workspace

RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    nano \
    tmux \
    htop \
    build-essential \
    python3-pip \
    python3-colcon-common-extensions \
    python3-numpy \
    python3-matplotlib \
    python3-pandas \
    python3-pyqtgraph \
    python3-pyqt5 \
    ros-jazzy-turtlebot3 \
    ros-jazzy-turtlebot3-description \
    ros-jazzy-turtlebot3-gazebo \
    ros-jazzy-ros-gz \
    ros-jazzy-ros-gz-bridge \
    ros-jazzy-ros-gz-sim \
    ros-jazzy-ros-gz-interfaces \
    ros-jazzy-slam-toolbox \
    ros-jazzy-rviz2 \
    ros-jazzy-tf-transformations \
    xvfb \
    x11vnc \
    novnc \
    websockify \
    xfce4 \
    xfce4-terminal \
    thunar \
    dbus-x11 \
    x11-xserver-utils \
    mesa-utils \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --break-system-packages \
    torch \
    torchvision \
    torchaudio \
    --index-url https://download.pytorch.org/whl/cu124

COPY scripts/start_novnc.sh /usr/local/bin/start_novnc.sh
RUN chmod +x /usr/local/bin/start_novnc.sh

RUN echo "source /opt/ros/jazzy/setup.bash" >> /root/.bashrc && \
    echo "if [ -f /workspace/install/setup.bash ]; then source /workspace/install/setup.bash; fi" >> /root/.bashrc && \
    echo "export TURTLEBOT3_MODEL=burger" >> /root/.bashrc && \
    echo "export ROS_DOMAIN_ID=1" >> /root/.bashrc && \
    echo "export DISPLAY=:1" >> /root/.bashrc

ENTRYPOINT ["/usr/local/bin/start_novnc.sh"]
CMD ["bash"]

# Auto-source ROS/project environment in every interactive shell
RUN echo "source /workspace/scripts/ros_env.sh" >> /root/.bashrc
