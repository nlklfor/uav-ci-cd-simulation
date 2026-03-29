#!/bin/bash

set -e

echo "Checking Gazebo installation..."

if ! command -v ign &> /dev/null
then
    echo "ign command not found!"
    exit 1
fi

echo "Starting Gazebo..."

ign gazebo -r -s &

SIM_PID=$!

sleep 5

echo "Stopping simulation..."

kill $SIM_PID

echo "Simulation completed successfully"