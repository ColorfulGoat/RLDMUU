#!/usr/bin/env bash

source /opt/ros/jazzy/setup.bash

if [ -f /workspace/install/setup.bash ]; then
  source /workspace/install/setup.bash
fi

export DRLNAV_BASE_PATH="${DRLNAV_BASE_PATH:-/workspace}"
export TURTLEBOT3_MODEL="${TURTLEBOT3_MODEL:-burger}"
export ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-1}"
