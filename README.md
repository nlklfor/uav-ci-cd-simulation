# CI/CD Pipeline for Reproducible UAV Simulation Testing

This project demonstrates how DevOps practices can be applied to UAV simulation testing. It uses a Dockerized Gazebo simulation environment integrated with a GitHub Actions CI/CD pipeline to automatically build, run, and validate simulation tests on every push.

## Project Structure

```
uav-ci-cd-simulation/
├── .github/
│   └── workflows/
│       └── ci.yml                  # GitHub Actions CI pipeline
├── scripts/
│   ├── run_simulation.sh           # Docker entrypoint — launches Gazebo and runs tests
│   └── test.py                     # UAV collision test script
├── worlds/
│   └── simple_world.sdf            # Gazebo simulation world definition
├── dockerfile                      # Docker image definition (ROS2 + Gazebo)
├── requirements.txt                # Python dependencies
└── README.md
```

## Technologies

| Technology | Version | Purpose |
|---|---|---|
| ROS2 | Humble | Robotics middleware |
| Gazebo | Ignition Fortress | Physics simulation engine |
| Docker | - | Reproducible build environment |
| GitHub Actions | - | CI/CD automation |

## How It Works

### Docker Image (`dockerfile`)

Builds from the official `ros:humble` base image and installs:
- `ros-humble-ros-gz` — ROS2-Gazebo bridge for communication between ROS2 and Gazebo
- `ignition-fortress` — Gazebo Ignition Fortress (the simulation engine paired with ROS2 Humble)

The container entrypoint is `run_simulation.sh`.

### Simulation Script (`scripts/run_simulation.sh`)

Orchestrates the full simulation run inside the container:
1. Launches Gazebo Ignition in **server-only mode** (`-s`) so no GUI is needed (headless for CI)
2. Starts the simulation immediately (`-r`) with the world defined in `simple_world.sdf`
3. Lets the simulation run for 5 seconds
4. Stops the simulation and exits

### World File (`worlds/simple_world.sdf`)

Defines the Gazebo simulation environment using SDF (Simulation Description Format):
- **Directional light** — simulates sunlight
- **Ground plane** — flat surface for the simulation
- **Box model** — a 1m cube with physics (mass, collision, visual) placed at the origin

### Test Script (`scripts/test.py`)

A placeholder UAV collision test that simulates a pass/fail check. Returns exit code `0` on success and `1` on failure, which the CI pipeline uses to determine build status.

### CI/CD Pipeline (`.github/workflows/ci.yml`)

Triggered on every `git push`:
1. Checks out the repository
2. Builds the Docker image (`docker build -t uav-sim .`)
3. Runs the container (`docker run uav-sim`)

If the simulation or tests fail (non-zero exit code), the pipeline fails.

## Usage

### Build and run locally

```bash
docker build -t uav-sim .
docker run --rm uav-sim
```

### Expected output

```
Starting simulation script...
Stopping simulation...
Simulation completed successfully
```

## Roadmap

- [ ] Integrate PX4 SITL for realistic autopilot simulation
- [ ] Replace placeholder test with real UAV flight scenario (arm → takeoff → land)
- [ ] Wire `test.py` into `run_simulation.sh` for end-to-end test validation
- [ ] Add pytest with JUnit XML output for CI test reporting
- [ ] Cache Docker layers in CI for faster builds
