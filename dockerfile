FROM ros:humble

RUN apt-get update && apt-get install -y \
    ros-humble-ros-gz \
    ros-humble-cv-bridge \
    ignition-fortress \
    python3-pip \
    python3-opencv \
    xvfb \
    libgl1-mesa-dri \
    libgles2 \
    libegl1 \
    && rm -rf /var/lib/apt/lists/*

SHELL ["/bin/bash", "-c"]

WORKDIR /app

COPY ros2_ws/src /app/ros2_ws/src

RUN source /opt/ros/humble/setup.bash && \
    rosdep update && \
    rosdep install --from-paths /app/ros2_ws/src --ignore-src -r -y

RUN source /opt/ros/humble/setup.bash && \
    cd /app/ros2_ws && \
    colcon build

COPY scripts/run_simulation.sh /app/run_simulation.sh
COPY scripts/test.py /app/test.py
COPY worlds /app/worlds

# Pre-cache Fuel models at build time so they don't download at simulation runtime
RUN ign fuel download -u "https://fuel.gazebosim.org/1.0/OpenRobotics/models/Person%20Standing" 2>/dev/null || true && \
    ign fuel download -u "https://fuel.gazebosim.org/1.0/OpenRobotics/models/Sedan" 2>/dev/null || true

RUN chmod +x /app/run_simulation.sh

CMD ["/bin/bash", "-c", \
     "source /opt/ros/humble/setup.bash && \
      source /app/ros2_ws/install/setup.bash && \
      /app/run_simulation.sh"]
