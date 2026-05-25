# CI/CD Pipeline for Reproducible UAV Simulation Testing

> **DevOps for Cyber-Physical Systems** — University of Bern  
> Author: Slieptsov Mykyta

A fully automated CI/CD pipeline that builds, runs, and validates a UAV simulation on every `git push`. Three parallel simulation runs with different random seeds prove that the system produces consistent, reproducible results across varying conditions.

---

## Pipeline Overview

```
git push
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  BUILD                                                  │
│  docker build → push to GHCR                            │
└───────────────────────┬─────────────────────────────────┘
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
   seed=42        seed=123       seed=456
   docker run     docker run     docker run
   (parallel)     (parallel)     (parallel)
          │             │             │
          └─────────────┼─────────────┘
                        ▼
┌─────────────────────────────────────────────────────────┐
│  VARIANCE REPORT                                        │
│  mean ± std  for deviation, flight time, YOLO latency   │
└─────────────────────────────────────────────────────────┘
```

Each simulation run inside Docker:
1. Starts virtual display (Xvfb) for headless rendering
2. Launches Ignition Gazebo with the urban scene
3. Starts ROS-Gazebo bridge (camera, odometry, velocity)
4. Runs UAV controller + YOLO perception node in parallel
5. Saves metrics, perception results, and two scene captures

---

## Technology Stack

| Technology | Version | Role |
|---|---|---|
| ROS2 | Humble | Robotics middleware, node communication |
| Ignition Gazebo | Fortress | Physics simulation, camera rendering |
| YOLOv8n | Ultralytics | Real-time object detection on camera frames |
| Docker | — | Reproducible, isolated simulation environment |
| GitHub Actions | — | CI/CD automation, parallel matrix runs |
| GHCR | — | Docker image registry between CI jobs |
| Xvfb + Mesa | — | Headless OpenGL rendering in CI |

---

## Project Structure

```
uav-ci-cd-simulation/
├── .github/
│   └── workflows/
│       └── ci.yml                   # Pipeline: build → 3x simulate → variance report
├── ros2_ws/
│   └── src/
│       └── uav_control/
│           └── uav_control/
│               ├── controller.py    # Proportional velocity controller, seeded MAX_SPEED
│               └── perception_node.py  # YOLO node subscribed to /uav/camera
├── scripts/
│   ├── run_simulation.sh            # Container entrypoint: starts all processes
│   └── test.py                      # Validates metrics.json after simulation
├── worlds/
│   └── simple_world.sdf             # Urban scene: road, buildings, trucks, people
├── dockerfile                       # ROS2 + Gazebo + YOLO image definition
└── requirements.txt
```

---

## Simulation Scene

The UAV flies at 8 m altitude over an urban block from `(0, 0)` to target `(5, 3)` in a straight path. The downward-facing camera (60° FOV) captures the scene below.

**Scene objects (all inline SDF geometry — no network downloads):**
- Green grass ground plane
- Dark asphalt road (16 × 5 m) running along the flight path
- Gray building (north of road) and beige building (south of road)
- Red truck and blue truck parked on the road
- Magenta person on the sidewalk

**Two scene captures per run:**
- `scene_capture_mid.jpg` — frame 15 (~3 s into flight, UAV over the road)
- `scene_capture.jpg` — last frame (UAV hovering at target)

---

## Seeded Randomness

Reproducibility is controlled via the `RANDOM_SEED` environment variable:

```bash
docker run -e RANDOM_SEED=42 uav-sim   # always produces identical result
docker run -e RANDOM_SEED=123 uav-sim  # different conditions, same code
```

Inside `controller.py`:

```python
SEED = int(os.environ.get('RANDOM_SEED', 42))
_rng = random.Random(SEED)
MAX_SPEED = round(0.7 + _rng.random() * 0.6, 3)  # 0.7–1.3 m/s
```

The seed controls `MAX_SPEED`, which simulates different motor/wind conditions. The same seed always produces byte-identical metrics.

---

## Test Criteria

### Simulation Test
| Check | Threshold |
|---|---|
| UAV reaches target `(5.0, 3.0)` | deviation < 0.5 m |
| Mission completes before timeout | < 20 s |

### Perception Test (YOLO)
| Check | Threshold |
|---|---|
| Camera frames processed | > 0 |
| Average inference latency | < 200 ms |

Both tests must pass for the pipeline to succeed (`exit 0`).

---

## Variance Report (Sample)

| Seed | Max Speed | Simulation | Perception | Deviation | Flight Time |
|---|---|---|---|---|---|
| 42 | 1.084 m/s | ✅ | ✅ | 0.481 m | 6.0 s |
| 123 | 0.731 m/s | ✅ | ✅ | 0.477 m | 7.4 s |
| 456 | 1.149 m/s | ✅ | ✅ | 0.493 m | 5.8 s |

| Metric | Mean | Std Dev | Interpretation |
|---|---|---|---|
| Deviation from target | 0.484 m | ±0.007 m | Navigation consistency |
| Flight time | 6.4 s | ±0.712 s | Speed consistency |
| YOLO avg latency | 84.8 ms | ±1.6 ms | Perception consistency |

**Low std deviation = high reproducibility** across different seeded conditions.

---

## Running Locally

### Prerequisites
- Docker

### Build and run with a specific seed

```bash
docker build -f dockerfile -t uav-sim .
docker run --name uav-test -e RANDOM_SEED=42 uav-sim
```

### Extract artifacts

```bash
docker cp uav-test:/app/metrics.json ./metrics.json
docker cp uav-test:/app/perception_results.json ./perception_results.json
docker cp uav-test:/app/scene_capture.jpg ./scene_capture.jpg
docker cp uav-test:/app/scene_capture_mid.jpg ./scene_capture_mid.jpg
docker rm uav-test
```

### Check results

```bash
cat metrics.json
cat perception_results.json
```

---

## How the ROS2-Gazebo Integration Works

```
Ignition Gazebo
    │  /uav/camera (Image)
    │  /model/uav/odometry (Odometry)
    ▼
ros_gz_bridge
    │
    ├──▶ perception_node  →  YOLOv8n inference  →  perception_results.json
    │                                            →  scene_capture*.jpg
    │
    └──▶ controller_node  →  /cmd_vel  ──────────▶  ros_gz_bridge  →  Gazebo VelocityControl
                          →  metrics.json
```

All communication uses standard ROS2 topics. The bridge translates between `ignition.msgs` and ROS2 message types.

---

## CI Artifacts

Every pipeline run uploads the following artifacts to GitHub Actions:

| Artifact | Contents |
|---|---|
| `metrics-{seed}` | `metrics-{seed}.json` — navigation result |
| `perception-{seed}` | `perception-{seed}.json` — YOLO statistics |
| `scene-capture-{seed}` | Mid-flight and end-flight JPEG images |
