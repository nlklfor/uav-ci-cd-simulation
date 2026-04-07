#!/bin/bash

set -e

echo "Starting simulation script..."

ign gazebo /app/worlds/simple_world.sdf -r -s &

SIM_PID=$!

sleep 5

echo "Stopping simulation..."

kill $SIM_PID

echo "Simulation completed successfully"