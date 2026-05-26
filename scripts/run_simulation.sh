#!/bin/bash

set -e

echo "[0/4] Starting virtual display for camera rendering..."
Xvfb :99 -screen 0 1280x1024x24 -ac +extension GLX -noreset &
export DISPLAY=:99
export LIBGL_ALWAYS_SOFTWARE=1
export MESA_GL_VERSION_OVERRIDE=3.3
sleep 2

echo "[1/4] Starting Gazebo..."
ign gazebo /app/worlds/simple_world.sdf -r -s &

sleep 35

echo "[2/4] Starting ROS-Gazebo Bridge..."
ros2 run ros_gz_bridge parameter_bridge \
  /cmd_vel@geometry_msgs/msg/Twist]ignition.msgs.Twist \
  /model/uav/odometry@nav_msgs/msg/Odometry[ignition.msgs.Odometry \
  /uav/camera@sensor_msgs/msg/Image[ignition.msgs.Image &

sleep 5

echo "[3/4] Starting UAV Controller and Perception nodes..."
ros2 run uav_control controller &
ros2 run uav_control perception &

echo "All processes started. Running simulation for 25 seconds..."
sleep 25

echo "Stopping simulation..."
kill $(jobs -p) 2>/dev/null

echo "Running simulation test..."
python3 /app/test.py
