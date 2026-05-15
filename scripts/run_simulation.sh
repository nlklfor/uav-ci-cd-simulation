#!/bin/bash

set -e

echo "[1/3] Starting Gazebo..."
ign gazebo /app/worlds/simple_world.sdf -r -s &

sleep 20

echo "[2/3] Starting ROS-Gazebo Bridge..."
ros2 run ros_gz_bridge parameter_bridge \
  /cmd_vel@geometry_msgs/msg/Twist]ignition.msgs.Twist \
  /model/uav/odometry@nav_msgs/msg/Odometry[ignition.msgs.Odometry \
  /uav/camera@sensor_msgs/msg/Image[ignition.msgs.Image &

sleep 5

echo "[3/3] Starting UAV Controller node..."

ros2 run uav_control controller &

echo "All processes started. Running simulation for 25 seconds..."
sleep 25

echo "Stopping simulation..."
kill $(jobs -p) 2>/dev/null

echo "Running tests..."
python3 /app/test.py
