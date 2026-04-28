#!/bin/bash

set -e

echo "[1/3] Starting Gazebo..."
ign gazebo /app/worlds/simple_world.sdf -r -s &

sleep 5

echo "[2/3] Starting ROS-Gazebo Bridge..."
ros2 run ros_gz_bridge parameter_bridge \
  /cmd_vel@geometry_msgs/msg/Twist]ignition.msgs.Twist &

sleep 2

echo "[3/3] Starting UAV Controller node..."
ros2 run uav_control controller &

echo "All processes started. Waiting..."
wait

echo "Simulation finished."
