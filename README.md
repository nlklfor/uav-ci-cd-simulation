# CI/CD Pipeline for Reproducible UAV Simulation Testing

This project demonstrates how DevOps practices can be applied to UAV simulation testing. It uses a Dockerized Gazebo simulation environment integrated with a GitHub Actions CI/CD pipeline to automatically build, run, and validate simulation tests on every push.

## Project Structure

```
uav-ci-cd-simulation/
├── .github/
│   └── workflows/
│       └── ci.yml                  # GitHub Actions CI pipeline
├── ros2_ws/
│   └── src/
│       └── uav_control/            # ROS2 UAV controller package
│           └── uav_control/
│               └── controller.py   # Publishes velocity commands to /cmd_vel
├── scripts/
│   ├── run_simulation.sh           # Docker entrypoint — launches Gazebo, Bridge, and ROS2 node
│   └── test.py                     # UAV collision test script
├── worlds/
│   └── simple_world.sdf            # Gazebo simulation world with UAV model and plugins
├── dockerfile                      # Docker image definition (ROS2 + Gazebo + workspace build)
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
3. Starts the **ROS-Gazebo Bridge** — bridges `/cmd_vel` from ROS2 to Gazebo
4. Starts the **UAV Controller** ROS2 node — publishes velocity commands
5. Waits for all processes; exits with non-zero code if any process fails

### World File (`worlds/simple_world.sdf`)

Defines the Gazebo simulation environment using SDF (Simulation Description Format):
- **Directional light** — simulates sunlight
- **Ground plane** — flat surface for the simulation
- **UAV model** — box with physics (mass, collision, visual) placed at 1m height
- **Physics plugin** — enables Gazebo physics engine
- **VelocityControl plugin** — listens to `/cmd_vel` and applies velocity to the UAV model

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
[1/3] Starting Gazebo...
[2/3] Starting ROS-Gazebo Bridge...
[3/3] Starting UAV Controller node...
All processes started. Waiting...
Sending velocity command
Sending velocity command
...
Simulation finished.
```

## Author

**Slieptsov Mykyta**
University of Bern — DevOps for Cyber-Physical Systems

## Roadmap

- [ ] Integrate PX4 SITL for realistic autopilot simulation
- [ ] Replace placeholder test with real UAV flight scenario (arm → takeoff → land)
- [ ] Wire `test.py` into `run_simulation.sh` for end-to-end test validation
- [ ] Add pytest with JUnit XML output for CI test reporting
- [ ] Cache Docker layers in CI for faster builds
